from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

from pcfinder.models import HttpSettings
from pcfinder.parse_price import parse_price_text

logger = logging.getLogger(__name__)


async def fetch_price(
    url: str,
    price_selector: str,
    http: HttpSettings,
) -> tuple[float | None, str | None]:
    headers = {"User-Agent": http.user_agent, "Accept-Language": "en-US,en;q=0.9"}
    try:
        async with httpx.AsyncClient(
            timeout=http.timeout_seconds,
            follow_redirects=True,
            headers=headers,
            verify=http.verify_ssl,
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("HTTP error for %s: %s", url, e)
        return None, str(e)

    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.select_one(price_selector)
    if el is None:
        logger.warning("Selector %r matched nothing on %s", price_selector, url)
        return None, "selector_miss"

    text = el.get_text(" ", strip=True)
    if not text and el.has_attr("content"):
        text = str(el["content"])
    price = parse_price_text(text)
    if price is None:
        logger.warning("Could not parse price from %r on %s", text, url)
        return None, "parse_fail"
    return price, None
