from __future__ import annotations

import asyncio
import html
import json
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx

from pcfinder.net_fallback import resilient_get_text
from pcfinder.slickdeals_rss import fetch_slickdeals_frontpage
from pcfinder.thumb_hd import (
    amazon_product_image_url,
    bh_product_image_url,
    extract_amazon_asin,
    og_image_for_url,
    og_image_for_url_async,
    reddit_atom_best_thumbnail,
    reddit_json_best_image_url,
    reddit_json_direct_listing_image_url,
    upgrade_reddit_image_url,
)

logger = logging.getLogger(__name__)

REDDIT_HOT = "https://www.reddit.com/r/buildapcsales/hot.json?limit=50"
REDDIT_HOT_ATOM = "https://www.reddit.com/r/buildapcsales/hot.rss"

_ATOM = "{http://www.w3.org/2005/Atom}"
_MEDIA = "{http://search.yahoo.com/mrss/}"
_LINK_IN_CONTENT = re.compile(
    r'<a\s+[^>]*href="([^"]+)"[^>]*>\s*\[link\]\s*</a>',
    re.I,
)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# Shown when Reddit JSON is unreachable (e.g. datacenter IP blocks) — same shape as live items.
BOOKMARK_FALLBACK_ITEMS: list[dict[str, Any]] = [
    {
        "id": "bm-bas-hot",
        "title": "r/buildapcsales — hot posts (best community PC deals)",
        "deal_url": "https://www.reddit.com/r/buildapcsales/hot/",
        "reddit_url": "https://www.reddit.com/r/buildapcsales/hot/",
        "score": 0,
        "flair": "Reddit",
        "created_utc": 0.0,
        "thumbnail": None,
        "is_self_post": True,
        "is_bookmark": True,
    },
    {
        "id": "bm-bas-new",
        "title": "r/buildapcsales — newest posts",
        "deal_url": "https://www.reddit.com/r/buildapcsales/new/",
        "reddit_url": "https://www.reddit.com/r/buildapcsales/new/",
        "score": 0,
        "flair": "Reddit",
        "created_utc": 0.0,
        "thumbnail": None,
        "is_self_post": True,
        "is_bookmark": True,
    },
    {
        "id": "bm-slick",
        "title": "Slickdeals — front page & search",
        "deal_url": "https://slickdeals.net/",
        "reddit_url": "https://slickdeals.net/",
        "score": 0,
        "flair": "Aggregator",
        "created_utc": 0.0,
        "thumbnail": None,
        "is_self_post": True,
        "is_bookmark": True,
    },
    {
        "id": "bm-newegg",
        "title": "Newegg — PC components category",
        "deal_url": "https://www.newegg.com/Computer-Hardware/Category/ID-33",
        "reddit_url": "https://www.newegg.com/Computer-Hardware/Category/ID-33",
        "score": 0,
        "flair": "Retailer",
        "created_utc": 0.0,
        "thumbnail": None,
        "is_self_post": True,
        "is_bookmark": True,
    },
    {
        "id": "bm-mc",
        "title": "Micro Center — store deals (US, in-store often)",
        "deal_url": "https://www.microcenter.com/site/content/deals.aspx",
        "reddit_url": "https://www.microcenter.com/site/content/deals.aspx",
        "score": 0,
        "flair": "Retailer",
        "created_utc": 0.0,
        "thumbnail": None,
        "is_self_post": True,
        "is_bookmark": True,
    },
]

# Skip typical non-product top posts
_SKIP_TITLE_FRAGMENTS = (
    "giveaway",
    "discord server",
    "official r/",
    "meta",
    "weekly discussion",
    "simple questions",
)


def _skip_post(title: str, url: str, data: dict[str, Any]) -> bool:
    if data.get("stickied"):
        return True
    return _skip_post_by_title_url(title, url)


def _skip_post_by_title_url(title: str, url: str) -> bool:
    t = (title or "").lower()
    u = (url or "").lower()
    for frag in _SKIP_TITLE_FRAGMENTS:
        if frag in t:
            return True
    if "discord.gg" in u and "giveaway" in t:
        return True
    return False


