"""Typed runtime configuration for Ouroboros."""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Callable, Dict, Optional


def _parse_int(raw: Optional[str], default: int, minimum: int = 0) -> int:
    try:
        val = int(str(raw))
    except Exception:
        val = default
    return max(minimum, val)


def _parse_budget(raw: Optional[str], default: float = 0.0) -> float:
    text = str(raw or "")
    cleaned = re.sub(r"[^0-9.\-]", "", text)
    try:
        return float(cleaned) if cleaned else default
    except Exception:
        return default


@dataclass(frozen=True)
class OuroborosConfig:
    openrouter_api_key: str
    telegram_bot_token: str
    github_token: str
    github_user: str
    github_repo: str
    total_budget: float
    model_main: str = "anthropic/claude-sonnet-4.6"
    model_code: str = "anthropic/claude-sonnet-4.6"
    model_light: str = "google/gemini-3-pro-preview"
    max_workers: int = 5
    soft_timeout_sec: int = 600
    hard_timeout_sec: int = 1800
    branch_dev: str = "ouroboros"
    branch_stable: str = "ouroboros-stable"
    drive_root: str = "/content/drive/MyDrive/Ouroboros"
    repo_dir: str = "/content/ouroboros_repo"
    diag_heartbeat_sec: int = 30
    diag_slow_cycle_sec: int = 20

    @classmethod
    def from_env(cls, secret_fn: Callable[[str], Optional[str]] = os.environ.get) -> "OuroborosConfig":
        def _first(*values: Optional[str], default: Optional[str] = None) -> Optional[str]:
            for value in values:
                if value is not None and str(value).strip():
                    return value
            return default

        openrouter_api_key = _first(os.environ.get("OPENROUTER_API_KEY"), secret_fn("OPENROUTER_API_KEY"), default="") or ""
        telegram_bot_token = _first(os.environ.get("TELEGRAM_BOT_TOKEN"), secret_fn("TELEGRAM_BOT_TOKEN"), default="") or ""
        github_token = _first(os.environ.get("GITHUB_TOKEN"), secret_fn("GITHUB_TOKEN"), default="") or ""
        github_user = _first(os.environ.get("GITHUB_USER"), secret_fn("GITHUB_USER"), default="") or ""
        github_repo = _first(os.environ.get("GITHUB_REPO"), secret_fn("GITHUB_REPO"), default="") or ""
        total_budget_raw = _first(os.environ.get("TOTAL_BUDGET"), secret_fn("TOTAL_BUDGET"), default="0") or "0"

        if not openrouter_api_key:
            raise ValueError("Missing OPENROUTER_API_KEY")
        if not telegram_bot_token:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN")
        if not github_token:
            raise ValueError("Missing GITHUB_TOKEN")
        if not github_user:
            raise ValueError("Missing GITHUB_USER")
        if not github_repo:
            raise ValueError("Missing GITHUB_REPO")

        return cls(
            openrouter_api_key=openrouter_api_key,
            telegram_bot_token=telegram_bot_token,
            github_token=github_token,
            github_user=github_user,
            github_repo=github_repo,
            total_budget=_parse_budget(total_budget_raw, default=0.0),
            model_main=_first(os.environ.get("OUROBOROS_MODEL"), secret_fn("OUROBOROS_MODEL"), default="anthropic/claude-sonnet-4.6") or "anthropic/claude-sonnet-4.6",
            model_code=_first(os.environ.get("OUROBOROS_MODEL_CODE"), secret_fn("OUROBOROS_MODEL_CODE"), default="anthropic/claude-sonnet-4.6") or "anthropic/claude-sonnet-4.6",
            model_light=_first(os.environ.get("OUROBOROS_MODEL_LIGHT"), secret_fn("OUROBOROS_MODEL_LIGHT"), default="google/gemini-3-pro-preview") or "google/gemini-3-pro-preview",
            max_workers=_parse_int(_first(os.environ.get("OUROBOROS_MAX_WORKERS"), secret_fn("OUROBOROS_MAX_WORKERS"), default="5"), 5, 1),
            soft_timeout_sec=_parse_int(_first(os.environ.get("OUROBOROS_SOFT_TIMEOUT_SEC"), secret_fn("OUROBOROS_SOFT_TIMEOUT_SEC"), default="600"), 600, 60),
            hard_timeout_sec=_parse_int(_first(os.environ.get("OUROBOROS_HARD_TIMEOUT_SEC"), secret_fn("OUROBOROS_HARD_TIMEOUT_SEC"), default="1800"), 1800, 120),
            branch_dev=_first(os.environ.get("OUROBOROS_BRANCH_DEV"), secret_fn("OUROBOROS_BRANCH_DEV"), default="ouroboros") or "ouroboros",
            branch_stable=_first(os.environ.get("OUROBOROS_BRANCH_STABLE"), secret_fn("OUROBOROS_BRANCH_STABLE"), default="ouroboros-stable") or "ouroboros-stable",
            drive_root=_first(os.environ.get("OUROBOROS_DRIVE_ROOT"), secret_fn("OUROBOROS_DRIVE_ROOT"), default="/content/drive/MyDrive/Ouroboros") or "/content/drive/MyDrive/Ouroboros",
            repo_dir=_first(os.environ.get("OUROBOROS_REPO_DIR"), secret_fn("OUROBOROS_REPO_DIR"), default="/content/ouroboros_repo") or "/content/ouroboros_repo",
            diag_heartbeat_sec=_parse_int(_first(os.environ.get("OUROBOROS_DIAG_HEARTBEAT_SEC"), secret_fn("OUROBOROS_DIAG_HEARTBEAT_SEC"), default="30"), 30, 0),
            diag_slow_cycle_sec=_parse_int(_first(os.environ.get("OUROBOROS_DIAG_SLOW_CYCLE_SEC"), secret_fn("OUROBOROS_DIAG_SLOW_CYCLE_SEC"), default="20"), 20, 0),
        )

    def to_env(self) -> Dict[str, str]:
        exports = {
            "OPENROUTER_API_KEY": self.openrouter_api_key,
            "TELEGRAM_BOT_TOKEN": self.telegram_bot_token,
            "GITHUB_TOKEN": self.github_token,
            "GITHUB_USER": self.github_user,
            "GITHUB_REPO": self.github_repo,
            "TOTAL_BUDGET": str(self.total_budget),
            "OUROBOROS_MODEL": self.model_main,
            "OUROBOROS_MODEL_CODE": self.model_code,
            "OUROBOROS_MODEL_LIGHT": self.model_light,
            "OUROBOROS_MAX_WORKERS": str(self.max_workers),
            "OUROBOROS_SOFT_TIMEOUT_SEC": str(self.soft_timeout_sec),
            "OUROBOROS_HARD_TIMEOUT_SEC": str(self.hard_timeout_sec),
            "OUROBOROS_BRANCH_DEV": self.branch_dev,
            "OUROBOROS_BRANCH_STABLE": self.branch_stable,
            "OUROBOROS_DRIVE_ROOT": self.drive_root,
            "OUROBOROS_REPO_DIR": self.repo_dir,
            "OUROBOROS_DIAG_HEARTBEAT_SEC": str(self.diag_heartbeat_sec),
            "OUROBOROS_DIAG_SLOW_CYCLE_SEC": str(self.diag_slow_cycle_sec),
        }
        for key, value in exports.items():
            os.environ[key] = value
        return exports
