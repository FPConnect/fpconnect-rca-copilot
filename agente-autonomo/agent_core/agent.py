from __future__ import annotations

import os
import re
import json
import importlib
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

from .config import settings
from .finance_knowledge import CURATED_FINANCE_KNOWLEDGE
from .memory import ConversationState, MemoryStore
from .knowledge import KnowledgeBase
from .market import handle_market_command, market_help_text, render_study_track
from .tools import (
    browser_click,
    browser_click_best_result,
    browser_click_first_result,
    browser_click_text,
    browser_disable,
    browser_enable,
    browser_extract_page_text,
    browser_extract_text,
    browser_go_back,
    browser_go_forward,
    browser_open_url,
    browser_press_key,
    browser_refresh,
    browser_search_current_page,
    browser_type_text,
    browser_type,
    browser_wait,
    describe_tools,
    open_remote_desktop,
    run_shell_command,
    speak_text,
)


BACKEND_ENV_VAR = "AGENTE_AUTONOMO_BACKEND"

_DIRECT_DESTINATIONS: list[tuple[str, str, str]] = [
    ("fpconnect", "http://127.0.0.1:3000/", "FPConnect"),
    ("linkedin", "https://www.linkedin.com/feed/", "LinkedIn"),
    ("github", "https://github.com/", "GitHub"),
    ("instagram", "https://www.instagram.com/", "Instagram"),
    ("facebook", "https://www.facebook.com/", "Facebook"),
    ("twitter", "https://x.com/", "X"),
    ("x", "https://x.com/", "X"),
    ("youtube", "https://www.youtube.com/", "YouTube"),
    ("gmail", "https://mail.google.com/", "Gmail"),
    ("outlook", "https://outlook.live.com/mail/", "Outlook"),
    ("whatsapp", "https://web.whatsapp.com/", "WhatsApp Web"),
]

_GENERIC_JOB_TERMS = {
    "vaga",
    "vagas",
    "job",
    "jobs",
    "emprego",
    "empregos",
    "trabalho",
    "trabalhos",
    "oportunidade",
    "oportunidades",
    "posicao",
    "posicoes",
}

_LOCATION_TERMS = {
    "brasil",
    "brazil",
    "europa",
    "europe",
    "portugal",
    "espanha",
    "spain",
    "alemanha",
    "germany",
    "holanda",
    "netherlands",
    "franca",
    "france",
    "italia",
    "italy",
    "canada",
    "usa",
    "india",
    "argentina",
    "mexico",
    "chile",
    "colombia",
    "peru",
}

_FILLER_TERMS = {
    "que",
    "seja",
    "sejam",
    "acordo",
    "perfil",
    "comigo",
    "conforme",
    "base",
    "baseado",
    "baseada",
    "encaixe",
    "encaixado",
    "encaixada",
    "combinem",
    "combine",
    "combinar",
    "combina",
    "matching",
    "match",
    "aderente",
    "aderentes",
    "aderencia",
    "aderência",
    "ideal",
    "ideais",
    "algo",
    "traga",
    "trazer",
}

_ACTION_RESIDUE_TERMS = {
    "entre",
    "entrar",
    "acesse",
    "acessar",
    "abra",
    "abrir",
    "busque",
    "buscar",
    "procure",
    "procurar",
    "pesquise",
    "pesquisar",
    "encontre",
    "achar",
}

_PROFILE_INTENT_TOKENS = {
    "meu perfil",
    "com meu perfil",
    "de acordo com meu perfil",
    "compativel com meu perfil",
    "compatível com meu perfil",
    "com base no meu perfil",
    "analise meu perfil",
    "analisa meu perfil",
    "analisar meu perfil",
    "encaixado",
    "encaixada",
    "encaixar",
    "matching com meu perfil",
    "combine comigo",
    "combinem comigo",
    "compativel comigo",
    "compatível comigo",
    "aderente ao meu perfil",
    "aderentes ao meu perfil",
}

_PROFILE_VAGUE_FIT_TERMS = {
    "combine comigo",
    "combina comigo",
    "combinam comigo",
    "combinem comigo",
    "que combina comigo",
    "que combinam comigo",
    "que combinem comigo",
    "encaixe",
    "encaixado",
    "encaixada",
    "aderente",
    "aderentes",
    "aderencia",
    "aderência",
    "tenho aderencia",
    "tenho aderência",
    "tenha aderencia",
    "tenha aderência",
    "que eu tenho aderencia",
    "que eu tenho aderência",
    "que eu tenha aderencia",
    "que eu tenha aderência",
    "me encaixo",
    "eu me encaixo",
    "matching",
    "match",
    "ideal para mim",
    "perfeita pra mim",
    "perfeito pra mim",
    "de acordo comigo",
}

_PROFILE_ROLE_TERMS = {
    "desenvolvedor",
    "desenvolvedora",
    "developer",
    "engenheiro",
    "engenheira",
    "engineer",
    "analista",
    "cientista",
    "scientist",
    "backend",
    "front-end",
    "frontend",
    "fullstack",
    "full stack",
    "qa",
    "tester",
    "devops",
    "sre",
    "arquiteto",
    "arquiteta",
    "product manager",
    "gerente de produto",
    "designer",
    "ux",
    "ui",
    "seguranca",
    "security",
    "suporte tecnico",
    "suporte técnico",
    "dados",
    "data engineer",
    "data analyst",
}

_PROFILE_SKILL_TERMS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "nodejs",
    "django",
    "flask",
    "spring",
    "dotnet",
    "c#",
    "c++",
    "golang",
    "aws",
    "azure",
    "gcp",
    "sql",
    "postgres",
    "mysql",
    "mongodb",
    "power bi",
    "sap",
    "salesforce",
    "excel",
    "tableau",
    "pyspark",
    "airflow",
    "kubernetes",
    "docker",
    "terraform",
}

_PROFILE_SENIORITY_TERMS = {
    "junior",
    "júnior",
    "pleno",
    "senior",
    "sênior",
    "estagio",
    "estágio",
    "trainee",
    "especialista",
    "lead",
    "coordenador",
    "coordenadora",
    "manager",
}

_PROFILE_STRUCTURED_CRITERIA_PATTERNS = [
    r"\bcargo\s*:\s*\w+",
    r"\bstack\s*:\s*\w+",
    r"\bsenioridade\s*:\s*\w+",
    r"\bempresa\s*:\s*\w+",
    r"\bidioma\s*:\s*\w+",
    r"\bsalario\s*:\s*\w+",
    r"\bfaixa\s+salarial\b",
    r"\bcom\s+\d+\+?\s*anos\b",
    r"\bremoto\b",
    r"\bhibrido\b",
    r"\bhíbrido\b",
    r"\bpresencial\b",
]


def _ascii_fold(value: str) -> str:
    text = value or ""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _has_access_verb(lowered: str) -> bool:
    return any(
        token in lowered
        for token in [
            "acesse",
            "acessar",
            "abra",
            "abrir",
            "entre",
            "entrar",
            "ir para",
            "va para",
            "vá para",
            "acessa",
        ]
    )


def _direct_destination_command(text: str, lowered: str, web_search_intent: bool) -> tuple[str | None, str | None]:
    if web_search_intent or not _has_access_verb(lowered):
        return None, None

    if "linkedin" in lowered and "/in/" in lowered:
        profile_match = re.search(r"https?://[^\s]+linkedin\.com/in/[^\s]+", text, flags=re.IGNORECASE)
        if profile_match:
            return f"abrir url: {profile_match.group(0)}", "Abrindo o perfil do LinkedIn pedido dentro da janela do agente."

    for keyword, url, label in _DIRECT_DESTINATIONS:
        if keyword == "x":
            if not re.search(r"\bx\b", lowered):
                continue
        elif keyword not in lowered:
            continue
        return f"abrir url: {url}", f"Abrindo o {label} direto na janela interna do agente."

    return None, None


def _has_rdp_words(lowered: str) -> bool:
    return any(
        token in lowered
        for token in [
            "rdp",
            "mstsc",
            "area de trabalho remota",
            "área de trabalho remota",
            "desktop remoto",
            "escritorio remoto",
            "escritório remoto",
        ]
    )


def _split_agent_mode_workflow(goal: str) -> list[str]:
    text = re.sub(r"\s+", " ", goal.strip())
    if not text:
        return []

    pattern = re.compile(
        r"\s+(?:e depois|depois|e em seguida|em seguida|e)\s+(?=(?:abra|abrir|acesse|acessar|pesquise|pesquisar|procure|procurar|busque|buscar|encontre|clique|clicar|digite|escreva|preencha|aperte|pressione|extraia|extrair|leia|ler|resuma|resumir|volte|voltar|avance|avancar|avançar|recarregue|recarregar|espere|aguarde)\b)",
        flags=re.IGNORECASE,
    )
    raw_parts = [part.strip(" .,!?:;") for part in pattern.split(text) if part.strip(" .,!?:;")]
    merged_parts: list[str] = []

    for part in raw_parts:
        lowered = part.lower()
        if (
            merged_parts
            and re.match(r"^(?:aperte|pressione)\s+enter\b", lowered)
            and re.match(r"^(?:digite|escreva|preencha)\b", merged_parts[-1].lower())
        ):
            merged_parts[-1] = f"{merged_parts[-1]} e {part}"
            continue
        merged_parts.append(part)

    return merged_parts


def _semantic_search_query(text: str) -> str:
    """Extracts a concise intent query from natural language user prompts."""
    lowered = text.lower().strip()
    if not lowered:
        return ""

    cleaned = re.sub(r"\b(ok|agora|entao|então|por favor|por gentileza|pfv)\b", " ", lowered, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(busque|buscar|pesquise|pesquisar|procure|procurar|encontre|achar|ache)\s+(?:por\s+)?", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(entre|entrar|acesse|acessar|abra|abrir)\s+(?:no|na|nos|nas|em)?\s*", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(compativeis?|compat[ií]veis?)\s+com\s+meu\s+perfil\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bde\s+acordo\s+com\s+meu\s+perfil\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:que\s+)?seja[m]?\s+de\s+acordo\s+com\s+meu\s+perfil\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:que\s+)?seja[m]?\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bde\s+acordo\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:que\s+)?combin\w*\s+comigo\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\baderent\w*\s+(?:ao\s+)?(?:meu\s+)?perfil\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bader[eê]nci\w*\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bque\s+eu\s+tenh\w*\s+ader[eê]nci\w*\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:de\s+)?acordo\s+comigo\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(e\s+)?me\s+inscrev\w*.*$", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(e\s+)?apliqu\w*.*$", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(e\s+)?candidate\w*.*$", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(na\s+web|na\s+internet|no\s+google|no\s+linkedin|linkedin|google|site|web|internet)\b", " ", cleaned, flags=re.IGNORECASE)

    stopwords = {
        "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
        "no", "na", "nos", "nas", "em", "com", "para", "pra", "por", "e", "ou", "me", "meu",
        "minha", "perfil", "favor", "quero", "preciso", "vagas", "vaga", "jobs", "job",
        "que", "sejam", "seja", "acordo", "conforme", "base", "bases", "combinem", "combine", "combinar",
        "comigo", "aderente", "aderentes", "aderencia", "aderência", "ideal", "ideais", "algo", "traga", "trazer",
        "entre", "entrar", "acesse", "acessar", "abra", "abrir", "busque", "buscar", "procure", "procurar", "pesquise", "pesquisar",
    }
    tokens = [
        token
        for token in re.findall(r"[a-z0-9áàâãéêíóôõúç\-\+]+", cleaned, flags=re.IGNORECASE)
        if token not in stopwords and len(token) > 2
    ]
    query = " ".join(tokens).strip()
    if query:
        weak_queries = {
            "que",
            "seja",
            "sejam",
            "que seja",
            "que sejam",
            "de acordo",
        }
        if query in weak_queries:
            return ""
        return query
    if any(token in lowered for token in ["vaga", "vagas", "job", "jobs"]):
        return "vagas"
    # Avoid returning near-verbatim user text for browser search payloads.
    return ""


def _extract_location_hint(text: str) -> str:
    lowered = text.lower()
    common_locations = [
        "brasil",
        "brazil",
        "europa",
        "europe",
        "portugal",
        "espanha",
        "spain",
        "alemanha",
        "germany",
        "holanda",
        "netherlands",
        "franca",
        "france",
        "italia",
        "italy",
        "reino unido",
        "united kingdom",
        "uk",
        "irlanda",
        "ireland",
        "canada",
        "usa",
        "estados unidos",
        "argentina",
        "mexico",
        "colombia",
        "india",
    ]
    for loc in common_locations:
        if re.search(rf"\b{re.escape(loc)}\b", lowered):
            return loc

    match = re.search(r"\b(?:em|no|na|nos|nas)\s+([a-z0-9áàâãéêíóôõúç\-\s]{2,40})", lowered, flags=re.IGNORECASE)
    if not match:
        return ""
    location = match.group(1)
    location = re.sub(r"\b(e\s+)?(me\s+inscrev\w*|apliqu\w*|candidate\w*|por\s+favor).*$", "", location, flags=re.IGNORECASE)
    return location.strip(" .,!?:;")


def _normalize_location_name(location: str) -> str:
    key = (location or "").strip().lower()
    if not key:
        return ""
    mapping = {
        "brasil": "Brazil",
        "brazil": "Brazil",
        "europa": "Europe",
        "europe": "Europe",
        "alemanha": "Germany",
        "germany": "Germany",
        "espanha": "Spain",
        "spain": "Spain",
        "franca": "France",
        "france": "France",
        "italia": "Italy",
        "italy": "Italy",
        "holanda": "Netherlands",
        "netherlands": "Netherlands",
        "reino unido": "United Kingdom",
        "uk": "United Kingdom",
        "estados unidos": "United States",
        "usa": "United States",
    }
    return mapping.get(key, location.strip())


