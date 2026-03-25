from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agent_core.memory import ConversationState
from agent_core.config import settings
from agent_core.agent import _is_generic_search_query, _semantic_search_query, plan_agent_mode_web_command, plan_agent_mode_workflow
from web import server as server_module
from web.server import app


def test_web_y_executes_pending_suggestion(tmp_path: Path) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    try:
        client = TestClient(app)

        q = "acesse meu linkedin https://www.linkedin.com/in/flavio-cruz-09751820/"
        first = client.post("/api/command", json={"input": q, "auto_accept": False})
        assert first.status_code == 200
        reply1 = first.json()["reply"].lower()
        assert "sugestão do agente" in reply1 or "sugestao do agente" in reply1

        second = client.post("/api/command", json={"input": "y", "auto_accept": False})
        assert second.status_code == 200
        reply2 = second.json()["reply"].lower()
        assert "janela interna" in reply2 or "playwright" in reply2
        assert "pesquisei na web e encontrei: y:" not in reply2
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_executes_web_goal_without_confirmation(tmp_path: Path) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "procure vagas no linkedin em porto alegre rs",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert body["auto_accept"] is True
        assert "sugestão do agente" not in reply and "sugestao do agente" not in reply
        assert "linkedin" in reply or "janela interna" in reply or "playwright" in reply
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_plan_agent_mode_web_command_opens_linkedin_directly_from_access_phrase() -> None:
    command, note = plan_agent_mode_web_command("com a area de trabalho remota, acesse meu linkedin")

    assert command == "abrir url: https://www.linkedin.com/feed/"
    assert note is not None
    assert "linkedin" in note.lower()


def test_plan_agent_mode_web_command_opens_github_directly_from_access_phrase() -> None:
    command, note = plan_agent_mode_web_command("abra meu github")

    assert command == "abrir url: https://github.com/"
    assert note is not None
    assert "github" in note.lower()


