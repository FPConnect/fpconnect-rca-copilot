"""Tests for ticket attachment upload endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import tickets as ticket_routes
from app.core.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_attachments.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2m\x9d"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(ticket_routes, "upload_file_object", lambda **kwargs: kwargs["object_key"])
    monkeypatch.setattr(
        ticket_routes,
        "create_presigned_get_url",
        lambda object_key: f"https://storage.test/{object_key}",
    )
    yield
    Base.metadata.drop_all(bind=engine)
    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


def auth_headers() -> dict[str, str]:
    credentials = {"email": "upload@example.com", "password": "SecurePass123!"}
    client.post("/auth/register", json=credentials)
    response = client.post("/auth/login", json=credentials)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_ticket(headers: dict[str, str]) -> int:
    response = client.post(
        "/tickets/",
        json={"title": "Infusion pump leaking", "priority": "high"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_upload_ticket_image_success():
    headers = auth_headers()
    ticket_id = create_ticket(headers)

    response = client.post(
        f"/tickets/{ticket_id}/attachments/images",
        files={"file": ("pump.png", PNG_BYTES, "image/png")},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"] == ticket_id
    assert data["filename"] == "pump.png"
    assert data["content_type"] == "image/png"
    assert data["size_bytes"] == len(PNG_BYTES)
    assert data["download_url"].startswith("https://storage.test/tickets/")


def test_upload_ticket_image_rejects_non_image():
    headers = auth_headers()
    ticket_id = create_ticket(headers)

    response = client.post(
        f"/tickets/{ticket_id}/attachments/images",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 415


def test_list_ticket_attachments():
    headers = auth_headers()
    ticket_id = create_ticket(headers)
    client.post(
        f"/tickets/{ticket_id}/attachments/images",
        files={"file": ("pump.png", PNG_BYTES, "image/png")},
        headers=headers,
    )

    response = client.get(f"/tickets/{ticket_id}/attachments", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["filename"] == "pump.png"


def test_upload_ticket_image_rejects_spoofed_image_type():
    headers = auth_headers()
    ticket_id = create_ticket(headers)

    response = client.post(
        f"/tickets/{ticket_id}/attachments/images",
        files={"file": ("fake.png", b"not a real image", "image/png")},
        headers=headers,
    )

    assert response.status_code == 415
    assert "Real file type" in response.json()["detail"]
