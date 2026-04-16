"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

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


def test_register_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "tech@example.com",
            "password": "SecurePass123",
            "full_name": "Tech User",
            "phone_number": "+55 47 99678-9861",
            "role": "technician",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "tech@example.com"
    assert data["phone_number"] == "+55 47 99678-9861"
    assert "id" in data


def test_register_duplicate_email():
    payload = {
        "email": "dup@example.com",
        "password": "SecurePass123",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_login_success():
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "SecurePass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials():
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_me_update_phone_and_sms_notification():
    client.post(
        "/auth/register",
        json={
            "email": "sms@example.com",
            "password": "SecurePass123",
            "full_name": "SMS User",
            "phone_number": "+55 47 99678-9861",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "sms@example.com", "password": "SecurePass123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_response = client.patch(
        "/auth/me",
        json={"phone_number": "+55 47 98888-7777"},
        headers=headers,
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["phone_number"] == "+55 47 98888-7777"

    sms_response = client.post(
        "/notifications/sms",
        json={"message": "Teste FPConnect"},
        headers=headers,
    )
    assert sms_response.status_code == 200
    data = sms_response.json()
    assert data["to"] == "+5547988887777"
    assert data["delivered"] is False


def test_n8n_internal_callbacks_update_and_log_ticket(monkeypatch):
    monkeypatch.setattr(settings, "n8n_sla_api_key", "test-internal-key")
    client.post(
        "/auth/register",
        json={"email": "n8n@example.com", "password": "SecurePass123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "n8n@example.com", "password": "SecurePass123"},
    )
    auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    ticket_response = client.post(
        "/tickets/",
        json={"title": "Ventilador UTI offline", "priority": "critical"},
        headers=auth_headers,
    )
    assert ticket_response.status_code == 201
    ticket_id = ticket_response.json()["id"]

    internal_headers = {"X-Internal-Key": "test-internal-key"}
    event_response = client.post(
        "/internal/n8n/sla/event",
        json={
            "ticket_id": ticket_id,
            "event_type": "n8n.critical_ticket.detected",
            "details": {"message": "n8n iniciou escalonamento."},
        },
        headers=internal_headers,
    )
    assert event_response.status_code == 200

    update_response = client.post(
        "/internal/n8n/sla/update",
        json={"ticket_id": ticket_id, "escalation_level": 1},
        headers=internal_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["changed"] is True

    refreshed = client.get(f"/tickets/{ticket_id}", headers=auth_headers)
    assert refreshed.status_code == 200
    assert refreshed.json()["escalation_level"] == 1


def test_intelligence_summary_returns_risk_governance_and_insights():
    client.post(
        "/auth/register",
        json={"email": "intel@example.com", "password": "SecurePass123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "intel@example.com", "password": "SecurePass123"},
    )
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response = client.get("/intelligence/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["asset_risks"]
    assert data["governance_checks"]
    assert data["insights"]
    assert {"code", "risk_score", "risk_level", "drivers"}.issubset(data["asset_risks"][0])


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
