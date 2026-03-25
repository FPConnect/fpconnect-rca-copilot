from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List
import json


@dataclass
class Message:
    role: str  # "user" or "agent"
    content: str


@dataclass
class ConversationState:
    messages: List[Message]

    @classmethod
    def empty(cls) -> "ConversationState":
        return cls(messages=[])

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def last_user_message(self) -> str | None:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def summary(self, limit: int = 5) -> str:
        recent = self.messages[-limit:]
        lines = [f"{m.role}: {m.content}" for m in recent]
        return "\n".join(lines) if lines else "(sem histórico ainda)"


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> ConversationState:
        if not self.path.exists():
            return ConversationState.empty()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        messages = [Message(**m) for m in data.get("messages", [])]
        return ConversationState(messages=messages)

    def save(self, state: ConversationState) -> None:
        data = {"messages": [asdict(m) for m in state.messages]}
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
