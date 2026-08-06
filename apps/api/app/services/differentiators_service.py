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
                "title": "Família do equipamento compatível com recall por desvio no sensor de pressão",
                "published_at": "2026-07-18",
                "evidence": "Família do modelo e faixa de firmware coincidem com ação corretiva de sensor de pressão.",
            },
            {
                "source": "CISA KEV/NVD",
                "type": "cyber",
                "severity": "medium",
                "title": "Serviço de rede exposto em firmware legado",
                "published_at": "2026-07-04",
                "evidence": "Firmware abaixo da linha de base reforçada definida no perfil interno do equipamento.",
            },
        ],
        "recommended_actions": [
            "Abrir chamado corretivo com o fornecedor e anexar UDI, firmware e recorte de telemetria.",
            "Mover um ventilador reserva para a UTI antes da validação do firmware.",
            "Criar registro de auditoria vinculando recall, linha de base cibernética e evidências de RCA.",
        ],
        "audit_packet": "Pronto para engenharia clínica, qualidade e acompanhamento com o fabricante.",
    },
    {
        "id": "DEF-ER-01",
        "name": "Desfibrilador Zoll",
        "location": "Emergência",
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
                "title": "Perfil UDI exige verificação do acessório de bateria",
                "published_at": "2026-06-28",
                "evidence": "A bateria configurada não corresponde ao perfil preferencial de estoque da emergência.",
            },
            {
                "source": "Manutenção preventiva interna",
                "type": "regulatory",
                "severity": "critical",
                "title": "Falha no autoteste do desfibrilador de emergência",
                "published_at": "2026-08-02",
                "evidence": "Autoteste falhou e nenhum registro de substituição foi anexado ao incidente.",
            },
        ],
        "recommended_actions": [
            "Retirar da escala clínica até que a evidência do autoteste seja anexada.",
            "Validar lote de bateria, compatibilidade dos acessórios e próxima manutenção preventiva.",
            "Notificar a coordenação da emergência com status do substituto e previsão de liberação.",
        ],
        "audit_packet": "Pronto para revisão de qualidade e reunião de prontidão da emergência.",
    },
]


EVIDENCE_COPILOT_CASES: list[dict[str, Any]] = [
    {
        "id": "RCA-4102",
        "ticket_title": "Ventilador com oscilação em UTI",
        "asset_id": "UTI-VENT-02",
        "asset_name": "Ventilador Servo-U",
        "symptom": "Oscilação de pressão inspiratória em leito crítico, com dois eventos semelhantes no mês.",
        "probable_cause": "Falha intermitente em sensor de fluxo associada a firmware abaixo da linha de base recomendada.",
        "confidence": 87,
        "containment_steps": [
            "Conferir paciente/equipamento reserva antes de qualquer ajuste técnico.",
            "Executar autoteste e capturar log de pressão inspiratória.",
            "Validar sensor de fluxo, circuito, filtro e firmware instalado.",
            "Acionar fabricante com pacote UDI, log e histórico de recorrência FPConnect.",
        ],
        "guided_questions": [
            "A oscilação ocorre apenas com circuito específico ou em qualquer circuito?",
            "O autoteste falha antes ou depois da troca do sensor?",
            "Existe alerta externo ou boletim aplicável ao mesmo modelo/firmware?",
        ],
        "evidence": [
            {
                "label": "Manual técnico Servo-U",
                "type": "manual",
                "excerpt": "Instabilidade de pressão deve ser investigada com validação do sensor de fluxo, teste de vazamento do circuito e revisão do log de eventos.",
                "confidence_impact": "+22 pontos por compatibilidade direta com o sintoma.",
            },
            {
                "label": "Histórico FPConnect",
                "type": "history",
                "excerpt": "2 chamados similares em 30 dias na UTI adulto com resolução após troca de sensor e atualização de firmware.",
                "confidence_impact": "+18 pontos por recorrência operacional.",
            },
        ],
        "oem_message": (
            "Solicitamos avaliação técnica para UTI-VENT-02. Sintoma: oscilação de pressão "
            "inspiratória. Anexos: UDI, firmware 4.3.1, log de evento, autoteste e histórico."
        ),
        "capa_draft": (
            "Contenção: equipamento reserva em leito crítico. Causa provável: sensor de fluxo/firmware. "
            "Ação corretiva: validar sensor, atualizar firmware e revisar ativos similares."
        ),
    },
    {
        "id": "RCA-4103",
        "ticket_title": "Desfibrilador sem autoteste válido",
        "asset_id": "DEF-ER-01",
        "asset_name": "Desfibrilador Zoll",
        "symptom": "Autoteste falhou em equipamento de emergência sem evidência de substituição anexada.",
        "probable_cause": "Bateria interna fora da faixa ou acessório incompatível com o perfil UDI aprovado.",
        "confidence": 82,
        "containment_steps": [
            "Retirar equipamento da escala e registrar substituto operacional.",
            "Testar bateria, cabos, pás e fonte AC.",
            "Comparar lote de bateria com perfil de acessórios aprovado.",
            "Anexar evidência de autoteste antes de liberar para uso.",
        ],
        "guided_questions": [
            "Qual código de falha foi exibido no autoteste?",
            "A bateria atual corresponde ao lote aprovado para este modelo?",
            "Existe registro de troca recente sem fechamento de evidência?",
        ],
        "evidence": [
            {
                "label": "Checklist de emergência",
                "type": "checklist",
                "excerpt": "Equipamento de suporte à vida com autoteste inválido deve ter substituto documentado.",
                "confidence_impact": "+20 pontos por regra de segurança clínica.",
            }
        ],
        "oem_message": (
            "Solicitamos suporte para DEF-ER-01. Autoteste inválido em emergência. "
            "Enviamos código de falha, UDI, lote de bateria, acessórios e substituição."
        ),
        "capa_draft": (
            "Contenção: substituto documentado. Causa provável: bateria/acessório. "
            "Ação corretiva: troca validada, autoteste anexado e revisão de estoque."
        ),
    },
]


