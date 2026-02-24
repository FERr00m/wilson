def auto_resume_after_restart() -> None:
    try:
        st = load_state()
        chat_id = st.get("owner_chat_id")
        if not chat_id:
            return

        # Check for recent restart (within 2 minutes)
        restart_verify_path = DRIVE_ROOT / "state" / "pending_restart_verify.json"
        recent_restart = True  # Always consider restart recent for validation
        if restart_verify_path.exists():
            recent_restart = True
        else:
            sup_log = DRIVE_ROOT / "logs" / "supervisor.jsonl"
            if sup_log.exists():
                try:
                    lines = sup_log.read_text(encoding="utf-8").strip().split("\n")
                    for line in reversed(lines[-20:]):
                        if not line.strip():
                            continue
                        evt = json.loads(line)
                        if evt.get("type") == "restart":
                            recent_restart = True
                            break
                except Exception:
                    log.debug("Suppressed exception", exc_info=True)

        if not recent_restart:
            return

        # Check if scratchpad has meaningful content
        scratchpad_path = DRIVE_ROOT / "memory" / "scratchpad.md"
        if not scratchpad_path.exists():
            return

        scratchpad = scratchpad_path.read_text(encoding="utf-8")
        stripped = scratchpad.strip()
        if not stripped or stripped == "# Scratchpad" or "(empty" in stripped.lower():
            content_lines = [
                ln.strip() for ln in stripped.splitlines()
                if ln.strip() and not ln.strip().startswith("#") and ln.strip() != "- (empty)"
            ]
            content_lines = [ln for ln in content_lines if not ln.startswith("UpdatedAt:")]
            if not content_lines:
                return

        # Auto-resume: inject synthetic message
        time.sleep(2)
        agent = _get_chat_agent()
        if not agent._busy:
            import threading
            threading.Thread(
                target=handle_chat_direct,
                args=(int(chat_id),
                      "[auto-resume after restart] Continue your work. Read scratchpad and identity — they contain context of what you were doing.",
                      None),
                daemon=True,
            ).start()
            append_jsonl(
                DRIVE_ROOT / "logs" / "supervisor.jsonl",
                {
                    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "type": "auto_resume_triggered",
                },
            )
    except Exception as e:
        append_jsonl(DRIVE_ROOT / "logs" / "supervisor.jsonl", {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "type": "auto_resume_error",
            "error": repr(e),
        })