from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _default_memory_path() -> Path:
    env_path = os.getenv("AGENTE_AUTONOMO_MEMORY_PATH", "").strip()
    if env_path:
        return Path(env_path).expanduser()

    home_path = Path.home() / ".agente_autonomo"
    if _is_writable_dir(home_path):
        return home_path / "memory.json"

    temp_path = Path(tempfile.gettempdir()) / "agente_autonomo"
    return temp_path / "memory.json"


@dataclass
class Settings:
    memory_path: Path = _default_memory_path()
    # Backend de planejamento; hoje o agente lê diretamente
    # AGENTE_AUTONOMO_BACKEND, mas mantemos aqui para futura extensão.
    backend: str = os.getenv("AGENTE_AUTONOMO_BACKEND", "auto").lower().strip()


settings = Settings()
