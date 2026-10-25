"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ScanSearch } from "lucide-react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import { useAuth } from "@/contexts/AuthContext";
import { useNotifications } from "@/contexts/NotificationContext";
import { api, Ticket } from "@/services/api";

const FILTERS = [
  {
    key: "priority",
    label: "Prioridade",
    options: [
      { label: "Crítico", value: "critical" },
      { label: "Alto", value: "high" },
      { label: "Médio", value: "medium" },
      { label: "Baixo", value: "low" },
    ],
  },
  {
    key: "status",
    label: "Status",
    options: [
      { label: "Aberto", value: "open" },
      { label: "Em Andamento", value: "in_progress" },
      { label: "Resolvido", value: "resolved" },
    ],
  },
];

export default function TicketsPage() {
  const { user } = useAuth();
  const { addNotification } = useNotifications();
  const canWrite = (user?.access_level ?? 0) >= 2;
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  const loadTickets = async () => {
    const data = await api.getTickets();
    setTickets(data);
  };

  useEffect(() => {
    loadTickets().catch(() => setTickets([]));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const newTicket = await api.createTicket({ title: title.trim(), priority });
    setTickets((prev) => [newTicket, ...prev]);
    setTitle("");
    setPriority("medium");
    addNotification("success", "Ticket criado", `"${newTicket.title}" foi criado com sucesso.`);
  };

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return tickets.filter((t) => {
      const matchSearch = !q || t.title.toLowerCase().includes(q);
      const matchPriority = !filters.priority || t.priority === filters.priority;
      const matchStatus = !filters.status || t.status === filters.status;
      return matchSearch && matchPriority && matchStatus;
    });
  }, [tickets, search, filters]);

  const priorityColors: Record<string, string> = {
    critical: "bg-red-100 text-red-800",
    high: "bg-orange-100 text-orange-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-green-100 text-green-800",
  };
  const priorityLabels: Record<string, string> = {
    critical: "Crítico",
    high: "Alto",
    medium: "Médio",
    low: "Baixo",
  };
  const statusLabels: Record<string, string> = {
    open: "Aberto",
    in_progress: "Em Andamento",
    resolved: "Resolvido",
    closed: "Fechado",
  };

  return (
    <div className="mx-auto min-w-0 max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Tickets</h1>
      {canWrite ? <form onSubmit={handleCreate} className="mb-6 rounded-lg bg-white p-4 shadow sm:p-6">
        <h2 className="text-lg font-semibold mb-4">Create Ticket</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center">
          <input type="text" placeholder="Ticket title" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full min-w-0 rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <select value={priority} onChange={(e) => setPriority(e.target.value)} className="w-full min-w-0 rounded-lg border px-3 py-2 sm:w-auto">
            <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
          </select>
          <button type="submit" className="w-full rounded-lg bg-blue-600 px-5 py-2 text-white transition hover:bg-blue-700 sm:w-auto">Create</button>
        </div>
      </form> : (
        <p role="note" className="mb-6 rounded-lg border border-cyan-200 bg-cyan-50 px-4 py-3 text-sm text-cyan-900">
          Acesso somente para consulta. Contas de usuário ou superiores podem criar e analisar tickets.
        </p>
      )}
      <div className="mb-4 flex min-w-0 flex-col gap-3 sm:flex-row sm:flex-wrap">
        <SearchBar placeholder="Pesquisar tickets..." value={search} onChange={setSearch} className="w-full sm:w-64" />
        <FilterBar filters={FILTERS} values={filters} onChange={(key, value) => setFilters((p) => ({ ...p, [key]: value }))} onClear={() => setFilters({})} />
      </div>
      {filtered.length === 0 ? <div className="bg-white rounded-xl shadow p-8 text-center text-gray-400">Nenhum ticket encontrado.</div> : (
        <div className="space-y-3">
          {filtered.map((t) => {
            const ticketId = Number(t.id);
            const canAnalyze = Number.isSafeInteger(ticketId) && ticketId > 0;
            return (
              <div key={t.id} className="flex min-w-0 flex-col gap-3 rounded-xl bg-white p-4 shadow sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0"><span className="break-words font-medium text-gray-900">{t.title}</span><span className="ml-2 text-sm text-gray-500">#{t.id}</span></div>
                <div className="flex w-full flex-wrap items-center gap-2 sm:w-auto sm:justify-end">
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${priorityColors[t.priority]}`}>{priorityLabels[t.priority] ?? t.priority}</span>
                  <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-100 text-gray-700">{statusLabels[t.status] ?? t.status}</span>
                  {canWrite && canAnalyze && (
                    <Link
                      href={{ pathname: "/analyze", query: { ticket_id: ticketId } }}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 hover:underline"
                    >
                      <ScanSearch size={14} aria-hidden="true" />
                      Analisar
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
