"""Supervisor config loading helpers."""

from __future__ import annotations

import os
from typing import Optional

from ouroboros.config import OuroborosConfig


def _userdata_get(name: str) -> Optional[str]:
    try:
        from google.colab import userdata  # type: ignore
    except Exception:
        return None
    try:
        return userdata.get(name)
    except Exception:
        return None


def get_secret(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    value = _userdata_get(name)
    if value is None or not str(value).strip():
        value = os.environ.get(name, default)
    if required and (value is None or not str(value).strip()):
        raise AssertionError(f"Missing required secret: {name}")
    return value


def load_config() -> OuroborosConfig:
    def _secret_fn(name: str) -> Optional[str]:
        value = get_secret(name)
        return str(value) if value is not None else None

    cfg = OuroborosConfig.from_env(secret_fn=_secret_fn)
    cfg.to_env()
    return cfg
