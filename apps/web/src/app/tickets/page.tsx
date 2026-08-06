"use client";

import { useEffect, useMemo, useState } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
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
  const { addNotification } = useNotifications();
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

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Tickets</h1>
      <form onSubmit={handleCreate} className="bg-white rounded-xl shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Create Ticket</h2>
        <div className="flex gap-3">
          <input type="text" placeholder="Ticket title" value={title} onChange={(e) => setTitle(e.target.value)} className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <select value={priority} onChange={(e) => setPriority(e.target.value)} className="border rounded-lg px-3 py-2">
            <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
          </select>
          <button type="submit" className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition">Create</button>
        </div>
      </form>
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar placeholder="Pesquisar tickets..." value={search} onChange={setSearch} className="w-64" />
        <FilterBar filters={FILTERS} values={filters} onChange={(key, value) => setFilters((p) => ({ ...p, [key]: value }))} onClear={() => setFilters({})} />
      </div>
      {filtered.length === 0 ? <div className="bg-white rounded-xl shadow p-8 text-center text-gray-400">Nenhum ticket encontrado.</div> : (
        <div className="space-y-3">
          {filtered.map((t) => (
            <div key={t.id} className="bg-white rounded-xl shadow p-4 flex items-center justify-between">
              <div><span className="font-medium text-gray-900">{t.title}</span><span className="ml-2 text-sm text-gray-500">#{t.id}</span></div>
              <div className="flex gap-2">
                <span className={`text-xs font-semibold px-2 py-1 rounded-full ${priorityColors[t.priority]}`}>{t.priority}</span>
                <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-100 text-gray-700">{t.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
