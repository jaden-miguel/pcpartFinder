from __future__ import annotations

from pcfinder.models import Watch


def collect_deal_reasons(
    watch: Watch,
    price: float,
    previous_scan_price: float | None,
) -> list[str]:
    """
    Reasons the current price matches the user's deal rules (for UI + alerts).
    previous_scan_price is the stored last_price before this scan (for drop %).
    """
    reasons: list[str] = []

    if watch.max_price is not None and price <= watch.max_price:
        reasons.append(f"at or below max ({watch.currency} {watch.max_price:.2f})")

    if (
        watch.baseline_price is not None
        and watch.min_discount_percent_vs_baseline is not None
    ):
        threshold = watch.baseline_price * (
            1.0 - watch.min_discount_percent_vs_baseline / 100.0
        )
        if price <= threshold:
            reasons.append(
                f"≥{watch.min_discount_percent_vs_baseline:.0f}% under baseline "
                f"({watch.currency} {watch.baseline_price:.2f})"
            )

    if watch.min_drop_percent is not None and previous_scan_price is not None:
        if previous_scan_price > 0:
            pct = (previous_scan_price - price) / previous_scan_price * 100.0
            if pct >= watch.min_drop_percent:
                reasons.append(
                    f"dropped {pct:.1f}% vs last scan ({watch.currency} {previous_scan_price:.2f})"
                )

    return reasons
