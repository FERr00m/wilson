"""Model pricing helpers for cost estimation."""

from __future__ import annotations

import threading
from typing import Dict, Tuple


MODEL_PRICING_STATIC: Dict[str, Tuple[float, float, float]] = {
    "anthropic/claude-opus-4.6": (5.0, 0.5, 25.0),
    "anthropic/claude-opus-4": (15.0, 1.5, 75.0),
    "anthropic/claude-sonnet-4": (3.0, 0.30, 15.0),
    "anthropic/claude-sonnet-4.6": (3.0, 0.30, 15.0),
    "anthropic/claude-sonnet-4.5": (3.0, 0.30, 15.0),
    "openai/o3": (2.0, 0.50, 8.0),
    "openai/o3-pro": (20.0, 1.0, 80.0),
    "openai/o4-mini": (1.10, 0.275, 4.40),
    "openai/gpt-4.1": (2.0, 0.50, 8.0),
    "openai/gpt-5.2": (1.75, 0.175, 14.0),
    "openai/gpt-5.2-codex": (1.75, 0.175, 14.0),
    "google/gemini-2.5-pro-preview": (1.25, 0.125, 10.0),
    "google/gemini-3-pro-preview": (2.0, 0.20, 12.0),
    "x-ai/grok-3-mini": (0.30, 0.03, 0.50),
    "qwen/qwen3.5-plus-02-15": (0.40, 0.04, 2.40),
}

_pricing_fetched = False
_cached_pricing: Dict[str, Tuple[float, float, float]] | None = None
_pricing_lock = threading.Lock()


def get_pricing() -> Dict[str, Tuple[float, float, float]]:
    global _pricing_fetched, _cached_pricing
    if _pricing_fetched:
        return _cached_pricing or MODEL_PRICING_STATIC

    with _pricing_lock:
        if _pricing_fetched:
            return _cached_pricing or MODEL_PRICING_STATIC
        _pricing_fetched = True
        _cached_pricing = dict(MODEL_PRICING_STATIC)
        try:
            from ouroboros.llm import fetch_openrouter_pricing
            live = fetch_openrouter_pricing()
            if live and len(live) > 5:
                _cached_pricing.update(live)
        except Exception:
            _pricing_fetched = False
        return _cached_pricing


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int, cached_tokens: int = 0, cache_write_tokens: int = 0) -> float:
    model_pricing = get_pricing()
    pricing = model_pricing.get(model)
    if not pricing:
        best_match = None
        best_length = 0
        for key, value in model_pricing.items():
            if model and model.startswith(key) and len(key) > best_length:
                best_match = value
                best_length = len(key)
        pricing = best_match
    if not pricing:
        return 0.0
    input_price, cached_price, output_price = pricing
    regular_input = max(0, prompt_tokens - cached_tokens)
    cost = (
        regular_input * input_price / 1_000_000
        + cached_tokens * cached_price / 1_000_000
        + completion_tokens * output_price / 1_000_000
    )
    return round(cost, 6)
