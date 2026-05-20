"use client";

import { useMemo, useState } from "react";
import Pagination from "@/components/Pagination";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";

const EVENTS = [
  { id: 1, action: "Chamado criado", user: "João Silva", resource: "Ressonância Magnética offline", time: "2026-02-26 14:32", type: "ticket" },
  { id: 2, action: "Alerta reconhecido", user: "Maria Santos", resource: "Monitor ECG com alta latência", time: "2026-02-26 13:10", type: "alert" },
  { id: 3, action: "Manutenção agendada", user: "Carlos Rocha", resource: "Desfibrilador", time: "2026-02-26 11:45", type: "maintenance" },
  { id: 4, action: "Usuário criado", user: "Admin", resource: "Ana Lima", time: "2026-02-26 10:00", type: "user" },
  { id: 5, action: "Health check falhou", user: "Sistema", resource: "Autoteste do desfibrilador", time: "2026-02-26 09:15", type: "health" },
  { id: 6, action: "Chamado resolvido", user: "Maria Santos", resource: "Alarme do ventilador", time: "2026-02-25 17:22", type: "ticket" },
];

const FILTERS = [
  {
    key: "type",
    label: "Tipo",
    options: [
      { label: "Chamado", value: "ticket" },
      { label: "Alerta", value: "alert" },
      { label: "Manutenção", value: "maintenance" },
      { label: "Usuário", value: "user" },
      { label: "Verificação técnica", value: "health" },
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

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Eventos de Auditoria</h1>
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar
          placeholder="Pesquisar eventos..."
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
        <table className="w-full text-sm min-w-[600px]">
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
