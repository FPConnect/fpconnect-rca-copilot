"""Pydantic schemas for ticket-related endpoints."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    """Schema for creating a ticket."""

    title: str
    description: Optional[str] = None
    priority: str = "medium"
    device_id: Optional[str] = None
    location: Optional[str] = None


class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    root_cause: Optional[str] = None
    recommendation: Optional[str] = None
    analysis_completed: Optional[datetime] = None


class TicketResponse(BaseModel):
    """Schema for ticket response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    creator_id: int
    assignee_id: Optional[int] = None
    root_cause: Optional[str] = None
    recommendation: Optional[str] = None
    analysis_completed: Optional[datetime] = None

class TicketAttachmentResponse(BaseModel):
    """Schema for an uploaded ticket attachment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    filename: str
    content_type: str
    size_bytes: int
    download_url: str

class AnalyzeIncidentRequest(BaseModel):
    """Request body for the clinical diagnosis endpoint."""

    ticket_id: int
    context: Optional[str] = None
    language: Literal["pt-BR", "en-US"] = "pt-BR"


class AnalyzeIncidentResponse(BaseModel):
    """Unconfirmed technical hypothesis; never automatically approved."""

    ticket_id: int
    root_cause: str
    recommendation: str
    explanation: str
    review_required: bool = True
    review_status: Literal["pending"] = "pending"
    analysis_kind: Literal["technical_hypothesis"] = "technical_hypothesis"
    confidence_is_probability: bool = False


class ConfirmIncidentAnalysisRequest(BaseModel):
    """A human reviewer attests to independent technical evidence.

    This action, unlike automated analysis, is allowed to persist a verified
    conclusion. No patient data or raw logs should be placed in evidence_refs.
    """

    root_cause: str = Field(min_length=5, max_length=1200)
    recommendation: str = Field(min_length=5, max_length=2500)
    evidence_refs: List[str] = Field(min_length=1, max_length=10)
    confirmed: Literal[True]


class ConfirmIncidentAnalysisResponse(BaseModel):
    ticket_id: int
    status: Literal["human_confirmed"] = "human_confirmed"
    reviewer_id: int
    review_required: bool = False


class AnalyzeTicketRequest(BaseModel):
    """Schema for RCA analysis request."""

    context: Optional[str] = None
    language: Literal["pt-BR", "en-US"] = "pt-BR"


class RCASuggestionResponse(BaseModel):
    """Schema for a single RCA suggestion."""

    cause: str
    confidence: float
    resolution: Optional[str] = None
    similar_incidents: List[str] = Field(default_factory=list)


class AnalyzeTicketResponse(BaseModel):
    """Schema for RCA analysis response."""

    ticket_id: int
    suggestions: List[RCASuggestionResponse]
