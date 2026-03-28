from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class WatchState:
    last_price: float | None = None
    last_alert_ts: float | None = None
    was_in_deal: bool = False

    @staticmethod
    def from_dict(d: dict[str, Any]) -> WatchState:
        return WatchState(
            last_price=_f(d.get("last_price")),
            last_alert_ts=_f(d.get("last_alert_ts")),
            was_in_deal=bool(
                d.get("was_in_deal", d.get("last_ok_deal", False))
            ),
        )


def _f(v: Any) -> float | None:
    if v is None:
        return None
    return float(v)


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._watches: dict[str, WatchState] = {}

    def load(self) -> None:
        if not self.path.exists():
            self._watches = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("State load failed (%s), starting fresh", e)
            self._watches = {}
            return
        watches = raw.get("watches") or {}
        self._watches = {
            k: WatchState.from_dict(v) if isinstance(v, dict) else WatchState()
            for k, v in watches.items()
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "watches": {wid: asdict(ws) for wid, ws in self._watches.items()},
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self, watch_id: str) -> WatchState:
        if watch_id not in self._watches:
            self._watches[watch_id] = WatchState()
        return self._watches[watch_id]

    def update(self, watch_id: str, **kwargs: Any) -> None:
        ws = self.get(watch_id)
        for k, v in kwargs.items():
            setattr(ws, k, v)
