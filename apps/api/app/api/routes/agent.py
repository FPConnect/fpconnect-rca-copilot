"""Rotas HTTP para o agente de IA integrado ao FPConnect."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user_payload
from app.services.agent_service import handle_message, analyze_ticket


router = APIRouter(prefix="/agent", tags=["agent"])


class AgentChatRequest(BaseModel):
    message: str


class AgentChatResponse(BaseModel):
    reply: str
    backend: str


class TicketContext(BaseModel):
    title: str
    description: str | None = None
    priority: str | None = None
    status: str | None = None


class TicketAgentRequest(BaseModel):
    ticket: TicketContext
    question: str


class TicketAgentResponse(BaseModel):
    reply: str
    backend: str


@router.post("/chat", response_model=AgentChatResponse)
def chat_endpoint(
    payload: AgentChatRequest,
    _current_user: dict = Depends(get_current_user_payload),
) -> AgentChatResponse:
    """Envia uma mensagem para o agente e retorna a resposta.

    O backend (regras ou OpenAI) é determinado pelas variáveis de ambiente
    do próprio agente.
    """

    result = handle_message(payload.message)
    return AgentChatResponse(**result)


@router.post("/tickets/analyze", response_model=TicketAgentResponse)
def analyze_ticket_endpoint(
    payload: TicketAgentRequest,
    _current_user: dict = Depends(get_current_user_payload),
) -> TicketAgentResponse:
    """Endpoint específico para análise de tickets.

    Recebe os campos principais do ticket + uma pergunta do técnico
    e usa o agente para sugerir próximos passos, hipóteses, etc.
    """

    result = analyze_ticket(payload.ticket.model_dump(), payload.question)
    return TicketAgentResponse(**result)
