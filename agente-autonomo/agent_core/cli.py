from __future__ import annotations

from .agent import create_agent
from .memory import ConversationState, Message


BANNER = """
==============================
 Agente Autônomo Local (CLI)
==============================
Comandos diretos:
  help                 mostra esta ajuda
  tools                lista as ferramentas locais
  terminal: <cmd>      executa um comando no shell
    abrir url: <url>     abre uma URL na janela interna do agente
  rdp[: caminho.rdp]   abre o cliente de área de trabalho remota (Windows)
  falar: <texto>       lê o texto em voz alta (TTS)
  quit / sair          encerra o agente
"""


def _find_last_suggested(state: ConversationState) -> str | None:
        """Encontra o último comando sugerido (SUGGESTED:...)."""

        for m in reversed(state.messages):
                if m.role == "agent" and m.content.startswith("SUGGESTED:"):
                        return m.content[len("SUGGESTED:") :].strip()
        return None


def run_cli() -> None:
    agent = create_agent()
    state: ConversationState = agent.load_state()
    auto_accept = False

    print(BANNER)

    while True:
        try:
            user_input = input("Comando> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if not user_input:
            continue

        lowered = user_input.lower()
        if lowered in {"quit", ":q", "sair", "exit"}:
            print("Até a próxima!")
            break

        reply = agent.handle_command(user_input, state)
        state.add("agent", reply)
        agent.save_state(state)
        print(f"-> {reply}")

        # Se houve sugestão de comando, oferecer confirmação rápida.
        suggested = _find_last_suggested(state)
        if suggested:
            if auto_accept:
                print(f"[auto] Executando sugestão: {suggested}")
                confirm = agent.handle_command(suggested, state)
                state.add("agent", confirm)
                agent.save_state(state)
                print(f"-> {confirm}")
                continue

            choice = input("Executar sugestão? [y/N/t=confiar na sessão] ").strip().lower()
            if choice in {"y", "s"}:
                print(f"[ok] Executando sugestão: {suggested}")
                confirm = agent.handle_command(suggested, state)
                state.add("agent", confirm)
                agent.save_state(state)
                print(f"-> {confirm}")
            elif choice == "t":
                auto_accept = True
                print("Sugestões futuras nesta sessão serão executadas automaticamente.")


def main() -> None:  # entrypoint para python -m
    run_cli()


if __name__ == "__main__":  # pragma: no cover
    main()
