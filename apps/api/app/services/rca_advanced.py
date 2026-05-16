"""Advanced RCA generation using structured methods and optional OpenAI assistance."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from openai import OpenAI, OpenAIError

from app.core.cache import get_cached, set_cached
from app.core.config import settings

METHODS = ["5whys", "fishbone", "fault_tree"]
_client = OpenAI(api_key=settings.openai_api_key)


def _cache_key(problem: str, context: str, method: str) -> str:
    digest = hashlib.sha256(f"{problem}|{context}|{method}".encode("utf-8")).hexdigest()
    return f"rca:{digest}"


def _fallback_rca(problem: str, method: str) -> dict[str, Any]:
    return {
        "analysis": {
            "method": method,
            "summary": "RCA generated from local rule-based fallback because the AI provider was unavailable.",
            "problem": problem,
        },
        "root_cause": "Insufficient evidence for a definitive root cause; escalate to engineering N2.",
        "confidence": 0.35,
        "actions": [
            "Collect equipment logs and maintenance history.",
            "Validate calibration status and environmental conditions.",
            "Update the knowledge base after corrective action confirmation.",
        ],
    }


def generate_rca(problem: str, context: str = "", method: str = "5whys") -> dict[str, Any]:
    """Generate a structured RCA using 5 Whys, fishbone, or fault-tree methodology."""
    if method not in METHODS:
        raise ValueError(f"Unsupported RCA method: {method}")
    cache_key = _cache_key(problem, context, method)
    cached = get_cached(cache_key)
    if cached:
        return cached

    prompt = (
        f"Method: {method}\n"
        f"Problem: {problem}\n"
        f"Context: {context}\n"
        'Return ONLY valid JSON with structure: {"analysis": {...}, "root_cause": "...", '
        '"confidence": 0.0, "actions": ["..."]}'
    )

    try:
        response = _client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
    except (OpenAIError, json.JSONDecodeError, IndexError, AttributeError):
        result = _fallback_rca(problem, method)

    set_cached(cache_key, result, ttl=86400)
    return result
