"""Pydantic schemas for internal n8n callback endpoints.

These endpoints are intended to be called only by n8n workflows
running inside the FPConnect infrastructure.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class N8nSlaEvent(BaseModel):
    """Payload for logging automation-related events on a ticket.

    This is kept metadata-only (no PHI) and is meant for timeline entries.
    """

    ticket_id: int
    event_type: str
    # Optional: which user triggered the automation step, if applicable
    actor_user_id: Optional[int] = None
    details: Dict[str, Any] = {}


class N8nSlaUpdate(BaseModel):
    """Payload for requesting SLA-related updates on a ticket.

    Typically used by n8n escalation flows to bump escalation_level or
    adjust SLA metadata.
    """

    ticket_id: int
    escalation_level: Optional[int] = None
    assignee_id: Optional[int] = None
