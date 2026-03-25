from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from agent_core.background import ensure_hidden_learning_loop, ensure_hidden_qa_loop
from agent_core.agent import _is_profile_intent_without_criteria, classify_agent_mode_intent, create_agent, is_profile_based_intent, plan_agent_mode_browser_command, plan_agent_mode_contextual_workflow, plan_agent_mode_llm_browser_command, plan_agent_mode_login_workflow, plan_agent_mode_web_command, plan_agent_mode_workflow
from agent_core.finance_knowledge import finance_knowledge_entries, finance_study_track_entries
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
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_hidden_qa_loop()
    ensure_hidden_learning_loop()
    yield


app = FastAPI(title="Agente Autonomo UI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class CommandRequest(BaseModel):
    input: str
    auto_accept: bool = False
    agent_mode: bool | None = None
    login_context: dict | None = None


class CommandResponse(BaseModel):
    reply: str
    auto_accept: bool
    agent_mode: bool


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
        login_ctx = payload.login_context or {}
        login_service = str(login_ctx.get("service") or "").strip()
        login_user = str(login_ctx.get("username") or "").strip()
        login_password = str(login_ctx.get("password") or "").strip()

        # Hard guard: block vague profile-fit prompts before any planner/fallback can execute.
        if _is_profile_intent_without_criteria(user_text):
            reply = (
                "Nao vou executar uma busca generica so com 'vagas'. Para buscar de acordo com seu perfil, preciso de contexto real, "
                "como cargo, stack, senioridade ou um perfil salvo/aberto para eu analisar."
            )
            state.add("agent", reply)
            agent.save_state(state)
            return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

        intent = classify_agent_mode_intent(user_text, state)

        if intent == "meta":
            reply = (
                "Entendi como uma instrucao sobre o comportamento do agente, nao como uma tarefa de navegador. "
                "Nenhuma acao na workspace foi executada para evitar copiar o texto do chat literalmente."
            )
            state.add("agent", reply)
            agent.save_state(state)
            return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

        if intent == "login":
            if not login_user or not login_password:
                reply = "Nao encontrei credenciais salvas na workspace. Preencha servico, usuario e senha no cofre lateral e tente de novo."
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

            login_steps, login_note = plan_agent_mode_login_workflow(user_text, login_service, login_user, login_password)
            if login_steps:
                reply = _execute_agent_mode_steps(agent, state, login_steps, login_note)
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

        # For profile-based prompts, prefer contextual reasoning (LLM + current page)
        # before deterministic keyword rules, to avoid generic searches like "vagas".
        if intent == "workspace_task" and is_profile_based_intent(user_text):
            llm_command, llm_note = plan_agent_mode_llm_browser_command(user_text, state)
            if llm_command:
                executed = agent.handle_command(llm_command, state)
                reply = f"{llm_note}\n\n{executed}" if llm_note else executed
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

        if intent == "workspace_task":
            contextual_steps, contextual_note = plan_agent_mode_contextual_workflow(user_text, state)
            if contextual_steps:
                reply = _execute_agent_mode_steps(agent, state, contextual_steps, contextual_note)
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

            workflow_steps, workflow_note = plan_agent_mode_workflow(user_text)
            if workflow_steps:
                reply = _execute_agent_mode_steps(agent, state, workflow_steps, workflow_note)
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

            planned_command, planned_note = plan_agent_mode_web_command(user_text)
            if planned_command:
                executed = agent.handle_command(planned_command, state)
                reply = f"{planned_note}\n\n{executed}" if planned_note else executed
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

            browser_command, browser_note = plan_agent_mode_browser_command(user_text)
            if browser_command:
                executed = agent.handle_command(browser_command, state)
                reply = f"{browser_note}\n\n{executed}" if browser_note else executed
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

            # LLM-based contextual planner: reads current page context and decides
            # which browser: command to execute, handling anything the regex planners missed.
            llm_command, llm_note = plan_agent_mode_llm_browser_command(user_text, state)
            if llm_command:
                executed = agent.handle_command(llm_command, state)
                reply = f"{llm_note}\n\n{executed}" if llm_note else executed
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

            if is_profile_based_intent(user_text):
                reply = (
                    "Nao vou executar uma busca generica so com 'vagas'. Para buscar de acordo com seu perfil, preciso de contexto real, "
                    "como cargo, stack, senioridade ou um perfil salvo/aberto para eu analisar."
                )
                state.add("agent", reply)
                agent.save_state(state)
                return CommandResponse(reply=reply, auto_accept=True, agent_mode=True)

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
    return CommandResponse(reply=reply, auto_accept=auto_accept, agent_mode=agent_mode)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/finance/tracks")
def get_finance_tracks() -> dict:
    return {"ok": True, "tracks": finance_study_track_entries()}


@app.get("/api/finance/knowledge")
def get_finance_knowledge() -> dict:
    return {"ok": True, "entries": finance_knowledge_entries()}


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
