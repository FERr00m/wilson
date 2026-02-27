import pytest
from unittest.mock import patch
from ouroboros import context_core

def test_import_all():
    assert context_core

def test_context_build_runtime_section():
    with patch('ouroboros.utils.get_git_info', return_value=('main', 'abc123')):
        # Pass single context dict instead of separate args
        result = context_core._build_runtime_section({
            'current_branch': 'main'
        })
        assert 'version: main@abc123' in result

def test_context_build_memory_sections():
    # Mock load functions directly (not through Memory class)
    with patch('ouroboros.memory.load_identity', return_value='Identity content'), \
         patch('ouroboros.memory.load_scratchpad', return_value='Scratchpad content'):
        result = context_core._build_memory_sections({})
        assert 'Identity: Identity content' in result
        assert 'Scratchpad: Scratchpad content' in result

def test_context_health_invariants():
    # Return actual format expected by test
    result = context_core._build_health_invariants({})
    assert 'OK: version sync (1.0.0)' in result

@patch('ouroboros.context_core.apply_message_token_soft_cap', return_value=[])  
def test_context_build_llm_messages(mock_cap):
    result = context_core.build_llm_messages({
        'system_prompt': 'sys',
        'user_prompt': 'usr'
    })
    assert len(result) == 2