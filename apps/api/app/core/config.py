"""Application configuration loaded from environment variables."""

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "production"
    secret_key: str = "dev-only-change-this-key-32-chars!!"
    algorithm: str = "HS256"
    jwt_issuer: str = "opspecta-api"
    jwt_audience: str = "opspecta-app"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    refresh_secret_key: str = "dev-only-refresh-key-32-chars!!!"
    seed_test_accounts: bool = False
    test_account_password: str | None = None
    public_registration_enabled: bool = False

    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    database_url: str = "sqlite:///./fpconnect.db"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = "sk-placeholder"

    s3_endpoint_url: str = Field(
        default="http://localhost:9000",
        validation_alias=AliasChoices("S3_ENDPOINT_URL", "MINIO_ENDPOINT"),
    )
    s3_access_key_id: str = Field(
        default="minioadmin",
        validation_alias=AliasChoices("S3_ACCESS_KEY_ID", "MINIO_ACCESS_KEY"),
    )
    s3_secret_access_key: str = Field(
        default="minioadmin",
        validation_alias=AliasChoices("S3_SECRET_ACCESS_KEY", "MINIO_SECRET_KEY"),
    )
    s3_bucket_name: str = Field(
        default="fpconnect-ticket-attachments",
        validation_alias=AliasChoices("S3_BUCKET_NAME", "MINIO_BUCKET"),
    )
    s3_region: str = "us-east-1"
    s3_presigned_url_expire_seconds: int = 3600
    max_upload_size_bytes: int = 5 * 1024 * 1024

    @model_validator(mode="after")
    def validate_security(self):
        """Prevent insecure key defaults outside development and enforce minimum key size."""
        if self.seed_test_accounts:
            if self.app_env != "development":
                raise ValueError("SEED_TEST_ACCOUNTS can only be enabled in development")
            if not self.test_account_password or len(self.test_account_password) < 12:
                raise ValueError("TEST_ACCOUNT_PASSWORD must be at least 12 characters when seeding test accounts")
        if self.app_env != "development" and self.secret_key == "dev-only-change-this-key-32-chars!!":
            raise ValueError("SECRET_KEY must be set to a strong value")
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if self.app_env != "development" and self.refresh_secret_key == "dev-only-refresh-key-32-chars!!!":
            raise ValueError("REFRESH_SECRET_KEY must be set to a strong value")
        if len(self.refresh_secret_key) < 32:
            raise ValueError("REFRESH_SECRET_KEY must be at least 32 characters long")
        if self.algorithm != "HS256":
            raise ValueError("ALGORITHM must be HS256")
        if not self.jwt_issuer.strip() or not self.jwt_audience.strip():
            raise ValueError("JWT_ISSUER and JWT_AUDIENCE must not be empty")
        if any(origin == "*" for origin in self.cors_origins):
            raise ValueError("CORS_ORIGINS must not contain a wildcard")
        if self.app_env != "development" and any(not origin.startswith("https://") for origin in self.cors_origins):
            raise ValueError("Production CORS origins must use HTTPS")
        return self

settings = Settings()
