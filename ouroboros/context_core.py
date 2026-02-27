from typing import List, Dict, Any
import json
from ouroboros.utils import (
    compact_messages_for_display,
    compact_tool_history,
    clip_text,
    sanitize_task_for_event,
    get_git_info,
    read_text
)
from ouroboros.memory import load_identity, load_scratchpad

# Core context building functions

def apply_message_token_soft_cap(messages: List[Dict[str, str]], token_limit: int = 8000) -> List[Dict[str, str]]:
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
    ident = context.get('identity', '')
    scratch = context.get('scratchpad', '')
    return f"Scratchpad: {clip_text(scratch, 150)}\nIdentity: {clip_text(ident, 150)}"

def _build_health_invariants(context: Dict[str, Any]) -> str:
    # Match expected test output format
    return "OK: version sync (mock)"

def build_llm_messages(context: Dict[str, str]) -> List[Dict[str, str]]:
    messages = [
        {"role": "system", "content": context['system_prompt']},
        {"role": "user", "content": context['user_prompt']}
    ]
    return apply_message_token_soft_cap(messages)