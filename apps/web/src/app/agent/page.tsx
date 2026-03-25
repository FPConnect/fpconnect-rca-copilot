"use client";

import Link from "next/link";
import { Suspense, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Bar, Pie } from "react-chartjs-2";
import html2canvas from "html2canvas";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";
import jsPDF from "jspdf";
import * as XLSX from "xlsx";
import {
  ArrowRight,
  BellRing,
  CalendarClock,
  ClipboardList,
  Download,
  Gauge,
  History,
  Monitor,
  Radar,
  ShieldCheck,
  Sparkles,
  Ticket,
  Users,
} from "lucide-react";

import {
  SIMULATOR_SCENARIOS,
  formatCurrencyBRL,
  type SimulatorScenario,
} from "@/lib/simulator-data";
import { addReportBranding, getReportContentBox } from "@/lib/report-branding";

Chart.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

type TabKey = "overview" | "operations" | "reports" | "deliverables";
type PdfAudience = "executive" | "operations" | "engineering";

type PdfScenarioTheme = {
  gradient: string;
  badge: string;
  card: string;
  accentLabel: string;
  monogram: string;
  clientLabel: string;
};

type PdfAudienceProfile = {
  label: string;
  shortLabel: string;
  badgeTone: string;
  summary: string;
  focus: string[];
  proposalTitle: string;
  proposalSummary: string;
  deliverableHeadline: string;
};

const TAB_LABELS: Array<{ key: TabKey; label: string }> = [
  { key: "overview", label: "Resumo" },
  { key: "operations", label: "Operacao" },
  { key: "reports", label: "Relatorios" },
  { key: "deliverables", label: "Pos-venda" },
];

const PDF_TOTAL_PAGES = 4;

const PDF_AUDIENCE_PROFILES: Record<PdfAudience, PdfAudienceProfile> = {
  executive: {
    label: "Diretoria e patrocinador executivo",
    shortLabel: "Executivo",
    badgeTone: "bg-slate-900 text-white border-slate-900",
    summary: "Leitura de valor, risco protegido, governanca e narrativa de renovacao ou expansao contratual.",
    focus: ["ROI e perda evitada", "risco assistencial protegido", "valor de pos-venda"],
    proposalTitle: "Proposta executiva de valor continuo",
    proposalSummary: "Organiza uma leitura pronta para diretoria, conectando uptime, perda evitada e capacidade de sustentar renovacao ou expansao.",
    deliverableHeadline: "Pacote executivo pronto para comite e patrocinador",
  },
  operations: {
    label: "Coordenacao operacional e servicos",
    shortLabel: "Operacao",
    badgeTone: "bg-blue-50 text-blue-900 border-blue-200",
    summary: "Leitura para backlog, SLA, agenda de manutencao, contencao e impacto diario na operacao assistencial.",
    focus: ["fila priorizada", "SLA e agenda", "capacidade de resposta"],
    proposalTitle: "Plano operacional de ativacao e rotina",
    proposalSummary: "Traduz o simulador em uma rotina de operacao com responsavel, cadence de reuniao e blocos de resposta acionavel.",
    deliverableHeadline: "Pacote operacional para rotina de campo e coordenacao",
  },
  engineering: {
    label: "Engenharia clinica e qualidade tecnica",
    shortLabel: "Engenharia",
    badgeTone: "bg-emerald-50 text-emerald-900 border-emerald-200",
    summary: "Leitura tecnica para RCA, manutencao baseada em risco, evidencias de campo e rastreabilidade auditavel.",
    focus: ["causa provavel e RCA", "manutencao baseada em risco", "trilha auditavel"],
    proposalTitle: "Plano tecnico de cobertura e RCA",
    proposalSummary: "Empacota causa provavel, janelas de manutencao e governanca tecnica para acelerar implantacao e auditoria.",
    deliverableHeadline: "Pacote tecnico para engenharia clinica e qualidade",
  },
};

const PDF_SCENARIO_THEMES: Record<string, PdfScenarioTheme> = {
  "tertiary-hospital": {
    gradient: "from-slate-950 via-blue-950 to-cyan-900",
    badge: "text-cyan-100 border-white/20 bg-white/10",
    card: "border-cyan-200 bg-cyan-50 text-cyan-950",
    accentLabel: "Operacao hospitalar critica",
    monogram: "SG",
    clientLabel: "Hospital Sao Gabriel",
  },
  "diagnostic-network": {
    gradient: "from-slate-950 via-emerald-950 to-teal-800",
    badge: "text-emerald-100 border-white/20 bg-white/10",
    card: "border-emerald-200 bg-emerald-50 text-emerald-950",
    accentLabel: "Rede de diagnostico distribuida",
    monogram: "RD",
    clientLabel: "Rede Diagnostica Prime",
  },
  "surgery-expansion": {
    gradient: "from-slate-950 via-violet-950 to-fuchsia-900",
    badge: "text-fuchsia-100 border-white/20 bg-white/10",
    card: "border-fuchsia-200 bg-fuchsia-50 text-fuchsia-950",
    accentLabel: "Expansao cirurgica e contrato",
    monogram: "CC",
    clientLabel: "Centro Cirurgico Horizonte",
  },
};

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-slate-600">{subtitle}</p> : null}
      </div>
      {children}
    </div>
  );
}

function PdfFooter({
  page,
  scenarioLabel,
  exportDate,
  totalPages,
}: {
  page: number;
  scenarioLabel: string;
  exportDate: string;
  totalPages: number;
}) {
  return (
    <div className="mt-8 flex items-center justify-between border-t border-slate-200 pt-4 text-xs text-slate-500">
      <div>{scenarioLabel}</div>
      <div>Gerado em {exportDate}</div>
      <div>
        Pagina {page} de {totalPages}
      </div>
    </div>
  );
}

