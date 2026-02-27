import importlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from supervisor.state import init, init_state


def test_import(module_name):
    """Smoke test that a module can be imported"""
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
        test_import(m)


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

    env = MagicMock()
    env.repo_dir = "/repo"
    env.drive_root = "/drive"
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

    memory = MagicMock(spec=Memory)
    memory.load_scratchpad.return_value = "Scratchpad content"
    memory.load_identity.return_value = "Identity content"
    # Mock summary path does not exist
    memory.drive_root = MagicMock()
    memory.drive_root.__truediv__.return_value.exists.return_value = False

    sections = _build_memory_sections(memory)
    assert len(sections) == 2
    assert "## Scratchpad" in sections[0]
    assert "Scratchpad content" in sections[0]
    assert "## Identity" in sections[1]
    assert "Identity content" in sections[1]


def test_context_health_invariants():
    from ouroboros.context_core import _build_health_invariants
    from unittest.mock import MagicMock

    env = MagicMock()
    env.repo_path.return_value = "/repo/VERSION"
    env.drive_path.return_value = "/drive/state/state.json"

    # Mock version file
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

    env = MagicMock()
    env.repo_path.return_value = "/repo/prompt"
    env.drive_path.return_value = "/drive/state"
    memory = MagicMock(spec=Memory)
    task = {"id": "test", "type": "user"}

    # Mock the helper functions to return known values
    def mock_build_runtime_section(env, task):
        return "## Runtime context\nRuntime data"

    def mock_build_memory_sections(memory):
        return ["## Scratchpad\nScratch"]

    def mock_build_health_invariants(env):
        return "## Health Invariants\nOK: test"

    original_build_runtime_section = build_llm_messages.__globals__["_build_runtime_section"]
    original_build_memory_sections = build_llm_messages.__globals__["_build_memory_sections"]
    original_build_health_invariants = build_llm_messages.__globals__["_build_health_invariants"]

    try:
        build_llm_messages.__globals__["_build_runtime_section"] = mock_build_runtime_section
        build_llm_messages.__globals__["_build_memory_sections"] = mock_build_memory_sections
        build_llm_messages.__globals__["_build_health_invariants"] = mock_build_health_invariants

        messages, cap_info = build_llm_messages(env, memory, task)

        # Check system block structure
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert len(messages[0]["content"]) == 3  # 3 cached blocks
        assert "Scratch" in messages[0]["content"][1]["text"]  # semi-stable
        assert "Runtime data" in messages[0]["content"][2]["text"]  # dynamic

    finally:
        build_llm_messages.__globals__["_build_runtime_section"] = original_build_runtime_section
        build_llm_messages.__globals__["_build_memory_sections"] = original_build_memory_sections
        build_llm_messages.__globals__["_build_health_invariants"] = original_build_health_invariants