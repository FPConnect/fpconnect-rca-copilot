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
    # --- DHS / Nihon Kohden Digital Health Solutions (NKDHS) ---
    # HealthConnect: EMR integration via HL7 Gateway, Enterprise Gateway, NKAnywhere, Ventilator Gateway
    # VirtualCare: remote ICU monitoring via NetKonnect, NGNK, Prefense, ViTrac
    # DataInsight: multi-source data acquisition and clinical analytics, CoMET
    {
        "keywords": ["hl7", "gateway", "emr", "ehr", "healthconnect", "enterprise gateway", "hl7 gateway"],
        "cause": "HL7/EMR integration failure (DHS HealthConnect)",
        "confidence": 0.88,
        "resolution": (
            "Check HL7 Gateway service status and HL7 message queue. "
            "Verify EMR endpoint connectivity and HL7 interface engine configuration. "
            "Consult Nihon Kohden DHS HealthConnect documentation at "
            "https://www.digitalhealthsolutions.com/product-main-pages/healthconnect"
        ),
        "similar_incidents": ["TKT-051", "TKT-058"],
    },
    {
        "keywords": ["nkanywhere", "firmware update", "remote firmware", "device update", "remote config"],
        "cause": "Remote firmware/settings update failure (DHS NKAnywhere)",
        "confidence": 0.82,
        "resolution": (
            "Verify NKAnywhere connectivity and device network reachability. "
            "Check update packages for compatibility with target device firmware version. "
            "Reference: https://www.digitalhealthsolutions.com/site-products/nkanywhere"
        ),
        "similar_incidents": ["TKT-053"],
    },
    {
        "keywords": ["netkonnect", "virtualcare", "remote icu", "remote monitoring", "central monitoring", "telemonitoring"],
        "cause": "Remote ICU/central monitoring connectivity failure (DHS VirtualCare)",
        "confidence": 0.87,
        "resolution": (
            "Check NetKonnect server connectivity and network bandwidth. "
            "Verify bedside monitor configuration for remote streaming. "
            "Review firewall rules for VirtualCare multicast traffic. "
            "Reference: https://www.digitalhealthsolutions.com/product-main-pages/virtualcare"
        ),
        "similar_incidents": ["TKT-060", "TKT-064"],
    },
    {
        "keywords": ["prefense", "telemetry", "centralized telemetry", "telemetry data", "ecg telemetry"],
        "cause": "Centralized telemetry monitoring failure (DHS Prefense)",
        "confidence": 0.83,
        "resolution": (
            "Check Prefense server status and wireless telemetry transmitter connectivity. "
            "Verify telemetry frequency assignments and check for RF interference. "
            "Reference: https://www.digitalhealthsolutions.com/site-products/prefense"
        ),
        "similar_incidents": ["TKT-066"],
    },
    {
        "keywords": ["vitrac", "mobile monitoring", "vital signs remote", "mobile device monitoring", "remote vital"],
        "cause": "Mobile/remote vital signs access failure (DHS ViTrac)",
        "confidence": 0.80,
        "resolution": (
            "Check ViTrac app connectivity and authentication. "
            "Verify patient monitor streaming configuration and mobile device network access. "
            "Reference: https://www.digitalhealthsolutions.com/site-products/vitrac"
        ),
        "similar_incidents": ["TKT-068"],
    },
    {
        "keywords": ["datainsight", "comet", "data acquisition", "clinical analytics", "waveform data", "live data"],
        "cause": "Clinical data acquisition/analytics platform failure (DHS DataInsight / CoMET)",
        "confidence": 0.81,
        "resolution": (
            "Check DataInsight/CoMET database connectivity and data pipeline status. "
            "Verify source device data export configuration and API credentials. "
            "Reference: https://www.digitalhealthsolutions.com/product-main-pages/datainsight"
        ),
        "similar_incidents": ["TKT-070", "TKT-072"],
    },
    {
        "keywords": ["ventilator gateway", "ventilator data", "ventilator emr", "ventilator integration"],
        "cause": "Ventilator-to-EMR data capture failure (DHS Ventilator Gateway)",
        "confidence": 0.85,
        "resolution": (
            "Check Ventilator Gateway service and serial/network connection to ventilator. "
            "Verify HL7 mapping configuration for ventilator waveform data. "
            "Reference: https://www.digitalhealthsolutions.com/site-products/ventilator-gateway"
        ),
        "similar_incidents": ["TKT-074"],
    },
    {
        "keywords": ["anvisa", "regulatory certification", "device certification", "compliance certification"],
        "cause": "Regulatory compliance issue affecting device operation",
        "confidence": 0.75,
        "resolution": (
            "Verify device regulatory certification status (ANVISA, FDA, CE). "
            "Check patch validation status at https://www.digitalhealthsolutions.com/patchvalidation "
            "and contact Nihon Kohden DHS support at info@nklab.com."
        ),
        "similar_incidents": ["TKT-076"],
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
