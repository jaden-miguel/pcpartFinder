from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class HttpSettings:
    timeout_seconds: float = 25.0
    user_agent: str = "pcFinderDealBot/1.0"
    verify_ssl: bool = True


@dataclass
class Watch:
    id: str
    name: str
    url: str
    price_selector: str
    max_price: float | None = None
    min_drop_percent: float | None = None
    baseline_price: float | None = None
    min_discount_percent_vs_baseline: float | None = None
    currency: str = "USD"
    alert_cooldown_hours: float | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> Watch:
        return Watch(
            id=d["id"],
            name=d.get("name", d["id"]),
            url=d["url"],
            price_selector=d["price_selector"],
            max_price=_optional_float(d.get("max_price")),
            min_drop_percent=_optional_float(d.get("min_drop_percent")),
            baseline_price=_optional_float(d.get("baseline_price")),
            min_discount_percent_vs_baseline=_optional_float(
                d.get("min_discount_percent_vs_baseline")
            ),
            currency=str(d.get("currency", "USD")),
            alert_cooldown_hours=_optional_float(d.get("alert_cooldown_hours")),
        )


def _optional_float(v: Any) -> float | None:
    if v is None:
        return None
    return float(v)


@dataclass
class AppConfig:
    scan_interval_minutes: int
    apprise_urls: list[str]
    watches: list[Watch]
    http: HttpSettings = field(default_factory=HttpSettings)
    state_path: Path = field(default_factory=lambda: Path("data/state.json"))
    default_alert_cooldown_hours: float = 12.0
    auto_start_scanner: bool = False

    @staticmethod
    def from_dict(d: dict[str, Any], base_dir: Path) -> AppConfig:
        http = d.get("http") or {}
        state_rel = d.get("state_path", "data/state.json")
        return AppConfig(
            scan_interval_minutes=int(d.get("scan_interval_minutes", 30)),
            apprise_urls=list(d.get("apprise_urls") or []),
            watches=[Watch.from_dict(w) for w in (d.get("watches") or [])],
            http=HttpSettings(
                timeout_seconds=float(http.get("timeout_seconds", 25)),
                user_agent=str(
                    http.get("user_agent", "pcFinderDealBot/1.0 (personal use)")
                ),
                verify_ssl=bool(http.get("verify_ssl", True)),
            ),
            state_path=(base_dir / state_rel).resolve(),
            default_alert_cooldown_hours=float(
                d.get("default_alert_cooldown_hours", 12.0)
            ),
            auto_start_scanner=bool(d.get("auto_start_scanner", False)),
        )