def _atom_published_ts(entry: ET.Element) -> float:
    for tag in ("updated", "published"):
        el = entry.find(f"{_ATOM}{tag}")
        if el is not None and el.text:
            raw = el.text.strip().replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(raw).timestamp()
            except ValueError:
                continue
    return 0.0


def _normalize_atom_feed(xml_text: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.warning("Reddit Atom parse error: %s", e)
        return []

    out: list[dict[str, Any]] = []
    for entry in root.findall(f"{_ATOM}entry"):
        title_el = entry.find(f"{_ATOM}title")
        title = html.unescape("".join(title_el.itertext()).strip()) if title_el is not None else ""
        link_el = entry.find(f"{_ATOM}link")
        thread_url = (link_el.get("href") or "").strip() if link_el is not None else ""
        if not title or not thread_url:
            continue

        content_el = entry.find(f"{_ATOM}content")
        raw_html = (
            html.unescape("".join(content_el.itertext()))
            if content_el is not None
            else ""
        )
        m = _LINK_IN_CONTENT.search(raw_html)
        ext_url = (m.group(1).strip() if m else "") or ""
        if ext_url.startswith("//"):
            ext_url = "https:" + ext_url

        deal_href = ext_url if ext_url and not ext_url.startswith("https://www.reddit.com") else thread_url
        is_self = not ext_url or ext_url.startswith("https://www.reddit.com")

        if _skip_post_by_title_url(title, deal_href):
            continue

        id_el = entry.find(f"{_ATOM}id")
        pid = (id_el.text or "").strip() if id_el is not None else thread_url

        thumb_el = entry.find(f"{_MEDIA}thumbnail")
        media_u: str | None = None
        if thumb_el is not None:
            u = thumb_el.get("url")
            if isinstance(u, str) and u.startswith("http"):
                media_u = html.unescape(u)
        thumb = reddit_atom_best_thumbnail(raw_html, media_u)

        flair_m = re.match(r"^\s*(\[[^\]]+\])", title)
        flair = flair_m.group(1) if flair_m else None

        out.append(
            {
                "id": pid,
                "title": title,
                "deal_url": deal_href,
                "reddit_url": thread_url,
                "score": 0,
                "flair": flair,
                "created_utc": _atom_published_ts(entry),
                "thumbnail": thumb,
                "is_self_post": is_self,
            }
        )
    return out


def _normalize_posts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    children = (payload.get("data") or {}).get("children") or []
    for child in children:
        if not isinstance(child, dict) or child.get("kind") != "t3":
            continue
        d = child.get("data") or {}
        if not isinstance(d, dict):
            continue
        title = html.unescape((d.get("title") or "").strip())
        ext_url = (d.get("url_overridden_by_dest") or d.get("url") or "").strip()
        permalink = d.get("permalink") or ""
        if permalink.startswith("/"):
            reddit_url = f"https://www.reddit.com{permalink}"
        else:
            reddit_url = permalink or ""

        if _skip_post(title, ext_url, d):
            continue

        # Self-posts: still show with link to Reddit (no external store)
        is_self = bool(d.get("is_self"))
        deal_href = ext_url if ext_url and not ext_url.startswith("https://www.reddit.com") else reddit_url

        flair = html.unescape((d.get("link_flair_text") or "").strip()) or None
        score = int(d.get("score") or 0)
        created = float(d.get("created_utc") or d.get("created") or 0)

        # --- Image selection (priority order) ---
        # 1. Direct image link in post URL (i.redd.it, imgur, etc.) — always reliable
        thumb = reddit_json_direct_listing_image_url(d)

        # 2. Amazon product image via ASIN (most r/buildapcsales posts link to Amazon)
        if not thumb:
            asin = extract_amazon_asin(ext_url)
            if asin:
                thumb = amazon_product_image_url(asin)

        # 2b. B&H Photo CDN — construct image URL directly from product ID in their URL
        if not thumb and "bhphotovideo.com" in ext_url:
            thumb = bh_product_image_url(ext_url)

        # 3. preview.redd.it (native Reddit-hosted images) — skip external-preview.redd.it
        #    (external-preview.redd.it is Reddit's CDN copy of product images; it 403s all
        #     server-side requests regardless of UA/Referer, so we skip it entirely)
        if not thumb:
            candidate = reddit_json_best_image_url(d)
            if candidate and "external-preview.redd.it" not in candidate:
                thumb = candidate

        # 4. Small Reddit thumbnail (b.thumbs.redditmedia.com / a.thumbs.redditmedia.com)
        #    These are ~70x70px but reliably accessible via the proxy.
        if not thumb:
            t = d.get("thumbnail")
            if isinstance(t, str) and t not in ("self", "default", "nsfw", ""):
                # Don't upgrade redd.it URLs here — just use as-is so it hits the proxy
                thumb = html.unescape(t.replace("&amp;", "&")) if t.startswith("http") else None

        pid = d.get("name") or d.get("id") or reddit_url

        out.append(
            {
                "id": pid,
                "title": title,
                "deal_url": deal_href,
                "reddit_url": reddit_url,
                "score": score,
                "flair": flair,
                "created_utc": created,
                "thumbnail": thumb,
                "is_self_post": is_self,
            }
        )
    return out


_PC_HINT = re.compile(
    r"\b(gpu|graphics|gtx|rtx|rx\s?\d{3,4}|geforce|radeon|arc\s?a\d|video card|"
    r"cpu|processor|ryzen|threadripper|intel core|\bi\d[-\s]?\d{3,4}\b|xeon|"
    r"ssd|nvme|hdd|ram|ddr[45]|memory|dimm|"
    r"motherboard|mobo|\b(b|x|z|h)\d{3}\b|am5|am4|lga\s?1[67]00|"
    r"psu|power supply|\d{3,4}\s*w(?:att)?\b|80\s?plus|"
    r"monitor|ultragear|\d{2,3}\s*hz|144hz|240hz|4k uhd|"
    r"laptop|macbook|thinkpad|chromebook|notebook|"
    r"keyboard|mechanical keyboard|mouse\b|headset|webcam|"
    r"pc case|mid tower|full tower|cpu cooler|aio cooler|liquid cooler|"
    r"router|mesh|wifi\s?[67]e?|nas\b|"
    r"usb-?c.*power bank|gan charger|wall charger)\b",
    re.I,
)


async def _fetch_reddit_hot_json() -> tuple[list[dict[str, Any]], str | None]:
    httpx_err: str | None = None
    async with httpx.AsyncClient(
        timeout=22.0,
        follow_redirects=True,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        },
    ) as client:
        try:
            r = await client.get(REDDIT_HOT)
            r.raise_for_status()
            payload = r.json()
        except Exception as e:
            httpx_err = str(e)
            logger.warning("Reddit JSON fetch failed (httpx): %s", e)
            body, fb_err = await resilient_get_text(
                REDDIT_HOT,
                accept="application/json",
                user_agent=UA,
            )
            if body:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    return [], f"{httpx_err} | fallback: invalid JSON ({fb_err or 'parse'})"
                if isinstance(payload, dict):
                    items = _normalize_posts(payload)
                    items.sort(key=lambda x: -x["score"])
                    return items[:30], None
                return [], f"{httpx_err} | fallback: unexpected JSON shape"
            return [], f"{httpx_err} | fallback: {fb_err or 'failed'}"
        if not isinstance(payload, dict):
            return [], "Unexpected Reddit response"

    items = _normalize_posts(payload)
    items.sort(key=lambda x: -x["score"])
    return items[:30], None


