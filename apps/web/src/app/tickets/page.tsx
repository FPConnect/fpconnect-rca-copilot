"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";
import { useNotifications } from "@/contexts/NotificationContext";
import { useState as useReactState } from "react";
import { api, Ticket as ApiTicket } from "@/services/api";

interface UITicket extends ApiTicket {
  feedback?: string;
  predictedResolution?: string;
}

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
    const [darkMode, setDarkMode] = useReactState(false);
  const { addNotification } = useNotifications();
  const [tickets, setTickets] = useState<UITicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  function suggestPriority(title: string): string {
    const t = title.toLowerCase();
    if (t.includes("offline") || t.includes("falha") || t.includes("erro")) return "critical";
    if (t.includes("slow") || t.includes("latency") || t.includes("alert")) return "high";
    if (t.includes("monitor") || t.includes("alarm")) return "medium";
    return "low";
  }

  function predictResolution(priority: string): string {
    switch (priority) {
      case "critical": return "2h";
      case "high": return "6h";
      case "medium": return "12h";
      default: return "24h";
    }
  }

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    api
      .getTickets()
      .then((data) => {
        if (!mounted) return;
        const withUi: UITicket[] = data.map((t) => ({
          ...t,
          predictedResolution: predictResolution(t.priority),
        }));
        setTickets(withUi);
      })
      .catch((err) => {
        console.error("Failed to load tickets", err);
        addNotification("error", "Erro ao carregar tickets", "Não foi possível carregar os tickets do servidor.");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const autoPriority = suggestPriority(title.trim());
    api
      .createTicket({ title: title.trim(), priority: autoPriority, description: description.trim() || undefined })
      .then((created) => {
        const newTicket: UITicket = {
          ...created,
          feedback: "",
          predictedResolution: predictResolution(created.priority),
        };
        setTickets((prev) => [newTicket, ...prev]);
        setTitle("");
        setDescription("");
        setPriority("medium");
        addNotification("success", "Ticket criado", `"${newTicket.title}" foi criado com sucesso. Prioridade sugerida: ${autoPriority}`);
      })
      .catch((err) => {
        console.error("Failed to create ticket", err);
        addNotification("error", "Erro ao criar ticket", "Não foi possível criar o ticket. Tente novamente.");
      });
  };

  const handleResolve = (id: number, feedback: string) => {
    setTickets((prev) =>
      prev.map((t) =>
        t.id === id ? { ...t, status: "resolved", feedback } : t
      )
    );
    addNotification("success", "Ticket resolvido", "Feedback registrado: " + feedback);
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

  const sortedTickets = useMemo(() => {
    return [...filtered].sort((a, b) => {
      if (a.priority === "critical" && b.priority !== "critical") return -1;
      if (b.priority === "critical" && a.priority !== "critical") return 1;
      return 0;
    });
  }, [filtered]);

  const priorityColors: Record<string, string> = {
    critical: "bg-red-100 text-red-800",
    high: "bg-orange-100 text-orange-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-green-100 text-green-800",
  };

  return (
    <div className={"max-w-4xl mx-auto " + (darkMode ? "dark bg-gray-900 text-white" : "")}>
      <div className="flex justify-end mb-2">
        <button
          onClick={() => setDarkMode((d) => !d)}
          className="px-3 py-1 rounded-lg text-xs font-medium bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700"
        >
          {darkMode ? "Modo Claro" : "Modo Escuro"}
        </button>
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Tickets</h1>

      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-6">
        <h2 className="text-sm font-semibold text-indigo-900 mb-2">
          Simulador completo do produto
        </h2>
        <p className="text-xs text-indigo-800 mb-3">
          Use o Centro de Simulacao para demonstrar backlog, causa provavel, relatorios executivos, manutencao, radar e entregas de pos-venda usando cenarios realistas do produto inteiro.
        </p>
        <div className="flex flex-wrap gap-2 items-center">
          <Link
            href="/agent?scenario=tertiary-hospital"
            className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700"
          >
            Abrir simulador central
          </Link>
          <Link
            href="/simulacoes"
            className="px-3 py-1.5 bg-white text-indigo-700 border border-indigo-200 rounded-lg text-xs font-medium hover:bg-indigo-50"
          >
            Abrir roteiro comercial
          </Link>
        </div>
      </div>

      {loading && (
        <p className="text-sm text-gray-500 mb-4">Carregando tickets...</p>
      )}

        {/* Create Form */}
        <form
          onSubmit={handleCreate}
          className="bg-white rounded-xl shadow p-6 mb-6"
        >
          <h2 className="text-lg font-semibold mb-4">Create Ticket</h2>
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Ticket title"
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                setPriority(suggestPriority(e.target.value));
              }}
              className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Descrição (opcional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="border rounded-lg px-3 py-2"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <button
              type="submit"
              className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Create
            </button>
          </div>
          {title && (
            <div className="mt-2 text-xs text-gray-500">Prioridade sugerida: <span className="font-bold">{suggestPriority(title)}</span> | Previsão de resolução: <span className="font-bold">{predictResolution(suggestPriority(title))}</span></div>
          )}
        </form>

        {/* Search & Filters */}
        <div className="flex flex-wrap gap-3 mb-4">
          <SearchBar
            placeholder="Pesquisar tickets..."
            value={search}
            onChange={setSearch}
            className="w-64"
          />
          <FilterBar
            filters={FILTERS}
            values={filters}
            onChange={(key, value) => setFilters((p) => ({ ...p, [key]: value }))}
            onClear={() => setFilters({})}
          />
        </div>

        {/* Ticket List */}
        {!loading && sortedTickets.length === 0 && (
          <p className="text-sm text-gray-500">Nenhum ticket encontrado.</p>
        )}
        {sortedTickets.map((t) => (
          <div key={t.id} className={"rounded-xl shadow p-4 mb-4 " + (darkMode ? "bg-gray-800 text-white" : "bg-white") }>
            <div className="flex justify-between items-center">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-bold text-lg">{t.title}</p>
                  {typeof t.escalation_level === "number" && t.escalation_level > 0 && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200">
                      Escalada L{t.escalation_level}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-300">
                  Prioridade:{" "}
                  <span className={"inline-flex rounded-full px-2 py-0.5 text-xs font-medium " + (priorityColors[t.priority] ?? "bg-slate-100 text-slate-800")}>
                    {t.priority}
                  </span>
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-300">Status: {t.status}</p>
                {t.description && (
                  <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">{t.description}</p>
                )}
                {t.predictedResolution && (
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">Previsão de resolução: {t.predictedResolution}</p>
                )}
                <Link
                  href={`/agent?scenario=tertiary-hospital&title=${encodeURIComponent(t.title)}&priority=${encodeURIComponent(t.priority)}&status=${encodeURIComponent(t.status)}&location=${encodeURIComponent(t.location ?? "Nao informado")}`}
                  className="mt-2 inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
                >
                  Simular este caso no centro de simulacao
                </Link>
                {t.status === "resolved" && t.feedback && (
                  <div className="mt-2 p-2 rounded bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300 text-xs">
                    <span className="font-bold">Feedback do técnico:</span> {t.feedback}
                  </div>
                )}
              </div>
              {t.status !== "resolved" && (
                <form
                  onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
                    e.preventDefault();
                    const feedback = new FormData(e.currentTarget).get("feedback");
                    if (typeof feedback !== "string") return;
                    handleResolve(t.id, feedback);
                  }}
                >
                  <input
                    name="feedback"
                    type="text"
                    placeholder="Feedback do técnico"
                    className="border rounded px-2 py-1 text-sm mr-2 dark:bg-gray-700 dark:text-white"
                    required
                  />
                  <button type="submit" className="px-3 py-1 bg-green-600 text-white rounded-lg text-xs font-medium hover:bg-green-700">Resolver</button>
                </form>
              )}
            </div>
          </div>
        ))}
    </div>
  );
}
