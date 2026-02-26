"use client";

import { useState } from "react";
import { AlertTriangle, Info, AlertOctagon } from "lucide-react";

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

export default function AlertsPage() {
  const [alerts, setAlerts] = useState(ALERTS);

  const acknowledge = (id: number) => {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a)));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Alertas</h1>
      <div className="space-y-3">
        {alerts.map((a) => {
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
    </div>
  );
}
