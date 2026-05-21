"use client";

import { useEffect, useMemo, useState } from "react";
import Pagination from "@/components/Pagination";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import { api, Machine } from "@/services/api";

const STATUS_COLORS: Record<string, string> = {
  online: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
  offline: "bg-red-100 text-red-700",
};

const CRITICALITY_COLORS: Record<string, string> = {
  Alta: "border-red-200 bg-red-50 text-red-800",
  Média: "border-amber-200 bg-amber-50 text-amber-800",
  Baixa: "border-emerald-200 bg-emerald-50 text-emerald-800",
};

const FILTERS = [
  {
    key: "status",
    label: "Status operacional",
    options: [
      { label: "Online", value: "online" },
      { label: "Offline", value: "offline" },
      { label: "Atenção", value: "warning" },
    ],
  },
  {
    key: "criticality",
    label: "Criticidade",
    options: [
      { label: "Alta", value: "Alta" },
      { label: "Média", value: "Média" },
      { label: "Baixa", value: "Baixa" },
    ],
  },
];

const PAGE_SIZE = 6;

export default function EquipmentPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  useEffect(() => {
    api.getMachines().then(setMachines).catch(() => setMachines([]));
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return machines.filter((equipment) => {
      const matchSearch =
        !q ||
        equipment.name.toLowerCase().includes(q) ||
        equipment.code.toLowerCase().includes(q) ||
        equipment.location.toLowerCase().includes(q) ||
        (equipment.model ?? "").toLowerCase().includes(q);
      const matchStatus = !filters.status || equipment.status === filters.status;
      const matchCriticality = !filters.criticality || equipment.criticality === filters.criticality;
      return matchSearch && matchStatus && matchCriticality;
    });
  }, [machines, search, filters]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Parque instalado</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Equipamentos</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600">
          Visão clínica do parque instalado com modelo, unidade, criticidade, status e falhas recorrentes para priorização de atendimento.
        </p>
      </section>

      <div className="flex flex-wrap gap-3">
        <SearchBar placeholder="Pesquisar equipamentos, modelos ou unidades..." value={search} onChange={(v) => { setSearch(v); setPage(1); }} className="w-80" />
        <FilterBar filters={FILTERS} values={filters} onChange={(key, value) => { setFilters((prev) => ({ ...prev, [key]: value })); setPage(1); }} onClear={() => { setFilters({}); setPage(1); }} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {paginated.map((equipment) => (
          <article key={equipment.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-xs text-slate-500">{equipment.code}</p>
                <h2 className="mt-1 text-lg font-bold text-slate-950">{equipment.name}</h2>
                <p className="text-sm text-slate-500">{equipment.model ?? "Modelo não informado"}</p>
              </div>
              <span className={`rounded-full px-2 py-1 text-xs font-semibold ${STATUS_COLORS[equipment.status]}`}>{equipment.status}</span>
            </div>
            <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div><dt className="text-slate-500">Unidade</dt><dd className="font-semibold text-slate-900">{equipment.location}</dd></div>
              <div><dt className="text-slate-500">Criticidade</dt><dd><span className={`rounded-full border px-2 py-1 text-xs font-semibold ${CRITICALITY_COLORS[equipment.criticality] ?? CRITICALITY_COLORS.Média}`}>{equipment.criticality}</span></dd></div>
              <div className="col-span-2"><dt className="text-slate-500">Última falha</dt><dd className="font-medium text-slate-800">{equipment.last_failure ?? "Sem falha registrada"}</dd></div>
            </dl>
            {equipment.recurrent_failures > 1 && (
              <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-900">
                Indicador de falhas recorrentes: {equipment.recurrent_failures} ocorrências recentes
              </div>
            )}
          </article>
        ))}
      </div>
      {paginated.length === 0 && <div className="rounded-xl bg-white p-8 text-center text-slate-400 shadow">Nenhum equipamento encontrado.</div>}
      <Pagination page={safePage} totalPages={totalPages} onPrev={() => setPage((p) => Math.max(1, p - 1))} onNext={() => setPage((p) => Math.min(totalPages, p + 1))} />
    </div>
  );
}
