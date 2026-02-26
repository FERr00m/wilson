"""Shared typed structures for Ouroboros runtime data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Literal, Optional, TypedDict


@dataclass
class TaskDict:
    id: str
    type: str
    chat_id: int
    text: str
    depth: int = 0
    priority: int = 5
    parent_task_id: Optional[str] = None
    image_base64: Optional[str] = None
    image_mime: str = "image/jpeg"
    image_caption: str = ""
    _is_direct_chat: bool = False
    _attempt: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskDict":
        return cls(
            id=str(data.get("id") or ""),
            type=str(data.get("type") or "task"),
            chat_id=int(data.get("chat_id") or 0),
            text=str(data.get("text") or ""),
            depth=int(data.get("depth") or 0),
            priority=int(data.get("priority") or 5),
            parent_task_id=str(data["parent_task_id"]) if data.get("parent_task_id") else None,
            image_base64=str(data["image_base64"]) if data.get("image_base64") else None,
            image_mime=str(data.get("image_mime") or "image/jpeg"),
            image_caption=str(data.get("image_caption") or ""),
            _is_direct_chat=bool(data.get("_is_direct_chat")),
            _attempt=int(data.get("_attempt") or 1),
        )


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    cost: float = 0.0
    rounds: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMUsage":
        return cls(
            prompt_tokens=int(data.get("prompt_tokens") or 0),
            completion_tokens=int(data.get("completion_tokens") or 0),
            total_tokens=int(data.get("total_tokens") or 0),
            cached_tokens=int(data.get("cached_tokens") or 0),
            cache_write_tokens=int(data.get("cache_write_tokens") or 0),
            cost=float(data.get("cost") or 0.0),
            rounds=int(data.get("rounds") or 0),
        )


# ---------------------------------------------------------------------------
# Typed worker/supervisor events
# ---------------------------------------------------------------------------

WorkerEventType = Literal[
    "llm_usage",
    "task_heartbeat",
    "typing_start",
    "send_message",
    "task_done",
    "task_metrics",
    "review_request",
    "restart_request",
    "promote_to_stable",
    "schedule_task",
    "cancel_task",
    "send_photo",
    "toggle_evolution",
    "toggle_consciousness",
    "owner_message_injected",
]


class BaseWorkerEvent(TypedDict):
    type: WorkerEventType


class LlmUsageEvent(BaseWorkerEvent, total=False):
    ts: str
    task_id: str
    usage: Dict[str, Any]
    category: str
    model: str


class TaskHeartbeatEvent(BaseWorkerEvent, total=False):
    task_id: str
    phase: str


class TypingStartEvent(BaseWorkerEvent, total=False):
    chat_id: int


class SendMessageEvent(BaseWorkerEvent, total=False):
    chat_id: int
    text: str
    format: str
    log_text: str
    is_progress: bool


class TaskDoneEvent(BaseWorkerEvent, total=False):
    ts: str
    task_id: str
    task_type: str
    worker_id: int
    cost_usd: float
    total_rounds: int


class TaskMetricsEvent(BaseWorkerEvent, total=False):
    task_id: str
    task_type: str
    duration_sec: float
    tool_calls: int
    tool_errors: int


class ReviewRequestEvent(BaseWorkerEvent, total=False):
    reason: str


class RestartRequestEvent(BaseWorkerEvent, total=False):
    reason: str


class PromoteToStableEvent(BaseWorkerEvent):
    pass


class ScheduleTaskEvent(BaseWorkerEvent, total=False):
    description: str
    context: str
    depth: int
    task_id: str
    parent_task_id: str


class CancelTaskEvent(BaseWorkerEvent, total=False):
    task_id: str


class SendPhotoEvent(BaseWorkerEvent, total=False):
    chat_id: int
    image_base64: str
    caption: str


class ToggleEvolutionEvent(BaseWorkerEvent, total=False):
    enabled: bool


class ToggleConsciousnessEvent(BaseWorkerEvent, total=False):
    action: str


class OwnerMessageInjectedEvent(BaseWorkerEvent, total=False):
    ts: str
    task_id: str
    text: str
