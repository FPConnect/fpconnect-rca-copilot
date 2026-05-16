"""Tests for clinical engineering workflows."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import analyze as analyze_routes
from app.core.database import Base, get_db
from app.main import app
from app.models.machine import Machine
from app.services.clinical_metrics import calculate_equipment_criticality

TEST_DB_URL = "sqlite:///./test_clinical.db"

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
def setup_db(monkeypatch):
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(
        analyze_routes,
        "analyze_ticket",
        lambda db, ticket, request: [
            SimpleNamespace(
                cause="Sensor SpO2 com cabo intermitente",
                confidence=0.91,
                resolution="Trocar cabo, validar curva e registrar teste funcional.",
            )
        ],
    )
    yield
    Base.metadata.drop_all(bind=engine)
    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override


def auth_headers() -> dict[str, str]:
    credentials = {"email": "clinical@example.com", "password": "SecurePass123!"}
    credentials = {"email": "clinical@example.com", "password": "SecurePass123"}
    client.post("/auth/register", json=credentials)
    response = client.post("/auth/login", json=credentials)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_incident(headers: dict[str, str]) -> int:
    response = client.post(
        "/tickets/",
        json={
            "title": "Monitor multiparamétrico perde leitura de SpO2",
            "description": "Falha intermitente na UTI Adulto",
            "priority": "critical",
            "device_id": "ECG-02",
            "location": "UTI Adulto",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_analyze_endpoint_persists_root_cause():
    headers = auth_headers()
    ticket_id = create_incident(headers)

    response = client.post("/analyze", json={"ticket_id": ticket_id}, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["root_cause"] == "Sensor SpO2 com cabo intermitente"
    assert data["recommendation"] == "Trocar cabo, validar curva e registrar teste funcional."

    ticket_response = client.get(f"/tickets/{ticket_id}", headers=headers)
    assert ticket_response.json()["root_cause"] == "Sensor SpO2 com cabo intermitente"
    assert ticket_response.json()["analysis_completed"] is not None


def test_playbook_crud():
    headers = auth_headers()
    payload = {
        "title": "Revalidar ventilador pulmonar",
        "equipment": "Ventilador Pulmonar",
        "steps": "1. Rodar autoteste\n2. Conferir sensores\n3. Registrar liberação",
        "files": "checklist-ventilador.pdf",
    }

    created = client.post("/playbooks/", json=payload, headers=headers)
    assert created.status_code == 201
    playbook_id = created.json()["id"]

    listed = client.get("/playbooks/?search=ventilador", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/playbooks/{playbook_id}",
        json={"title": "Revalidar ventilador após falha"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Revalidar ventilador após falha"

    deleted = client.delete(f"/playbooks/{playbook_id}", headers=headers)
    assert deleted.status_code == 204


def test_equipment_criticality_calculation():
    assert calculate_equipment_criticality(
        status="offline", recurrent_failures=0, base_criticality="Baixa"
    ) == "Alta"
    assert calculate_equipment_criticality(
        status="online", recurrent_failures=3, base_criticality="Média"
    ) == "Alta"
    assert calculate_equipment_criticality(
        status="online", recurrent_failures=0, base_criticality="Baixa"
    ) == "Baixa"


def test_machine_schema_includes_clinical_fields():
    headers = auth_headers()
    db = TestingSessionLocal()
    db.add(
        Machine(
            code="AUTO-01",
            name="Autoclave",
            model="Steris 400",
            location="CME",
            type="sterilization",
            status="warning",
            criticality="Média",
            last_failure="Falha de ciclo Bowie-Dick",
            recurrent_failures=2,
        )
    )
    db.commit()
    db.close()

    response = client.get("/machines/", headers=headers)
    assert response.status_code == 200
    data = response.json()[0]
    assert data["criticality"] == "Média"
    assert data["recurrent_failures"] == 2
