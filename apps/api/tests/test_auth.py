"""Tests for authentication endpoints."""

import base64
import hashlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import hash_password, verify_password
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
    preserved = (
        db.query(User).filter(User.email == "long-legacy-admin@example.com").one()
    )
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
    assert response.json()["refresh_token"]


def test_change_password_replaces_credentials():
    email = "password-change@example.com"
    current_password = "SecurePass123!"
    new_password = "NewSecurePass456!"
    client.post("/auth/register", json={"email": email, "password": current_password})
    login_response = client.post(
        "/auth/login", json={"email": email, "password": current_password}
    )
    token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": current_password, "new_password": new_password},
    )

    assert response.status_code == 200
    assert (
        client.post("/auth/refresh", json={"refresh_token": refresh_token}).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login", json={"email": email, "password": current_password}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login", json={"email": email, "password": new_password}
        ).status_code
        == 200
    )


def test_change_password_rejects_wrong_current_password():
    email = "wrong-current@example.com"
    password = "SecurePass123!"
    client.post("/auth/register", json={"email": email, "password": password})
    token = client.post(
        "/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]

    response = client.post(
        "/auth/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass456!",
        },
    )

    assert response.status_code == 400


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
        json={
            "email": "production-verify@example.com",
            "phone_number": "+55 51 98510-2172",
        },
    )

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "SMS verification is not configured for this deployment"
    )


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


def _create_privileged_user(email: str, role: str, access_level: int) -> str:
    password = "SecurePass123!"
    db = TestingSessionLocal()
    db.add(
        User(
            email=email,
            hashed_password=hash_password(password),
            role=role,
            access_level=access_level,
            is_active=True,
        )
    )
    db.commit()
    db.close()
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_master_can_create_admin_and_list_real_users():
    token = _create_privileged_user("master@example.com", "master", 5)
    response = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "new-admin@example.com",
            "password": "AdminSecure123!",
            "full_name": "New Admin",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "admin"
    assert response.json()["access_level"] == 4
    assert response.json()["is_active"] is True
    listed = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert {account["email"] for account in listed.json()} == {
        "master@example.com",
        "new-admin@example.com",
    }


def test_admin_can_create_manager_but_not_another_admin():
    token = _create_privileged_user("admin@example.com", "admin", 4)
    manager = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "manager@example.com",
            "password": "ManagerSecure123!",
            "role": "manager",
        },
    )
    peer = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "peer-admin@example.com",
            "password": "AdminSecure123!",
            "role": "admin",
        },
    )

    assert manager.status_code == 201
    assert manager.json()["access_level"] == 3
    assert peer.status_code == 403


def test_manager_cannot_access_user_administration_or_inject_access_level():
    manager_token = _create_privileged_user("manager@example.com", "manager", 3)
    assert (
        client.get(
            "/users", headers={"Authorization": f"Bearer {manager_token}"}
        ).status_code
        == 403
    )

    master_token = _create_privileged_user("master@example.com", "master", 5)
    injected = client.post(
        "/users",
        headers={"Authorization": f"Bearer {master_token}"},
        json={
            "email": "injected@example.com",
            "password": "InjectedSecure123!",
            "role": "visitor",
            "access_level": 5,
        },
    )
    assert injected.status_code == 422


def test_deactivation_revokes_existing_tokens_and_blocks_login():
    master_token = _create_privileged_user("master@example.com", "master", 5)
    user_password = "UserSecure123!"
    created = client.post(
        "/users",
        headers={"Authorization": f"Bearer {master_token}"},
        json={"email": "user@example.com", "password": user_password, "role": "user"},
    ).json()
    user_token = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": user_password},
    ).json()["access_token"]

    deactivated = client.patch(
        f"/users/{created['id']}",
        headers={"Authorization": f"Bearer {master_token}"},
        json={"is_active": False},
    )

    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
    assert (
        client.get(
            "/auth/me", headers={"Authorization": f"Bearer {user_token}"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": user_password},
        ).status_code
        == 401
    )


def test_role_change_recalculates_level_and_revokes_old_token():
    master_token = _create_privileged_user("master@example.com", "master", 5)
    admin_token = _create_privileged_user("admin@example.com", "admin", 4)
    db = TestingSessionLocal()
    admin = db.query(User).filter(User.email == "admin@example.com").one()
    admin_id = admin.id
    db.close()

    updated = client.patch(
        f"/users/{admin_id}",
        headers={"Authorization": f"Bearer {master_token}"},
        json={"role": "manager"},
    )

    assert updated.status_code == 200
    assert updated.json()["role"] == "manager"
    assert updated.json()["access_level"] == 3
    assert (
        client.get(
            "/users", headers={"Authorization": f"Bearer {admin_token}"}
        ).status_code
        == 401
    )


def test_admin_cannot_modify_master_or_its_own_access():
    master_token = _create_privileged_user("master@example.com", "master", 5)
    admin_token = _create_privileged_user("admin@example.com", "admin", 4)
    db = TestingSessionLocal()
    master_id = db.query(User).filter(User.email == "master@example.com").one().id
    admin_id = db.query(User).filter(User.email == "admin@example.com").one().id
    db.close()

    master_update = client.patch(
        f"/users/{master_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )
    self_update = client.patch(
        f"/users/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "manager"},
    )

    assert master_update.status_code == 403
    assert self_update.status_code == 403
    assert (
        client.get(
            "/users", headers={"Authorization": f"Bearer {master_token}"}
        ).status_code
        == 200
    )


def test_visitor_is_read_only_for_operational_actions():
    master_token = _create_privileged_user("master@example.com", "master", 5)
    visitor_password = "VisitorSecure123!"
    created = client.post(
        "/users",
        headers={"Authorization": f"Bearer {master_token}"},
        json={
            "email": "visitor@example.com",
            "password": visitor_password,
            "role": "visitor",
        },
    )
    assert created.status_code == 201
    visitor_token = client.post(
        "/auth/login",
        json={"email": "visitor@example.com", "password": visitor_password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {visitor_token}"}

    assert client.get("/tickets", headers=headers).status_code == 200
    assert (
        client.post(
            "/tickets",
            headers=headers,
            json={"title": "Unauthorized write", "priority": "low"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/enterprise/rca",
            headers=headers,
            json={"problem": "Unauthorized RCA"},
        ).status_code
        == 403
    )
