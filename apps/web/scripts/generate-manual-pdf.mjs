import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { jsPDF } from "jspdf";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outputDir = path.join(__dirname, "..", "public", "downloads");
const outputFile = path.join(outputDir, "fpconnect-manual-institucional.pdf");
const screenshotsDir = path.join(__dirname, "..", "public", "manual-screens");

const theme = {
  ink: [15, 23, 42],
  slate: [71, 85, 105],
  border: [203, 213, 225],
  panel: [248, 250, 252],
  white: [255, 255, 255],
  blue: [37, 99, 235],
  cyan: [8, 145, 178],
  emerald: [5, 150, 105],
  amber: [217, 119, 6],
  rose: [225, 29, 72],
  navy: [7, 19, 44],
  sky: [239, 246, 255],
  sand: [255, 251, 235],
  blush: [254, 242, 242],
};

const routes = [
  ["/dashboard", "Dashboard", "Resumo do dia, cards prioritarios e atalhos para o restante do fluxo."],
  ["/machines", "Maquinas", "Consulta do parque por nome, ID, localizacao, status e ultimo check."],
  ["/health-checks", "Health Checks", "Leituras automaticas com resultado OK, WARNING e FAIL."],
  ["/alerts", "Alertas", "Fila de eventos por severidade com acao de reconhecimento."],
  ["/tickets", "Tickets", "Abertura, filtragem, priorizacao e encerramento de chamados."],
  ["/maintenance", "Manutencao", "Agenda preventiva, corretiva e calibracao."],
  ["/metrics", "Metricas", "KPIs, graficos e exportacoes executivas."],
  ["/history", "Historico", "Linha do tempo auditavel com pesquisa, filtro e paginacao."],
  ["/settings", "Configuracoes", "Perfil, timezone, preferencias e notificacoes."],
];

const dailyRoutine = [
  "Comece pelo Dashboard para identificar criticos, tickets abertos e tendencias rapidas.",
  "Valide o estado real do equipamento em Maquinas antes de agir sobre um alerta.",
  "Cruze os sintomas com Health Checks para separar ruido de falha confirmada.",
  "Use Alertas para priorizar resposta e reconhecer somente o que ja tem responsavel.",
  "Abra ou atualize Tickets com prioridade, ETA e feedback de execucao.",
  "Finalize com Metricas e Historico para reportar resultado e exportar evidencias.",
];

const ticketSteps = [
  "Abra a rota /tickets e localize o formulario de criacao no topo da tela.",
  "Digite o titulo do chamado. O sistema sugere a prioridade com base no texto inserido.",
  "Opcionalmente informe uma descricao com sintomas, local e contexto clinico.",
  "Revise a prioridade sugerida e a previsao de resolucao exibida ao usuario.",
  "Clique em Create para registrar o ticket e inclui-lo na lista do backlog.",
  "Use SearchBar e FilterBar para filtrar por prioridade e status.",
  "Ao concluir o trabalho, registre feedback e marque o ticket como resolvido.",
];

const metricGlossary = [
  ["Uptime", "Percentual de tempo em que o ativo ou parque permaneceu disponivel."],
  ["MTBF", "Tempo medio entre falhas. Quanto maior, mais confiavel e o equipamento."],
  ["MTTR", "Tempo medio de recuperacao. Quanto menor, mais rapida foi a resposta."],
  ["Alertas 7d", "Quantidade de alertas recentes. Crescimento abrupto pede investigacao."],
];

const exportGuide = [
  ["PDF", "Ideal para relatorio executivo, envio formal e documentacao visual."],
  ["Excel", "Melhor opcao para analise tabular, filtros adicionais e consolidacao."],
  ["PNG", "Util para inserir graficos em apresentacoes ou mensagens rapidas."],
];

const bestPractices = [
  "Nao reconheca alertas sem definir claramente quem assumiu a analise.",
  "Evite ticket duplicado pesquisando por maquina, localizacao e sintoma antes de criar.",
  "Use feedback de encerramento objetivo para fortalecer auditoria e pos-analise.",
  "Padronize fuso horario e preferencias em Configuracoes antes de emitir relatorios.",
  "Historico deve ser consultado antes de discutir causa raiz ou escalonamento externo.",
];

