from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pcfinder.models import AppConfig, HttpSettings, Watch


def yaml_to_config(data: dict[str, Any], base_dir: Path) -> AppConfig:
    return AppConfig.from_dict(data, base_dir=base_dir)


def config_to_yaml_dict(cfg: AppConfig) -> dict[str, Any]:
    watches: list[dict[str, Any]] = []
    for w in cfg.watches:
        d: dict[str, Any] = {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "price_selector": w.price_selector,
            "currency": w.currency,
        }
        if w.max_price is not None:
            d["max_price"] = w.max_price
        if w.min_drop_percent is not None:
            d["min_drop_percent"] = w.min_drop_percent
        if w.baseline_price is not None:
            d["baseline_price"] = w.baseline_price
        if w.min_discount_percent_vs_baseline is not None:
            d["min_discount_percent_vs_baseline"] = w.min_discount_percent_vs_baseline
        if w.alert_cooldown_hours is not None:
            d["alert_cooldown_hours"] = w.alert_cooldown_hours
        watches.append(d)

    return {
        "scan_interval_minutes": cfg.scan_interval_minutes,
        "default_alert_cooldown_hours": cfg.default_alert_cooldown_hours,
        "auto_start_scanner": cfg.auto_start_scanner,
        "apprise_urls": cfg.apprise_urls,
        "http": {
            "timeout_seconds": cfg.http.timeout_seconds,
            "user_agent": cfg.http.user_agent,
            "verify_ssl": cfg.http.verify_ssl,
        },
        "watches": watches,
    }


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")


def load_app_config(path: Path) -> AppConfig:
    data = read_yaml(path)
    base = path.parent.resolve()
    if not data:
        return AppConfig(
            scan_interval_minutes=30,
            apprise_urls=[],
            watches=[],
            http=HttpSettings(),
            state_path=(base / "data/state.json").resolve(),
            default_alert_cooldown_hours=12.0,
        )
    return yaml_to_config(data, base)


def save_app_config(path: Path, cfg: AppConfig) -> None:
    write_yaml(path, config_to_yaml_dict(cfg))
