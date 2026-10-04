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
  scenarioValue: number;
  scenarioHours: number;
  boardMessage: string;
};

export const strategicMoats: StrategicMoat[] = [
  {
    id: "capacity-twin",
    title: "Clinical Capacity Twin",
    shortTitle: "Capacity Twin",
    thesis:
      "Hipótese de produto a validar: organizar dados de ativos e operação pode ajudar equipes a discutir cenários de indisponibilidade e contingência.",
    commercialEdge:
      "Hipótese de posicionamento: relacionar registros de manutenção a prioridades operacionais pode complementar a análise de ordens de serviço.",
    buyerHook:
      "Validar com responsáveis operacionais se disponibilidade de equipamentos se relaciona a prioridades de leitos, procedimentos e exames.",
    proofMetric:
      "Evidência a definir com o cliente: dados disponíveis, critério de prioridade e resultado observado no piloto.",
    ninetyDayWedge:
      "Avaliar uma linha de cuidado apenas após confirmar responsável, dor, dados exportáveis, orçamento e prazo.",
    sourceSignals: [
      "Verificar fontes públicas sobre simulação operacional e registrar a publicação, data e aplicação ao escopo.",
      "Consultar publicações de risco da ECRI diretamente antes de citar qualquer achado ou ano.",
      "Comparar funcionalidades de CMMSs com fontes atuais de cada fornecedor; não generalizar o mercado.",
    ],
    operatingLoop: [
      "Confirmar com o cliente os ativos e campos que podem ser analisados.",
      "Descrever prioridades e critérios com a equipe responsável.",
      "Apresentar cenários identificados como hipóteses, não como previsões.",
      "Registrar revisão humana e evidências acordadas no piloto.",
    ],
  },
  {
    id: "trust-graph",
    title: "Device Trust Graph",
    shortTitle: "Trust Graph",
    thesis:
      "Hipótese de produto a validar: relacionar inventário autorizado a fontes externas pode facilitar a revisão de informações por ativo.",
    commercialEdge:
      "Hipótese de posicionamento: reunir referências e evidências para revisão humana pode complementar alertas e registros existentes.",
    buyerHook:
      "Validar com segurança, qualidade e engenharia clínica quais fontes, responsáveis e evidências são relevantes para cada revisão.",
    proofMetric:
      "Evidência a definir com o cliente: cobertura dos dados autorizados, rastreabilidade das fontes e utilidade na revisão.",
    ninetyDayWedge:
      "Começar somente com dados e fontes aprovados pelo cliente; confirmar identificadores, acesso, limites e atualização antes de qualquer cruzamento.",
    sourceSignals: [
      "Consultar fontes oficiais da FDA para a questão específica e registrar URL, data e limites de cobertura.",
      "Verificar documentação vigente de UDI/GUDID e condições de consulta antes de propor integração.",
      "Consultar fontes oficiais da CISA para KEV/SBOM; não presumir atualização, correspondência ou cobertura de dispositivo.",
    ],
    operatingLoop: [
      "Confirmar autorização, identificadores e qualidade dos dados de inventário.",
      "Consultar somente fontes externas aprovadas e registrar origem e data.",
      "Apresentar correspondências como itens para validação, não como determinação de risco.",
      "Encaminhar a revisão e decisão às pessoas autorizadas pelo cliente.",
    ],
  },
  {
    id: "revenue-command",
    title: "Executive Revenue Command",
    shortTitle: "Revenue Command",
    thesis:
      "Hipótese comercial a validar: evidências operacionais revisadas podem ajudar um sponsor a avaliar a continuidade ou expansão de um piloto.",
    commercialEdge:
      "Hipótese de posicionamento: comunicar escopo, dados e aprendizados de um piloto pode apoiar conversas comerciais sem prometer ROI ou payback.",
    buyerHook:
      "Validar com o sponsor quais evidências, critérios e próximos passos seriam necessários para avaliar uma contratação.",
    proofMetric:
      "Evidência a definir: retorno do sponsor, critérios de compra, escopo validado e resultados documentados com autorização.",
    ninetyDayWedge:
      "Usar aprendizados de pilotos pagos, se contratados, para revisar proposta, esforço, margem e critérios de continuidade.",
    sourceSignals: [
      "Confirmar com cada conta quem decide, qual dor foi validada, quais dados podem ser exportados e qual o prazo.",
      "Distinguir projeções de resultados medidos e não apresentar cenários como histórico ou garantia.",
      "Registrar autorização antes de divulgar nomes, depoimentos, resultados ou casos de clientes.",
    ],
    operatingLoop: [
      "Registrar o problema e o critério de sucesso acordados com o cliente.",
      "Executar apenas o escopo contratado e autorizado.",
      "Separar dados observados, premissas e limitações no resumo do piloto.",
      "Revisar próximos passos com o sponsor, sem automatizar decisões comerciais.",
    ],
  },
];

