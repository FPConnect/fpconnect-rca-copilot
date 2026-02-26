"use client";

import { useState } from "react";
import Pagination from "@/components/Pagination";

const EVENTS = [
  { id: 1, action: "Ticket criado", user: "João Silva", resource: "MRI Scanner offline", time: "2026-02-26 14:32" },
  { id: 2, action: "Alerta reconhecido", user: "Maria Santos", resource: "ECG Monitor high latency", time: "2026-02-26 13:10" },
  { id: 3, action: "Manutenção agendada", user: "Carlos Rocha", resource: "Defibrillator", time: "2026-02-26 11:45" },
  { id: 4, action: "Usuário criado", user: "Admin", resource: "Ana Lima", time: "2026-02-26 10:00" },
  { id: 5, action: "Health check falhou", user: "Sistema", resource: "Defibrillator self-test", time: "2026-02-26 09:15" },
  { id: 6, action: "Ticket resolvido", user: "Maria Santos", resource: "Ventilator alarm", time: "2026-02-25 17:22" },
];

const PAGE_SIZE = 4;

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const totalPages = Math.ceil(EVENTS.length / PAGE_SIZE);
  const paginated = EVENTS.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Histórico de Auditoria</h1>
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
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
            {paginated.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{e.action}</td>
                <td className="px-4 py-3 text-gray-600">{e.user}</td>
                <td className="px-4 py-3 text-gray-500">{e.resource}</td>
                <td className="px-4 py-3 text-gray-400 text-xs">{e.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination
        page={page}
        totalPages={totalPages}
        onPrev={() => setPage((p) => Math.max(1, p - 1))}
        onNext={() => setPage((p) => Math.min(totalPages, p + 1))}
      />
    </div>
  );
}