def test_web_agent_mode_can_extract_page_text_from_open_page(tmp_path: Path) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    try:
        client = TestClient(app)

        opened = client.post(
            "/api/command",
            json={
                "input": "abra https://example.com",
                "auto_accept": False,
                "agent_mode": True,
            },
        )
        assert opened.status_code == 200

        extracted = client.post(
            "/api/command",
            json={
                "input": "extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert extracted.status_code == 200
        body = extracted.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert "texto principal da pagina" in reply
        assert "example domain" in reply
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_opens_linkedin_directly_instead_of_search(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command == "abrir url: https://www.linkedin.com/feed/":
                return "Janela interna navegou para: https://www.linkedin.com/feed/"
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "com a area de trabalho remota, acesse meu linkedin",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        reply = response.json()["reply"].lower()
        assert "google.com/search" not in reply
        assert fake_agent.calls == ["abrir url: https://www.linkedin.com/feed/"]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_plan_agent_mode_workflow_splits_compound_goal() -> None:
    steps, note = plan_agent_mode_workflow("abra https://example.com e extraia o texto da pagina")

    assert steps is not None
    assert note is not None
    assert steps[0][0] == "abrir url: https://example.com"
    assert steps[1][0] == "browser: extrair pagina"


def test_plan_agent_mode_workflow_supports_wait_step() -> None:
    steps, note = plan_agent_mode_workflow("abra https://example.com e aguarde 1,5 segundos e extraia o texto da pagina")

    assert steps is not None
    assert note is not None
    assert steps[0][0] == "abrir url: https://example.com"
    assert steps[1][0] == "browser: esperar 1.5"
    assert steps[2][0] == "browser: extrair pagina"


def test_plan_agent_mode_workflow_keeps_type_plus_enter_together() -> None:
    steps, _ = plan_agent_mode_workflow("digite exemplo e aperte enter e extraia o texto da pagina")

    assert steps is not None
    assert steps[0][0] == "browser: texto+enter exemplo"
    assert steps[1][0] == "browser: extrair pagina"


def test_plan_agent_mode_workflow_supports_open_first_result() -> None:
    steps, _ = plan_agent_mode_workflow("procure example domain na web e abra o primeiro resultado e extraia o texto da pagina")

    assert steps is not None
    assert steps[0][0].startswith("abrir url: https://www.google.com/search?q=")
    assert steps[1][0] == "browser: primeiro resultado"
    assert steps[2][0] == "browser: extrair pagina"


def test_plan_agent_mode_workflow_supports_search_on_current_page() -> None:
    steps, _ = plan_agent_mode_workflow("abra https://duckduckgo.com e pesquise example domain neste site e abra o primeiro resultado e extraia o texto da pagina")

    assert steps is not None
    assert steps[0][0] == "abrir url: https://duckduckgo.com"
    assert steps[1][0] == "browser: pesquisar example domain"
    assert steps[2][0] == "browser: primeiro resultado"
    assert steps[3][0] == "browser: extrair pagina"


def test_plan_agent_mode_workflow_supports_targeted_result() -> None:
    steps, _ = plan_agent_mode_workflow("abra https://duckduckgo.com e pesquise example domain neste site e abra o resultado download browser e extraia o texto da pagina")

    assert steps is not None
    assert steps[0][0] == "abrir url: https://duckduckgo.com"
    assert steps[1][0] == "browser: pesquisar example domain"
    assert steps[2][0] == "browser: resultado download browser"
    assert steps[3][0] == "browser: extrair pagina"


def test_plan_agent_mode_workflow_routes_targeted_result_with_browser_words_to_browser_step() -> None:
    steps, _ = plan_agent_mode_workflow("abra https://duckduckgo.com e abra o resultado baixar navegador gratis")

    assert steps is not None
    assert steps[0][0] == "abrir url: https://duckduckgo.com"
    assert steps[1][0] == "browser: resultado baixar navegador gratis"


def test_web_agent_mode_executes_compound_goal_sequence(tmp_path: Path) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "abra https://example.com e extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert body["auto_accept"] is True
        assert "sequencia de acoes" in reply
        assert "janela interna navegou para: https://example.com" in reply
        assert "espera automatica para estabilizar a pagina" in reply
        assert "texto principal da pagina" in reply
        assert "example domain" in reply
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_auto_waits_after_enter_before_extraction(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command.startswith("browser: texto+enter "):
                return "Texto digitado na janela interna."
            if command == "browser: esperar 1":
                return "Aguardado 1.0s na janela interna."
            if command == "browser: extrair pagina":
                return "Texto principal da pagina: resultados carregados"
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "digite exemplo e aperte enter e extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert "espera automatica para estabilizar a pagina" in reply
        assert fake_agent.calls == ["browser: texto+enter exemplo", "browser: esperar 1", "browser: extrair pagina"]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_stops_workflow_after_failed_step(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command.startswith("abrir url:"):
                return "Janela interna navegou para: https://example.com"
            if command == "browser: extrair pagina":
                return "Erro ao extrair texto da pagina: timeout"
            return "Clique executado no texto visivel: Entrar"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "abra https://example.com e extraia o texto da pagina e clique em entrar",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert "fluxo interrompido na etapa 2" in reply
        assert fake_agent.calls == ["abrir url: https://example.com", "browser: esperar 1", "browser: extrair pagina"]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_opens_first_result_then_extracts(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command.startswith("abrir url: https://www.google.com/search?q="):
                return "Janela interna navegou para: https://www.google.com/search?q=example+domain"
            if command == "browser: esperar 1":
                return "Aguardado 1.0s na janela interna."
            if command == "browser: primeiro resultado":
                return "Primeiro resultado aberto na janela interna: Example Domain"
            if command == "browser: extrair pagina":
                return "Texto principal da pagina: example domain opened"
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "procure example domain na web e abra o primeiro resultado e extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert "primeiro resultado aberto na janela interna" in reply
        assert fake_agent.calls == [
            "abrir url: https://www.google.com/search?q=example+domain",
            "browser: esperar 1",
            "browser: primeiro resultado",
            "browser: esperar 1",
            "browser: extrair pagina",
        ]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_searches_current_page_then_opens_first_result(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command == "abrir url: https://duckduckgo.com":
                return "Janela interna navegou para: https://duckduckgo.com"
            if command == "browser: esperar 1":
                return "Aguardado 1.0s na janela interna."
            if command == "browser: pesquisar example domain":
                return "Busca digitada no campo de pesquisa da pagina."
            if command == "browser: primeiro resultado":
                return "Primeiro resultado aberto na janela interna: Example Domain"
            if command == "browser: extrair pagina":
                return "Texto principal da pagina: example domain opened"
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "abra https://duckduckgo.com e pesquise example domain neste site e abra o primeiro resultado e extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert "pesquisando isso no campo de busca da pagina atual" in reply
        assert fake_agent.calls == [
            "abrir url: https://duckduckgo.com",
            "browser: esperar 1",
            "browser: pesquisar example domain",
            "browser: esperar 1",
            "browser: primeiro resultado",
            "browser: esperar 1",
            "browser: extrair pagina",
        ]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_searches_current_page_then_opens_targeted_result(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command == "abrir url: https://duckduckgo.com":
                return "Janela interna navegou para: https://duckduckgo.com"
            if command == "browser: esperar 1":
                return "Aguardado 1.0s na janela interna."
            if command == "browser: pesquisar example domain":
                return "Busca digitada no campo de pesquisa da pagina."
            if command == "browser: resultado download browser":
                return "Resultado relacionado a 'download browser' aberto na janela interna: Download Browser"
            if command == "browser: extrair pagina":
                return "Texto principal da pagina: download browser opened"
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "abra https://duckduckgo.com e pesquise example domain neste site e abra o resultado download browser e extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert body["agent_mode"] is True
        assert "resultado relacionado" in reply
        assert fake_agent.calls == [
            "abrir url: https://duckduckgo.com",
            "browser: esperar 1",
            "browser: pesquisar example domain",
            "browser: esperar 1",
            "browser: resultado download browser",
            "browser: esperar 1",
            "browser: extrair pagina",
        ]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_stops_after_targeted_result_failure(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command == "abrir url: https://duckduckgo.com":
                return "Janela interna navegou para: https://duckduckgo.com"
            if command == "browser: esperar 1":
                return "Aguardado 1.0s na janela interna."
            if command == "browser: pesquisar example domain":
                return "Busca digitada no campo de pesquisa da pagina."
            if command == "browser: resultado download browser":
                return "Nao encontrei um resultado relacionado a 'download browser' na pagina aberta."
            if command == "browser: extrair pagina":
                return "Texto principal da pagina: nao deveria executar"
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "abra https://duckduckgo.com e pesquise example domain neste site e abra o resultado download browser e extraia o texto da pagina",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "fluxo interrompido na etapa 3" in reply
        assert fake_agent.calls == [
            "abrir url: https://duckduckgo.com",
            "browser: esperar 1",
            "browser: pesquisar example domain",
            "browser: esperar 1",
            "browser: resultado download browser",
        ]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_browser_copy_endpoint_returns_selected_text(monkeypatch) -> None:
    monkeypatch.setattr(
        server_module,
        "browser_copy_selection",
        lambda: {"ok": True, "text": "texto copiado", "message": "Texto copiado da janela interna (13 caracteres)."},
    )
    monkeypatch.setattr(
        server_module,
        "browser_snapshot",
        lambda: {"ok": True, "image_base64": "ZmFrZQ==", "width": 1280, "height": 720, "url": "https://example.com", "title": "Example"},
    )

    client = TestClient(app)
    response = client.post("/api/browser/copy")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["copied_text"] == "texto copiado"
    assert body["message"].startswith("Texto copiado da janela interna")


def test_browser_bootstrap_endpoint_returns_snapshot(monkeypatch) -> None:
    monkeypatch.setattr(
        server_module,
        "browser_bootstrap",
        lambda: {"ok": True, "message": "Area remota inicializada automaticamente."},
    )
    monkeypatch.setattr(
        server_module,
        "browser_snapshot",
        lambda: {"ok": True, "image_base64": "ZmFrZQ==", "width": 1280, "height": 720, "url": "about:blank", "title": "Area de trabalho remota pronta"},
    )

    client = TestClient(app)
    response = client.post("/api/browser/bootstrap")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["message"] == "Area remota inicializada automaticamente."
    assert body["image_base64"] == "ZmFrZQ=="


def test_browser_paste_endpoint_returns_snapshot(monkeypatch) -> None:
    monkeypatch.setattr(server_module, "browser_paste_text", lambda text: f"Texto colado na janela interna ({len(text)} caracteres).")
    monkeypatch.setattr(
        server_module,
        "browser_snapshot",
        lambda: {"ok": True, "image_base64": "ZmFrZQ==", "width": 1280, "height": 720, "url": "https://example.com", "title": "Example"},
    )

    client = TestClient(app)
    response = client.post("/api/browser/paste", json={"text": "colar isso"})

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["message"] == "Texto colado na janela interna (10 caracteres)."
    assert body["image_base64"] == "ZmFrZQ=="


def test_browser_zoom_endpoint_returns_snapshot(monkeypatch) -> None:
    monkeypatch.setattr(
        server_module,
        "browser_set_zoom",
        lambda zoom: {"ok": True, "zoom": zoom, "message": f"Zoom do navegador interno ajustado para {round(zoom * 100):d}%."},
    )
    monkeypatch.setattr(
        server_module,
        "browser_snapshot",
        lambda: {"ok": True, "image_base64": "ZmFrZQ==", "width": 1280, "height": 720, "url": "https://example.com", "title": "Example", "zoom": 1.3},
    )

    client = TestClient(app)
    response = client.post("/api/browser/zoom", json={"zoom": 1.3})

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["message"] == "Zoom do navegador interno ajustado para 130%."
    assert body["zoom"] == "1.3"


def test_semantic_query_ignores_connective_profile_fillers() -> None:
    query = _semantic_search_query("procure vagas no brasil que sejam de acordo com meu perfil")

    assert query == "brasil"
    assert "que" not in query
    assert "sejam" not in query
    assert _is_generic_search_query(query) is True


def test_web_agent_mode_profile_prompt_without_criteria_does_not_execute_browser_actions(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "procure vagas no brasil que sejam de acordo com meu perfil",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "nao vou executar uma busca generica" in reply
        assert fake_agent.calls == []
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_meta_instruction_never_executes_browser_action(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "nao copie o que esta no chat, analise e execute corretamente",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "instrucao sobre o comportamento" in reply
        assert fake_agent.calls == []
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_login_uses_saved_workspace_credentials(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            if command.startswith("abrir url: https://www.linkedin.com/login"):
                return "Janela interna navegou para: https://www.linkedin.com/login"
            if command == "browser: esperar 1":
                return "Aguardado 1.0s na janela interna."
            if command.startswith("browser: texto "):
                return "Texto digitado na janela interna."
            if command == "browser: tecla Tab":
                return "Tecla Tab enviada para a janela interna."
            if command.startswith("browser: texto+enter "):
                return "Texto enviado com Enter na janela interna."
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "faça login no linkedin",
                "auto_accept": False,
                "agent_mode": True,
                "login_context": {
                    "service": "linkedin",
                    "username": "flavio.rj@hotmail.com",
                    "password": "senha-secreta",
                },
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "executando login com credenciais salvas" in reply
        assert fake_agent.calls == [
            "abrir url: https://www.linkedin.com/login",
            "browser: esperar 1",
            "browser: texto flavio.rj@hotmail.com",
            "browser: tecla Tab",
            "browser: esperar 1",
            "browser: texto+enter senha-secreta",
        ]
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_semantic_query_drops_action_residue_term_entre() -> None:
    query = _semantic_search_query("entre no meu linkedin e busque vagas com meu perfil")

    assert query == ""


def test_plan_agent_mode_web_command_profile_prompt_with_entre_residue_is_blocked() -> None:
    command, note = plan_agent_mode_web_command("entre no meu linkedin e busque vagas com meu perfil")

    assert command is None
    assert note is None


def test_plan_agent_mode_web_command_profile_fit_phrase_without_criteria_is_blocked() -> None:
    command, note = plan_agent_mode_web_command("analise o meu perfil e busque vagas em que eu possa ser encaixado")

    assert command is None
    assert note is None


def test_web_agent_mode_profile_fit_phrase_without_criteria_does_not_execute_browser_actions(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "analise o meu perfil e busque vagas em que eu possa ser encaixado",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "nao vou executar uma busca generica" in reply
        assert fake_agent.calls == []
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_web_agent_mode_hard_guard_blocks_vague_profile_fit_prompt_before_planners(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "analise o que combina comigo e vagas no linkedin",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "nao vou executar uma busca generica" in reply
        assert fake_agent.calls == []
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_plan_agent_mode_web_command_blocks_aderencia_phrase_without_real_criteria() -> None:
    command, note = plan_agent_mode_web_command("agora procure todas as vagas na europa que eu tenho aderencia")

    assert command is None
    assert note is None


def test_web_agent_mode_hard_guard_blocks_aderencia_phrase_without_real_criteria(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"

    class FakeAgent:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.state = ConversationState.empty()

        def load_state(self) -> ConversationState:
            return self.state

        def save_state(self, state: ConversationState) -> None:
            self.state = state

        def handle_command(self, command: str, state: ConversationState) -> str:
            self.calls.append(command)
            return f"UNEXPECTED {command}"

    fake_agent = FakeAgent()
    monkeypatch.setattr(server_module, "create_agent", lambda: fake_agent)

    try:
        client = TestClient(app)

        response = client.post(
            "/api/command",
            json={
                "input": "agora procure todas as vagas na europa que eu tenho aderencia",
                "auto_accept": False,
                "agent_mode": True,
            },
        )

        assert response.status_code == 200
        body = response.json()
        reply = body["reply"].lower()
        assert "nao vou executar uma busca generica" in reply
        assert fake_agent.calls == []
    finally:
        settings.memory_path = original_memory_path  # type: ignore[assignment]


@pytest.mark.parametrize(
    "prompt",
    [
        "analise meu perfil e busque vagas para mim",
        "analisa meu perfil e encontre oportunidades",
        "com base no meu perfil procure vagas",
        "de acordo com meu perfil busque vagas no linkedin",
        "entre no linkedin e ache vagas compativeis com meu perfil",
        "acesse meu linkedin e procure algo que combine comigo",
        "quero vagas que encaixem no meu perfil",
        "encontre vagas aderentes ao meu perfil",
        "procure oportunidades ideais para meu perfil",
        "busque empregos que tenham meu perfil",
        "me arruma vagas conforme meu perfil",
        "traga vagas de acordo comigo",
        "encontre uma vaga que eu possa ser encaixado",
        "pesquise jobs no linkedin que combinem comigo",
        "busca vaga perfeita pro meu perfil",
        "vagas para meu perfil no brasil",
        "vagas para meu perfil na europa",
        "ache vagas em que eu possa ser encaixado",
        "analise o meu perfil e veja vagas para mim",
        "entre no meu linkedin e me traga vagas aderentes",
    ],
)
def test_plan_agent_mode_web_command_blocks_many_profile_vague_variants(prompt: str) -> None:
    command, note = plan_agent_mode_web_command(prompt)

    assert command is None
    assert note is None


def test_plan_agent_mode_web_command_allows_profile_prompt_with_real_criteria() -> None:
    command, note = plan_agent_mode_web_command(
        "com base no meu perfil busque vagas de engenheiro de dados senior com python no linkedin"
    )

    assert command is not None
    assert note is not None
    assert command.startswith("abrir url: https://www.linkedin.com/jobs/search/?keywords=")


def test_plan_agent_mode_web_command_blocks_3500_generated_profile_vague_prompts() -> None:
    actions = [
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
    ]
    starters = [
        "meu perfil",
        "o meu perfil",
        "com meu perfil",
        "com base no meu perfil",
        "de acordo com meu perfil",
        "de acordo comigo",
        "o que combina comigo",
        "o que seja aderente ao meu perfil",
        "algo compativel com meu perfil",
        "algo que encaixe em mim",
    ]
    vague_targets = [
        "vagas",
        "jobs",
        "oportunidades",
        "trabalhos",
        "vagas no brasil",
        "vagas na europa",
        "vagas remotas",
    ]
    tails = [
        "no linkedin",
        "agora",
        "por favor",
        "para mim",
        "",
    ]

    seen = 0
    for action in actions:
        for starter in starters:
            for target in vague_targets:
                for tail in tails:
                    prompt = f"{action} {starter} e {target} {tail}".strip()
                    command, note = plan_agent_mode_web_command(prompt)
                    assert command is None, f"Nao deveria gerar comando para prompt vago: {prompt}"
                    assert note is None, f"Nao deveria gerar nota para prompt vago: {prompt}"
                    seen += 1
                    if seen >= 3500:
                        break
                if seen >= 3500:
                    break
            if seen >= 3500:
                break
        if seen >= 3500:
            break

    assert seen == 3500
