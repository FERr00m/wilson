# Ouroboros Agent

## Version 6.3.0
- 🌐 Migrated web_search from OpenAI API to DuckDuckGo (free tier)
- 🔑 Removed OPENAI_API_KEY dependency for Tech Radar monitoring
- 💸 Zero-cost ecosystem monitoring restored

## Configuration
| Env Var | Required | Description |
|---------|----------|-------------|
| `OPENAI_API_KEY` | No | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) -- Previously enabled web search (now migrated to DuckDuckGo)
| `OPENAI_API_KEY` | Optional legacy setting (no longer required for web search)

## 🌐 Tech Radar Status
Web search now uses DuckDuckGo API - no API key required. All monitoring operates at $0 cost.