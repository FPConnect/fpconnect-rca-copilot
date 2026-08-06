export type RiskSeverity = "critical" | "high" | "medium" | "low";

export interface RiskSignal {
  source: string;
  type: "recall" | "cyber" | "regulatory" | "udi" | "sbom";
  severity: RiskSeverity;
  title: string;
  publishedAt: string;
  evidence: string;
}

export interface ClinicalRiskAsset {
  id: string;
  name: string;
  location: string;
  manufacturer: string;
  model: string;
  udi: string;
  firmware: string;
  clinicalCriticality: "life-support" | "diagnostic" | "monitoring" | "support";
  overallRisk: number;
  recallRisk: number;
  cyberRisk: number;
  regulatoryRisk: number;
  downtimeImpactBRL: number;
  status: "action_required" | "monitor" | "cleared";
  signals: RiskSignal[];
  recommendedActions: string[];
  auditPacket: string;
}

export interface EvidenceSource {
  label: string;
  type: "manual" | "history" | "telemetry" | "external" | "checklist";
  excerpt: string;
  confidenceImpact: string;
}

export interface EvidenceCopilotCase {
  id: string;
  ticketTitle: string;
  assetId: string;
  assetName: string;
  symptom: string;
  probableCause: string;
  confidence: number;
  containmentSteps: string[];
  guidedQuestions: string[];
  evidence: EvidenceSource[];
  oemMessage: string;
  capaDraft: string;
}

export interface ValueLever {
  label: string;
  value: string;
  detail: string;
}

export interface ValueEngineScenario {
  id: string;
  clientProfile: string;
  period: string;
  protectedAssets: number;
  avoidedDowntimeHours: number;
  avoidedLossBRL: number;
  renewalExpansionBRL: number;
  renewalRisk: "low" | "medium" | "high";
  recommendedOffer: string;
  executiveNarrative: string;
  levers: ValueLever[];
  boardQuestions: string[];
}

export const CLINICAL_RISK_ASSETS: ClinicalRiskAsset[] = [
  {
    id: "UTI-VENT-02",
    name: "Ventilador Servo-U",
    location: "UTI Adulto Leito 2",
    manufacturer: "Maquet/Getinge",
    model: "Servo-U",
    udi: "(01)07350012345678(21)SU-UTI-02",
    firmware: "4.3.1",
    clinicalCriticality: "life-support",
    overallRisk: 91,
    recallRisk: 82,
    cyberRisk: 74,
    regulatoryRisk: 88,
    downtimeImpactBRL: 98000,
    status: "action_required",
    signals: [
      {
        source: "FDA/openFDA",
        type: "recall",
        severity: "high",
        title: "Família do equipamento compatível com recall por desvio no sensor de pressão",
        publishedAt: "2026-07-18",
        evidence: "Família do modelo e faixa de firmware coincidem com ação corretiva de sensor de pressão.",
      },
      {
        source: "CISA KEV/NVD",
        type: "cyber",
        severity: "medium",
        title: "Serviço de rede exposto em firmware legado",
        publishedAt: "2026-07-04",
        evidence: "Firmware abaixo da linha de base reforçada definida no perfil interno do equipamento.",
      },
      {
        source: "RCA interno",
        type: "regulatory",
        severity: "critical",
        title: "Ativo de cuidado crítico com chamados recorrentes de oscilação de pressão",
        publishedAt: "2026-08-01",
        evidence: "Dois eventos semelhantes foram registrados na UTI nos últimos 30 dias.",
      },
    ],
    recommendedActions: [
      "Abrir chamado corretivo com o fornecedor e anexar UDI, firmware e recorte de telemetria.",
      "Mover um ventilador reserva para a UTI antes da validação do firmware.",
      "Criar registro de auditoria vinculando recall, linha de base cibernética e evidências de RCA.",
    ],
    auditPacket: "Pronto para engenharia clínica, qualidade e acompanhamento com o fabricante.",
  },
  {
    id: "DEF-ER-01",
    name: "Desfibrilador Zoll",
    location: "Emergência",
    manufacturer: "Zoll",
    model: "R Series",
    udi: "(01)00847946000011(21)DEF-ER-01",
    firmware: "2.18",
    clinicalCriticality: "life-support",
    overallRisk: 87,
    recallRisk: 78,
    cyberRisk: 42,
    regulatoryRisk: 90,
    downtimeImpactBRL: 124000,
    status: "action_required",
    signals: [
      {
        source: "AccessGUDID",
        type: "udi",
        severity: "medium",
        title: "Perfil UDI exige verificação do acessório de bateria",
        publishedAt: "2026-06-28",
        evidence: "A bateria configurada não corresponde ao perfil preferencial de estoque da emergência.",
      },
      {
        source: "Manutenção preventiva interna",
        type: "regulatory",
        severity: "critical",
        title: "Falha no autoteste do desfibrilador de emergência",
        publishedAt: "2026-08-02",
        evidence: "Autoteste falhou e nenhum registro de substituição foi anexado ao incidente.",
      },
    ],
    recommendedActions: [
      "Retirar da escala clínica até que a evidência do autoteste seja anexada.",
      "Validar lote de bateria, compatibilidade dos acessórios e próxima manutenção preventiva.",
      "Notificar a coordenação da emergência com status do substituto e previsão de liberação.",
    ],
    auditPacket: "Pronto para revisão de qualidade e reunião de prontidão da emergência.",
  },
  {
    id: "MON-ENF-14",
    name: "Monitor multiparamétrico",
    location: "Enfermaria A",
    manufacturer: "Nihon Kohden",
    model: "BSM Series",
    udi: "(01)04987654321098(21)MON-ENF-14",
    firmware: "1.9.8",
    clinicalCriticality: "monitoring",
    overallRisk: 68,
    recallRisk: 36,
    cyberRisk: 81,
    regulatoryRisk: 54,
    downtimeImpactBRL: 18000,
    status: "monitor",
    signals: [
      {
        source: "Perfil MDS2/SBOM",
        type: "sbom",
        severity: "high",
        title: "Componente de rede embarcado abaixo da linha de base aprovada",
        publishedAt: "2026-07-22",
        evidence: "Versão do componente SBOM abaixo da linha de base aprovada pelo hospital para monitoramento de rede.",
      },
      {
        source: "Chamados internos",
        type: "regulatory",
        severity: "medium",
        title: "Quatro eventos recorrentes de degradação do sinal de SpO2",
        publishedAt: "2026-08-03",
        evidence: "Sintomas recorrentes indicam desgaste de cabo ou latência de firmware/rede.",
      },
    ],
    recommendedActions: [
      "Inspecionar cabos e verificar a linha de base do firmware em janela de baixa ocupação.",
      "Anexar exceção de SBOM ao registro de risco.",
      "Agendar revisão do fornecedor se o próximo evento de SpO2 se repetir em até sete dias.",
    ],
    auditPacket: "Pronto para atualização do registro de risco e planejamento de serviço.",
  },
];

