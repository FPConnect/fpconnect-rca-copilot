"use client";

const RELATORIO_ROI = {
  economiaTotal: "R$ 142.300,00",
  downtimeEvitado: "48 horas",
  alertasCriticos: 12,
  contratoAnual: "R$ 60.000,00",
  roi: "137%",
};

const DESASTRES_EVITADOS = [
  {
    equipamento: "MRI Scanner - Tomógrafo A",
    alerta: "Anomalia detectada no tubo de resfriamento",
    acao: "Reparo agendado antes da falha total (Tempo: 2h)",
    economia: "R$ 85.000,00 (Evitou queima de peça + frete + 3 dias parado)",
  },
  {
    equipamento: "Geladeira UTI Neonatal",
    alerta: "Vibração anômala no compressor detectada",
    acao: "Ordem de serviço automática e componente trocado sem queda de temperatura",
    economia: "R$ 35.000,00 (Estoque salvo) | Risco zero ao paciente",
  },
  {
    equipamento: "Central de Gases Especiais",
    alerta: "Desgaste acelerado na válvula de pressão",
    acao: "Troca preventiva realizada fora de horário de pico",
    economia: "R$ 22.300,00 (Evitou cirurgias canceladas e compra de cilindros avulsos)",
  },
];

import React, { useState, useEffect } from "react";
import { Bar, Line, Pie } from "react-chartjs-2";
import { Chart, CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend } from "chart.js";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { addReportBranding } from "@/lib/report-branding";
import { downloadCsv, type CsvRow } from "@/utils/downloadCsv";
Chart.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend);

const METRICS = [
  { label: "Uptime Médio", value: "99.2%", change: "+0.1%", positive: true },
  { label: "MTBF (horas)", value: "1,240", change: "+5%", positive: true },
  { label: "MTTR (minutos)", value: "18", change: "-12%", positive: true },
  { label: "Alertas (7d)", value: "34", change: "+8%", positive: false },
];

const PERFORMANCE = [
  { machine: "MRI Scanner", uptime: 99.8, incidents: 0 },
  { machine: "ECG Monitor", uptime: 94.5, incidents: 3 },
  { machine: "Ventilator", uptime: 99.9, incidents: 0 },
  { machine: "Defibrillator", uptime: 78.2, incidents: 5 },
  { machine: "Patient Monitor", uptime: 98.7, incidents: 1 },
];

const EVENTS = [
  { id: 1, action: "Ticket criado", user: "João Silva", resource: "MRI Scanner offline", time: "2026-02-26 14:32", type: "ticket" },
  { id: 2, action: "Alerta reconhecido", user: "Maria Santos", resource: "ECG Monitor high latency", time: "2026-02-26 13:10", type: "alert" },
  { id: 3, action: "Manutenção agendada", user: "Carlos Rocha", resource: "Defibrillator", time: "2026-02-26 11:45", type: "maintenance" },
  { id: 4, action: "Usuário criado", user: "Admin", resource: "Ana Lima", time: "2026-02-26 10:00", type: "user" },
  { id: 5, action: "Health check falhou", user: "Sistema", resource: "Defibrillator self-test", time: "2026-02-26 09:15", type: "health" },
  { id: 6, action: "Ticket resolvido", user: "Maria Santos", resource: "Ventilator alarm", time: "2026-02-25 17:22", type: "ticket" },
];

const INITIAL_MACHINES = [
  { id: "M001", name: "MRI Scanner", location: "Ward A", status: "online", lastCheck: "2 min ago", type: "imaging" },
  { id: "M002", name: "ECG Monitor", location: "ICU", status: "warning", lastCheck: "5 min ago", type: "monitoring" },
  { id: "M003", name: "Ventilator", location: "Ward B", status: "online", lastCheck: "1 min ago", type: "life-support" },
  { id: "M004", name: "Defibrillator", location: "Emergency", status: "offline", lastCheck: "1 hour ago", type: "life-support" },
];

