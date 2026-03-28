from __future__ import annotations

import logging

import apprise

from pcfinder.deals import DealEvent

logger = logging.getLogger(__name__)


def send_plain_notification(urls: list[str], title: str, body: str) -> bool:
    if not urls:
        return False
    a = apprise.Apprise()
    for u in urls:
        a.add(u)
    return bool(a.notify(title=title, body=body))


def send_deal_alert(urls: list[str], event: DealEvent) -> bool:
    if not urls:
        logger.warning("No apprise_urls configured; skipping notification")
        return False
    a = apprise.Apprise()
    for u in urls:
        a.add(u)
    ok = a.notify(title=event.title, body=event.body)
    if not ok:
        logger.error("Apprise failed to send notification")
    return bool(ok)
