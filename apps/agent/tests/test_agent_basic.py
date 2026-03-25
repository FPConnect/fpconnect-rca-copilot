from pathlib import Path

from apps.agent.agent import Agent, default_llm
from apps.agent.memory import ConversationState, MemoryStore
from apps.agent.config import Settings


def test_memory_store_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    store = MemoryStore(path)
    state = ConversationState.empty()
    state.add("user", "Oi agente")
    state.add("agent", "Olá!")

    store.save(state)
    loaded = store.load()

    assert len(loaded.messages) == 2
    assert loaded.messages[0].role == "user"
    assert loaded.messages[0].content == "Oi agente"


def test_default_llm_greeting() -> None:
    state = ConversationState.empty()
    reply = default_llm("Oi, tudo bem?", state)
    assert "Olá" in reply or "ola" in reply.lower()


def test_agent_run_turn_persists_state(tmp_path: Path) -> None:
    settings = Settings(memory_path=tmp_path / "mem.json")
    store = MemoryStore(settings.memory_path)
    state = store.load()
    agent = Agent(memory_store=store)

    reply = agent.run_turn("Quero um resumo depois", state)

    assert reply
    assert store.path.exists()
    loaded = store.load()
    assert any(m.role == "user" for m in loaded.messages)
    assert any(m.role == "agent" for m in loaded.messages)
