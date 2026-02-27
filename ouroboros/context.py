from __future__ import annotations

from .context_core import (
    build_llm_messages,
    apply_message_token_soft_cap,
)

# Legacy alias for backward compatibility (to be removed after full migration)
# Maintains Principle 1: Continuity through smooth transitions
build_context = build_llm_messages