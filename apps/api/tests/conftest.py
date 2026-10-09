import os

os.environ["APP_ENV"] = "development"
os.environ["SEED_TEST_ACCOUNTS"] = "false"
os.environ["PUBLIC_REGISTRATION_ENABLED"] = "true"

# Application settings must be established before application modules are imported.
import pytest  # noqa: E402

from app.core.security import limiter  # noqa: E402


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield
