from __future__ import annotations

import asyncio
import logging
import time as time_module
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pcfinder.config_persist import load_app_config, save_app_config
from pcfinder.models import AppConfig, HttpSettings, Watch
from pcfinder.notify import send_plain_notification
from pcfinder.net_fallback import resilient_get_bytes
from pcfinder.reddit_deals import BOOKMARK_FALLBACK_ITEMS, fetch_curated_deals
from pcfinder.runner import run_scan
from pcfinder.scan_results import read_scan_results, scan_results_path
from pcfinder.telegram_util import merge_apprise_urls, split_apprise_urls

logger = logging.getLogger(__name__)

# Project root (folder that contains the `pcfinder` package), not process cwd — so the UI works
# when the server is started from any directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = _PROJECT_ROOT / "config.yaml"
STATIC_DIR = Path(__file__).resolve().parent / "static"

_scanner_task: asyncio.Task[None] | None = None
_scanner_running = False
_last_scan_at: str | None = None
_last_scan_error: str | None = None
_scan_lock = asyncio.Lock()

_curated_lock = asyncio.Lock()
_curated_cache_mono: float = 0.0
_curated_cache_response: dict[str, Any] | None = None
CURATED_TTL_SEC = 180.0

IMG_PROXY_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def _allowed_thumbnail_proxy_url(url: str) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme != "https":
        return False
    host = (p.hostname or "").lower()
    if not host:
        return False
    if host.endswith(".redd.it") or host == "redd.it":
        return True
    if host.endswith(".redditmedia.com") or host == "redditmedia.com":
        return True
    if host.endswith(".slickdealscdn.com"):
        return True
    # Amazon CDNs (product images, Woot OG images, etc.)
    if "media-amazon.com" in host or "ssl-images-amazon.com" in host:
        return True
    if host.endswith(".amazon.com"):
        return True
    # Newegg
    if "newegg" in host:
        return True
    # B&H
    if "bhphotovideo.com" in host or "photos.bhphotovideo.com" in host:
        return True
    # BestBuy
    if "bestbuy" in host:
        return True
    # Woot / Amazon sub-brands
    if "woot" in host or "wootcdn" in host:
        return True
    # eBay
    if "ebayimg.com" in host or "ebay.com" in host:
        return True
    # Walmart
    if "walmart" in host or "walmartimages.com" in host or "i5.walmartimages.com" in host:
        return True
    # General product image CDNs
    if "adorama.com" in host or "microcenter.com" in host or "antonline.com" in host:
        return True
    if "costco.com" in host or "costcocdn.com" in host:
        return True
    return False


def _guess_image_media_type(data: bytes) -> str:
    if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if len(data) >= 6 and data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if len(data) >= 12 and data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis"):
        return "image/avif"
    return "image/jpeg"


class HttpPayload(BaseModel):
    timeout_seconds: float = 25
    user_agent: str = "pcFinderDealBot/1.0 (personal use)"
    verify_ssl: bool = True


class WatchPayload(BaseModel):
    id: str
    name: str = ""
    url: str
    price_selector: str
    max_price: float | None = None
    min_drop_percent: float | None = None
    baseline_price: float | None = None
    min_discount_percent_vs_baseline: float | None = None
    currency: str = "USD"
    alert_cooldown_hours: float | None = None


class ConfigPayload(BaseModel):
    scan_interval_minutes: int = Field(ge=1, le=1440)
    default_alert_cooldown_hours: float = Field(ge=0, le=168)
    auto_start_scanner: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    extra_apprise_urls: list[str] = Field(default_factory=list)
    http: HttpPayload = Field(default_factory=HttpPayload)
    watches: list[WatchPayload] = Field(default_factory=list)


def _cfg_path() -> Path:
    return CONFIG_PATH.resolve()


def _app_config() -> AppConfig:
    return load_app_config(_cfg_path())


