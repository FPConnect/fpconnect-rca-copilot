"""Internal callbacks for n8n workflows.

These endpoints are meant to be called only by n8n, not by
external clients. Use network controls and API keys to restrict
access.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import secrets_match
from app.models.ticket import Ticket, TicketLog
from app.schemas.n8n import N8nSlaEvent, N8nSlaUpdate

router = APIRouter(prefix="/internal/n8n", tags=["n8n-internal"])


def _verify_internal_key(x_internal_key: Optional[str] = Header(None)) -> None:
    """Very simple API-key style check for internal calls.

    For now we reuse the same n8n_sla_api_key setting. In production,
    this should be combined with network-level restrictions.
    """

    expected = settings.n8n_sla_api_key
    if not expected:
        # If no key configured, treat all calls as unauthorized.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="n8n internal key not configured",
        )
    if not secrets_match(expected, x_internal_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid n8n internal key",
        )


@router.post("/sla/event")
def log_sla_event(
    payload: N8nSlaEvent,
    db: Session = Depends(get_db),
    _: None = Depends(_verify_internal_key),
):
    """Create a TicketLog entry for an automation-related event.

    The `details` field is stored as text for now. n8n is expected to
    send small, structured metadata (no PHI).
    """

    ticket = db.query(Ticket).filter(Ticket.id == payload.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    # Simple, human-readable detail; n8n can control the message.
    detail = payload.details.get("message") if isinstance(payload.details, dict) else None
    if not detail:
        detail = f"Automation event: {payload.event_type}"

    log = TicketLog(
        ticket_id=ticket.id,
        user_id=payload.actor_user_id,
        action=payload.event_type,
        detail=detail,
    )
    db.add(log)
    db.commit()

    return {"status": "ok"}


@router.post("/sla/update")
def update_sla_fields(
    payload: N8nSlaUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(_verify_internal_key),
):
    """Allow n8n escalation flows to adjust SLA-related fields.

    For now we support updating escalation_level and assignee_id.
    """

    ticket = db.query(Ticket).filter(Ticket.id == payload.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    changed = False
    if payload.escalation_level is not None:
        ticket.escalation_level = payload.escalation_level
        changed = True
    if payload.assignee_id is not None:
        ticket.assignee_id = payload.assignee_id
        changed = True

    if changed:
        db.add(ticket)
        db.commit()

    return {"status": "ok", "changed": changed}