export const stakeholderPerspectives: Record<MoatId, StakeholderPerspective[]> = {
  "capacity-twin": [
    {
      stakeholder: "CEO / COO",
      pain: "Hipótese de dor: indisponibilidade pode afetar prioridades operacionais e assistenciais.",
      promise: "Hipótese de valor: organizar cenários para discussão com as áreas responsáveis.",
      proof: "Evidência necessária: critérios, dados e avaliação registrados pelo cliente.",
    },
    {
      stakeholder: "Engenharia Clínica",
      pain: "Hipótese de dor: a equipe pode precisar conciliar chamados com outros critérios de prioridade.",
      promise: "Hipótese de valor: estruturar critérios de revisão com os dados disponíveis.",
      proof: "Evidência necessária: critérios aprovados e revisão da equipe responsável.",
    },
    {
      stakeholder: "CFO",
      pain: "Hipótese de dor: pode ser difícil relacionar indisponibilidade a custos sem dados suficientes.",
      promise: "Hipótese de valor: explicitar premissas para análise financeira pelo cliente.",
      proof: "Evidência necessária: fontes, premissas e validação financeira do cliente.",
    },
  ],
  "trust-graph": [
    {
      stakeholder: "CISO / TI",
      pain: "Hipótese de dor: contexto e restrições de dispositivos conectados podem variar entre clientes.",
      promise: "Hipótese de valor: reunir referências verificáveis para revisão com TI e engenharia.",
      proof: "Evidência necessária: fonte, data, identificador correspondente e validação humana.",
    },
    {
      stakeholder: "Qualidade / Regulatório",
      pain: "Hipótese de dor: registros e evidências podem estar distribuídos entre sistemas e equipes.",
      promise: "Hipótese de valor: organizar evidências autorizadas com origem rastreável.",
      proof: "Evidência necessária: trilha validada pelo cliente; não representa certificação regulatória.",
    },
    {
      stakeholder: "Compras / Jurídico",
      pain: "Hipótese de dor: requisitos de fornecedor e ciclo de vida podem demandar consolidação.",
      promise: "Hipótese de valor: preparar perguntas para análise de contratos e fornecedores.",
      proof: "Evidência necessária: requisitos revisados pelas áreas jurídica e de compras.",
    },
  ],
  "revenue-command": [
    {
      stakeholder: "Sponsor executivo",
      pain: "Hipótese de dor: resultados e critérios de continuidade podem não estar explícitos no piloto.",
      promise: "Hipótese de valor: resumir escopo, observações e questões para revisão conjunta.",
      proof: "Evidência necessária: resumo aprovado pelo sponsor e baseado em dados autorizados.",
    },
    {
      stakeholder: "Comercial",
      pain: "Hipótese de dor: pode faltar informação validada para adaptar uma proposta.",
      promise: "Hipótese de valor: documentar dor, dados, decisor e critérios informados pela conta.",
      proof: "Evidência necessária: confirmação do cliente; sem ROI ou resultado presumido.",
    },
    {
      stakeholder: "Customer Success",
      pain: "Hipótese de dor: a continuidade de um piloto pode depender de critérios ainda não acordados.",
      promise: "Hipótese de valor: organizar perguntas e próximos passos para decisão humana.",
      proof: "Evidência necessária: critérios e decisão registrados pelos responsáveis.",
    },
  ],
};

