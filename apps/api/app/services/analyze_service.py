"""Mock RCA analyzer service.

In production this would integrate with OpenAI embeddings and pgvector
for semantic similarity search. For MVP, it returns rule-based suggestions.
"""

from typing import List

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import AnalyzeTicketRequest, RCASuggestionResponse

# Simple keyword-to-cause mapping for mock RCA
KEYWORD_RULES = [
    {
        "keywords": ["offline", "unreachable", "network", "connection"],
        "cause": "Network connectivity failure",
        "confidence": 0.85,
        "resolution": "Check network cables, switch port, and device IP configuration.",
        "similar_incidents": ["TKT-001", "TKT-007"],
    },
    {
        "keywords": ["power", "shutdown", "restart", "reboot"],
        "cause": "Power supply or firmware issue",
        "confidence": 0.80,
        "resolution": "Check power supply unit and run firmware diagnostic.",
        "similar_incidents": ["TKT-012", "TKT-019"],
    },
    {
        "keywords": ["slow", "performance", "lag", "timeout"],
        "cause": "Resource exhaustion (CPU/memory)",
        "confidence": 0.75,
        "resolution": "Review resource utilization and restart offending processes.",
        "similar_incidents": ["TKT-034"],
    },
    {
        "keywords": ["error", "alarm", "alert", "fault"],
        "cause": "Hardware fault or sensor alarm",
        "confidence": 0.70,
        "resolution": "Run hardware self-test and review event log.",
        "similar_incidents": ["TKT-022", "TKT-041"],
    },
]


def analyze_ticket(
    db: Session, ticket: Ticket, request: AnalyzeTicketRequest
) -> List[RCASuggestionResponse]:
    """Generate RCA suggestions for a ticket using keyword matching.

    Args:
        db: Database session (reserved for future vector search).
        ticket: The ticket to analyze.
        request: Additional context provided by the user.

    Returns:
        A list of RCA suggestion objects ordered by confidence.
    """
    text = " ".join(
        filter(
            None,
            [
                ticket.title or "",
                ticket.description or "",
                request.context or "",
            ],
        )
    ).lower()

    suggestions: List[RCASuggestionResponse] = []

    for rule in KEYWORD_RULES:
        if any(kw in text for kw in rule["keywords"]):
            suggestions.append(
                RCASuggestionResponse(
                    cause=rule["cause"],
                    confidence=rule["confidence"],
                    resolution=rule["resolution"],
                    similar_incidents=rule["similar_incidents"],
                )
            )

    # If no keyword matches, return a generic suggestion
    if not suggestions:
        suggestions.append(
            RCASuggestionResponse(
                cause="Unknown root cause",
                confidence=0.50,
                resolution="Escalate to Level 2 support and gather additional logs.",
                similar_incidents=[],
            )
        )

    return sorted(suggestions, key=lambda s: s.confidence, reverse=True)
