"""Tests for ticket attachment upload endpoints."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import tickets as ticket_routes
from app.core.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_attachments.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

PNG_BUFFER = BytesIO()
Image.new("RGB", (1, 1), color="white").save(PNG_BUFFER, format="PNG")
PNG_BYTES = PNG_BUFFER.getvalue()


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


def auth_headers(email: str = "upload@example.com") -> dict[str, str]:
    credentials = {"email": email, "password": "SecurePass123!"}
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
    assert response.json()["detail"] == "Image data is invalid or unsafe"


def test_regular_user_cannot_read_another_users_ticket_or_attachments():
    owner_headers = auth_headers("owner@example.com")
    ticket_id = create_ticket(owner_headers)
    other_headers = auth_headers("other@example.com")

    ticket_response = client.get(f"/tickets/{ticket_id}", headers=other_headers)
    attachment_response = client.get(f"/tickets/{ticket_id}/attachments", headers=other_headers)

    assert ticket_response.status_code == 404
    assert attachment_response.status_code == 404
