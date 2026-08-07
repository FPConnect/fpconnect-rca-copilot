export interface SimulatorMachine {
  id: string;
  name: string;
  location: string;
  status: "online" | "warning" | "offline";
  lastCheck: string;
  risk: "baixo" | "moderado" | "alto";
}

export interface SimulatorHealthCheck {
  id: number;
  machine: string;
  check: string;
  result: "OK" | "WARNING" | "FAIL";
  value: string;
  time: string;
}

export interface SimulatorAlert {
  id: number;
  severity: "critical" | "high" | "medium" | "low";
  message: string;
  machine: string;
  owner: string;
  elapsed: string;
}

export interface SimulatorTicket {
  id: number;
  title: string;
  priority: "critical" | "high" | "medium" | "low";
  status: "open" | "in_progress" | "resolved";
  location: string;
  assignee: string;
  eta: string;
  probableCause: string;
  estimatedImpactBRL: number;
}

export interface SimulatorMaintenanceItem {
  id: number;
  machine: string;
  type: string;
  window: string;
  technician: string;
  status: string;
}

export interface SimulatorUser {
  id: number;
  name: string;
  role: string;
  status: string;
}

export interface SimulatorEvent {
  id: number;
  action: string;
  user: string;
  resource: string;
  time: string;
  type: string;
}

export interface SimulatorNotification {
  id: number;
  title: string;
  message: string;
  type: "success" | "warning" | "info" | "error";
  createdAt: string;
}

export interface SimulatorIntelItem {
  id: number;
  source: string;
  topic: string;
  title: string;
  summary: string;
  impact: string;
}

export interface SimulatorReport {
  id: string;
  title: string;
  cadence: string;
  audience: string;
  sections: string[];
  outcome: string;
}

export interface SimulatorToolModule {
  route: string;
  name: string;
  metric: string;
  deliverable: string;
  value: string;
}

export interface SimulatorScenario {
  id: string;
  name: string;
  facility: string;
  profile: string;
  narrative: string;
  monitoredAssets: number;
  criticalAssets: number;
  uptime: number;
  mttrMinutes: number;
  mtbfHours: number;
  pmCompliance: number;
  slaCompliance: number;
  openTickets: number;
  criticalAlerts: number;
  preventedDowntimeHours: number;
  estimatedSavingsBRL: number;
  avoidedLossBRL: number;
  benchmarkNotes: string[];
  toolModules: SimulatorToolModule[];
  reports: SimulatorReport[];
  machines: SimulatorMachine[];
  healthChecks: SimulatorHealthCheck[];
  alerts: SimulatorAlert[];
  tickets: SimulatorTicket[];
  maintenance: SimulatorMaintenanceItem[];
  users: SimulatorUser[];
  events: SimulatorEvent[];
  notifications: SimulatorNotification[];
  intel: SimulatorIntelItem[];
}

function metricCurrency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

