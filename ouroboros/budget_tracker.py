# Budget Tracking Service

from typing import Dict, Any
from supervisor.state import (
    TOTAL_BUDGET_LIMIT,
    budget_remaining as base_budget_remaining,
    update_budget_from_usage,
    budget_pct
)


def budget_remaining(state: Dict[str, Any]) -> float:
    """Calculate remaining budget in USD"""
    return base_budget_remaining(state)

def validate_evolution_mode(state: Dict[str, Any]) -> bool:
    """Check if evolution mode can be enabled"""
    return budget_remaining(state) >= 5.0