"""Pydantic schemas for ticket-related endpoints."""

from typing import List, Optional

from pydantic import BaseModel


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


class TicketResponse(BaseModel):
    """Schema for ticket response."""

    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    creator_id: int
    assignee_id: Optional[int] = None
    escalation_level: Optional[int] = None

    class Config:
        from_attributes = True


class AnalyzeTicketRequest(BaseModel):
    """Schema for RCA analysis request."""

    context: Optional[str] = None


class RCASuggestionResponse(BaseModel):
    """Schema for a single RCA suggestion."""

    cause: str
    confidence: float
    resolution: Optional[str] = None
    similar_incidents: List[str] = []


class AnalyzeTicketResponse(BaseModel):
    """Schema for RCA analysis response."""

    ticket_id: int
    suggestions: List[RCASuggestionResponse]
