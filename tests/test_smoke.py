import pytest
from unittest.mock import patch
from ouroboros import context_core


def test_import_all():
    assert context_core

def test_context_build_runtime_section():
    with patch('ouroboros.context_core.get_git_info', return_value=('main', 'abc123')):
        result = context_core._build_runtime_section({'current_branch': 'main'})
        assert 'main@abc123' in result

def test_context_build_memory_sections():
    # Pass identity/scratchpad directly in context
    result = context_core._build_memory_sections({
        'identity': 'Identity content',
        'scratchpad': 'Scratchpad content'
    })
    assert 'Identity: Identity content' in result
    assert 'Scratchpad: Scratchpad content' in result

def test_context_health_invariants():
    # Return expected health format
    result = context_core._build_health_invariants({})
    assert 'OK: version sync' in result

def test_context_build_llm_messages():
    result = context_core.build_llm_messages({
        'system_prompt': 'sys',
        'user_prompt': 'usr'
    })
    assert len(result) == 2