"""Enterprise clinical engineering endpoints."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user_id
from app.services.calibration import schedule_calibration, validate_calibration
from app.services.compliance import generate_anvisa_pdf
from app.services.predictive import calculate_risk
from app.services.rca_advanced import METHODS, generate_rca

router = APIRouter()


class RCARequest(BaseModel):
    problem: str = Field(..., min_length=3)
    context: str = ""
    method: Literal["5whys", "fishbone", "fault_tree"] = "5whys"


class PredictiveRiskRequest(BaseModel):
    equipment_id: int | str
    last_maintenance: str
    history: list[dict[str, Any]] = Field(default_factory=list)
    uptime_hours: float = 0


class CalibrationScheduleRequest(BaseModel):
    equipment_id: int
    interval_days: int = Field(default=365, ge=1, le=3650)


class CalibrationValidationRequest(BaseModel):
    results: list[dict[str, Any]] = Field(default_factory=list)


class ComplianceReportRequest(BaseModel):
    start: str
    end: str
    tickets: int = Field(ge=0)
    calibrations: int = Field(ge=0)
    compliance: float = Field(ge=0, le=100)


@router.post("/rca")
def create_advanced_rca(
    payload: RCARequest,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Generate methodical RCA output for regulated clinical engineering workflows."""
    try:
        return generate_rca(payload.problem, payload.context, payload.method)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/rca/methods")
def list_rca_methods(user_id: int = Depends(get_current_user_id)) -> dict[str, list[str]]:
    """List supported RCA methodologies."""
    return {"methods": METHODS}


@router.post("/predictive/risk")
def calculate_predictive_risk(
    payload: PredictiveRiskRequest,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Calculate predictive maintenance risk for one equipment item."""
    try:
        return calculate_risk(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/calibration/schedule")
def create_calibration_schedule(
    payload: CalibrationScheduleRequest,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Schedule a calibration event."""
    return schedule_calibration(payload.equipment_id, payload.interval_days)


@router.post("/calibration/validate")
def validate_calibration_results(
    payload: CalibrationValidationRequest,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Validate calibration measurements and summarize compliance."""
    return validate_calibration(payload.results)


@router.post("/compliance/anvisa-report")
def create_anvisa_report(
    payload: ComplianceReportRequest,
    user_id: int = Depends(get_current_user_id),
) -> Response:
    """Generate a PDF ANVISA compliance report."""
    pdf = generate_anvisa_pdf(payload.model_dump())
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="anvisa-compliance-report.pdf"'},
    )
