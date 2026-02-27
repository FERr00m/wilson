# Основной цикл агента — оркестратор LLM

from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any
import os
from contextlib import contextmanager
from ouroboros.llm import LLMClient
from ouroboros.utils import (
    clip_text,
    estimate_tokens,
    compact_tool_history,
    sanitize_task_for_event
)

log = logging.getLogger(__name__)

class ToolResult(ABC):
    """Базовый класс для результатов инструментов"""
    @property
    @abstractmethod
    def is_ok(self) -> bool:
        ...

    @property
    @abstractmethod
    def payload(self) -> Any:
        ...

    @abstractmethod
    def display_summary(self) -> str:
        ...

class AgentLoop:
    def __init__(self, llm_client: LLMClient, ...):
        self.llm_client = llm_client
        ...

    def run(self) -> None:
        ...

    def build_context(self, ...):
        ...

    def extract_tool_call_blocks(self, text: str) -> List[Dict[str, str]]:
        return compact_tool_history(self.tool_history)
    # ... остальные методы