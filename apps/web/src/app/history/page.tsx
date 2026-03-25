"use client";

import { useMemo, useState } from "react";
import Pagination from "@/components/Pagination";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import jsPDF from "jspdf";
import * as XLSX from "xlsx";
import html2canvas from "html2canvas";
import { addReportBranding } from "@/lib/report-branding";

const EVENTS = [
  { id: 1, action: "Ticket criado", user: "João Silva", resource: "MRI Scanner offline", time: "2026-02-26 14:32", type: "ticket" },
  { id: 2, action: "Alerta reconhecido", user: "Maria Santos", resource: "ECG Monitor high latency", time: "2026-02-26 13:10", type: "alert" },
  { id: 3, action: "Manutenção agendada", user: "Carlos Rocha", resource: "Defibrillator", time: "2026-02-26 11:45", type: "maintenance" },
  { id: 4, action: "Usuário criado", user: "Admin", resource: "Ana Lima", time: "2026-02-26 10:00", type: "user" },
  { id: 5, action: "Health check falhou", user: "Sistema", resource: "Defibrillator self-test", time: "2026-02-26 09:15", type: "health" },
  { id: 6, action: "Ticket resolvido", user: "Maria Santos", resource: "Ventilator alarm", time: "2026-02-25 17:22", type: "ticket" },
];

const FILTERS = [
  {
    key: "type",
    label: "Tipo",
    options: [
      { label: "Ticket", value: "ticket" },
      { label: "Alerta", value: "alert" },
      { label: "Manutenção", value: "maintenance" },
      { label: "Usuário", value: "user" },
      { label: "Health Check", value: "health" },
    ],
  },
];

const PAGE_SIZE = 4;

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return EVENTS.filter((e) => {
      const matchSearch =
        !q ||
        e.action.toLowerCase().includes(q) ||
        e.user.toLowerCase().includes(q) ||
        e.resource.toLowerCase().includes(q);
      const matchType = !filters.type || e.type === filters.type;
      return matchSearch && matchType;
    });
  }, [search, filters]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  const handleSearch = (value: string) => {
    setSearch(value);
    setPage(1);
  };

  async function exportPDF() {
    const doc = new jsPDF();
    let currentY = await addReportBranding(doc, {
      title: "Histórico de Incidentes FPConnect",
      subtitle: "Linha do tempo operacional com eventos, usuários envolvidos e recursos afetados.",
      rightLabel: "Trilha auditável",
      pageNumber: 1,
      totalPages: 1,
    });

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(51, 65, 85);
    filtered.forEach((e, i) => {
      doc.text(
        `${e.time} - ${e.action} (${e.user}) - ${e.resource}`.slice(0, 92),
        14,
        currentY + i * 7.5,
      );
    });
    doc.save("historico-incidentes.pdf");
  }

  function exportExcel() {
    const ws = XLSX.utils.json_to_sheet(filtered);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Histórico");
    XLSX.writeFile(wb, "historico-incidentes.xlsx");
  }

  async function exportPNG() {
    const table = document.getElementById("history-table");
    if (table) {
      const canvas = await html2canvas(table);
      const url = canvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.href = url;
      a.download = "historico-incidentes.png";
      a.click();
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Histórico de Incidentes</h1>
      <div className="flex gap-4 mb-6">
        <button onClick={exportPDF} className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">Exportar PDF</button>
        <button onClick={exportExcel} className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700">Exportar Excel</button>
        <button onClick={exportPNG} className="px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700">Exportar PNG</button>
      </div>
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar
          placeholder="Pesquisar histórico..."
          value={search}
          onChange={handleSearch}
          className="w-64"
        />
        <FilterBar
          filters={FILTERS}
          values={filters}
          onChange={(key, value) => { setFilters((p) => ({ ...p, [key]: value })); setPage(1); }}
          onClear={() => { setFilters({}); setPage(1); }}
        />
      </div>
      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <table id="history-table" className="w-full text-sm min-w-[600px]">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["Ação", "Usuário", "Recurso", "Data/Hora"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {paginated.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-gray-400">
                  Nenhum evento encontrado.
                </td>
              </tr>
            ) : (
              paginated.map((e) => (
                <tr key={e.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{e.action}</td>
                  <td className="px-4 py-3 text-gray-600">{e.user}</td>
                  <td className="px-4 py-3 text-gray-500">{e.resource}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{e.time}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <Pagination
        page={safePage}
        totalPages={totalPages}
        onPrev={() => setPage((p) => Math.max(1, p - 1))}
        onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
      />
    </div>
  );
}
