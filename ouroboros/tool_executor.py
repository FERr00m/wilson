# Tool Execution Core

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ouroboros.utils import compact_tool_history


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

def extract_tool_call_blocks(tool_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Извлекает блоки вызовов инструментов из истории"""
    return compact_tool_history(tool_history)

class ToolExecutor:
    def __init__(self):
        self.tool_history = []

    def record_result(self, result: ToolResult):
        self.tool_history.append({
            "is_ok": result.is_ok,
            "summary": result.display_summary()
        })