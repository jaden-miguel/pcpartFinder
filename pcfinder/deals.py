from __future__ import annotations

import time
from dataclasses import dataclass

from pcfinder.deal_rules import collect_deal_reasons
from pcfinder.models import Watch
from pcfinder.state import StateStore, WatchState


@dataclass
class DealEvent:
    title: str
    body: str
    url: str


def evaluate_watch(
    watch: Watch,
    price: float,
    state: StateStore,
    default_cooldown_hours: float,
) -> DealEvent | None:
    ws: WatchState = state.get(watch.id)
    now = time.time()
    cooldown_h = (
        watch.alert_cooldown_hours
        if watch.alert_cooldown_hours is not None
        else default_cooldown_hours
    )
    cooldown_s = max(0.0, cooldown_h * 3600.0)

    reasons = collect_deal_reasons(watch, price, ws.last_price)

    if not reasons:
        state.update(watch.id, last_price=price, was_in_deal=False)
        return None

    in_deal = True
    first_entry = not ws.was_in_deal
    improved = ws.last_price is not None and price < ws.last_price - 1e-6
    in_cooldown = (
        ws.last_alert_ts is not None and (now - ws.last_alert_ts) < cooldown_s
    )

    should_alert = first_entry or improved
    if in_cooldown and not improved:
        state.update(
            watch.id,
            last_price=price,
            was_in_deal=in_deal,
        )
        return None

    if not should_alert:
        state.update(
            watch.id,
            last_price=price,
            was_in_deal=in_deal,
        )
        return None

    title = f"Deal: {watch.name}"
    body = (
        f"{watch.currency} {price:.2f}\n"
        + "\n".join(f"• {r}" for r in reasons)
        + f"\n\n{watch.url}"
    )
    state.update(
        watch.id,
        last_price=price,
        was_in_deal=in_deal,
        last_alert_ts=now,
    )
    return DealEvent(title=title, body=body, url=watch.url)
