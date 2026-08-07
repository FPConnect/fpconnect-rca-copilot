from __future__ import annotations

from contextlib import asynccontextmanager
import os
from urllib.parse import urlencode
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from pathlib import Path

from agent_core.background import ensure_hidden_qa_loop
from agent_core.agent import create_agent, plan_agent_mode_browser_command, plan_agent_mode_web_command, plan_agent_mode_workflow
from agent_core.cloud_drives import (
    CloudDriveError,
    complete_cloud_oauth,
    disconnect_cloud_provider,
    list_cloud_provider_statuses,
    start_cloud_oauth,
)
from agent_core.memory import ConversationState
from agent_core.tools import (
    browser_bootstrap,
    browser_click_at,
    browser_disable,
    browser_copy_selection,
    browser_enable,
    browser_open_url,
    browser_paste_text,
    browser_press_key,
    browser_set_zoom,
    browser_snapshot,
    browser_type_text,
    extract_search_query_from_url,
    web_search_results,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_hidden_qa_loop()
    yield


app = FastAPI(title="Agente Autonomo UI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class CommandRequest(BaseModel):
    input: str
    auto_accept: bool = False
    agent_mode: bool | None = None


class CommandResponse(BaseModel):
    reply: str
    auto_accept: bool
    agent_mode: bool
    sources: list[dict[str, str]] = Field(default_factory=list)
    workspace_visible: bool = False
    workspace_title: str | None = None
    activity: list[str] = Field(default_factory=list)


class BrowserClickRequest(BaseModel):
    x: int
    y: int


class BrowserTypeRequest(BaseModel):
    text: str
    press_enter: bool = False


class BrowserOpenRequest(BaseModel):
    url: str


class BrowserKeyRequest(BaseModel):
    key: str


class BrowserPasteRequest(BaseModel):
    text: str


class BrowserZoomRequest(BaseModel):
    zoom: float


class CloudProvidersResponse(BaseModel):
    providers: list[dict[str, object]]


class CloudOauthStartResponse(BaseModel):
    provider: str
    auth_url: str


class CloudDisconnectResponse(BaseModel):
    ok: bool
    message: str


def _configured_public_base_url() -> str | None:
    value = os.getenv("AGENTE_AUTONOMO_PUBLIC_BASE_URL", "").strip()
    return value.rstrip("/") if value else None


def _public_base_url_from_request(request: Request) -> str:
    return _configured_public_base_url() or str(request.base_url).rstrip("/")


def _cloud_callback_redirect(provider: str, status: str, message: str | None = None) -> RedirectResponse:
    params = {"cloud_provider": provider, "cloud_status": status}
    if message:
        params["cloud_message"] = message
    return RedirectResponse(url=f"/?{urlencode(params)}", status_code=303)


def _find_last_suggested(state: ConversationState) -> str | None:
    for m in reversed(state.messages):
        if m.role == "agent" and m.content.startswith("SUGGESTED:"):
            return m.content[len("SUGGESTED:") :].strip()
    return None


def _session_auto_accept(state: ConversationState) -> bool:
    for m in reversed(state.messages):
        if m.role == "tool" and m.content.startswith("AUTO_ACCEPT:"):
            return m.content.split(":", 1)[1].strip() == "1"
    return False


def _set_session_auto_accept(state: ConversationState, enabled: bool) -> None:
    state.add("tool", f"AUTO_ACCEPT:{'1' if enabled else '0'}")


def _session_agent_mode(state: ConversationState) -> bool:
    for m in reversed(state.messages):
        if m.role == "tool" and m.content.startswith("AGENT_MODE:"):
            return m.content.split(":", 1)[1].strip() == "1"
    return False


def _set_session_agent_mode(state: ConversationState, enabled: bool) -> None:
    state.add("tool", f"AGENT_MODE:{'1' if enabled else '0'}")


def _agent_mode_step_failed(executed: str) -> bool:
    lowered = executed.strip().lower()
    if not lowered:
        return True

    failure_markers = [
        "erro ",
        "erro ao",
        "falha ",
        "falha na",
        "nenhuma pagina ativa",
        "nenhuma página ativa",
        "acesso web ainda nao concedido",
        "acesso web ainda não concedido",
        "nao foi possivel",
        "não foi possível",
        "tempo invalido",
        "formato invalido",
        "texto vazio",
        "seletor vazio",
        "tecla vazia",
        "nao encontrei",
        "não encontrei",
    ]
    return any(marker in lowered for marker in failure_markers)


def _agent_mode_needs_auto_wait(command: str) -> bool:
    lowered = command.strip().lower()
    return lowered.startswith((
        "abrir url:",
        "browser: abrir ",
        "browser: primeiro resultado",
        "browser: resultado ",
        "browser: pesquisar ",
        "browser: voltar",
        "browser: avancar",
        "browser: avançar",
        "browser: recarregar",
        "browser: tecla ",
        "browser: texto+enter ",
        "browser: clicar ",
        "browser: clicar texto ",
    ))


def _execute_agent_mode_steps(agent, state: ConversationState, steps: list[tuple[str, str | None]], summary_note: str | None) -> str:
    chunks: list[str] = []
    if summary_note:
        chunks.append(summary_note)

    for index, (command, note) in enumerate(steps, start=1):
        executed = agent.handle_command(command, state)
        if note:
            chunks.append(f"{index}. {note}\n{executed}")
        else:
            chunks.append(f"{index}. {executed}")

        if _agent_mode_step_failed(executed):
            if index < len(steps):
                chunks.append(f"Fluxo interrompido na etapa {index} porque a etapa anterior falhou.")
            break

        if index < len(steps) and _agent_mode_needs_auto_wait(command):
            auto_wait_result = agent.handle_command("browser: esperar 1", state)
            chunks.append(f"{index}.1 Espera automatica para estabilizar a pagina antes da proxima etapa.\n{auto_wait_result}")
            if _agent_mode_step_failed(auto_wait_result):
                chunks.append(f"Fluxo interrompido apos a etapa {index} porque a espera automatica falhou.")
                break

    return "\n\n".join(chunks)


def _browser_snapshot_response(message: str, **extra: str) -> dict:
    snap = browser_snapshot()
    snap["message"] = message
    snap.update(extra)
    return snap


def _looks_like_workspace_task(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in [
            "pesquis",
            "procure",
            "busque",
            "web",
            "internet",
            "site",
            "pagina",
            "página",
            "linkedin",
            "github",
            "janela interna",
            "browser:",
            "abrir url:",
            "resultado",
        ]
    )


def _sources_from_snapshot(snapshot: dict | None) -> list[dict[str, str]]:
    if not snapshot:
        return []
    raw = snapshot.get("results")
    if not isinstance(raw, list):
        return []
    sources: list[dict[str, str]] = []
    for item in raw[:5]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        url = str(item.get("url") or "").strip()
        if not title or not url:
            continue
        source = {"title": title, "url": url}
        snippet = str(item.get("snippet") or "").strip()
        if snippet:
            source["snippet"] = snippet
        sources.append(source)
    return sources


def _compose_search_reply(query: str, sources: list[dict[str, str]], executed: str) -> tuple[str, list[str]]:
    activity = [f"Buscando na web por: {query}"]
    if not sources:
        return (
            f"Fiz a busca por '{query}', mas nao consegui reunir resultados estruturados confiaveis neste ambiente agora.",
            activity,
        )

    lines = [f"Pesquisei na web sobre '{query}' e organizei os principais resultados aqui."]
    for index, item in enumerate(sources, start=1):
        title = item.get("title", "Resultado")
        url = item.get("url", "")
        snippet = item.get("snippet", "")
        line = f"{index}. {title}"
        if snippet:
            line += f" - {snippet}"
        if url:
            line += f" ({url})"
        lines.append(line)
    if executed:
        activity.append(executed)
    return ("\n".join(lines), activity)


@app.post("/api/command", response_model=CommandResponse)
def run_command(payload: CommandRequest) -> CommandResponse:
    """Endpoint mínimo para conversar com o agente-autonomo.

    Observação: o fluxo de auto-aceitação de sugestões está implementado na
    CLI. Aqui mantemos a lógica simples: apenas chamamos handle_command
    uma vez por requisição. Você continua vendo o que é executado.
    """

    agent = create_agent()
    state: ConversationState = agent.load_state()

    session_auto = _session_auto_accept(state)
    session_agent_mode = _session_agent_mode(state)
    agent_mode = session_agent_mode if payload.agent_mode is None else bool(payload.agent_mode)
    if payload.agent_mode is not None and agent_mode != session_agent_mode:
        _set_session_agent_mode(state, agent_mode)

    auto_accept = bool(payload.auto_accept or session_auto or agent_mode)
    user_text = payload.input.strip()
    lowered = user_text.lower()

    # Confirmação explícita da última sugestão (como na CLI).
    if lowered in {"y", "s"}:
        suggested = _find_last_suggested(state)
        if not suggested:
            reply = "Nao ha sugestao pendente para executar agora."
        else:
            reply = agent.handle_command(suggested, state)
        state.add("agent", reply)
        agent.save_state(state)
        return CommandResponse(reply=reply, auto_accept=auto_accept, agent_mode=agent_mode)

    # Confiar nas próximas sugestões da sessão web.
    if lowered == "t":
        _set_session_auto_accept(state, True)
        reply = "Confianca ativada nesta sessao web. Vou executar as proximas sugestoes automaticamente."
        state.add("agent", reply)
        agent.save_state(state)
        return CommandResponse(reply=reply, auto_accept=True, agent_mode=agent_mode)

    if lowered in {"modo agente", "modo agente on", "agent mode on"}:
        _set_session_agent_mode(state, True)
        _set_session_auto_accept(state, True)
        reply = "Modo agente ativado nesta sessao web. Vou executar acoes web seguras diretamente dentro da janela interna."
        state.add("agent", reply)
        agent.save_state(state)
        return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

    if lowered in {"modo agente off", "agent mode off"}:
        _set_session_agent_mode(state, False)
        reply = "Modo agente desativado nesta sessao web. Voltei ao fluxo com mais confirmacoes."
        state.add("agent", reply)
        agent.save_state(state)
        return CommandResponse(reply=reply, auto_accept=auto_accept, agent_mode=False)

    if agent_mode:
        workflow_steps, workflow_note = plan_agent_mode_workflow(user_text)
        if workflow_steps:
            reply = _execute_agent_mode_steps(agent, state, workflow_steps, workflow_note)
            state.add("agent", reply)
            agent.save_state(state)
            snapshot = browser_snapshot()
            return CommandResponse(
                reply=reply,
                auto_accept=True,
                agent_mode=True,
                sources=_sources_from_snapshot(snapshot),
                workspace_visible=_looks_like_workspace_task(user_text) or bool(snapshot.get("url")),
                workspace_title=str(snapshot.get("title") or "") or None,
                activity=[workflow_note] if workflow_note else [],
            )

        planned_command, planned_note = plan_agent_mode_web_command(user_text)
        if planned_command:
            executed = agent.handle_command(planned_command, state)
            snapshot = browser_snapshot()
            query = extract_search_query_from_url(planned_command.removeprefix("abrir url: ").strip())
            sources = _sources_from_snapshot(snapshot)
            activity = [planned_note] if planned_note else []
            if query:
                if not sources:
                    sources = web_search_results(query, limit=5)
                reply, search_activity = _compose_search_reply(query, sources, executed)
                activity.extend(search_activity)
            else:
                reply = f"{planned_note}\n\n{executed}" if planned_note else executed
                if executed:
                    activity.append(executed)
            state.add("agent", reply)
            agent.save_state(state)
            return CommandResponse(
                reply=reply,
                auto_accept=True,
                agent_mode=True,
                sources=sources,
                workspace_visible=_looks_like_workspace_task(user_text) or bool(snapshot.get("url")),
                workspace_title=str(snapshot.get("title") or "") or None,
                activity=activity,
            )

        browser_command, browser_note = plan_agent_mode_browser_command(user_text)
        if browser_command:
            executed = agent.handle_command(browser_command, state)
            reply = f"{browser_note}\n\n{executed}" if browser_note else executed
            state.add("agent", reply)
            agent.save_state(state)
            snapshot = browser_snapshot()
            activity = [browser_note] if browser_note else []
            if executed:
                activity.append(executed)
            return CommandResponse(
                reply=reply,
                auto_accept=True,
                agent_mode=True,
                sources=_sources_from_snapshot(snapshot),
                workspace_visible=_looks_like_workspace_task(user_text) or bool(snapshot.get("url")),
                workspace_title=str(snapshot.get("title") or "") or None,
                activity=activity,
            )

    reply = agent.handle_command(user_text, state)
    state.add("agent", reply)

    # Se auto-aceitar estiver ativo e houver sugestão pendente, executa.
    if auto_accept:
        suggested = _find_last_suggested(state)
        if suggested:
            executed = agent.handle_command(suggested, state)
            state.add("agent", executed)
            reply = f"{reply}\n\n[auto] Executado: {executed}"

    agent.save_state(state)
    snapshot = browser_snapshot()
    return CommandResponse(
        reply=reply,
        auto_accept=auto_accept,
        agent_mode=agent_mode,
        sources=_sources_from_snapshot(snapshot),
        workspace_visible=_looks_like_workspace_task(user_text) or bool(snapshot.get("url")),
        workspace_title=str(snapshot.get("title") or "") or None,
        activity=[],
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/browser/snapshot")
def get_browser_snapshot() -> dict:
    return browser_snapshot()


@app.post("/api/browser/bootstrap")
def post_browser_bootstrap() -> dict:
    result = browser_bootstrap()
    if not result.get("ok"):
        return result
    return _browser_snapshot_response(result.get("message", "Area remota inicializada."))


@app.post("/api/browser/click")
def post_browser_click(payload: BrowserClickRequest) -> dict:
    msg = browser_click_at(payload.x, payload.y)
    return _browser_snapshot_response(msg)


@app.post("/api/browser/type")
def post_browser_type(payload: BrowserTypeRequest) -> dict:
    msg = browser_type_text(payload.text, press_enter=payload.press_enter)
    return _browser_snapshot_response(msg)


@app.post("/api/browser/open")
def post_browser_open(payload: BrowserOpenRequest) -> dict:
    browser_enable()
    msg = browser_open_url(payload.url)
    return _browser_snapshot_response(msg)


@app.post("/api/browser/key")
def post_browser_key(payload: BrowserKeyRequest) -> dict:
    msg = browser_press_key(payload.key)
    return _browser_snapshot_response(msg)


@app.post("/api/browser/copy")
def post_browser_copy() -> dict:
    result = browser_copy_selection()
    if not result.get("ok"):
        return result
    return _browser_snapshot_response(result.get("message", "Texto copiado da janela interna."), copied_text=result.get("text", ""))


@app.post("/api/browser/paste")
def post_browser_paste(payload: BrowserPasteRequest) -> dict:
    msg = browser_paste_text(payload.text)
    return _browser_snapshot_response(msg)


@app.post("/api/browser/zoom")
def post_browser_zoom(payload: BrowserZoomRequest) -> dict:
    result = browser_set_zoom(payload.zoom)
    if not result.get("ok"):
        return result
    return _browser_snapshot_response(result.get("message", "Zoom ajustado."), zoom=str(result.get("zoom", "")))


@app.post("/api/browser/disable")
def post_browser_disable() -> dict:
    msg = browser_disable()
    snap = browser_snapshot()
    return {
        "ok": "erro" not in msg.lower() and "falha" not in msg.lower(),
        "message": msg,
        "snapshot": snap,
    }


@app.get("/api/cloud/providers", response_model=CloudProvidersResponse)
def get_cloud_providers() -> CloudProvidersResponse:
    return CloudProvidersResponse(providers=list_cloud_provider_statuses())


@app.post("/api/cloud/oauth/{provider}/start", response_model=CloudOauthStartResponse)
def post_cloud_oauth_start(provider: str, request: Request) -> CloudOauthStartResponse:
    base_url = _public_base_url_from_request(request)
    auth_url = start_cloud_oauth(provider, base_url=base_url)
    return CloudOauthStartResponse(provider=provider, auth_url=auth_url)


@app.get("/api/cloud/oauth/{provider}/callback")
def get_cloud_oauth_callback(
    provider: str,
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    if error:
        description = (error_description or error).strip()
        return _cloud_callback_redirect(provider, "error", f"Falha na conexao cloud: {description}")

    if not code or not state:
        return HTMLResponse(
            "<html><body style='font-family:Segoe UI,Arial,sans-serif;padding:24px;background:#0f1117;color:#eef3fb'>"
            "<h1>Callback invalido</h1><p>Codigo ou estado ausente.</p></body></html>",
            status_code=400,
        )

    try:
        complete_cloud_oauth(provider, code, state)
    except CloudDriveError as exc:
        return _cloud_callback_redirect(provider, "error", str(exc))

    base_url = _public_base_url_from_request(request)
    return RedirectResponse(
        url=f"{base_url}/?{urlencode({'cloud_provider': provider, 'cloud_status': 'connected'})}",
        status_code=303,
    )


@app.post("/api/cloud/{provider}/disconnect", response_model=CloudDisconnectResponse)
def post_cloud_disconnect(provider: str) -> CloudDisconnectResponse:
    try:
        message = disconnect_cloud_provider(provider)
    except CloudDriveError as exc:
        return CloudDisconnectResponse(ok=False, message=str(exc))
    return CloudDisconnectResponse(ok=True, message=message)