const screenshotFiles = {
  dashboard: path.join(screenshotsDir, "dashboard.png"),
  machines: path.join(screenshotsDir, "machines.png"),
  tickets: path.join(screenshotsDir, "tickets.png"),
  history: path.join(screenshotsDir, "history.png"),
};

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function setFill(doc, color) {
  doc.setFillColor(...color);
}

function setDraw(doc, color) {
  doc.setDrawColor(...color);
}

function setText(doc, color) {
  doc.setTextColor(...color);
}

function pageSize(doc) {
  return {
    width: doc.internal.pageSize.getWidth(),
    height: doc.internal.pageSize.getHeight(),
  };
}

function drawHeader(doc, pageNumber, label) {
  const { width } = pageSize(doc);
  setFill(doc, theme.navy);
  doc.roundedRect(12, 10, width - 24, 14, 4, 4, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  setText(doc, theme.white);
  doc.text("FPConnect RCA Copilot", 18, 18.8);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.5);
  setText(doc, [191, 219, 254]);
  doc.text(label, width - 18, 16.2, { align: "right" });
  doc.text(`Pagina ${pageNumber}`, width - 18, 20.2, { align: "right" });
}

function drawFooter(doc) {
  const { width, height } = pageSize(doc);
  setDraw(doc, theme.border);
  doc.line(14, height - 12, width - 14, height - 12);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  setText(doc, theme.slate);
  doc.text("Manual de uso do software", 14, height - 6.2);
  doc.text("http://localhost:3000/downloads/fpconnect-manual-institucional.pdf", width - 14, height - 6.2, { align: "right" });
}

function drawTitle(doc, title, subtitle) {
  doc.setFont("helvetica", "bold");
  doc.setFontSize(23);
  setText(doc, theme.ink);
  doc.text(title, 16, 38);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  setText(doc, theme.slate);
  doc.text(doc.splitTextToSize(subtitle, 176), 16, 46);
}

function paragraph(doc, text, x, y, width, size = 10, color = theme.slate, leading = 5.3) {
  doc.setFont("helvetica", "normal");
  doc.setFontSize(size);
  setText(doc, color);
  const lines = doc.splitTextToSize(text, width);
  doc.text(lines, x, y);
  return y + lines.length * leading;
}

function section(doc, title, x, y) {
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  setText(doc, theme.ink);
  doc.text(title, x, y);
  setDraw(doc, theme.border);
  doc.line(x, y + 2, x + 52, y + 2);
  return y + 8;
}

function bulletList(doc, items, x, y, width, tone = theme.cyan) {
  let currentY = y;
  items.forEach((item) => {
    setFill(doc, tone);
    doc.circle(x + 1.8, currentY - 1.2, 1.3, "F");
    currentY = paragraph(doc, item, x + 6, currentY, width - 6, 9.4, theme.slate, 4.9) + 1.5;
  });
  return currentY;
}

