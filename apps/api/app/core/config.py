"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_env: str = "development"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    database_url: str = "sqlite:///./fpconnect.db"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = "sk-placeholder"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