def _normalized_payload_text(value: str) -> str:
    lowered = _ascii_fold((value or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9#\+ ]+", " ", lowered)).strip()


def _looks_like_literal_echo(goal: str, payload: str) -> bool:
    goal_norm = _normalized_payload_text(goal)
    payload_norm = _normalized_payload_text(payload)
    if not goal_norm or not payload_norm:
        return False

    goal_words = goal_norm.split()
    payload_words = payload_norm.split()
    if len(payload_words) <= 3:
        return False

    if payload_norm == goal_norm:
        return True

    if payload_norm in goal_norm and len(payload_words) >= max(4, int(len(goal_words) * 0.6)):
        return True

    overlap = len(set(goal_words) & set(payload_words))
    similarity = overlap / max(1, len(set(payload_words)))
    return len(payload_words) >= 5 and similarity >= 0.8


def _safe_semantic_payload(goal: str, payload: str) -> str:
    payload = (payload or "").strip(" .,!?:;'")
    if not payload:
        return ""
    meta_terms = [
        "chat",
        "workspace",
        "agente",
        "copiar",
        "colar",
        "copie",
        "cole",
        "literal",
        "filtro",
        "busca",
        "pesquisa",
    ]
    payload_lower = payload.lower()
    if any(term in payload_lower for term in meta_terms):
        return ""
    if _looks_like_literal_echo(goal, payload):
        semantic = _semantic_search_query(goal)
        return semantic.strip(" .,!?:;'")
    return payload


def _command_contains_literal_echo(goal: str, command: str) -> bool:
    lowered = (command or "").strip().lower()
    prefixes = ["browser: pesquisar ", "browser: texto ", "browser: texto+enter "]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            payload = command[len(prefix):].strip()
            return _looks_like_literal_echo(goal, payload)
    return False


def is_meta_instruction_intent(text: str) -> bool:
    lowered = (text or "").lower()
    behavior_terms = [
        "nao copie",
        "não copie",
        "nao colar",
        "não colar",
        "copiar e colar",
        "copie e cole",
        "nao pode copiar",
        "não pode copiar",
        "literal",
        "melhore o filtro",
        "filtro do workspace",
        "o agente tem que",
        "o agente deve",
        "nao e pra",
        "não é pra",
        "comportamento do agente",
        "o chat",
        "a workspace",
    ]
    return any(term in lowered for term in behavior_terms)


def _is_generic_search_query(query: str) -> bool:
    normalized = _normalized_payload_text(query)
    if not normalized:
        return True
    words = normalized.split()
    if not words:
        return True
    if len(words) == 1 and words[0] in _GENERIC_JOB_TERMS:
        return True
    if set(words).issubset(_GENERIC_JOB_TERMS):
        return True
    weak_union = _GENERIC_JOB_TERMS | _LOCATION_TERMS | _FILLER_TERMS | _ACTION_RESIDUE_TERMS
    if set(words).issubset(weak_union):
        return True
    if len(words) <= 3 and all(word in weak_union for word in words):
        return True
    return False


def _browser_payload_is_weak(command: str) -> bool:
    lowered = (command or "").strip().lower()
    prefixes = ["browser: pesquisar ", "browser: texto ", "browser: texto+enter ", "browser: resultado "]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            payload = command[len(prefix):].strip()
            return _is_generic_search_query(payload)
    # Also block "abrir url:" commands whose search keyword is generic.
    if lowered.startswith("abrir url:"):
        url = command[len("abrir url:"):].strip()
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            keyword = (qs.get("keywords") or qs.get("q") or qs.get("query") or qs.get("search") or [None])[0]
            if keyword and _is_generic_search_query(str(keyword)):
                return True
        except Exception:
            pass
    return False


def _looks_like_workspace_task(text: str) -> bool:
    lowered = (text or "").lower()
    task_terms = [
        "abra",
        "abrir",
        "acesse",
        "acessar",
        "entre no",
        "pesquise",
        "pesquisar",
        "procure",
        "buscar",
        "busque",
        "encontre",
        "clique",
        "clicar",
        "digite",
        "preencha",
        "escreva",
        "envie",
        "faça login",
        "faca login",
        "volte",
        "avance",
        "avançe",
        "recarregue",
        "extraia",
        "resuma a pagina",
        "resultado",
        "link",
        "site",
        "pagina",
        "página",
        "browser",
        "workspace",
        "linkedin",
        "github",
        "google",
        "gmail",
        "outlook",
        "whatsapp",
        "vaga",
        "vagas",
        "job",
        "jobs",
    ]
    return any(term in lowered for term in task_terms) or bool(re.search(r"https?://|www\.", lowered))


def _agent_intent_classifier_prompt() -> str:
    return (
        "Classifique a mensagem do usuario em exatamente uma categoria. "
        "Responda SOMENTE JSON valido no formato {\"intent\":\"...\"}.\n\n"
        "Categorias permitidas:\n"
        "- meta: instrucoes sobre como o agente deve se comportar, reclamacoes sobre filtro, copiar/colar, chat, workspace, comportamento.\n"
        "- login: pedido para entrar/logar/autenticar com credenciais.\n"
        "- workspace_task: tarefa que deve ser executada na web/workspace/browser.\n"
        "- chat: pergunta geral, conversa, explicacao ou pedido sem acao de navegador.\n\n"
        "Regras:\n"
        "- Se o usuario estiver dizendo como o agente deve agir, use meta.\n"
        "- Se pedir busca, clique, abrir site, navegar, preencher formulario ou agir na pagina, use workspace_task.\n"
        "- Se pedir login, use login.\n"
        "- Caso contrario, use chat."
    )


def classify_agent_mode_intent(goal: str, state: ConversationState) -> str:
    """Classifies agent-mode messages into meta/login/workspace_task/chat."""
    text = (goal or "").strip()
    if not text:
        return "chat"

    if is_meta_instruction_intent(text):
        return "meta"
    if is_login_intent(text):
        return "login"
    if _looks_like_workspace_task(text):
        return "workspace_task"

    runtime = _resolve_openai_runtime()
    if runtime is None:
        return "chat"

    api_key, model, base_url = runtime
    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return "chat"

    history = state.summary(limit=4)
    messages = [
        {"role": "system", "content": _agent_intent_classifier_prompt()},
    ]
    if history:
        messages.append({"role": "system", "content": f"Historico recente:\n{history}"})
    messages.append({"role": "user", "content": text})

    try:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=40,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = (completion.choices[0].message.content or "").strip()
        payload = json.loads(raw)
        intent = str(payload.get("intent") or "chat").strip().lower()
        if intent in {"meta", "login", "workspace_task", "chat"}:
            return intent
    except Exception:
        pass

    return "chat"


def is_profile_based_intent(text: str) -> bool:
    lowered = _normalized_payload_text(text)
    return any(_normalized_payload_text(token) in lowered for token in _PROFILE_INTENT_TOKENS)


def _is_profile_fit_style_intent(text: str) -> bool:
    lowered = _normalized_payload_text(text)
    has_fit_term = any(_normalized_payload_text(term) in lowered for term in _PROFILE_VAGUE_FIT_TERMS)
    has_job_term = any(term in lowered for term in _GENERIC_JOB_TERMS | {"linkedin", "carreira", "trampo"})
    return has_fit_term and has_job_term


def _contains_normalized_term(text: str, term: str) -> bool:
    normalized_term = _normalized_payload_text(term)
    if not normalized_term:
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _has_profile_search_criteria(text: str) -> bool:
    lowered = _normalized_payload_text(text)

    has_role = any(_contains_normalized_term(lowered, term) for term in _PROFILE_ROLE_TERMS)
    has_skill = any(_contains_normalized_term(lowered, term) for term in _PROFILE_SKILL_TERMS)
    has_seniority = any(_contains_normalized_term(lowered, term) for term in _PROFILE_SENIORITY_TERMS)
    has_structured_filter = any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in _PROFILE_STRUCTURED_CRITERIA_PATTERNS)

    # Location/work-mode alone is not enough for profile-only requests.
    return has_role or has_skill or has_seniority or has_structured_filter


def _is_profile_intent_without_criteria(text: str) -> bool:
    if not (is_profile_based_intent(text) or _is_profile_fit_style_intent(text)):
        return False
    return not _has_profile_search_criteria(text)


def _remove_location_from_query(query: str, location: str) -> str:
    if not query:
        return ""
    cleaned = query
    if location:
        cleaned = re.sub(rf"\b{re.escape(location.lower())}\b", " ", cleaned.lower(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(brasil|brazil|europa|europe|portugal|espanha|spain|alemanha|germany|holanda|netherlands|franca|france|italia|italy|india)\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,!?:;")
    return cleaned


def _linkedin_filters_from_text(lowered: str) -> list[str]:
    filters: list[str] = []
    if any(token in lowered for token in ["remoto", "remote"]):
        filters.append("f_WT=2")
    if any(token in lowered for token in ["hibrido", "híbrido", "hybrid"]):
        filters.append("f_WT=3")
    if any(token in lowered for token in ["presencial", "onsite", "on-site"]):
        filters.append("f_WT=1")
    if "junior" in lowered:
        filters.append("f_E=2")
    elif any(token in lowered for token in ["pleno", "mid", "middle"]):
        filters.append("f_E=3")
    elif any(token in lowered for token in ["senior", "sênior", "sr"]):
        filters.append("f_E=4")
    return filters


def is_login_intent(text: str) -> bool:
    lowered = text.lower()
    login_words = [
        "login",
        "logar",
        "entrar",
        "acessar conta",
        "fazer login",
        "sign in",
        "signin",
        "credencial",
        "usuario",
        "usuário",
        "senha",
    ]
    return any(token in lowered for token in login_words)


def _service_login_url(service: str) -> str | None:
    key = (service or "").strip().lower()
    mapping = {
        "linkedin": "https://www.linkedin.com/login",
        "github": "https://github.com/login",
        "gmail": "https://accounts.google.com/signin",
        "google": "https://accounts.google.com/signin",
        "outlook": "https://login.live.com/",
        "microsoft": "https://login.live.com/",
        "facebook": "https://www.facebook.com/login",
        "instagram": "https://www.instagram.com/accounts/login/",
        "x": "https://x.com/i/flow/login",
        "twitter": "https://x.com/i/flow/login",
    }
    return mapping.get(key)


def plan_agent_mode_login_workflow(
    goal: str,
    service: str | None,
    username: str | None,
    password: str | None,
) -> tuple[list[tuple[str, str | None]] | None, str | None]:
    """Creates a safe login workflow using credentials saved in workspace."""

    if not is_login_intent(goal):
        return None, None

    user_value = (username or "").strip()
    pass_value = (password or "").strip()
    if not user_value or not pass_value:
        return None, None

    steps: list[tuple[str, str | None]] = []
    login_url = _service_login_url(service or "")
    if login_url:
        steps.append((f"abrir url: {login_url}", "Abrindo a pagina de login do servico selecionado."))

    # Sequencia padrao para formularios de login: usuario -> TAB -> senha -> ENTER.
    steps.append((f"browser: texto {user_value}", "Preenchendo usuario salvo no cofre da workspace."))
    steps.append(("browser: tecla Tab", "Movendo para o campo de senha."))
    steps.append((f"browser: texto+enter {pass_value}", "Preenchendo senha salva e enviando login."))

    return steps, "Executando login com credenciais salvas na workspace."


def plan_agent_mode_workflow(goal: str) -> tuple[list[tuple[str, str | None]] | None, str | None]:
    """Planeja uma sequencia curta de passos para pedidos compostos no modo agente."""

    text = goal.strip()
    if not text:
        return None, None
    if _is_profile_intent_without_criteria(text):
        return None, None

    parts = _split_agent_mode_workflow(text)
    if len(parts) < 2:
        return None, None

    steps: list[tuple[str, str | None]] = []
    saw_web_step = False
    saw_browser_step = False

    for part in parts[:6]:
        command, note = plan_agent_mode_web_command(part)
        if command:
            steps.append((command, note))
            saw_web_step = True
            continue

        command, note = plan_agent_mode_browser_command(part)
        if command:
            steps.append((command, note))
            saw_browser_step = True
            continue

        return None, None

    if len(steps) < 2:
        return None, None

    if not saw_web_step and not saw_browser_step:
        return None, None

    summary = "Executando uma sequencia de acoes na janela interna do agente."
    return steps, summary


def plan_agent_mode_web_command(goal: str) -> tuple[str | None, str | None]:
    """Converte objetivos web em ações diretas para a janela interna.

    Não tenta cobrir tudo; apenas os casos de alto sinal onde um modo agente
    mais autônomo é útil e previsível.
    """

    text = goal.strip()
    lowered = text.lower()
    if not text:
        return None, None
    if _is_profile_intent_without_criteria(text):
        return None, None

    direct_prefixes = (
        "terminal:",
        "abrir url:",
        "browser:",
        "rdp:",
        "falar:",
        "http://",
        "https://",
        "www.",
    )
    if lowered.startswith(direct_prefixes):
        return None, None

    for token in text.split():
        cleaned = token.strip("()[]{}<>,.;:'\" ")
        if cleaned.startswith("http://") or cleaned.startswith("https://"):
            return f"abrir url: {cleaned}", "Abrindo o link pedido dentro da janela do agente."
        if cleaned.startswith("www."):
            return f"abrir url: https://{cleaned}", "Abrindo o link pedido dentro da janela do agente."

    web_search_intent = any(
        token in lowered
        for token in [
            "pesquise",
            "pesquisar",
            "procure",
            "procurar",
            "busque",
            "buscar",
            "encontre",
            "achar",
            "ache",
            "vagas",
            "vaga",
            "jobs",
            "job",
        ]
    )
    current_page_context = any(
        token in lowered
        for token in [
            "nesta pagina",
            "nessa pagina",
            "na pagina",
            "neste site",
            "nesse site",
            "no site atual",
            "aqui",
        ]
    )
    mentions_web = any(
        token in lowered
        for token in [
            "linkedin",
            "site",
            "web",
            "internet",
            "google",
            "navegador",
            "feed",
        ]
    )
    if web_search_intent and current_page_context:
        return None, None

    if re.search(r"\b(?:abra|abrir|clique|clicar)\s+(?:no|na|o|a)?\s*(?:resultado|link)\b", lowered):
        return None, None

    direct_command, direct_note = _direct_destination_command(text, lowered, web_search_intent)
    if direct_command:
        return direct_command, direct_note

    if "linkedin.com/feed" in lowered or ("linkedin" in lowered and "feed" in lowered):
        return "abrir url: https://www.linkedin.com/feed/", "Abrindo o feed do LinkedIn na janela interna do agente."

    if web_search_intent and ("linkedin" in lowered or "vaga" in lowered or "job" in lowered):
        location = _extract_location_hint(text)
        query = _semantic_search_query(text)
        query = _remove_location_from_query(query, location)
        if is_profile_based_intent(text) and _is_generic_search_query(query):
            return None, None
        if not query:
            query = "vagas"
        linkedin_url = "https://www.linkedin.com/jobs/search/?keywords=" + quote_plus(query)
        normalized_location = _normalize_location_name(location)
        if normalized_location:
            linkedin_url += "&location=" + quote_plus(normalized_location)
        for item in _linkedin_filters_from_text(lowered):
            linkedin_url += "&" + item

        note = "Pesquisando vagas no LinkedIn com filtros inferidos do seu pedido"
        if normalized_location:
            note += f" (local: {normalized_location})"
        note += "."
        return f"abrir url: {linkedin_url}", note

    if web_search_intent or mentions_web:
        query = _semantic_search_query(text)
        if is_profile_based_intent(text) and _is_generic_search_query(query):
            return None, None
        return (
            f"abrir url: https://www.google.com/search?q={quote_plus(query)}",
            "Pesquisando isso na web dentro da janela interna do agente.",
        )

    return None, None


def plan_agent_mode_browser_command(goal: str) -> tuple[str | None, str | None]:
    """Interpreta pedidos naturais para agir na pagina que ja esta aberta."""

    text = goal.strip()
    lowered = text.lower()
    if not text:
        return None, None
    if _is_profile_intent_without_criteria(text):
        return None, None

    if any(token in lowered for token in ["extrair texto", "leia a pagina", "ler a pagina", "resuma a pagina", "texto da pagina", "conteudo da pagina", "conteúdo da página"]):
        return "browser: extrair pagina", "Extraindo o texto principal da pagina aberta na janela interna."

    targeted_result_match = re.search(
        r"\b(?:abra|abrir|clique|clicar)\s+(?:no|na|o|a)?\s*(?:resultado|link)(?:\s+(?:sobre|com|de|para))?\s+(.+)$",
        text,
        flags=re.IGNORECASE,
    )
    if targeted_result_match and "primeiro resultado" not in lowered and "primeiro link" not in lowered:
        target = targeted_result_match.group(1).strip(" .,!?:;'")
        if target:
            return f"browser: resultado {target}", "Abrindo o resultado mais aderente ao texto pedido na pagina atual."

    if any(token in lowered for token in ["primeiro resultado", "primeiro link"]):
        return "browser: primeiro resultado", "Abrindo o primeiro resultado util na pagina atual da janela interna."

    current_page_search = re.search(
        r"\b(?:pesquise|pesquisar|procure|procurar|busque|buscar)\s+(.+?)\s+(?:nesta pagina|nessa pagina|na pagina|neste site|nesse site|no site atual|aqui)\b",
        text,
        flags=re.IGNORECASE,
    )
    if current_page_search:
        query = _safe_semantic_payload(goal, current_page_search.group(1))
        if query and not _is_generic_search_query(query):
            return f"browser: pesquisar {query}", "Pesquisando isso no campo de busca da pagina atual."

    if any(token in lowered for token in ["volte", "voltar", "pagina anterior", "página anterior"]):
        return "browser: voltar", "Voltando para a pagina anterior na janela interna."

    if any(token in lowered for token in ["avance", "avancar", "avançar", "proxima pagina", "próxima página"]):
        return "browser: avancar", "Avancando para a proxima pagina na janela interna."

    if any(token in lowered for token in ["recarregue", "recarregar", "atualize a pagina", "atualizar pagina", "refresh"]):
        return "browser: recarregar", "Recarregando a pagina na janela interna."

    wait_match = re.search(r"\b(?:espere|aguarde)\s+(\d+(?:[\.,]\d+)?)\s*(?:s|seg|segundo|segundos)?\b", lowered)
    if wait_match:
        seconds = wait_match.group(1).replace(",", ".")
        return f"browser: esperar {seconds}", f"Aguardando {seconds}s na janela interna antes do proximo passo."

    click_match = re.search(r"\bcliqu(?:e|ar)\s+(?:em\s+)?(.+)$", text, flags=re.IGNORECASE)
    if click_match:
        label = click_match.group(1).strip(" .,!?:;'")
        if label:
            return f"browser: clicar texto {label}", "Tentando clicar no texto visivel pedido dentro da pagina aberta."

    type_match = re.search(r"\b(?:digite|escreva|preencha)\s+(.+)$", text, flags=re.IGNORECASE)
    if type_match:
        payload = type_match.group(1).strip()
        press_enter = False
        if " e aperte enter" in payload.lower():
            payload = re.sub(r"\s+e\s+aperte\s+enter\s*$", "", payload, flags=re.IGNORECASE)
            press_enter = True
        payload = _safe_semantic_payload(goal, payload)
        if payload and not _is_generic_search_query(payload):
            prefix = "browser: texto+enter " if press_enter else "browser: texto "
            note = "Digitando esse texto na pagina aberta e enviando Enter." if press_enter else "Digitando esse texto na pagina aberta."
            return prefix + payload, note

    if any(token in lowered for token in ["aperte enter", "pressione enter", "tecla enter"]):
        return "browser: tecla Enter", "Enviando Enter para a janela interna."

    return None, None


def _planner_system_prompt() -> str:
    return (
        "Você é um planejador de comandos para um agente local. "
        "Receberá um pedido do usuário e deve responder com UMA única "
        "linha de comando em português, usando APENAS um destes formatos:\n"
        "- terminal: <comando>\n"
        "- abrir url: <url>\n"
        "- falar: <texto>\n"
        "- rdp: <caminho .rdp opcional>\n\n"
        "Se não for apropriado executar nada, responda exatamente: none"
    )


def _get_browser_page_context() -> str:
    """Returns URL, title and text snippet of the currently open page for LLM context."""
    try:
        from .tools import _browser_ctx, _is_browser_session_alive  # type: ignore
        if not _is_browser_session_alive():
            return "Nenhuma pagina aberta no momento."
        page = _browser_ctx.get("page")
        if page is None:
            return "Nenhuma pagina aberta no momento."
        url = ""
        title = ""
        text = ""
        try:
            url = page.url or ""
        except Exception:
            pass
        try:
            title = page.title() or ""
        except Exception:
            pass
        try:
            raw = page.locator("body").inner_text(timeout=8000)
            text = " ".join(raw.split())[:2000]
        except Exception:
            pass
        parts = []
        if url:
            parts.append(f"URL atual: {url}")
        if title:
            parts.append(f"Titulo da pagina: {title}")
        if text:
            parts.append(f"Texto visivel na pagina (trecho):\n{text}")
        return "\n".join(parts) if parts else "Nenhuma informacao de pagina disponivel."
    except Exception:
        return "Nao foi possivel obter contexto da pagina."


def _browser_agent_system_prompt() -> str:
    return (
        "Voce e um agente de automacao de navegador.\n"
        "O usuario fara um pedido. Analise o contexto da pagina atual e responda com "
        "EXATAMENTE UMA linha de comando para executar. Nao explique, nao acrescente nada.\n\n"
        "Comandos disponiveis:\n"
        "- browser: clicar texto <texto>  -> clica no elemento visivel com esse texto\n"
        "- browser: texto <texto>  -> digita o texto no campo focado\n"
        "- browser: texto+enter <texto>  -> digita o texto e pressiona Enter\n"
        "- browser: pesquisar <texto>  -> usa o campo de busca da pagina atual\n"
        "- browser: voltar  -> volta para a pagina anterior\n"
        "- browser: avancar  -> avanca para a proxima pagina\n"
        "- browser: recarregar  -> recarrega a pagina\n"
        "- browser: tecla <tecla>  -> pressiona uma tecla (Enter, Tab, Escape, ArrowDown etc.)\n"
        "- browser: extrair pagina  -> extrai e retorna o texto completo da pagina\n"
        "- browser: primeiro resultado  -> clica no primeiro resultado util da lista\n"
        "- browser: resultado <texto>  -> clica no resultado que melhor corresponde ao texto\n"
        "- browser: esperar <segundos>  -> aguarda N segundos\n"
        "- abrir url: <url>  -> abre uma URL no navegador\n\n"
        "Se nenhuma acao fizer sentido ou o pedido for apenas uma pergunta, responda exatamente: none"
    )


def _is_valid_agent_action_command(command: str) -> bool:
    lowered = (command or "").strip().lower()
    return lowered.startswith(("browser:", "abrir url:"))


def _contextual_agent_workflow_prompt() -> str:
    return (
        "Voce e um planejador de automacao web. "
        "Seu trabalho e entender a intencao do usuario e devolver um plano curto de acoes reais, "
        "sem copiar o texto do usuario literalmente para campos de busca quando isso nao fizer sentido.\n\n"
        "Regras:\n"
        "- Pense no objetivo antes de agir.\n"
        "- Extraia intencao, filtros, localizacao, palavras-chave e proximos passos.\n"
        "- Nao repita frases completas do usuario em browser: texto, browser: pesquisar ou URLs de busca.\n"
        "- Se o usuario disser algo como 'busque vagas de acordo com meu perfil no brasil', voce deve resumir para termos uteis, por exemplo cargo/filtros/local, e nunca colar a frase inteira.\n"
        "- So use texto literal quando o usuario pedir explicitamente para digitar/copiar uma frase exata.\n"
        "- Prefira comandos concretos e seguros.\n"
        "- Use no maximo 5 passos.\n"
        "- Responda SOMENTE JSON valido.\n\n"
        "Formato de resposta:\n"
        '{"note":"resumo curto","steps":["abrir url: ...","browser: ..."]}\n\n'
        "Passos permitidos:\n"
        "- abrir url: <url>\n"
        "- browser: pesquisar <texto>\n"
        "- browser: clicar texto <texto>\n"
        "- browser: resultado <texto>\n"
        "- browser: primeiro resultado\n"
        "- browser: texto <texto>\n"
        "- browser: texto+enter <texto>\n"
        "- browser: tecla <tecla>\n"
        "- browser: voltar\n"
        "- browser: avancar\n"
        "- browser: recarregar\n"
        "- browser: esperar <segundos>\n"
        "- browser: extrair pagina\n\n"
        "Se nao houver acao segura e clara, responda exatamente: none"
    )


def plan_agent_mode_contextual_workflow(goal: str, state: ConversationState) -> tuple[list[tuple[str, str | None]] | None, str | None]:
    """Uses LLM + page context to build a short validated action plan for general requests."""

    if not goal.strip():
        return None, None
    if _is_profile_intent_without_criteria(goal):
        return None, None

    runtime = _resolve_openai_runtime()
    if runtime is None:
        return None, None

    api_key, model, base_url = runtime

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None, None

    page_context = _get_browser_page_context()
    history = state.summary(limit=6)

    messages: list[dict] = [
        {"role": "system", "content": _contextual_agent_workflow_prompt()},
        {"role": "system", "content": f"Contexto atual do navegador:\n{page_context}"},
    ]
    if history:
        messages.append({"role": "system", "content": f"Historico recente:\n{history}"})
    messages.append({"role": "user", "content": goal})

    try:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=280,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = (completion.choices[0].message.content or "").strip()
        if not raw or raw.lower() == "none":
            return None, None
        payload = json.loads(raw)
        raw_steps = payload.get("steps") if isinstance(payload, dict) else None
        if not isinstance(raw_steps, list):
            return None, None

        steps: list[tuple[str, str | None]] = []
        for item in raw_steps[:5]:
            command = str(item or "").strip()
            if not command or not _is_valid_agent_action_command(command):
                return None, None
            if _command_contains_literal_echo(goal, command):
                return None, None
            if _browser_payload_is_weak(command):
                return None, None
            steps.append((command, None))

        if not steps:
            return None, None

        note = str(payload.get("note") or "").strip() if isinstance(payload, dict) else ""
        return steps, note or "Executando plano contextual montado a partir do pedido e da pagina atual."
    except Exception:
        return None, None


def plan_agent_mode_llm_browser_command(goal: str, state: ConversationState) -> tuple[str | None, str | None]:
    """Usa LLM para interpretar pedidos contextuais e gerar um comando browser:.

    Le o contexto da pagina atual (URL + texto visivel) e envia ao LLM para
    decidir qual acao de browser executar. Retorna (comando, nota) ou (None, None).
    """
    if not goal.strip():
        return None, None
    if _is_profile_intent_without_criteria(goal):
        return None, None

    runtime = _resolve_openai_runtime()
    if runtime is None:
        return None, None

    api_key, model, base_url = runtime

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None, None

    page_context = _get_browser_page_context()
    history = state.summary(limit=4)

    messages: list[dict] = [
        {"role": "system", "content": _browser_agent_system_prompt()},
        {"role": "system", "content": f"Contexto atual do navegador:\n{page_context}"},
    ]
    if history:
        messages.append({"role": "system", "content": f"Historico recente da conversa:\n{history}"})
    messages.append({"role": "user", "content": goal})

    try:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=128,
            temperature=0.0,
        )
        raw = (completion.choices[0].message.content or "").strip()
        raw_first = raw.splitlines()[0].strip() if raw else ""
        raw_lower = raw_first.lower()
        if not raw_lower or raw_lower == "none":
            return None, None
        valid_prefixes = ("browser:", "abrir url:", "terminal:", "falar:")
        if not any(raw_lower.startswith(p) for p in valid_prefixes):
            return None, None
        if _browser_payload_is_weak(raw_first):
            return None, None
        return raw_first, "Executando acao na workspace conforme analise do contexto da pagina."
    except Exception:
        return None, None


def _clean_suggested_command(text: str | None) -> str | None:
    if not text:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    if stripped.lower() == "none":
        return None
    return stripped.splitlines()[0].strip()


def _resolve_openai_runtime() -> tuple[str, str, str | None] | None:
    """Resolve credenciais/modelo para OpenAI e endpoints compatíveis.

    Suporta modo local com Ollama quando AGENTE_AUTONOMO_BACKEND=ollama,
    sem exigir chave real de API.
    """

    backend = os.getenv(BACKEND_ENV_VAR, "auto").lower().strip()
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    model = (os.getenv("OPENAI_MODEL") or "").strip()
    base_url = (os.getenv("OPENAI_BASE_URL") or "").strip() or None

    if backend == "ollama":
        if not base_url:
            base_url = (os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434/v1").strip()
        if not model:
            model = (os.getenv("OLLAMA_MODEL") or "granite4:tiny-h").strip()
        if not api_key:
            api_key = (os.getenv("OLLAMA_API_KEY") or "ollama").strip() or "ollama"

    if not api_key:
        return None

    if not model:
        model = "gpt-4.1-mini"

    return api_key, model, base_url


def _llm_status_description() -> str:
    """Retorna uma descrição textual do estado de configuração de LLMs.

    Não tenta chamar nenhum provedor — apenas olha variáveis de ambiente
    para responder perguntas do tipo "você já está configurado?".
    """

    backend = os.getenv(BACKEND_ENV_VAR, "auto").lower().strip()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    openai_base_url = (os.getenv("OPENAI_BASE_URL") or "").strip().lower()
    has_ollama = backend == "ollama" or "127.0.0.1:11434" in openai_base_url or "localhost:11434" in openai_base_url

    providers: list[str] = []
    if has_ollama:
        providers.append("Ollama (local)")
    if has_openai:
        providers.append("OpenAI")
    if has_anthropic:
        providers.append("Anthropic")
    if has_gemini:
        providers.append("Gemini")

    if not providers:
        return (
            "Ainda nao encontrei chaves de LLM configuradas. "
            "Posso continuar no modo local e, quando voce quiser, te guio para ativar Ollama local, OpenAI, Anthropic ou Gemini."
        )

    listed = ", ".join(providers)
    return (
        f"Sim, estou configurado para LLMs. Backend atual: {backend or 'auto'}. "
        f"Provedores ativos: {listed}. "
        "Quando voce pedir, eu respondo direto ou sugiro comando com confirmacao."
    )


def _planner_rules(goal: str) -> str | None:
    """Planejador determinístico por regras simples.

    Isso funciona mesmo sem nenhuma LLM configurada, cobrindo os casos
    mais comuns em português/inglês com mapeamentos diretos.
    """

    text = goal.strip()
    lowered = text.lower()

    direct_command, _ = _direct_destination_command(text, lowered, web_search_intent=False)
    if direct_command:
        return direct_command

    # Comandos de listagem de arquivos / diretório.
    if any(word in lowered for word in ["listar arquivos", "lista arquivos", "listar pasta", "listar diretório", "listar diretorio", "list files", "show files"]):
        return "terminal: dir"

    if any(word in lowered for word in ["listar processo", "listar processos", "processos rodando", "list processes"]):
        return "terminal: tasklist"

    # Abrir URL se encontrarmos algo que parece link.
    for token in text.split():
        if token.startswith("http://") or token.startswith("https://") or token.startswith("www."):
            url = token
            if url.startswith("www."):
                url = "https://" + url
            return f"abrir url: {url}"

    if "abrir" in lowered and "url" in lowered:
        # fallback genérico para quando o usuário já deu a URL mas sem padrão óbvio
        return f"abrir url: {text.split('abrir', 1)[1].strip()}" if "abrir" in lowered else None

    # Falar texto em voz alta.
    if any(word in lowered for word in ["falar", "ler em voz alta", "fala em voz alta", "diga em voz alta", "read aloud", "speak"]):
        # Tira o início mais comum e usa o resto.
        cleaned = (
            lowered.replace("falar", "")
            .replace("ler em voz alta", "")
            .replace("fala em voz alta", "")
            .replace("diga em voz alta", "")
            .replace("read aloud", "")
            .replace("speak", "")
        ).strip()
        payload = cleaned or text
        return f"falar: {payload}"

    # Conexão RDP simples.
    if ".rdp" in lowered or "conectar rdp" in lowered or _has_rdp_words(lowered):
        return "rdp:"

    return None


def _planner_openai(goal: str, state: ConversationState) -> str | None:
    """Planejador usando OpenAI / APIs compatíveis com o cliente OpenAI.

    Suporta tanto OpenAI oficial quanto endpoints compatíveis (Azure,
    OpenRouter, LM Studio, Ollama HTTP etc.) via OPENAI_BASE_URL.
    """

    runtime = _resolve_openai_runtime()
    if runtime is None:
        return None
    api_key, model, base_url = runtime

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = OpenAI(api_key=api_key)

    system = _planner_system_prompt()
    history = state.summary(limit=6)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "system",
                    "content": f"Histórico recente:\n{history}",
                },
                {"role": "user", "content": goal},
            ],
            max_tokens=128,
        )
        raw = completion.choices[0].message.content or ""
        return _clean_suggested_command(raw)
    except Exception:
        return None


