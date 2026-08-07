from __future__ import annotations

from pathlib import Path

import agent_core.agent as agent_module
from agent_core.agent import AutonomousAgent
from agent_core.config import settings
from agent_core.knowledge import KnowledgeBase
from agent_core.memory import MemoryStore
from agent_core import tools as tools_module
from agent_core.tools import _result_candidate_score


OLD_ERROR = "não reconheci um plano de ação seguro"


def build_agent(tmp_path: Path) -> tuple[AutonomousAgent, object]:
    original_memory_path = settings.memory_path
    settings.memory_path = tmp_path / "memory.json"
    store = MemoryStore(settings.memory_path)
    agent = AutonomousAgent(memory_store=store)
    return agent, original_memory_path


def restore_settings(original_memory_path: object) -> None:
    settings.memory_path = original_memory_path  # type: ignore[assignment]


def test_common_questions_do_not_return_old_error(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        questions = [
            "que dia é hoje?",
            "muito bem! qual é o seu nome?",
            "serio?",
            "como configuro você com llms?",
            "chame modelos externos",
        ]

        for question in questions:
            answer = agent.handle_command(question, state)
            assert OLD_ERROR not in answer.lower()
    finally:
        restore_settings(original_memory_path)


def test_name_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("qual é o seu nome?", state)
        assert "nome" in answer.lower()
        assert OLD_ERROR not in answer.lower()
    finally:
        restore_settings(original_memory_path)


def test_unknown_free_text_uses_safe_conversational_fallback(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("me explica algo aleatório sobre esse agente", state)
        assert "estilo copiloto" in answer
        assert "faltou contexto" in answer
        assert OLD_ERROR not in answer.lower()
    finally:
        restore_settings(original_memory_path)


def test_resources_intent_returns_human_style_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("quais recursos voce tem?", state)
        lowered = answer.lower()
        assert "posso te ajudar" in lowered
        assert "6 frentes" in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_configured_intent_returns_human_style_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("voce esta configurado?", state)
        lowered = answer.lower()
        assert "configur" in lowered or "chaves" in lowered
        assert "estado atual de configuração de llms" not in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_all_llms_intent_returns_human_style_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("quero consultar todos os modelos", state)
        lowered = answer.lower()
        assert "no momento" in lowered or "provedores" in lowered or "backend atual" in lowered
        assert "estado de llms para consulta" not in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_chile_population_question_is_answered_not_greeting(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("qual o estado mais populoso do chile?", state)
        lowered = answer.lower()
        assert "regiao metropolitana de santiago" in lowered
        assert "olá. posso responder perguntas gerais" not in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_brazil_states_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("quantos estados o brasil tem?", state)
        lowered = answer.lower()
        assert "26 estados" in lowered
        assert "27 unidades federativas" in lowered
        assert "entendi. se quiser" not in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_generic_fallback_is_not_saved_to_global_kb(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        question = "blorpt zqxw nartil me ajude"
        answer = agent.handle_command(question, state)
        assert "estilo copiloto" in answer.lower()

        kb = KnowledgeBase(tmp_path / "knowledge.db")
        try:
            hits = kb.search(question, limit=5, min_score=0.01)
            assert all("estilo copiloto" not in item.answer.lower() for item in hits)
        finally:
            kb.close()
    finally:
        restore_settings(original_memory_path)


def test_sign_question_has_direct_identity_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("qual e o seu signo?", state)
        lowered = answer.lower()
        assert "nao tenho data de nascimento" in lowered
        assert "meu nome" not in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_stars_question_has_direct_estimate_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("quantas estrelas tem no espaco?", state)
        lowered = answer.lower()
        assert "10^22" in lowered
        assert "10^24" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_browser_enable_command_is_handled(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("browser enable", state)
        lowered = answer.lower()
        assert "acesso web concedido" in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_browser_type_format_validation(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("browser: digitar #email sem separador", state)
        lowered = answer.lower()
        assert "formato invalido" in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_direct_linkedin_access_phrase_suggests_opening_linkedin(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("acesse meu linkedin", state)
        lowered = answer.lower()
        assert "linkedin" in lowered
        assert "google.com/search" not in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_direct_github_access_phrase_suggests_opening_github(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("abra meu github", state)
        lowered = answer.lower()
        assert "github" in lowered
        assert "google.com/search" not in lowered
        assert OLD_ERROR not in lowered
    finally:
        restore_settings(original_memory_path)


def test_fpconnect_post_profile_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("Consegue fazer posts no meu perfil do FPConnect?", state)
        lowered = answer.lower()
        assert "fpconnect" in lowered
        assert "nao encontrei" in lowered or "ainda nao" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_direct_fpconnect_access_phrase_suggests_opening_local_app(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("abra meu FPConnect", state)
        lowered = answer.lower()
        assert "sugest" in lowered
        assert "127.0.0.1:3000" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_cloud_status_command_is_handled(tmp_path: Path, monkeypatch) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    monkeypatch.setattr(agent_module, "cloud_drive_status_summary", lambda: "Estado cloud ok")
    try:
        state = agent.load_state()
        answer = agent.handle_command("drive status", state)
        assert answer == "Estado cloud ok"
    finally:
        restore_settings(original_memory_path)


def test_cloud_connect_natural_language_is_handled(tmp_path: Path, monkeypatch) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    monkeypatch.setattr(agent_module, "connect_cloud_provider", lambda provider: f"oauth {provider}")
    try:
        state = agent.load_state()
        answer = agent.handle_command("conecte o google drive", state)
        assert answer == "oauth google"
    finally:
        restore_settings(original_memory_path)


def test_cloud_write_command_is_handled(tmp_path: Path, monkeypatch) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    monkeypatch.setattr(
        agent_module,
        "cloud_drive_write_text",
        lambda provider, path, content: f"write {provider} {path} {content}",
    )
    try:
        state = agent.load_state()
        answer = agent.handle_command("drive write google /docs/teste.txt => ola mundo", state)
        assert answer == "write google /docs/teste.txt ola mundo"
    finally:
        restore_settings(original_memory_path)


def test_result_score_matches_synonyms_for_download_and_browser() -> None:
    score = _result_candidate_score("Download Browser Free", "https://example.com/download", "baixar navegador gratis")
    assert score > 0


def test_browser_open_url_returns_search_results_when_embedded_browser_is_blocked(monkeypatch) -> None:
    monkeypatch.setattr(
        tools_module,
        "_call_browser_worker",
        lambda fn, *args: {"ok": False, "error": "A janela interna do agente nao esta disponivel neste ambiente por restricao local de execucao."},
    )
    monkeypatch.setattr(
        tools_module,
        "_web_search_results",
        lambda query, limit=5: [{"title": "Resultado", "url": "https://example.com"}],
    )

    answer = tools_module.browser_open_url("https://www.google.com/search?q=flavio+pimenta+da+cruz")

    assert "janela interna navegou para" in answer.lower()
    assert "https://example.com" in answer


def test_browser_open_url_reports_embedded_and_backend_limits_for_search_when_no_results_are_available(monkeypatch) -> None:
    monkeypatch.setattr(
        tools_module,
        "_call_browser_worker",
        lambda fn, *args: {"ok": False, "error": "A janela interna do agente nao esta disponivel neste ambiente por restricao local de execucao."},
    )
    monkeypatch.setattr(tools_module, "_web_search_results", lambda query, limit=5: [])

    answer = tools_module.browser_open_url("https://www.google.com/search?q=flavio+pimenta+da+cruz")

    lowered = answer.lower()
    assert "janela interna navegou para" in lowered
    assert "nao foi possivel obter resultados reais da web neste ambiente" in lowered
