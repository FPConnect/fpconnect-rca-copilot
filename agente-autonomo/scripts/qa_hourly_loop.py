from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from agent_core.config import settings
from agent_core.knowledge import KnowledgeBase


API_URL = "http://127.0.0.1:8012/api/command"
GENERIC_FALLBACK_MARKERS = [
    "quero te responder no estilo copiloto",
    "faltou contexto para eu ser preciso",
    "me diz em uma frase o que voce quer agora",
]


KNOWN_EXPECTATIONS: dict[str, str] = {
    "quantos estados o brasil tem?": "26 estados e o Distrito Federal",
    "qual o estado mais populoso do chile?": "Regiao Metropolitana de Santiago",
    "qual e o seu signo?": "nao tenho data de nascimento",
    "e o signo?": "nao tenho data de nascimento",
    "quantas estrelas tem no espaco?": "10^22 a 10^24",
    "o sol e uma estrela?": "sim, o sol e uma estrela",
    "o que e buraco negro?": "regiao do espaco-tempo com gravidade extrema",
    "quantos planetas tem no sistema solar?": "8 planetas",
}


@dataclass
class AskResult:
    question: str
    answer: str
    ok: bool
    reason: str
    corrected: bool


def _ask(question: str, timeout: float = 12.0) -> str:
    payload = json.dumps({"input": question, "auto_accept": False}).encode("utf-8")
    req = Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8", errors="ignore"))
    return str(body.get("reply", "")).strip()


def _contains_generic_fallback(answer: str) -> bool:
    lowered = answer.lower()
    return any(marker in lowered for marker in GENERIC_FALLBACK_MARKERS)


def _heal_known_mismatch(question: str) -> bool:
    normalized = question.strip().lower()
    normalized = normalized.replace("?", "")
    normalized = " ".join(normalized.split())

    expected = KNOWN_EXPECTATIONS.get(question.strip().lower())
    if not expected:
        expected = KNOWN_EXPECTATIONS.get(normalized + "?") or KNOWN_EXPECTATIONS.get(normalized)
    if not expected:
        return False

    corrected_answer = {
        "quantos estados o brasil tem?": "O Brasil tem 26 estados e o Distrito Federal, totalizando 27 unidades federativas.",
        "qual o estado mais populoso do chile?": "No Chile nao existem estados; a divisao principal e por regioes. A mais populosa e a Regiao Metropolitana de Santiago.",
        "qual e o seu signo?": "Como IA, eu nao tenho data de nascimento, entao nao tenho signo.",
        "e o signo?": "Como IA, eu nao tenho data de nascimento, entao nao tenho signo.",
        "quantas estrelas tem no espaco?": "Nao existe um numero exato confirmado. A estimativa mais usada para o universo observavel fica na ordem de 10^22 a 10^24 estrelas.",
        "o sol e uma estrela?": "Sim. O Sol e uma estrela de tipo espectral G (ana amarela) e e a estrela central do Sistema Solar.",
        "o sol e uma estrela": "Sim. O Sol e uma estrela de tipo espectral G (ana amarela) e e a estrela central do Sistema Solar.",
        "o que e buraco negro?": "Um buraco negro e uma regiao do espaco-tempo com gravidade tao intensa que nem a luz escapa apos cruzar o horizonte de eventos.",
        "o que e buraco negro": "Um buraco negro e uma regiao do espaco-tempo com gravidade tao intensa que nem a luz escapa apos cruzar o horizonte de eventos.",
        "quantos planetas tem no sistema solar?": "O Sistema Solar tem 8 planetas reconhecidos pela IAU: Mercurio, Venus, Terra, Marte, Jupiter, Saturno, Urano e Netuno.",
        "quantos planetas tem no sistema solar": "O Sistema Solar tem 8 planetas reconhecidos pela IAU: Mercurio, Venus, Terra, Marte, Jupiter, Saturno, Urano e Netuno.",
    }.get(question.strip().lower())

    if not corrected_answer:
        corrected_answer = {
            "o sol e uma estrela": "Sim. O Sol e uma estrela de tipo espectral G (ana amarela) e e a estrela central do Sistema Solar.",
            "o que e buraco negro": "Um buraco negro e uma regiao do espaco-tempo com gravidade tao intensa que nem a luz escapa apos cruzar o horizonte de eventos.",
            "quantos planetas tem no sistema solar": "O Sistema Solar tem 8 planetas reconhecidos pela IAU: Mercurio, Venus, Terra, Marte, Jupiter, Saturno, Urano e Netuno.",
        }.get(normalized)

    if not corrected_answer:
        return False

    kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
    try:
        kb.add(question, corrected_answer)
    finally:
        kb.close()
    return True


