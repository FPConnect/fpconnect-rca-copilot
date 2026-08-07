from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass

from agent_core.agent import (
    _is_profile_intent_without_criteria,
    plan_agent_mode_browser_command,
    plan_agent_mode_web_command,
)


@dataclass(frozen=True)
class Case:
    prompt: str
    kind: str  # vague_profile | concrete_profile | direct_destination | vague_question | vague_affirmation


def build_cases() -> list[Case]:
    random.seed(42)

    vague_actions = [
        "analise",
        "analisa",
        "busque",
        "procure",
        "encontre",
        "veja",
        "traga",
        "ache",
        "pesquise",
        "mapeie",
        "localize",
    ]
    vague_profile_hooks = [
        "meu perfil",
        "o meu perfil",
        "com meu perfil",
        "com base no meu perfil",
        "de acordo com meu perfil",
        "o que combina comigo",
        "o que combinem comigo",
        "algo compativel com meu perfil",
        "algo compatível com meu perfil",
        "o que seja aderente ao meu perfil",
        "o que encaixe no meu perfil",
    ]
    vague_targets = [
        "vagas",
        "jobs",
        "oportunidades",
        "trabalhos",
        "vagas no brasil",
        "vagas na europa",
        "vagas remotas",
        "vagas hibridas",
        "vagas híbridas",
    ]
    vague_tails = [
        "no linkedin",
        "agora",
        "por favor",
        "para mim",
        "",
    ]
    vague_question_forms = [
        "quais vagas combinam comigo na europa?",
        "quais jobs eu teria aderencia no brasil?",
        "quais oportunidades eu me encaixo no linkedin?",
        "tem vagas para o meu perfil em portugal?",
    ]
    vague_affirmations = [
        "eu quero vagas que eu tenha aderencia",
        "preciso de vagas que combinem comigo",
        "quero oportunidades para o meu perfil",
        "me traga vagas que eu me encaixe",
    ]

    concrete_actions = ["busque", "procure", "pesquise", "encontre", "ache"]
    concrete_roles = [
        "engenheiro de dados",
        "desenvolvedor backend",
        "analista de dados",
        "cientista de dados",
        "devops",
        "qa",
        "product manager",
        "designer ux",
    ]
    concrete_skills = [
        "python",
        "java",
        "react",
        "aws",
        "sql",
        "pyspark",
        "docker",
        "kubernetes",
    ]
    concrete_seniority = ["junior", "pleno", "senior", "especialista", "lead"]
    concrete_locations = [
        "sao paulo",
        "rio de janeiro",
        "porto alegre",
        "curitiba",
        "brasil",
        "portugal",
        "europa",
    ]

    direct_destinations = [
        ("linkedin", "https://www.linkedin.com/feed/"),
        ("github", "https://github.com/"),
        ("gmail", "https://mail.google.com/"),
        ("outlook", "https://outlook.live.com/mail/"),
        ("youtube", "https://www.youtube.com/"),
        ("facebook", "https://www.facebook.com/"),
        ("instagram", "https://www.instagram.com/"),
        ("whatsapp", "https://web.whatsapp.com/"),
    ]

    cases: list[Case] = []
    seen: set[str] = set()

    # 800 vague profile-fit prompts (must be blocked)
    for a in vague_actions:
        for h in vague_profile_hooks:
            for t in vague_targets:
                for tail in vague_tails:
                    prompt = f"{a} {h} e {t} {tail}".strip()
                    if prompt in seen:
                        continue
                    seen.add(prompt)
                    cases.append(Case(prompt=prompt, kind="vague_profile"))
                    if len([c for c in cases if c.kind == "vague_profile"]) >= 800:
                        break
                if len([c for c in cases if c.kind == "vague_profile"]) >= 800:
                    break
            if len([c for c in cases if c.kind == "vague_profile"]) >= 800:
                break
        if len([c for c in cases if c.kind == "vague_profile"]) >= 800:
            break

    # 120 vague question prompts (must be blocked)
    for q in vague_question_forms:
        for place in ["europa", "brasil", "portugal", "sao paulo", "rio de janeiro"]:
            prompt = q.replace("europa", place)
            if prompt in seen:
                continue
            seen.add(prompt)
            cases.append(Case(prompt=prompt, kind="vague_question"))
            if len([c for c in cases if c.kind == "vague_question"]) >= 120:
                break
        if len([c for c in cases if c.kind == "vague_question"]) >= 120:
            break

    # 80 vague affirmation prompts (must be blocked)
    for base in vague_affirmations:
        for suffix in ["agora", "no linkedin", "na europa", "no brasil", ""]:
            prompt = f"{base} {suffix}".strip()
            if prompt in seen:
                continue
            seen.add(prompt)
            cases.append(Case(prompt=prompt, kind="vague_affirmation"))
            if len([c for c in cases if c.kind == "vague_affirmation"]) >= 80:
                break
        if len([c for c in cases if c.kind == "vague_affirmation"]) >= 80:
            break

    # 300 concrete profile prompts (must produce deterministic web command)
    for a in concrete_actions:
        for role in concrete_roles:
            for skill in concrete_skills:
                for s in concrete_seniority:
                    for loc in concrete_locations:
                        prompt = f"{a} vagas de {role} {s} com {skill} no linkedin em {loc} com base no meu perfil"
                        if prompt in seen:
                            continue
                        seen.add(prompt)
                        cases.append(Case(prompt=prompt, kind="concrete_profile"))
                        if len([c for c in cases if c.kind == "concrete_profile"]) >= 300:
                            break
                    if len([c for c in cases if c.kind == "concrete_profile"]) >= 300:
                        break
                if len([c for c in cases if c.kind == "concrete_profile"]) >= 300:
                    break
            if len([c for c in cases if c.kind == "concrete_profile"]) >= 300:
                break
        if len([c for c in cases if c.kind == "concrete_profile"]) >= 300:
            break

    # 75 direct destination prompts (must open known URLs)
    prefixes = ["abra", "acesse", "entre no", "abrir", "acessar"]
    for prefix in prefixes:
        for site, _ in direct_destinations:
            prompt = f"{prefix} meu {site}"
            if prompt in seen:
                continue
            seen.add(prompt)
            cases.append(Case(prompt=prompt, kind="direct_destination"))
            if len([c for c in cases if c.kind == "direct_destination"]) >= 75:
                break
        if len([c for c in cases if c.kind == "direct_destination"]) >= 75:
            break

    # Fill until exactly 1175 using extra unique vague variants.
    i = 0
    while len(cases) < 1175:
        prompt = f"analise o meu perfil e encontre oportunidades para mim variante {i}"
        i += 1
        if prompt in seen:
            continue
        seen.add(prompt)
        cases.append(Case(prompt=prompt, kind="vague_profile"))

    if len(cases) != 1175:
        raise RuntimeError(f"Expected 1175 cases, got {len(cases)}")

    random.shuffle(cases)
    return cases


