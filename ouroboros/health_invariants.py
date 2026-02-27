from typing import Dict, Any

def build_health_invariants(context: Dict[str, Any]) -> str:
    # Реализация проверки health invariants
    # Пример: проверка версионной синхронизации, бюджетного дрейфа
    invariants = []
    
    # Check version sync
    if context.get('version_status') == 'OK':
        invariants.append("OK: version sync (%s)" % context.get('current_version', 'mock'))
    else:
        invariants.append("CRITICAL: version desync")

    # Check budget drift
    budget_drift = context.get('budget_drift_pct', 0)
    if budget_drift < 20:
        invariants.append("OK: budget drift within tolerance")
    else:
        invariants.append("WARNING: budget drift > 20%%")

    # Check identity freshness
    if context.get('identity_last_update_hours', 4) <= 4:
        invariants.append("OK: identity.md recent")
    else:
        invariants.append("WARNING: identity.md not updated for >4h")

    return "\n".join(invariants)