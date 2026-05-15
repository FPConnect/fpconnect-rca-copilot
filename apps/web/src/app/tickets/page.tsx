"use client";

import { useEffect, useMemo, useState } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import SeverityBadge from "@/components/SeverityBadge";
import { useNotifications } from "@/contexts/NotificationContext";
import { api, Ticket } from "@/services/api";

const FILTERS = [
  {
    key: "priority",
    label: "Severidade",
    options: [
      { label: "Crítica", value: "critical" },
      { label: "Alta", value: "high" },
      { label: "Média", value: "medium" },
      { label: "Baixa", value: "low" },
    ],
  },
  {
    key: "status",
    label: "Status",
    options: [
      { label: "Aberto", value: "open" },
      { label: "Em atendimento", value: "in_progress" },
      { label: "Resolvido", value: "resolved" },
    ],
  },
];

const statusLabels: Record<string, string> = {
  open: "Aberto",
  in_progress: "Em atendimento",
  resolved: "Resolvido",
  closed: "Fechado",
};

export default function IncidentsPage() {
  const { addNotification } = useNotifications();
  const [incidents, setIncidents] = useState<Ticket[]>([]);
  const [selected, setSelected] = useState<Ticket | null>(null);
  const [title, setTitle] = useState("");
  const [equipment, setEquipment] = useState("");
  const [unit, setUnit] = useState("");
  const [priority, setPriority] = useState("medium");
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  const loadIncidents = async () => {
    const data = await api.getTickets();
    setIncidents(data);
    setSelected((current) => current ?? data[0] ?? null);
  };

  useEffect(() => {
    loadIncidents().catch(() => setIncidents([]));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const newIncident = await api.createTicket({
      title: title.trim(),
      priority,
      device_id: equipment,
      location: unit,
      description: `Ocorrência reportada em ${unit || "unidade não informada"}.`,
    });
    setIncidents((prev) => [newIncident, ...prev]);
    setSelected(newIncident);
    setTitle("");
    setEquipment("");
    setUnit("");
    setPriority("medium");
    addNotification("success", "Chamado criado", `Incidente "${newIncident.title}" registrado.`);
  };

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return incidents.filter((incident) => {
      const matchSearch =
        !q ||
        incident.title.toLowerCase().includes(q) ||
        (incident.device_id ?? "").toLowerCase().includes(q) ||
        (incident.location ?? "").toLowerCase().includes(q);
      const matchPriority = !filters.priority || incident.priority === filters.priority;
      const matchStatus = !filters.status || incident.status === filters.status;
      return matchSearch && matchPriority && matchStatus;
    });
  }, [incidents, search, filters]);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Engenharia Clínica</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Incidentes e Chamados</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600">
          Registre ocorrências assistenciais, acompanhe severidade e acesse rapidamente causa raiz sugerida e ação recomendada.
        </p>
      </section>

      <form onSubmit={handleCreate} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Novo chamado de equipamento</h2>
        <div className="grid gap-3 md:grid-cols-[1fr_160px_180px_150px_auto]">
          <input aria-label="Descrição do chamado" type="text" placeholder="Descrição da ocorrência" value={title} onChange={(e) => setTitle(e.target.value)} className="rounded-lg border border-slate-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <input aria-label="Equipamento" type="text" placeholder="Equipamento" value={equipment} onChange={(e) => setEquipment(e.target.value)} className="rounded-lg border border-slate-300 px-4 py-2" />
          <input aria-label="Unidade clínica" type="text" placeholder="Unidade clínica" value={unit} onChange={(e) => setUnit(e.target.value)} className="rounded-lg border border-slate-300 px-4 py-2" />
          <select aria-label="Severidade" value={priority} onChange={(e) => setPriority(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2">
            <option value="low">Baixa</option><option value="medium">Média</option><option value="high">Alta</option><option value="critical">Crítica</option>
          </select>
          <button type="submit" className="rounded-lg bg-slate-900 px-5 py-2 font-semibold text-white transition hover:bg-slate-700">Criar chamado</button>
        </div>
      </form>

      <div className="flex flex-wrap gap-3">
        <SearchBar placeholder="Pesquisar por equipamento, unidade ou ocorrência..." value={search} onChange={setSearch} className="w-80" />
        <FilterBar filters={FILTERS} values={filters} onChange={(key, value) => setFilters((p) => ({ ...p, [key]: value }))} onClear={() => setFilters({})} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-[860px] w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-left text-slate-600">
              <tr>{["Equipamento", "Unidade", "Severidade", "Status", "Data", "Causa provável"].map((h) => <th key={h} className="px-4 py-3 font-semibold">{h}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((incident) => (
                <tr key={incident.id} onClick={() => setSelected(incident)} className="cursor-pointer hover:bg-blue-50/50">
                  <td className="px-4 py-3 font-semibold text-slate-900">{incident.device_id ?? incident.title}</td>
                  <td className="px-4 py-3 text-slate-600">{incident.location ?? "Não informada"}</td>
                  <td className="px-4 py-3"><SeverityBadge value={incident.priority} /></td>
                  <td className="px-4 py-3 text-slate-700">{statusLabels[incident.status] ?? incident.status}</td>
                  <td className="px-4 py-3 text-slate-500">Hoje</td>
                  <td className="px-4 py-3 text-slate-700">{incident.root_cause ?? "Aguardando diagnóstico"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <aside className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-slate-950">Detalhe do incidente</h2>
          {selected ? (
            <div className="mt-4 space-y-5">
              <div>
                <p className="text-sm text-slate-500">#{selected.id}</p>
                <h3 className="font-semibold text-slate-900">{selected.title}</h3>
              </div>
              <div className="space-y-3 border-l-2 border-blue-200 pl-4">
                <p className="text-sm text-slate-600"><strong>Evento recebido:</strong> chamado registrado pela unidade.</p>
                <p className="text-sm text-slate-600"><strong>Triagem:</strong> severidade {selected.priority} validada.</p>
                <p className="text-sm text-slate-600"><strong>Diagnóstico:</strong> {selected.analysis_completed ? "Causa raiz calculada" : "pendente"}.</p>
              </div>
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase text-slate-500">Causa raiz sugerida</p>
                <p className="mt-1 text-sm text-slate-900">{selected.root_cause ?? "Clique em Diagnóstico de Falha para analisar este chamado."}</p>
              </div>
              <div className="rounded-xl bg-blue-50 p-4">
                <p className="text-xs font-semibold uppercase text-blue-700">Ação recomendada</p>
                <p className="mt-1 text-sm text-blue-950">{selected.recommendation ?? "Aplicar playbook do equipamento e registrar evidências."}</p>
              </div>
              <a href={`/analyze?ticket_id=${selected.id}`} className="block rounded-lg bg-blue-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-blue-700">Analisar falha</a>
            </div>
          ) : <p className="mt-4 text-sm text-slate-500">Selecione um incidente para ver timeline, causa raiz e ação recomendada.</p>}
        </aside>
      </div>
    </div>
  );
}
