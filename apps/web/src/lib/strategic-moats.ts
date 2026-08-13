export type MoatId = "capacity-twin" | "trust-graph" | "revenue-command";

export type StrategicMoat = {
  id: MoatId;
  title: string;
  shortTitle: string;
  thesis: string;
  commercialEdge: string;
  buyerHook: string;
  proofMetric: string;
  ninetyDayWedge: string;
  sourceSignals: string[];
  operatingLoop: string[];
};

export type StakeholderPerspective = {
  stakeholder: string;
  pain: string;
  promise: string;
  proof: string;
};

export type Experiment = {
  moatId: MoatId;
  name: string;
  owner: string;
  metric: string;
  passSignal: string;
  firstAsset: string;
};

export type ImpactInputs = {
  downtimeHours: number;
  assetsAtRisk: number;
  hourlyClinicalValue: number;
  clinicalMultiplier: number;
  avoidableRate: number;
};

export type ImpactProjection = {
  protectedValue: number;
  avoidedHours: number;
  executiveScore: number;
  boardMessage: string;
};

export const strategicMoats: StrategicMoat[] = [
  {
    id: "capacity-twin",
    title: "Clinical Capacity Twin",
    shortTitle: "Capacity Twin",
    thesis:
      "O FPConnect deixa de ser um painel de manutenção e passa a simular capacidade clínica: quais leitos, salas, filas e receitas ficam em risco quando um ativo crítico cai.",
    commercialEdge:
      "Concorrentes vendem ordem de serviço; a FPConnect vende decisão de capacidade e risco assistencial antes da falha virar crise.",
    buyerHook:
      "CEO, COO e diretoria assistencial enxergam disponibilidade de equipamentos como impacto em leito, centro cirúrgico, UTI, imagem e faturamento.",
    proofMetric: "Valor clínico-financeiro protegido por hora de indisponibilidade evitada.",
    ninetyDayWedge:
      "Começar com UTI, centro cirúrgico e diagnóstico por imagem, usando dados simples de ativos, criticidade, uso e histórico de tickets.",
    sourceSignals: [
      "Digital twins permitem testar cenários hospitalares antes de mudar operação real.",
      "ECRI lista preparo para eventos de indisponibilidade digital como risco crítico de 2026.",
      "CMMSs comuns ainda priorizam work order, compliance e manutenção, não capacidade clínica.",
    ],
    operatingLoop: [
      "Mapear ativos críticos por linha de cuidado.",
      "Converter falha em impacto de leito, procedimento, exame e receita.",
      "Simular cenários de indisponibilidade e contingência.",
      "Gerar plano executivo com prioridade, custo evitado e dono da ação.",
    ],
  },
  {
    id: "trust-graph",
    title: "Device Trust Graph",
    shortTitle: "Trust Graph",
    thesis:
      "Cada ativo vira um grafo vivo de confiança: UDI/GUDID, recall, SBOM, CVE/KEV, firmware, fornecedor, contrato, evidência interna e risco clínico.",
    commercialEdge:
      "Em vez de mostrar alertas soltos, a FPConnect mostra a cadeia de responsabilidade e a próxima ação defensável para engenharia, TI, qualidade e compras.",
    buyerHook:
      "CISO, qualidade e engenharia clínica ganham uma trilha auditável para priorizar risco de legacy devices, recalls e obrigações de fornecedor.",
    proofMetric: "Percentual de ativos críticos com evidência completa e ação recomendada auditável.",
    ninetyDayWedge:
      "Começar com ventiladores, bombas de infusão e imagem; cruzar inventário demo com recalls FDA, AccessGUDID, CISA KEV e SBOM simulado.",
    sourceSignals: [
      "FDA reforça cybersecurity e uso de identificadores únicos de dispositivo.",
      "AccessGUDID fornece API/RSS para consulta de dispositivos.",
      "CISA atualizou elementos mínimos de SBOM em 2026; ECRI destaca legacy devices e falhas de recall.",
    ],
    operatingLoop: [
      "Normalizar ativo, modelo, UDI e firmware.",
      "Cruzar recall, early alert, SBOM, CVE/KEV e histórico interno.",
      "Classificar risco por exposição clínica, rede, paciente e fornecedor.",
      "Gerar pacote de evidência para auditoria, OEM, compras e diretoria.",
    ],
  },
  {
    id: "revenue-command",
    title: "Executive Revenue Command",
    shortTitle: "Revenue Command",
    thesis:
      "O sistema transforma operação em narrativa de venda: ROI, expansão contratual, SLA protegido, risco regulatório evitado e próxima proposta comercial por cliente.",
    commercialEdge:
      "A FPConnect não só reduz MTTR; ela prova valor em linguagem de CFO e cria gatilhos para upgrade, consultoria, implantação multiunidade e contratos enterprise.",
    buyerHook:
      "CFO e sponsor executivo recebem o racional de compra pronto: risco protegido, perda evitada, plano de adoção e payback por linha de cuidado.",
    proofMetric: "Pipeline influenciado por evidência operacional e payback estimado por conta.",
    ninetyDayWedge:
      "Usar dados de demo e pilotos para criar business cases automáticos por perfil de hospital, começando por redes e hospitais com alta complexidade.",
    sourceSignals: [
      "Compradores exigem compliance, multi-site, integrações e implantação rápida.",
      "Hospitais estão pressionados por custos, ataques cibernéticos e disponibilidade operacional.",
      "Diferencial comercial real surge quando o produto vira argumento de diretoria, não apenas ferramenta técnica.",
    ],
    operatingLoop: [
      "Medir valor protegido por ativo e unidade.",
      "Gerar business case por stakeholder.",
      "Recomendar pacote comercial e próximos passos.",
      "Retroalimentar CRM, LinkedIn e proposta com evidências do produto.",
    ],
  },
];

