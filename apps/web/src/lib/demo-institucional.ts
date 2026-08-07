export type SceneId = "dashboard" | "tickets" | "logs" | "metrics" | "roi";

export type DemoStep = {
  id: string;
  scene: SceneId;
  title: string;
  durationMs: number;
  narration: string;
  caption: string;
  focusLabel: string;
  x: number;
  y: number;
  click?: boolean;
};

export const DEMO_STEPS: DemoStep[] = [
  {
    id: "dashboard-risk",
    scene: "dashboard",
    title: "Abertura executiva",
    durationMs: 7000,
    narration:
      "Bem-vindo ao FPConnect. A demonstração começa no painel executivo, onde o cliente enxerga pressão operacional, ativos críticos e o ponto exato que exige resposta imediata.",
    caption:
      "O cursor abre a conversa pela dor operacional: backlog crítico, incidentes abertos e impacto visível em ativos sensíveis.",
    focusLabel: "Card de tickets críticos",
    x: 36,
    y: 31,
    click: true,
  },
  {
    id: "ticket-create",
    scene: "tickets",
    title: "Criação orientada de ticket",
    durationMs: 7500,
    narration:
      "Na tela de tickets, a operação registra a falha em segundos. O sistema sugere prioridade, estima prazo de resposta e organiza o chamado com linguagem de negócio clara para o cliente.",
    caption:
      "A simulação mostra criação de chamado com priorização sugerida automaticamente para acelerar triagem e SLA.",
    focusLabel: "Botão criar ticket",
    x: 69,
    y: 33,
    click: true,
  },
  {
    id: "ticket-triage",
    scene: "tickets",
    title: "Fila priorizada para ação",
    durationMs: 6500,
    narration:
      "Depois de criado, o ticket aparece no topo da fila com risco classificado. Isso ajuda a equipe a mostrar, ao vivo, como o produto transforma ruído operacional em ordem de execução.",
    caption:
      "A fila se reorganiza para destacar o novo chamado crítico e a resposta prevista, reforçando ganho operacional imediato.",
    focusLabel: "Linha do ticket crítico recém-criado",
    x: 69,
    y: 56,
  },
  {
    id: "logs-audit",
    scene: "logs",
    title: "Trilha auditável e exportável",
    durationMs: 7500,
    narration:
      "Em seguida, a demonstração abre a trilha auditável. Aqui o cliente vê quem registrou o evento, quando a ação ocorreu e como o histórico pode ser exportado para PDF, Excel ou imagem.",
    caption:
      "Os logs reforçam governança, rastreabilidade e capacidade de auditoria para equipes clínicas, operacionais e de qualidade.",
    focusLabel: "Botão exportar PDF do histórico",
    x: 24,
    y: 28,
    click: true,
  },
  {
    id: "metrics-explain",
    scene: "metrics",
    title: "Explicação guiada dos indicadores",
    durationMs: 8500,
    narration:
      "Na sequência, o FPConnect explica o que cada dado do relatório significa. Uptime mede disponibilidade real. M T B F indica confiabilidade entre falhas. M T T R mostra a velocidade de recuperação. Alertas sinalizam risco antes da quebra.",
    caption:
      "A leitura é institucional: cada métrica recebe contexto de negócio, efeito operacional e conexão com disponibilidade assistencial.",
    focusLabel: "Cards de métricas com explicação",
    x: 32,
    y: 28,
  },
  {
    id: "report-export",
    scene: "metrics",
    title: "Relatório pronto para comitê",
    durationMs: 6500,
    narration:
      "Com um clique, o operador exporta um relatório pronto para diretoria, coordenação ou engenharia clínica. A apresentação deixa claro que a plataforma já sai da demo com argumento comercial acionável.",
    caption:
      "A exportação fecha a ponte entre operação, pós-venda e decisão executiva sem depender de planilhas externas.",
    focusLabel: "Botão exportar relatório",
    x: 22,
    y: 42,
    click: true,
  },
  {
    id: "roi-close",
    scene: "roi",
    title: "Fechamento comercial em ROI",
    durationMs: 9000,
    narration:
      "A etapa final transforma a narrativa em valor. O cliente vê perda evitada, horas de downtime protegidas e retorno sobre investimento. Esta é a tela ideal para fechar a reunião e encaminhar expansão contratual.",
    caption:
      "A demo termina em proposta de valor: disponibilidade protegida, economia comprovável e próximo passo comercial claro.",
    focusLabel: "Card principal de ROI",
    x: 31,
    y: 31,
  },
];

export const KPI_EXPLANATIONS = [
  {
    label: "Uptime médio",
    value: "99,2%",
    description: "Percentual do tempo em que a frota ficou disponível para operação clínica sem interrupção crítica.",
  },
  {
    label: "MTBF",
    value: "1.240 h",
    description: "Tempo médio entre falhas. Quanto maior, mais previsível e estável está o parque monitorado.",
  },
  {
    label: "MTTR",
    value: "18 min",
    description: "Tempo médio para restaurar a operação depois de uma falha, refletindo agilidade de resposta.",
  },
  {
    label: "Alertas em 7 dias",
    value: "34",
    description: "Sinais capturados antes da quebra total, usados para antecipar manutenção e reduzir indisponibilidade.",
  },
];