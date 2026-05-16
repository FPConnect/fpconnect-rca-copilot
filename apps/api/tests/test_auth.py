"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
            "password": "SecurePass123!",
            "full_name": "Tech User",
            "role": "technician",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "tech@example.com"
    assert "id" in data


def test_register_duplicate_email():
    payload = {
        "email": "dup@example.com",
        "password": "SecurePass123!",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


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