export const EVIDENCE_COPILOT_CASES: EvidenceCopilotCase[] = [
  {
    id: "RCA-4102",
    ticketTitle: "Ventilador com oscilação em UTI",
    assetId: "UTI-VENT-02",
    assetName: "Ventilador Servo-U",
    symptom: "Oscilação de pressão inspiratória em leito crítico, com dois eventos semelhantes no mês.",
    probableCause: "Falha intermitente em sensor de fluxo associada a firmware abaixo da linha de base recomendada.",
    confidence: 87,
    containmentSteps: [
      "Conferir paciente/equipamento reserva antes de qualquer ajuste técnico.",
      "Executar autoteste e capturar log de pressão inspiratória.",
      "Validar sensor de fluxo, circuito, filtro e firmware instalado.",
      "Acionar fabricante com pacote UDI, log e histórico de recorrência.",
    ],
    guidedQuestions: [
      "A oscilação ocorre apenas com circuito específico ou em qualquer circuito?",
      "O autoteste falha antes ou depois da troca do sensor?",
      "Existe alerta externo ou boletim aplicável ao mesmo modelo/firmware?",
    ],
    evidence: [
      {
        label: "Manual técnico Servo-U",
        type: "manual",
        excerpt: "Instabilidade de pressão deve ser investigada com validação do sensor de fluxo, teste de vazamento do circuito e revisão do log de eventos.",
        confidenceImpact: "+22 pontos por compatibilidade direta com o sintoma.",
      },
      {
        label: "Histórico FPConnect",
        type: "history",
        excerpt: "2 chamados similares em 30 dias na UTI adulto com resolução após troca de sensor e atualização de firmware.",
        confidenceImpact: "+18 pontos por recorrência operacional.",
      },
      {
        label: "Radar de Risco",
        type: "external",
        excerpt: "Sinal externo de recall/ação corretiva cruza com modelo e faixa de firmware.",
        confidenceImpact: "+16 pontos por evidência regulatória.",
      },
    ],
    oemMessage:
      "Solicitamos avaliação técnica para UTI-VENT-02. Sintoma: oscilação de pressão inspiratória. Anexos: UDI, firmware 4.3.1, log de evento, autoteste e histórico de recorrência FPConnect.",
    capaDraft:
      "Contenção: equipamento reserva em leito crítico e validação de circuito. Causa provável: sensor de fluxo/firmware. Ação corretiva: validar sensor, atualizar firmware e revisar família de ativos similares.",
  },
  {
    id: "RCA-4103",
    ticketTitle: "Desfibrilador sem autoteste válido",
    assetId: "DEF-ER-01",
    assetName: "Desfibrilador Zoll",
    symptom: "Autoteste falhou em equipamento de emergência sem evidência de substituição anexada.",
    probableCause: "Bateria interna fora da faixa ou acessório incompatível com o perfil UDI aprovado.",
    confidence: 82,
    containmentSteps: [
      "Retirar equipamento da escala e registrar substituto operacional.",
      "Testar bateria, cabos, pás e fonte AC.",
      "Comparar lote de bateria com perfil de acessórios aprovado.",
      "Anexar evidência de autoteste antes de liberar para uso.",
    ],
    guidedQuestions: [
      "Qual código de falha foi exibido no autoteste?",
      "A bateria atual corresponde ao lote aprovado para este modelo?",
      "Existe registro de troca recente sem fechamento de evidência?",
    ],
    evidence: [
      {
        label: "Checklist de emergência",
        type: "checklist",
        excerpt: "Equipamento de suporte à vida com autoteste inválido deve ter substituto documentado antes da devolução à escala.",
        confidenceImpact: "+20 pontos por regra de segurança clínica.",
      },
      {
        label: "AccessGUDID/UDI",
        type: "external",
        excerpt: "Perfil UDI exige validação de acessórios e bateria associados ao modelo.",
        confidenceImpact: "+14 pontos por compatibilidade de acessório.",
      },
    ],
    oemMessage:
      "Solicitamos suporte para DEF-ER-01. Autoteste inválido em área de emergência. Enviamos código de falha, UDI, lote de bateria, acessórios e registro de substituição.",
    capaDraft:
      "Contenção: substituto documentado. Causa provável: bateria/acessório. Ação corretiva: troca validada, autoteste anexado e revisão do estoque de baterias.",
  },
];

