"""Integração da API FPConnect com o agente de IA local.

Este serviço reaproveita o código em apps/agent.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Mapping

# Garantir que o diretório raiz do monorepo esteja no sys.path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from apps.agent.agent import Agent, BACKEND_ENV_VAR  # type: ignore  # noqa: E402
except ModuleNotFoundError:
    # Fallback para import relativo se rodando em ambiente de teste
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
    from apps.agent.agent import Agent, BACKEND_ENV_VAR  # type: ignore  # noqa: E402
from apps.agent.config import settings as agent_settings  # type: ignore  # noqa: E402
from apps.agent.memory import ConversationState, MemoryStore  # type: ignore  # noqa: E402


def _get_memory_path() -> Path:
    """Resolve o caminho de memória usado pelo agente dentro da API.

    Se a variável FP_AGENT_MEMORY_PATH estiver definida, usa esse caminho.
    Caso contrário, reutiliza o caminho padrão do agente de CLI.
    """

    override = os.getenv("FP_AGENT_MEMORY_PATH")
    if override:
        return Path(override)
    return Path(agent_settings.memory_path)


def get_agent_and_state() -> tuple[Agent, ConversationState, str]:
    memory_path = _get_memory_path()
    store = MemoryStore(memory_path)
    state = store.load()
    agent = Agent(memory_store=store)
    backend = os.getenv(BACKEND_ENV_VAR, "rules").lower().strip()
    return agent, state, backend


def handle_message(message: str) -> Dict[str, str]:
    """Executa um turno do agente e retorna a resposta e o backend ativo."""

    agent, state, backend = get_agent_and_state()
    reply = agent.run_turn(message, state)
    return {"reply": reply, "backend": backend}


def analyze_ticket(ticket: Mapping[str, object], question: str) -> Dict[str, str]:
    """Gera uma resposta do agente usando o contexto de um ticket.

    O objetivo aqui é ser mais "FPConnect-specific": o agente recebe
    título, prioridade, status e descrição do ticket e responde à
    pergunta do técnico com esse contexto.
    """

    title = str(ticket.get("title", "(sem título)"))
    priority = str(ticket.get("priority", "(sem prioridade)"))
    status = str(ticket.get("status", "(sem status)"))
    description = str(ticket.get("description", "")) or "(sem descrição)"

    composed = (
        "Você é um assistente de RCA/field service. Use o contexto do "
        "ticket abaixo para responder de forma curta, objetiva e em "
        "português para o técnico.\n\n"
        f"Título: {title}\n"
        f"Prioridade: {priority}\n"
        f"Status: {status}\n"
        f"Descrição: {description}\n\n"
        f"Pergunta do técnico: {question}\n\n"
        "Responda com no máximo 3 frases, focando em próximos passos ou "
        "hipóteses principais."
    )

    agent, state, backend = get_agent_and_state()
    reply = agent.run_turn(composed, state)
    return {"reply": reply, "backend": backend}