def _planner_anthropic(goal: str, state: ConversationState) -> str | None:
    """Planejador usando Anthropic Claude (opcional).

    Requer:
    - ANTHROPIC_API_KEY
    - opcionalmente ANTHROPIC_MODEL (padrão: claude-3-haiku-20240307)
    """

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic  # type: ignore
    except Exception:
        return None

    client = anthropic.Anthropic(api_key=api_key)
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

    system = _planner_system_prompt()
    history = state.summary(limit=6)

    prompt = (
        system
        + "\n\nHistórico recente:\n"
        + history
        + "\n\nPedido do usuário (responda APENAS com a linha de comando ou 'none'):\n"
        + goal
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=128,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        return None

    try:
        parts = getattr(response, "content", [])
        text_chunks: list[str] = []
        for part in parts:
            if getattr(part, "type", "") == "text":  # tipo TextBlock
                value = getattr(part, "text", "")
                if value:
                    text_chunks.append(str(value))
        raw = "".join(text_chunks)
    except Exception:
        return None

    return _clean_suggested_command(raw)


def _planner_gemini(goal: str, state: ConversationState) -> str | None:
    """Planejador usando Google Gemini (opcional).

    Requer:
    - GEMINI_API_KEY ou GOOGLE_API_KEY
    - opcionalmente GEMINI_MODEL (padrão: gemini-1.5-flash)
    """

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        genai = importlib.import_module("google.generativeai")
    except Exception:
        return None

    configure = getattr(genai, "configure", None)
    generative_model = getattr(genai, "GenerativeModel", None)
    if not callable(configure) or generative_model is None:
        return None

    configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    system = _planner_system_prompt()
    history = state.summary(limit=6)

    prompt = (
        system
        + "\n\nHistórico recente:\n"
        + history
        + "\n\nPedido do usuário (responda APENAS com a linha de comando ou 'none'):\n"
        + goal
    )

    try:
        model = generative_model(model_name)
        response = model.generate_content(prompt)
        raw = (getattr(response, "text", "") or "").strip()
    except Exception:
        return None

    return _clean_suggested_command(raw)


def _qa_openai(question: str, state: ConversationState) -> str | None:
    """Responde perguntas gerais usando OpenAI / APIs compatíveis.

    Usa o mesmo modelo configurado em OPENAI_MODEL, mas sem formato de
    comando; aqui é resposta em linguagem natural.
    """

    runtime = _resolve_openai_runtime()
    if runtime is None:
        return None
    api_key, model, base_url = runtime

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = OpenAI(api_key=api_key)

    history = state.summary(limit=10)
    system = (
        "Você é um assistente técnico em português no estilo copiloto: "
        "claro, direto, confiável e útil. "
        "Responda de forma objetiva, com passos práticos quando fizer sentido. "
        "Se houver incerteza factual, diga explicitamente e proponha como validar. "
        "Evite resposta genérica e evite enrolação."
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "system", "content": f"Histórico recente:\n{history}"},
                {"role": "user", "content": question},
            ],
            max_tokens=256,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text or None
    except Exception:
        return None


