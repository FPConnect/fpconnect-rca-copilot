"""Integration helpers for n8n workflows."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


def _dt_iso(value: Optional[datetime]) -> Optional[str]:
    """Return an ISO 8601 string for a datetime, or None."""
    if value is None:
        return None
    return value.isoformat()


def _build_ticket_payload(ticket: Ticket, event_type: str, triggered_by_user_id: Optional[int]) -> Dict[str, Any]:
    """Build a safe, metadata-only payload to send to n8n."""
    return {
        "event_type": event_type,
        "ticket_id": ticket.id,
        "priority": getattr(ticket, "priority", None),
        "status": getattr(ticket, "status", None),
        "device_id": getattr(ticket, "device_id", None),
        "location": getattr(ticket, "location", None),
        "creator_id": getattr(ticket, "creator_id", None),
        "assignee_id": getattr(ticket, "assignee_id", None),
        "escalation_level": getattr(ticket, "escalation_level", None),
        "triggered_by_user_id": triggered_by_user_id,
        "created_at": _dt_iso(getattr(ticket, "created_at", None)),
        "updated_at": _dt_iso(getattr(ticket, "updated_at", None)),
        "resolved_at": _dt_iso(getattr(ticket, "resolved_at", None)),
    }


def notify_sla_workflow(ticket: Ticket, event_type: str, triggered_by_user_id: Optional[int] = None) -> None:
    """Send a best-effort notification to the n8n SLA workflow."""
    url = settings.n8n_sla_workflow_url
    if not url:
        return

    headers = {"Content-Type": "application/json"}
    if settings.n8n_sla_api_key:
        headers["X-Api-Key"] = settings.n8n_sla_api_key

    try:
        response = httpx.post(
            url,
            json=_build_ticket_payload(ticket, event_type, triggered_by_user_id),
            headers=headers,
            timeout=float(settings.n8n_sla_timeout_seconds or 5),
        )
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to notify n8n SLA workflow: %s", exc)
