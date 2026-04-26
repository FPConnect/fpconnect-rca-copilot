from __future__ import annotations

from fastapi.testclient import TestClient

from web import server as server_module
from web.server import app


def test_healthz_reports_ok() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_cloud_providers_returns_statuses(monkeypatch) -> None:
    monkeypatch.setattr(
        server_module,
        "list_cloud_provider_statuses",
        lambda: [
            {
                "provider": "google",
                "label": "Google Drive",
                "configured": True,
                "connected": False,
                "account_label": "",
                "account_email": "",
                "expires_at": 0,
                "redirect_uri": "https://agent.example.com/api/cloud/oauth/google/callback",
            }
        ],
    )
    client = TestClient(app)
    response = client.get("/api/cloud/providers")
    assert response.status_code == 200
    assert response.json()["providers"][0]["provider"] == "google"


def test_post_cloud_oauth_start_uses_request_base_url_by_default(monkeypatch) -> None:
    monkeypatch.delenv("AGENTE_AUTONOMO_PUBLIC_BASE_URL", raising=False)
    captured: dict[str, str | None] = {}

    def fake_start_cloud_oauth(provider: str, base_url: str | None = None) -> str:
        captured["provider"] = provider
        captured["base_url"] = base_url
        return "https://oauth.example.com/start"

    monkeypatch.setattr(server_module, "start_cloud_oauth", fake_start_cloud_oauth)
    client = TestClient(app, base_url="https://agent.example.com")
    response = client.post("/api/cloud/oauth/google/start")
    assert response.status_code == 200
    assert captured == {"provider": "google", "base_url": "https://agent.example.com"}
    assert response.json()["auth_url"] == "https://oauth.example.com/start"


def test_post_cloud_oauth_start_prefers_explicit_public_base_url(monkeypatch) -> None:
    monkeypatch.setenv("AGENTE_AUTONOMO_PUBLIC_BASE_URL", "https://painel.seudominio.com")
    captured: dict[str, str | None] = {}

    def fake_start_cloud_oauth(provider: str, base_url: str | None = None) -> str:
        captured["provider"] = provider
        captured["base_url"] = base_url
        return "https://oauth.example.com/start"

    monkeypatch.setattr(server_module, "start_cloud_oauth", fake_start_cloud_oauth)
    client = TestClient(app, base_url="https://interno.local")
    response = client.post("/api/cloud/oauth/onedrive/start")
    assert response.status_code == 200
    assert captured == {"provider": "onedrive", "base_url": "https://painel.seudominio.com"}


def test_cloud_callback_redirects_back_to_chat_on_success(monkeypatch) -> None:
    monkeypatch.setenv("AGENTE_AUTONOMO_PUBLIC_BASE_URL", "https://agente.seudominio.com")
    monkeypatch.setattr(server_module, "complete_cloud_oauth", lambda provider, code, state: {"provider": provider})
    client = TestClient(app)
    response = client.get(
        "/api/cloud/oauth/google/callback?code=abc&state=xyz",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "https://agente.seudominio.com/?cloud_provider=google&cloud_status=connected"


def test_cloud_callback_redirects_back_to_chat_on_error(monkeypatch) -> None:
    client = TestClient(app)
    response = client.get(
        "/api/cloud/oauth/onedrive/callback?error=access_denied&error_description=Usuario+cancelou",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/?cloud_provider=onedrive&cloud_status=error")