function exportScenarioExcel(scenario: SimulatorScenario) {
  const workbook = XLSX.utils.book_new();

  const kpiSheet = XLSX.utils.json_to_sheet([
    {
      facility: scenario.facility,
      scenario: scenario.name,
      uptime_pct: scenario.uptime,
      mttr_minutes: scenario.mttrMinutes,
      mtbf_hours: scenario.mtbfHours,
      pm_compliance_pct: scenario.pmCompliance,
      sla_compliance_pct: scenario.slaCompliance,
      open_tickets: scenario.openTickets,
      critical_alerts: scenario.criticalAlerts,
      prevented_downtime_hours: scenario.preventedDowntimeHours,
      estimated_savings_brl: scenario.estimatedSavingsBRL,
      avoided_loss_brl: scenario.avoidedLossBRL,
    },
  ]);

  XLSX.utils.book_append_sheet(workbook, kpiSheet, "KPIs");
  XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(scenario.machines), "Machines");
  XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(scenario.alerts), "Alerts");
  XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(scenario.tickets), "Tickets");
  XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(scenario.maintenance), "Maintenance");
  XLSX.utils.book_append_sheet(workbook, XLSX.utils.json_to_sheet(scenario.reports), "Reports");

  XLSX.writeFile(workbook, `fpconnect-simulador-${scenario.id}.xlsx`);
}

