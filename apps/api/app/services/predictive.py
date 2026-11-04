"""Exploratory maintenance priority scoring; not a validated failure prediction.

This function does NOT estimate a probability or forecast failure date and
must not drive clinical or equipment maintenance decisions autonomously.
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def calculate_risk(metrics: dict[str, Any]) -> dict[str, Any]:
    """Return an unvalidated operational triage index, never a failure date.

    The weights are demonstrative, not fitted/calibrated to MedTech failures.
    """
    equipment_id = str(metrics.get("equipment_id") or "").strip()
    if not equipment_id:
        raise ValueError("equipment_id is required")
    last_maintenance = metrics.get("last_maintenance")
    if not isinstance(last_maintenance, str) or not last_maintenance:
        raise ValueError("last_maintenance is required")
    try:
        parsed = _parse_datetime(last_maintenance)
    except (TypeError, ValueError) as exc:
        raise ValueError("last_maintenance must be a valid ISO date/time") from exc

    now = datetime.now(timezone.utc)
    if parsed > now:
        raise ValueError("last_maintenance cannot be in the future")

    history = metrics.get("history", [])
    if not isinstance(history, list) or len(history) > 10000:
        raise ValueError("history must be a list with at most 10000 records")
    try:
        uptime = float(metrics.get("uptime_hours", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("uptime_hours must be a finite nonnegative number") from exc
    if not math.isfinite(uptime) or uptime < 0:
        raise ValueError("uptime_hours must be a finite nonnegative number")

    days_since = (now - parsed).days
    # Existing relative prioritization formula maintained for compatibility.
    # DO NOT interpret as physical probability of failure.
    score = min(100.0, (days_since / 10) * 30 + (len(history) * 10) + (uptime / 100) * 20)
    level = (
        "critical" if score >= 75
        else "high" if score >= 50
        else "medium" if score >= 25
        else "low"
    )
    return {
        "equipment_id": equipment_id,
        "score": round(score, 1),
        "level": level,
        "score_type": "unvalidated_heuristic_priority_index",
        "predicted_failure_days": None,
        "is_failure_probability": False,
        "review_required": True,
        "limitations": (
            "This is an exploratory prioritization score using arbitrary weights; "
            "it is not a validated failure probability or estimate of days until failure. "
            "Qualified technical review and manufacturer procedures remain mandatory."
        ),
    }
