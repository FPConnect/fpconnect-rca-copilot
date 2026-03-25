from __future__ import annotations

from pathlib import Path

from agent_core.agent import AutonomousAgent
from agent_core.config import settings
from agent_core.market import MarketAnalysis, QuoteSnapshot, TradePlan, build_trade_plan, handle_market_command, load_paper_state
from agent_core.memory import MemoryStore


def test_build_trade_plan_respects_brl_constraints(monkeypatch) -> None:
    quote = QuoteSnapshot(
        symbol="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        asset_type="equity",
        price=100.0,
        previous_close=99.0,
        change_percent=1.0,
        market_state="REGULAR",
        fetched_at="2026-03-12T00:00:00+00:00",
    )
    analysis = MarketAnalysis(
        quote=quote,
        sma20=98.0,
        sma50=95.0,
        rsi14=58.0,
        atr14=2.0,
        momentum_20d_pct=6.0,
        volatility_20d_pct=22.0,
        action="buy",
        confidence="alta",
        reasons=["preco acima das medias"],
    )

    monkeypatch.setattr("agent_core.market.analyze_symbol", lambda symbol: analysis)
    monkeypatch.setattr("agent_core.market.fetch_brl_fx_rate", lambda currency: 5.0)

    plan = build_trade_plan("AAPL")
    assert plan.approved is True
    assert plan.modeled_profit_brl >= 100.0
    assert plan.modeled_loss_brl <= 50.0
    assert plan.quantity > 0


def test_handle_market_command_returns_help_for_root_command() -> None:
    reply = handle_market_command("mercado")
    assert reply is not None
    assert "mercado: analisar" in reply.lower()


def test_agent_routes_market_commands_without_kb(tmp_path: Path, monkeypatch) -> None:
    original_memory_path = settings.memory_path
    original_market_state_path = settings.market_state_path
    settings.memory_path = tmp_path / "memory.json"
    settings.market_state_path = tmp_path / "market_state.json"
    try:
        store = MemoryStore(settings.memory_path)
        agent = AutonomousAgent(memory_store=store)
        state = agent.load_state()
        monkeypatch.setattr("agent_core.agent.handle_market_command", lambda command: "mercado roteado")
        reply = agent.handle_command("mercado: carteira", state)
        assert reply == "mercado roteado"
    finally:
        settings.memory_path = original_memory_path
        settings.market_state_path = original_market_state_path


def test_load_paper_state_uses_configured_initial_cash(tmp_path: Path) -> None:
    original_market_state_path = settings.market_state_path
    original_initial_cash = settings.paper_initial_cash_brl
    settings.market_state_path = tmp_path / "market_state.json"
    settings.paper_initial_cash_brl = 12345.0
    try:
        state = load_paper_state()
        assert state.cash_brl == 12345.0
        assert state.positions == []
    finally:
        settings.market_state_path = original_market_state_path
        settings.paper_initial_cash_brl = original_initial_cash


def test_market_study_track_command_returns_guided_content() -> None:
    reply = handle_market_command("mercado: trilha iniciante")
    assert reply is not None
    lowered = reply.lower()
    assert "trilha iniciante" in lowered
    assert "reserva de emergencia" in lowered


def test_market_help_mentions_study_tracks() -> None:
    reply = handle_market_command("mercado")
    assert reply is not None
    lowered = reply.lower()
    assert "mercado: trilha iniciante" in lowered
    assert "mercado: trilha trader" in lowered