import os
from typing import Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

EVOLUTION_BUDGET_RESERVE = 5.0
TOTAL_BUDGET = float(os.getenv('TOTAL_BUDGET', '50.0'))

@dataclass
class SystemState:
    evolution_mode_enabled: bool = True
    evolution_consecutive_failures: int = 0
    evolution_cycle: int = 0
    last_evolution_task_at: Optional[datetime] = None
    ...

def load_state() -> SystemState:
    # Реальная реализация загрузки состояния
    return SystemState()

def save_state(state: SystemState):
    # Реальная реализация сохранения состояния
    pass