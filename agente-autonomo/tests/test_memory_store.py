from __future__ import annotations

import json
from pathlib import Path

from agent_core.memory import ConversationState, MAX_MESSAGES, MemoryStore


def test_load_recovers_from_corrupt_json(tmp_path: Path) -> None:
    mem_path = tmp_path / "memory.json"
    mem_path.write_text('{"messages": []}\n{"messages": []}', encoding="utf-8")

    store = MemoryStore(mem_path)
    state = store.load()

    assert state.messages == []
    backups = list(tmp_path.glob("memory.corrupt.*.json"))
    assert backups, "Expected corrupt backup file to be created"


def test_save_trims_messages_to_max(tmp_path: Path) -> None:
    mem_path = tmp_path / "memory.json"
    store = MemoryStore(mem_path)

    state = ConversationState.empty()
    for i in range(MAX_MESSAGES + 50):
        state.add("user", f"msg-{i}")

    store.save(state)
    raw = json.loads(mem_path.read_text(encoding="utf-8"))
    msgs = raw.get("messages", [])

    assert len(msgs) == MAX_MESSAGES
    assert msgs[0]["content"] == "msg-50"
    assert msgs[-1]["content"] == f"msg-{MAX_MESSAGES + 49}"


def test_save_retries_replace_when_file_is_temporarily_locked(tmp_path: Path, monkeypatch) -> None:
    mem_path = tmp_path / "memory.json"
    store = MemoryStore(mem_path)

    state = ConversationState.empty()
    state.add("user", "msg-1")

    replace_calls = {"count": 0}
    original_replace = Path.replace

    def flaky_replace(self: Path, target: Path):
        replace_calls["count"] += 1
        if replace_calls["count"] == 1:
            raise PermissionError(32, "locked")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", flaky_replace)
    monkeypatch.setattr("agent_core.memory.time.sleep", lambda _: None)

    store.save(state)

    assert replace_calls["count"] >= 2
    raw = json.loads(mem_path.read_text(encoding="utf-8"))
    assert raw["messages"][0]["content"] == "msg-1"