def _payload_to_config(p: ConfigPayload) -> AppConfig:
    current = _app_config()
    tg = None
    if p.telegram_bot_token.strip() and p.telegram_chat_id.strip():
        tg = (p.telegram_bot_token.strip(), p.telegram_chat_id.strip())
    apprise_urls = merge_apprise_urls(tg, [u.strip() for u in p.extra_apprise_urls if u.strip()])
    watches = [
        Watch(
            id=w.id.strip(),
            name=(w.name or w.id).strip(),
            url=w.url.strip(),
            price_selector=w.price_selector.strip(),
            max_price=w.max_price,
            min_drop_percent=w.min_drop_percent,
            baseline_price=w.baseline_price,
            min_discount_percent_vs_baseline=w.min_discount_percent_vs_baseline,
            currency=w.currency.strip() or "USD",
            alert_cooldown_hours=w.alert_cooldown_hours,
        )
        for w in p.watches
        if w.id.strip() and w.url.strip() and w.price_selector.strip()
    ]
    return AppConfig(
        scan_interval_minutes=p.scan_interval_minutes,
        apprise_urls=apprise_urls,
        watches=watches,
        http=HttpSettings(
            timeout_seconds=p.http.timeout_seconds,
            user_agent=p.http.user_agent,
            verify_ssl=p.http.verify_ssl,
        ),
        state_path=current.state_path,
        default_alert_cooldown_hours=p.default_alert_cooldown_hours,
        auto_start_scanner=p.auto_start_scanner,
    )


def _config_to_response(cfg: AppConfig) -> dict[str, Any]:
    tgram, other = split_apprise_urls(cfg.apprise_urls)
    bot_token, chat_id = ("", "")
    if tgram:
        bot_token, chat_id = tgram
    return {
        "scan_interval_minutes": cfg.scan_interval_minutes,
        "default_alert_cooldown_hours": cfg.default_alert_cooldown_hours,
        "auto_start_scanner": cfg.auto_start_scanner,
        "telegram_bot_token": bot_token,
        "telegram_chat_id": chat_id,
        "extra_apprise_urls": other,
        "http": {
            "timeout_seconds": cfg.http.timeout_seconds,
            "user_agent": cfg.http.user_agent,
            "verify_ssl": cfg.http.verify_ssl,
        },
        "watches": [
            {
                "id": w.id,
                "name": w.name,
                "url": w.url,
                "price_selector": w.price_selector,
                "max_price": w.max_price,
                "min_drop_percent": w.min_drop_percent,
                "baseline_price": w.baseline_price,
                "min_discount_percent_vs_baseline": w.min_discount_percent_vs_baseline,
                "currency": w.currency,
                "alert_cooldown_hours": w.alert_cooldown_hours,
            }
            for w in cfg.watches
        ],
    }


def _deal_feed_dict(cfg: AppConfig) -> dict[str, Any]:
    try:
        raw = read_scan_results(scan_results_path(cfg.state_path))
    except Exception:
        logger.exception("deal_feed read failed")
        return {"scan_finished_at": None, "items": [], "deal_count": 0}
    items = raw.get("items") or []
    if not isinstance(items, list):
        items = []
    clean = [i for i in items if isinstance(i, dict)]
    deal_n = sum(1 for i in clean if i.get("is_deal"))
    return {
        "scan_finished_at": raw.get("scan_finished_at"),
        "items": clean,
        "deal_count": deal_n,
    }


async def _get_curated_payload(*, force_refresh: bool = False) -> dict[str, Any]:
    global _curated_cache_mono, _curated_cache_response
    now = time_module.monotonic()
    async with _curated_lock:
        if (
            not force_refresh
            and _curated_cache_response is not None
            and (now - _curated_cache_mono) < CURATED_TTL_SEC
        ):
            return _curated_cache_response
        items, err = await fetch_curated_deals()
        bookmark_mode = not items
        if bookmark_mode:
            items = list(BOOKMARK_FALLBACK_ITEMS)
        out: dict[str, Any] = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source": "r/buildapcsales",
            "source_url": "https://www.reddit.com/r/buildapcsales/hot/",
            "items": items,
            "reddit_error": err,
            "bookmark_mode": bookmark_mode,
        }
        _curated_cache_response = out
        _curated_cache_mono = time_module.monotonic()
        return out


async def _scanner_loop() -> None:
    global _last_scan_at, _last_scan_error, _scanner_running
    path = _cfg_path()
    while _scanner_running:
        async with _scan_lock:
            try:
                await run_scan(path)
                _last_scan_at = datetime.now(timezone.utc).isoformat()
                _last_scan_error = None
            except Exception as e:
                logger.exception("Background scan failed")
                _last_scan_error = str(e)
        cfg = load_app_config(path)
        wait_s = max(60, int(cfg.scan_interval_minutes) * 60)
        for _ in range(wait_s):
            if not _scanner_running:
                break
            await asyncio.sleep(1)


def _start_background_scanner() -> None:
    global _scanner_task, _scanner_running
    if _scanner_task is not None and not _scanner_task.done():
        return
    _scanner_running = True
    _scanner_task = asyncio.create_task(_scanner_loop())


