"""Schemas for FPConnect differentiator modules."""

from typing import Literal

from pydantic import BaseModel


RiskSeverity = Literal["critical", "high", "medium", "low"]


class RiskSignalResponse(BaseModel):
    source: str
    type: Literal["recall", "cyber", "regulatory", "udi", "sbom"]
    severity: RiskSeverity
    title: str
    published_at: str
    evidence: str


class ClinicalRiskAssetResponse(BaseModel):
    id: str
    name: str
    location: str
    manufacturer: str
    model: str
    udi: str
    firmware: str
    clinical_criticality: Literal["life-support", "diagnostic", "monitoring", "support"]
    overall_risk: int
    recall_risk: int
    cyber_risk: int
    regulatory_risk: int
    downtime_impact_brl: int
    status: Literal["action_required", "monitor", "cleared"]
    signals: list[RiskSignalResponse]
    recommended_actions: list[str]
    audit_packet: str


class EvidenceSourceResponse(BaseModel):
    label: str
    type: Literal["manual", "history", "telemetry", "external", "checklist"]
    excerpt: str
    confidence_impact: str


class EvidenceCopilotCaseResponse(BaseModel):
    id: str
    ticket_title: str
    asset_id: str
    asset_name: str
    symptom: str
    probable_cause: str
    confidence: int
    containment_steps: list[str]
    guided_questions: list[str]
    evidence: list[EvidenceSourceResponse]
    oem_message: str
    capa_draft: str


class ValueLeverResponse(BaseModel):
    label: str
    value: str
    detail: str


class ValueEngineScenarioResponse(BaseModel):
    id: str
    client_profile: str
    period: str
    protected_assets: int
    avoided_downtime_hours: int
    avoided_loss_brl: int
    renewal_expansion_brl: int
    renewal_risk: Literal["low", "medium", "high"]
    recommended_offer: str
    executive_narrative: str
    levers: list[ValueLeverResponse]
    board_questions: list[str]
