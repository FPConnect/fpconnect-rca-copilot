"""Tests for notification endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_notifications.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


def auth_headers(phone_number: str = "+55 47 99678-9861") -> dict[str, str]:
    credentials = {
        "email": "sms@example.com",
        "password": "SecurePass123",
        "full_name": "SMS User",
        "phone_number": phone_number,
    }
    client.post("/auth/register", json=credentials)
    response = client.post(
        "/auth/login",
        json={"email": credentials["email"], "password": credentials["password"]},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_send_sms_notification_success():
    headers = auth_headers()

    response = client.post(
        "/notifications/sms",
        json={"message": "FPConnect SMS test"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "sent",
        "to": "+55 47 99678-9861",
        "provider": "development-mock",
        "delivered": True,
    }


def test_send_sms_notification_requires_valid_phone():
    headers = auth_headers(phone_number="123")

    response = client.post(
        "/notifications/sms",
        json={"message": "FPConnect SMS test"},
        headers=headers,
    )

    assert response.status_code == 422