async def _stop_background_scanner() -> None:
    global _scanner_task, _scanner_running
    _scanner_running = False
    if _scanner_task is not None:
        t = _scanner_task
        _scanner_task = None
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    path = _cfg_path()
    if path.exists():
        try:
            cfg = load_app_config(path)
            if cfg.auto_start_scanner:
                _start_background_scanner()
        except Exception:
            logger.exception("Could not load config for auto-start")
    yield
    await _stop_background_scanner()


def create_app() -> FastAPI:
    app = FastAPI(title="pcFinder", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/curated-deals")
    async def curated_deals(refresh: int = 0) -> dict[str, Any]:
        return await _get_curated_payload(force_refresh=(refresh != 0))

    @app.get("/api/deals")
    def get_deals() -> dict[str, Any]:
        try:
            try:
                cfg = _app_config()
            except Exception:
                return {
                    "scan_finished_at": None,
                    "items": [],
                    "deal_count": 0,
                }
            return _deal_feed_dict(cfg)
        except Exception as e:
            logger.exception("GET /api/deals failed")
            raise HTTPException(500, str(e)) from e

    @app.get("/api/proxy-img")
    async def proxy_thumbnail(u: str) -> Response:
        """Serve deal thumbnails same-origin; Reddit/Slickdeals often 403 direct browser loads."""
        raw = unquote(u).strip()
        if not raw or len(raw) > 3000:
            raise HTTPException(400, "Invalid URL")
        if not _allowed_thumbnail_proxy_url(raw):
            raise HTTPException(400, "URL host not allowed")
        data, err = await resilient_get_bytes(raw, user_agent=IMG_PROXY_UA)
        if not data:
            logger.warning("proxy-img failed: %s", err)
            raise HTTPException(502, err or "upstream failed")
        return Response(
            content=data,
            media_type=_guess_image_media_type(data),
            headers={"Cache-Control": "public, max-age=300"},
        )

    @app.get("/api/config")
    async def get_config(refresh_curated: int = 0) -> dict[str, Any]:
        try:
            cfg = _app_config()
        except Exception as e:
            raise HTTPException(500, str(e)) from e
        out = _config_to_response(cfg)
        out["scanner_running"] = _scanner_running and (
            _scanner_task is not None and not _scanner_task.done()
        )
        out["last_scan_at"] = _last_scan_at
        out["last_scan_error"] = _last_scan_error
        out["deal_feed"] = _deal_feed_dict(cfg)
        out["curated_deals"] = await _get_curated_payload(
            force_refresh=(refresh_curated != 0),
        )
        return out

    @app.post("/api/config")
    def post_config(body: ConfigPayload) -> dict[str, Any]:
        cfg = _payload_to_config(body)
        try:
            save_app_config(_cfg_path(), cfg)
        except Exception as e:
            raise HTTPException(500, f"Save failed: {e}") from e
        return {"ok": True}

    @app.post("/api/scanner/start")
    async def scanner_start() -> dict[str, bool]:
        _start_background_scanner()
        return {"ok": True}

    @app.post("/api/scanner/stop")
    async def scanner_stop() -> dict[str, bool]:
        await _stop_background_scanner()
        return {"ok": True}

    @app.post("/api/scan-once")
    async def scan_once() -> dict[str, Any]:
        async with _scan_lock:
            try:
                await run_scan(_cfg_path())
                global _last_scan_at, _last_scan_error
                _last_scan_at = datetime.now(timezone.utc).isoformat()
                _last_scan_error = None
                return {"ok": True}
            except Exception as e:
                logger.exception("Manual scan failed")
                raise HTTPException(500, str(e)) from e

    @app.post("/api/test-telegram")
    def test_telegram(body: ConfigPayload) -> dict[str, Any]:
        cfg = _payload_to_config(body)
        if not cfg.apprise_urls:
            raise HTTPException(400, "Add Telegram bot token and chat ID first")
        ok = send_plain_notification(
            cfg.apprise_urls,
            "pcFinder test",
            "If you see this, Telegram notifications are working.",
        )
        if not ok:
            raise HTTPException(502, "Apprise could not send (check token, chat ID, and bot privacy)")
        return {"ok": True}

    @app.get("/")
    def index() -> FileResponse:
        index_path = STATIC_DIR / "index.html"
        if not index_path.is_file():
            raise HTTPException(500, "Missing static/index.html")
        return FileResponse(index_path)

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app
