from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List
import json
import os
import tempfile
import time
from datetime import datetime


MAX_MESSAGES = 1200
SAVE_RETRIES = 5
SAVE_RETRY_DELAY_SECONDS = 0.05


@dataclass
class Message:
    role: str  # "user" | "agent" | "tool"
    content: str


@dataclass
class ConversationState:
    messages: List[Message]

    @classmethod
    def empty(cls) -> "ConversationState":
        return cls(messages=[])

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def summary(self, limit: int = 10) -> str:
        recent = self.messages[-limit:]
        lines = [f"{m.role}: {m.content}" for m in recent]
        return "\n".join(lines) if lines else "(sem histórico ainda)"


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            fallback_dir = Path(tempfile.gettempdir()) / "agente_autonomo"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            self.path = fallback_dir / self.path.name

    def load(self) -> ConversationState:
        if not self.path.exists():
            return ConversationState.empty()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            raw_messages = data.get("messages", []) if isinstance(data, dict) else []
            messages = [Message(**m) for m in raw_messages if isinstance(m, dict)]
            if len(messages) > MAX_MESSAGES:
                messages = messages[-MAX_MESSAGES:]
            return ConversationState(messages=messages)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            # Auto-recuperacao para evitar derrubar a API por arquivo corrompido.
            try:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup = self.path.with_suffix(f".corrupt.{stamp}.json")
                self.path.replace(backup)
            except OSError:
                pass
            return ConversationState.empty()

    def save(self, state: ConversationState) -> None:
        trimmed = state.messages[-MAX_MESSAGES:]
        data = {"messages": [asdict(m) for m in trimmed]}
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        tmp_path = self.path.with_name(
            f"{self.path.stem}.{os.getpid()}.{time.time_ns()}.tmp"
        )
        tmp_path.write_text(payload, encoding="utf-8")

        last_error: OSError | None = None
        for attempt in range(SAVE_RETRIES):
            try:
                tmp_path.replace(self.path)
                return
            except PermissionError as exc:
                last_error = exc
                if attempt == SAVE_RETRIES - 1:
                    break
                time.sleep(SAVE_RETRY_DELAY_SECONDS)

        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass

        if last_error is not None:
            raise last_error
