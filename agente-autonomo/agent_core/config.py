from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MEMORY_PATH = Path.home() / ".agente_autonomo" / "memory.json"
DEFAULT_MARKET_STATE_PATH = Path.home() / ".agente_autonomo" / "market_state.json"


@dataclass
class Settings:
    memory_path: Path = DEFAULT_MEMORY_PATH
    market_state_path: Path = DEFAULT_MARKET_STATE_PATH
    # Backend de planejamento; hoje o agente lê diretamente
    # AGENTE_AUTONOMO_BACKEND, mas mantemos aqui para futura extensão.
    backend: str = os.getenv("AGENTE_AUTONOMO_BACKEND", "auto").lower().strip()
    paper_initial_cash_brl: float = float(os.getenv("AGENTE_AUTONOMO_PAPER_CASH_BRL", "10000"))
    allow_live_trading: bool = os.getenv("AGENTE_AUTONOMO_ALLOW_LIVE_TRADING", "0").strip() == "1"


settings = Settings()
