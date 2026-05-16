"""Calibration scheduling and validation helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def schedule_calibration(equip_id: int, interval_days: int = 365) -> dict[str, Any]:
    """Create the next calibration schedule for an equipment item."""
    now = datetime.now(timezone.utc)
    return {
        "equipment_id": equip_id,
        "scheduled": now.isoformat(),
        "next_due": (now + timedelta(days=interval_days)).isoformat(),
        "status": "pending",
    }


def validate_calibration(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate calibration result entries and return compliance percentage."""
    passed_count = sum(1 for item in results if item.get("passed", False))
    return {
        "passed": bool(results) and passed_count == len(results),
        "compliance_pct": (passed_count / len(results)) * 100 if results else 0,
    }
