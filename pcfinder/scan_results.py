from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def scan_results_path(state_path: Path) -> Path:
    return state_path.parent / "scan_results.json"


def write_scan_results(
    path: Path,
    items: list[dict[str, Any]],
    scan_finished_at: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "scan_finished_at": scan_finished_at
        or datetime.now(timezone.utc).isoformat(),
        "items": items,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_scan_results(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "scan_finished_at": None,
            "items": [],
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Could not read scan results: %s", e)
        return {
            "scan_finished_at": None,
            "items": [],
        }
    if not isinstance(data, dict):
        return {"scan_finished_at": None, "items": []}
    items = data.get("items")
    if not isinstance(items, list):
        items = []
    return {
        "scan_finished_at": data.get("scan_finished_at"),
        "items": items,
    }
