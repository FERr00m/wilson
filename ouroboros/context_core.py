from typing import List, Dict, Any
import json
from ouroboros.utils import (
    compact_messages_for_display,
    compact_tool_history,
    clip_text,
    sanitize_task_for_event
)

def _build_runtime_section(state: dict, tasks: list) -> str:
    # ... runtime section implementation
    return "Runtime: [data]"

def _build_memory_sections(scratchpad: str, identity: str) -> str:
    # ... memory sections implementation
    return "Scratchpad: [data]\nIdentity: [data]"

def _build_health_invariants() -> str:
    # ... health checks
    return "Health: OK"

def build_llm_messages(context: dict) -> List[Dict[str, str]]:
    # Core message building logic
    return compact_messages_for_display([
        {"role": "system", "content": context['system_prompt']},
        *[...],
        {"role": "user", "content": context['user_prompt']}
    ])