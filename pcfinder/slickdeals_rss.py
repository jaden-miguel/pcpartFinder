from __future__ import annotations

import html
import logging
import re
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from pcfinder.net_fallback import resilient_get_text
from pcfinder.thumb_hd import upgrade_slickdeals_thumb_url

logger = logging.getLogger(__name__)

SLICKDEALS_RSS_URLS: tuple[str, ...] = (
    "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&rss=1",
    "https://slickdeals.net/newsearch.php?searcharea=deals&search=GPU&rss=1",
    "https://slickdeals.net/newsearch.php?searcharea=deals&search=CPU+processor&rss=1",
    "https://slickdeals.net/newsearch.php?searcharea=deals&search=SSD+NVMe&rss=1",
    "https://slickdeals.net/newsearch.php?searcharea=deals&search=gaming+monitor&rss=1",
    "https://slickdeals.net/newsearch.php?searcharea=deals&search=gaming+laptop&rss=1",
)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

_NS_CONTENT = "{http://purl.org/rss/1.0/modules/content/}encoded"

# Must match at least one PC/tech keyword to be included
_PC_REQUIRED = re.compile(
    r"\b("
    # GPUs
    r"gpu|graphics\s+card|video\s+card|geforce|radeon|rtx\s*\d|gtx\s*\d|rx\s*\d{3,4}|"
    r"arc\s+[ab]\d|nvida|nvidia|amd\s+radeon|"
    # CPUs
    r"cpu|processor|ryzen|threadripper|intel\s+core|i\d[-\s]\d{3,5}|"
    r"core\s+ultra|xeon|athlon|"
    # Motherboards / chipsets
    r"motherboard|mobo|b\d{3}m?|x\d{3}|z\d{3}|h\d{3}|am[45]|lga\s*1[67]\d{2}|"
    # Memory / storage
    r"ssd|nvme|m\.2|hdd|hard\s+drive|ram|ddr[345]|so-?dimm|dimm|flash\s+drive|"
    r"microsd|sd\s+card|usb\s+drive|thumb\s+drive|external\s+(ssd|hdd|drive)|"
    # Cooling
    r"cpu\s+cooler|aio|all.in.one\s+cooler|liquid\s+cooler|liquid\s+cooling|"
    r"air\s+cooler|heatsink|thermal\s+paste|arctic\s+|noctua|be\s+quiet|"
    r"thermalright|deepcool|corsair\s+icue|"
    # Power supplies
    r"psu|power\s+supply|\d{3,4}\s*w(?:att)?\s*(psu|power|gold|platinum|modular)|"
    r"80\s+plus|atx\s+\d|sfx\s+\d|modular\s+psu|"
    # Cases
    r"pc\s+case|atx\s+case|mid.tower|full.tower|mini.itx|micro.atx|"
    # Monitors
    r"monitor|display|ips\s+panel|oled\s+monitor|qd.oled|miniled|"
    r"\d{2,3}hz|144\s*hz|165\s*hz|240\s*hz|360\s*hz|4k\s+monitor|ultrawide|"
    r"1440p|2160p|qhd|uhd|"
    # Laptops / desktops
    r"laptop|gaming\s+laptop|macbook|thinkpad|notebook|chromebook|"
    r"gaming\s+pc|prebuilt|desktop\s+pc|mini\s+pc|"
    # Peripherals
    r"mechanical\s+keyboard|gaming\s+keyboard|gaming\s+mouse|gaming\s+headset|"
    r"webcam|capture\s+card|stream\s+deck|"
    # Networking / NAS
    r"router|wifi\s*[67]|mesh\s+wifi|nas\b|network\s+switch|ethernet|"
    # Tablets / handhelds that belong here
    r"ipad|surface\s+pro|gaming\s+tablet|steam\s+deck|"
    # Accessories
    r"usb.c\s+hub|usb\s+hub|thunderbolt|kvm\s+switch|monitor\s+arm|"
    r"cable\s+management|pcie|"
    # Brand + generic signals
    r"asus|gigabyte|msi\b|evga|sapphire|xfx|powercolor|zotac|palit|inno3d|"
    r"corsair|g\.skill|kingston|crucial|western\s+digital|seagate|samsung\s+(ssd|nvme|evo|pro|t\d)|"
    r"intel\b|amd\b|nvidia\b|logitech\s+(g\d|mx)|razer\b|"
    r"nzxt|fractal\s+design|lian\s+li|phanteks|"
    r"ibuypower|cyberpowerpc|alienware|"
    r"prebuilt|gaming\s+desktop"
    r")\b",
    re.I,
)


