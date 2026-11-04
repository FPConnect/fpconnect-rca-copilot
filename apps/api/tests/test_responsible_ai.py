"""Responsible AI: privacy gating, non-definitive output, and policy defaults."""

from types import SimpleNamespace

import pytest

from app.services import rca_advanced


def test_local_rca_does_not_call_external_provider_or_cache(monkeypatch):
    def no_external(*_args, **_kwargs):
        raise AssertionError("External provider must not be contacted by default")

    monkeypatch.setattr(rca_advanced, "OpenAI", no_external)
    result = rca_advanced.generate_rca("Intermittent equipment log anomaly")

    assert result["review_required"] is True
    assert result["review_status"] == "pending"
    assert result["confidence"] is None
    assert result["confidence_is_probability"] is False
    assert result["source"] == "local_no_external_processing"
    assert result["root_cause"] != "Intermittent equipment log anomaly"


def test_external_processing_requires_deployment_approval(monkeypatch):
    monkeypatch.setattr(rca_advanced.settings, "ai_external_processing_enabled", False)
    with pytest.raises(ValueError, match="disabled"):
        rca_advanced.generate_rca(
            "Technical anomaly",
            allow_external_processing=True,
            data_deidentified=True,
        )


def test_external_processing_requires_requester_deidentification_attestation(monkeypatch):
    monkeypatch.setattr(rca_advanced.settings, "ai_external_processing_enabled", True)
    with pytest.raises(ValueError, match="de-identification attestation"):
        rca_advanced.generate_rca("Technical anomaly", allow_external_processing=True)


@pytest.mark.parametrize(
    "unsafe",
    [
        "Contact patient@example.org",
        "senha=SuperSecret123!",
        "Bearer: abc.def.ghi",
        "Paciente ID: 1234",
        "CPF: 123456789",
    ],
)
def test_sensitive_content_detection(unsafe):
    assert rca_advanced.may_contain_sensitive_data(unsafe)


def test_external_processing_rejects_common_identifiers_even_with_opt_in(monkeypatch):
    monkeypatch.setattr(rca_advanced.settings, "ai_external_processing_enabled", True)
    monkeypatch.setattr(rca_advanced.settings, "openai_api_key", "sk-test-key")
    with pytest.raises(ValueError, match="sensitive"):
        rca_advanced.generate_rca(
            "A fictional technical anomaly",
            context="patient@example.org",
            allow_external_processing=True,
            data_deidentified=True,
        )


def test_external_provider_response_remains_draft_and_uncalibrated(monkeypatch):
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"hypothesis": "Review a possible log sequence mismatch", "limits": "The evidence is incomplete"}')
            )])

    class FakeClient:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(rca_advanced.settings, "ai_external_processing_enabled", True)
    monkeypatch.setattr(rca_advanced.settings, "openai_api_key", "sk-test-key")
    monkeypatch.setattr(rca_advanced, "OpenAI", FakeClient)

    result = rca_advanced.generate_rca(
        "Synthetic failure log",
        context="Non-identifiable simulated telemetry",
        allow_external_processing=True,
        data_deidentified=True,
    )

    assert result["source"] == "external_ai_draft"
    assert result["root_cause"].startswith("Unconfirmed hypothesis:")
    assert result["confidence"] is None
    assert result["review_required"] is True
    assert result["confidence_is_probability"] is False
    assert len(calls) == 2
    assert calls[1]["messages"][0]["role"] == "system"
