"""Typed supervisor runtime context."""

from __future__ import annotations

import pathlib
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from ouroboros.config import OuroborosConfig


class TelegramLike(Protocol):
    def send_chat_action(self, chat_id: int, action: str = "typing") -> bool:
        ...

    def send_photo(self, chat_id: int, photo_bytes: bytes, caption: str = "") -> tuple[bool, str]:
        ...


class WorkerLike(Protocol):
    busy_task_id: Optional[str]


class ConsciousnessLike(Protocol):
    @property
    def is_running(self) -> bool:
        ...

    def start(self) -> str:
        ...

    def stop(self) -> str:
        ...


class SupervisorEventContext(Protocol):
    drive_root: pathlib.Path
    repo_dir: pathlib.Path
    branch_dev: str
    branch_stable: str
    tg: TelegramLike
    workers: Dict[int, WorkerLike]
    pending: List[Dict[str, Any]]
    running: Dict[str, Dict[str, Any]]
    consciousness: ConsciousnessLike

    def send_with_budget(self, chat_id: int, text: str, **kwargs: Any) -> None:
        ...

    def load_state(self) -> Dict[str, Any]:
        ...

    def save_state(self, st: Dict[str, Any]) -> None:
        ...

    def update_budget_from_usage(self, usage: Dict[str, Any]) -> None:
        ...

    def append_jsonl(self, path: pathlib.Path, obj: Dict[str, Any]) -> None:
        ...

    def enqueue_task(self, task: Dict[str, Any]) -> None:
        ...

    def cancel_task_by_id(self, task_id: str) -> bool:
        ...

    def queue_review_task(self, *, reason: str, force: bool) -> None:
        ...

    def persist_queue_snapshot(self, *, reason: str) -> None:
        ...

    def safe_restart(self, *, reason: str, unsynced_policy: str) -> tuple[bool, str]:
        ...

    def kill_workers(self) -> None:
        ...

    def sort_pending(self) -> None:
        ...


@dataclass
class SupervisorContext:
    config: OuroborosConfig
    drive_root: pathlib.Path
    repo_dir: pathlib.Path
    tg: TelegramLike
    workers: Dict[int, Any] = field(default_factory=dict)
    pending: List[Dict[str, Any]] = field(default_factory=list)
    running: Dict[str, Any] = field(default_factory=dict)
    consciousness: Optional[ConsciousnessLike] = None
    queue_lock: threading.Lock = field(default_factory=threading.Lock)
