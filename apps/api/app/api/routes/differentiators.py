"""Routes for FPConnect high-differentiation modules."""

from fastapi import APIRouter

from app.schemas.differentiators import (
    ClinicalRiskAssetResponse,
    EvidenceCopilotCaseResponse,
    ValueEngineScenarioResponse,
)
from app.services.differentiators_service import (
    get_evidence_copilot_cases,
    get_risk_radar_assets,
    get_value_engine_scenarios,
)


router = APIRouter(prefix="/differentiators", tags=["differentiators"])


@router.get("/risk-radar", response_model=list[ClinicalRiskAssetResponse])
def list_risk_radar_assets():
    """Return equipment-level regulatory, cyber and recall risk signals."""

    return get_risk_radar_assets()


@router.get("/evidence-copilot", response_model=list[EvidenceCopilotCaseResponse])
def list_evidence_copilot_cases():
    """Return evidence-backed RCA demo cases."""

    return get_evidence_copilot_cases()


@router.get("/value-engine", response_model=list[ValueEngineScenarioResponse])
def list_value_engine_scenarios():
    """Return executive ROI and contract-renewal scenarios."""

    return get_value_engine_scenarios()