async def _fetch_reddit_hot_atom() -> tuple[list[dict[str, Any]], str | None]:
    httpx_err: str | None = None
    text: str | None = None
    async with httpx.AsyncClient(
        timeout=22.0,
        follow_redirects=True,
        headers={
            "User-Agent": UA,
            "Accept": "application/atom+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    ) as client:
        try:
            r = await client.get(REDDIT_HOT_ATOM)
            r.raise_for_status()
            text = r.text
        except Exception as e:
            httpx_err = str(e)
            logger.warning("Reddit Atom fetch failed (httpx): %s", e)
            body, fb_err = await resilient_get_text(
                REDDIT_HOT_ATOM,
                accept="application/atom+xml,application/xml;q=0.9,*/*;q=0.8",
                user_agent=UA,
            )
            if body:
                items = _normalize_atom_feed(body)
                items.sort(key=lambda x: -float(x.get("created_utc") or 0))
                return items[:30], None
            return [], f"{httpx_err} | fallback: {fb_err or 'failed'}"

    assert text is not None
    items = _normalize_atom_feed(text)
    items.sort(key=lambda x: -float(x.get("created_utc") or 0))
    return items[:30], None


async def _fetch_reddit_hot() -> tuple[list[dict[str, Any]], str | None]:
    items, j_err = await _fetch_reddit_hot_json()
    if items:
        return items, None
    items, a_err = await _fetch_reddit_hot_atom()
    if items:
        return items, None
    errs = [x for x in (j_err, a_err) if x]
    return [], " | ".join(errs) if errs else "Reddit unavailable"


async def _enrich_thumbnails(items: list[dict[str, Any]]) -> None:
    """
    For items that still have external-preview.redd.it thumbnails (blocked server-side),
    replace them with images scraped from the actual product page (OG image).
    Runs all lookups concurrently with a cap, times out gracefully.
    """
    needs_enrich = [
        i for i in items
        if not i.get("thumbnail")
        or "external-preview.redd.it" in (i.get("thumbnail") or "")
    ]
    if not needs_enrich:
        return

    async def _enrich_one(item: dict[str, Any]) -> None:
        url = item.get("deal_url") or ""
        if not url:
            return
        try:
            img = await asyncio.wait_for(
                og_image_for_url_async(url),
                timeout=10,
            )
            if img:
                item["thumbnail"] = img
            elif "external-preview.redd.it" in (item.get("thumbnail") or ""):
                # Drop the blocked URL rather than serve a broken image
                item["thumbnail"] = None
        except Exception:
            if "external-preview.redd.it" in (item.get("thumbnail") or ""):
                item["thumbnail"] = None

    await asyncio.gather(*[_enrich_one(i) for i in needs_enrich])


async def fetch_curated_deals() -> tuple[list[dict[str, Any]], str | None]:
    """
    Product deals: r/buildapcsales (JSON, then Atom RSS, then curl fallback if httpx is 403'd)
    merged with Slickdeals RSS (multiple feeds; httpx then curl). Bookmarks only if all sources fail.
    """
    r_items, r_err = await _fetch_reddit_hot()
    sd_items, sd_err = await fetch_slickdeals_frontpage()

    for it in r_items:
        it["source"] = "reddit"
        it["_sort"] = int(it.get("score") or 0) + 4000

    # Enrich Reddit items that lack good thumbnails (external-preview.redd.it is blocked
    # server-side; we replace them with OG images from the actual product pages)
    await _enrich_thumbnails(r_items)

    for it in sd_items:
        it["source"] = "slickdeals"
        base = int(it.get("score") or 0)
        if _PC_HINT.search(it.get("title", "")):
            base += 2800
        it["_sort"] = base

    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for bucket in (r_items, sd_items):
        for it in bucket:
            key = (it.get("deal_url") or it.get("reddit_url") or it.get("id") or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(it)

    merged.sort(key=lambda x: -int(x.get("_sort", 0)))
    for it in merged:
        it.pop("_sort", None)

    # Cap Reddit-only dominance: guarantee at least 6 Slickdeals slots so images always appear
    reddit_part = [i for i in merged if i.get("source") == "reddit"][:20]
    sd_part = [i for i in merged if i.get("source") == "slickdeals"][:12]
    combined = reddit_part + sd_part
    combined.sort(key=lambda x: 0)  # preserve existing order (already sorted by _sort above)
    # Simple interleave: keep score-sorted order but ensure at least some SD entries
    final: list[dict[str, Any]] = []
    sd_queue = [i for i in merged if i.get("source") == "slickdeals"]
    sd_inserted = 0
    for it in merged:
        if it.get("source") == "reddit" and len(final) < 28:
            final.append(it)
        if len(final) % 4 == 3 and sd_queue and sd_inserted < 8:
            final.append(sd_queue.pop(0))
            sd_inserted += 1
    # Fill remaining SD items at the end up to 28
    for it in sd_queue:
        if len(final) >= 28:
            break
        final.append(it)
    merged = final[:28]

    if merged:
        return merged, None

    errs = [x for x in (r_err, sd_err) if x]
    return [], " | ".join(errs) if errs else "No deals available"