def _parse_thumb_score(encoded: str) -> tuple[str | None, int]:
    thumb = None
    m_img = re.search(r'src="(https://static\.slickdealscdn\.com[^"]+)"', encoded)
    if m_img:
        thumb = html.unescape(m_img.group(1))
    score = 0
    m_ts = re.search(r"Thumb Score:\s*\+?(-?\d+)", encoded)
    if m_ts:
        score = int(m_ts.group(1))
    return thumb, score


def parse_slickdeals_rss(xml_text: str, limit: int = 70) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.warning("Slickdeals RSS parse error: %s", e)
        return []

    channel = root.find("channel")
    if channel is None:
        return []

    out: list[dict[str, Any]] = []
    for item in channel.findall("item"):
        if len(out) >= limit:
            break
        title_el = item.find("title")
        link_el = item.find("link")
        guid_el = item.find("guid")
        title = html.unescape("".join(title_el.itertext()).strip()) if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        guid = (guid_el.text or "").strip() if guid_el is not None else link
        if not title or not link:
            continue
        # Only include PC/tech deals — skip anything that doesn't match
        if not _PC_REQUIRED.search(title):
            continue

        enc_el = item.find(_NS_CONTENT)
        raw_enc = enc_el.text or "" if enc_el is not None else ""
        thumbnail, thumb_score = _parse_thumb_score(raw_enc)
        if thumbnail:
            thumbnail = upgrade_slickdeals_thumb_url(thumbnail)

        gid = re.sub(r"\W+", "-", guid)[:48] or str(len(out))

        out.append(
            {
                "id": f"sd-{gid}",
                "title": title,
                "deal_url": link,
                "reddit_url": link,
                "score": max(thumb_score, 0),
                "flair": "Slickdeals",
                "created_utc": 0.0,
                "thumbnail": thumbnail,
                "is_self_post": False,
                "is_bookmark": False,
                "source": "slickdeals",
            }
        )
    return out


async def fetch_slickdeals_frontpage() -> tuple[list[dict[str, Any]], str | None]:
    headers = {
        "User-Agent": UA,
        "Accept": "application/rss+xml, application/xml, text/xml, */*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://slickdeals.net/",
    }
    all_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    last_err: str | None = None

    async def _fetch_one(url: str) -> list[dict[str, Any]]:
        nonlocal last_err
        text: str | None = None
        async with httpx.AsyncClient(
            timeout=22.0,
            follow_redirects=True,
            headers=headers,
        ) as client:
            try:
                r = await client.get(url)
                r.raise_for_status()
                text = r.text
            except Exception as e:
                last_err = str(e)
                logger.warning("Slickdeals RSS fetch failed (httpx) %s: %s", url, e)
                body, fb_err = await resilient_get_text(
                    url,
                    accept="application/rss+xml, application/xml, text/xml, */*;q=0.8",
                    user_agent=UA,
                )
                if body:
                    text = body
                else:
                    last_err = f"{last_err} | fallback: {fb_err or 'failed'}"
                    return []
        if text is None:
            return []
        return parse_slickdeals_rss(text)

    # Fetch all feeds concurrently and merge, deduplicating by id
    import asyncio as _asyncio
    results = await _asyncio.gather(*[_fetch_one(u) for u in SLICKDEALS_RSS_URLS])
    for feed_items in results:
        for it in feed_items:
            iid = it.get("id") or it.get("deal_url") or ""
            if iid and iid not in seen_ids:
                seen_ids.add(iid)
                all_items.append(it)

    if all_items:
        return all_items, None
    return [], last_err or "Slickdeals RSS unavailable"