export const stakeholderPerspectives: Record<MoatId, StakeholderPerspective[]> = {
  "capacity-twin": [
    {
      stakeholder: "CEO / COO",
      pain: "Indisponibilidade vira atraso assistencial e pressão reputacional.",
      promise: "Simular onde a operação quebra antes do pico de demanda.",
      proof: "Leitos, exames e procedimentos protegidos por plano de contingência.",
    },
    {
      stakeholder: "Engenharia Clínica",
      pain: "Prioridade de manutenção compete com urgências sem critério executivo.",
      promise: "Fila de ação por impacto clínico real, não só status do chamado.",
      proof: "Ativos ranqueados por criticalidade, uso e cascata operacional.",
    },
    {
      stakeholder: "CFO",
      pain: "Downtime aparece como custo invisível e difícil de defender em orçamento.",
      promise: "Converter horas evitadas em valor protegido e payback.",
      proof: "Estimativa por hora, unidade, linha de cuidado e contrato.",
    },
  ],
  "trust-graph": [
    {
      stakeholder: "CISO / TI",
      pain: "Legacy devices não podem ser tratados como endpoints comuns.",
      promise: "Priorizar vulnerabilidade pelo impacto clínico e possibilidade operacional.",
      proof: "CVE/KEV + firmware + localização + status de uso + mitigação.",
    },
    {
      stakeholder: "Qualidade / Regulatório",
      pain: "Recall e evidência ficam dispersos entre e-mail, planilha e fornecedor.",
      promise: "Pacote auditável por ativo, com fonte, decisão e responsável.",
      proof: "Linha do tempo com recall, ação, anexo e aceite.",
    },
    {
      stakeholder: "Compras / Jurídico",
      pain: "Fornecedor vende tecnologia sem clareza de SBOM, SLA e risco de ciclo de vida.",
      promise: "Base objetiva para negociar suporte, troca, crédito ou mitigação.",
      proof: "Checklist de cláusulas, evidência técnica e risco financeiro.",
    },
  ],
  "revenue-command": [
    {
      stakeholder: "Sponsor executivo",
      pain: "Ferramentas técnicas morrem no piloto quando não viram narrativa de valor.",
      promise: "Criar a história de compra com números, riscos e próximos passos.",
      proof: "Resumo executivo pronto para comitê e proposta.",
    },
    {
      stakeholder: "Vendas FPConnect",
      pain: "Abordagem genérica compete com qualquer CMMS.",
      promise: "Personalizar pitch por hospital, cargo, risco e maturidade.",
      proof: "Mensagem, ROI e oferta recomendada por conta.",
    },
    {
      stakeholder: "Customer Success",
      pain: "Adoção inicial não necessariamente vira expansão.",
      promise: "Detectar gatilhos de expansão com base no valor já capturado.",
      proof: "Playbook de upgrade, consultoria e multiunidade.",
    },
  ],
};