function exportScenarioJson(scenario: SimulatorScenario) {
  const blob = new Blob([JSON.stringify(scenario, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `fpconnect-simulador-${scenario.id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function SimulationCenterContent() {
  const searchParams = useSearchParams();
  const ticketTitle = searchParams.get("title");
  const ticketPriority = searchParams.get("priority");
  const ticketStatus = searchParams.get("status");
  const ticketLocation = searchParams.get("location");
  const requestedScenario = searchParams.get("scenario");

  const defaultScenario =
    SIMULATOR_SCENARIOS.find((scenario) => scenario.id === requestedScenario)?.id ??
    SIMULATOR_SCENARIOS[0].id;

  const [scenarioId, setScenarioId] = useState(defaultScenario);
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [pdfAudience, setPdfAudience] = useState<PdfAudience>("executive");
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const pdfReportRef = useRef<HTMLDivElement | null>(null);

  const scenario =
    SIMULATOR_SCENARIOS.find((item) => item.id === scenarioId) ?? SIMULATOR_SCENARIOS[0];
  const scenarioTheme = PDF_SCENARIO_THEMES[scenario.id] ?? PDF_SCENARIO_THEMES["tertiary-hospital"];
  const audienceProfile = PDF_AUDIENCE_PROFILES[pdfAudience];
  const exportDate = new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date());

  const ticketImpactData = useMemo(() => {
    return {
      labels: scenario.tickets.map((item) => `#${item.id}`),
      datasets: [
        {
          label: "Impacto financeiro estimado (BRL)",
          data: scenario.tickets.map((item) => item.estimatedImpactBRL),
          backgroundColor: scenario.tickets.map((item) =>
            item.priority === "critical"
              ? "#dc2626"
              : item.priority === "high"
                ? "#f97316"
                : item.priority === "medium"
                  ? "#eab308"
                  : "#22c55e",
          ),
        },
      ],
    };
  }, [scenario]);

  const assetStatusData = useMemo(() => {
    const online = scenario.machines.filter((item) => item.status === "online").length;
    const warning = scenario.machines.filter((item) => item.status === "warning").length;
    const offline = scenario.machines.filter((item) => item.status === "offline").length;

    return {
      labels: ["Online", "Warning", "Offline"],
      datasets: [
        {
          data: [online, warning, offline],
          backgroundColor: ["#22c55e", "#eab308", "#ef4444"],
        },
      ],
    };
  }, [scenario]);

  const topRiskTickets = useMemo(() => {
    return [...scenario.tickets].sort((left, right) => right.estimatedImpactBRL - left.estimatedImpactBRL);
  }, [scenario]);

  const contextualTicket = useMemo(() => {
    const matchByTitle = ticketTitle
      ? scenario.tickets.find((item) => item.title.toLowerCase() === ticketTitle.toLowerCase())
      : undefined;

    return {
      title: matchByTitle?.title ?? ticketTitle,
      priority: matchByTitle?.priority ?? ticketPriority,
      status: matchByTitle?.status ?? ticketStatus,
      location: matchByTitle?.location ?? ticketLocation,
      assignee: matchByTitle?.assignee,
      eta: matchByTitle?.eta,
      probableCause: matchByTitle?.probableCause,
      estimatedImpactBRL: matchByTitle?.estimatedImpactBRL,
    };
  }, [scenario.tickets, ticketLocation, ticketPriority, ticketStatus, ticketTitle]);

  const saleFlowSteps = [
    "1. Abrir o cenario e mostrar o parque monitorado, ativos criticos e risco atual.",
    "2. Entrar em Tickets para provar priorizacao, ETA e impacto financeiro por incidente.",
    "3. Mostrar Radar e Historico para conectar contexto externo com governanca interna.",
    "4. Fechar com Relatorios e o valor economico do pos-venda, nao apenas com dashboards.",
  ];

  const proposalItems = [
    {
      label: "Escopo recomendado",
      value: `${scenario.monitoredAssets} ativos monitorados`,
      detail: `${scenario.criticalAssets} ativos criticos cobertos com priorizacao por risco.`,
    },
    {
      label: "Valor protegido",
      value: formatCurrencyBRL(scenario.avoidedLossBRL),
      detail: "Perda operacional evitada quando o backlog e tratado com telemetria, contexto e SLA.",
    },
    {
      label: "Valor entregue",
      value: formatCurrencyBRL(scenario.estimatedSavingsBRL),
      detail: "Economia estimada com downtime evitado, manutencao coordenada e resposta mais rapida.",
    },
  ];

  const nextStepCards = [
    {
      title: "Fase 1 | Kickoff e baseline",
      text: "Inventario validado, responsabilidades, ativos criticos e baseline de uptime, SLA e pendencias.",
    },
    {
      title: "Fase 2 | Ativacao operacional",
      text: "Alertas, tickets, manutencao, notificacoes e ritual de acompanhamento por publico definido.",
    },
    {
      title: "Fase 3 | Valor continuo",
      text: "Relatorios recorrentes, RCA, pacote executivo e expansao sustentada por resultado.",
    },
  ];

  const deliverableItems = [
    { icon: Monitor, title: "Painel vivo do parque", text: "Disponibilidade, risco e checks automatizados por equipamento." },
    { icon: Ticket, title: "Fila de tickets com SLA", text: "Chamados priorizados por impacto, ETA e perda evitada." },
    { icon: CalendarClock, title: "Agenda de manutencao", text: "Janelas preventivas, corretivas e calibracoes com responsavel." },
    { icon: Radar, title: "Radar externo", text: "Recalls e sinais publicos conectados ao inventario monitorado." },
    { icon: BellRing, title: "Notificacoes acionaveis", text: "Acionamento por tecnico, coordenacao e diretoria conforme contexto." },
    { icon: History, title: "Historico auditavel", text: "Linha do tempo pronta para RCA, qualidade e tratativa com fornecedor." },
    { icon: Users, title: "Governanca", text: "Perfis, acessos e responsabilizacao entre times internos e terceiros." },
    { icon: ClipboardList, title: "Relatorios exportaveis", text: "PDF, Excel e pacotes executivos prontos para reuniao." },
  ];

  const handleExportScenarioPdf = async () => {
    if (!pdfReportRef.current || isExportingPdf) return;

    setIsExportingPdf(true);
    try {
      await new Promise((resolve) => window.setTimeout(resolve, 250));

      const pages = Array.from(
        pdfReportRef.current.querySelectorAll<HTMLElement>("[data-pdf-page='true']"),
      );

      if (pages.length === 0) return;

      const doc = new jsPDF("p", "mm", "a4");
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 8;
      const maxWidth = pageWidth - margin * 2;
      const maxHeight = pageHeight - margin * 2;

      for (const [index, page] of pages.entries()) {
        const canvas = await html2canvas(page, {
          scale: 2,
          backgroundColor: "#ffffff",
          useCORS: true,
          logging: false,
          windowWidth: page.scrollWidth,
          windowHeight: page.scrollHeight,
        });

        const imgData = canvas.toDataURL("image/png");
        if (index > 0) {
          doc.addPage();
        }

        await addReportBranding(doc, {
          title: `Pacote executivo FPConnect | ${scenario.label}`,
          subtitle: `Visão preparada para ${PDF_AUDIENCE_PROFILES[pdfAudience].label.toLowerCase()}.`,
          rightLabel: PDF_AUDIENCE_PROFILES[pdfAudience].shortLabel,
          pageNumber: index + 1,
          totalPages: pages.length,
        });

        const contentBox = getReportContentBox(doc);
        const ratio = Math.min(contentBox.width / canvas.width, contentBox.height / canvas.height);
        const imgWidth = canvas.width * ratio;
        const imgHeight = canvas.height * ratio;
        const x = contentBox.x + (contentBox.width - imgWidth) / 2;
        const y = contentBox.y + (contentBox.height - imgHeight) / 2;

        doc.addImage(imgData, "PNG", x, y, imgWidth, imgHeight, undefined, "FAST");
      }

      doc.save(`fpconnect-simulador-${scenario.id}-${pdfAudience}.pdf`);
    } finally {
      setIsExportingPdf(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 space-y-6">
      <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8 text-white shadow-sm">
        <div className="absolute -right-10 top-0 h-40 w-40 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-32 w-32 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-cyan-100">
              <Sparkles size={14} />
              Centro de Simulacao FPConnect
            </div>
            <h1 className="mt-4 text-3xl md:text-4xl font-bold leading-tight">
              Simulador integrado de todas as ferramentas do software, com entregas de pos-venda, relatorios e metricas prontas para demo comercial.
            </h1>
            <p className="mt-4 max-w-3xl text-sm md:text-base leading-relaxed text-slate-200">
              Os cenarios abaixo foram montados para parecer o ambiente que o cliente vera apos a compra: operacao monitorada, tickets priorizados, manutencao planejada, radar externo, governanca, auditoria e material executivo exportavel.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleExportScenarioPdf}
              className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 hover:bg-slate-100"
            >
              <Download size={16} />
              {isExportingPdf ? "Gerando PDF..." : "PDF executivo"}
            </button>
            <button
              onClick={() => exportScenarioExcel(scenario)}
              className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/15"
            >
              <Download size={16} />
              Excel operacional
            </button>
            <button
              onClick={() => exportScenarioJson(scenario)}
              className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/15"
            >
              <Download size={16} />
              JSON tecnico
            </button>
          </div>
        </div>
      </div>

      <SectionCard
        title="Versao do PDF"
        subtitle="Escolha a leitura que sera exportada para o cliente ou para a reuniao interna. O simulador online nao muda; apenas o pacote PDF muda."
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {(Object.entries(PDF_AUDIENCE_PROFILES) as Array<[PdfAudience, PdfAudienceProfile]>).map(([key, profile]) => (
            <button
              key={key}
              type="button"
              onClick={() => setPdfAudience(key)}
              className={`rounded-2xl border p-4 text-left transition ${
                pdfAudience === key
                  ? "border-slate-900 bg-slate-900 text-white shadow-sm"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-semibold">{profile.label}</div>
                <span
                  className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold ${
                    pdfAudience === key ? "border-white/20 bg-white/10 text-white" : profile.badgeTone
                  }`}
                >
                  {profile.shortLabel}
                </span>
              </div>
              <div className={`mt-3 text-sm ${pdfAudience === key ? "text-slate-200" : "text-slate-600"}`}>
                {profile.summary}
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {profile.focus.map((focusItem) => (
                  <span
                    key={focusItem}
                    className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${
                      pdfAudience === key ? "bg-white/10 text-white" : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {focusItem}
                  </span>
                ))}
              </div>
            </button>
          ))}
        </div>
      </SectionCard>

      {(ticketTitle || ticketPriority || ticketStatus || ticketLocation) && (
        <SectionCard
          title="Simulacao contextual iniciada a partir de um ticket"
          subtitle="Este bloco reproduz como o software apresentaria o caso para operacao, engenharia clinica e diretoria."
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-sm">
            <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
              <div className="text-slate-500">Ticket</div>
              <div className="mt-1 font-semibold text-slate-900">{ticketTitle ?? "Nao informado"}</div>
            </div>
            <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
              <div className="text-slate-500">Prioridade</div>
              <div className="mt-1 font-semibold text-slate-900">{ticketPriority ?? "Nao informada"}</div>
            </div>
            <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
              <div className="text-slate-500">Status</div>
              <div className="mt-1 font-semibold text-slate-900">{ticketStatus ?? "Nao informado"}</div>
            </div>
            <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
              <div className="text-slate-500">Local</div>
              <div className="mt-1 font-semibold text-slate-900">{ticketLocation ?? "Nao informado"}</div>
            </div>
          </div>
        </SectionCard>
      )}

      <SectionCard
        title="Escolha o cenario"
        subtitle="Troque o contexto para simular hospital geral, rede de diagnostico ou expansao contratual em centro cirurgico."
      >
        <div className="grid grid-cols-1 lg:grid-cols-[1.3fr_1fr] gap-4">
          <div className="space-y-3">
            {SIMULATOR_SCENARIOS.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setScenarioId(item.id)}
                className={`w-full rounded-2xl border p-4 text-left transition ${
                  item.id === scenario.id
                    ? "border-blue-600 bg-blue-50 shadow-sm"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="text-sm font-semibold text-slate-900">{item.name}</div>
                <div className="mt-1 text-sm text-slate-600">{item.profile}</div>
              </button>
            ))}
          </div>
          <div className="rounded-2xl bg-slate-50 border border-slate-200 p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-blue-700">Perfil selecionado</div>
                {isExportingPdf ? "Gerando PDF..." : `PDF ${audienceProfile.shortLabel.toLowerCase()}`}
            <p className="mt-2 text-sm leading-relaxed text-slate-600">{scenario.narrative}</p>
            <div className="mt-4 space-y-2 text-sm text-slate-700">
              {scenario.benchmarkNotes.map((note) => (
                <div key={note} className="rounded-xl bg-white px-3 py-2 border border-slate-100">
                  {note}
                </div>
              ))}
            </div>
          </div>
        </div>
      </SectionCard>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {[
          { label: "Uptime", value: `${scenario.uptime.toFixed(2)}%`, icon: Gauge },
          { label: "MTTR", value: `${scenario.mttrMinutes} min`, icon: Ticket },
          { label: "PM compliance", value: `${scenario.pmCompliance}%`, icon: CalendarClock },
          { label: "SLA", value: `${scenario.slaCompliance}%`, icon: ShieldCheck },
          { label: "Downtime evitado", value: `${scenario.preventedDowntimeHours} h`, icon: Monitor },
          { label: "Economia estimada", value: formatCurrencyBRL(scenario.estimatedSavingsBRL), icon: Sparkles },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs uppercase tracking-wide">{label}</span>
              <Icon size={16} />
            </div>
            <div className="mt-3 text-2xl font-bold text-slate-900">{value}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {TAB_LABELS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
              activeTab === tab.key
                ? "bg-slate-900 text-white"
                : "bg-white border border-slate-200 text-slate-700 hover:bg-slate-50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr] gap-6">
          <SectionCard
            title="Cobertura do software"
            subtitle="Cada modulo abaixo representa o que o cliente passa a ver e operar apos a ativacao do ambiente."
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {scenario.toolModules.map((module) => (
                <Link
                  key={module.route}
                  href={module.route}
                  className="rounded-2xl border border-slate-200 bg-slate-50 p-4 hover:border-blue-300 hover:bg-blue-50 transition"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-slate-900">{module.name}</div>
                      <div className="mt-1 text-xs text-slate-500">{module.metric}</div>
                    </div>
                    <span className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-blue-700 border border-blue-100">
                      {module.value}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-slate-600">{module.deliverable}</p>
                </Link>
              ))}
            </div>
          </SectionCard>

          <div className="space-y-6">
            <SectionCard
              title="Impacto financeiro dos tickets"
              subtitle="O simulador trata chamados como objetos operacionais e executivos, com ETA, causa provavel e perda evitada."
            >
              <Bar
                data={ticketImpactData}
                options={{
                  responsive: true,
                  plugins: { legend: { display: false } },
                }}
              />
            </SectionCard>
            <SectionCard
              title="Status do parque"
              subtitle="Mistura de ativos online, sob observacao e indisponiveis no momento."
            >
              <div className="mx-auto max-w-[280px]">
                <Pie
                  data={assetStatusData}
                  options={{
                    responsive: true,
                    plugins: { legend: { position: "bottom" } },
                  }}
                />
              </div>
            </SectionCard>
          </div>
        </div>
      )}

      {activeTab === "operations" && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <SectionCard title="Parque monitorado" subtitle="Amostra do que a equipe acompanha no painel de ativos.">
            <div className="space-y-3">
              {scenario.machines.map((machine) => (
                <div key={machine.id} className="rounded-xl border border-slate-200 p-4 bg-slate-50">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-slate-900">{machine.name}</div>
                      <div className="text-sm text-slate-600">{machine.id} | {machine.location}</div>
                    </div>
                    <div className="flex gap-2 text-xs">
                      <span className="rounded-full bg-white px-2.5 py-1 border border-slate-200 text-slate-700">status: {machine.status}</span>
                      <span className="rounded-full bg-white px-2.5 py-1 border border-slate-200 text-slate-700">risco: {machine.risk}</span>
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-slate-500">Ultimo check {machine.lastCheck}</div>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Alertas e checks" subtitle="Fila de sinais que alimenta a operacao diaria e o escalonamento.">
            <div className="space-y-4">
              {scenario.alerts.map((alert) => (
                <div key={alert.id} className="rounded-xl border border-slate-200 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-semibold text-slate-900">{alert.message}</div>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                      {alert.severity}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-slate-600">{alert.machine} | owner: {alert.owner} | aberto ha {alert.elapsed}</div>
                </div>
              ))}
              <div className="rounded-xl bg-slate-50 border border-slate-200 p-4">
                <div className="text-sm font-semibold text-slate-900 mb-3">Ultimos health checks</div>
                <div className="space-y-2 text-sm text-slate-600">
                  {scenario.healthChecks.map((check) => (
                    <div key={check.id} className="flex items-center justify-between gap-3 rounded-lg bg-white border border-slate-100 px-3 py-2">
                      <span>{check.machine} - {check.check}</span>
                      <span className="font-semibold text-slate-900">{check.result}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Tickets e impacto" subtitle="Chamados com ETA, causa provavel e impacto financeiro estimado.">
            <div className="space-y-3">
              {topRiskTickets.map((ticketItem) => (
                <div key={ticketItem.id} className="rounded-xl border border-slate-200 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold text-slate-900">#{ticketItem.id} - {ticketItem.title}</div>
                      <div className="mt-1 text-sm text-slate-600">{ticketItem.location} | {ticketItem.assignee} | ETA {ticketItem.eta}</div>
                    </div>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                      {ticketItem.priority}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="rounded-lg bg-slate-50 px-3 py-2 border border-slate-100">
                      <div className="text-slate-500">Causa provavel</div>
                      <div className="font-medium text-slate-900">{ticketItem.probableCause}</div>
                    </div>
                    <div className="rounded-lg bg-slate-50 px-3 py-2 border border-slate-100">
                      <div className="text-slate-500">Impacto estimado</div>
                      <div className="font-medium text-slate-900">{formatCurrencyBRL(ticketItem.estimatedImpactBRL)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Manutencao, notificacoes e trilha" subtitle="Recorrencia operacional apos a compra do software.">
            <div className="space-y-4">
              <div>
                <div className="text-sm font-semibold text-slate-900 mb-2">Agenda de manutencao</div>
                <div className="space-y-2 text-sm text-slate-600">
                  {scenario.maintenance.map((item) => (
                    <div key={item.id} className="rounded-lg bg-slate-50 border border-slate-100 px-3 py-2">
                      {item.machine} | {item.type} | {item.window} | {item.status}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900 mb-2">Notificacoes que o cliente recebe</div>
                <div className="space-y-2 text-sm text-slate-600">
                  {scenario.notifications.map((item) => (
                    <div key={item.id} className="rounded-lg bg-white border border-slate-200 px-3 py-2">
                      <div className="font-medium text-slate-900">{item.title}</div>
                      <div>{item.message}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900 mb-2">Historico auditavel</div>
                <div className="space-y-2 text-sm text-slate-600">
                  {scenario.events.map((item) => (
                    <div key={item.id} className="rounded-lg bg-white border border-slate-200 px-3 py-2">
                      {item.time} | {item.action} | {item.resource}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </SectionCard>
        </div>
      )}

      {activeTab === "reports" && (
        <div className="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6">
          <SectionCard title="Relatorios reais que o cliente recebe" subtitle="O simulador entrega material operacional, executivo, de conformidade e RCA.">
            <div className="space-y-4">
              {scenario.reports.map((report) => (
                <div key={report.id} className="rounded-2xl border border-slate-200 p-5 bg-slate-50">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-semibold text-slate-900">{report.title}</div>
                      <div className="mt-1 text-sm text-slate-600">{report.cadence} | {report.audience}</div>
                    </div>
                    <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                      pronto para exportacao
                    </span>
                  </div>
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-slate-600">
                    {report.sections.map((section) => (
                      <div key={section} className="rounded-lg bg-white border border-slate-100 px-3 py-2">
                        {section}
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 rounded-xl bg-white border border-blue-100 px-4 py-3 text-sm text-slate-700">
                    <span className="font-semibold text-slate-900">Resultado:</span> {report.outcome}
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Exemplo de leitura executiva" subtitle="Como apresentar valor para diretoria usando os mesmos dados da operacao.">
            <div className="space-y-4 text-sm text-slate-700">
              <div className="rounded-2xl bg-emerald-50 border border-emerald-200 p-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-emerald-700">Valor entregue no periodo</div>
                <div className="mt-2 text-2xl font-bold text-emerald-900">{formatCurrencyBRL(scenario.estimatedSavingsBRL)}</div>
                <p className="mt-2">Economia estimada combinando downtime evitado, deslocamentos reduzidos e protecao de agenda clinica.</p>
              </div>
              <div className="rounded-2xl bg-amber-50 border border-amber-200 p-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-amber-700">Risco protegido</div>
                <div className="mt-2 text-2xl font-bold text-amber-900">{formatCurrencyBRL(scenario.avoidedLossBRL)}</div>
                <p className="mt-2">Estimativa de perda operacional evitada por contencao antecipada e manutencao baseada em risco.</p>
              </div>
              <div className="rounded-2xl bg-blue-50 border border-blue-200 p-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-blue-700">Mensagem para o cliente</div>
                <p className="mt-2 leading-relaxed">
                  Depois da compra, o cliente nao recebe apenas alertas. Ele recebe backlog priorizado, material executivo, trilha auditavel, agenda de manutencao e contexto externo que sustentam decisoes clinicas e financeiras.
                </p>
              </div>
            </div>
          </SectionCard>
        </div>
      )}

      {activeTab === "deliverables" && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <SectionCard title="O que o cliente passa a receber apos a compra" subtitle="Pacote pos-venda estruturado para operacao, lideranca e renovacao contratual.">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {deliverableItems.map(({ icon: Icon, title, text }) => (
                <div key={title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white border border-slate-200 text-slate-800">
                    <Icon size={18} />
                  </div>
                  <div className="mt-3 font-semibold text-slate-900">{title}</div>
                  <div className="mt-1 text-sm text-slate-600">{text}</div>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Fluxo sugerido para venda" subtitle="Sequencia curta para apresentar problema, diagnostico, acao e valor.">
            <div className="space-y-4">
              {[
                ...saleFlowSteps,
              ].map((step) => (
                <div key={step} className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
                  {step}
                </div>
              ))}
              <div className="rounded-2xl bg-slate-900 text-white p-5">
                <div className="text-sm font-semibold">Atalhos rapidos</div>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Link href="/tickets" className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-100">
                    Abrir tickets
                    <ArrowRight size={16} />
                  </Link>
                  <Link href="/demo-recursos" className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white hover:bg-white/15">
                    Abrir ROI e relatorios
                    <ArrowRight size={16} />
                  </Link>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>
      )}

      <SectionCard title="Ferramentas relacionadas" subtitle="Use estas rotas durante a apresentacao para abrir o detalhe operacional de cada modulo.">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
          {scenario.toolModules.map((module) => (
            <Link
              key={module.route}
              href={module.route}
              className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 hover:border-blue-300 hover:text-blue-700 transition"
            >
              {module.name}
            </Link>
          ))}
        </div>
        <div className="mt-4 text-xs text-slate-500">
          Observacao: os cenarios foram organizados para demonstracao comercial e simulacao operacional realista, preservando o fluxo que o cliente tera depois da implantacao.
        </div>
      </SectionCard>

      <div className="fixed -left-[99999px] top-0 pointer-events-none opacity-100" aria-hidden="true">
        <div ref={pdfReportRef} className="w-[1120px] bg-white text-slate-900">
          <section data-pdf-page="true" className="min-h-[1560px] p-10 bg-white">
            <div className={`rounded-[32px] bg-gradient-to-br ${scenarioTheme.gradient} p-10 text-white`}>
              <div className="flex items-start justify-between gap-6">
                <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${scenarioTheme.badge}`}>
                  <Sparkles size={14} />
                  FPConnect Simulation Report
                </div>
                <div className="flex items-center gap-3">
                  <div className="rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-center">
                    <div className="text-[10px] uppercase tracking-[0.25em] text-white/60">FPConnect</div>
                    <div className="mt-1 text-xl font-bold">FP</div>
                  </div>
                  <div className="rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-center">
                    <div className="text-[10px] uppercase tracking-[0.25em] text-white/60">Cliente</div>
                    <div className="mt-1 text-xl font-bold">{scenarioTheme.monogram}</div>
                  </div>
                </div>
              </div>
              <div className="mt-5 flex items-start justify-between gap-6">
                <div className="max-w-2xl">
                  <div className="text-sm uppercase tracking-[0.2em] text-white/70">{scenarioTheme.accentLabel}</div>
                  <h1 className="text-4xl font-bold leading-tight">{scenario.facility}</h1>
                  <p className="mt-3 text-lg text-slate-200">{scenario.name}</p>
                  <p className="mt-4 text-sm leading-relaxed text-slate-200">{scenario.narrative}</p>
                  <div className="mt-6 flex flex-wrap gap-2">
                    <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold text-white">
                      Versao {audienceProfile.shortLabel}
                    </span>
                    {audienceProfile.focus.map((focusItem) => (
                      <span key={focusItem} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/80">
                        {focusItem}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="min-w-[320px] space-y-4">
                  <div className="rounded-3xl bg-white/10 px-6 py-5 border border-white/10">
                    <div className="text-xs uppercase tracking-wide text-white/70">Leitura orientada</div>
                    <div className="mt-3 text-sm leading-relaxed text-white/90">{audienceProfile.summary}</div>
                  </div>
                  <div className="rounded-3xl bg-white text-slate-900 p-5">
                    <div className="flex items-center gap-4">
                      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-950 text-xl font-bold text-white">
                        {scenarioTheme.monogram}
                      </div>
                      <div>
                        <div className="text-xs uppercase tracking-wide text-slate-500">Cliente demonstrado</div>
                        <div className="mt-1 text-lg font-bold text-slate-950">{scenarioTheme.clientLabel}</div>
                        <div className="text-sm text-slate-600">Cenario preparado para venda consultiva e defesa executiva.</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {(contextualTicket.title || contextualTicket.priority || contextualTicket.location) && (
              <div className="mt-8 rounded-[28px] border border-slate-200 bg-slate-50 p-6">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Contexto de entrada</div>
                    <div className="mt-2 text-2xl font-bold text-slate-900">Simulacao iniciada a partir de um ticket</div>
                  </div>
                  <div className={`rounded-full border px-4 py-2 text-sm font-semibold ${scenarioTheme.card}`}>
                    Caso contextual para priorizacao e ROI
                  </div>
                </div>
                <div className="mt-5 grid grid-cols-4 gap-4 text-sm">
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Ticket</div>
                    <div className="mt-2 font-semibold text-slate-900">{contextualTicket.title ?? "Nao informado"}</div>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Prioridade</div>
                    <div className="mt-2 font-semibold text-slate-900">{contextualTicket.priority ?? "Nao informada"}</div>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Status e local</div>
                    <div className="mt-2 font-semibold text-slate-900">{contextualTicket.status ?? "Nao informado"}</div>
                    <div className="mt-1 text-slate-600">{contextualTicket.location ?? "Nao informado"}</div>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Tratativa sugerida</div>
                    <div className="mt-2 font-semibold text-slate-900">{contextualTicket.assignee ?? "Time FPConnect"}</div>
                    <div className="mt-1 text-slate-600">ETA {contextualTicket.eta ?? "a definir"}</div>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-[1.2fr_0.8fr] gap-4 text-sm">
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Hipotese operacional</div>
                    <div className="mt-2 text-slate-700">{contextualTicket.probableCause ?? "O software organiza sinais do parque, backlog e historico para chegar rapidamente na causa provavel e orientar a resposta."}</div>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Impacto estimado</div>
                    <div className="mt-2 text-2xl font-bold text-slate-900">
                      {contextualTicket.estimatedImpactBRL ? formatCurrencyBRL(contextualTicket.estimatedImpactBRL) : formatCurrencyBRL(scenario.estimatedSavingsBRL)}
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="mt-8 grid grid-cols-3 gap-4">
              {[
                { label: "Uptime medio", value: `${scenario.uptime.toFixed(2)}%`, tone: "bg-emerald-50 border-emerald-200 text-emerald-900" },
                { label: "PM compliance", value: `${scenario.pmCompliance}%`, tone: "bg-blue-50 border-blue-200 text-blue-900" },
                { label: "SLA compliance", value: `${scenario.slaCompliance}%`, tone: "bg-violet-50 border-violet-200 text-violet-900" },
                { label: "MTTR", value: `${scenario.mttrMinutes} min`, tone: "bg-amber-50 border-amber-200 text-amber-900" },
                { label: "Downtime evitado", value: `${scenario.preventedDowntimeHours} h`, tone: "bg-slate-50 border-slate-200 text-slate-900" },
                { label: "Economia estimada", value: formatCurrencyBRL(scenario.estimatedSavingsBRL), tone: "bg-rose-50 border-rose-200 text-rose-900" },
              ].map((item) => (
                <div key={item.label} className={`rounded-3xl border p-5 ${item.tone}`}>
                  <div className="text-xs uppercase tracking-wide opacity-80">{item.label}</div>
                  <div className="mt-3 text-3xl font-bold">{item.value}</div>
                </div>
              ))}
            </div>

            <div className="mt-8 grid grid-cols-[1.2fr_0.8fr] gap-6">
              <div className="rounded-3xl border border-slate-200 p-6">
                <div className="text-lg font-semibold text-slate-900">Impacto financeiro dos tickets</div>
                <p className="mt-1 text-sm text-slate-600">Chamados priorizados por perda evitada, ETA e criticidade.</p>
                <div className="mt-4">
                  <Bar data={ticketImpactData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
                </div>
              </div>
              <div className="rounded-3xl border border-slate-200 p-6">
                <div className="text-lg font-semibold text-slate-900">Status do parque</div>
                <p className="mt-1 text-sm text-slate-600">Distribuicao de ativos em operacao, observacao e indisponibilidade.</p>
                <div className="mt-4">
                  <Pie data={assetStatusData} options={{ responsive: true, plugins: { legend: { position: "bottom" } } }} />
                </div>
              </div>
            </div>

            <div className="mt-8 grid grid-cols-2 gap-6">
              <div className="rounded-3xl border border-slate-200 p-6 bg-slate-50">
                <div className="text-lg font-semibold text-slate-900">Leituras executivas</div>
                <div className="mt-4 space-y-3 text-sm text-slate-700">
                  {scenario.benchmarkNotes.map((note) => (
                    <div key={note} className="rounded-2xl bg-white border border-slate-200 px-4 py-3">
                      {note}
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-3xl border border-slate-200 p-6 bg-slate-50">
                <div className="text-lg font-semibold text-slate-900">Resumo de valor</div>
                <div className="mt-4 space-y-4 text-sm text-slate-700">
                  <div className="rounded-2xl bg-white border border-emerald-200 px-4 py-4">
                    <div className="text-xs uppercase tracking-wide text-emerald-700">Valor entregue</div>
                    <div className="mt-2 text-2xl font-bold text-emerald-900">{formatCurrencyBRL(scenario.estimatedSavingsBRL)}</div>
                  </div>
                  <div className="rounded-2xl bg-white border border-amber-200 px-4 py-4">
                    <div className="text-xs uppercase tracking-wide text-amber-700">Perda evitada</div>
                    <div className="mt-2 text-2xl font-bold text-amber-900">{formatCurrencyBRL(scenario.avoidedLossBRL)}</div>
                  </div>
                </div>
              </div>
            </div>

            <PdfFooter page={1} scenarioLabel={`${scenario.facility} | ${audienceProfile.label}`} exportDate={exportDate} totalPages={PDF_TOTAL_PAGES} />
          </section>

          <section data-pdf-page="true" className="min-h-[1560px] p-10 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-blue-700">Operacao simulada</div>
                <h2 className="mt-2 text-3xl font-bold text-slate-900">Backlog, alertas e modulos do produto</h2>
              </div>
              <div className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700">
                {scenario.openTickets} tickets | {scenario.criticalAlerts} alertas criticos
              </div>
            </div>

            <div className="mt-8 rounded-3xl border border-slate-200 p-6 bg-slate-50">
              <div className="text-lg font-semibold text-slate-900">Cobertura de modulos</div>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                {scenario.toolModules.map((module) => (
                  <div key={module.route} className="rounded-2xl bg-white border border-slate-200 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-semibold text-slate-900">{module.name}</div>
                        <div className="mt-1 text-slate-500">{module.metric}</div>
                      </div>
                      <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                        {module.value}
                      </span>
                    </div>
                    <div className="mt-3 text-slate-600">{module.deliverable}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 grid grid-cols-2 gap-6">
              <div className="rounded-3xl border border-slate-200 p-6">
                <div className="text-lg font-semibold text-slate-900">Top tickets por impacto</div>
                <div className="mt-4 space-y-3 text-sm">
                  {topRiskTickets.map((ticketItem) => (
                    <div key={ticketItem.id} className="rounded-2xl bg-slate-50 border border-slate-200 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="font-semibold text-slate-900">#{ticketItem.id} - {ticketItem.title}</div>
                          <div className="mt-1 text-slate-600">{ticketItem.location} | {ticketItem.assignee} | ETA {ticketItem.eta}</div>
                        </div>
                        <span className="rounded-full bg-white border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700">
                          {ticketItem.priority}
                        </span>
                      </div>
                      <div className="mt-3 grid grid-cols-2 gap-3">
                        <div className="rounded-xl bg-white border border-slate-200 px-3 py-2">
                          <div className="text-xs text-slate-500">Causa provavel</div>
                          <div className="mt-1 font-medium text-slate-900">{ticketItem.probableCause}</div>
                        </div>
                        <div className="rounded-xl bg-white border border-slate-200 px-3 py-2">
                          <div className="text-xs text-slate-500">Impacto estimado</div>
                          <div className="mt-1 font-medium text-slate-900">{formatCurrencyBRL(ticketItem.estimatedImpactBRL)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="rounded-3xl border border-slate-200 p-6">
                  <div className="text-lg font-semibold text-slate-900">Alertas criticos</div>
                  <div className="mt-4 space-y-3 text-sm">
                    {scenario.alerts.map((alert) => (
                      <div key={alert.id} className="rounded-2xl bg-slate-50 border border-slate-200 p-4">
                        <div className="font-semibold text-slate-900">{alert.message}</div>
                        <div className="mt-1 text-slate-600">{alert.machine} | {alert.owner} | {alert.elapsed}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-200 p-6">
                  <div className="text-lg font-semibold text-slate-900">Parque monitorado</div>
                  <div className="mt-4 space-y-2 text-sm">
                    {scenario.machines.map((machine) => (
                      <div key={machine.id} className="rounded-xl bg-slate-50 border border-slate-200 px-3 py-3 flex items-center justify-between gap-3">
                        <div>
                          <div className="font-medium text-slate-900">{machine.name}</div>
                          <div className="text-slate-600">{machine.id} | {machine.location}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold text-slate-900">{machine.status}</div>
                          <div className="text-slate-500">{machine.lastCheck}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <PdfFooter page={2} scenarioLabel={`${scenario.facility} | ${audienceProfile.label}`} exportDate={exportDate} totalPages={PDF_TOTAL_PAGES} />
          </section>

          <section data-pdf-page="true" className="min-h-[1560px] p-10 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-violet-700">Pos-venda e valor continuo</div>
                <h2 className="mt-2 text-3xl font-bold text-slate-900">Relatorios, entregaveis e governanca</h2>
              </div>
              <div className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700">
                {scenario.reports.length} relatorios | {scenario.notifications.length} notificacoes
              </div>
            </div>

            <div className="mt-8 grid grid-cols-2 gap-6">
              <div className="rounded-3xl border border-slate-200 p-6 bg-slate-50">
                <div className="text-lg font-semibold text-slate-900">Relatorios entregues ao cliente</div>
                <div className="mt-4 space-y-4 text-sm">
                  {scenario.reports.map((report) => (
                    <div key={report.id} className="rounded-2xl bg-white border border-slate-200 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="font-semibold text-slate-900">{report.title}</div>
                          <div className="mt-1 text-slate-600">{report.cadence} | {report.audience}</div>
                        </div>
                        <span className="rounded-full bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700 border border-slate-200">
                          pronto
                        </span>
                      </div>
                      <div className="mt-3 grid grid-cols-2 gap-2">
                        {report.sections.map((section) => (
                          <div key={section} className="rounded-xl bg-slate-50 border border-slate-200 px-3 py-2 text-slate-600">
                            {section}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="rounded-3xl border border-slate-200 p-6 bg-slate-50">
                  <div className="text-lg font-semibold text-slate-900">{audienceProfile.deliverableHeadline}</div>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    {deliverableItems.map(({ title, text }) => (
                      <div key={title} className="rounded-2xl bg-white border border-slate-200 p-4">
                        <div className="font-semibold text-slate-900">{title}</div>
                        <div className="mt-2 text-slate-600">{text}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-200 p-6 bg-slate-50">
                  <div className="text-lg font-semibold text-slate-900">Notificacoes e trilha</div>
                  <div className="mt-4 space-y-3 text-sm">
                    {scenario.notifications.map((item) => (
                      <div key={item.id} className="rounded-2xl bg-white border border-slate-200 p-4">
                        <div className="font-semibold text-slate-900">{item.title}</div>
                        <div className="mt-1 text-slate-600">{item.message}</div>
                      </div>
                    ))}
                    {scenario.events.map((item) => (
                      <div key={item.id} className="rounded-2xl bg-white border border-slate-200 p-4 text-slate-600">
                        {item.time} | {item.action} | {item.resource}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-6">
              <div className="text-lg font-semibold text-slate-900">Fluxo sugerido para venda</div>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-700">
                {saleFlowSteps.map((step) => (
                  <div key={step} className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                    {step}
                  </div>
                ))}
              </div>
            </div>

            <PdfFooter page={3} scenarioLabel={`${scenario.facility} | ${audienceProfile.label}`} exportDate={exportDate} totalPages={PDF_TOTAL_PAGES} />
          </section>

          <section data-pdf-page="true" className="min-h-[1560px] p-10 bg-white">
            <div className={`rounded-[32px] border p-8 ${scenarioTheme.card}`}>
              <div className="flex items-start justify-between gap-6">
                <div className="max-w-3xl">
                  <div className="text-xs font-semibold uppercase tracking-[0.2em] opacity-75">Proposta comercial</div>
                  <h2 className="mt-3 text-3xl font-bold">{audienceProfile.proposalTitle}</h2>
                  <p className="mt-4 text-sm leading-relaxed opacity-90">{audienceProfile.proposalSummary}</p>
                </div>
                <div className="rounded-3xl bg-white/70 px-5 py-4 text-right">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Cenario base</div>
                  <div className="mt-1 text-lg font-bold text-slate-950">{scenario.facility}</div>
                  <div className="text-sm text-slate-700">{audienceProfile.shortLabel}</div>
                </div>
              </div>
            </div>

            <div className="mt-8 grid grid-cols-3 gap-4">
              {proposalItems.map((item) => (
                <div key={item.label} className="rounded-3xl border border-slate-200 bg-white p-6">
                  <div className="text-xs uppercase tracking-wide text-slate-500">{item.label}</div>
                  <div className="mt-3 text-3xl font-bold text-slate-900">{item.value}</div>
                  <div className="mt-3 text-sm leading-relaxed text-slate-600">{item.detail}</div>
                </div>
              ))}
            </div>

            <div className="mt-8 grid grid-cols-[1.1fr_0.9fr] gap-6">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                <div className="text-lg font-semibold text-slate-900">Roadmap de ativacao</div>
                <div className="mt-4 space-y-3 text-sm text-slate-700">
                  {nextStepCards.map((item) => (
                    <div key={item.title} className="rounded-2xl border border-slate-200 bg-white p-4">
                      <div className="font-semibold text-slate-900">{item.title}</div>
                      <div className="mt-2">{item.text}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                  <div className="text-lg font-semibold text-slate-900">Mensagem de fechamento</div>
                  <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4 text-sm leading-relaxed text-slate-700">
                    O cliente nao compra apenas visibilidade. Compra um pacote de operacao, governanca, resposta tecnica e narrativa executiva sustentado por dados do proprio parque monitorado.
                  </div>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                  <div className="text-lg font-semibold text-slate-900">Modulos cobertos na proposta</div>
                  <div className="mt-4 flex flex-wrap gap-2 text-sm">
                    {scenario.toolModules.slice(0, 8).map((module) => (
                      <span key={module.route} className="rounded-full border border-slate-200 bg-white px-3 py-2 text-slate-700">
                        {module.name}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white">
                  <div className="text-xs uppercase tracking-wide text-slate-400">Fechamento FPConnect</div>
                  <div className="mt-3 text-2xl font-bold">Pronto para demonstracao, proposta e follow-up</div>
                  <div className="mt-3 text-sm leading-relaxed text-slate-200">
                    Este PDF pode ser entregue apos a reuniao como material de venda, alinhamento interno ou kick-off tecnico, conforme o publico selecionado.
                  </div>
                </div>
              </div>
            </div>

            <PdfFooter page={4} scenarioLabel={`${scenario.facility} | ${audienceProfile.label}`} exportDate={exportDate} totalPages={PDF_TOTAL_PAGES} />
          </section>
        </div>
      </div>
    </div>
  );
}

export default function AgentConsolePage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-7xl mx-auto py-8 px-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm text-sm text-slate-600">
            Carregando centro de simulacao...
          </div>
        </div>
      }
    >
      <SimulationCenterContent />
    </Suspense>
  );
}
