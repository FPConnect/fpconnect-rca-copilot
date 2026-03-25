from __future__ import annotations

from pathlib import Path

from agent_core.agent import AutonomousAgent
from agent_core.config import settings
from agent_core.knowledge import KnowledgeBase
from agent_core.memory import MemoryStore
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
        assert "paper trading" in lowered
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


def test_beginner_stock_market_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("Como faço para investir na bolsa?", state)
        lowered = answer.lower()
        assert "corretora" in lowered
        assert "divers" in lowered
        assert "estilo copiloto" not in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_learning_to_invest_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("como faço pra aprender a investir?", state)
        lowered = answer.lower()
        assert "renda fixa" in lowered
        assert "trilha iniciante" in lowered
        assert "estilo copiloto" not in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_small_amount_investment_question_has_actionable_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("quero investir 30 reais agora, como faco?", state)
        lowered = answer.lower()
        assert "tesouro selic" in lowered or "cdb" in lowered
        assert "corretora" in lowered
        assert "consigo responder perguntas amplas" not in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_quero_aprender_phrase_does_not_use_generic_fallback(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("ok, vamos la, quero aprender", state)
        lowered = answer.lower()
        assert "estilo copiloto" not in lowered
        assert "faltou contexto" not in lowered
        assert "vamos aprender" in lowered
    finally:
        restore_settings(original_memory_path)


def test_learning_menu_numeric_choice_routes_to_investments(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        menu_answer = agent.handle_command("ok, vamos la, quero aprender", state)
        assert "escolha um caminho" in menu_answer.lower()

        answer = agent.handle_command("2", state)
        lowered = answer.lower()
        assert "renda fixa" in lowered
        assert "tesouro selic" in lowered
        assert "pesquisei na web e encontrei" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_bare_numeric_input_without_menu_does_not_use_web_lookup(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("2", state)
        lowered = answer.lower()
        assert "pesquisei na web e encontrei" not in lowered
        assert "recebi apenas um numero" in lowered
    finally:
        restore_settings(original_memory_path)


def test_ok_vamos_para_trilha_returns_study_track(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("ok, vamos para a trilha", state)
        lowered = answer.lower()
        assert "trilha iniciante" in lowered or "trilha de mercado" in lowered
        assert "faltou contexto" not in lowered
        assert "estilo copiloto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_renda_fixa_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("O que e renda fixa?", state)
        lowered = answer.lower()
        assert "tesouro selic" in lowered
        assert "cdb" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_selic_and_cdi_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("Qual a diferenca entre Selic e CDI?", state)
        lowered = answer.lower()
        assert "selic" in lowered
        assert "cdi" in lowered
        assert "ipca" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_valuation_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("O que e valuation?", state)
        lowered = answer.lower()
        assert "pl" in lowered or "p/l" in lowered
        assert "ev/ebitda" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_trading_style_question_has_direct_answer(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("Qual a diferenca entre day trade, swing trade e buy and hold?", state)
        lowered = answer.lower()
        assert "day trade" in lowered
        assert "swing trade" in lowered
        assert "buy and hold" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_debentures_question_is_answered_from_finance_knowledge(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("O que sao debentures?", state)
        lowered = answer.lower()
        assert "titulos de divida" in lowered or "títulos de dívida" in lowered
        assert "fgc" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_natural_language_finance_study_request_returns_beginner_track(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        answer = agent.handle_command("Quero estudar mercado financeiro", state)
        lowered = answer.lower()
        assert "trilha iniciante" in lowered
        assert "reserva de emergencia" in lowered
        assert "faltou contexto" not in lowered
    finally:
        restore_settings(original_memory_path)


def test_curated_finance_knowledge_is_seeded_into_local_db(tmp_path: Path) -> None:
    agent, original_memory_path = build_agent(tmp_path)
    try:
        state = agent.load_state()
        _ = agent.handle_command("O que sao debentures?", state)

        kb = KnowledgeBase(tmp_path / "knowledge.db")
        try:
            hits = kb.search("o que sao debentures", limit=5, min_score=0.05)
            assert any("debentures" in item.question.lower() for item in hits)
        finally:
            kb.close()
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


def test_result_score_matches_synonyms_for_download_and_browser() -> None:
    score = _result_candidate_score("Download Browser Free", "https://example.com/download", "baixar navegador gratis")
    assert score > 0
