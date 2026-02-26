from dataclasses import dataclass
from typing import Optional

@dataclass
class State:
    owner_id: int = 0
    owner_chat_id: int = 0
    tg_offset: int = 0
    spent_usd: float = 0.0
    spent_calls: int = 0
    spent_tokens_prompt: int = 0
    spent_tokens_completion: int = 0
    spent_tokens_cached: int = 0
    session_id: str = ""
    current_branch: str = ""
    current_sha: str = ""
    last_owner_message_at: Optional[str] = None
    last_evolution_task_at: Optional[str] = None
    budget_messages_since_report: int = 0
    evolution_mode_enabled: bool = False
    evolution_cycle: int = 0
    session_total_snapshot: float = 0.0
    session_spent_snapshot: float = 0.0
    budget_drift_pct: float = 0.0
    budget_drift_alert: bool = False
    evolution_consecutive_failures: int = 0
    openrouter_total_usd: float = 0.0
    openrouter_daily_usd: float = 0.0
    openrouter_last_check_at: Optional[str] = None

    # Core configuration
    EVOLUTION_BUDGET_RESERVE: float = 5.0  # Reduced from 50.0 to allow evolutions
    TOTAL_BUDGET_LIMIT: float = 100.0     # Match actual total budget

    def __post_init__(self):
        if self.TOTAL_BUDGET_LIMIT == 0.0:
            self.TOTAL_BUDGET_LIMIT = 100.0  # Default fallback
        if self.EVOLUTION_BUDGET_RESERVE >= self.TOTAL_BUDGET_LIMIT:
            # Safety: ensure evolution budget is always less than total
            self.EVOLUTION_BUDGET_RESERVE = min(5.0, self.TOTAL_BUDGET_LIMIT * 0.05)