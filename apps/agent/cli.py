from __future__ import annotations

import sys

from .agent import Agent
from .config import settings
from .memory import MemoryStore


BANNER = f"""
==============================
 {settings.app_name} - Agente de IA Local
==============================
Comandos especiais:
  :help    mostra esta ajuda
  :quit    sai do agente
  :resumo  mostra um resumo recente da conversa
  :recursos mostra os recursos disponíveis do agente
"""


def run_cli() -> None:
    store = MemoryStore(settings.memory_path)
    state = store.load()
    agent = Agent(memory_store=store)

    print(BANNER)

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo... Até a próxima!")
            break

        if not user_input:
            continue

        if user_input in {":quit", ":q", ":sair"}:
            print("Agente: Até a próxima!")
            break

        if user_input in {":help", ":h"}:
            print(BANNER)
            continue

        if user_input == ":resumo":
            print("Agente (resumo):")
            print(state.summary())
            continue

        if user_input == ":recursos":
            print("Agente:")
            print(agent.describe_capabilities())
            continue

        reply = agent.run_turn(user_input, state)
        print(f"Agente: {reply}")


def main() -> None:  # entrypoint para python -m
    run_cli()


if __name__ == "__main__":  # pragma: no cover
    main()
