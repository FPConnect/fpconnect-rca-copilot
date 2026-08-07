"""Integration helpers for n8n workflows.

Currently used for SLA-based alerting and escalation when tickets change.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


def _dt_iso(value: Optional[datetime]) -> Optional[str]:
    """Return an ISO 8601 string for a datetime, or None.

    Keeps type-checkers happy when dealing with optional ORM fields.
    """

    if value is None:
        return None
    return value.isoformat()


def _build_ticket_payload(ticket: Ticket, event_type: str, triggered_by_user_id: Optional[int]) -> Dict[str, Any]:
    """Build a safe payload to send to n8n.

    NOTE: Do not include PHI or long free-text fields here. Stick to
    identifiers and metadata that n8n needs for routing/notifications.
    """

    return {
        "event_type": event_type,
        "ticket_id": ticket.id,
        "priority": getattr(ticket, "priority", None),
        "status": getattr(ticket, "status", None),
        "device_id": getattr(ticket, "device_id", None),
        "location": getattr(ticket, "location", None),
        "creator_id": getattr(ticket, "creator_id", None),
        "assignee_id": getattr(ticket, "assignee_id", None),
        "triggered_by_user_id": triggered_by_user_id,
        # Timestamps as ISO strings when available
        "created_at": _dt_iso(getattr(ticket, "created_at", None)),
        "updated_at": _dt_iso(getattr(ticket, "updated_at", None)),
        "resolved_at": _dt_iso(getattr(ticket, "resolved_at", None)),
    }


def notify_sla_workflow(ticket: Ticket, event_type: str, triggered_by_user_id: Optional[int] = None) -> None:
    """Send a best-effort notification to the n8n SLA workflow.

    This function is designed to be used with FastAPI BackgroundTasks so
    that API requests are not blocked by network calls to n8n.

    If the n8n URL is not configured, this becomes a no-op.
    """

    url = settings.n8n_sla_workflow_url
    if not url:
        # Integration disabled; nothing to do.
        return

    payload = _build_ticket_payload(ticket, event_type=event_type, triggered_by_user_id=triggered_by_user_id)

    headers = {"Content-Type": "application/json"}
    if settings.n8n_sla_api_key:
        headers["X-Api-Key"] = settings.n8n_sla_api_key

    timeout = float(settings.n8n_sla_timeout_seconds or 5)

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        # Best-effort: log and move on; do not raise into the request path.
        logger.warning("Failed to notify n8n SLA workflow: %s", exc)
