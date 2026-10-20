"""Enterprise clinical engineering endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.core.security import limiter
from app.models.machine import Machine
from app.models.ticket import Ticket
from app.services.calibration import schedule_calibration, validate_calibration
from app.services.compliance import generate_anvisa_pdf
from app.services.equipment_report import (
    EquipmentRecord,
    TicketRecord,
    generate_equipment_pdf,
)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get("/rca/methods")
def list_rca_methods(
    user_id: int = Depends(get_current_user_id),
) -> dict[str, list[str]]:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


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
        headers={
            "Content-Disposition": 'attachment; filename="anvisa-compliance-report.pdf"'
        },
    )


@router.get("/reports/equipment/{equipment_code}")
@limiter.limit("12/minute")
def create_equipment_report(
    request: Request,
    equipment_code: str,
    period_days: int = Query(default=90, ge=1, le=365),
    demonstration: bool = Query(default=False),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Response:
    """Generate a PDF from persisted equipment data and the caller's tickets."""
    machine = db.query(Machine).filter(Machine.code == equipment_code).first()
    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    start = datetime.now(timezone.utc) - timedelta(days=period_days)
    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.creator_id == user_id,
            Ticket.device_id == machine.code,
            Ticket.created_at >= start,
        )
        .order_by(Ticket.created_at.desc())
        .limit(25)
        .all()
    )
    equipment_record = EquipmentRecord(
        code=machine.code,
        name=machine.name,
        model=machine.model,
        location=machine.location,
        equipment_type=machine.type,
        status=machine.status,
        criticality=machine.criticality,
        last_failure=machine.last_failure,
        recurrent_failures=machine.recurrent_failures,
        last_check=machine.last_check,
    )
    ticket_records = [
        TicketRecord(
            ticket_id=ticket.id,
            title=ticket.title,
            status=ticket.status,
            priority=ticket.priority,
            created_at=ticket.created_at,
            root_cause=ticket.root_cause,
            recommendation=ticket.recommendation,
        )
        for ticket in tickets
    ]
    pdf, filename = generate_equipment_pdf(
        equipment_record,
        ticket_records,
        period_days=period_days,
        demonstration=demonstration,
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
        },
    )