export const VALUE_ENGINE_SCENARIOS: ValueEngineScenario[] = [
  {
    id: "executive-renewal",
    clientProfile: "Hospital terciário com UTI, emergência e centro cirúrgico",
    period: "Últimos 30 dias",
    protectedAssets: 47,
    avoidedDowntimeHours: 61,
    avoidedLossBRL: 612000,
    renewalExpansionBRL: 438700,
    renewalRisk: "low",
    recommendedOffer: "Renovar contrato premium com Radar de Risco + RCA Copilot + pacote mensal executivo.",
    executiveNarrative:
      "O FPConnect deixou de ser apenas controle de chamados: ele protegeu disponibilidade de ativos críticos, reduziu tempo de resposta e gerou evidências para qualidade, diretoria e fornecedor.",
    levers: [
      {
        label: "Indisponibilidade evitada",
        value: "61 h",
        detail: "Baseado em incidentes críticos contidos antes de indisponibilidade prolongada.",
      },
      {
        label: "Perda evitada",
        value: "R$ 612 mil",
        detail: "Estimativa combinando agenda protegida, substituição preventiva e suporte à vida.",
      },
      {
        label: "Expansão recomendada",
        value: "R$ 438 mil",
        detail: "Upsell defensável para radar regulatório, linha de base cibernética e RCA assistido.",
      },
    ],
    boardQuestions: [
      "Quanto custaria uma hora sem ventilador, desfibrilador ou sala cirúrgica?",
      "Qual evidência temos para provar que a engenharia clínica reduziu risco assistencial?",
      "Quais contratos devem ser expandidos antes da próxima auditoria?",
    ],
  },
  {
    id: "diagnostic-network",
    clientProfile: "Rede de diagnóstico por imagem e laboratório",
    period: "Últimos 30 dias",
    protectedAssets: 16,
    avoidedDowntimeHours: 34,
    avoidedLossBRL: 301000,
    renewalExpansionBRL: 219400,
    renewalRisk: "medium",
    recommendedOffer: "Expandir cobertura para cadeia fria, imagem e integração de agenda.",
    executiveNarrative:
      "O maior valor está em preservar agenda e cadeia fria. A combinação de verificações, alertas e RCA reduz remarcações e perdas operacionais distribuídas.",
    levers: [
      {
        label: "Agenda protegida",
        value: "12 exames",
        detail: "Alertas antecipados permitiram redistribuir capacidade antes de parada completa.",
      },
      {
        label: "Cadeia fria",
        value: "R$ 76 mil",
        detail: "Risco estimado em reagentes e amostras contido por resposta rápida.",
      },
      {
        label: "Unidades priorizadas",
        value: "3",
        detail: "Foco em unidades com maior backlog e criticidade financeira.",
      },
    ],
    boardQuestions: [
      "Quais unidades geram maior perda por indisponibilidade?",
      "Quais ativos deveriam entrar primeiro no contrato preditivo?",
      "Como provar redução de remarcação para a diretoria regional?",
    ],
  },
];
