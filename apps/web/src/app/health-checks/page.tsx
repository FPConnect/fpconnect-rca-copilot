"use client";

import { useState } from "react";
import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";

const CHECKS = [
  { id: 1, machine: "MRI Scanner", check: "Temperature", result: "OK", value: "36°C", time: "2 min ago" },
  { id: 2, machine: "ECG Monitor", check: "Connectivity", result: "WARNING", value: "Latency 250ms", time: "5 min ago" },
  { id: 3, machine: "Ventilator", check: "Battery", result: "OK", value: "98%", time: "1 min ago" },
  { id: 4, machine: "Defibrillator", check: "Self-test", result: "FAIL", value: "Error code 0x1A", time: "1 hour ago" },
  { id: 5, machine: "Patient Monitor", check: "Signal", result: "OK", value: "Strong", time: "3 min ago" },
];

const RESULT_CONFIG: Record<string, { icon: typeof CheckCircle; color: string }> = {
  OK: { icon: CheckCircle, color: "text-green-500" },
  WARNING: { icon: AlertTriangle, color: "text-yellow-500" },
  FAIL: { icon: XCircle, color: "text-red-500" },
};

export default function HealthChecksPage() {
  const [filter, setFilter] = useState<string>("ALL");

  const filtered = filter === "ALL" ? CHECKS : CHECKS.filter((c) => c.result === filter);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Health Checks</h1>
        <div className="flex gap-2">
          {["ALL", "OK", "WARNING", "FAIL"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === f
                  ? "bg-blue-600 text-white"
                  : "bg-white border border-gray-300 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-3">
        {filtered.map((c) => {
          const { icon: Icon, color } = RESULT_CONFIG[c.result];
          return (
            <div key={c.id} className="bg-white rounded-xl shadow p-4 flex items-center gap-4">
              <Icon size={24} className={color} />
              <div className="flex-1">
                <p className="font-medium text-gray-900">
                  {c.machine} — {c.check}
                </p>
                <p className="text-sm text-gray-500">{c.value}</p>
              </div>
              <span className="text-xs text-gray-400">{c.time}</span>
            </div>
          );
        })}
        {filtered.length === 0 && (
          <p className="text-gray-500 text-center py-8">Nenhum resultado encontrado.</p>
        )}
      </div>
    </div>
  );
}
