"""Upgrade deal-card image URLs to higher-resolution variants where the CDN allows it."""

from __future__ import annotations

import html
import re
import ssl
import urllib.request
from typing import Any

_REDDIT_PREVIEW_HOST = re.compile(
    r"https://(?:external-preview|preview)\.redd\.it[^\"\s<>]+",
    re.I,
)
_REDDIT_DIRECT_IMG = re.compile(
    r"https://i\.redd\.it/[a-z0-9_-]+\.(?:jpe?g|png|gif|webp)\b",
    re.I,
)
_WIDTH_PARAM = re.compile(r"width=(\d+)", re.I)
_IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")

# Amazon ASIN: 10-char alphanumeric starting with B, or 10 digits
_AMAZON_ASIN = re.compile(
    r"/(?:dp|gp/product|product-reviews|ASIN)/([A-Z0-9]{10})(?:[/?#]|$)",
    re.I,
)
_AMAZON_HOST = re.compile(
    r"(?:^|\.)amazon\.(?:com|ca|co\.uk|de|fr|es|it|co\.jp|com\.au|com\.br|com\.mx)$",
    re.I,
)
_OG_IMAGE = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']'
    r'|<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.I,
)
_SHORT_AMAZON = re.compile(r"https?://(?:www\.)?a\.co/", re.I)
_NEWEGG_HOST = re.compile(r"(?:^|\.)(newegg\.com)$", re.I)
_WALMART_IMG = re.compile(
    r"i5\.walmartimages\.com/dfw/[A-Za-z0-9_/-]+\.(?:jpg|jpeg|png|webp)",
    re.I,
)

_SCRAPE_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)


def _make_ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    try:
        import certifi  # type: ignore
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        pass
    return ctx


def _resolve_short_amazon_url(url: str, timeout: int = 6) -> str | None:
    """Follow a.co short link and return the resolved Amazon URL (sync)."""
    if not _SHORT_AMAZON.match(url):
        return None
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": _SCRAPE_UA})
        resp = urllib.request.urlopen(req, timeout=timeout, context=_make_ssl_ctx())
        final = resp.geturl()
        return final if "amazon." in final else None
    except Exception:
        try:
            # Some servers don't support HEAD — fall back to GET with small read
            req2 = urllib.request.Request(url, headers={"User-Agent": _SCRAPE_UA})
            resp2 = urllib.request.urlopen(req2, timeout=timeout, context=_make_ssl_ctx())
            return resp2.geturl() if "amazon." in resp2.geturl() else None
        except Exception:
            return None


