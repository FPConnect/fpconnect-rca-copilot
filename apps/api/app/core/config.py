"""Application configuration loaded from environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_env: str = "development"
    secret_key: str = "dev-only-change-this-key-32-chars!!"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    database_url: str = "sqlite:///./fpconnect.db"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = "sk-placeholder"

    @model_validator(mode="after")
    def validate_security(self):
        """Prevent insecure key defaults outside development and enforce minimum key size."""
        if self.app_env != "development" and self.secret_key == "dev-only-change-this-key-32-chars!!":
            raise ValueError("SECRET_KEY must be set to a strong value")
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return self

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
