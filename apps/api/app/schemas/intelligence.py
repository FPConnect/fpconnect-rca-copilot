"""Schemas for operational intelligence endpoints."""

from typing import List

from pydantic import BaseModel


class AssetRiskResponse(BaseModel):
    """Predictive risk score for one monitored asset."""

    code: str
    name: str
    location: str
    status: str
    risk_score: int
    risk_level: str
    drivers: List[str]
    recommended_action: str


class GovernanceCheckResponse(BaseModel):
    """Data quality and governance control status."""

    control: str
    status: str
    evidence: str


class OperationalInsightResponse(BaseModel):
    """Actionable business insight derived from operational data."""

    title: str
    impact: str
    recommended_action: str


class IntelligenceSummaryResponse(BaseModel):
    """Complete operational intelligence summary."""

    asset_risks: List[AssetRiskResponse]
    governance_checks: List[GovernanceCheckResponse]
    insights: List[OperationalInsightResponse]