function numberedList(doc, items, x, y, width, tone = theme.blue) {
  let currentY = y;
  items.forEach((item, index) => {
    setFill(doc, tone);
    doc.circle(x + 2.5, currentY - 1.4, 2.3, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(7.8);
    setText(doc, theme.white);
    doc.text(String(index + 1), x + 1.1, currentY + 0.4);
    currentY = paragraph(doc, item, x + 8, currentY, width - 8, 9.4, theme.slate, 4.9) + 1.5;
  });
  return currentY;
}

function infoBox(doc, title, text, x, y, w, h, fill, accent) {
  setFill(doc, fill);
  doc.roundedRect(x, y, w, h, 6, 6, "F");
  setFill(doc, accent);
  doc.roundedRect(x, y, 4, h, 4, 4, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  setText(doc, theme.ink);
  doc.text(title, x + 8, y + 9);
  paragraph(doc, text, x + 8, y + 16, w - 12, 9.1, theme.slate, 4.8);
}

function statCard(doc, x, y, w, h, label, value, tone) {
  setFill(doc, tone);
  doc.roundedRect(x, y, w, h, 6, 6, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  setText(doc, theme.white);
  doc.text(label.toUpperCase(), x + 4, y + 8);
  doc.setFontSize(17);
  doc.text(value, x + 4, y + 19);
}

function table(doc, headers, rows, x, y, widths, rowHeight = 11) {
  let currentY = y;
  const totalWidth = widths.reduce((sum, value) => sum + value, 0);
  setFill(doc, theme.navy);
  doc.roundedRect(x, currentY, totalWidth, rowHeight, 3, 3, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.2);
  setText(doc, theme.white);
  let cursorX = x + 3;
  headers.forEach((header, index) => {
    doc.text(header, cursorX, currentY + 6.2, { maxWidth: widths[index] - 6 });
    cursorX += widths[index];
  });
  currentY += rowHeight + 1;

  rows.forEach((row, rowIndex) => {
    setFill(doc, rowIndex % 2 === 0 ? theme.white : theme.panel);
    doc.roundedRect(x, currentY, totalWidth, rowHeight, 2, 2, "F");
    let cellX = x + 3;
    row.forEach((cell, index) => {
      doc.setFont("helvetica", index === 0 ? "bold" : "normal");
      doc.setFontSize(8);
      setText(doc, theme.ink);
      doc.text(String(cell), cellX, currentY + 5.8, { maxWidth: widths[index] - 6 });
      cellX += widths[index];
    });
    currentY += rowHeight + 1;
  });

  return currentY;
}

function readImageAsDataUri(filePath) {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  const stats = fs.statSync(filePath);
  if (!stats.size) {
    return null;
  }
  return `data:image/png;base64,${fs.readFileSync(filePath).toString("base64")}`;
}

function drawScreenshot(doc, filePath, x, y, w, h, caption) {
  setFill(doc, theme.white);
  doc.roundedRect(x, y, w, h, 6, 6, "F");
  const imageData = readImageAsDataUri(filePath);
  if (imageData) {
    doc.addImage(imageData, "PNG", x + 2, y + 2, w - 4, h - 12, undefined, "FAST");
  } else {
    setFill(doc, theme.panel);
    doc.roundedRect(x + 2, y + 2, w - 4, h - 12, 4, 4, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    setText(doc, theme.slate);
    doc.text("Captura nao disponivel", x + w / 2, y + h / 2 - 4, { align: "center" });
  }
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  setText(doc, theme.ink);
  doc.text(caption, x + 3, y + h - 4);
}

function dashboardMock(doc, x, y, w, h) {
  setFill(doc, theme.panel);
  doc.roundedRect(x, y, w, h, 8, 8, "F");
  setFill(doc, theme.navy);
  doc.roundedRect(x + 2, y + 2, 38, h - 4, 7, 7, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  setText(doc, theme.white);
  doc.text("Navegacao", x + 7, y + 11);
  ["Dashboard", "Maquinas", "Alertas", "Tickets", "Metricas", "Historico"].forEach((item, index) => {
    const top = y + 20 + index * 9;
    setFill(doc, index === 0 ? theme.cyan : [14, 30, 58]);
    doc.roundedRect(x + 5, top, 28, 6, 3, 3, "F");
    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    setText(doc, theme.white);
    doc.text(item, x + 8, top + 4.1);
  });

  setFill(doc, theme.white);
  doc.roundedRect(x + 44, y + 7, w - 50, 22, 6, 6, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  setText(doc, theme.ink);
  doc.text("Dashboard", x + 50, y + 16);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.2);
  setText(doc, theme.slate);
  doc.text("Ponto de partida para entender prioridade e decidir para onde navegar.", x + 50, y + 23, { maxWidth: w - 60 });

  statCard(doc, x + 44, y + 34, 31, 23, "Tickets", "12", theme.amber);
  statCard(doc, x + 79, y + 34, 31, 23, "Criticos", "2", theme.rose);
  statCard(doc, x + 114, y + 34, 31, 23, "Resolvidos", "8", theme.emerald);
  statCard(doc, x + 149, y + 34, 31, 23, "Em prog.", "5", theme.blue);

  setFill(doc, theme.white);
  doc.roundedRect(x + 44, y + 64, 66, 30, 6, 6, "F");
  doc.roundedRect(x + 114, y + 64, 66, 30, 6, 6, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  setText(doc, theme.ink);
  doc.text("Como ler", x + 49, y + 73);
  doc.text("Proximo clique", x + 119, y + 73);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  setText(doc, theme.slate);
  doc.text("1. Veja cards\n2. Abra o desvio\n3. Aprofunde", x + 49, y + 81);
  doc.text("Critico -> Tickets\nRuido -> Health Checks\nEvidencia -> Historico", x + 119, y + 81);
}

function createManual() {
  ensureDir(outputDir);
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const { width } = pageSize(doc);

  for (let index = 0; index < 8; index += 1) {
    setFill(doc, [6 + index * 6, 18 + index * 5, 42 + index * 7]);
    doc.rect(0, index * 37, width, 37, "F");
  }
  setFill(doc, theme.cyan);
  doc.circle(width - 22, 28, 20, "F");
  setFill(doc, theme.blue);
  doc.circle(width - 6, 58, 16, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  setText(doc, [186, 230, 253]);
  doc.text("MANUAL DE USO", 16, 22);
  doc.setFontSize(30);
  setText(doc, theme.white);
  doc.text("FPConnect RCA Copilot", 16, 38);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.text("Guia pratico para ensinar como usar o software, navegar entre modulos, tratar incidentes, interpretar KPIs e exportar evidencias.", 16, 50, { maxWidth: 134 });
  infoBox(doc, "Finalidade", "Este PDF foi desenhado para treinamento. Ele explica o fluxo real de uso do produto e pode ser entregue a quem vai operar ou demonstrar o sistema.", 16, 64, 92, 30, theme.white, theme.cyan);
  infoBox(doc, "Perfil de uso", "Coordenacao clinica, tecnico de campo, operacao, qualidade e time comercial que precise mostrar a logica do software com seguranca.", 112, 64, 84, 30, theme.white, theme.emerald);
  statCard(doc, 16, 104, 41, 26, "Ativos", "186", theme.blue);
  statCard(doc, 61, 104, 41, 26, "Criticos", "47", theme.rose);
  statCard(doc, 106, 104, 41, 26, "Uptime", "99,21%", theme.emerald);
  statCard(doc, 151, 104, 45, 26, "Tickets", "18", theme.amber);
  infoBox(doc, "Link de download", "http://localhost:3000/downloads/fpconnect-manual-institucional.pdf", 16, 140, 180, 20, theme.white, theme.blue);
  let y = section(doc, "O que o leitor aprende", 16, 176);
  bulletList(doc, [
    "Como iniciar pelo Dashboard e usar o menu lateral corretamente.",
    "Como validar o estado de maquinas e leituras automaticas antes de agir.",
    "Como criar, filtrar, priorizar e fechar tickets.",
    "Como interpretar metricas, historico e exportacoes.",
  ], 16, y, 176, theme.cyan);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 2, "Mapa do sistema");
  drawTitle(doc, "1. Visao geral do software", "Comece entendendo qual e o papel de cada tela. Isso evita usar o modulo errado para uma necessidade operacional.");
  y = 62;
  y = section(doc, "Estrutura de navegacao", 16, y);
  y = paragraph(doc, "O menu lateral e o eixo principal do sistema. O Dashboard resume a situacao atual; os demais modulos aprofundam monitoramento, resposta e evidencia. A navegacao ideal vai do macro para o detalhe e do alerta para a acao.", 16, y, 176) + 4;
  y = table(doc, ["Rota", "Tela", "Quando abrir"], routes, 16, y, [30, 34, 116], 11) + 4;
  infoBox(doc, "Sequencia recomendada", "Para treinar um novo usuario, siga: Dashboard -> Maquinas -> Health Checks -> Alertas -> Tickets -> Metricas -> Historico -> Configuracoes.", 16, y, 180, 24, theme.sand, theme.amber);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 3, "Primeiros passos");
  drawTitle(doc, "2. Como comecar no dia a dia", "O Dashboard e o ponto de partida e o menu lateral indica para onde aprofundar conforme a necessidade.");
  if (readImageAsDataUri(screenshotFiles.dashboard)) {
    drawScreenshot(doc, screenshotFiles.dashboard, 14, 58, 182, 102, "Tela real do Dashboard");
  } else {
    dashboardMock(doc, 14, 58, 182, 102);
  }
  y = section(doc, "Fluxo de leitura inicial", 16, 174);
  y = numberedList(doc, [
    "Abra o Dashboard e leia primeiro os cards de topo. Eles destacam tickets abertos, criticos, em progresso e resolvidos.",
    "Se houver numero critico, clique no card ou siga imediatamente para Tickets.",
    "Se a duvida for sobre o estado tecnico do ativo, va para Maquinas ou Health Checks antes de abrir um chamado novo.",
    "Se a intencao for demonstrar o produto para terceiros, use Simulacoes; para operacao real, use os modulos funcionais do menu.",
  ], 16, y, 176, theme.blue);
  infoBox(doc, "Leitura correta do Dashboard", "Os cards coloridos nao sao apenas indicadores. Eles funcionam como atalhos operacionais. Um card vermelho de criticos deve levar o usuario diretamente a fila correspondente de tickets ou alertas.", 16, 242, 180, 18, theme.sky, theme.blue);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 4, "Telas reais");
  drawTitle(doc, "2A. Capturas reais do sistema", "Abaixo estao telas reais do ambiente local, incorporadas ao manual para aproximar o treinamento da experiencia visual do produto.");
  drawScreenshot(doc, screenshotFiles.machines, 14, 58, 88, 76, "Maquinas");
  drawScreenshot(doc, screenshotFiles.tickets, 108, 58, 88, 76, "Tickets");
  drawScreenshot(doc, screenshotFiles.history, 14, 144, 88, 76, "Historico");
  infoBox(doc, "Como usar estas imagens", "Use estas capturas para orientar o olhar do usuario durante o treinamento. Primeiro mostre o layout da tela e depois execute o passo a passo descrito nas paginas seguintes.", 108, 144, 88, 36, theme.sand, theme.amber);
  infoBox(doc, "Observacao", "As capturas foram geradas localmente do proprio software e servem como referencia visual do ambiente atual de demonstracao.", 108, 184, 88, 36, theme.sky, theme.blue);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 5, "Monitoramento");
  drawTitle(doc, "3. Monitoramento do parque", "As rotas Maquinas, Health Checks e Alertas formam o bloco de observacao do sistema. Use essas tres telas antes de agir na execucao.");
  y = 60;
  y = section(doc, "Maquinas", 16, y);
  y = paragraph(doc, "Na rota /machines o usuario pesquisa equipamentos por nome, ID e localizacao. Tambem filtra por status e tipo. Essa tela responde rapidamente onde esta o ativo, qual e seu estado e quando ocorreu o ultimo contato.", 16, y, 176) + 3;
  infoBox(doc, "Como usar", "1. Pesquise a maquina. 2. Confirme a localizacao. 3. Leia o status. 4. Verifique o ultimo check. 5. So depois decida abrir ticket ou seguir para Health Checks.", 16, y, 84, 24, theme.sky, theme.blue);
  infoBox(doc, "Como interpretar", "Online indica comunicacao normal. Warning sinaliza desvio ou degradacao. Offline aponta perda de comunicacao ou indisponibilidade e pede validacao imediata.", 112, y, 84, 24, theme.blush, theme.rose);
  y += 34;
  y = section(doc, "Health Checks", 16, y);
  y = paragraph(doc, "Na rota /health-checks o sistema mostra leituras automaticas por equipamento, como conectividade, bateria, temperatura e autoteste. O filtro por ALL, OK, WARNING e FAIL ajuda a separar normalidade de falha tecnica confirmada.", 16, y, 176) + 2;
  y = bulletList(doc, [
    "OK: sem acao imediata.",
    "WARNING: atencao, mas precisa de contexto antes de escalonar.",
    "FAIL: falha confirmada, normalmente associada a alerta ou ticket.",
  ], 16, y, 176, theme.emerald) + 2;
  y = section(doc, "Alertas", 16, y);
  y = paragraph(doc, "Na rota /alerts a equipe acompanha a fila por severidade, mensagem, maquina e tempo decorrido. O botao Reconhecer serve para indicar que alguem assumiu o tratamento do evento, e nao para encerrar o problema.", 16, y, 176) + 2;
  bulletList(doc, [
    "Critical e high devem ser tratados primeiro.",
    "Use filtros por severidade e status para trabalhar a fila pendente.",
    "Nunca reconheca um alerta sem responsavel definido.",
  ], 16, y, 176, theme.rose);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 6, "Execucao operacional");
  drawTitle(doc, "4. Tickets e manutencao", "Depois de confirmar a necessidade de acao, o proximo passo e organizar a execucao em tickets e agenda de manutencao.");
  y = 60;
  y = section(doc, "Como abrir e tratar tickets", 16, y);
  y = numberedList(doc, ticketSteps, 16, y, 176, theme.blue);
  infoBox(doc, "Prioridade automatica", "O sistema eleva titulos com termos como offline, falha ou erro para niveis mais altos. O usuario pode revisar manualmente, mas a sugestao acelera triagem e padroniza a fila.", 16, y + 1, 180, 24, theme.sand, theme.amber);
  y += 34;
  y = section(doc, "Como usar Manutencao", 16, y);
  y = paragraph(doc, "Na rota /maintenance o usuario enxerga as intervencoes agendadas e pode abrir o modal de Agendar Manutencao. O formulario pede maquina, tipo e data. Isso organiza preventivas, corretivas e calibracoes em uma agenda visivel para a equipe.", 16, y, 176) + 2;
  bulletList(doc, [
    "Use Preventiva para rotinas programadas.",
    "Use Corretiva quando a acao nasceu de falha ou incidente.",
    "Use Calibracao quando o objetivo for conformidade tecnica ou regulatoria.",
  ], 16, y, 176, theme.cyan);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 7, "Analise e evidencia");
  drawTitle(doc, "5. Metricas, relatorios e historico", "Esses modulos transformam operacao em evidencia. Eles explicam performance, consolidam auditoria e geram material exportavel.");
  y = 60;
  y = section(doc, "Metricas", 16, y);
  y = paragraph(doc, "Na rota /metrics o usuario encontra cards de KPI, graficos e botoes de exportacao. A tela tambem oferece ajuda contextual e pode solicitar permissao para notificacoes inteligentes. Use essa area para leitura executiva e para explicar o comportamento do parque ao longo do tempo.", 16, y, 176) + 3;
  y = table(doc, ["Indicador", "Como ler"], metricGlossary, 16, y, [34, 146], 11) + 4;
  y = table(doc, ["Exportacao", "Uso recomendado"], exportGuide, 16, y, [32, 148], 11) + 3;
  y = section(doc, "Historico", 16, y);
  y = paragraph(doc, "Na rota /history o sistema registra eventos como ticket criado, alerta reconhecido, manutencao agendada, usuario criado e falha em health check. A pesquisa, os filtros e a paginacao ajudam a reconstruir a linha do tempo de um incidente sem depender de memoria ou planilhas paralelas.", 16, y, 176) + 2;
  bulletList(doc, [
    "Pesquise por acao, usuario ou recurso.",
    "Filtre por tipo para isolar tickets, alertas, manutencao ou health checks.",
    "Exporte PDF, Excel ou PNG quando precisar compartilhar evidencia.",
  ], 16, y, 176, theme.emerald);
  drawFooter(doc);

  doc.addPage();
  drawHeader(doc, 8, "Rotina recomendada");
  drawTitle(doc, "6. Rotina de uso e boas praticas", "Esta pagina fecha o manual com uma rotina operacional simples e regras praticas para evitar erros comuns.");
  y = 60;
  y = section(doc, "Rotina diaria sugerida", 16, y);
  y = numberedList(doc, dailyRoutine, 16, y, 176, theme.cyan) + 3;
  y = section(doc, "Configuracoes e governanca", 16, y);
  y = paragraph(doc, "Na rota /settings o usuario ajusta perfil, senha, timezone, preferencias do sistema e notificacoes. Essas definicoes impactam a consistencia dos alertas, dos horarios exibidos e da experiencia do time. Faca esse ajuste antes de formalizar relatorios ou treinar um novo operador.", 16, y, 176) + 2;
  y = section(doc, "Boas praticas", 16, y);
  y = bulletList(doc, bestPractices, 16, y, 176, theme.amber) + 3;
  infoBox(doc, "Encerramento", "Se alguem perguntar como usar o sistema em uma frase: comece no Dashboard, valide o estado em Maquinas e Health Checks, aja por Alertas e Tickets, e feche o ciclo com Metricas e Historico.", 16, y, 180, 24, theme.sky, theme.blue);
  drawFooter(doc);

  doc.save(outputFile);
  return outputFile;
}

console.log(createManual());