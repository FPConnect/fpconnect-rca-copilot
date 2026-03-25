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

    # Intel/Radar feature (public sources). Keep auth optional for MVP.
    intel_sources_path: str = "app/intel/sources.yaml"
    intel_default_limit: int = 50
    intel_require_auth: bool = False

    # n8n integration for SLA alerts / automations
    # If not configured, related integrations become no-ops.
    n8n_sla_workflow_url: str | None = None
    n8n_sla_api_key: str | None = None
    n8n_sla_timeout_seconds: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
