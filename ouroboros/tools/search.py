# '''Web search tool.'''

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from ouroboros.tools.registry import ToolContext, ToolEntry


def _web_search(ctx: ToolContext, query: str) -> str:
    try:
        encoded_query = urllib.parse.quote(query)
        api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&lang=en"
        
        # Используем прямой HTTP-запрос вместо вызова browse_page
        with urllib.request.urlopen(api_url) as response:
            page_result = response.read().decode('utf-8')
        
        data = json.loads(page_result)
        
        abstract = data.get('AbstractText', '')
        results = data.get('RelatedTopics', [])
        
        answer = f"🔍 Результаты поиска (на английском):

"
        if abstract:
            answer += f"**Кратко:** {abstract[:300]}...
\n"
        
        answer += "**Топ результатов:**\n"
        for i, topic in enumerate(results[:3]):
            if 'Text' in topic:
                answer += f"{i+1}. {topic['Text']}\n"
                
        return json.dumps({"answer": answer}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"}, ensure_ascii=False)


def get_tools() -> List[ToolEntry]:
    return [
        ToolEntry("web_search", {
            "name": "web_search",
            "description": "Search the web via DuckDuckGo API. Free alternative to OpenAI Responses.",
            "parameters": {"type": "object", "properties": {
                "query": {"type": "string"},
            }, "required": ["query"]},
        }, _web_search),
    ]