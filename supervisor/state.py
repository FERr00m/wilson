import os
import json
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
    # ... остальные поля

def load_state() -> SystemState:
    # Реализация загрузки состояния
    return SystemState()

def save_state(state: SystemState):
    # Реализация сохранения состояния
    pass

def append_jsonl(path: str, data: dict):
    """Append data as JSON line to file"""
    with open(path, 'a') as f:
        f.write(json.dumps(data) + '\n')