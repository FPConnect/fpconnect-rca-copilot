"""Clinical diagnosis endpoint focused on root cause and recommended action."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.crud.ticket import complete_ticket_analysis, get_ticket_by_id
from app.schemas.ticket import AnalyzeIncidentRequest, AnalyzeIncidentResponse, AnalyzeTicketRequest
from app.services.analyze_service import analyze_ticket

router = APIRouter()


@router.post("", response_model=AnalyzeIncidentResponse)
def analyze_incident(
    request: AnalyzeIncidentRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Run clinical failure diagnosis for an incident and persist the result."""
    ticket = get_ticket_by_id(db, request.ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    suggestions = analyze_ticket(db, ticket, AnalyzeTicketRequest(context=request.context))
    primary = suggestions[0] if suggestions else None
    root_cause = primary.cause if primary else "Causa raiz não determinada"
    recommendation = primary.resolution if primary and primary.resolution else "Acionar engenharia clínica N2."
    explanation = (
        f"Diagnóstico gerado a partir da ocorrência #{ticket.id}, descrição informada e histórico técnico. "
        f"Confiança estimada: {primary.confidence:.0%}." if primary else
        "Não havia dados suficientes para estimar confiança do diagnóstico."
    )

    complete_ticket_analysis(
        db,
        ticket,
        root_cause=root_cause,
        recommendation=recommendation,
    )
    return AnalyzeIncidentResponse(
        ticket_id=ticket.id,
        root_cause=root_cause,
        recommendation=recommendation,
        explanation=explanation,
    )
