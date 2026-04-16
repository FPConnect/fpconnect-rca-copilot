"""Operational intelligence routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.tickets import get_current_user_id
from app.core.database import get_db
from app.schemas.intelligence import IntelligenceSummaryResponse
from app.services.intelligence_service import build_intelligence_summary

router = APIRouter()


@router.get("/summary", response_model=IntelligenceSummaryResponse)
def get_intelligence_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Return predictive risk, data governance, and actionable insights."""
    return build_intelligence_summary(db)