export const experiments: Experiment[] = [
  {
    moatId: "capacity-twin",
    name: "Simulador UTI + imagem em 7 dias",
    owner: "Produto + Eng. Clínica",
    metric: "Horas críticas convertidas em valor protegido",
    passSignal: "Diretor entende impacto em menos de 3 minutos.",
    firstAsset: "Ventilador, tomógrafo e monitor multiparamétrico",
  },
  {
    moatId: "capacity-twin",
    name: "Mapa de contingência por linha de cuidado",
    owner: "Operações",
    metric: "Tempo para decidir realocação",
    passSignal: "Plano reduz decisão de contingência para menos de 15 minutos.",
    firstAsset: "UTI adulto e centro cirúrgico",
  },
  {
    moatId: "trust-graph",
    name: "UDI + recall + firmware pack",
    owner: "Produto + Segurança",
    metric: "Ativos críticos com evidência completa",
    passSignal: "Engenharia consegue abrir ticket OEM com anexos em 1 clique.",
    firstAsset: "Bomba de infusão",
  },
  {
    moatId: "trust-graph",
    name: "SBOM demand letter",
    owner: "Jurídico + Compras",
    metric: "Fornecedores com resposta formal",
    passSignal: "Fornecedor entrega SBOM, mitigação ou plano de ciclo de vida.",
    firstAsset: "Dispositivo conectado com firmware legado",
  },
  {
    moatId: "revenue-command",
    name: "Business case por hospital alvo",
    owner: "Vendas + CS",
    metric: "Reuniões executivas agendadas",
    passSignal: "Mensagem gera resposta de sponsor com dor operacional real.",
    firstAsset: "Hospitais com UTI, imagem e centro cirúrgico",
  },
  {
    moatId: "revenue-command",
    name: "Upgrade trigger em piloto",
    owner: "CS + Produto",
    metric: "Sinais de expansão por conta",
    passSignal: "Piloto vira plano Premium/Consultoria com payback defendável.",
    firstAsset: "Primeiro cliente com dados de tickets",
  },
];

export const evidenceSignals = [
  {
    label: "ECRI 2026",
    value: "AI misuse, digital darkness, recall failure, legacy cyber risk",
    posture: "Risco assistencial preventivo",
  },
  {
    label: "FDA",
    value: "Cybersecurity, recalls, early alerts, UDI/GUDID",
    posture: "Evidência regulatória por ativo",
  },
  {
    label: "CISA / SBOM",
    value: "KEV + elementos mínimos de SBOM atualizados em 2026",
    posture: "Transparência de software e cadeia de suprimentos",
  },
  {
    label: "Mercado CMMS",
    value: "Compliance, work orders, multi-site, preditivo e integrações",
    posture: "Diferenciar acima do CMMS tradicional",
  },
];

export function calculateMoatImpact(inputs: ImpactInputs): ImpactProjection {
  const avoidableRate = Math.min(Math.max(inputs.avoidableRate, 0), 0.9);
  const avoidedHours = inputs.downtimeHours * inputs.assetsAtRisk * avoidableRate;
  const protectedValue =
    avoidedHours * inputs.hourlyClinicalValue * inputs.clinicalMultiplier;
  const executiveScore = Math.min(
    99,
    Math.round(
      48 +
        inputs.assetsAtRisk * 4.5 +
        inputs.clinicalMultiplier * 11 +
        avoidableRate * 30 +
        Math.min(inputs.downtimeHours, 72) * 0.22,
    ),
  );

  const boardMessage =
    protectedValue >= 500000
      ? "Caso executivo forte: tratar como agenda de diretoria e proposta enterprise."
      : protectedValue >= 180000
        ? "Caso comercial bom: pilotar com sponsor operacional e CFO."
        : "Caso de entrada: usar como diagnóstico para capturar dados reais.";

  return {
    avoidedHours: Math.round(avoidedHours),
    protectedValue: Math.round(protectedValue),
    executiveScore,
    boardMessage,
  };
}
