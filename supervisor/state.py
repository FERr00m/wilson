import os
import json
from typing import Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

EVOLUTION_BUDGET_RESERVE = 5.0
TOTAL_BUDGET = float(os.getenv('TOTAL_BUDGET', '50.0'))
QUEUE_SNAPSHOT_PATH = os.getenv('QUEUE_SNAPSHOT_PATH', 'queue_snapshot.json')
DRIVE_STATE_PATH = os.getenv('DRIVE_STATE_PATH', 'drive_state.json')

@dataclass
class SystemState:
    evolution_mode_enabled: bool = True
    evolution_consecutive_failures: int = 0
    evolution_cycle: int = 0
    last_evolution_task_at: Optional[datetime] = None
    budget_messages_since_report: int = 0
    # ... остальные поля

def load_state() -> SystemState:
    return SystemState()

def save_state(state: SystemState):
    pass

def append_jsonl(path: str, data: dict):
    with open(path, 'a') as f:
        f.write(json.dumps(data) + '\n')

def atomic_write_text(path: str, content: str):
    temp_path = f"{path}.tmp"
    with open(temp_path, 'w') as f:
        f.write(content)
    os.replace(temp_path, path)