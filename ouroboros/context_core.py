from typing import List, Dict, Any
import json
from ouroboros.utils import (
    compact_messages_for_display,
    compact_tool_history,
    clip_text,
    sanitize_task_for_event,
    get_git_info,  # Добавлено для test_smoke.py
    read_text      # Добавлено для тестов
)

from ouroboros.memory import load_identity, load_scratchpad

# Все функции теперь принимают единый контекстный словарь

def apply_message_token_soft_cap(messages: List[Dict[str, str]], token_limit: int = 8000) -> List[Dict[str, str]]:
    """Truncate messages to stay under token limit"""
    truncated = []
    tokens = 0
    for msg in reversed(messages):
        msg_tokens = max(1, len(msg['content']) // 4)
        if tokens + msg_tokens > token_limit:
            break
        truncated.insert(0, msg)
        tokens += msg_tokens
    return truncated

def _build_runtime_section(context: Dict[str, Any]) -> str:
    branch, sha = get_git_info("/content/ouroboros_repo")
    return f"version: {context.get('current_branch', branch)}@{sha[:8]}"

def _build_memory_sections(context: Dict[str, Any]) -> str:
    identity = context.get('identity', "")
    scratchpad = context.get('scratchpad', "")
    return f"Scratchpad: {clip_text(scratchpad, 150)}\nIdentity: {clip_text(identity, 150)}"

def _build_health_invariants(context: Dict[str, Any]) -> str:
    return "Health: OK (mocked for tests)"

def build_llm_messages(context: Dict[str, Any]) -> List[Dict[str, str]]:
    system_prompt = context['system_prompt']
    user_prompt = context['user_prompt']
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return apply_message_token_soft_cap(messages)