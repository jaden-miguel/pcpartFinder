from __future__ import annotations

import logging
from pathlib import Path

import yaml

from pcfinder.models import AppConfig

logger = logging.getLogger(__name__)


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Copy config.example.yaml to config.yaml and edit."
        )
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("config must be a YAML mapping")
    base = path.parent.resolve()
    cfg = AppConfig.from_dict(data, base_dir=base)
    if not cfg.watches:
        logger.warning("No watches configured")
    if not cfg.apprise_urls:
        logger.warning("No apprise_urls — you will only see log output")
    return cfg
