"""Optional LLM helpers.

This module is intentionally minimal and safe:
- If OPENAI_API_KEY is not set, functions fall back to simple heuristics.
- Replace the OpenAI call with your preferred provider if needed.

NOTE: This project does NOT scrape LinkedIn. Use only authorized APIs.
"""

from __future__ import annotations

import os
import textwrap
import requests


def summarize_simple(text: str, limit: int = 280) -> str:
    if not text:
        return ""
    t = " ".join(text.strip().split())
    return (t[:limit] + "…") if len(t) > limit else t


def translate_stub(text: str, target: str) -> str:
    """Fallback translation: returns the original text.
    
    For bilingual UX, you'll typically integrate a translation model here.
    """
    return text


def try_openai_chat(prompt: str, system: str = "You are a helpful assistant.") -> str | None:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    # Minimal OpenAI-compatible call (works with OpenAI and some gateways)
    url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def summarize_bilingual(text: str) -> tuple[str, str]:
    """Return (summary_en, summary_pt)."""
    base = summarize_simple(text, limit=320)

    # Attempt LLM bilingual summary if key exists
    resp = try_openai_chat(
        prompt=textwrap.dedent(f"""
        Create two short summaries (max 3 bullet points each), one in English and one in Brazilian Portuguese.
        Text:
        {text}
        """),
        system="You write concise, factual summaries. If uncertain, state uncertainty."
    )
    if resp:
        # naive split
        # expected format: EN: ... PT: ...
        en = ""
        pt = ""
        lower = resp.lower()
        if "pt" in lower and "en" in lower:
            # try split markers
            parts = resp.split("PT")
            if len(parts) >= 2:
                left = parts[0]
                right = "PT".join(parts[1:])
                en = left.replace("EN:", "").strip()
                pt = right.replace(":", "", 1).strip()
        if not en or not pt:
            # fallback: use same text
            en = base
            pt = base
        return en[:800], pt[:800]

    # No LLM: fallback
    return base, base
