"use client";

import { useState } from "react";
import Pagination from "@/components/Pagination";

const MACHINES = [
  { id: "M001", name: "MRI Scanner", location: "Ward A", status: "online", lastCheck: "2 min ago" },
  { id: "M002", name: "ECG Monitor", location: "ICU", status: "warning", lastCheck: "5 min ago" },
  { id: "M003", name: "Ventilator", location: "Ward B", status: "online", lastCheck: "1 min ago" },
  { id: "M004", name: "Defibrillator", location: "Emergency", status: "offline", lastCheck: "1 hour ago" },
  { id: "M005", name: "Patient Monitor", location: "Ward C", status: "online", lastCheck: "3 min ago" },
  { id: "M006", name: "Infusion Pump", location: "Ward A", status: "online", lastCheck: "2 min ago" },
];

const STATUS_COLORS: Record<string, string> = {
  online: "bg-green-100 text-green-700",
  warning: "bg-yellow-100 text-yellow-700",
  offline: "bg-red-100 text-red-700",
};

const PAGE_SIZE = 4;

export default function MachinesPage() {
  const [page, setPage] = useState(1);
  const totalPages = Math.ceil(MACHINES.length / PAGE_SIZE);
  const paginated = MACHINES.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Máquinas</h1>
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["ID", "Nome", "Localização", "Status", "Último Check"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {paginated.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-gray-500">{m.id}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{m.name}</td>
                <td className="px-4 py-3 text-gray-600">{m.location}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${STATUS_COLORS[m.status]}`}>
                    {m.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{m.lastCheck}</td>
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
