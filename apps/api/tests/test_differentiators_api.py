"""Tests for differentiator module endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_risk_radar_endpoint_returns_asset_level_risk():
    response = client.get("/differentiators/risk-radar")

    assert response.status_code == 200
    data = response.json()
    assert data
    assert data[0]["overall_risk"] >= 0
    assert data[0]["signals"]
    assert data[0]["recommended_actions"]


def test_evidence_copilot_endpoint_returns_rca_package():
    response = client.get("/differentiators/evidence-copilot")

    assert response.status_code == 200
    data = response.json()
    assert data
    assert data[0]["probable_cause"]
    assert data[0]["evidence"]
    assert data[0]["oem_message"]


def test_value_engine_endpoint_returns_roi_narrative():
    response = client.get("/differentiators/value-engine")

    assert response.status_code == 200
    data = response.json()
    assert data
    assert data[0]["avoided_loss_brl"] > 0
    assert data[0]["recommended_offer"]
    assert data[0]["board_questions"]
