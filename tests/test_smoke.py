import importlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock
from pathlib import Path

import pytest

from supervisor.state import init, init_state


def _test_import(module_name):
    """Helper to import a module"""
    mod = importlib.import_module(module_name)
    assert mod is not None


def test_import_all():
    modules = [
        'ouroboros.agent',
        'ouroboros.context',
        'ouroboros.loop',
        'ouroboros.memory',
        'ouroboros.review',
        'ouroboros.llm',
        'ouroboros.utils',
        'supervisor.supervisor',
        'supervisor.state',
        'supervisor.telegram_bot',
        'supervisor.queue',
        'supervisor.worker',
        'supervisor.supervisor',
    ]
    for m in modules:
        _test_import(m)


def setup_state():
    from supervisor.state import DRIVE_ROOT
    import os
    import shutil

    # Clear existing state
    if DRIVE_ROOT.exists():
        shutil.rmtree(DRIVE_ROOT)
    os.makedirs(DRIVE_ROOT / "state", exist_ok=True)
    os.makedirs(DRIVE_ROOT / "logs", exist_ok=True)
    os.makedirs(DRIVE_ROOT / "memory/backups/core", exist_ok=True)

    init(DRIVE_ROOT, total_budget_limit=100.0)
    init_state()


def test_context_build_runtime_section():
    from ouroboros.context_core import _build_runtime_section
    from unittest.mock import MagicMock
    from pathlib import Path

    env = MagicMock()
    env.repo_dir = Path("/repo")
    env.drive_root = Path("/drive")
    task = {"id": "test", "type": "test"}

    # Mock the get_git_info to return known values
    original_get_git_info = _build_runtime_section.__globals__["get_git_info"]
    try:
        _build_runtime_section.__globals__["get_git_info"] = lambda repo_dir: ("test-branch", "test-sha")
        result = _build_runtime_section(env, task)
        assert "test-branch" in result
        assert "test-sha" in result
    finally:
        _build_runtime_section.__globals__["get_git_info"] = original_get_git_info


def test_context_build_memory_sections():
    from ouroboros.context_core import _build_memory_sections
    from ouroboros.memory import Memory
    from unittest.mock import MagicMock
    from pathlib import Path

    memory = MagicMock(spec=Memory)
    memory.load_scratchpad.return_value = "Scratchpad content"
    memory.load_identity.return_value = "Identity content"

    # Set up path mocking for summary file check
    memory.drive_root = MagicMock()
    summary_path = MagicMock()
    summary_path.exists.return_value = False
    memory.drive_root.__truediv__.return_value.__truediv__.return_value = summary_path

    sections = _build_memory_sections(memory)
    assert len(sections) == 2
    assert "## Scratchpad" in sections[0]
    assert "Scratchpad content" in sections[0]
    assert "## Identity" in sections[1]
    assert "Identity content" in sections[1]


def test_context_health_invariants():
    from ouroboros.context_core import _build_health_invariants
    from unittest.mock import MagicMock
    from pathlib import Path

    env = MagicMock()
    env.repo_path = MagicMock(return_value=Path("/repo/VERSION"))
    env.drive_path = MagicMock(return_value=Path("/drive/state/state.json"))

    # Mock version files
    def mock_read_text(path, *args, **kwargs):
        if "VERSION" in str(path):
            return "1.0.0"
        if "pyproject.toml" in str(path):
            return "version = \"1.0.0\""
        if "state.json" in str(path):
            return '{"budget_drift_alert": false}'
        return ""

    original_read_text = _build_health_invariants.__globals__["read_text"]
    try:
        _build_health_invariants.__globals__["read_text"] = mock_read_text
        result = _build_health_invariants(env)
        assert "OK: version sync (1.0.0)" in result
        assert "OK: budget drift within tolerance" in result
    finally:
        _build_health_invariants.__globals__["read_text"] = original_read_text


def test_context_build_llm_messages():
    from ouroboros.context_core import build_llm_messages
    from ouroboros.memory import Memory
    from unittest.mock import MagicMock
    from pathlib import Path

    env = MagicMock()
    env.repo_path = MagicMock(return_value=Path("/repo/prompt"))
    env.drive_path = MagicMock(return_value=Path("/drive/state"))

    # Setup fully mocked Memory object with string return values
    memory = MagicMock(spec=Memory)
    memory.drive_root = MagicMock()
    memory.load_scratchpad.return_value = "Scratchpad content"
    memory.load_identity.return_value = "Identity content"
    
    # Mock all summary methods to return strings
    memory.summarize_chat.return_value = "Chat summary"
    memory.summarize_progress.return_value = "Progress summary"
    memory.summarize_tools.return_value = "Tools summary"
    memory.summarize_events.return_value = "Events summary"
    memory.summarize_supervisor.return_value = "Supervisor summary"

    # Mock path.exists for identity.md
    identity_path = MagicMock()
    identity_path.exists.return_value = True
    memory.drive_root.__truediv__.return_value.__truediv__.return_value = identity_path

    task = {"id": "test", "type": "user"}

    # Mock internal functions to return valid strings
    original_build_runtime_section = build_llm_messages.__globals__["_build_runtime_section"]
    original_build_memory_sections = build_llm_messages.__globals__["_build_memory_sections"]
    original_build_health_invariants = build_llm_messages.__globals__["_build_health_invariants"]

    try:
        # Mock all section builders to return strings
        build_llm_messages.__globals__["_build_runtime_section"] = lambda env, task: "Runtime section"
        build_llm_messages.__globals__["_build_memory_sections"] = lambda memory: ["Memory section 1", "Memory section 2"]
        build_llm_messages.__globals__["_build_health_invariants"] = lambda env: "Health section"

        messages, cap_info = build_llm_messages(env, memory, task)

        # Check system block structure
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert len(messages[0]["content"]) == 3  # static, semi-stable, dynamic

    finally:
        # Restore original functions
        build_llm_messages.__globals__["_build_runtime_section"] = original_build_runtime_section
        build_llm_messages.__globals__["_build_memory_sections"] = original_build_memory_sections
        build_llm_messages.__globals__["_build_health_invariants"] = original_build_health_invariants