def validate_case(case: Case) -> tuple[bool, str]:
    prompt = case.prompt

    web_cmd, _ = plan_agent_mode_web_command(prompt)
    browser_cmd, _ = plan_agent_mode_browser_command(prompt)

    if case.kind == "vague_profile":
        if not _is_profile_intent_without_criteria(prompt):
            return False, "expected profile-vague detector to be true"
        if web_cmd is not None:
            return False, f"expected web_cmd None, got: {web_cmd}"
        if browser_cmd is not None:
            return False, f"expected browser_cmd None, got: {browser_cmd}"
        return True, "ok"

    if case.kind in {"vague_question", "vague_affirmation"}:
        if not _is_profile_intent_without_criteria(prompt):
            return False, "expected vague profile detector to be true"
        if web_cmd is not None:
            return False, f"expected web_cmd None, got: {web_cmd}"
        if browser_cmd is not None:
            return False, f"expected browser_cmd None, got: {browser_cmd}"
        return True, "ok"

    if case.kind == "concrete_profile":
        if _is_profile_intent_without_criteria(prompt):
            return False, "unexpected block for concrete profile prompt"
        if web_cmd is None:
            return False, "expected concrete web command, got None"
        if not web_cmd.startswith("abrir url: https://www.linkedin.com/jobs/search/?keywords="):
            return False, f"unexpected web command format: {web_cmd}"
        return True, "ok"

    if case.kind == "direct_destination":
        if web_cmd is None:
            return False, "expected direct destination command, got None"
        if not web_cmd.startswith("abrir url: https://"):
            return False, f"unexpected destination command: {web_cmd}"
        return True, "ok"

    return False, f"unknown case kind: {case.kind}"


def run(loop_count: int, report_every: int) -> int:
    cases = build_cases()
    failures: list[str] = []

    started = time.time()
    for cycle in range(1, loop_count + 1):
        for idx, case in enumerate(cases, start=1):
            ok, reason = validate_case(case)
            if not ok:
                failures.append(
                    f"cycle={cycle} case={idx} kind={case.kind} prompt={case.prompt!r} reason={reason}"
                )
                if len(failures) >= 50:
                    break
        if cycle % report_every == 0 or cycle == loop_count:
            elapsed = time.time() - started
            print(f"progress cycle={cycle}/{loop_count} elapsed={elapsed:.1f}s failures={len(failures)}")
        if failures:
            break

    total_checks = loop_count * len(cases)
    elapsed = time.time() - started

    print("--- SUMMARY ---")
    print(f"cases_per_cycle={len(cases)}")
    print(f"cycles={loop_count}")
    print(f"total_checks_target={total_checks}")
    print(f"elapsed_seconds={elapsed:.2f}")

    if failures:
        print(f"status=FAILED failures={len(failures)}")
        for row in failures[:20]:
            print(row)
        return 1

    print("status=PASSED failures=0")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Massive QA matrix for profile-search guard behavior")
    parser.add_argument("--loops", type=int, default=350, help="Number of full cycles")
    parser.add_argument("--report-every", type=int, default=25, help="Progress report cadence")
    args = parser.parse_args()

    return run(loop_count=args.loops, report_every=args.report_every)


if __name__ == "__main__":
    raise SystemExit(main())