export default function DemoRecursosPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [machines, setMachines] = useState(INITIAL_MACHINES);
  const [notification, setNotification] = useState("");

  // IoT Simulação
  useEffect(() => {
    const interval = setInterval(() => {
      setMachines((prev) =>
        prev.map((m) => {
          const statuses = ["online", "warning", "offline"];
          const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
          const minutes = Math.floor(Math.random() * 60);
          return { ...m, status: newStatus, lastCheck: `${minutes} min ago` };
        })
      );
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Notificação inteligente
  useEffect(() => {
    const lowUptime = PERFORMANCE.find((p) => p.uptime < 90);
    if (lowUptime && notification === "") {
      setTimeout(() => {
        setNotification(`Alerta: Uptime baixo em ${lowUptime.machine}`);
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification(`Alerta: Uptime baixo em ${lowUptime.machine}`, { body: `O equipamento está com uptime de ${lowUptime.uptime}%` });
        }
      }, 2000);
    }
  }, [notification]);

  // Gráficos
  const barData = {
    labels: PERFORMANCE.map((p) => p.machine),
    datasets: [
      {
        label: "Uptime (%)",
        data: PERFORMANCE.map((p) => p.uptime),
        backgroundColor: PERFORMANCE.map((p) => p.uptime >= 99 ? "#22c55e" : p.uptime >= 90 ? "#eab308" : "#ef4444"),
      },
    ],
  };
  const lineData = {
    labels: PERFORMANCE.map((p) => p.machine),
    datasets: [
      {
        label: "Incidentes",
        data: PERFORMANCE.map((p) => p.incidents),
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,0.2)",
        fill: true,
      },
    ],
  };
  const pieData = {
    labels: ["Sem Incidente", "Com Incidente"],
    datasets: [
      {
        label: "Distribuição",
        data: [PERFORMANCE.filter((p) => p.incidents === 0).length, PERFORMANCE.filter((p) => p.incidents > 0).length],
        backgroundColor: ["#22c55e", "#ef4444"],
      },
    ],
  };

  async function exportPDF() {
    const doc = new jsPDF();
    let currentY = await addReportBranding(doc, {
      title: "Relatório Executivo FPConnect",
      subtitle: "Economia gerada, ROI e riscos operacionais mitigados no período analisado.",
      rightLabel: "Pacote de pós-venda",
      pageNumber: 1,
      totalPages: 1,
    });

    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(15, 23, 42);
    doc.text("Indicadores centrais", 14, currentY);
    currentY += 8;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(51, 65, 85);
    doc.text(`Economia total: ${RELATORIO_ROI.economiaTotal}`, 14, currentY);
    currentY += 7;
    doc.text(`Downtime evitado: ${RELATORIO_ROI.downtimeEvitado}`, 14, currentY);
    currentY += 7;
    doc.text(`ROI estimado: ${RELATORIO_ROI.roi}`, 14, currentY);
    currentY += 7;
    doc.text(`Alertas críticos resguardados: ${RELATORIO_ROI.alertasCriticos}`, 14, currentY);
    currentY += 11;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(15, 23, 42);
    doc.text("Desastres operacionais evitados", 14, currentY);
    currentY += 8;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9.5);
    doc.setTextColor(51, 65, 85);
    DESASTRES_EVITADOS.forEach((item, index) => {
      doc.text(`${index + 1}. ${item.equipamento}`, 14, currentY);
      currentY += 6;
      doc.text(`Alerta: ${item.alerta}`.slice(0, 110), 18, currentY);
      currentY += 6;
      doc.text(`Ação: ${item.acao}`.slice(0, 110), 18, currentY);
      currentY += 6;
      doc.text(`Economia: ${item.economia}`.slice(0, 110), 18, currentY);
      currentY += 8;
    });

    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(15, 23, 42);
    doc.text("Métricas operacionais", 14, currentY);
    currentY += 8;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(51, 65, 85);
    METRICS.forEach((m, i) => {
      doc.text(`${m.label}: ${m.value} (${m.change})`, 14, currentY + i * 7.5);
    });
    doc.save("relatorio-metricas.pdf");
  }
  function exportExcel() {
    const rows: CsvRow[] = [
      ...METRICS.map((metric) => ({
        secao: "metricas",
        indicador: metric.label,
        valor: metric.value,
        variacao: metric.change,
      })),
      ...EVENTS.map((event) => ({
        secao: "historico",
        acao: event.action,
        usuario: event.user,
        recurso: event.resource,
        horario: event.time,
      })),
      ...machines.map((machine) => ({
        secao: "maquinas",
        id: machine.id,
        nome: machine.name,
        localizacao: machine.location,
        status: machine.status,
        ultimo_check: machine.lastCheck,
      })),
    ];

    downloadCsv("relatorio-metricas.csv", rows);
  }
  async function exportPNG() {
    const chart = document.getElementById("barChart");
    if (chart) {
      const canvas = await html2canvas(chart);
      const url = canvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.href = url;
      a.download = "grafico-metricas.png";
      a.click();
    }
  }

  return (
    <div className={"max-w-5xl mx-auto " + (darkMode ? "dark bg-gray-900 text-white" : "")} aria-label="Página de demonstração de recursos" tabIndex={0}>
      <div className="flex justify-end mb-2">
        <button onClick={() => setDarkMode((d) => !d)} className="px-3 py-1 rounded-lg text-xs font-medium bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700">{darkMode ? "Modo Claro" : "Modo Escuro"}</button>
        <button onClick={() => setShowHelp((h) => !h)} className="ml-2 px-3 py-1 rounded-lg text-xs font-medium bg-indigo-600 text-white hover:bg-indigo-700">Ajuda</button>
      </div>
      {showHelp && (
        <div className="fixed bottom-20 right-6 z-50 bg-white border rounded-lg shadow-lg p-4 max-w-xs text-sm">
          <h2 className="font-bold mb-2">Ajuda & Onboarding</h2>
          <ul className="list-disc ml-4 mb-2">
            <li>Gráficos interativos e exportação (PDF, Excel, PNG)</li>
            <li>Notificações push e alertas inteligentes</li>
            <li>Histórico detalhado e relatórios exportáveis</li>
            <li>Automação de priorização e análise preditiva</li>
            <li>Integração IoT simulada</li>
            <li>Feedback dos técnicos e UX aprimorado</li>
            <li>Modo escuro e acessibilidade</li>
          </ul>
          <button onClick={() => setShowHelp(false)} className="mt-2 px-3 py-1 bg-gray-200 rounded hover:bg-gray-300">Fechar</button>
        </div>
      )}
      <h1 className="text-3xl font-bold mb-6">Demonstração de Todos os Recursos</h1>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-8 border-l-4 border-green-500">
        <h2 className="text-2xl font-bold mb-2 text-green-700 dark:text-green-400">Extrato de Economia Gerada (Mês Atual)</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-6">Seu contrato atual salvou <strong className="text-xl text-green-600">{RELATORIO_ROI.economiaTotal}</strong> e <strong>{RELATORIO_ROI.downtimeEvitado}</strong> de operação hospitalar mitigando riscos críticos.</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-green-50 dark:bg-green-900 rounded p-4 text-center">
            <span className="block text-sm text-green-700 dark:text-green-300">Economia Estimada (YTD)</span>
            <span className="block text-2xl font-bold text-green-800 dark:text-green-100">{RELATORIO_ROI.economiaTotal}</span>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900 rounded p-4 text-center">
            <span className="block text-sm text-blue-700 dark:text-blue-300">Retorno sobre Investimento (ROI)</span>
            <span className="block text-2xl font-bold text-blue-800 dark:text-blue-100">{RELATORIO_ROI.roi}</span>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900 rounded p-4 text-center">
            <span className="block text-sm text-yellow-700 dark:text-yellow-300">Alertas Críticos Resguardados</span>
            <span className="block text-2xl font-bold text-yellow-800 dark:text-yellow-100">{RELATORIO_ROI.alertasCriticos}</span>
          </div>
        </div>

        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">Desastres Operacionais Evitados:</h3>
        <div className="space-y-4">
          {DESASTRES_EVITADOS.map((d, i) => (
            <div key={i} className="flex flex-col md:flex-row bg-gray-50 dark:bg-gray-700 rounded-lg p-4 gap-4 border-l-2 border-indigo-500">
              <div className="flex-1">
                <span className="font-bold text-indigo-700 dark:text-indigo-300">{d.equipamento}</span>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1"><strong>Alerta Preditivo:</strong> {d.alerta}</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1"><strong>Ação do Sistema:</strong> {d.acao}</p>
              </div>
              <div className="flex items-center justify-start md:justify-end">
                <span className="bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100 text-sm font-semibold px-3 py-1 rounded-full">
                  Economia: {d.economia}
                </span>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-8 bg-indigo-50 dark:bg-indigo-900 p-6 rounded-lg text-center border border-indigo-200 dark:border-indigo-700">
          <h3 className="text-lg font-bold text-indigo-800 dark:text-indigo-200 mb-2">Maximize sua Proteção e Economia</h3>
          <p className="text-sm text-indigo-700 dark:text-indigo-300 mb-4">
            Atualmente seu plano cobre preditiva para 25 equipamentos críticos. Expandir o Contrato Preditivo para a <strong>Sala Cirúrgica e UTI</strong> tem uma economia extra projetada de <strong>R$ 200.000,00/ano</strong>.
          </p>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition-colors">
            Simular Novo Contrato Preditivo
          </button>
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {METRICS.map((m) => (
          <div key={m.label} className="bg-white dark:bg-gray-800 rounded-xl shadow p-5">
            <p className="text-sm text-gray-500 dark:text-gray-300">{m.label}</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{m.value}</p>
            <p className={`text-sm font-medium mt-1 ${m.positive ? "text-green-600" : "text-red-600"}`}>{m.change} vs semana anterior</p>
          </div>
        ))}
      </div>
      <div className="flex gap-4 mb-6">
        <button onClick={exportPDF} className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">Exportar PDF</button>
        <button onClick={exportExcel} className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700">Exportar Excel</button>
        <button onClick={exportPNG} className="px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700">Exportar PNG</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Uptime por Equipamento</h2>
          <div id="barChart">
            <Bar data={barData} options={{ responsive: true, plugins: { legend: { display: false }, title: { display: true, text: "Uptime (%) por Equipamento" } } }} />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Incidentes por Equipamento</h2>
          <Line data={lineData} options={{ responsive: true, plugins: { legend: { display: false }, title: { display: true, text: "Incidentes por Equipamento" } } }} />
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Distribuição de Incidentes</h2>
          <Pie data={pieData} options={{ responsive: true, plugins: { legend: { position: "bottom" }, title: { display: true, text: "Distribuição de Incidentes" } } }} />
        </div>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Histórico de Incidentes</h2>
        <table className="w-full text-sm min-w-[600px]">
          <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200">
            <tr>
              {["Ação", "Usuário", "Recurso", "Data/Hora"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {EVENTS.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="px-4 py-3 font-medium">{e.action}</td>
                <td className="px-4 py-3">{e.user}</td>
                <td className="px-4 py-3">{e.resource}</td>
                <td className="px-4 py-3 text-xs">{e.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Máquinas (IoT Simulado)</h2>
        <table className="w-full text-sm min-w-[600px]">
          <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200">
            <tr>
              {["ID", "Nome", "Localização", "Status", "Último Check"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600 dark:text-gray-300">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
            {machines.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="px-4 py-3 font-mono">{m.id}</td>
                <td className="px-4 py-3 font-medium">{m.name}</td>
                <td className="px-4 py-3">{m.location}</td>
                <td className="px-4 py-3">{m.status}</td>
                <td className="px-4 py-3">{m.lastCheck}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {notification && (
        <div className="fixed top-6 right-6 z-50 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 rounded shadow-lg">
          {notification}
        </div>
      )}
    </div>
  );
}
