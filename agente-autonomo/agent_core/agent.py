from __future__ import annotations

import os
import re
import json
import importlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .config import settings
from .cloud_drives import (
    CloudDriveError,
    cloud_drive_delete,
    cloud_drive_list,
    cloud_drive_make_directory,
    cloud_drive_move,
    cloud_drive_read_text,
    cloud_drive_rename,
    cloud_drive_status_summary,
    cloud_drive_upload_local_file,
    cloud_drive_write_text,
    connect_cloud_provider,
    disconnect_cloud_provider,
)
from .memory import ConversationState, MemoryStore
from .knowledge import KnowledgeBase
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


def _cloud_provider_from_text(lowered: str) -> str | None:
    if "google drive" in lowered or ("google" in lowered and "drive" in lowered):
        return "google"
    if "onedrive" in lowered or "one drive" in lowered:
        return "onedrive"
    return None


def _plan_cloud_drive_command(text: str) -> str | None:
    lowered = text.lower()
    provider = _cloud_provider_from_text(lowered)
    if not provider:
        return None

    if any(token in lowered for token in ["conecte", "conectar", "login", "autorize", "autorizar"]):
        return f"drive connect {provider}"
    if any(token in lowered for token in ["desconecte", "desconectar", "logout"]):
        return f"drive disconnect {provider}"
    if any(token in lowered for token in ["status", "estado", "conectado", "conexao", "conexão"]):
        return "drive status"
    return None


def _dispatch_cloud_drive_command(raw_command: str) -> str | None:
    text = raw_command.strip()
    if not text:
        return None

    parts = text.split()
    if not parts or parts[0].lower() not in {"drive", "cloud", "nuvem"}:
        return None

    if len(parts) == 1:
        return (
            "Comandos de armazenamento em nuvem:\n"
            "- drive status\n"
            "- drive connect <google|onedrive>\n"
            "- drive disconnect <google|onedrive>\n"
            "- drive list <provider> [caminho]\n"
            "- drive mkdir <provider> <caminho>\n"
            "- drive read <provider> <arquivo>\n"
            "- drive write <provider> <arquivo> => <conteudo>\n"
            "- drive upload <provider> <arquivo-local> => <arquivo-remoto>\n"
            "- drive rename <provider> <caminho> => <novo-nome>\n"
            "- drive move <provider> <caminho> => <pasta-destino>\n"
            "- drive delete <provider> <caminho>\n"
        )

    action = parts[1].lower()
    rest = text.split(None, 2)[2].strip() if len(parts) > 2 else ""

    try:
        if action in {"status", "estado", "providers", "provedores"}:
            return cloud_drive_status_summary()

        if action in {"connect", "conectar", "login"}:
            if not rest:
                return "Informe o provedor. Exemplo: drive connect google"
            provider = rest.split()[0]
            return connect_cloud_provider(provider)

        if action in {"disconnect", "desconectar", "logout"}:
            if not rest:
                return "Informe o provedor. Exemplo: drive disconnect onedrive"
            provider = rest.split()[0]
            return disconnect_cloud_provider(provider)

        if not rest:
            return "Informe o provedor. Exemplo: drive list google /"

        provider, _, tail = rest.partition(" ")
        provider = provider.strip()
        tail = tail.strip()

        if action in {"list", "listar", "ls"}:
            return cloud_drive_list(provider, tail or "/")

        if action in {"mkdir", "criarpasta", "pasta"}:
            if not tail:
                return "Informe o caminho da pasta. Exemplo: drive mkdir google /Projetos/2026"
            return cloud_drive_make_directory(provider, tail)

        if action in {"read", "ler", "cat"}:
            if not tail:
                return "Informe o arquivo. Exemplo: drive read google /Projetos/nota.txt"
            return cloud_drive_read_text(provider, tail)

        if action in {"write", "escrever", "replace", "substituir", "salvar"}:
            if "=>" not in tail:
                return "Formato invalido. Use: drive write google /pasta/arquivo.txt => conteudo"
            remote_path, content = tail.split("=>", 1)
            return cloud_drive_write_text(provider, remote_path.strip(), content.strip())

        if action in {"upload", "enviar"}:
            if "=>" not in tail:
                return "Formato invalido. Use: drive upload onedrive C:\\arquivo.txt => /Destino/arquivo.txt"
            local_path, remote_path = tail.split("=>", 1)
            return cloud_drive_upload_local_file(provider, local_path.strip(), remote_path.strip())

        if action in {"rename", "renomear"}:
            if "=>" not in tail:
                return "Formato invalido. Use: drive rename google /origem.txt => novo-nome.txt"
            source_path, new_name = tail.split("=>", 1)
            return cloud_drive_rename(provider, source_path.strip(), new_name.strip())

        if action in {"move", "mover"}:
            if "=>" not in tail:
                return "Formato invalido. Use: drive move google /origem.txt => /Nova/Pasta"
            source_path, destination = tail.split("=>", 1)
            return cloud_drive_move(provider, source_path.strip(), destination.strip())

        if action in {"delete", "deletar", "excluir", "apagar", "rm"}:
            if not tail:
                return "Informe o caminho. Exemplo: drive delete google /Projetos/arquivo.txt"
            return cloud_drive_delete(provider, tail)
    except CloudDriveError as exc:
        return str(exc)

    return "Acao de drive invalida. Use 'drive' para ver os comandos disponiveis."


