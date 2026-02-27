import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

log = logging.getLogger(__name__)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def clip_text(text: str, max_len: int = 1000, suffix: str = "...") -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + suffix

def estimate_tokens(text: str) -> int:
    # Very rough estimate for test purposes
    return max(1, len(text.split()))

def get_git_info(repo_dir: str) -> tuple[str, str]:
    branch = os.getenv("GIT_BRANCH", "main")
    sha = os.getenv("GIT_SHA", "deadbeef")
    return branch, sha

def compact_messages_for_display(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Simplified version that just passes through for test purposes"""
    return messages

def compact_tool_history(tool_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return tool_history[:10]

def extract_tool_call_blocks(text: str) -> List[Dict[str, str]]:
    # Simplified regex for test
    pattern = r'```tool_call\s*name="([^"]+)"\s*id="([^"]+)"\s*(.*?)```'
    return [{"name": m[0], "id": m[1], "arguments": m[2]} 
            for m in re.findall(pattern, text, re.DOTALL)]