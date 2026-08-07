from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from agent_core.config import settings
from agent_core.knowledge import KnowledgeBase

BLOCKED_MARKERS = (
    "nao reconheci um plano de acao seguro",
    "posso te ajudar de dois jeitos",
    "olá. posso responder perguntas gerais",
    "ola. posso responder perguntas gerais",
    "entendi. se quiser, eu respondo direto",
    "quero te responder no estilo copiloto",
    "faltou contexto para eu ser preciso",
    "sugestao do agente",
)


def _is_blocked_answer(answer: str) -> bool:
    lowered = answer.strip().lower()
    if not lowered:
        return True
    return any(marker in lowered for marker in BLOCKED_MARKERS)


def _safe_load_messages(memory_path: Path) -> list[dict[str, str]]:
    if not memory_path.exists():
        return []
    try:
        payload = json.loads(memory_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    raw = payload.get("messages", []) if isinstance(payload, dict) else []
    if not isinstance(raw, list):
        return []
    messages: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()
        if not role or not content:
            continue
        messages.append({"role": role, "content": content})
    return messages


def _load_offset(offset_path: Path) -> int:
    if not offset_path.exists():
        return 0
    try:
        return int(offset_path.read_text(encoding="utf-8").strip())
    except Exception:
        return 0


def _save_offset(offset_path: Path, value: int) -> None:
    offset_path.write_text(str(max(0, value)), encoding="utf-8")


def _learn_from_messages(memory_path: Path, db_path: Path, offset_path: Path) -> int:
    messages = _safe_load_messages(memory_path)
    if not messages:
        _save_offset(offset_path, 0)
        return 0

    start = _load_offset(offset_path)
    start = max(0, min(start, len(messages)))

    learned = 0
    kb = KnowledgeBase(db_path)
    try:
        i = start
        while i < len(messages) - 1:
            current = messages[i]
            nxt = messages[i + 1]
            if current["role"] != "user":
                i += 1
                continue
            if nxt["role"] != "agent":
                i += 1
                continue

            question = current["content"].strip()
            answer = nxt["content"].strip()
            if question and answer and not _is_blocked_answer(answer):
                try:
                    if not kb.has_question(question):
                        kb.add(question, answer)
                        learned += 1
                except Exception:
                    pass
            i += 2
    finally:
        kb.close()

    _save_offset(offset_path, len(messages))
    return learned


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop de aprendizado continuo do agente")
    parser.add_argument("--interval-seconds", type=float, default=1.0, help="Intervalo entre ciclos")
    parser.add_argument("--reports-dir", type=str, default="", help="Diretorio para estado e log")
    args = parser.parse_args()

    interval = max(0.2, args.interval_seconds)

    memory_path = settings.memory_path
    base_dir = memory_path.parent
    reports_dir = Path(args.reports_dir).resolve() if args.reports_dir else (Path(__file__).resolve().parent / "qa_loop_reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    offset_path = reports_dir / "learning.offset"
    heartbeat_path = reports_dir / "learning.heartbeat"
    db_path = base_dir / "knowledge.db"

    while True:
        learned = _learn_from_messages(memory_path, db_path, offset_path)
        heartbeat_path.write_text(f"last_run={time.time():.3f} learned={learned}\n", encoding="utf-8")
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