export const experiments: Experiment[] = [
  {
    moatId: "capacity-twin",
    name: "Entrevista sobre prioridade e indisponibilidade",
    owner: "A definir com o sponsor",
    metric: "Dor confirmada, dados disponíveis e critério acordado",
    passSignal:
      "Responsável confirma a dor, autoriza os dados necessários e acorda como avaliar o piloto.",
    firstAsset: "Definido pelo cliente após validar escopo e acesso",
  },
  {
    moatId: "capacity-twin",
    name: "Revisão de cenário de contingência",
    owner: "A definir com o cliente",
    metric: "Utilidade percebida e limitações documentadas",
    passSignal:
      "Equipe responsável revisa o cenário e registra correções, limitações e decisão.",
    firstAsset: "Linha de cuidado e ativo selecionados pelo cliente",
  },
  {
    moatId: "trust-graph",
    name: "Revisão de identificadores e fontes",
    owner: "A definir com TI e Engenharia Clínica",
    metric: "Correspondências verificadas e origem rastreável",
    passSignal:
      "Cliente valida identificadores, fontes, acesso e processo de revisão humana.",
    firstAsset: "Selecionado pelo cliente; dados e consultas autorizados",
  },
  {
    moatId: "trust-graph",
    name: "Validação de evidências de fornecedor",
    owner: "A definir com Compras e Jurídico",
    metric: "Requisitos e evidências confirmados pelas áreas responsáveis",
    passSignal:
      "Áreas responsáveis aprovam o checklist e confirmam as fontes antes de utilizá-lo.",
    firstAsset: "Fornecedor e escopo escolhidos pelo cliente",
  },
  {
    moatId: "revenue-command",
    name: "Revisão de critérios de compra",
    owner: "A definir com a conta",
    metric: "Decisor, dor, orçamento, dados e prazo validados",
    passSignal:
      "Sponsor confirma os critérios e o próximo passo; nenhuma conversão é presumida.",
    firstAsset: "Conta com interesse confirmado e dados autorizados",
  },
  {
    moatId: "revenue-command",
    name: "Revisão de continuidade do piloto",
    owner: "A definir com o sponsor",
    metric: "Critérios de continuidade e esforço documentados",
    passSignal:
      "Sponsor avalia os resultados documentados e decide os próximos passos.",
    firstAsset: "Piloto pago concluído, se contratado",
  },
];

export const evidenceSignals = [
  {
    label: "ECRI",
    value:
      "Consultar a publicação aplicável diretamente; registrar edição, data, trecho e limites antes de citar.",
    posture: "Fonte a verificar",
  },
  {
    label: "FDA",
    value:
      "Verificar a fonte oficial específica, seus identificadores, atualização e cobertura para o caso de uso.",
    posture: "Consulta a validar",
  },
  {
    label: "CISA / SBOM",
    value:
      "Consultar documentação oficial vigente; não inferir correspondência de dispositivo ou risco clínico.",
    posture: "Escopo a validar",
  },
  {
    label: "Mercado CMMS",
    value:
      "Comparar páginas e documentação atuais de fornecedores identificados antes de descrever capacidades.",
    posture: "Pesquisa pendente",
  },
];

export function calculateMoatImpact(inputs: ImpactInputs): ImpactProjection {
  const downtimeHours = Math.max(0, inputs.downtimeHours);
  const assetsAtRisk = Math.max(0, inputs.assetsAtRisk);
  const hourlyClinicalValue = Math.max(0, inputs.hourlyClinicalValue);
  const clinicalMultiplier = Math.max(0, inputs.clinicalMultiplier);
  const avoidableRate = Math.min(Math.max(inputs.avoidableRate, 0), 1);
  const scenarioHours = downtimeHours * assetsAtRisk * avoidableRate;
  const scenarioValue =
    scenarioHours * hourlyClinicalValue * clinicalMultiplier;

  return {
    scenarioHours: Math.round(scenarioHours),
    scenarioValue: Math.round(scenarioValue),
    boardMessage:
      "Cenário aritmético baseado somente nas premissas informadas. Não mede efeito do produto, economia realizada, redução de downtime nem retorno garantido.",
  };
}
