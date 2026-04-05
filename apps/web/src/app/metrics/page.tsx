"use client";

import React, { useEffect, useState } from "react";
import { Bar, Line, Pie } from "react-chartjs-2";
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import jsPDF from "jspdf";
import { useNotification } from "../../contexts/NotificationContext";
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

async function exportPDF() {
  const doc = new jsPDF();
  let currentY = await addReportBranding(doc, {
    title: "Relatório de Métricas FPConnect",
    subtitle: "Indicadores de disponibilidade, confiabilidade e incidentes por equipamento.",
    rightLabel: "Performance operacional",
    pageNumber: 1,
    totalPages: 1,
  });

  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(15, 23, 42);
  doc.text("Resumo executivo", 14, currentY);
  currentY += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(51, 65, 85);
  METRICS.forEach((m, i) => {
    doc.text(`${m.label}: ${m.value} (${m.change})`, 14, currentY + i * 7.5);
  });

  currentY += METRICS.length * 7.5 + 10;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(15, 23, 42);
  doc.text("Uptime por equipamento", 14, currentY);
  currentY += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(51, 65, 85);
  PERFORMANCE.forEach((p, i) => {
    doc.text(`${p.machine}: ${p.uptime}%`, 14, currentY + i * 7.5);
  });

  currentY += PERFORMANCE.length * 7.5 + 10;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(15, 23, 42);
  doc.text("Incidentes recentes", 14, currentY);
  currentY += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(51, 65, 85);
  PERFORMANCE.forEach((p, i) => {
    doc.text(`${p.machine}: ${p.incidents} incidente(s)`, 14, currentY + i * 7.5);
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
      positivo: metric.positive,
    })),
    ...PERFORMANCE.map((item) => ({
      secao: "equipamentos",
      equipamento: item.machine,
      uptime_pct: item.uptime,
      incidentes: item.incidents,
    })),
  ];

  downloadCsv("relatorio-metricas.csv", rows);
}

function exportPNG(chartId: string) {
  const chart = document.getElementById(chartId) as HTMLCanvasElement | null;
  if (chart) {
    const url = chart.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = url;
    a.download = `${chartId}.png`;
    a.click();
  }
}
export default function MetricsPage() {
  const [showHelp, setShowHelp] = useState(false);
  const { permission, requestPermission, scheduleAlert } =
    useNotification();

  // Exemplo: alerta inteligente se algum equipamento está abaixo de 90% uptime
  useEffect(() => {
    const lowUptime = PERFORMANCE.find((p) => p.uptime < 90);
    if (lowUptime && permission === "granted") {
      scheduleAlert(
        `Alerta: Uptime baixo em ${lowUptime.machine}`,
        { body: `O equipamento está com uptime de ${lowUptime.uptime}%` },
        2000,
      );
    }
  }, [permission, scheduleAlert]);

  const barData = {
    labels: PERFORMANCE.map((p) => p.machine),
    datasets: [
      {
        label: "Uptime (%)",
        data: PERFORMANCE.map((p) => p.uptime),
        backgroundColor: PERFORMANCE.map((p) =>
          p.uptime >= 99 ? "#22c55e" : p.uptime >= 90 ? "#eab308" : "#ef4444",
        ),
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
  return (
    <div className="max-w-5xl mx-auto" aria-label="Página de métricas" tabIndex={0}>
      <button
        onClick={() => setShowHelp((h) => !h)}
        className="fixed bottom-6 right-6 z-50 px-4 py-2 bg-indigo-600 text-white rounded-full shadow-lg hover:bg-indigo-700"
        aria-label="Ajuda"
      >
        ?
      </button>
      {showHelp && (
        <div className="fixed bottom-20 right-6 z-50 bg-white border rounded-lg shadow-lg p-4 max-w-xs text-sm">
          <h2 className="font-bold mb-2">Ajuda & Onboarding</h2>
          <ul className="list-disc ml-4 mb-2">
            <li>Explore os gráficos para visualizar o desempenho dos equipamentos.</li>
            <li>Use os botões de exportação para gerar relatórios em PDF, Excel ou PNG.</li>
            <li>Ative notificações para receber alertas inteligentes.</li>
            <li>Use o modo escuro para melhor acessibilidade.</li>
          </ul>
          <button onClick={() => setShowHelp(false)} className="mt-2 px-3 py-1 bg-gray-200 rounded hover:bg-gray-300">Fechar</button>
        </div>
      )}
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Métricas de Performance</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {METRICS.map((m) => (
          <div key={m.label} className="bg-white rounded-xl shadow p-5">
            <p className="text-sm text-gray-500">{m.label}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{m.value}</p>
            <p className={`text-sm font-medium mt-1 ${m.positive ? "text-green-600" : "text-red-600"}`}>
              {m.change} vs semana anterior
            </p>
          </div>
        ))}
      </div>
      <div className="flex gap-4 mb-6">
        <button onClick={exportPDF} className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">Exportar PDF</button>
        <button onClick={exportExcel} className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700">Exportar Excel</button>
        <button
          onClick={() => exportPNG("barChart")}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700"
        >
          Exportar PNG Gráfico
        </button>
        {permission !== "granted" && (
          <button onClick={requestPermission} className="px-4 py-2 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700">Ativar Notificações</button>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Uptime por Equipamento</h2>
          <div id="barChart">
            <Bar
              data={barData}
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false },
                  title: { display: true, text: "Uptime (%) por Equipamento" },
                },
              }}
            />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Incidentes por Equipamento</h2>
          <Line
            data={lineData}
            options={{
              responsive: true,
              plugins: {
                legend: { display: false },
                title: { display: true, text: "Incidentes por Equipamento" },
              },
            }}
          />
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Distribuição de Incidentes</h2>
          <Pie
            data={pieData}
            options={{
              responsive: true,
              plugins: {
                legend: { position: "bottom" },
                title: { display: true, text: "Distribuição de Incidentes" },
              },
            }}
          />
        </div>
      </div>
      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Incidentes Recentes</h2>
        <ul className="divide-y divide-gray-100">
          {PERFORMANCE.map((p) => (
            <li key={p.machine} className="py-2 flex justify-between text-sm">
              <span className="font-medium text-gray-700">{p.machine}</span>
              <span className="text-gray-500">{p.incidents} incidente(s)</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
