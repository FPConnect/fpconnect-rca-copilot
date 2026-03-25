"""Tests for the integrated agent API endpoint."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_chat_basic():
    response = client.post("/agent/chat", json={"message": "Oi agente"})
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert data["reply"]
    assert data.get("backend") in {"rules", "openai"}


def test_agent_ticket_analyze():
    payload = {
        "ticket": {
            "title": "Monitor offline na UTI",
            "description": "Monitor cardíaco sem sinal há 10 minutos",
            "priority": "critical",
            "status": "open",
        },
        "question": "Quais próximos passos devo seguir?",
    }
    response = client.post("/agent/tickets/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("backend") in {"rules", "openai"}
    assert isinstance(data.get("reply"), str)
    assert data["reply"]
