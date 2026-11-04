"""Technical hypotheses with mandatory human confirmation before persistence."""

from __future__ import annotations

import json
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, require_access_level
from app.core.database import get_db
from app.crud.ticket import complete_ticket_analysis, get_ticket_by_id
from app.models.ticket import TicketLog
from app.schemas.ticket import (
    AnalyzeIncidentRequest,
    AnalyzeIncidentResponse,
    AnalyzeTicketRequest,
    ConfirmIncidentAnalysisRequest,
    ConfirmIncidentAnalysisResponse,
)
from app.services.analyze_service import analyze_ticket

router = APIRouter()


@router.post("", response_model=AnalyzeIncidentResponse)
def analyze_incident(
    request: AnalyzeIncidentRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(2)),
):
    """Suggest a technical hypothesis without writing a confirmed root cause.

    Similarity scores from the knowledge base are NOT calibrated probabilities.
    An engineer must validate any recommendation and follow applicable procedures.
    """
    ticket = get_ticket_by_id(db, request.ticket_id)
    if not ticket or (
        current_user.access_level < 3 and ticket.creator_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    suggestions = analyze_ticket(
        db,
        ticket,
        AnalyzeTicketRequest(context=request.context, language=request.language),
        requester_id=current_user.id,
    )
    primary = suggestions[0] if suggestions else None
    english = request.language == "en-US"
    root_cause = (
        primary.cause
        if primary
        else ("No supported hypothesis" if english else "Sem hipótese sustentada")
    )
    recommendation = (
        "Request qualified technical review of the source evidence; do not perform repairs based on this suggestion alone."
        if english
        else "Solicite revisão técnica qualificada das evidências; não execute reparos com base apenas nesta sugestão."
    )
    if primary:
        explanation = (
            f"Unconfirmed hypothesis for incident #{ticket.id}, based on available records. "
            "Similarity/retrieval scores are not calibrated confidence or proof of causality. "
            "Human review is required; the ticket's confirmed root cause was NOT changed."
            if english
            else f"Hipótese não confirmada para a ocorrência #{ticket.id}, baseada nos registros disponíveis. "
            "Pontuações de similaridade não são confiança calibrada nem prova de causalidade. "
            "Revisão humana obrigatória; a causa raiz confirmada do chamado NÃO foi alterada."
        )
    else:
        explanation = (
            "Insufficient evidence to support a hypothesis; no conclusion was stored."
            if english
            else "Evidências insuficientes para sustentar hipótese; nenhuma conclusão foi gravada."
        )

    # Metadata-only audit; never log raw context, descriptions, patient data or output.
    db.add(TicketLog(
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="analysis_hypothesis_requested",
        detail=json.dumps({"schema": "responsible-ai-v1", "review_status": "pending"}),
    ))
    db.commit()
    return AnalyzeIncidentResponse(
        ticket_id=ticket.id,
        root_cause=root_cause,
        recommendation=recommendation,
        explanation=explanation,
    )


@router.post(
    "/{ticket_id}/confirm",
    response_model=ConfirmIncidentAnalysisResponse,
)
def confirm_incident_analysis(
    ticket_id: int,
    payload: ConfirmIncidentAnalysisRequest,
    db: Session = Depends(get_db),
    reviewer: AuthenticatedUser = Depends(require_access_level(3)),
):
    """Persist a technical conclusion only after explicit qualified human sign-off.

    The reviewer attests that evidence references are available through the
    organization's authorized record system. Reference tokens aren't raw logs.
    """
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    # Restrict references to short, opaque ticket/test tokens instead of narrative,
    # URLs, credentials, e-mail addresses or patient information.
    if any(not re.fullmatch(r"[a-zA-Z0-9_:\-.]{1,64}", ref) for ref in payload.evidence_refs):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Use short, non-sensitive evidence reference IDs only",
        )

    complete_ticket_analysis(
        db,
        ticket,
        root_cause=payload.root_cause,
        recommendation=payload.recommendation,
        commit=False,  # Audit event and reviewed conclusion must be atomic.
    )
    db.add(TicketLog(
        ticket_id=ticket.id,
        user_id=reviewer.id,
        action="analysis_human_confirmed",
        detail=json.dumps({
            "schema": "responsible-ai-v1",
            "review_status": "human_confirmed",
            "evidence_count": len(payload.evidence_refs),
        }),
    ))
    db.commit()
    return ConfirmIncidentAnalysisResponse(ticket_id=ticket.id, reviewer_id=reviewer.id)