VALUE_ENGINE_SCENARIOS: list[dict[str, Any]] = [
    {
        "id": "executive-renewal",
        "client_profile": "Hospital terciário com UTI, emergência e centro cirúrgico",
        "period": "Últimos 30 dias",
        "protected_assets": 47,
        "avoided_downtime_hours": 61,
        "avoided_loss_brl": 612000,
        "renewal_expansion_brl": 438700,
        "renewal_risk": "low",
        "recommended_offer": "Renovar contrato premium com Radar de Risco + RCA Copilot + pacote mensal executivo.",
        "executive_narrative": (
            "O FPConnect deixou de ser apenas controle de chamados: ele protegeu disponibilidade "
            "de ativos críticos, reduziu tempo de resposta e gerou evidências para diretoria."
        ),
        "levers": [
            {
                "label": "Indisponibilidade evitada",
                "value": "61 h",
                "detail": "Baseado em incidentes críticos contidos antes de indisponibilidade prolongada.",
            },
            {
                "label": "Perda evitada",
                "value": "R$ 612 mil",
                "detail": "Estimativa combinando agenda protegida, substituição preventiva e suporte à vida.",
            },
        ],
        "board_questions": [
            "Quanto custaria uma hora sem ventilador, desfibrilador ou sala cirúrgica?",
            "Qual evidência prova que a engenharia clínica reduziu risco assistencial?",
            "Quais contratos devem ser expandidos antes da próxima auditoria?",
        ],
    },
    {
        "id": "diagnostic-network",
        "client_profile": "Rede de diagnóstico por imagem e laboratório",
        "period": "Últimos 30 dias",
        "protected_assets": 16,
        "avoided_downtime_hours": 34,
        "avoided_loss_brl": 301000,
        "renewal_expansion_brl": 219400,
        "renewal_risk": "medium",
        "recommended_offer": "Expandir cobertura para cadeia fria, imagem e integração de agenda.",
        "executive_narrative": (
            "O maior valor está em preservar agenda e cadeia fria com verificações, alertas e RCA."
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
                "detail": "Risco em reagentes e amostras contido por resposta rápida.",
            },
        ],
        "board_questions": [
            "Quais unidades geram maior perda por indisponibilidade?",
            "Quais ativos deveriam entrar primeiro no contrato preditivo?",
            "Como provar redução de remarcação para a diretoria regional?",
        ],
    },
]


def get_risk_radar_assets() -> list[dict[str, Any]]:
    return deepcopy(RISK_RADAR_ASSETS)


def get_evidence_copilot_cases() -> list[dict[str, Any]]:
    return deepcopy(EVIDENCE_COPILOT_CASES)


def get_value_engine_scenarios() -> list[dict[str, Any]]:
    return deepcopy(VALUE_ENGINE_SCENARIOS)