def _evaluate(question: str, answer: str) -> tuple[bool, str, bool]:
    normalized_q = " ".join(question.strip().lower().replace("?", "").split())
    normalized_a = answer.strip().lower()

    if _contains_generic_fallback(answer):
        corrected = _heal_known_mismatch(normalized_q)
        return False, "generic_fallback", corrected

    expected = KNOWN_EXPECTATIONS.get(normalized_q) or KNOWN_EXPECTATIONS.get(normalized_q + "?")
    if expected and expected.lower() not in normalized_a:
        corrected = _heal_known_mismatch(normalized_q)
        return False, "known_expectation_mismatch", corrected

    if not answer.strip():
        corrected = _heal_known_mismatch(normalized_q)
        return False, "empty_answer", corrected

    return True, "ok", False


def _question_bank() -> list[str]:
    known = list(KNOWN_EXPECTATIONS.keys())
    geography = [
        "qual a capital da argentina?",
        "qual a moeda do japao?",
        "qual idioma principal da alemanha?",
        "em que continente fica o egito?",
        "qual a capital do canada?",
    ]
    conversational = [
        "esta pronto?",
        "qual e o seu nome?",
        "como configuro voce com llms?",
        "quais recursos voce tem?",
        "voce esta configurado?",
        "quero consultar todos os modelos",
    ]
    science = [
        "quantas estrelas tem no universo observavel?",
        "qual a velocidade da luz?",
        "o que e buraco negro?",
        "o sol e uma estrela?",
        "quantos planetas tem no sistema solar?",
    ]
    math = [
        "quanto e 17*23?",
        "quanto e 144/12?",
        "calcule 31+79",
        "resultado de (8+4)*3",
    ]

    all_questions = known + geography + conversational + science + math

    # Variantes com pequenas mutacoes para aumentar diversidade entre ciclos.
    suffixes = ["", " por favor", "", "", " agora", ""]
    variants: list[str] = []
    for q in all_questions:
        for suffix in suffixes:
            variants.append((q + suffix).strip())
            variants.append(q.replace("?", ""))
            variants.append(q.upper())
    return list(dict.fromkeys(variants))


def _generate_questions(count: int) -> list[str]:
    bank = _question_bank()
    random.shuffle(bank)
    if len(bank) >= count:
        return bank[:count]

    out = bank[:]
    while len(out) < count:
        q = random.choice(bank)
        # injeta um ruído leve para produzir perguntas diferentes no tempo
        token = random.choice(["", " hoje", " agora", " rapidamente", " com detalhe"])
        out.append((q + token).strip())
    return out[:count]


def run_cycle(count: int, reports_dir: Path) -> dict[str, Any]:
    questions = _generate_questions(count)
    results: list[AskResult] = []

    for question in questions:
        try:
            answer = _ask(question)
            ok, reason, corrected = _evaluate(question, answer)
        except Exception as exc:  # noqa: BLE001
            answer = f"<request_error: {exc}>"
            ok, reason, corrected = False, "request_error", False
        results.append(
            AskResult(
                question=question,
                answer=answer,
                ok=ok,
                reason=reason,
                corrected=corrected,
            )
        )

    ok_count = sum(1 for r in results if r.ok)
    fail_count = len(results) - ok_count
    corrected_count = sum(1 for r in results if r.corrected)

    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(results),
        "ok": ok_count,
        "fail": fail_count,
        "corrected": corrected_count,
        "failures": [
            {
                "question": r.question,
                "reason": r.reason,
                "answer": r.answer,
                "corrected": r.corrected,
            }
            for r in results
            if not r.ok
        ][:80],
    }

    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (reports_dir / f"qa_cycle_{ts}.json").write_text(
        json.dumps(summary, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    (reports_dir / "latest.json").write_text(
        json.dumps(summary, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop de QA do agente com autocorrecao limitada")
    parser.add_argument("--count", type=int, default=1500, help="Perguntas por ciclo")
    parser.add_argument("--interval", type=int, default=900, help="Intervalo entre ciclos (s)")
    parser.add_argument("--once", action="store_true", help="Executa um ciclo e sai")
    parser.add_argument(
        "--reports-dir",
        default=str(Path(__file__).resolve().parent / "qa_loop_reports"),
        help="Diretorio de relatorios",
    )
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)

    while True:
        summary = run_cycle(args.count, reports_dir)
        print(
            f"[QA] {summary['timestamp']} count={summary['count']} ok={summary['ok']} "
            f"fail={summary['fail']} corrected={summary['corrected']}",
            flush=True,
        )
        if args.once:
            return 0
        time.sleep(max(60, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
