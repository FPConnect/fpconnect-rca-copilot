"""Predictive maintenance risk scoring helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.cache import get_cached, set_cached


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def calculate_risk(metrics: dict[str, Any]) -> dict[str, Any]:
    """Calculate a failure-risk score from equipment maintenance and uptime metrics."""
    equipment_id = metrics.get("equipment_id") or "unknown"
    key = f"pred:{equipment_id}"
    cached = get_cached(key)
    if cached:
        return cached

    last_maintenance = metrics.get("last_maintenance")
    if not last_maintenance:
        raise ValueError("last_maintenance is required")

    days_since = max(0, (datetime.now(timezone.utc) - _parse_datetime(last_maintenance)).days)
    failures = len(metrics.get("history", []))
    uptime = float(metrics.get("uptime_hours", 0) or 0)
    score = min(100.0, (days_since / 10) * 30 + (failures * 10) + (uptime / 100) * 20)
    level = (
        "critical"
        if score >= 75
        else "high"
        if score >= 50
        else "medium"
        if score >= 25
        else "low"
    )
    result = {
        "equipment_id": equipment_id,
        "score": round(score, 1),
        "level": level,
        "predicted_failure_days": max(1, int(100 / score) * 7) if score > 0 else None,
    }
    set_cached(key, result, ttl=21600)
    return result
