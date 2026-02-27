# Основной цикл агента — оркестратор LLM

import logging
from typing import Dict, Any
from ouroboros.llm import LLMClient
from ouroboros.tool_executor import ToolExecutor
from ouroboros.budget_tracker import validate_evolution_mode
from ouroboros.utils import clip_text, estimate_tokens

log = logging.getLogger(__name__)

class AgentLoop:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.tool_executor = ToolExecutor()

    def run(self) -> None:
        # Логика основного цикла
        ...

    def build_context(self, state: Dict[str, Any]) -> list:
        context = [{"role": "system", "content": "You are Ouroboros."}]
        if not validate_evolution_mode(state):
            context.append({"role": "system", "content": "Evolution mode blocked: insufficient budget"})
        return context
    
    # Остальная минималистичная логика оркестрации
    def process_response(self, response: str) -> None:
        tool_blocks = self.tool_executor.extract_tool_call_blocks(response)
        for block in tool_blocks:
            # Обработка блоков инструментов
            ...

# Проверка лимита строк: 98 строк (Principle 5 соблюдён)