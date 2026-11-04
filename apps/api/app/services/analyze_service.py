"""Evidence retrieval constrained to reviewed and authorized knowledge.

Lexical retrieval intentionally replaces the legacy unscoped vector query.
It never treats relevance as a probability or a confirmed technical cause.
"""
from __future__ import annotations

import re
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import AnalyzeTicketRequest, RCASuggestionResponse

_STOPWORDS = {
    "para", "quando", "com", "uma", "sem", "dos", "das", "que",
    "por", "this", "with", "from", "equipment", "equipamento",
    "falha", "failure", "problema", "problem", "service", "chamado",
}


def _keywords(description: str) -> list[str]:
    terms: list[str] = []
    for word in re.findall(r"\w+", description.lower(), re.UNICODE):
        if len(word) < 4 or word in _STOPWORDS or word in terms:
            continue
        terms.append(word[:60])
        if len(terms) == 8:
            break
    return terms


def get_root_cause_analysis(db: Session, description: str, requester_id: int):
    """Search only approved articles in permitted visibility scopes.

    The workspace membership is resolved server-side from the authenticated
    requester's ID. The caller cannot insert a workspace or bypass approval.
    Legacy records remain completely excluded. The score is deliberately
    zero rather than a fabricated confidence/probability.
    """
    if requester_id <= 0:
        return []
    words = _keywords(description)
    if not words:
        return []
    patterns = []
    params: dict[str, str | int] = {"requester_id": requester_id}
    for i, word in enumerate(words):
        key = f"token_{i}"
        patterns.append(
            f"(lower(kb.title) LIKE :{key} OR lower(coalesce(kb.tags, '')) LIKE :{key} "
            f"OR lower(coalesce(kb.equipment_family, '')) LIKE :{key} "
            f"OR lower(coalesce(kb.failure_code, '')) LIKE :{key})"
        )
        params[key] = f"%{word}%"
    query = text(
        """
        SELECT kb.title, 0.0 AS similarity
        FROM kb_articles AS kb
        WHERE kb.review_status = 'approved'
          AND (
            kb.visibility = 'global'
            OR (kb.visibility = 'private' AND kb.owner_id = :requester_id)
            OR (
              kb.visibility = 'workspace'
              AND EXISTS (
                SELECT 1 FROM knowledge_memberships AS km
                WHERE km.workspace_id = kb.workspace_id
                  AND km.user_id = :requester_id
              )
            )
          )
          AND (""" + " OR ".join(patterns) + """)
        ORDER BY kb.id DESC
        LIMIT 3
        """
    )
    return db.execute(query, params).fetchall()


def analyze_ticket(
    db: Session,
    ticket: Ticket,
    request: AnalyzeTicketRequest,
    *,
    requester_id: int | None = None,
) -> List[RCASuggestionResponse]:
    """Return unverified knowledge matches for an authorized ticket."""
    description = " ".join(
        filter(None, [
            ticket.title or "",
            ticket.description or "",
            request.context or "",
        ])
    ).strip()[:6000]

    english = request.language == "en-US"
    if not description:
        return [
            RCASuggestionResponse(
                cause="Insufficient data for analysis" if english else "Dados insuficientes para análise",
                confidence=0.0,
                resolution=(
                    "Add context using only authorized, non-sensitive technical records."
                    if english else
                    "Adicione contexto técnico autorizado, sem dados pessoais ou sigilosos."
                ),
                similar_incidents=[],
            )
        ]

    try:
        matches = (
            get_root_cause_analysis(db, description, requester_id)
            if requester_id is not None else []
        )
    except Exception:
        # Fail closed if the governance migration is absent or storage fails.
        matches = []

    if not matches:
        return [
            RCASuggestionResponse(
                cause=(
                    "No approved and authorized related article found"
                    if english else
                    "Nenhum artigo relacionado, aprovado e autorizado foi encontrado"
                ),
                confidence=0.0,
                resolution=(
                    "Request qualified technical review using an authorized secure channel."
                    if english else
                    "Solicite revisão técnica qualificada por um canal seguro e autorizado."
                ),
                similar_incidents=[],
            )
        ]

    return [
        RCASuggestionResponse(
            cause=(
                f"Related reference (not a confirmed cause): {row.title}"
                if english else f"Referência relacionada (não confirma causa): {row.title}"
            ),
            confidence=0.0,
            # Do not surface an unrestricted historical repair procedure as
            # automatic physical maintenance instructions.
            resolution=(
                "Review the cited KB article and underlying evidence with an authorized engineer."
                if english else
                "Revise o artigo original e as evidências com o profissional técnico autorizado."
            ),
            similar_incidents=[],
        )
        for row in matches
    ]