export const SIMULATOR_SCENARIOS: SimulatorScenario[] = [
  {
    id: "tertiary-hospital",
    name: "Hospital terciario com UTI e centro cirurgico",
    facility: "Hospital Sao Gabriel",
    profile: "280 leitos, 9 salas cirurgicas, UTI adulto e neonatal, engenharia clinica com 11 tecnicos.",
    narrative:
      "Cenario calibrado para uma operacao hospitalar de alta criticidade, onde falhas em equipamentos de suporte a vida e imagem geram impacto clinico imediato e custo operacional relevante.",
    monitoredAssets: 186,
    criticalAssets: 47,
    uptime: 99.21,
    mttrMinutes: 42,
    mtbfHours: 1380,
    pmCompliance: 96,
    slaCompliance: 94,
    openTickets: 18,
    criticalAlerts: 6,
    preventedDowntimeHours: 61,
    estimatedSavingsBRL: 438700,
    avoidedLossBRL: 612000,
    benchmarkNotes: [
      "Priorizacao orientada por impacto em servicos de emergencia, terapia intensiva e centro cirurgico.",
      "Uso de sinais de recall e vigilancia externa para complementar manutencao baseada em risco.",
      "Indicadores organizados para rotina de engenharia clinica, operacao hospitalar e patrocinador executivo.",
    ],
    toolModules: [
      { route: "/machines", name: "Maquinas", metric: "Ativos monitorados", deliverable: "Mapa do parque por criticidade e status", value: "186 ativos" },
      { route: "/health-checks", name: "Health Checks", metric: "Checks automatizados", deliverable: "Leituras de conectividade, bateria, temperatura e autoteste", value: "1.284 checks/dia" },
      { route: "/alerts", name: "Alertas", metric: "Alertas criticos", deliverable: "Fila priorizada com tempo em aberto e responsavel", value: "6 criticos" },
      { route: "/tickets", name: "Tickets", metric: "Chamados abertos", deliverable: "Backlog com SLA, causa provavel e impacto financeiro", value: "18 chamados" },
      { route: "/maintenance", name: "Manutencao", metric: "PM compliance", deliverable: "Janela de manutencao, tecnico responsavel e plano corretivo", value: "96%" },
      { route: "/metrics", name: "Metricas", metric: "Uptime", deliverable: "Indicadores executivos de disponibilidade e performance", value: "99,21%" },
      { route: "/intel", name: "Radar", metric: "Sinais externos", deliverable: "Recalls, alertas e tendencias que afetam o parque", value: "14 sinais ativos" },
      { route: "/access-control", name: "Controle de Acesso", metric: "Usuarios ativos", deliverable: "Perfis, responsabilidades e trilha de governanca", value: "23 usuarios" },
      { route: "/history", name: "Historico", metric: "Eventos rastreados", deliverable: "Linha do tempo auditavel de incidentes e acoes", value: "312 eventos/30d" },
      { route: "/notifications", name: "Notificacoes", metric: "Acoes direcionadas", deliverable: "Alertas operacionais e executivos por contexto", value: "41 notificacoes" },
    ],
    reports: [
      {
        id: "weekly-ops",
        title: "Relatorio semanal de operacao",
        cadence: "Semanal",
        audience: "Coordenacao de engenharia clinica",
        sections: ["Tickets por criticidade", "Alertas recorrentes", "Atrasos de SLA", "Equipamentos com risco alto"],
        outcome: "Reduz backlog e define plano da semana sem consolidacao manual.",
      },
      {
        id: "executive-roi",
        title: "Relatorio executivo de disponibilidade e ROI",
        cadence: "Mensal",
        audience: "Diretoria operacional e financeira",
        sections: ["Uptime consolidado", "Downtime evitado", "Economia evitada", "Prioridades para expansao contratual"],
        outcome: "Conecta engenharia clinica com impacto financeiro e risco assistencial.",
      },
      {
        id: "compliance",
        title: "Relatorio de conformidade e manutencao",
        cadence: "Mensal",
        audience: "Qualidade, auditoria e biomedica",
        sections: ["PM compliance", "Pendencias criticas", "Checklist de calibracao", "Historico de intervencoes"],
        outcome: "Sustenta auditoria e reduz dependencia de planilhas locais.",
      },
      {
        id: "incident-pack",
        title: "Pacote RCA de incidente critico",
        cadence: "Sob demanda",
        audience: "Diretoria, qualidade e fornecedor",
        sections: ["Linha do tempo", "Hipotese principal", "Eventos relacionados", "Plano CAPA"],
        outcome: "Acelera resposta a incidentes com material pronto para follow-up.",
      },
    ],
    machines: [
      { id: "UTI-VENT-02", name: "Ventilador Servo-U", location: "UTI Adulto Leito 2", status: "warning", lastCheck: "ha 2 min", risk: "alto" },
      { id: "MRI-01", name: "MRI 1.5T", location: "Imagem", status: "online", lastCheck: "ha 1 min", risk: "moderado" },
      { id: "DEF-ER-01", name: "Desfibrilador Zoll", location: "Emergencia", status: "offline", lastCheck: "ha 48 min", risk: "alto" },
      { id: "NICU-FR-03", name: "Geladeira de hemocomponentes", location: "UTI Neonatal", status: "online", lastCheck: "ha 4 min", risk: "moderado" },
      { id: "OR-AN-05", name: "Estacao de anestesia", location: "Centro Cirurgico Sala 5", status: "warning", lastCheck: "ha 6 min", risk: "alto" },
    ],
    healthChecks: [
      { id: 1, machine: "Ventilador Servo-U", check: "Pressao inspiratoria", result: "WARNING", value: "desvio 8%", time: "ha 2 min" },
      { id: 2, machine: "MRI 1.5T", check: "Temperatura do chiller", result: "OK", value: "35,8 C", time: "ha 1 min" },
      { id: 3, machine: "Desfibrilador Zoll", check: "Autoteste", result: "FAIL", value: "erro 0x1A", time: "ha 48 min" },
      { id: 4, machine: "Estacao de anestesia", check: "Fluxo de gas", result: "WARNING", value: "variacao 5,4%", time: "ha 6 min" },
    ],
    alerts: [
      { id: 1, severity: "critical", message: "Autoteste falhou e equipamento removido da escala", machine: "Desfibrilador Zoll", owner: "Maria Santos", elapsed: "48 min" },
      { id: 2, severity: "critical", message: "Oscilacao de pressao no ventilador da UTI", machine: "Ventilador Servo-U", owner: "Joao Silva", elapsed: "12 min" },
      { id: 3, severity: "high", message: "Recall aplicavel a lote de bombas de infusao", machine: "Bomba de infusao Alaris", owner: "Radar Intel", elapsed: "2 h" },
      { id: 4, severity: "medium", message: "Calibracao vencendo em 72 horas", machine: "Monitor multiparametrico", owner: "Carlos Rocha", elapsed: "1 dia" },
    ],
    tickets: [
      { id: 4102, title: "Ventilador com oscilacao em UTI", priority: "critical", status: "in_progress", location: "UTI Adulto", assignee: "Joao Silva", eta: "2h", probableCause: "Falha intermitente em sensor de fluxo", estimatedImpactBRL: 98000 },
      { id: 4103, title: "Desfibrilador sem autoteste valido", priority: "critical", status: "open", location: "Emergencia", assignee: "Maria Santos", eta: "1h", probableCause: "Bateria interna fora da faixa", estimatedImpactBRL: 124000 },
      { id: 4096, title: "Latencia em monitor multiparametrico", priority: "high", status: "in_progress", location: "Enfermaria A", assignee: "Carlos Rocha", eta: "6h", probableCause: "Degradacao de firmware e pacote de rede", estimatedImpactBRL: 18000 },
      { id: 4089, title: "Calibracao de ECG da recepcao", priority: "medium", status: "resolved", location: "Recepcao", assignee: "Ana Lima", eta: "concluido", probableCause: "Ajuste de ganho e limpeza de conectores", estimatedImpactBRL: 4500 },
    ],
    maintenance: [
      { id: 1, machine: "MRI 1.5T", type: "Preventiva", window: "12/03 22:00-01:00", technician: "Equipe Imagem", status: "agendada" },
      { id: 2, machine: "Ventilador Servo-U", type: "Corretiva", window: "imediata", technician: "Joao Silva", status: "em execucao" },
      { id: 3, machine: "Estacao de anestesia", type: "Calibracao", window: "13/03 06:00-07:30", technician: "Carlos Rocha", status: "confirmada" },
    ],
    users: [
      { id: 1, name: "Marina Lopes", role: "Admin", status: "ativo" },
      { id: 2, name: "Joao Silva", role: "Tecnico lider", status: "ativo" },
      { id: 3, name: "Maria Santos", role: "Tecnica campo", status: "ativo" },
      { id: 4, name: "Diretoria Operacional", role: "Viewer executivo", status: "ativo" },
    ],
    events: [
      { id: 1, action: "Ticket escalado para nivel 2", user: "Sistema", resource: "Ventilador Servo-U", time: "2026-03-10 06:12", type: "ticket" },
      { id: 2, action: "Alerta reconhecido", user: "Maria Santos", resource: "Desfibrilador Zoll", time: "2026-03-10 05:58", type: "alert" },
      { id: 3, action: "Janela de manutencao aprovada", user: "Coordenacao CC", resource: "MRI 1.5T", time: "2026-03-09 22:11", type: "maintenance" },
      { id: 4, action: "Recall anexado ao parque", user: "Radar Intel", resource: "Bomba de infusao Alaris", time: "2026-03-09 14:20", type: "intel" },
    ],
    notifications: [
      { id: 1, title: "SLA critico em andamento", message: "Ventilador da UTI precisa de contencao em ate 2h.", type: "warning", createdAt: "2026-03-10T06:15:00Z" },
      { id: 2, title: "Recall aplicavel identificado", message: "Radar anexou novo sinal para 14 bombas de infusao do mesmo lote.", type: "info", createdAt: "2026-03-09T14:20:00Z" },
      { id: 3, title: "Preventiva aprovada", message: "Janela da MRI confirmada pelo centro cirurgico para hoje as 22h.", type: "success", createdAt: "2026-03-09T22:11:00Z" },
    ],
    intel: [
      { id: 1, source: "WHO acute care strategy", topic: "critical-care", title: "Continuidade de dispositivos criticos ganha peso em planejamento de cuidado agudo", summary: "Riscos de indisponibilidade em servicos de emergencia e terapia intensiva exigem resposta operacional mais rapida e padronizada.", impact: "Refina priorizacao de ativos criticos." },
      { id: 2, source: "Recall feed", topic: "recall", title: "Lote de bombas de infusao com recall ativo", summary: "Sinal externo cruza com inventario e dispara revisao preventiva de 14 equipamentos similares.", impact: "Evita falha repetitiva e reforca compliance." },
      { id: 3, source: "Benchmark interno", topic: "operations", title: "Atrasos de SLA concentram-se em ativos de suporte a vida", summary: "Historico indica maior perda operacional quando manutencao corretiva compete com agenda cirurgica.", impact: "Prioriza janelas e equipe senior." },
    ],
  },
  {
    id: "diagnostic-network",
    name: "Rede de diagnostico por imagem e laboratorio",
    facility: "Rede Viva Diagnosticos",
    profile: "18 unidades, 74 ativos monitorados, foco em ressonancia, tomografia, ultrassom e cadeia fria.",
    narrative:
      "Cenario pensado para rede multiunidade onde a maior dor e indisponibilidade em agendas, remarcacoes e custo de atendimento terceirizado.",
    monitoredAssets: 74,
    criticalAssets: 16,
    uptime: 98.74,
    mttrMinutes: 97,
    mtbfHours: 1125,
    pmCompliance: 93,
    slaCompliance: 91,
    openTickets: 11,
    criticalAlerts: 3,
    preventedDowntimeHours: 34,
    estimatedSavingsBRL: 219400,
    avoidedLossBRL: 301000,
    benchmarkNotes: [
      "Alta sensibilidade a remarcacao de exames e agenda de imagem.",
      "Risco elevado em cadeia fria, no-show e custo de redistribuicao entre unidades.",
      "Relatorios orientados para operacao regional e central de servicos compartilhados.",
    ],
    toolModules: [
      { route: "/machines", name: "Maquinas", metric: "Ativos monitorados", deliverable: "Inventario multiunidade com risco e disponibilidade", value: "74 ativos" },
      { route: "/health-checks", name: "Health Checks", metric: "Checks automatizados", deliverable: "Autotestes, temperatura, latencia e cadeia fria", value: "486 checks/dia" },
      { route: "/alerts", name: "Alertas", metric: "Alertas criticos", deliverable: "Fila de riscos por unidade e responsavel", value: "3 criticos" },
      { route: "/tickets", name: "Tickets", metric: "Chamados abertos", deliverable: "Visao consolidada de backlog e ETA", value: "11 chamados" },
      { route: "/maintenance", name: "Manutencao", metric: "PM compliance", deliverable: "Planejamento regional com bloqueio de agenda", value: "93%" },
      { route: "/metrics", name: "Metricas", metric: "Uptime", deliverable: "Disponibilidade por unidade e modalidade", value: "98,74%" },
      { route: "/intel", name: "Radar", metric: "Sinais externos", deliverable: "Recalls e tendencias de fabricantes", value: "9 sinais ativos" },
      { route: "/access-control", name: "Controle de Acesso", metric: "Usuarios ativos", deliverable: "Governanca entre central e unidades", value: "14 usuarios" },
      { route: "/history", name: "Historico", metric: "Eventos rastreados", deliverable: "Auditoria de resposta e remarcacoes", value: "184 eventos/30d" },
      { route: "/notifications", name: "Notificacoes", metric: "Acoes direcionadas", deliverable: "Alertas de agenda e cadeia fria", value: "28 notificacoes" },
    ],
    reports: [
      { id: "regional-ops", title: "Relatorio regional de unidades", cadence: "Semanal", audience: "Gerencia regional", sections: ["Status por unidade", "Backlog por modalidade", "Impacto em agenda", "Plano da semana"], outcome: "Equaliza capacidade e reduz remarcacao." },
      { id: "cold-chain", title: "Relatorio de cadeia fria", cadence: "Diario", audience: "Laboratorio e qualidade", sections: ["Alarmes de temperatura", "Tempo fora da faixa", "Ativos reincidentes", "Acoes executadas"], outcome: "Mitiga perda de insumos e amostras." },
      { id: "executive-network", title: "Resumo executivo da rede", cadence: "Mensal", audience: "Diretoria", sections: ["Uptime por modalidade", "Economia evitada", "Unidades de maior risco", "Plano de investimento"], outcome: "Mostra impacto economico em rede distribuida." },
      { id: "vendor-review", title: "Pacote para fornecedor", cadence: "Sob demanda", audience: "Fornecedor OEM", sections: ["Linha do tempo", "Telemetria associada", "Recorrencia", "Peças sugeridas"], outcome: "Acelera tratativa tecnica com OEM." },
    ],
    machines: [
      { id: "CT-07", name: "Tomografo 128 canais", location: "Unidade Centro", status: "warning", lastCheck: "ha 7 min", risk: "alto" },
      { id: "MRI-03", name: "Ressonancia 3T", location: "Unidade Norte", status: "online", lastCheck: "ha 2 min", risk: "moderado" },
      { id: "FRIO-09", name: "Freezer de reagentes", location: "Lab Matriz", status: "warning", lastCheck: "ha 4 min", risk: "alto" },
      { id: "US-14", name: "Ultrassom premium", location: "Unidade Sul", status: "online", lastCheck: "ha 5 min", risk: "baixo" },
    ],
    healthChecks: [
      { id: 1, machine: "Tomografo 128 canais", check: "Temperatura do gantry", result: "WARNING", value: "38,7 C", time: "ha 7 min" },
      { id: 2, machine: "Freezer de reagentes", check: "Temperatura interna", result: "WARNING", value: "-18 C fora da faixa", time: "ha 4 min" },
      { id: 3, machine: "Ressonancia 3T", check: "Chiller", result: "OK", value: "35,1 C", time: "ha 2 min" },
    ],
    alerts: [
      { id: 1, severity: "critical", message: "Cadeia fria fora da faixa por 11 minutos", machine: "Freezer de reagentes", owner: "Lab Matriz", elapsed: "11 min" },
      { id: 2, severity: "high", message: "Tomografo com tendencia de sobreaquecimento", machine: "Tomografo 128 canais", owner: "Equipe Centro", elapsed: "39 min" },
      { id: 3, severity: "medium", message: "Ressonancia com preventiva vencendo em 5 dias", machine: "Ressonancia 3T", owner: "Planejamento", elapsed: "1 dia" },
    ],
    tickets: [
      { id: 5201, title: "Tomografo com aumento de temperatura", priority: "high", status: "in_progress", location: "Unidade Centro", assignee: "Felipe Costa", eta: "4h", probableCause: "Ventilacao do ambiente insuficiente", estimatedImpactBRL: 52000 },
      { id: 5202, title: "Freezer de reagentes fora da faixa", priority: "critical", status: "open", location: "Lab Matriz", assignee: "Renata Alves", eta: "1h", probableCause: "Porta mal vedada e compressor sobrecarregado", estimatedImpactBRL: 76000 },
      { id: 5197, title: "Ultrassom sem sincronismo de laudo", priority: "medium", status: "resolved", location: "Unidade Sul", assignee: "Bruno Lima", eta: "concluido", probableCause: "Fila de integracao local", estimatedImpactBRL: 9000 },
    ],
    maintenance: [
      { id: 1, machine: "Ressonancia 3T", type: "Preventiva", window: "14/03 21:00-00:00", technician: "OEM", status: "agendada" },
      { id: 2, machine: "Tomografo 128 canais", type: "Inspecao", window: "hoje 19:30", technician: "Equipe Centro", status: "confirmada" },
      { id: 3, machine: "Freezer de reagentes", type: "Corretiva", window: "imediata", technician: "Renata Alves", status: "em execucao" },
    ],
    users: [
      { id: 1, name: "Felipe Costa", role: "Coordenador regional", status: "ativo" },
      { id: 2, name: "Renata Alves", role: "Tecnica laboratorio", status: "ativo" },
      { id: 3, name: "Bruno Lima", role: "Suporte integracao", status: "ativo" },
    ],
    events: [
      { id: 1, action: "Agenda bloqueada preventivamente", user: "Sistema", resource: "Tomografo 128 canais", time: "2026-03-10 07:10", type: "scheduling" },
      { id: 2, action: "Cadeia fria reconhecida", user: "Renata Alves", resource: "Freezer de reagentes", time: "2026-03-10 06:58", type: "alert" },
      { id: 3, action: "Fornecedor acionado", user: "Felipe Costa", resource: "Ressonancia 3T", time: "2026-03-09 16:40", type: "maintenance" },
    ],
    notifications: [
      { id: 1, title: "Agenda protegida", message: "Sistema bloqueou 12 exames antes de indisponibilidade confirmada do tomografo.", type: "info", createdAt: "2026-03-10T07:10:00Z" },
      { id: 2, title: "Cadeia fria em contencao", message: "Equipe do laboratorio recebeu protocolo de resposta imediata.", type: "warning", createdAt: "2026-03-10T06:58:00Z" },
    ],
    intel: [
      { id: 1, source: "Recall feed", topic: "diagnostic", title: "Atualizacao de seguranca para console de imagem", summary: "Boletim externo sugere correcao preventiva em consoles da mesma familia do parque instalado.", impact: "Reduz risco de parada por software." },
      { id: 2, source: "Setor laboratorio", topic: "cold-chain", title: "Aumento de perdas em cadeia fria em redes descentralizadas", summary: "Comparativos mostram que alarmes acionaveis e rastreabilidade reduzem perdas operacionais.", impact: "Reforca valor do monitoramento continuo." },
    ],
  },
  {
    id: "surgery-expansion",
    name: "Expansao de contrato preditivo em centro cirurgico",
    facility: "Instituto Vida Plena",
    profile: "Hospital com 7 salas cirurgicas e foco na expansao do contrato de preditiva para anestesia, video e gases medicinais.",
    narrative:
      "Cenario orientado para venda consultiva, destacando o antes e depois da expansao contratual com foco em cancelamento de cirurgia, risco reputacional e previsibilidade financeira.",
    monitoredAssets: 52,
    criticalAssets: 21,
    uptime: 99.43,
    mttrMinutes: 31,
    mtbfHours: 1495,
    pmCompliance: 98,
    slaCompliance: 97,
    openTickets: 7,
    criticalAlerts: 2,
    preventedDowntimeHours: 28,
    estimatedSavingsBRL: 287900,
    avoidedLossBRL: 355000,
    benchmarkNotes: [
      "Centrado em sala cirurgica e risco de cancelamento de procedimento.",
      "Entrega material de negocio para patrocinador operacional e financeiro.",
      "Simulacao de estado futuro apos expansao de cobertura preditiva.",
    ],
    toolModules: [
      { route: "/machines", name: "Maquinas", metric: "Ativos cirurgicos", deliverable: "Mapa dos ativos cobertos e descobertos", value: "52 ativos" },
      { route: "/health-checks", name: "Health Checks", metric: "Checks automatizados", deliverable: "Sinais de anestesia, video, gases e energia", value: "338 checks/dia" },
      { route: "/alerts", name: "Alertas", metric: "Alertas criticos", deliverable: "Fila operavel antes da agenda cirurgica", value: "2 criticos" },
      { route: "/tickets", name: "Tickets", metric: "Chamados abertos", deliverable: "Visao de impacto por procedimento e sala", value: "7 chamados" },
      { route: "/maintenance", name: "Manutencao", metric: "PM compliance", deliverable: "Planejamento noturno com bloqueio minimo", value: "98%" },
      { route: "/metrics", name: "Metricas", metric: "Uptime", deliverable: "Disponibilidade e risco por sala cirurgica", value: "99,43%" },
      { route: "/intel", name: "Radar", metric: "Sinais externos", deliverable: "Boletins e recalls aplicaveis ao parque", value: "5 sinais ativos" },
      { route: "/access-control", name: "Controle de Acesso", metric: "Usuarios ativos", deliverable: "Visao compartilhada entre biomedica e centro cirurgico", value: "9 usuarios" },
      { route: "/history", name: "Historico", metric: "Eventos rastreados", deliverable: "Linha do tempo para auditoria e CAPA", value: "121 eventos/30d" },
      { route: "/notifications", name: "Notificacoes", metric: "Acoes direcionadas", deliverable: "Acionamento por sala, tecnico e coordenador", value: "16 notificacoes" },
    ],
    reports: [
      { id: "expansion-case", title: "Caso de expansao contratual", cadence: "Sob demanda", audience: "Diretoria e compras", sections: ["Ativos cobertos x descobertos", "Risco por sala", "Economia projetada", "Roadmap de expansao"], outcome: "Material comercial para fechar expansao com base operacional." },
      { id: "or-ops", title: "Relatorio de operacao do centro cirurgico", cadence: "Semanal", audience: "Coordenacao cirurgica", sections: ["Alertas por sala", "Intervencoes antes da agenda", "Ativos de maior risco", "Pendencias criticas"], outcome: "Evita cancelamentos e reprogramacoes." },
      { id: "monthly-value", title: "Resumo mensal de valor entregue", cadence: "Mensal", audience: "Patrocinador executivo", sections: ["Downtime evitado", "Economia evitada", "SLA", "Indicadores de satisfacao"], outcome: "Mostra valor apos compra e favorece renovacao." },
      { id: "rca-room", title: "Pacote RCA por sala", cadence: "Sob demanda", audience: "Qualidade e biomedica", sections: ["Linha do tempo", "Ativo afetado", "Causa provavel", "Plano de mitigacao"], outcome: "Padroniza resposta a ocorrencias de sala." },
    ],
    machines: [
      { id: "OR-AN-02", name: "Estacao de anestesia A2", location: "Sala 2", status: "warning", lastCheck: "ha 3 min", risk: "alto" },
      { id: "OR-VID-04", name: "Torre de video 4K", location: "Sala 4", status: "online", lastCheck: "ha 2 min", risk: "moderado" },
      { id: "GAS-CC-01", name: "Painel de gases medicinais", location: "Corredor central", status: "online", lastCheck: "ha 1 min", risk: "alto" },
    ],
    healthChecks: [
      { id: 1, machine: "Estacao de anestesia A2", check: "Fluxo inspiratorio", result: "WARNING", value: "desvio 4,8%", time: "ha 3 min" },
      { id: 2, machine: "Painel de gases medicinais", check: "Pressao", result: "OK", value: "normal", time: "ha 1 min" },
      { id: 3, machine: "Torre de video 4K", check: "Autoteste", result: "OK", value: "aprovado", time: "ha 2 min" },
    ],
    alerts: [
      { id: 1, severity: "critical", message: "Desvio de fluxo em estacao de anestesia antes da primeira cirurgia", machine: "Estacao de anestesia A2", owner: "Equipe plantao", elapsed: "18 min" },
      { id: 2, severity: "high", message: "Painel de gases com tendencia de desgaste em valvula", machine: "Painel de gases medicinais", owner: "Biomedica", elapsed: "4 h" },
    ],
    tickets: [
      { id: 6101, title: "Estacao de anestesia com desvio de fluxo", priority: "critical", status: "in_progress", location: "Sala 2", assignee: "Equipe plantao", eta: "90 min", probableCause: "Valvula proporcional com desgaste", estimatedImpactBRL: 112000 },
      { id: 6098, title: "Torre de video com preventive due", priority: "medium", status: "open", location: "Sala 4", assignee: "Andre Nunes", eta: "8h", probableCause: "Janela de preventiva vencendo", estimatedImpactBRL: 14000 },
    ],
    maintenance: [
      { id: 1, machine: "Estacao de anestesia A2", type: "Corretiva", window: "imediata", technician: "Equipe plantao", status: "em execucao" },
      { id: 2, machine: "Painel de gases medicinais", type: "Preventiva", window: "15/03 23:00", technician: "Andre Nunes", status: "agendada" },
    ],
    users: [
      { id: 1, name: "Patricia Lima", role: "Gerente cirurgica", status: "ativo" },
      { id: 2, name: "Andre Nunes", role: "Biomedico", status: "ativo" },
      { id: 3, name: "Equipe plantao", role: "Tecnico", status: "ativo" },
    ],
    events: [
      { id: 1, action: "Cirurgia protegida por troca preventiva", user: "Sistema", resource: "Estacao de anestesia A2", time: "2026-03-10 06:41", type: "operations" },
      { id: 2, action: "Plano CAPA emitido", user: "Andre Nunes", resource: "Painel de gases medicinais", time: "2026-03-09 17:30", type: "maintenance" },
    ],
    notifications: [
      { id: 1, title: "Sala 2 em contencao", message: "Fluxo de anestesia monitorado antes da primeira cirurgia do dia.", type: "warning", createdAt: "2026-03-10T06:41:00Z" },
      { id: 2, title: "Expansao contratual recomendada", message: "Simulacao mostra ganho anual estimado acima de R$ 280 mil com cobertura adicional.", type: "info", createdAt: "2026-03-09T18:10:00Z" },
    ],
    intel: [
      { id: 1, source: "Boletim tecnico", topic: "anesthesia", title: "Falhas intermitentes em componentes de fluxo podem elevar cancelamento cirurgico", summary: "Sinal externo reforca necessidade de inspeção preventiva em estacoes da mesma familia.", impact: "Ajuda a vender expansao de cobertura." },
      { id: 2, source: "Benchmark de operacao", topic: "or-efficiency", title: "Janela noturna reduz impacto em agenda de sala", summary: "Planejamento orientado por risco diminui cancelamentos e horas improdutivas.", impact: "Sustenta proposta executiva." },
    ],
  },
];

export function formatCurrencyBRL(value: number): string {
  return metricCurrency(value);
}