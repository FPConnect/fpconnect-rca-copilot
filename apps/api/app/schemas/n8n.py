"""Pydantic schemas for internal n8n callback endpoints."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class N8nSlaEvent(BaseModel):
    """Payload for logging automation-related events on a ticket."""

    ticket_id: int
    event_type: str
    actor_user_id: Optional[int] = None
    details: Dict[str, Any] = {}


class N8nSlaUpdate(BaseModel):
    """Payload for requesting SLA-related updates on a ticket."""

    ticket_id: int
    escalation_level: Optional[int] = None
    assignee_id: Optional[int] = None
