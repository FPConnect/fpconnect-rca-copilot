"""Application configuration loaded from environment variables."""

from pydantic import field_validator
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
    intel_require_auth: bool = True
    allow_dev_anonymous_access: bool = False
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ]
    cors_origin_regex: str | None = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    # n8n integration for SLA alerts / automations
    # If not configured, related integrations become no-ops.
    n8n_sla_workflow_url: str | None = None
    n8n_sla_api_key: str | None = None
    n8n_sla_timeout_seconds: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    def validate_runtime_security(self) -> None:
        """Fail fast when unsafe production defaults are still enabled."""

        if self.app_env.lower() != "production":
            return

        normalized_origins = {origin.strip() for origin in self.cors_origins}
        if self.secret_key == "change-me-in-production" or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be unique and at least 32 characters in production.")
        if "*" in normalized_origins:
            raise ValueError("Wildcard CORS is not allowed in production.")
        if self.allow_dev_anonymous_access:
            raise ValueError("ALLOW_DEV_ANONYMOUS_ACCESS must be disabled in production.")


settings = Settings()
