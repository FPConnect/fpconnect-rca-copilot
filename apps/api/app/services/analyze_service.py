"""RCA analyzer service using semantic search with pgvector."""

from functools import lru_cache
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import AnalyzeTicketRequest, RCASuggestionResponse


@lru_cache(maxsize=1)
def get_model():
    """Load embedding model once per process."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def get_root_cause_analysis(db: Session, description: str):
    """Return top matching KB articles by embedding similarity."""
    vector = get_model().encode(description).tolist()
    query = text(
        """
        SELECT title, content, 1 - (embedding <=> :v) as similarity
        FROM kb_articles
        WHERE embedding IS NOT NULL
          AND 1 - (embedding <=> :v) > 0.7
        ORDER BY similarity DESC
        LIMIT 3
    """
    )
    return db.execute(query, {"v": str(vector)}).fetchall()


def analyze_ticket(
    db: Session, ticket: Ticket, request: AnalyzeTicketRequest
) -> List[RCASuggestionResponse]:
    """Generate RCA suggestions for a ticket using semantic KB search."""
    description = " ".join(
        filter(
            None,
            [
                ticket.title or "",
                ticket.description or "",
                request.context or "",
            ],
        )
    ).strip()

    if not description:
        return [
            RCASuggestionResponse(
                cause="Dados insuficientes para análise",
                confidence=0.0,
                resolution="Adicione descrição detalhada e contexto técnico do incidente.",
                similar_incidents=[],
            )
        ]

    try:
        rows = get_root_cause_analysis(db, description)
    except Exception:
        rows = []

    if not rows:
        return [
            RCASuggestionResponse(
                cause="Nenhuma causa semelhante encontrada na base de conhecimento",
                confidence=0.5,
                resolution="Escalone para N2 e inclua logs para enriquecer a base.",
                similar_incidents=[],
            )
        ]

    return [
        RCASuggestionResponse(
            cause=row.title,
            confidence=float(row.similarity),
            resolution=row.content,
            similar_incidents=[],
        )
        for row in rows
    ]