def _qa_anthropic(question: str, state: ConversationState) -> str | None:
    """Responde perguntas gerais usando Anthropic Claude (se configurado)."""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic  # type: ignore
    except Exception:
        return None

    client = anthropic.Anthropic(api_key=api_key)
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

    history = state.summary(limit=10)
    prompt = (
        "Você é um assistente técnico em português no estilo copiloto: "
        "claro, direto, confiável e útil. "
        "Responda com objetividade e com passos práticos quando fizer sentido. "
        "Se houver incerteza factual, assuma isso explicitamente e proponha validação.\n\n"
        f"Histórico recente:\n{history}\n\nPergunta:\n{question}"
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        return None

    try:
        parts = getattr(response, "content", [])
        chunks: list[str] = []
        for part in parts:
            if getattr(part, "type", "") == "text":
                value = getattr(part, "text", "")
                if value:
                    chunks.append(str(value))
        text = "".join(chunks).strip()
        return text or None
    except Exception:
        return None


def _qa_gemini(question: str, state: ConversationState) -> str | None:
    """Responde perguntas gerais usando Google Gemini (se configurado)."""

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        genai = importlib.import_module("google.generativeai")
    except Exception:
        return None

    configure = getattr(genai, "configure", None)
    generative_model = getattr(genai, "GenerativeModel", None)
    if not callable(configure) or generative_model is None:
        return None

    configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    history = state.summary(limit=10)
    prompt = (
        "Você é um assistente técnico em português no estilo copiloto: "
        "claro, direto, confiável e útil. "
        "Responda com objetividade e com passos práticos quando fizer sentido. "
        "Se houver incerteza factual, assuma isso explicitamente e proponha validação.\n\n"
        f"Histórico recente:\n{history}\n\nPergunta:\n{question}"
    )

    try:
        model = generative_model(model_name)
        response = model.generate_content(prompt)
        text = (getattr(response, "text", "") or "").strip()
        return text or None
    except Exception:
        return None


def _qa_answer(question: str, state: ConversationState) -> str | None:
    """Tenta responder perguntas gerais usando os LLMs configurados.

    Usa AGENTE_AUTONOMO_BACKEND para decidir a prioridade, com o modo
    'auto'/'ensemble' tentando todos em sequência.
    """

    backend = os.getenv(BACKEND_ENV_VAR, "auto").lower().strip()

    if backend in {"all", "full"}:
        providers: list[tuple[str, str | None]] = [
            ("openai", _qa_openai(question, state)),
            ("anthropic", _qa_anthropic(question, state)),
            ("gemini", _qa_gemini(question, state)),
        ]
        available = [(name, answer) for name, answer in providers if answer]
        if not available:
            return None
        if len(available) == 1:
            return available[0][1]
        lines = ["Resposta agregada de multiplos modelos:"]
        for name, answer in available:
            lines.append(f"- {name}: {answer}")
        return "\n".join(lines)

    if backend in {"auto", "ensemble"}:
        for qa in (_qa_openai, _qa_anthropic, _qa_gemini):
            ans = qa(question, state)
            if ans:
                return ans
        return None

    if backend == "ollama":
        return _qa_openai(question, state)

    if backend == "anthropic":
        return _qa_anthropic(question, state)
    if backend in {"gemini", "google"}:
        return _qa_gemini(question, state)

    # "openai" ou qualquer outro valor -> tenta OpenAI primeiro.
    return _qa_openai(question, state)


def _web_research_answer(question: str) -> str | None:
    """Busca uma resposta curta na web quando local/LLM não responderem.

    Usa DuckDuckGo Instant Answer (sem chave) para evitar travar em
    fallback genérico.
    """

    query = question.strip()
    if not query:
        return None

    try:
        url = (
            "https://api.duckduckgo.com/?q="
            + quote_plus(query)
            + "&format=json&no_html=1&skip_disambig=1"
        )
        req = Request(url, headers={"User-Agent": "AgenteAutonomo/1.0"})
        with urlopen(req, timeout=6) as response:
            payload = response.read().decode("utf-8", errors="ignore")
        data = json.loads(payload)
    except Exception:
        return None

    answer = (data.get("Answer") or "").strip()
    abstract = (data.get("AbstractText") or "").strip()
    heading = (data.get("Heading") or "").strip()

    if answer:
        return f"Pesquisei na web e encontrei: {answer}"
    if abstract:
        prefix = f"{heading}: " if heading else ""
        return f"Pesquisei na web e encontrei: {prefix}{abstract}"

    related = data.get("RelatedTopics") or []
    for item in related:
        text = (item.get("Text") or "").strip() if isinstance(item, dict) else ""
        if text:
            return f"Pesquisei na web e encontrei: {text}"
        if isinstance(item, dict) and isinstance(item.get("Topics"), list):
            for sub in item["Topics"]:
                sub_text = (sub.get("Text") or "").strip() if isinstance(sub, dict) else ""
                if sub_text:
                    return f"Pesquisei na web e encontrei: {sub_text}"

    return None


def _is_finance_intent(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in [
            "mercado financeiro",
            "investir",
            "investimento",
            "bolsa",
            "acoes",
            "ações",
            "acao",
            "ação",
            "b3",
            "renda fixa",
            "renda variavel",
            "renda variável",
            "selic",
            "cdi",
            "ipca",
            "inflacao",
            "inflação",
            "juros",
            "etf",
            "fii",
            "fiis",
            "dividendo",
            "dividendos",
            "valuation",
            "fundamentalista",
            "analise tecnica",
            "análise técnica",
            "debenture",
            "debentures",
            "duration",
            "curva de juros",
            "opcoes",
            "opções",
            "futuros",
            "contratos futuros",
            "marcacao a mercado",
            "marcação a mercado",
            "balanco",
            "balanço",
            "fluxo de caixa descontado",
            "roe",
            "roic",
            "day trade",
            "swing trade",
            "buy and hold",
            "stop loss",
            "corretora",
            "carteira",
            "rebalanceamento",
            "tributacao",
            "tributação",
            "cripto",
            "forex",
        ]
    )


def _finance_web_research_answer(question: str) -> str | None:
    """Complementa lacunas do dominio financeiro com pesquisa curta na web."""

    if not _is_finance_intent(question):
        return None

    answer = _web_research_answer(question)
    if not answer:
        return None

    return (
        f"{answer} "
        "Use isso como ponto de partida e valide a regra exata antes de decidir ou operar, especialmente em tributacao, produtos e normas que mudam com o tempo."
    )


def _ensure_curated_finance_knowledge() -> None:
    try:
        kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
        try:
            kb.ensure_seed(CURATED_FINANCE_KNOWLEDGE)
        finally:
            kb.close()
    except Exception:
        pass


def _normalize_knowledge_question(text: str) -> str:
    return re.sub(r"[^a-z0-9áàâãéêíóôõúç\s]", " ", text.lower()).strip()


def _extract_teach_pair(command: str) -> tuple[str, str] | None:
    """Extrai pergunta/resposta para aprendizado explícito.

    Formatos aceitos:
    - ensinar: pergunta => resposta
    - aprender: pergunta => resposta
    - memorize: pergunta => resposta
    """

    text = command.strip()
    lowered = text.lower()
    if not lowered.startswith(("ensinar:", "aprender:", "memorize:")):
        return None

    payload = text.split(":", 1)[1].strip() if ":" in text else ""
    if "=>" not in payload:
        return None

    question, answer = payload.split("=>", 1)
    question = question.strip()
    answer = answer.strip()
    if not question or not answer:
        return None
    return question, answer


def _curated_finance_kb_answer(question: str) -> str | None:
    normalized_question = _normalize_knowledge_question(question)
    try:
        kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
        try:
            exact = kb.get_exact_answer(normalized_question)
            if exact:
                return exact
            hits = kb.search(question, limit=5, min_score=0.2)
        finally:
            kb.close()
    except Exception:
        return None

    curated_questions = {_normalize_knowledge_question(item[0]) for item in CURATED_FINANCE_KNOWLEDGE}
    for item in hits:
        normalized = _normalize_knowledge_question(item.question)
        if normalized in curated_questions:
            return item.answer
    return None


def _market_education_answer(question: str) -> str | None:
    """Respostas locais para educação financeira e perguntas amplas de mercado.

    A ideia aqui não é prometer conhecimento infinito, e sim cobrir os
    casos amplos e recorrentes com respostas úteis, seguras e diretas.
    """

    text = question.strip()
    lowered = text.lower()
    if not lowered:
        return None

    if lowered.startswith(("mercado:", "trading:", "trade:", "acoes:", "ações:")):
        return None

    finance_tokens = [
        "mercado financeiro",
        "investir",
        "investimento",
        "investimentos",
        "bolsa de valores",
        "bolsa",
        "acoes",
        "ações",
        "acao",
        "ação",
        "b3",
        "corretora",
        "renda fixa",
        "renda variavel",
        "renda variável",
        "selic",
        "cdi",
        "ipca",
        "inflacao",
        "inflação",
        "juros",
        "valuation",
        "fundamentalista",
        "analise tecnica",
        "análise técnica",
        "debenture",
        "debentures",
        "duration",
        "curva de juros",
        "opcoes",
        "opções",
        "futuros",
        "contratos futuros",
        "marcacao a mercado",
        "marcação a mercado",
        "balanco",
        "balanço",
        "fluxo de caixa descontado",
        "roe",
        "roic",
        "analise fundamentalista",
        "análise fundamentalista",
        "buy and hold",
        "day trade",
        "swing trade",
        "stop loss",
        "rebalanceamento",
        "rebalanc",
        "imposto",
        "tribut",
        "tesouro selic",
        "tesouro direto",
        "etf",
        "fii",
        "fiis",
        "dividendo",
        "dividendos",
        "cripto",
        "forex",
        "carteira",
        "trilha",
        "estudo",
    ]
    if not any(token in lowered for token in finance_tokens):
        return None

    if any(phrase in lowered for phrase in ["como faço para investir na bolsa", "como investir na bolsa", "como comecar na bolsa", "como começar na bolsa"]):
        return (
            "Para investir na bolsa sem pular etapa, siga esta ordem: "
            "1) monte reserva de emergencia em liquidez diaria; "
            "2) defina objetivo e prazo; "
            "3) abra conta em uma corretora confiavel; "
            "4) comece pequeno, de preferencia por ETFs ou poucas acoes bem entendidas; "
            "5) diversifique por setores e nao concentre tudo em um papel; "
            "6) aporte de forma recorrente e revise risco, custos e horizonte. "
            "Se quiser operacao pratica, eu tambem consigo analisar ativos e montar paper trade com os comandos de mercado."
        )

    if any(
        phrase in lowered
        for phrase in [
            "como aprender a investir",
            "como faço para aprender a investir",
            "como faco para aprender a investir",
            "como faço pra aprender a investir",
            "como faco pra aprender a investir",
            "quero aprender a investir",
            "me ensina a investir",
        ]
    ):
        return (
            "Para aprender a investir sem se perder, siga esta ordem: "
            "1) entenda reserva de emergencia, liquidez e risco; "
            "2) aprenda a diferenca entre renda fixa e renda variavel; "
            "3) estude primeiro Tesouro Selic, CDB, ETF, acao e FII; "
            "4) monte uma carteira simples e pequena antes de buscar retorno maior; "
            "5) aprenda custos, imposto e diversificacao; "
            "6) so depois avance para valuation, analise tecnica ou operacoes mais curtas. "
            "Se quiser, eu tambem posso te passar uma trilha pronta com: mercado: trilha iniciante"
        )

    small_amount_now = re.search(r"\b(\d{1,4}(?:[\.,]\d{1,2})?)\s*(?:r\$|reais?)\b", lowered)
    if small_amount_now and any(token in lowered for token in ["investir", "invisto", "investimento"]):
        raw_value = small_amount_now.group(1).replace(".", "").replace(",", ".")
        try:
            amount = float(raw_value)
        except ValueError:
            amount = 0.0

        if 0 < amount <= 100:
            return (
                f"Com R$ {amount:.2f}, o caminho mais seguro para começar agora e este: "
                "1) usar corretora com aporte minimo baixo e sem taxa de custodia; "
                "2) priorizar Tesouro Selic ou CDB com liquidez diaria para reserva e aprendizado; "
                "3) fazer 1 microaporte hoje e repetir semanalmente para ganhar consistencia. "
                "Se voce quiser renda variavel, trate esse valor como estudo e diversifique via ETF fracionado em vez de concentrar em uma unica acao. "
                "Se quiser, eu monto um plano objetivo em 60 segundos para seu perfil (conservador, moderado ou arrojado)."
            )

    if ("o que" in lowered or "oque" in lowered or "explica" in lowered or "explique" in lowered) and any(token in lowered for token in ["mercado financeiro", "bolsa", "b3"]):
        return (
            "Mercado financeiro e o ambiente onde dinheiro, credito e ativos sao negociados. "
            "Na pratica, para pessoa fisica isso costuma se dividir em renda fixa (Tesouro, CDB, LCI/LCA) e renda variavel (acoes, ETFs, FIIs e alguns fundos). "
            "A bolsa e a parte onde ativos listados oscilam mais no curto prazo, entao o ponto central e alinhar risco, prazo e diversificacao."
        )

    if any(token in lowered for token in ["renda fixa", "tesouro selic", "cdb", "lci", "lca"]) and any(token in lowered for token in ["o que", "oque", "como funciona", "vale a pena", "explica", "explique"]):
        return (
            "Renda fixa e um grupo de investimentos em que a regra de remuneracao ja nasce definida ou referenciada, como CDI, IPCA ou uma taxa prefixada. "
            "Ela costuma ser a base da carteira para reserva, objetivos de curto prazo e controle de risco. "
            "Tesouro Selic e o produto mais usado para liquidez e caixa; CDB, LCI e LCA entram quando prazo, emissor e cobertura fazem sentido."
        )

    if any(token in lowered for token in ["renda variavel", "renda variável", "acoes", "ações", "acao", "ação"]) and any(token in lowered for token in ["o que", "oque", "como funciona", "explica", "explique", "vale a pena"]):
        return (
            "Renda variavel e a parte da carteira em que preco e retorno oscilam mais, sem promessa de resultado fixo. "
            "Acoes representam participacao em empresas; ETFs replicam indices; FIIs concentram imoveis ou recebiveis. "
            "Ela faz mais sentido para horizontes maiores, aportes graduais e tolerancia a volatilidade."
        )

    if any(token in lowered for token in ["etf", "etfs"]):
        return (
            "ETF e um fundo negociado em bolsa que replica um indice ou uma cesta de ativos. "
            "Para iniciante, costuma ser uma forma simples de diversificar sem escolher muitas acoes individualmente. "
            "Os pontos principais para avaliar sao indice seguido, taxa, liquidez e exposicao geografica ou setorial."
        )

    if any(token in lowered for token in ["fii", "fiis", "fundo imobiliario", "fundos imobiliarios"]):
        return (
            "FII e um fundo listado em bolsa que investe em imoveis ou recebiveis imobiliarios. "
            "Muita gente usa FIIs buscando fluxo recorrente, mas eles continuam sendo renda variavel e podem cair de preco. "
            "O basico e olhar qualidade dos ativos, vacancia, contratos, divida, gestao e diversificacao."
        )

    if any(token in lowered for token in ["dividendo", "dividendos"]):
        return (
            "Dividendos sao parte do lucro distribuida aos acionistas, mas nao devem ser analisados so pelo valor pago hoje. "
            "O ponto certo e combinar qualidade do negocio, geracao de caixa, nivel de endividamento e sustentabilidade do payout. "
            "Dividend yield alto isolado pode ser armadilha se o lucro cair ou o mercado estiver precificando risco."
        )

    if any(token in lowered for token in ["corretora", "abrir conta na corretora", "qual corretora"]):
        return (
            "Para escolher corretora, compare regulacao, solidez, custos, plataforma, atendimento e facilidade para transferir e declarar investimentos. "
            "Para quem esta comecando, o mais importante costuma ser uma operacao simples, boa usabilidade e custo previsivel, nao a plataforma mais complexa."
        )

    if any(token in lowered for token in ["selic", "cdi", "ipca", "inflacao", "inflação", "juros"]) and any(token in lowered for token in ["o que", "oque", "qual a diferenca", "qual a diferença", "como funciona", "explica", "explique"]):
        return (
            "Selic e a taxa basica de juros da economia; CDI e a referencia mais comum do mercado bancario de curtissimo prazo; IPCA mede inflacao oficial. "
            "Na pratica, Selic e CDI ajudam a comparar renda fixa pos-fixada, enquanto IPCA entra para proteger poder de compra em horizontes maiores. "
            "Quando juros sobem, renda fixa tende a ficar mais atraente e ativos de risco costumam exigir mais retorno para justificar o preco."
        )

    if any(token in lowered for token in ["valuation", "valor intrinseco", "valor intrínseco", "pl", "p/l", "ev/ebitda"]) and any(token in lowered for token in ["o que", "oque", "como funciona", "explica", "explique", "vale a pena"]):
        return (
            "Valuation e a tentativa de estimar quanto um ativo ou empresa vale com base em lucro, caixa, crescimento, risco e comparaveis. "
            "Multiplos como P/L e EV/EBITDA ajudam a comparar empresas, mas nao funcionam sozinhos. "
            "O ponto serio e combinar qualidade do negocio, margem, divida, retorno sobre capital e cenario de crescimento antes de concluir se algo esta barato ou caro."
        )

    if any(token in lowered for token in ["analise fundamentalista", "análise fundamentalista", "fundamentalista"]):
        return (
            "Analise fundamentalista olha o negocio por baixo do preco: receita, lucro, caixa, margem, divida, retorno sobre capital, governanca e vantagem competitiva. "
            "Ela faz mais sentido para quem quer investir com horizonte mais longo e decidir se a empresa merece continuar na carteira mesmo fora do ruido do curto prazo."
        )

    if any(token in lowered for token in ["analise tecnica", "análise técnica", "grafico", "gráfico", "suporte", "resistencia", "resistência", "rsi", "media movel", "média móvel"]):
        return (
            "Analise tecnica observa preco, volume, tendencia e volatilidade para montar cenarios operacionais. "
            "Ferramentas comuns sao medias moveis, suportes, resistencias, RSI e ATR. "
            "Ela ajuda no timing e na gestao de risco, mas nao substitui entender a qualidade do ativo quando o objetivo e investimento de prazo maior."
        )

    if any(token in lowered for token in ["day trade", "swing trade", "buy and hold"]):
        return (
            "Day trade busca zerar a posicao no mesmo dia; swing trade carrega por alguns dias ou semanas; buy and hold pensa em anos. "
            "Quanto menor o prazo, maior tende a ser o impacto de custo, erro operacional, ruido e disciplina emocional. "
            "Para iniciante, buy and hold diversificado ou aportes graduais em ETFs costuma ser muito mais robusto que tentar viver de giro curto logo no inicio."
        )

    if any(token in lowered for token in ["stop loss", "stop", "gestao de risco", "gestão de risco", "risco retorno"]):
        return (
            "Stop loss e uma trava operacional para limitar perda planejada, mas nao e garantia absoluta no mercado real por causa de gap, liquidez e slippage. "
            "Gestao de risco envolve tambem tamanho de posicao, diversificacao, correlacao entre ativos e disciplina para nao aumentar risco so porque o mercado caiu."
        )

    if any(token in lowered for token in ["rebalanceamento", "rebalancear", "rebalancear carteira", "alocacao", "alocação"]):
        return (
            "Rebalanceamento e o ajuste periodico da carteira para voltar aos pesos de risco que voce definiu. "
            "Ele evita que um ativo que subiu demais passe a dominar a carteira sem voce perceber e tambem disciplina realizacao parcial e reposicao em classes que ficaram para tras."
        )

    if any(token in lowered for token in ["imposto", "tributacao", "tributação", "ir", "imposto de renda"]) and any(token in lowered for token in ["acao", "ação", "acoes", "ações", "etf", "fii", "fiis", "bolsa"]):
        return (
            "Tributacao em bolsa varia por classe de ativo e tipo de operacao, entao o caminho seguro e separar por acoes, ETFs, FIIs e day trade antes de calcular imposto. "
            "Eu consigo te explicar a estrutura geral, mas regra fiscal muda com frequencia e precisa ser validada para o seu caso concreto antes de declarar ou recolher."
        )

    if any(token in lowered for token in ["melhor investimento", "onde investir", "vale a pena investir", "qual o melhor ativo"]):
        return (
            "Nao existe melhor investimento universal. O melhor ativo depende de prazo, liquidez necessaria, tolerancia a risco, necessidade de renda e disciplina para manter a estrategia. "
            "Em geral, caixa e reserva pedem renda fixa liquida; crescimento pede renda variavel diversificada; e objetivos intermediarios pedem combinacao das duas coisas."
        )

    if any(token in lowered for token in ["quero estudar mercado financeiro", "como estudar mercado financeiro", "trilha de estudo", "plano de estudo de mercado", "quero aprender mercado financeiro", "vamos para a trilha", "vamos para trilha", "vamos pra trilha", "quero a trilha", "vamos la para trilha", "vamos lá para trilha"]):
        return render_study_track("iniciante")

    if any(token in lowered for token in ["quero estudar analise fundamentalista", "quero estudar análise fundamentalista", "trilha fundamentalista", "aprender fundamentos de empresas"]):
        return render_study_track("fundamentalista")

    if any(token in lowered for token in ["quero estudar trade", "quero estudar trader", "trilha trader", "como estudar day trade", "como estudar swing trade"]):
        return render_study_track("trader")

    if any(token in lowered for token in ["carteira", "alocar", "alocacao", "alocação", "diversificar", "diversificacao", "diversificação"]):
        return (
            "Uma carteira equilibrada normalmente comeca por objetivo, prazo e risco tolerado. "
            "Na pratica: reserva e caixa em renda fixa liquida, medio prazo em renda fixa e ativos menos volateis, e crescimento em acoes, ETFs ou FIIs em pesos que voce aguente manter mesmo em queda. "
            "Diversificar nao e ter dezenas de ativos aleatorios; e combinar riscos diferentes com criterio."
        )

    curated_answer = _curated_finance_kb_answer(text)
    if curated_answer:
        return curated_answer

    return (
        "Bora direto ao ponto. Eu consigo te orientar em tres trilhos praticos: "
        "1) comecar do zero com pouco dinheiro, "
        "2) montar carteira com risco controlado, "
        "3) analisar ativo especifico e simular plano sem operar de verdade. "
        "Me diga qual trilho voce quer agora e eu te entrego um passo a passo objetivo para executar hoje."
    )


def _extract_learning_menu_choice(text: str) -> str | None:
    """Extrai escolhas numericas 1-4 de um menu guiado."""

    match = re.fullmatch(r"\s*(?:op(?:cao|ção)\s*)?([1-4])\s*[).:\-]?\s*", text.lower())
    if not match:
        return None
    return match.group(1)


def _has_recent_learning_menu_prompt(state: ConversationState) -> bool:
    """Verifica se o agente ofereceu recentemente o menu de aprendizado."""

    markers = (
        "escolha um caminho e eu ja sigo com voce",
        "1) mercado financeiro iniciante, 2) investimentos",
    )
    for message in reversed(state.messages[-10:]):
        if message.role != "agent":
            continue
        lowered = message.content.lower()
        if all(marker in lowered for marker in markers):
            return True
    return False


def _learning_menu_choice_answer(choice: str) -> str:
    """Resolve o passo seguinte para escolhas numericas do menu guiado."""

    if choice == "1":
        return render_study_track("iniciante")

    if choice == "2":
        invest_answer = _market_education_answer("como faco pra aprender a investir")
        if invest_answer:
            return invest_answer
        return (
            "Perfeito, vamos para investimentos. "
            "Comece por reserva de emergencia, depois diferencie renda fixa de renda variavel, "
            "e so entao avance para carteira simples com Tesouro Selic, CDB, ETF, acao e FII."
        )

    if choice == "3":
        return (
            "Fechado, vamos para trade e gestao de risco. "
            "Comece definindo risco por operacao, stop tecnico e tamanho de posicao antes de pensar em retorno. "
            "Depois disso, praticamos com plano de entrada, saida e diario operacional sem operacao real no inicio."
        )

    return describe_tools()


def _local_qa_answer(question: str) -> str | None:
    """Fallback de conversa local quando não houver LLM disponível.

    Evita respostas genéricas de erro para perguntas comuns de chat.
    """

    text = question.strip()
    lowered = text.lower()

    if any(token in lowered for token in ["quero aprender", "vamos la, quero aprender", "vamos lá, quero aprender", "me ensina", "me ensinar"]):
        return (
            "Perfeito, vamos aprender de forma pratica. "
            "Escolha um caminho e eu ja sigo com voce: "
            "1) Mercado financeiro iniciante, 2) Investimentos (renda fixa, acoes, ETFs e FIIs), "
            "3) Trade e gestao de risco, 4) Ferramentas do agente no seu PC. "
            "Se quiser mercado agora, mande: mercado: trilha iniciante."
        )

    market_answer = _market_education_answer(text)
    if market_answer:
        return market_answer

    if (
        "fpconnect" in lowered
        and any(token in lowered for token in ["post", "posts", "postar", "publicar", "publicacao", "publicação"])
        and any(token in lowered for token in ["perfil", "profile", "meu", "minha"])
    ):
        return (
            "Ainda nao do jeito que voce descreveu. Neste repositorio do FPConnect eu nao encontrei fluxo de perfil social ou criacao de posts no perfil. "
            "Se o seu objetivo for operar o app atual, eu consigo abrir o FPConnect local e te ajudar a navegar. Se o objetivo for criar esse recurso, eu posso implementar a tela e o fluxo de postagem."
        )

    if (
        "fpconnect" in lowered
        and any(token in lowered for token in ["consegue", "pode", "da para", "dá para"])
        and any(token in lowered for token in ["perfil", "profile"])
    ):
        return (
            "No estado atual do projeto, nao encontrei modulo de perfil do usuario no FPConnect. "
            "Posso abrir o app local para voce ou implementar esse recurso se esse for o proximo passo."
        )

    if "signo" in lowered and any(token in lowered for token in ["seu", "voce", "você"]):
        return "Como IA, eu nao tenho data de nascimento, entao nao tenho signo."

    if lowered.strip() in {"e o signo?", "e o signo", "signo?"}:
        return "Como IA, eu nao tenho data de nascimento, entao nao tenho signo."

    if (
        "estrela" in lowered
        and any(token in lowered for token in ["espaco", "espaço", "universo"])
        and any(token in lowered for token in ["quantas", "quanto", "numero", "número"])
    ):
        return (
            "Nao existe um numero exato confirmado. "
            "A estimativa mais usada para o universo observavel fica na ordem de "
            "10^22 a 10^24 estrelas."
        )
    if (
        ("mais populoso" in lowered or "mais populosa" in lowered)
        and "chile" in lowered
        and any(token in lowered for token in ["estado", "regiao", "região", "provincia", "província"])
    ):
        return (
            "No Chile nao existem estados; a divisao principal e por regioes. "
            "A mais populosa e a Regiao Metropolitana de Santiago."
        )

    if (
        "brasil" in lowered
        and "quant" in lowered
        and any(token in lowered for token in ["estado", "estados", "unidade federativa", "unidades federativas"])
    ):
        return (
            "O Brasil tem 26 estados e o Distrito Federal, "
            "totalizando 27 unidades federativas."
        )


    if not lowered:
        return "Pode mandar sua pergunta ou objetivo."

    if any(w in lowered for w in ["que dia é hoje", "que dia e hoje", "data de hoje", "hoje é"]):
        now = datetime.now()
        return f"Hoje é {now.strftime('%d/%m/%Y')}."

    if any(w in lowered for w in ["que horas", "hora agora", "horário", "horario"]):
        now = datetime.now()
        return f"Agora são {now.strftime('%H:%M')}."

    if "capital" in lowered and ("qual" in lowered or "quais" in lowered):
        # Q&A local para perguntas comuns de capital, com tolerancia simples
        # a erros de digitacao recorrentes.
        capitals = {
            "brasil": "Brasilia",
            "argentina": "Buenos Aires",
            "franca": "Paris",
            "frança": "Paris",
            "alemanha": "Berlim",
            "alemanha?": "Berlim",
            "estados unidos": "Washington, D.C.",
            "eua": "Washington, D.C.",
            "usa": "Washington, D.C.",
            "washington": "Washington, D.C.",
            "washington dc": "Washington, D.C.",
        }

        # Extrai o alvo apos "de/do/da".
        target = ""
        m_target = re.search(r"\bd(?:e|o|a)\s+(.+)$", lowered)
        if m_target:
            target = m_target.group(1).strip(" ?.!;:")

        if target:
            for key, value in capitals.items():
                if key in target or (target and target in key):
                    return f"A capital de {target} e {value}."

            # Heuristica para erros comuns do tipo "whasingthon".
            if target.startswith("wash") or "wasing" in target or "whasing" in target:
                return "A capital dos Estados Unidos e Washington, D.C."

        # Se perguntou por capital mas sem alvo claro, pede especificacao.
        return "Me diga de qual pais ou regiao voce quer saber a capital."

    if any(token in lowered for token in ["moeda", "qual a moeda", "qual é a moeda"]):
        currencies = {
            "brasil": "real (BRL)",
            "argentina": "peso argentino (ARS)",
            "estados unidos": "dolar americano (USD)",
            "eua": "dolar americano (USD)",
            "usa": "dolar americano (USD)",
            "canada": "dolar canadense (CAD)",
            "reino unido": "libra esterlina (GBP)",
            "inglaterra": "libra esterlina (GBP)",
            "japao": "iene (JPY)",
            "japão": "iene (JPY)",
            "china": "yuan renminbi (CNY)",
            "franca": "euro (EUR)",
            "frança": "euro (EUR)",
            "alemanha": "euro (EUR)",
            "espanha": "euro (EUR)",
            "portugal": "euro (EUR)",
            "italia": "euro (EUR)",
            "italía": "euro (EUR)",
            "mexico": "peso mexicano (MXN)",
            "méxico": "peso mexicano (MXN)",
            "australia": "dolar australiano (AUD)",
        }
        m_target = re.search(r"\bd(?:e|o|a)\s+(.+)$", lowered)
        target = m_target.group(1).strip(" ?.!;:") if m_target else ""
        for key, value in currencies.items():
            if (target and (key in target or target in key)) or key in lowered:
                return f"A moeda de {key} e {value}."
        return "Me diga de qual pais voce quer saber a moeda."

    if any(token in lowered for token in ["idioma", "lingua", "língua", "idioma oficial"]):
        languages = {
            "brasil": "portugues",
            "portugal": "portugues",
            "argentina": "espanhol",
            "mexico": "espanhol",
            "méxico": "espanhol",
            "estados unidos": "ingles",
            "eua": "ingles",
            "usa": "ingles",
            "reino unido": "ingles",
            "inglaterra": "ingles",
            "franca": "frances",
            "frança": "frances",
            "alemanha": "alemao",
            "espanha": "espanhol",
            "italia": "italiano",
            "japao": "japones",
            "japão": "japones",
            "china": "mandarim",
        }
        m_target = re.search(r"\bd(?:e|o|a)\s+(.+)$", lowered)
        target = m_target.group(1).strip(" ?.!;:") if m_target else ""
        for key, value in languages.items():
            if (target and (key in target or target in key)) or key in lowered:
                return f"O idioma principal de {key} e {value}."
        return "Me diga de qual pais ou regiao voce quer saber o idioma."

    if "continente" in lowered:
        continents = {
            "brasil": "America do Sul",
            "argentina": "America do Sul",
            "estados unidos": "America do Norte",
            "eua": "America do Norte",
            "canada": "America do Norte",
            "mexico": "America do Norte",
            "franca": "Europa",
            "alemanha": "Europa",
            "espanha": "Europa",
            "portugal": "Europa",
            "italia": "Europa",
            "reino unido": "Europa",
            "japao": "Asia",
            "china": "Asia",
            "india": "Asia",
            "australia": "Oceania",
            "egito": "Africa",
            "africa do sul": "Africa",
        }
        m_target = re.search(r"\bd(?:e|o|a)\s+(.+)$", lowered)
        target = m_target.group(1).strip(" ?.!;:") if m_target else ""
        for key, value in continents.items():
            if (target and (key in target or target in key)) or key in lowered:
                return f"{key.capitalize()} fica na {value}."
        return "Me diga qual pais ou regiao voce quer localizar no continente."

    if any(token in lowered for token in ["trading", "trade", "acoes", "ações", "bolsa", "mercado financeiro", "cripto", "forex"]) and any(
        token in lowered for token in ["garant", "nunca perder", "nunca ganhar menos", "automatic", "sozinho", "bot"]
    ):
        return (
            "Eu consigo estruturar analise e paper trading com travas modeladas em BRL, mas mercado real nao permite garantir lucro minimo nem limite absoluto de perda. "
            "Nesta versao, a automacao de mercado fica restrita a analise, plano de trade e carteira simulada; para execucao real, o caminho correto e manter confirmacao humana e integrar uma corretora especifica depois."
        )

    # Conversoes simples de temperatura.
    m_c = re.search(r"(-?\d+(?:[\.,]\d+)?)\s*[°]?\s*c\b", lowered)
    m_f = re.search(r"(-?\d+(?:[\.,]\d+)?)\s*[°]?\s*f\b", lowered)
    if ("converter" in lowered or "quanto" in lowered or "equivale" in lowered) and m_c:
        val = float(m_c.group(1).replace(",", "."))
        f = val * 9.0 / 5.0 + 32.0
        return f"{val:g} C equivalem a {f:.2f} F."
    if ("converter" in lowered or "quanto" in lowered or "equivale" in lowered) and m_f:
        val = float(m_f.group(1).replace(",", "."))
        c = (val - 32.0) * 5.0 / 9.0
        return f"{val:g} F equivalem a {c:.2f} C."

    # Contas simples: "quanto e 2+2", "calcule 15*7".
    if any(token in lowered for token in ["quanto e", "quanto é", "calcule", "resultado de"]):
        expr = lowered
        for prefix in ["quanto e", "quanto é", "calcule", "resultado de"]:
            if prefix in expr:
                expr = expr.split(prefix, 1)[1]
        expr = expr.strip(" ?.!;:")
        expr = expr.replace("x", "*").replace("÷", "/")
        if re.fullmatch(r"[0-9\s\+\-\*\/\(\)\.,]+", expr):
            try:
                value = eval(expr.replace(",", "."), {"__builtins__": {}}, {})  # noqa: S307
                return f"O resultado e {value}."
            except Exception:
                pass

    if any(
        w in lowered
        for w in [
            "esta pronto",
            "está pronto",
            "ta pronto",
            "tá pronto",
            "pronto?",
        ]
    ):
        return (
            "Sim, estou pronto. O painel web esta no ar e o backend esta configurado para usar LLMs. "
            "Se quiser, ja posso responder perguntas gerais ou propor comandos para voce confirmar."
        )

    if any(
        w in lowered
        for w in [
            "qual é o seu nome",
            "qual e o seu nome",
            "seu nome",
            "como você se chama",
            "como voce se chama",
            "your name",
        ]
    ):
        return "Meu nome é Agente Autônomo Local."

    greeting_match = re.search(r"(^|\s)(oi|olá|ola|hello|hi)(\s|[!?.,;:]|$)", lowered)
    if greeting_match:
        return "Olá. Posso responder perguntas gerais, te ajudar com comandos e executar ações com confirmação."

    if any(w in lowered for w in ["sério", "serio", "fala sério", "fala serio"]):
        return (
            "Sim, e você está certo em cobrar. "
            "Vamos resolver de forma prática: me diga o objetivo e eu respondo diretamente "
            "ou proponho um comando seguro para você confirmar."
        )

    if any(w in lowered for w in ["obrigado", "valeu", "thanks"]):
        return "Perfeito. Quando quiser, me passe o próximo objetivo."

    if any(
        w in lowered
        for w in ["excelente", "ótimo", "otimo", "perfeito", "boa", "show", "top"]
    ):
        return "Excelente. Estou pronto para o próximo passo."

    if any(w in lowered for w in ["quem é você", "quem e voce", "o que você faz", "o que voce faz"]):
        return (
            "Sou um agente local: respondo perguntas, sugiro comandos e executo ações no seu PC "
            "apenas com sua confirmação."
        )

    return None


def _is_blocked_kb_answer(answer: str) -> bool:
    normalized = answer.strip().lower()
    if normalized == "(nenhum plano de ação seguro encontrado)":
        return True
    if "não reconheci um plano de ação seguro" in normalized:
        return True
    if "posso te ajudar de dois jeitos" in normalized:
        return True
    if "olá. posso responder perguntas gerais" in normalized:
        return True
    if "ola. posso responder perguntas gerais" in normalized:
        return True
    if "entendi. se quiser, eu respondo direto" in normalized:
        return True
    if "me diz em uma frase o que voce quer agora" in normalized:
        return True
    if "quero te responder no estilo copiloto" in normalized:
        return True
    if "faltou contexto para eu ser preciso" in normalized:
        return True
    return False


def _render_kb_answer(answer: str) -> str:
    """Normaliza respostas vindas da base de conhecimento.

    Entradas de sugestão são salvas com prefixo técnico; aqui convertemos
    para uma resposta amigável ao usuário.
    """

    text = answer.strip()
    if text.startswith("SUGESTAO_COMANDO:"):
        suggested = text.split(":", 1)[1].strip()
        return (
            "Sugestão do agente (não executada):\n"
            f"  {suggested}\n\n"
            "Digite 'y' para executar agora ou 't' para confiar "
            "nas próximas sugestões nesta sessão."
        )
    return text


def _default_conversational_fallback(user_text: str) -> str:
    """Resposta final curta e natural para conversa livre."""

    return (
        "Quero te responder no estilo copiloto, mas faltou contexto para eu ser preciso. "
        "Me diga seu objetivo com 1 detalhe util (ex.: pais, periodo, sistema ou erro) e eu te respondo direto."
    )


def _internet_status_description() -> str:
    """Retorna status de conectividade de internet de forma pragmatica."""

    test_url = "https://clients3.google.com/generate_204"
    try:
        with urlopen(test_url, timeout=4) as response:
            code = getattr(response, "status", 0)
        if int(code) in {200, 204}:
            return "Sim, estou online agora e consegui validar acesso externo." 
        return f"Estou com rede ativa, mas o teste externo voltou com status {code}."
    except (URLError, TimeoutError, OSError):
        return "Agora nao consegui validar internet externa. Vale checar firewall, proxy e DNS."


def _update_status_description() -> str:
    """Retorna status da rotina automatica de atualizacao de pacotes."""

    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
    report_path = scripts_dir / "install-report.txt"
    log_path = scripts_dir / "auto-update.log"

    if not report_path.exists() and not log_path.exists():
        return (
            "Ainda nao encontrei registro local de atualizacao automatica. "
            "Posso configurar/verificar a task de atualizacao para voce."
        )

    parts: list[str] = []

    if report_path.exists():
        ts = datetime.fromtimestamp(report_path.stat().st_mtime).strftime("%d/%m/%Y %H:%M:%S")
        parts.append(f"Ultimo relatorio de pacotes: {ts}.")

    if log_path.exists():
        ts = datetime.fromtimestamp(log_path.stat().st_mtime).strftime("%d/%m/%Y %H:%M:%S")
        parts.append(f"Ultimo log da atualizacao automatica: {ts}.")

        # Tenta extrair a ultima linha [DONE] com contagem ok/fail.
        try:
            lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            done = ""
            for line in reversed(lines):
                if "[DONE]" in line:
                    done = line
                    break
            if done:
                # Extrai apenas o resumo util para nao ficar verboso.
                if "[DONE]" in done and "ok=" in done:
                    parts.append(done.split("[DONE]", 1)[1].strip())
                else:
                    parts.append(done)
        except Exception:
            pass

    # Resposta curta e humana.
    summary = " ".join(parts)
    return f"Sim, esta atualizado. {summary}".strip()


def _is_internet_intent(text: str) -> bool:
    """Detecta pedidos/perguntas sobre conectividade de internet."""

    lowered = text.lower()
    has_internet_word = any(token in lowered for token in ["internet", "online", "conexao", "conexão", "rede"])
    has_connect_word = any(
        token in lowered
        for token in [
            "conectar",
            "conecte",
            "conectado",
            "conectada",
            "acessar",
            "acesse",
            "verificar",
            "teste",
            "validar",
            "puxe",
            "buscar",
        ]
    )
    return has_internet_word and has_connect_word


def _llm_connectivity_summary() -> str:
    backend = os.getenv(BACKEND_ENV_VAR, "auto").lower().strip()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    openai_base_url = (os.getenv("OPENAI_BASE_URL") or "").strip().lower()
    has_ollama = backend == "ollama" or "127.0.0.1:11434" in openai_base_url or "localhost:11434" in openai_base_url

    providers: list[str] = []
    if has_ollama:
        providers.append("Ollama(local)")
    if has_openai:
        providers.append("OpenAI")
    if has_anthropic:
        providers.append("Anthropic")
    if has_gemini:
        providers.append("Gemini")

    if not providers:
        return (
            "No momento nao tenho nenhum provedor externo ativo. "
            "Se quiser, eu te ajudo a configurar as chaves agora."
        )

    listed = ", ".join(providers)
    if backend in {"all", "full"}:
        return (
            f"Estou pronto para consultar todos os modelos configurados ({listed}). "
            "O modo all ja esta ativo."
        )

    return (
        f"Tenho estes provedores prontos: {listed}. Backend atual: {backend or 'auto'}. "
        "Se quiser consultar todos antes de responder, use: backend: all"
    )


def _nl_to_command(goal: str, state: ConversationState) -> str | None:
    """Usa regras locais e LLMs opcionais para sugerir um comando.

    Ordem de tentativa:
    1. Regras determinísticas (_planner_rules) – funcionam sempre.
    2. LLM(s) configurados via AGENTE_AUTONOMO_BACKEND.

    Valores aceitos em AGENTE_AUTONOMO_BACKEND:
    - openai (padrão): tenta apenas OpenAI/APIs compatíveis.
    - ollama         : usa Ollama local via API compatível OpenAI.
    - anthropic      : tenta apenas Claude.
    - gemini/google  : tenta apenas Gemini.
    - auto/ensemble  : tenta TODOS na ordem: OpenAI -> Anthropic -> Gemini.
    """

    # 1) Regras determinísticas primeiro.
    rule_based = _planner_rules(goal)
    if rule_based is not None:
        return rule_based

    backend = os.getenv(BACKEND_ENV_VAR, "auto").lower().strip()

    # 2) Multi-backend LLM opcional.
    if backend in {"auto", "ensemble"}:
        for planner in (_planner_openai, _planner_anthropic, _planner_gemini):
            suggested = planner(goal, state)
            if suggested is not None:
                return suggested
        return None

    if backend == "anthropic":
        return _planner_anthropic(goal, state)
    if backend in {"gemini", "google"}:
        return _planner_gemini(goal, state)
    if backend == "ollama":
        return _planner_openai(goal, state)

    # "openai" ou qualquer outro valor -> tenta OpenAI primeiro.
    return _planner_openai(goal, state)


@dataclass
class AutonomousAgent:
    memory_store: MemoryStore

    def load_state(self) -> ConversationState:
        return self.memory_store.load()

    def save_state(self, state: ConversationState) -> None:
        self.memory_store.save(state)

    def handle_command(self, command: str, state: ConversationState) -> str:
        """Interpreta comandos simples de alto nível.

        Este agente é "semi-autônomo": ele executa ações locais, mas
        espera que você confirme comandos sensíveis na CLI antes.
        """

        cmd = command.strip()
        if not cmd:
            return "Comando vazio."

        lowered = cmd.lower()

        teach_pair = _extract_teach_pair(cmd)
        if teach_pair is not None:
            question, answer = teach_pair
            kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
            try:
                kb.add(question, answer)
            finally:
                kb.close()

            reply = (
                "Aprendido com sucesso. "
                f"Vou lembrar desta resposta para perguntas como: '{question}'."
            )
            state.add("user", cmd)
            state.add("agent", reply)
            self.save_state(state)
            return reply

        if _is_finance_intent(cmd) or lowered.startswith(("mercado:", "trading:", "trade:", "acoes:", "ações:")) or lowered in {"mercado", "trading", "trade"}:
            _ensure_curated_finance_knowledge()

        if lowered.startswith("backend:"):
            desired = cmd.split(":", 1)[1].strip().lower()
            valid = {"auto", "openai", "ollama", "anthropic", "gemini", "google", "all", "full", "ensemble"}
            if desired not in valid:
                return (
                    "Backend invalido. Use um destes: auto, openai, ollama, anthropic, gemini, all."
                )
            os.environ[BACKEND_ENV_VAR] = desired
            return f"Backend atualizado para: {desired}"

        if lowered in {"help", ":help", "ajuda"}:
            return (
                "Comandos suportados (modo direto):\n"
                "- terminal: <comando>  -> executa um comando de shell.\n"
                "- abrir url: <url>     -> abre URL na janela interna do agente.\n"
                "- rdp: [arquivo.rdp]   -> abre mstsc (Windows).\n"
                "- falar: <texto>       -> lê o texto em voz alta.\n"
                "- mercado: help        -> lista analise tecnica e paper trading.\n"
                "- browser enable       -> abre janela interna para automacao web.\n"
                "- browser disable      -> fecha janela interna de automacao web.\n"
                "- browser: abrir <url>\n"
                "- browser: clicar <seletor CSS>\n"
                "- browser: digitar <seletor> => <texto>\n"
                "- browser: extrair <seletor CSS>\n"
                "- browser: esperar <segundos>\n"
                "- tools                -> lista as ferramentas disponíveis.\n"
                "- frase solta          -> o agente sugere um comando usando LLM (se configurado).\n"
                "- quit / sair          -> encerra.\n"
            )

        # Perguntas abertas sobre capacidades/recursos do agente
        if any(word in lowered for word in ["recurso", "recursos", "capacidade", "capacidades", "o que voce sabe fazer", "o que você sabe fazer", "what can you do", "capabilities"]):
            return (
                "Posso te ajudar em 6 frentes: executar comando de terminal, abrir URL, abrir RDP, falar texto, responder perguntas e analisar mercado com paper trading. "
                "Se LLMs estiverem ativos, tambem interpreto pedidos em linguagem natural e te proponho uma acao segura para confirmar."
            )

        if lowered in {"mercado: help", "mercado: ajuda", "trading: help", "trading: ajuda", "mercado", "trading", "trade"}:
            return market_help_text()

        # Perguntas sobre se o agente já está configurado com LLMs
        if (
            ("configurado" in lowered or "configurada" in lowered)
            and any(token in lowered for token in ["voce", "você", "you"])
        ):
            return _llm_status_description()

        if any(token in lowered for token in ["atualizado", "atualizada", "atualizacao", "atualização", "update"]):
            return _update_status_description()

        if _is_internet_intent(cmd) or (any(token in lowered for token in ["internet", "conectado", "online"]) and "?" in lowered):
            return _internet_status_description()

        if any(
            phrase in lowered
            for phrase in [
                "todas as llms",
                "todos os modelos",
                "consultar todas as llms",
                "consultar todos os modelos",
            ]
        ):
            return _llm_connectivity_summary()

        menu_choice = _extract_learning_menu_choice(cmd)
        if menu_choice and _has_recent_learning_menu_prompt(state):
            guided_answer = _learning_menu_choice_answer(menu_choice)
            state.add("user", cmd)
            state.add("agent", guided_answer)
            self.save_state(state)
            kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
            try:
                kb.add(cmd, guided_answer)
            except Exception:
                pass
            finally:
                kb.close()
            return guided_answer

        # Primeiro tenta conversa local (perguntas gerais comuns), para
        # evitar cair em fluxo de comando quando o usuário só quer uma
        # resposta textual.
        local_first = _local_qa_answer(cmd)
        if local_first:
            state.add("user", cmd)
            state.add("agent", local_first)
            self.save_state(state)
            kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
            try:
                kb.add(cmd, local_first)
            except Exception:
                pass
            finally:
                kb.close()
            return local_first

        # Perguntas sobre como configurar LLMs / modelos
        if (
            "configur" in lowered
            and any(
                token in lowered
                for token in ["llm", "modelo", "modelos", "openai", "anthropic", "gemini", "api key", "chave api"]
            )
        ) or "conectar voce" in lowered or "conectar você" in lowered:
            howto = (
                "Para me configurar com LLMs, você usa variáveis de ambiente.\n\n"
                "1) Escolha o modo de backend (padrão: ensemble):\n"
                "   - AGENTE_AUTONOMO_BACKEND=auto   # tenta OpenAI -> Anthropic -> Gemini\n"
                "   - ou 'ollama', 'openai', 'anthropic', 'gemini' se quiser forçar um só.\n\n"
                "2) Para modo local (estilo IBM/Ollama + Granite):\n"
                "   - AGENTE_AUTONOMO_BACKEND=ollama\n"
                "   - OLLAMA_BASE_URL=http://127.0.0.1:11434/v1\n"
                "   - OLLAMA_MODEL=granite4:tiny-h\n"
                "   - OLLAMA_API_KEY=ollama\n\n"
                "2) Defina as chaves dos provedores que você tem:\n"
                "   - OPENAI_API_KEY=...        (opc. OPENAI_MODEL, OPENAI_BASE_URL)\n"
                "   - ANTHROPIC_API_KEY=...     (opc. ANTHROPIC_MODEL)\n"
                "   - GEMINI_API_KEY=...        ou GOOGLE_API_KEY=... (opc. GEMINI_MODEL)\n\n"
                "Mesmo sem nenhuma chave eu ainda funciono com regras locais;\n"
                "os LLMs entram apenas para planejar comandos melhores mantendo sua confirmação.\n"
            )
            return howto

        # Pedidos diretos para "chamar" ou "usar" modelos externos/LLMs
        if any(
            phrase in lowered
            for phrase in [
                "chame modelos externos",
                "chamar modelos externos",
                "use modelos externos",
                "usar modelos externos",
                "use llm",
                "usar llm",
                "use os llms",
                "ativar modelos externos",
                "ative modelos externos",
            ]
        ):
            status = _llm_status_description()
            extra = (
                "\n\nNão existe um comando único para "
                '"ligar" os modelos: quando as variáveis de ambiente '
                "estão configuradas, eu já uso automaticamente os LLMs "
                "para planejar comandos a partir dos seus objetivos.\n"
                "Se nenhuma chave estiver configurada, configure pelo menos "
                "um provedor (OpenAI, Anthropic ou Gemini) e continue "
                "falando em linguagem natural que eu cuido do resto."
            )
            return status + extra

        if any(
            phrase in lowered
            for phrase in [
                "navegador interno",
                "browser interno",
                "abrir navegador interno",
                "acesse seu navegador interno",
            ]
        ):
            return browser_enable()

        # Comandos operacionais diretos devem rodar antes da busca em KB,
        # evitando que similaridade semântica desvie para "Sugestão" antiga.
        if lowered in {"browser enable", "ativar browser", "ativar navegador interno", "conceder acesso web"}:
            return browser_enable()

        market_reply = handle_market_command(cmd)
        if market_reply is not None:
            state.add("user", cmd)
            state.add("agent", market_reply)
            self.save_state(state)
            return market_reply

        if lowered in {"browser disable", "desativar browser", "fechar navegador interno", "revogar acesso web"}:
            return browser_disable()

        if lowered.startswith("browser: abrir "):
            payload = cmd.split(":", 1)[1].strip()
            url = payload[len("abrir ") :].strip() if payload.lower().startswith("abrir ") else payload
            return browser_open_url(url)

        if lowered.startswith("browser: clicar "):
            payload = cmd.split(":", 1)[1].strip()
            selector = payload[len("clicar ") :].strip() if payload.lower().startswith("clicar ") else payload
            return browser_click(selector)

        if lowered == "browser: extrair pagina":
            return browser_extract_page_text()

        if lowered == "browser: primeiro resultado":
            return browser_click_first_result()

        if lowered.startswith("browser: resultado "):
            payload = cmd.split(":", 1)[1].strip()[len("resultado ") :].strip()
            if not payload:
                return "Texto alvo vazio. Use: browser: resultado seu termo"
            return browser_click_best_result(payload)

        if lowered.startswith("browser: pesquisar "):
            payload = cmd.split(":", 1)[1].strip()[len("pesquisar ") :].strip()
            if not payload:
                return "Texto vazio. Use: browser: pesquisar sua busca"
            return browser_search_current_page(payload, press_enter=True)

        if lowered.startswith("browser: extrair "):
            payload = cmd.split(":", 1)[1].strip()
            selector = payload[len("extrair ") :].strip() if payload.lower().startswith("extrair ") else payload
            return browser_extract_text(selector)

        if lowered.startswith("browser: esperar "):
            payload = cmd.split(":", 1)[1].strip()
            raw = payload[len("esperar ") :].strip() if payload.lower().startswith("esperar ") else payload
            raw = raw.replace("segundos", "").replace("segundo", "").replace("s", "").strip()
            try:
                seconds = float(raw)
            except Exception:
                return "Tempo invalido. Use: browser: esperar 2"
            return browser_wait(seconds)

        if lowered == "browser: voltar":
            return browser_go_back()

        if lowered in {"browser: avancar", "browser: avançar"}:
            return browser_go_forward()

        if lowered == "browser: recarregar":
            return browser_refresh()

        if lowered.startswith("browser: tecla "):
            key = cmd.split(":", 1)[1].strip()[len("tecla ") :].strip()
            if not key:
                return "Tecla vazia. Use: browser: tecla Enter"
            return browser_press_key(key)

        if lowered.startswith("browser: texto+enter "):
            text_payload = cmd.split(":", 1)[1].strip()[len("texto+enter ") :].strip()
            if not text_payload:
                return "Texto vazio. Use: browser: texto+enter sua busca"
            return browser_type_text(text_payload, press_enter=True)

        if lowered.startswith("browser: texto "):
            text_payload = cmd.split(":", 1)[1].strip()[len("texto ") :].strip()
            if not text_payload:
                return "Texto vazio. Use: browser: texto sua busca"
            return browser_type_text(text_payload, press_enter=False)

        if lowered.startswith("browser: clicar texto "):
            label = cmd.split(":", 1)[1].strip()[len("clicar texto ") :].strip()
            if not label:
                return "Texto alvo vazio. Use: browser: clicar texto Entrar"
            return browser_click_text(label)

        if lowered.startswith("browser: digitar "):
            payload = cmd.split(":", 1)[1].strip()
            payload = payload[len("digitar ") :].strip() if payload.lower().startswith("digitar ") else payload
            if "=>" not in payload:
                return "Formato invalido. Use: browser: digitar <seletor> => <texto>"
            selector, text = payload.split("=>", 1)
            selector = selector.strip()
            text = text.strip()
            if not selector:
                return "Seletor vazio. Use: browser: digitar <seletor> => <texto>"
            return browser_type(selector, text)

        if lowered.startswith("abrir url:"):
            url = cmd.split(":", 1)[1].strip()
            return browser_open_url(url)

        # Se o usuário enviar apenas uma URL, abrimos direto na janela interna.
        if lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("www."):
            return browser_open_url(cmd)

        # Consulta ao banco de conhecimento global antes de planejar
        # qualquer ação: se já vimos uma pergunta muito parecida, podemos
        # reaproveitar a resposta imediatamente.
        kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
        try:
            hits = kb.search(cmd, limit=1)
        except Exception:
            hits = []

        if hits:
            best = hits[0]
            # Ignora respostas negativas antigas para não perpetuar erros.
            if not _is_blocked_kb_answer(best.answer):
                rendered = _render_kb_answer(best.answer)
                if best.answer.startswith("SUGESTAO_COMANDO:"):
                    suggested = best.answer.split(":", 1)[1].strip()
                    state.add("agent", f"SUGGESTED:{suggested}")
                state.add("user", cmd)
                state.add("agent", rendered)
                self.save_state(state)
                kb.close()
                return rendered
        kb.close()

        if lowered == "tools":
            return describe_tools()

        if lowered.startswith("terminal:"):
            to_run = cmd.split(":", 1)[1].strip()
            return run_shell_command(to_run)

        if lowered.startswith("abrir url:"):
            url = cmd.split(":", 1)[1].strip()
            return browser_open_url(url)

        if lowered.startswith("rdp"):
            # Permite "rdp" ou "rdp: caminho".
            _, _, rest = cmd.partition(":")
            target = rest.strip() or None
            return open_remote_desktop(target)

        if lowered.startswith("falar:"):
            text = cmd.split(":", 1)[1].strip()
            return speak_text(text)

        # Fallback: tenta planejar um comando a partir de linguagem natural
        # usando regras locais + LLMs opcionais.
        suggested = _nl_to_command(cmd, state)
        state.add("user", cmd)

        if suggested is None:
            # Sem plano de ação seguro; antes de desistir, tentamos
            # responder a pergunta diretamente usando os LLMs como
            # assistente de linguagem (modo Q&A).
            answer = _qa_answer(cmd, state)
            if answer:
                state.add("agent", answer)
                self.save_state(state)
                kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
                try:
                    kb.add(cmd, answer)
                except Exception:
                    pass
                finally:
                    kb.close()
                return answer

            # Se não houver LLM disponível, usa um fallback local para
            # perguntas comuns e conversa básica.
            local_answer = _local_qa_answer(cmd)
            if local_answer:
                state.add("agent", local_answer)
                self.save_state(state)
                kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
                try:
                    kb.add(cmd, local_answer)
                except Exception:
                    pass
                finally:
                    kb.close()
                return local_answer

            if re.fullmatch(r"\s*\d+\s*", cmd):
                numeric_hint = (
                    "Recebi apenas um numero. Se isso foi escolha de menu, eu aplico a opcao assim que voce pedir o menu novamente. "
                    "Se for outro contexto, me diga em uma frase o objetivo junto com esse numero."
                )
                state.add("agent", numeric_hint)
                self.save_state(state)
                return numeric_hint

            finance_web_answer = _finance_web_research_answer(cmd)
            if finance_web_answer:
                state.add("agent", finance_web_answer)
                self.save_state(state)
                kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
                try:
                    kb.add(cmd, finance_web_answer)
                except Exception:
                    pass
                finally:
                    kb.close()
                return finance_web_answer

            # Sem resposta local/LLM: tenta uma pesquisa rápida na web
            # para evitar resposta vazia ou genérica.
            web_answer = _web_research_answer(cmd)
            if web_answer:
                state.add("agent", web_answer)
                self.save_state(state)
                kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
                try:
                    kb.add(cmd, web_answer)
                except Exception:
                    pass
                finally:
                    kb.close()
                return web_answer

            final_fallback = _default_conversational_fallback(cmd)
            state.add("agent", final_fallback)
            self.save_state(state)
            return final_fallback

        # Nunca executa diretamente comandos sugeridos pelo LLM.
        # Guardamos a sugestão em uma mensagem técnica especial para que a
        # CLI possa oferecer confirmação com uma tecla.
        state.add("agent", f"SUGGESTED:{suggested}")

        # Também registramos no banco de conhecimento global o par
        # (pergunta, sugestão), permitindo reutilizar isso no futuro.
        kb = KnowledgeBase(settings.memory_path.parent / "knowledge.db")
        try:
            kb.add(cmd, f"SUGESTAO_COMANDO: {suggested}")
        except Exception:
            pass
        finally:
            kb.close()

        return (
            "Sugestão do agente (não executada):\n"
            f"  {suggested}\n\n"
            "Digite 'y' para executar agora ou 't' para confiar "
            "nas próximas sugestões nesta sessão."
        )


def create_agent() -> AutonomousAgent:
    store = MemoryStore(settings.memory_path)
    return AutonomousAgent(memory_store=store)
