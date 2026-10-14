"""Tests for authentication endpoints."""

import base64
import hashlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import verify_password
from app.main import app
from app.models.user import User

# Use an in-memory SQLite database for tests
TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def legacy_pbkdf2_sha256(password: str, rounds: int = 29_000) -> str:
    """Create the legacy Passlib-compatible format for migration tests."""
    salt = b"legacy-test-salt"
    checksum = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)

    def adapted_base64(value: bytes) -> str:
        return base64.b64encode(value).decode().rstrip("=").replace("+", ".")

    return f"$pbkdf2-sha256${rounds}${adapted_base64(salt)}${adapted_base64(checksum)}"


def test_register_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "tech@example.com",
            "password": "SecurePass123!",
            "full_name": "Tech User",
            "role": "technician",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "tech@example.com"
    assert data["role"] == "user"
    assert data["access_level"] == 2
    assert "id" in data


def test_register_duplicate_email():
    payload = {
        "email": "dup@example.com",
        "password": "SecurePass123!",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_register_is_blocked_when_public_registration_is_disabled(monkeypatch):
    monkeypatch.setattr(settings, "public_registration_enabled", False)
    response = client.post(
        "/auth/register",
        json={"email": "blocked@example.com", "password": "SecurePass123!"},
    )
    assert response.status_code == 403


def test_register_respects_email_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "registration_allowed_emails", ["owner@example.com"])

    blocked = client.post(
        "/auth/register",
        json={"email": "other@example.com", "password": "SecurePass123!"},
    )
    allowed = client.post(
        "/auth/register",
        json={"email": "Owner@Example.com", "password": "SecurePass123!"},
    )

    assert blocked.status_code == 403
    assert allowed.status_code == 201
    assert allowed.json()["email"] == "owner@example.com"


def test_login_success():
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "SecurePass123!"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "SecurePass123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials():
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_with_malformed_hash_returns_unauthorized():
    db = TestingSessionLocal()
    db.add(
        User(
            email="broken-hash@example.com",
            hashed_password="not-a-valid-password-hash",
            role="admin",
            access_level=4,
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/auth/login",
        json={"email": "broken-hash@example.com", "password": "AnyPassword123!"},
    )

    assert response.status_code == 401


def test_login_migrates_legacy_pbkdf2_hash_to_bcrypt():
    password = "LegacyAdmin123!"
    db = TestingSessionLocal()
    db.add(
        User(
            email="legacy-admin@example.com",
            hashed_password=legacy_pbkdf2_sha256(password),
            role="admin",
            access_level=4,
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/auth/login",
        json={"email": "legacy-admin@example.com", "password": password},
    )

    assert response.status_code == 200
    db = TestingSessionLocal()
    migrated = db.query(User).filter(User.email == "legacy-admin@example.com").one()
    assert migrated.hashed_password.startswith("$2")
    assert verify_password(password, migrated.hashed_password)
    db.close()


def test_login_preserves_long_legacy_pbkdf2_password():
    password = "LongLegacy1!" + ("x" * 80)
    db = TestingSessionLocal()
    db.add(
        User(
            email="long-legacy-admin@example.com",
            hashed_password=legacy_pbkdf2_sha256(password),
            role="admin",
            access_level=4,
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/auth/login",
        json={"email": "long-legacy-admin@example.com", "password": password},
    )

    assert response.status_code == 200
    db = TestingSessionLocal()
    preserved = db.query(User).filter(User.email == "long-legacy-admin@example.com").one()
    assert preserved.hashed_password.startswith("$pbkdf2-sha256$")
    assert verify_password(password, preserved.hashed_password)
    db.close()


def test_register_normalizes_email_case():
    response = client.post(
        "/auth/register",
        json={"email": "Case.User@Example.com", "password": "SecurePass123!"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "case.user@example.com"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_refresh_token_success():
    client.post(
        "/auth/register",
        json={"email": "refresh@example.com", "password": "SecurePass123!"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "refresh@example.com", "password": "SecurePass123!"},
    )
    refresh = login_response.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh})

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["refresh_token"] == refresh


def test_send_verification_code_success():
    response = client.post(
        "/auth/verification-code",
        json={"email": "verify@example.com", "phone_number": "+55 51 98510-2172"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "generated"
    assert data["to"] == "***2172"
    assert data["provider"] == "development-mock"
    assert data["verification_code"]
    assert len(data["verification_code"]) == 6
    assert data["verification_code"].isdigit()


def test_send_verification_code_fails_when_sms_is_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    response = client.post(
        "/auth/verification-code",
        json={"email": "production-verify@example.com", "phone_number": "+55 51 98510-2172"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "SMS verification is not configured for this deployment"


def test_register_with_verification_code_success():
    code_response = client.post(
        "/auth/verification-code",
        json={"email": "verified@example.com", "phone_number": "+55 51 98510-2172"},
    )
    code = code_response.json()["verification_code"]

    response = client.post(
        "/auth/register/verify",
        json={
            "email": "verified@example.com",
            "password": "SecurePass123!",
            "full_name": "Verified User",
            "phone_number": "+55 51 98510-2172",
            "verification_code": code,
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "verified@example.com"
    assert response.json()["phone_number"] == "+55 51 98510-2172"


def test_register_with_invalid_verification_code_fails():
    client.post(
        "/auth/verification-code",
        json={"email": "invalid-code@example.com", "phone_number": "+55 51 98510-2172"},
    )

    response = client.post(
        "/auth/register/verify",
        json={
            "email": "invalid-code@example.com",
            "password": "SecurePass123!",
            "full_name": "Invalid Code",
            "phone_number": "+55 51 98510-2172",
            "verification_code": "000000",
        },
    )

    assert response.status_code == 400
