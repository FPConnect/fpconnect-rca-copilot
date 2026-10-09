import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_is_the_default_and_test_account_seeding_is_disabled(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    settings = Settings(app_env="development")

    assert settings.seed_test_accounts is False
    assert settings.test_account_password is None

    settings = Settings(
        _env_file=None,
        secret_key="prod-secret-key-that-is-long-enough",
        refresh_secret_key="prod-refresh-key-that-is-long-enough",
        cors_origins=["https://fpconnect.tec.br"],
    )
    assert settings.app_env == "production"
    assert settings.seed_test_accounts is False


def test_test_account_seeding_requires_development_and_a_strong_password():
    with pytest.raises(ValidationError, match="SEED_TEST_ACCOUNTS can only be enabled in development"):
        Settings(
            app_env="production",
            secret_key="prod-secret-key-that-is-long-enough",
            refresh_secret_key="prod-refresh-key-that-is-long-enough",
            cors_origins=["https://fpconnect.tec.br"],
            seed_test_accounts=True,
            test_account_password="long-enough-password",
        )


def test_production_rejects_insecure_cors_origins():
    with pytest.raises(ValidationError, match="must use HTTPS"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="prod-secret-key-that-is-long-enough",
            refresh_secret_key="prod-refresh-key-that-is-long-enough",
            cors_origins=["http://localhost:3000"],
        )

    with pytest.raises(ValidationError, match="TEST_ACCOUNT_PASSWORD must be at least 12 characters"):
        Settings(
            app_env="development",
            seed_test_accounts=True,
            test_account_password="short",
        )
