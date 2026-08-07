"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, Info, AlertOctagon } from "lucide-react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";

const ALERTS = [
  { id: 1, severity: "critical", message: "Defibrillator self-test failed", machine: "M004", time: "1 hour ago", acknowledged: false },
  { id: 2, severity: "high", message: "ECG Monitor high latency (250ms)", machine: "M002", time: "5 min ago", acknowledged: false },
  { id: 3, severity: "medium", message: "MRI Scanner scheduled maintenance due", machine: "M001", time: "2 hours ago", acknowledged: true },
  { id: 4, severity: "low", message: "Patient Monitor log rotation", machine: "M005", time: "4 hours ago", acknowledged: true },
];

const SEVERITY_CONFIG: Record<string, { icon: typeof AlertOctagon; bg: string; text: string }> = {
  critical: { icon: AlertOctagon, bg: "bg-red-50 border-red-200", text: "text-red-700" },
  high: { icon: AlertTriangle, bg: "bg-orange-50 border-orange-200", text: "text-orange-700" },
  medium: { icon: AlertTriangle, bg: "bg-yellow-50 border-yellow-200", text: "text-yellow-700" },
  low: { icon: Info, bg: "bg-blue-50 border-blue-200", text: "text-blue-700" },
};

const FILTERS = [
  {
    key: "severity",
    label: "Severidade",
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
      { label: "Pendente", value: "pending" },
      { label: "Reconhecido", value: "acknowledged" },
    ],
  },
];

const ALERTS_STORAGE_KEY = "fpconnect_alerts";

function readAlerts() {
  if (typeof window === "undefined") return ALERTS;
  try {
    const raw = localStorage.getItem(ALERTS_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as typeof ALERTS) : ALERTS;
  } catch {
    return ALERTS;
  }
}

function writeAlerts(alerts: typeof ALERTS) {
  localStorage.setItem(ALERTS_STORAGE_KEY, JSON.stringify(alerts));
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState(readAlerts);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  const acknowledge = (id: number) => {
    setAlerts((prev) => {
      const next = prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a));
      writeAlerts(next);
      return next;
    });
  };

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return alerts.filter((a) => {
      const matchSearch =
        !q ||
        a.message.toLowerCase().includes(q) ||
        a.machine.toLowerCase().includes(q);
      const matchSeverity = !filters.severity || a.severity === filters.severity;
      const matchStatus =
        !filters.status ||
        (filters.status === "acknowledged" && a.acknowledged) ||
        (filters.status === "pending" && !a.acknowledged);
      return matchSearch && matchSeverity && matchStatus;
    });
  }, [alerts, search, filters]);

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Alertas</h1>
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar
          placeholder="Pesquisar alertas..."
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
      {filtered.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-400">
          Nenhum alerta encontrado.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((a) => {
            const { icon: Icon, bg, text } = SEVERITY_CONFIG[a.severity];
            return (
              <div key={a.id} className={`border rounded-xl p-4 flex items-start gap-3 ${bg}`}>
                <Icon size={20} className={text} />
                <div className="flex-1">
                  <p className={`font-medium ${text}`}>{a.message}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {a.machine} &middot; {a.time}
                  </p>
                </div>
                {!a.acknowledged ? (
                  <button
                    onClick={() => acknowledge(a.id)}
                    className="text-xs px-3 py-1 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Reconhecer
                  </button>
                ) : (
                  <span className="text-xs text-gray-400 italic">Reconhecido</span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
