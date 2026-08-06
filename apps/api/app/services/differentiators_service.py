"""Demo data for FPConnect high-differentiation modules.

The data is intentionally deterministic for demos. Production can replace these
providers with FDA/openFDA, Anvisa, AccessGUDID, CISA, NVD, MDS2/SBOM and
internal ticket/manual indexes without changing the API contract.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


RISK_RADAR_ASSETS: list[dict[str, Any]] = [
    {
        "id": "UTI-VENT-02",
        "name": "Ventilador Servo-U",
        "location": "UTI Adulto Leito 2",
        "manufacturer": "Maquet/Getinge",
        "model": "Servo-U",
        "udi": "(01)07350012345678(21)SU-UTI-02",
        "firmware": "4.3.1",
        "clinical_criticality": "life-support",
        "overall_risk": 91,
        "recall_risk": 82,
        "cyber_risk": 74,
        "regulatory_risk": 88,
        "downtime_impact_brl": 98000,
        "status": "action_required",
        "signals": [
            {
                "source": "FDA/openFDA",
                "type": "recall",
                "severity": "high",
                "title": "Recall family match for ventilator pressure sensor drift",
                "published_at": "2026-07-18",
                "evidence": "Model family and firmware range overlap with a pressure-sensor corrective action.",
            },
            {
                "source": "CISA KEV/NVD",
                "type": "cyber",
                "severity": "medium",
                "title": "Network service exposed on legacy firmware baseline",
                "published_at": "2026-07-04",
                "evidence": "Firmware is below the hardened baseline defined in the internal device profile.",
            },
        ],
        "recommended_actions": [
            "Open a supplier-backed corrective ticket and attach UDI, firmware and telemetry snapshot.",
            "Move a backup ventilator to the UTI before firmware validation.",
            "Create an audit record linking recall, cyber baseline and RCA evidence.",
        ],
        "audit_packet": "Ready for biomedical engineering, quality and OEM follow-up.",
    },
    {
        "id": "DEF-ER-01",
        "name": "Desfibrilador Zoll",
        "location": "Emergencia",
        "manufacturer": "Zoll",
        "model": "R Series",
        "udi": "(01)00847946000011(21)DEF-ER-01",
        "firmware": "2.18",
        "clinical_criticality": "life-support",
        "overall_risk": 87,
        "recall_risk": 78,
        "cyber_risk": 42,
        "regulatory_risk": 90,
        "downtime_impact_brl": 124000,
        "status": "action_required",
        "signals": [
            {
                "source": "AccessGUDID",
                "type": "udi",
                "severity": "medium",
                "title": "UDI profile requires battery accessory verification",
                "published_at": "2026-06-28",
                "evidence": "Configured battery accessory does not match the preferred emergency stock profile.",
            },
            {
                "source": "Internal PM",
                "type": "regulatory",
                "severity": "critical",
                "title": "Autotest failure on emergency defibrillator",
                "published_at": "2026-08-02",
                "evidence": "Autotest failed and no replacement record was attached to the incident.",
            },
        ],
        "recommended_actions": [
            "Remove from clinical rotation until autotest evidence is attached.",
            "Validate battery lot, accessory compatibility and next PM date.",
            "Notify emergency coordinator with replacement status and ETA.",
        ],
        "audit_packet": "Ready for quality event review and emergency readiness meeting.",
    },
]


EVIDENCE_COPILOT_CASES: list[dict[str, Any]] = [
    {
        "id": "RCA-4102",
        "ticket_title": "Ventilador com oscilacao em UTI",
        "asset_id": "UTI-VENT-02",
        "asset_name": "Ventilador Servo-U",
        "symptom": "Oscilacao de pressao inspiratoria em leito critico, com dois eventos semelhantes no mes.",
        "probable_cause": "Falha intermitente em sensor de fluxo associada a firmware abaixo do baseline recomendado.",
        "confidence": 87,
        "containment_steps": [
            "Conferir paciente/equipamento backup antes de qualquer ajuste tecnico.",
            "Executar autoteste e capturar log de pressao inspiratoria.",
            "Validar sensor de fluxo, circuito, filtro e firmware instalado.",
            "Acionar OEM com pacote UDI + log + historico de recorrencia FPConnect.",
        ],
        "guided_questions": [
            "A oscilacao ocorre apenas com circuito especifico ou em qualquer circuito?",
            "O autoteste falha antes ou depois da troca do sensor?",
            "Existe alerta externo ou boletim aplicavel ao mesmo modelo/firmware?",
        ],
        "evidence": [
            {
                "label": "Manual tecnico Servo-U",
                "type": "manual",
                "excerpt": "Pressure instability should be investigated through flow sensor validation, circuit leak test and event log review.",
                "confidence_impact": "+22 pontos por compatibilidade direta com o sintoma.",
            },
            {
                "label": "Historico FPConnect",
                "type": "history",
                "excerpt": "2 tickets similares em 30 dias na UTI adulto com resolucao apos troca de sensor e atualizacao de firmware.",
                "confidence_impact": "+18 pontos por recorrencia operacional.",
            },
        ],
        "oem_message": (
            "Solicitamos avaliacao tecnica para UTI-VENT-02. Sintoma: oscilacao de pressao "
            "inspiratoria. Anexos: UDI, firmware 4.3.1, log de evento, autoteste e historico."
        ),
        "capa_draft": (
            "Contencao: backup em leito critico. Causa provavel: sensor de fluxo/firmware. "
            "Acao corretiva: validar sensor, atualizar firmware e revisar ativos similares."
        ),
    },
    {
        "id": "RCA-4103",
        "ticket_title": "Desfibrilador sem autoteste valido",
        "asset_id": "DEF-ER-01",
        "asset_name": "Desfibrilador Zoll",
        "symptom": "Autoteste falhou em equipamento de emergencia sem evidencia de substituicao anexada.",
        "probable_cause": "Bateria interna fora da faixa ou acessorio incompatavel com o perfil UDI aprovado.",
        "confidence": 82,
        "containment_steps": [
            "Retirar equipamento da escala e registrar substituto operacional.",
            "Testar bateria, cabos, pas e fonte AC.",
            "Comparar lote de bateria com perfil de acessorios aprovado.",
            "Anexar evidencia de autoteste antes de liberar para uso.",
        ],
        "guided_questions": [
            "Qual codigo de falha foi exibido no autoteste?",
            "A bateria atual corresponde ao lote aprovado para este modelo?",
            "Existe registro de troca recente sem fechamento de evidencia?",
        ],
        "evidence": [
            {
                "label": "Checklist emergencia",
                "type": "checklist",
                "excerpt": "Equipamento de suporte a vida com autoteste invalido deve ter substituto documentado.",
                "confidence_impact": "+20 pontos por regra de seguranca clinica.",
            }
        ],
        "oem_message": (
            "Solicitamos suporte para DEF-ER-01. Autoteste invalido em emergencia. "
            "Enviamos codigo de falha, UDI, lote de bateria, acessorios e substituicao."
        ),
        "capa_draft": (
            "Contencao: substituto documentado. Causa provavel: bateria/acessorio. "
            "Acao corretiva: troca validada, autoteste anexado e revisao de estoque."
        ),
    },
]


VALUE_ENGINE_SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "executive-renewal",
        "client_profile": "Hospital terciario com UTI, emergencia e centro cirurgico",
        "period": "Ultimos 30 dias",
        "protected_assets": 47,
        "avoided_downtime_hours": 61,
        "avoided_loss_brl": 612000,
        "renewal_expansion_brl": 438700,
        "renewal_risk": "low",
        "recommended_offer": "Renovar contrato premium com Risk Radar + RCA Copilot + pacote mensal executivo.",
        "executive_narrative": (
            "O FPConnect deixou de ser apenas controle de chamados: ele protegeu disponibilidade "
            "de ativos criticos, reduziu tempo de resposta e gerou evidencias para diretoria."
        ),
        "levers": [
            {
                "label": "Downtime evitado",
                "value": "61 h",
                "detail": "Baseado em incidentes criticos contidos antes de indisponibilidade prolongada.",
            },
            {
                "label": "Perda evitada",
                "value": "R$ 612 mil",
                "detail": "Estimativa combinando agenda protegida, substituicao preventiva e suporte a vida.",
            },
        ],
        "board_questions": [
            "Quanto custaria uma hora sem ventilador, desfibrilador ou sala cirurgica?",
            "Qual evidencia prova que a engenharia clinica reduziu risco assistencial?",
            "Quais contratos devem ser expandidos antes da proxima auditoria?",
        ],
    },
    {
        "id": "diagnostic-network",
        "client_profile": "Rede de diagnostico por imagem e laboratorio",
        "period": "Ultimos 30 dias",
        "protected_assets": 16,
        "avoided_downtime_hours": 34,
        "avoided_loss_brl": 301000,
        "renewal_expansion_brl": 219400,
        "renewal_risk": "medium",
        "recommended_offer": "Expandir cobertura para cadeia fria, imagem e integracao de agenda.",
        "executive_narrative": (
            "O maior valor esta em preservar agenda e cadeia fria com health checks, alertas e RCA."
        ),
        "levers": [
            {
                "label": "Agenda protegida",
                "value": "12 exames",
                "detail": "Alertas antecipados permitiram redistribuir capacidade antes da parada.",
            },
            {
                "label": "Cadeia fria",
                "value": "R$ 76 mil",
                "detail": "Risco em reagentes e amostras contido por resposta rapida.",
            },
        ],
        "board_questions": [
            "Quais unidades geram maior perda por indisponibilidade?",
            "Quais ativos deveriam entrar primeiro no contrato preditivo?",
            "Como provar reducao de remarcacao para a diretoria regional?",
        ],
    },
]


def get_risk_radar_assets() -> list[dict[str, Any]]:
    return deepcopy(RISK_RADAR_ASSETS)


def get_evidence_copilot_cases() -> list[dict[str, Any]]:
    return deepcopy(EVIDENCE_COPILOT_CASES)


def get_value_engine_scenarios() -> list[dict[str, Any]]:
    return deepcopy(VALUE_ENGINE_SCENARIOS)
