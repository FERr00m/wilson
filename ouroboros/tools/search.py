# '''Web search tool.'''

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import logging
from typing import Any, Dict, List

from ouroboros.tools.registry import ToolContext, ToolEntry

logger = logging.getLogger(__name__)

def _web_search(ctx: ToolContext, query: str) -> str:
    try:
        encoded_query = urllib.parse.quote(query)
        api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&lang=en"
        
        # Прямой запрос через urllib
        with urllib.request.urlopen(api_url, timeout=10) as response:
            page_result = response.read().decode('utf-8')
        
        data = json.loads(page_result)
        
        # Формируем ответ
        abstract = data.get('AbstractText', '')
        results = data.get('RelatedTopics', [])
        
        answer = f"🔍 Результаты поиска (на английском):\n\n"
        if abstract:
            answer += f"**Кратко:** {abstract[:300]}...\n\n"
        
        answer += "**Топ результатов:**\n"
        for i, topic in enumerate(results[:3]):
            # Безопасное получение текста через .get()
            text = topic.get('Text', '')
            if text:
                answer += f"{i+1}. {text}\n"
        
        return json.dumps({"answer": answer}, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Web search failed: %s", str(e))
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