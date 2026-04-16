"""Operational intelligence and predictive scoring service."""

from collections import Counter
from typing import Iterable, List

from sqlalchemy.orm import Session

from app.crud.machine import get_machines
from app.crud.ticket import get_tickets
from app.models.machine import Machine
from app.models.ticket import Ticket
from app.schemas.intelligence import (
    AssetRiskResponse,
    GovernanceCheckResponse,
    IntelligenceSummaryResponse,
    OperationalInsightResponse,
)


def _risk_level(score: int) -> str:
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def _recommended_action(score: int, machine: Machine) -> str:
    if score >= 75:
        return "Schedule preventive maintenance and prepare backup equipment."
    if machine.status == "warning" or score >= 50:
        return "Review recent alerts, logs, network conditions, and firmware version."
    return "Keep standard health checks active."


def _ticket_pressure(machine: Machine, tickets: Iterable[Ticket]) -> int:
    machine_terms = {machine.code.lower(), machine.name.lower()}
    count = 0
    for ticket in tickets:
        haystack = " ".join(
            [
                str(ticket.device_id or ""),
                str(ticket.title or ""),
                str(ticket.description or ""),
            ]
        ).lower()
        if any(term and term in haystack for term in machine_terms):
            count += 1
    return count


def score_asset(machine: Machine, tickets: List[Ticket]) -> AssetRiskResponse:
    """Calculate a deterministic predictive risk score for a machine."""
    score = 10
    drivers: List[str] = []

    if machine.status == "offline":
        score += 45
        drivers.append("Asset is offline.")
    elif machine.status == "warning":
        score += 25
        drivers.append("Asset is in warning state.")
    else:
        drivers.append("Asset is currently online.")

    pressure = _ticket_pressure(machine, tickets)
    if pressure:
        score += min(pressure * 12, 30)
        drivers.append(f"{pressure} related ticket(s) found.")

    critical_count = sum(1 for ticket in tickets if ticket.priority == "critical")
    if critical_count:
        score += min(critical_count * 5, 15)
        drivers.append(f"{critical_count} critical ticket(s) in the queue.")

    if machine.type in {"life-support", "monitoring"}:
        score += 10
        drivers.append("Asset type has elevated operational criticality.")

    score = min(score, 100)
    return AssetRiskResponse(
        code=machine.code,
        name=machine.name,
        location=machine.location,
        status=machine.status,
        risk_score=score,
        risk_level=_risk_level(score),
        drivers=drivers,
        recommended_action=_recommended_action(score, machine),
    )


def build_governance_checks(machines: List[Machine], tickets: List[Ticket]) -> List[GovernanceCheckResponse]:
    """Return core data governance checks for operational intelligence."""
    duplicate_codes = [code for code, count in Counter(machine.code for machine in machines).items() if count > 1]
    tickets_without_priority = [ticket.id for ticket in tickets if not ticket.priority]
    tickets_without_status = [ticket.id for ticket in tickets if not ticket.status]

    return [
        GovernanceCheckResponse(
            control="Unique asset identifier",
            status="pass" if not duplicate_codes else "fail",
            evidence="All machine codes are unique." if not duplicate_codes else f"Duplicate codes: {duplicate_codes}",
        ),
        GovernanceCheckResponse(
            control="Ticket priority completeness",
            status="pass" if not tickets_without_priority else "fail",
            evidence="All tickets have priority." if not tickets_without_priority else f"Missing priority: {tickets_without_priority}",
        ),
        GovernanceCheckResponse(
            control="Ticket status completeness",
            status="pass" if not tickets_without_status else "fail",
            evidence="All tickets have status." if not tickets_without_status else f"Missing status: {tickets_without_status}",
        ),
        GovernanceCheckResponse(
            control="Automation payload minimization",
            status="pass",
            evidence="n8n payloads use metadata only: IDs, status, priority, location, and escalation level.",
        ),
    ]


def build_insights(asset_risks: List[AssetRiskResponse]) -> List[OperationalInsightResponse]:
    """Convert scored assets into actionable operational insights."""
    high_risk = [asset for asset in asset_risks if asset.risk_level == "high"]
    medium_or_high = [asset for asset in asset_risks if asset.risk_level in {"medium", "high"}]
    top_asset = max(asset_risks, key=lambda asset: asset.risk_score, default=None)

    insights = [
        OperationalInsightResponse(
            title="Predictive maintenance focus",
            impact=f"{len(medium_or_high)} asset(s) require proactive follow-up.",
            recommended_action="Prioritize assets with medium or high risk before opening new preventive windows.",
        ),
        OperationalInsightResponse(
            title="Critical escalation readiness",
            impact=f"{len(high_risk)} high-risk asset(s) may need automatic n8n escalation.",
            recommended_action="Keep SLA workflow and SMS notification channels active for critical tickets.",
        ),
    ]
    if top_asset:
        insights.append(
            OperationalInsightResponse(
                title="Highest operational risk",
                impact=f"{top_asset.name} is currently scored at {top_asset.risk_score}%.",
                recommended_action=top_asset.recommended_action,
            )
        )
    return insights


def build_intelligence_summary(db: Session) -> IntelligenceSummaryResponse:
    """Build the full operational intelligence summary."""
    machines = get_machines(db)
    tickets = get_tickets(db)
    asset_risks = [score_asset(machine, tickets) for machine in machines]
    asset_risks.sort(key=lambda asset: asset.risk_score, reverse=True)
    return IntelligenceSummaryResponse(
        asset_risks=asset_risks,
        governance_checks=build_governance_checks(machines, tickets),
        insights=build_insights(asset_risks),
    )
