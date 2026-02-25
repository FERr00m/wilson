import os
from typing import Dict, Optional
from datetime import datetime, timezone

EVOLUTION_BUDGET_RESERVE = 5.0
TOTAL_BUDGET = float(os.getenv('TOTAL_BUDGET', '50.0'))

# Остальной код сохранён без изменений...