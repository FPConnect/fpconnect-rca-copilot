from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "http://127.0.0.1:8012/api/command"


@dataclass(frozen=True)
class LiveCase:
    prompt: str
    expect_contains_any: tuple[str, ...] = ()
    expect_not_contains_any: tuple[str, ...] = ()
    agent_mode: bool = True


def post_command(prompt: str, agent_mode: bool, login_context: dict | None) -> str:
    payload = {
        "input": prompt,
        "auto_accept": True,
        "agent_mode": agent_mode,
        "login_context": login_context,
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(API_URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    parsed = json.loads(raw)
    return str(parsed.get("reply") or "")


def build_cases() -> list[LiveCase]:
    base = [
        LiveCase(
            prompt="analise o meu perfil e busque vagas em que eu possa ser encaixado",
            expect_contains_any=("nao vou executar uma busca generica",),
        ),
        LiveCase(
            prompt="entre no meu linkedin e busque vagas com meu perfil",
            expect_contains_any=("nao vou executar uma busca generica",),
        ),
        LiveCase(
            prompt="analise o que combina comigo e vagas no linkedin",
            expect_contains_any=("nao vou executar uma busca generica",),
        ),
        LiveCase(
            prompt="abra https://www.google.com",
            expect_contains_any=("google", "janela interna"),
        ),
        LiveCase(
            prompt="abra meu github",
            expect_contains_any=("github", "janela interna"),
        ),
        LiveCase(
            prompt="com base no meu perfil busque vagas de engenheiro de dados senior com python no linkedin",
            expect_contains_any=("linkedin", "jobs/search", "janela interna"),
            expect_not_contains_any=("nao vou executar uma busca generica",),
        ),
    ]

    google_topics = [
        "clima em lisboa",
        "cotacao do dolar hoje",
        "feriados nacionais 2026",
        "python dataclass examples",
        "o que e kubernetes",
        "como funciona ipv6",
        "receita de pao caseiro",
        "noticias tecnologia brasil",
        "diferença entre sql e nosql",
        "como estudar para certificacao aws",
    ]

    linkedin_queries = [
        "engenheiro de dados senior python",
        "analista de dados pleno sql",
        "devops kubernetes aws",
        "qa automation python",
        "backend java spring",
        "frontend react typescript",
    ]

    for topic in google_topics:
        base.append(
            LiveCase(
                prompt=f"pesquise no google sobre {topic}",
                expect_contains_any=("google", "janela interna", "pesquisando"),
            )
        )

    for q in linkedin_queries:
        base.append(
            LiveCase(
                prompt=f"busque vagas de {q} no linkedin",
                expect_contains_any=("linkedin", "jobs/search", "janela interna"),
            )
        )

    # Add random variants to broaden real traffic without overloading runtime.
    actions = ["pesquise", "procure", "busque", "encontre"]
    places = ["brasil", "portugal", "europa", "sao paulo", "rio de janeiro"]
    roles = ["engenheiro de dados", "analista de dados", "devops", "qa", "backend"]
    skills = ["python", "sql", "aws", "java", "react"]

    random.seed(123)
    for _ in range(80):
        a = random.choice(actions)
        role = random.choice(roles)
        skill = random.choice(skills)
        place = random.choice(places)
        base.append(
            LiveCase(
                prompt=f"{a} vagas de {role} com {skill} no linkedin em {place}",
                expect_contains_any=("linkedin", "jobs/search", "janela interna"),
            )
        )

    return base


def run(login_service: str, login_user: str, login_password: str, cycles: int) -> int:
    login_context = None
    if login_user and login_password:
        login_context = {
            "service": login_service or "linkedin",
            "username": login_user,
            "password": login_password,
        }

    cases = build_cases()
    failures: list[str] = []
    started = time.time()

    # Optional real login check when creds are provided.
    if login_context:
        try:
            reply = post_command("faça login no linkedin", agent_mode=True, login_context=login_context)
            lower = reply.lower()
            if "login" not in lower and "credenciais" not in lower and "linkedin" not in lower:
                failures.append("login_check: resposta inesperada no teste de login")
        except Exception as exc:
            failures.append(f"login_check_error: {exc}")

    total = len(cases) * cycles
    done = 0

    for cycle in range(1, cycles + 1):
        for idx, case in enumerate(cases, start=1):
            try:
                reply = post_command(case.prompt, case.agent_mode, login_context)
            except HTTPError as exc:
                failures.append(f"cycle={cycle} case={idx} HTTPError={exc.code}")
                continue
            except URLError as exc:
                failures.append(f"cycle={cycle} case={idx} URLError={exc}")
                continue
            except Exception as exc:
                failures.append(f"cycle={cycle} case={idx} Exception={exc}")
                continue

            lower = reply.lower()
            if case.expect_contains_any and not any(token in lower for token in case.expect_contains_any):
                failures.append(
                    f"cycle={cycle} case={idx} contains_miss prompt={case.prompt!r} reply={reply[:260]!r}"
                )
            if case.expect_not_contains_any and any(token in lower for token in case.expect_not_contains_any):
                failures.append(
                    f"cycle={cycle} case={idx} contains_forbidden prompt={case.prompt!r} reply={reply[:260]!r}"
                )

            done += 1
            if len(failures) >= 100:
                break
        if cycle % max(1, cycles // 10) == 0 or cycle == cycles:
            elapsed = time.time() - started
            print(f"progress cycle={cycle}/{cycles} checks={done}/{total} failures={len(failures)} elapsed={elapsed:.1f}s")
        if len(failures) >= 100:
            break

    print("--- LIVE SUMMARY ---")
    print(f"cycles={cycles}")
    print(f"cases_per_cycle={len(cases)}")
    print(f"total_checks={done}")
    print(f"failures={len(failures)}")

    if failures:
        for row in failures[:30]:
            print(row)
        print("status=FAILED")
        return 1

    print("status=PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Live environment API regression for agent mode")
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--login-service", default="linkedin")
    parser.add_argument("--login-user", default="")
    parser.add_argument("--login-password", default="")
    args = parser.parse_args()
    return run(args.login_service, args.login_user, args.login_password, args.cycles)


if __name__ == "__main__":
    raise SystemExit(main())
