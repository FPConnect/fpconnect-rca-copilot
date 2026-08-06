"use client";

import { useEffect, useMemo, useState } from "react";
import Pagination from "@/components/Pagination";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import { api, Machine } from "@/services/api";

const STATUS_COLORS: Record<string, string> = {
  online: "bg-green-100 text-green-700",
  warning: "bg-yellow-100 text-yellow-700",
  offline: "bg-red-100 text-red-700",
};

const STATUS_LABELS: Record<string, string> = {
  online: "Online",
  warning: "Atenção",
  offline: "Offline",
};

const FILTERS = [
  {
    key: "status",
    label: "Status",
    options: [
      { label: "Online", value: "online" },
      { label: "Offline", value: "offline" },
      { label: "Atenção", value: "warning" },
    ],
  },
  {
    key: "type",
    label: "Tipo",
    options: [
      { label: "Imagem", value: "imaging" },
      { label: "Monitoramento", value: "monitoring" },
      { label: "Suporte de Vida", value: "life-support" },
      { label: "Infusão", value: "infusion" },
    ],
  },
];

const PAGE_SIZE = 4;

export default function MachinesPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  useEffect(() => {
    api.getMachines().then(setMachines).catch(() => setMachines([]));
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return machines.filter((m) => {
      const matchSearch = !q || m.name.toLowerCase().includes(q) || m.code.toLowerCase().includes(q) || m.location.toLowerCase().includes(q);
      const matchStatus = !filters.status || m.status === filters.status;
      const matchType = !filters.type || m.type === filters.type;
      return matchSearch && matchStatus && matchType;
    });
  }, [machines, search, filters]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Máquinas</h1>
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar placeholder="Pesquisar máquinas..." value={search} onChange={(v) => { setSearch(v); setPage(1); }} className="w-64" />
        <FilterBar filters={FILTERS} values={filters} onChange={(key, value) => { setFilters((prev) => ({ ...prev, [key]: value })); setPage(1); }} onClear={() => { setFilters({}); setPage(1); }} />
      </div>
      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm min-w-[600px]"><thead className="bg-gray-50 border-b border-gray-200"><tr>{["ID", "Nome", "Localização", "Status", "Último Check"].map((h) => <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-gray-100">
            {paginated.length === 0 ? <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Nenhuma máquina encontrada.</td></tr> : paginated.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-gray-500">{m.code}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{m.name}</td>
                <td className="px-4 py-3 text-gray-600">{m.location}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs font-semibold ${STATUS_COLORS[m.status]}`}>{STATUS_LABELS[m.status] ?? m.status}</span></td>
                <td className="px-4 py-3 text-gray-500">{new Date(m.last_check).toLocaleString("pt-BR")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={safePage} totalPages={totalPages} onPrev={() => setPage((p) => Math.max(1, p - 1))} onNext={() => setPage((p) => Math.min(totalPages, p + 1))} />
    </div>
  );
}