def _fetch_og_image_sync(url: str, timeout: int = 8) -> str | None:
    """Fetch the og:image meta tag from a product page URL (sync, short read)."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _SCRAPE_UA,
                "Accept": "text/html,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        ctx = _make_ssl_ctx()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            # Read first 32 KB — enough to find og:image in <head>
            chunk = resp.read(32768).decode("utf-8", errors="replace")
        m = _OG_IMAGE.search(chunk)
        if m:
            img = (m.group(1) or m.group(2) or "").strip()
            if img.startswith("http"):
                return img
    except Exception:
        pass
    return None


def og_image_for_url(url: str) -> str | None:
    """
    Synchronous: returns the best product image URL for a given deal page URL.
    - For a.co short links: resolve redirect then extract ASIN
    - For other Amazon URLs: extract ASIN directly
    - For Newegg/Woot/BestBuy/Walmart/etc: fetch og:image from the page
    Returns None if nothing usable found.
    """
    if not url or not url.startswith("http"):
        return None

    # a.co → resolve redirect → extract ASIN
    if _SHORT_AMAZON.match(url):
        resolved = _resolve_short_amazon_url(url)
        if resolved:
            asin = extract_amazon_asin(resolved)
            if asin:
                return amazon_product_image_url(asin)
        return None

    # Direct Amazon URL with ASIN already handled in _normalize_posts;
    # fall through to OG for other Amazon URLs without /dp/ pattern
    asin = extract_amazon_asin(url)
    if asin:
        return amazon_product_image_url(asin)

    # Newegg, Woot, BestBuy, Walmart, eBay, B&H — scrape og:image
    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower().lstrip("www.")
    _OG_HOSTS = (
        "newegg.com", "bestbuy.com", "bhphotovideo.com",
        "woot.com", "walmart.com", "ebay.com", "adorama.com",
        "microcenter.com", "antonline.com", "costco.com",
        "hp.com", "dell.com", "lenovo.com",
    )
    if any(host.endswith(h) for h in _OG_HOSTS):
        return _fetch_og_image_sync(url)

    return None


async def og_image_for_url_async(url: str) -> str | None:
    """
    Async version using httpx — handles HTTP/2, better TLS, works for Walmart etc.
    Priority: ASIN (Amazon) → Walmart CDN → og:image scrape.
    """
    if not url or not url.startswith("http"):
        return None

    # a.co short link resolution
    if _SHORT_AMAZON.match(url):
        try:
            import httpx as _httpx

            async with _httpx.AsyncClient(timeout=6, follow_redirects=True) as c:
                r = await c.head(url, headers={"User-Agent": _SCRAPE_UA})
                final = str(r.url)
                if "amazon." in final:
                    asin = extract_amazon_asin(final)
                    if asin:
                        return amazon_product_image_url(asin)
        except Exception:
            pass
        return None

    asin = extract_amazon_asin(url)
    if asin:
        return amazon_product_image_url(asin)

    from urllib.parse import urlparse

    host = urlparse(url).netloc.lower().lstrip("www.")
    _OG_HOSTS_SET = {
        "newegg.com", "bestbuy.com", "bhphotovideo.com",
        "woot.com", "walmart.com", "ebay.com", "adorama.com",
        "microcenter.com", "antonline.com", "costco.com",
        "hp.com", "dell.com", "lenovo.com", "acer.com",
        "asus.com", "msi.com",
    }
    if not any(host.endswith(h) for h in _OG_HOSTS_SET):
        return None

    try:
        import httpx as _httpx

        headers = {
            "User-Agent": _SCRAPE_UA,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        chunk = None
        try:
            async with _httpx.AsyncClient(timeout=9, follow_redirects=True) as c:
                r = await c.get(url, headers=headers)
                if r.status_code < 400:
                    chunk = r.text[:40000]
        except Exception:
            pass

        # httpx fallback → urllib (handles cases where httpx TLS fingerprinting is blocked)
        if chunk is None:
            import urllib.request as _urllib_req
            import ssl as _ssl

            def _urllib_fetch() -> str | None:
                ctx = _make_ssl_ctx()
                req = _urllib_req.Request(url, headers={
                    "User-Agent": _SCRAPE_UA,
                    "Accept": "text/html",
                    "Accept-Language": "en-US,en;q=0.9",
                })
                try:
                    with _urllib_req.urlopen(req, timeout=9, context=ctx) as resp:
                        return resp.read(40960).decode("utf-8", errors="replace")
                except Exception:
                    return None

            import asyncio as _asyncio
            chunk = await _asyncio.to_thread(_urllib_fetch)

        if not chunk:
            return None

        # Walmart: extract first i5.walmartimages.com product image
        if "walmart.com" in host:
            m = _WALMART_IMG.search(chunk)
            if m:
                return "https://" + m.group(0)

        # Generic og:image
        m = _OG_IMAGE.search(chunk)
        if m:
            img = (m.group(1) or m.group(2) or "").strip()
            if img.startswith("http"):
                return img

        # B&H: try CDN pattern from product ID in URL
        if "bhphotovideo.com" in host:
            bh_m = re.search(r"/product/(\d+)-", url)
            if bh_m:
                bh_img = f"https://photos.bhphotovideo.com/catMedia/full/{bh_m.group(1)}.jpg"
                try:
                    async with _httpx.AsyncClient(timeout=5, follow_redirects=True) as c2:
                        rh = await c2.head(bh_img, headers={"User-Agent": _SCRAPE_UA})
                        if rh.status_code == 200:
                            return bh_img
                except Exception:
                    pass

    except Exception:
        pass

    return None


def extract_amazon_asin(url: str | None) -> str | None:
    """Return 10-char ASIN if URL is an Amazon product page, else None."""
    if not url:
        return None
    url = url.strip()
    try:
        from urllib.parse import urlparse
        h = urlparse(url).netloc.lower().lstrip("www.")
        if not _AMAZON_HOST.search(h) and "amazon." not in h:
            return None
    except Exception:
        return None
    m = _AMAZON_ASIN.search(url)
    if m:
        asin = m.group(1).upper()
        # ASINs start with B or are 10 digits; filter obvious false positives
        if len(asin) == 10 and (asin.startswith("B") or asin.isdigit()):
            return asin
    return None


def amazon_product_image_url(asin: str) -> str:
    """Best-effort high-res Amazon product image URL from ASIN (no auth required)."""
    return f"https://m.media-amazon.com/images/P/{asin}.jpg"


def reddit_json_direct_listing_image_url(d: dict[str, Any]) -> str | None:
    """
    Use the submission's outbound URL when it already points at a raw image (e.g. i.redd.it).
    Those hosts usually load reliably; external-preview.redd.it often 403s hotlinked fetches.
    """
    u = (d.get("url_overridden_by_dest") or d.get("url") or "").strip()
    if not u.startswith("https://"):
        return None
    if "reddit.com" in u:
        return None
    base = u.split("?", 1)[0].lower()
    if "i.redd.it" in base or "i.redditmedia.com" in base:
        return html.unescape(u)
    if any(base.endswith(ext) for ext in _IMG_EXTS):
        return html.unescape(u)
    return None


def upgrade_reddit_image_url(url: str | None) -> str | None:
    """Widen redd.it preview query caps (Atom / legacy thumb URLs)."""
    if not url or not isinstance(url, str):
        return None
    u = html.unescape(url.strip()).replace("&amp;", "&")
    if "external-preview.redd.it" not in u and "preview.redd.it" not in u:
        return u
    m = _WIDTH_PARAM.search(u)
    if m:
        w = int(m.group(1))
        if w < 1920:
            u = _WIDTH_PARAM.sub("width=1920", u, count=1)
    return u


def reddit_json_best_image_url(d: dict[str, Any]) -> str | None:
    """Prefer full preview image from Reddit JSON over the small `thumbnail` field."""
    preview = d.get("preview")
    if isinstance(preview, dict) and preview.get("enabled"):
        images = preview.get("images")
        if isinstance(images, list) and images:
            im0 = images[0]
            if isinstance(im0, dict):
                source = im0.get("source")
                if isinstance(source, dict):
                    u = source.get("url")
                    if isinstance(u, str) and u.startswith("http"):
                        return upgrade_reddit_image_url(
                            html.unescape(u.replace("&amp;", "&"))
                        )
                resolutions = im0.get("resolutions")
                if isinstance(resolutions, list) and resolutions:
                    cand = [
                        r
                        for r in resolutions
                        if isinstance(r, dict) and isinstance(r.get("url"), str)
                    ]
                    if cand:
                        best = max(cand, key=lambda r: int(r.get("width") or 0))
                        u = best.get("url")
                        if isinstance(u, str) and u.startswith("http"):
                            return upgrade_reddit_image_url(
                                html.unescape(u.replace("&amp;", "&"))
                            )
    return None


def reddit_atom_best_thumbnail(raw_html: str, media_thumb: str | None) -> str | None:
    """Prefer direct i.redd.it image links; else widest preview.redd.it from Atom content."""
    raw = raw_html or ""
    dm = _REDDIT_DIRECT_IMG.search(raw)
    if dm:
        return html.unescape(dm.group(0))

    candidates: list[str] = []
    for m in _REDDIT_PREVIEW_HOST.finditer(raw):
        candidates.append(html.unescape(m.group(0)))
    if media_thumb and media_thumb.startswith("http"):
        candidates.append(html.unescape(media_thumb))

    best: str | None = None
    best_w = -1
    for u in candidates:
        mw = _WIDTH_PARAM.search(u)
        w = int(mw.group(1)) if mw else 0
        if w >= best_w:
            best_w = w
            best = u
    return upgrade_reddit_image_url(best)


def bh_product_image_url(url: str) -> str | None:
    """B&H Photo CDN: construct image URL from product ID embedded in their URL."""
    m = re.search(r"/product/(\d{6,})-", url)
    if not m:
        return None
    pid = m.group(1)
    return f"https://photos.bhphotovideo.com/catMedia/full/{pid}.jpg"


def upgrade_slickdeals_thumb_url(url: str | None) -> str | None:
    """Slickdeals RSS uses 300x300 paths; 600x600 is served for the same attachment."""
    if not url or not isinstance(url, str):
        return None
    u = html.unescape(url.strip())
    return u.replace("/300x300/", "/600x600/")
