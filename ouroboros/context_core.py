from typing import List, Dict, Any

def compact_tool_history(tool_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Keep only the last 10 tool calls for display"""
    return tool_history[:10]

def compact_messages_for_display(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trim long message content for display"""
    result = []
    for msg in messages:
        clean = msg.copy()
        if 'content' in clean and isinstance(clean['content'], str):
            clean['content'] = clean['content'][:1000] + '...' if len(clean['content']) > 1000 else clean['content']
        result.append(clean)
    return result