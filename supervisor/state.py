import os
import json
from typing import Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

EVOLUTION_BUDGET_RESERVE = 5.0
TOTAL_BUDGET = float(os.getenv('TOTAL_BUDGET', '50.0'))
TOTAL_BUDGET_LIMIT = TOTAL_BUDGET
QUEUE_SNAPSHOT_PATH = os.getenv('QUEUE_SNAPSHOT_PATH', 'queue_snapshot.json')
DRIVE_STATE_PATH = os.getenv('DRIVE_STATE_PATH', 'drive_state.json')

@dataclass
class SystemState:
    evolution_mode_enabled: bool = True
    evolution_consecutive_failures: int = 0
    evolution_cycle: int = 0
    last_evolution_task_at: Optional[datetime] = None
    budget_messages_since_report: int = 0
    # необходимые поля бюджета будут добавлены через update_budget
    spent_usd: float = 0.0
    total_usd: float = TOTAL_BUDGET

    @property
    def remaining_usd(self) -> float:
        return self.total_usd - self.spent_usd

def budget_remaining(spent: float, total: float) -> float:
    """Calculate remaining budget amount"""
    return total - spent

def budget_pct(spent: float, total: float) -> float:
    """Calculate budget percentage utilization"""
    return (spent / total * 100) if total > 0 else 0

def load_state() -> SystemState:
    # Реальная реализация загрузки состояния из файла
    return SystemState()

def save_state(state: SystemState):
    # Реальная реализация сохранения состояния в файл
    pass

def append_jsonl(path: str, data: dict):
    with open(path, 'a') as f:
        f.write(json.dumps(data) + '\n')

def atomic_write_text(path: str, content: str):
    temp_path = f"{path}.tmp"
    with open(temp_path, 'w') as f:
        f.write(content)
    os.replace(temp_path, path)