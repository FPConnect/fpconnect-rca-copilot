from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .memory import ConversationState, MemoryStore


BACKEND_ENV_VAR = "FP_AGENT_BACKEND"


LLMCallable = Callable[[str, ConversationState], str]


def default_llm(prompt: str, state: ConversationState) -> str:
    """LLM muito simples somente para demonstração.

    Ele tenta inferir a intenção pelo texto e responde de forma
    determinística, sem depender de APIs externas.
    """
    text = prompt.lower().strip()

    if any(word in text for word in ["oi", "olá", "ola", "hello", "hi"]):
        return "Olá! Eu sou o seu agente de IA local. Como posso ajudar hoje?"

    if "resum" in text or "summary" in text or "resumo" in text:
        summary = state.summary()
        return "Aqui está um resumo recente da nossa conversa:\n" + summary

    if "ideia" in text or "idéia" in text or "idea" in text:
        return (
            "Algumas ideias: 1) Dividir o problema em partes menores; "
            "2) Priorizar o que traz mais valor; 3) Definir próximos passos claros."
        )

    if "tarefa" in text or "todo" in text or "próximo passo" in text:
        return (
            "Posso te ajudar a estruturar tarefas. Me diga o objetivo principal, "
            "e eu sugerirei 3 próximos passos concretos."
        )

    if "ajuda" in text or "help" in text:
        return (
            "Posso: (1) Resumir nossa conversa, (2) Ajudar a quebrar problemas em tarefas, "
            "(3) Servir como bloco de anotações inteligente. Pergunte algo específico."
        )

    last_user = state.last_user_message()
    if last_user:
        return (
            "Entendi o que você disse antes e agora: vou guardar isso no contexto. "
            "Ainda sou um agente simples, então respondo de forma determinística, "
            "mas você pode me estender para usar um LLM real."
        )

    return (
        "Sou um agente de IA minimalista rodando localmente. "
        "Me conte o que você quer fazer e eu ajudo a organizar suas ideias."
    )


@dataclass
class Agent:
    memory_store: MemoryStore
    llm: LLMCallable = default_llm

    def run_turn(self, user_input: str, state: ConversationState) -> str:
        state.add("user", user_input)
        reply = self.llm(user_input, state)
        state.add("agent", reply)
        self.memory_store.save(state)
        return reply

    def describe_capabilities(self) -> str:
        return (
            "Recursos do agente:\n"
            "- Memória persistente de conversa em arquivo local.\n"
            "- Respostas determinísticas baseadas em regras simples (sem depender de APIs).\n"
            "- Capacidade de resumir as últimas interações.\n"
            "- Estrutura pronta para conectar um LLM real depois (por exemplo, OpenAI).\n"
        )
