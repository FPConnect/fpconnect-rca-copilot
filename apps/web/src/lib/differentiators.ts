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
        title: "Recall family match for ventilator pressure sensor drift",
        publishedAt: "2026-07-18",
        evidence: "Model family and firmware range overlap with a pressure-sensor corrective action.",
      },
      {
        source: "CISA KEV/NVD",
        type: "cyber",
        severity: "medium",
        title: "Network service exposed on legacy firmware baseline",
        publishedAt: "2026-07-04",
        evidence: "Firmware is below the hardened baseline defined in the internal device profile.",
      },
      {
        source: "Internal RCA",
        type: "regulatory",
        severity: "critical",
        title: "Critical care asset with recurring pressure oscillation ticket",
        publishedAt: "2026-08-01",
        evidence: "Two similar UTI events were recorded within the last 30 days.",
      },
    ],
    recommendedActions: [
      "Open a supplier-backed corrective ticket and attach UDI, firmware and telemetry snapshot.",
      "Move a backup ventilator to the UTI before firmware validation.",
      "Create an audit record linking recall, cyber baseline and RCA evidence.",
    ],
    auditPacket: "Ready for biomedical engineering, quality and OEM follow-up.",
  },
  {
    id: "DEF-ER-01",
    name: "Desfibrilador Zoll",
    location: "Emergencia",
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
        title: "UDI profile requires battery accessory verification",
        publishedAt: "2026-06-28",
        evidence: "Configured battery accessory does not match the preferred emergency stock profile.",
      },
      {
        source: "Internal PM",
        type: "regulatory",
        severity: "critical",
        title: "Autotest failure on emergency defibrillator",
        publishedAt: "2026-08-02",
        evidence: "Autotest failed and no replacement record was attached to the incident.",
      },
    ],
    recommendedActions: [
      "Remove from clinical rotation until autotest evidence is attached.",
      "Validate battery lot, accessory compatibility and next PM date.",
      "Notify emergency coordinator with replacement status and ETA.",
    ],
    auditPacket: "Ready for quality event review and emergency readiness meeting.",
  },
  {
    id: "MON-ENF-14",
    name: "Monitor multiparametrico",
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
        source: "MDS2/SBOM profile",
        type: "sbom",
        severity: "high",
        title: "Embedded network component below approved patch baseline",
        publishedAt: "2026-07-22",
        evidence: "SBOM component version is below the hospital's approved network monitoring baseline.",
      },
      {
        source: "Internal tickets",
        type: "regulatory",
        severity: "medium",
        title: "Four recurring SpO2 signal degradation events",
        publishedAt: "2026-08-03",
        evidence: "Recurring symptoms point to cable wear or firmware/network latency.",
      },
    ],
    recommendedActions: [
      "Run cable inspection and firmware baseline check during low census window.",
      "Attach SBOM exception note to the risk register.",
      "Schedule vendor review if the next SpO2 event repeats within seven days.",
    ],
    auditPacket: "Ready for risk register update and service planning.",
  },
];

