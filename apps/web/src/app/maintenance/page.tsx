"use client";

import { useState } from "react";
import Modal from "@/components/Modal";
import Form from "@/components/Form";

const SCHEDULED = [
  { id: 1, machine: "MRI Scanner", type: "Preventive", date: "2026-03-01", technician: "João Silva", status: "scheduled" },
  { id: 2, machine: "Defibrillator", type: "Corrective", date: "2026-02-27", technician: "Maria Santos", status: "in_progress" },
  { id: 3, machine: "ECG Monitor", type: "Calibration", date: "2026-03-10", technician: "Carlos Rocha", status: "scheduled" },
];

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
};

export default function MaintenancePage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [machine, setMachine] = useState("");
  const [date, setDate] = useState("");
  const [type, setType] = useState("Preventive");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setModalOpen(false);
    setMachine("");
    setDate("");
    setType("Preventive");
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Manutenção</h1>
        <button
          onClick={() => setModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Agendar Manutenção
        </button>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["Máquina", "Tipo", "Data", "Técnico", "Status"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {SCHEDULED.map((s) => (
              <tr key={s.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{s.machine}</td>
                <td className="px-4 py-3 text-gray-600">{s.type}</td>
                <td className="px-4 py-3 text-gray-600">{s.date}</td>
                <td className="px-4 py-3 text-gray-600">{s.technician}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${STATUS_COLORS[s.status]}`}>
                    {s.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modalOpen} title="Agendar Manutenção" onClose={() => setModalOpen(false)}>
        <Form onSubmit={handleSubmit} className="shadow-none p-0">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Máquina</label>
              <input
                type="text"
                value={machine}
                onChange={(e) => setMachine(e.target.value)}
                placeholder="Ex: MRI Scanner"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Preventive">Preventiva</option>
                <option value="Corrective">Corretiva</option>
                <option value="Calibration">Calibração</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 text-sm rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700"
              >
                Agendar
              </button>
            </div>
          </div>
        </Form>
      </Modal>
    </div>
  );
}
