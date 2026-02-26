from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
from pathlib import Path
import os

# Core paths
QUEUE_SNAPSHOT_PATH = "/content/drive/MyDrive/Ouroboros/state/queue_snapshot.jsonl"
CHAT_LOG_PATH = "/content/drive/MyDrive/Ouroboros/logs/chat.jsonl"
PROGRESS_LOG_PATH = "/content/drive/MyDrive/Ouroboros/logs/progress.jsonl"
EVENT_LOG_PATH = "/content/drive/MyDrive/Ouroboros/logs/events.jsonl"

# Core configuration (required as module-level constants for imports)
TOTAL_BUDGET_LIMIT = 100.0
EVOLUTION_BUDGET_RESERVE = 5.0

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

    # Class copy of config (updated from module constants on init)
    EVOLUTION_BUDGET_RESERVE: float = 5.0
    TOTAL_BUDGET_LIMIT: float = 100.0

    def __post_init__(self):
        if self.TOTAL_BUDGET_LIMIT == 0.0:
            self.TOTAL_BUDGET_LIMIT = 100.0
        if self.EVOLUTION_BUDGET_RESERVE >= self.TOTAL_BUDGET_LIMIT:
            self.EVOLUTION_BUDGET_RESERVE = min(5.0, self.TOTAL_BUDGET_LIMIT * 0.05)


def load_state() -> State:
    """Load state from Google Drive JSON file"""
    try:
        drive_path = Path("/content/drive/MyDrive/Ouroboros/state/state.json")
        if drive_path.exists():
            with open(drive_path, 'r') as f:
                data = json.load(f)
            return State(**data)
        return State()
    except Exception as e:
        print(f"Error loading state: {e}")
        return State()

def save_state(state: State):
    """Save state to Google Drive"""
    try:
        drive_path = Path("/content/drive/MyDrive/Ouroboros/state")
        drive_path.mkdir(parents=True, exist_ok=True)
        with open(drive_path / 'state.json', 'w') as f:
            json.dump(state.__dict__, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def append_jsonl(path: str, data: Dict[str, Any]):
    """Append JSON object to JSONL file"""
    try:
        full_path = Path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
    except Exception as e:
        print(f"Error appending JSONL: {e}")

def atomic_write_text(path: str, content: str):
    """Atomically write text to file"""
    temp_path = f"{path}.tmp"
    with open(temp_path, 'w') as f:
        f.write(content)
    os.replace(temp_path, path)

def budget_pct(state: State) -> float:
    """Calculate current budget usage percentage"""
    if state.TOTAL_BUDGET_LIMIT <= 0:
        return 0.0
    return (state.spent_usd / state.TOTAL_BUDGET_LIMIT) * 100.0