export const EVIDENCE_COPILOT_CASES: EvidenceCopilotCase[] = [
  {
    id: "RCA-4102",
    ticketTitle: "Ventilador com oscilacao em UTI",
    assetId: "UTI-VENT-02",
    assetName: "Ventilador Servo-U",
    symptom: "Oscilacao de pressao inspiratoria em leito critico, com dois eventos semelhantes no mes.",
    probableCause: "Falha intermitente em sensor de fluxo associada a firmware abaixo do baseline recomendado.",
    confidence: 87,
    containmentSteps: [
      "Conferir paciente/equipamento backup antes de qualquer ajuste tecnico.",
      "Executar autoteste e capturar log de pressao inspiratoria.",
      "Validar sensor de fluxo, circuito, filtro e firmware instalado.",
      "Acionar OEM com pacote UDI + log + historico de recorrencia.",
    ],
    guidedQuestions: [
      "A oscilacao ocorre apenas com circuito especifico ou em qualquer circuito?",
      "O autoteste falha antes ou depois da troca do sensor?",
      "Existe alerta externo ou boletim aplicavel ao mesmo modelo/firmware?",
    ],
    evidence: [
      {
        label: "Manual tecnico Servo-U",
        type: "manual",
        excerpt: "Pressure instability should be investigated through flow sensor validation, circuit leak test and event log review.",
        confidenceImpact: "+22 pontos por compatibilidade direta com o sintoma.",
      },
      {
        label: "Historico FPConnect",
        type: "history",
        excerpt: "2 tickets similares em 30 dias na UTI adulto com resolucao apos troca de sensor e atualizacao de firmware.",
        confidenceImpact: "+18 pontos por recorrencia operacional.",
      },
      {
        label: "Risk Radar",
        type: "external",
        excerpt: "Sinal externo de recall/corrective action cruza com modelo e faixa de firmware.",
        confidenceImpact: "+16 pontos por evidencia regulatoria.",
      },
    ],
    oemMessage:
      "Solicitamos avaliacao tecnica para UTI-VENT-02. Sintoma: oscilacao de pressao inspiratoria. Anexos: UDI, firmware 4.3.1, log de evento, autoteste e historico de recorrencia FPConnect.",
    capaDraft:
      "Contencao: backup em leito critico e validacao de circuito. Causa provavel: sensor de fluxo/firmware. Acao corretiva: validar sensor, atualizar firmware e revisar familia de ativos similares.",
  },
  {
    id: "RCA-4103",
    ticketTitle: "Desfibrilador sem autoteste valido",
    assetId: "DEF-ER-01",
    assetName: "Desfibrilador Zoll",
    symptom: "Autoteste falhou em equipamento de emergencia sem evidencia de substituicao anexada.",
    probableCause: "Bateria interna fora da faixa ou acessorio incompatavel com o perfil UDI aprovado.",
    confidence: 82,
    containmentSteps: [
      "Retirar equipamento da escala e registrar substituto operacional.",
      "Testar bateria, cabos, pas e fonte AC.",
      "Comparar lote de bateria com perfil de acessorios aprovado.",
      "Anexar evidencia de autoteste antes de liberar para uso.",
    ],
    guidedQuestions: [
      "Qual codigo de falha foi exibido no autoteste?",
      "A bateria atual corresponde ao lote aprovado para este modelo?",
      "Existe registro de troca recente sem fechamento de evidencia?",
    ],
    evidence: [
      {
        label: "Checklist emergencia",
        type: "checklist",
        excerpt: "Equipamento de suporte a vida com autoteste invalido deve ter substituto documentado antes da devolucao a escala.",
        confidenceImpact: "+20 pontos por regra de seguranca clinica.",
      },
      {
        label: "AccessGUDID/UDI",
        type: "external",
        excerpt: "Perfil UDI exige validacao de acessorios e bateria associados ao modelo.",
        confidenceImpact: "+14 pontos por compatibilidade de acessorio.",
      },
    ],
    oemMessage:
      "Solicitamos suporte para DEF-ER-01. Autoteste invalido em area de emergencia. Enviamos codigo de falha, UDI, lote de bateria, acessorios e registro de substituicao.",
    capaDraft:
      "Contencao: substituto documentado. Causa provavel: bateria/acessorio. Acao corretiva: troca validada, autoteste anexado e revisao do estoque de baterias.",
  },
];

export const VALUE_ENGINE_SCENARIOS: ValueEngineScenario[] = [
  {
    id: "executive-renewal",
    clientProfile: "Hospital terciario com UTI, emergencia e centro cirurgico",
    period: "Ultimos 30 dias",
    protectedAssets: 47,
    avoidedDowntimeHours: 61,
    avoidedLossBRL: 612000,
    renewalExpansionBRL: 438700,
    renewalRisk: "low",
    recommendedOffer: "Renovar contrato premium com Risk Radar + RCA Copilot + pacote mensal executivo.",
    executiveNarrative:
      "O FPConnect deixou de ser apenas controle de chamados: ele protegeu disponibilidade de ativos criticos, reduziu tempo de resposta e gerou evidencias para qualidade, diretoria e fornecedor.",
    levers: [
      {
        label: "Downtime evitado",
        value: "61 h",
        detail: "Baseado em incidentes criticos contidos antes de indisponibilidade prolongada.",
      },
      {
        label: "Perda evitada",
        value: "R$ 612 mil",
        detail: "Estimativa combinando agenda protegida, substituicao preventiva e suporte a vida.",
      },
      {
        label: "Expansao recomendada",
        value: "R$ 438 mil",
        detail: "Upsell defensavel para radar regulatorio, cyber baseline e RCA assistido.",
      },
    ],
    boardQuestions: [
      "Quanto custaria uma hora sem ventilador, desfibrilador ou sala cirurgica?",
      "Qual evidencia temos para provar que a engenharia clinica reduziu risco assistencial?",
      "Quais contratos devem ser expandidos antes da proxima auditoria?",
    ],
  },
  {
    id: "diagnostic-network",
    clientProfile: "Rede de diagnostico por imagem e laboratorio",
    period: "Ultimos 30 dias",
    protectedAssets: 16,
    avoidedDowntimeHours: 34,
    avoidedLossBRL: 301000,
    renewalExpansionBRL: 219400,
    renewalRisk: "medium",
    recommendedOffer: "Expandir cobertura para cadeia fria, imagem e integracao de agenda.",
    executiveNarrative:
      "O maior valor esta em preservar agenda e cadeia fria. A combinacao de health checks, alertas e RCA reduz remarcacoes e perdas operacionais distribuidas.",
    levers: [
      {
        label: "Agenda protegida",
        value: "12 exames",
        detail: "Alertas antecipados permitiram redistribuir capacidade antes de parada completa.",
      },
      {
        label: "Cadeia fria",
        value: "R$ 76 mil",
        detail: "Risco estimado em reagentes e amostras contido por resposta rapida.",
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
      "Como provar reducao de remarcacao para a diretoria regional?",
    ],
  },
];
