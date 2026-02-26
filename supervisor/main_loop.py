"""Supervisor main loop helpers extracted from colab launcher."""

from __future__ import annotations

import datetime
import time
import uuid
from typing import Any


def safe_qsize(q: Any) -> int:
    try:
        return int(q.qsize())
    except Exception:
        return -1


def handle_supervisor_command(text: str, chat_id: int, tg_offset: int, ctx: Any):
    """Handle supervisor slash-commands.

    Returns:
        True  -> terminal command fully handled
        str   -> note to prepend and continue LLM flow
        ""    -> not a command
    """
    lowered = text.strip().lower()

    if lowered.startswith("/panic"):
        ctx.send_with_budget(chat_id, "🛑 PANIC: stopping everything now.")
        ctx.kill_workers()
        st2 = ctx.load_state()
        st2["tg_offset"] = tg_offset
        ctx.save_state(st2)
        raise SystemExit("PANIC")

    if lowered.startswith("/restart"):
        st2 = ctx.load_state()
        st2["session_id"] = uuid.uuid4().hex
        st2["tg_offset"] = tg_offset
        ctx.save_state(st2)
        ctx.send_with_budget(chat_id, "♻️ Restarting (soft).")
        ok, msg = ctx.safe_restart(reason="owner_restart", unsynced_policy="rescue_and_reset")
        if not ok:
            ctx.send_with_budget(chat_id, f"⚠️ Restart cancelled: {msg}")
            return True
        ctx.kill_workers()
        ctx.exec_restart()

    if lowered.startswith("/status"):
        status = ctx.status_text()
        ctx.send_with_budget(chat_id, status, force_budget=True)
        return "[Supervisor handled /status — status text already sent to chat]\n"

    if lowered.startswith("/review"):
        ctx.queue_review_task(reason="owner:/review", force=True)
        return "[Supervisor handled /review — review task queued]\n"

    if lowered.startswith("/evolve"):
        parts = lowered.split()
        action = parts[1] if len(parts) > 1 else "on"
        turn_on = action not in ("off", "stop", "0")
        st2 = ctx.load_state()
        st2["evolution_mode_enabled"] = bool(turn_on)
        ctx.save_state(st2)
        if not turn_on:
            ctx.pending_ref[:] = [t for t in ctx.pending_ref if str(t.get("type")) != "evolution"]
            ctx.sort_pending()
            ctx.persist_queue_snapshot(reason="evolve_off")
        state_str = "ON" if turn_on else "OFF"
        ctx.send_with_budget(chat_id, f"🧬 Evolution: {state_str}")
        return f"[Supervisor handled /evolve — evolution toggled {state_str}]\n"

    if lowered.startswith("/bg"):
        parts = lowered.split()
        action = parts[1] if len(parts) > 1 else "status"
        if action in ("start", "on", "1"):
            result = ctx.consciousness.start()
            ctx.send_with_budget(chat_id, f"🧠 {result}")
        elif action in ("stop", "off", "0"):
            result = ctx.consciousness.stop()
            ctx.send_with_budget(chat_id, f"🧠 {result}")
        else:
            bg_status = "running" if ctx.consciousness.is_running else "stopped"
            ctx.send_with_budget(chat_id, f"🧠 Background consciousness: {bg_status}")
        return f"[Supervisor handled /bg {action}]\n"

    return ""


def heartbeat_event(offset: int, workers_total: int, workers_alive: int, pending_count: int, running_count: int, event_q_size: int, running_task_ids: list[str], spent_usd: Any) -> dict:
    return {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "type": "main_loop_heartbeat",
        "offset": offset,
        "workers_total": workers_total,
        "workers_alive": workers_alive,
        "pending_count": pending_count,
        "running_count": running_count,
        "event_q_size": event_q_size,
        "running_task_ids": running_task_ids[:5],
        "spent_usd": spent_usd,
    }


def slow_cycle_event(duration_sec: float, pending_count: int, running_count: int) -> dict:
    return {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "type": "main_loop_slow_cycle",
        "duration_sec": round(duration_sec, 3),
        "pending_count": pending_count,
        "running_count": running_count,
    }


def sleep_for_mode(last_message_ts: float, active_window_sec: int = 300) -> float:
    now = time.time()
    return 0.1 if (now - last_message_ts) < active_window_sec else 0.5
