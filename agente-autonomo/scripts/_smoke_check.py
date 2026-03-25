from __future__ import annotations

import argparse
from agent_core.agent import create_agent


def _stable_commands() -> list[str]:
    return [
        "qual e o seu nome?",
        "quais recursos voce tem?",
        "voce esta configurado?",
        "mercado: help",
        "mercado: trilha trader",
    ]


def _network_commands() -> list[str]:
    return [
        "mercado: ranking AAPL,MSFT",
        "mercado: analisar AAPL",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test do agente")
    parser.add_argument("--network", action="store_true", help="Inclui comandos que dependem de rede de mercado")
    parser.add_argument("--fail-fast", action="store_true", help="Sai no primeiro erro")
    args = parser.parse_args()

    agent = create_agent()
    state = agent.load_state()
    commands = _stable_commands()
    if args.network:
        commands.extend(_network_commands())

    for command in commands:
        try:
            result = agent.handle_command(command, state)
            print("---", command)
            print((result or "").replace("\n", " | ")[:500])
        except Exception as exc:  # noqa: BLE001
            print("---", command)
            print(f"[ERRO] {exc}")
            if args.fail_fast:
                return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
