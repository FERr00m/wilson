from typing import Dict, Any
from ouroboros.utils import clip_text

def build_memory_sections(context: Dict[str, Any]) -> str:
    """Строит секции памяти (scratchpad, identity) для контекста"""
    scratch = context.get('scratchpad', '')
    ident = context.get('identity', '')
    return (
        f"Scratchpad: {clip_text(scratch, 150)}\n"
        f"Identity: {clip_text(ident, 150)}"
    )