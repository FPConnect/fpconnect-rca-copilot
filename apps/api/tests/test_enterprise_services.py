"""Tests for enterprise predictive, calibration, and compliance helpers."""

from datetime import datetime, timedelta, timezone

from app.services.calibration import schedule_calibration, validate_calibration
from app.services.compliance import generate_anvisa_pdf
from app.services.predictive import calculate_risk


def test_predictive_risk_scores_critical_for_stale_high_failure_equipment():
    metrics = {
        "equipment_id": "VENT-01",
        "last_maintenance": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        "history": [{"id": 1}, {"id": 2}],
        "uptime_hours": 120,
    }

    result = calculate_risk(metrics)

    assert result["equipment_id"] == "VENT-01"
    assert result["score"] == 100
    assert result["level"] == "critical"
    assert result["predicted_failure_days"] == 7


def test_calibration_schedule_and_validation():
    schedule = schedule_calibration(equip_id=42, interval_days=180)
    validation = validate_calibration([{"passed": True}, {"passed": False}])

    assert schedule["equipment_id"] == 42
    assert schedule["status"] == "pending"
    assert validation == {"passed": False, "compliance_pct": 50.0}


def test_anvisa_pdf_generation_returns_pdf_bytes():
    pdf = generate_anvisa_pdf(
        {
            "start": "2026-01-01",
            "end": "2026-01-31",
            "tickets": 12,
            "calibrations": 7,
            "compliance": 98.5,
        }
    )

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 100
