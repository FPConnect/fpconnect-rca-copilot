from pathlib import Path


APP_NAME = "MeuAgenteIA"
DEFAULT_MEMORY_PATH = Path.home() / ".meu_agente_ia" / "memory.json"


class Settings:
    def __init__(self, memory_path: Path | None = None) -> None:
        self.app_name = APP_NAME
        self.memory_path = memory_path or DEFAULT_MEMORY_PATH


settings = Settings()