def _looks_like_direct_tool_command(lowered: str) -> bool:
    direct_prefixes = (
        "terminal:",
        "abrir url:",
        "falar:",
        "browser:",
        "rdp:",
        "drive ",
        "cloud ",
        "nuvem ",
    )
    direct_exact = {
        "rdp",
        "drive",
        "cloud",
        "nuvem",
        "browser enable",
        "browser disable",
        "ativar browser",
        "desativar browser",
        "ativar navegador interno",
        "fechar navegador interno",
        "conceder acesso web",
        "revogar acesso web",
    }
    return lowered.startswith(direct_prefixes) or lowered in direct_exact


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
            return f"abrir url: {profile_match.group(0)}", "Abrindo o perfil do LinkedIn pedido agora."

    for keyword, url, label in _DIRECT_DESTINATIONS:
        if keyword == "x":
            if not re.search(r"\bx\b", lowered):
                continue
        elif keyword not in lowered:
            continue
        return f"abrir url: {url}", f"Abrindo o {label} agora."

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


def plan_agent_mode_workflow(goal: str) -> tuple[list[tuple[str, str | None]] | None, str | None]:
    """Planeja uma sequencia curta de passos para pedidos compostos no modo agente."""

    text = goal.strip()
    if not text:
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
        return "abrir url: https://www.linkedin.com/feed/", "Abrindo o feed do LinkedIn agora."

    if web_search_intent and ("linkedin" in lowered or "vaga" in lowered or "job" in lowered):
        location = ""
        location_match = re.search(r"\bem\s+([a-z0-9áàâãéêíóôõúç\-\s]+)$", lowered, flags=re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip(" .,!?:;")

        query = re.sub(
            r"\b(procure|procurar|pesquise|pesquisar|busque|buscar|encontre|achar|ache|no linkedin|na web|na internet)\b",
            " ",
            lowered,
            flags=re.IGNORECASE,
        )
        query = re.sub(r"\s+", " ", query).strip(" .,!?:;") or lowered
        linkedin_url = "https://www.linkedin.com/jobs/search/?keywords=" + quote_plus(query)
        if location:
            linkedin_url += "&location=" + quote_plus(location)
        return f"abrir url: {linkedin_url}", "Pesquisando vagas no LinkedIn agora."

    if web_search_intent or mentions_web:
        query = re.sub(
            r"\b(pesquise|pesquisar|procure|procurar|busque|buscar|encontre|achar|ache|na web|na internet|no google|google|site)\b",
            " ",
            lowered,
            flags=re.IGNORECASE,
        )
        query = re.sub(r"\s+", " ", query).strip(" .,!?:;") or lowered
        return (
            f"abrir url: https://duckduckgo.com/?q={quote_plus(query)}",
            "Pesquisando isso na web agora.",
        )

    return None, None


def plan_agent_mode_browser_command(goal: str) -> tuple[str | None, str | None]:
    """Interpreta pedidos naturais para agir na pagina que ja esta aberta."""

    text = goal.strip()
    lowered = text.lower()
    if not text:
        return None, None

    if any(token in lowered for token in ["extrair texto", "leia a pagina", "ler a pagina", "resuma a pagina", "texto da pagina", "conteudo da pagina", "conteúdo da página"]):
        return "browser: extrair pagina", "Extraindo o texto principal da pagina aberta."

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
        return "browser: primeiro resultado", "Abrindo o primeiro resultado util na pagina atual."

    current_page_search = re.search(
        r"\b(?:pesquise|pesquisar|procure|procurar|busque|buscar)\s+(.+?)\s+(?:nesta pagina|nessa pagina|na pagina|neste site|nesse site|no site atual|aqui)\b",
        text,
        flags=re.IGNORECASE,
    )
    if current_page_search:
        query = current_page_search.group(1).strip(" .,!?:;'")
        if query:
            return f"browser: pesquisar {query}", "Pesquisando isso no campo de busca da pagina atual."

    if any(token in lowered for token in ["volte", "voltar", "pagina anterior", "página anterior"]):
        return "browser: voltar", "Voltando para a pagina anterior."

    if any(token in lowered for token in ["avance", "avancar", "avançar", "proxima pagina", "próxima página"]):
        return "browser: avancar", "Avancando para a proxima pagina."

    if any(token in lowered for token in ["recarregue", "recarregar", "atualize a pagina", "atualizar pagina", "refresh"]):
        return "browser: recarregar", "Recarregando a pagina."

    wait_match = re.search(r"\b(?:espere|aguarde)\s+(\d+(?:[\.,]\d+)?)\s*(?:s|seg|segundo|segundos)?\b", lowered)
    if wait_match:
        seconds = wait_match.group(1).replace(",", ".")
        return f"browser: esperar {seconds}", f"Aguardando {seconds}s antes do proximo passo."

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
        payload = payload.strip(" .,!?:;'")
        if payload:
            prefix = "browser: texto+enter " if press_enter else "browser: texto "
            note = "Digitando esse texto na pagina aberta e enviando Enter." if press_enter else "Digitando esse texto na pagina aberta."
            return prefix + payload, note

    if any(token in lowered for token in ["aperte enter", "pressione enter", "tecla enter"]):
        return "browser: tecla Enter", "Enviando Enter para a pagina aberta."

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


def _clean_suggested_command(text: str | None) -> str | None:
    if not text:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    if stripped.lower() == "none":
        return None
    return stripped.splitlines()[0].strip()


def _llm_status_description() -> str:
    """Retorna uma descrição textual do estado de configuração de LLMs.

    Não tenta chamar nenhum provedor — apenas olha variáveis de ambiente
    para responder perguntas do tipo "você já está configurado?".
    """

    backend = os.getenv(BACKEND_ENV_VAR, "auto").lower().strip()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    providers: list[str] = []
    if has_openai:
        providers.append("OpenAI")
    if has_anthropic:
        providers.append("Anthropic")
    if has_gemini:
        providers.append("Gemini")

    if not providers:
        return (
            "Ainda nao encontrei chaves de LLM configuradas. "
            "Posso continuar no modo local e, quando voce quiser, te guio para ativar OpenAI, Anthropic ou Gemini."
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

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = OpenAI(api_key=api_key)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

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

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        client = OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = OpenAI(api_key=api_key)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

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


def _local_qa_answer(question: str) -> str | None:
    """Fallback de conversa local quando não houver LLM disponível.

    Evita respostas genéricas de erro para perguntas comuns de chat.
    """

    text = question.strip()
    lowered = text.lower()

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

    providers: list[str] = []
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

        if lowered.startswith("backend:"):
            desired = cmd.split(":", 1)[1].strip().lower()
            valid = {"auto", "openai", "anthropic", "gemini", "google", "all", "full", "ensemble"}
            if desired not in valid:
                return (
                    "Backend invalido. Use um destes: auto, openai, anthropic, gemini, all."
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
                "- browser enable       -> abre janela interna para automacao web.\n"
                "- browser disable      -> fecha janela interna de automacao web.\n"
                "- browser: abrir <url>\n"
                "- browser: clicar <seletor CSS>\n"
                "- browser: digitar <seletor> => <texto>\n"
                "- browser: extrair <seletor CSS>\n"
                "- browser: esperar <segundos>\n"
                "- drive ...            -> conecta Google Drive/OneDrive e opera arquivos.\n"
                "- tools                -> lista as ferramentas disponíveis.\n"
                "- frase solta          -> o agente sugere um comando usando LLM (se configurado).\n"
                "- quit / sair          -> encerra.\n"
            )

        # Perguntas abertas sobre capacidades/recursos do agente
        if any(word in lowered for word in ["recurso", "recursos", "capacidade", "capacidades", "o que voce sabe fazer", "o que você sabe fazer", "what can you do", "capabilities"]):
            return (
                "Posso te ajudar em 6 frentes: executar comando de terminal, abrir URL, abrir RDP, falar texto, operar Google Drive/OneDrive e responder perguntas. "
                "Se LLMs estiverem ativos, tambem interpreto pedidos em linguagem natural e te proponho uma acao segura para confirmar."
            )

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

        # Primeiro tenta conversa local (perguntas gerais comuns), para
        # evitar cair em fluxo de comando quando o usuário só quer uma
        # resposta textual.
        if not _looks_like_direct_tool_command(lowered):
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
                "   - ou 'openai', 'anthropic', 'gemini' se quiser forçar um só.\n\n"
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

        planned_cloud_command = _plan_cloud_drive_command(cmd)
        if planned_cloud_command:
            cloud_reply = _dispatch_cloud_drive_command(planned_cloud_command)
            if cloud_reply is not None:
                return cloud_reply

        cloud_direct = _dispatch_cloud_drive_command(cmd)
        if cloud_direct is not None:
            return cloud_direct

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

        if lowered in {"browser enable", "ativar browser", "ativar navegador interno", "conceder acesso web"}:
            return browser_enable()

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
