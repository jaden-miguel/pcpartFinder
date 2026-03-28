from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pcfinder.config_persist import load_app_config
from pcfinder.deal_rules import collect_deal_reasons
from pcfinder.deals import evaluate_watch
from pcfinder.fetcher import fetch_price
from pcfinder.notify import send_deal_alert
from pcfinder.scan_results import scan_results_path, write_scan_results
from pcfinder.state import StateStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def run_scan(config_path: Path) -> None:
    cfg = load_app_config(config_path.resolve())
    state = StateStore(cfg.state_path)
    state.load()
    result_rows: list[dict[str, Any]] = []
    finished_at = datetime.now(timezone.utc).isoformat()

    for w in cfg.watches:
        ws = state.get(w.id)
        prev_price = ws.last_price
        price, err = await fetch_price(w.url, w.price_selector, cfg.http)
        if price is None:
            logger.info("[%s] skip fetch error: %s", w.id, err)
            result_rows.append(
                {
                    "id": w.id,
                    "name": w.name,
                    "url": w.url,
                    "currency": w.currency,
                    "price": None,
                    "error": err or "fetch failed",
                    "deal_reasons": [],
                    "is_deal": False,
                }
            )
            continue
        logger.info("[%s] %s %s", w.id, w.currency, price)
        reasons = collect_deal_reasons(w, price, prev_price)
        result_rows.append(
            {
                "id": w.id,
                "name": w.name,
                "url": w.url,
                "currency": w.currency,
                "price": price,
                "error": None,
                "deal_reasons": reasons,
                "is_deal": bool(reasons),
            }
        )
        event = evaluate_watch(w, price, state, cfg.default_alert_cooldown_hours)
        if event:
            logger.info("Alert: %s", event.title)
            send_deal_alert(cfg.apprise_urls, event)

    write_scan_results(scan_results_path(cfg.state_path), result_rows, finished_at)
    state.save()


async def run_forever(config_path: Path) -> None:
    cfg = load_app_config(config_path.resolve())
    interval = max(60, int(cfg.scan_interval_minutes) * 60)
    while True:
        try:
            await run_scan(config_path)
        except Exception:
            logger.exception("Scan failed")
        await asyncio.sleep(interval)


def main() -> None:
    p = argparse.ArgumentParser(description="PC parts deal notifier")
    p.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml",
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="Run a single scan and exit",
    )
    p.add_argument(
        "--web",
        action="store_true",
        help="Open the web dashboard (local UI + API)",
    )
    p.add_argument(
        "--host",
        default="127.0.0.1",
        help="With --web: bind address (default 127.0.0.1)",
    )
    p.add_argument(
        "--port",
        type=int,
        default=8765,
        help="With --web: port (default 8765)",
    )
    args = p.parse_args()
    config_path = args.config

    if args.web:
        import uvicorn

        from pcfinder.webapp import create_app

        uvicorn.run(
            create_app(),
            host=args.host,
            port=args.port,
            log_level="info",
        )
        return

    if not config_path.exists():
        raise SystemExit(
            f"Missing {config_path.resolve()}. Copy config.example.yaml to config.yaml."
        )

    try:
        if args.once:
            asyncio.run(run_scan(config_path))
        else:
            asyncio.run(run_forever(config_path))
    except KeyboardInterrupt:
        logger.info("Stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
