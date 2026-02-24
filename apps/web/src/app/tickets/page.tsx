"use client";

import { useState } from "react";

interface Ticket {
  id: number;
  title: string;
  status: string;
  priority: string;
}

const MOCK_TICKETS: Ticket[] = [
  { id: 1, title: "MRI Scanner offline - Ward A", status: "open", priority: "critical" },
  { id: 2, title: "ECG Monitor slow response", status: "in_progress", priority: "high" },
  { id: 3, title: "Patient monitor alarm", status: "open", priority: "medium" },
];

export default function TicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>(MOCK_TICKETS);
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    const newTicket: Ticket = {
      id: tickets.length + 1,
      title: title.trim(),
      status: "open",
      priority,
    };
    setTickets([newTicket, ...tickets]);
    setTitle("");
    setPriority("medium");
  };

  const priorityColors: Record<string, string> = {
    critical: "bg-red-100 text-red-800",
    high: "bg-orange-100 text-orange-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-green-100 text-green-800",
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Tickets</h1>

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
              onChange={(e) => setTitle(e.target.value)}
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
        </form>

        {/* Ticket List */}
        <div className="space-y-3">
          {tickets.map((t) => (
            <div
              key={t.id}
              className="bg-white rounded-xl shadow p-4 flex items-center justify-between"
            >
              <div>
                <span className="font-medium text-gray-900">{t.title}</span>
                <span className="ml-2 text-sm text-gray-500">#{t.id}</span>
              </div>
              <div className="flex gap-2">
                <span
                  className={`text-xs font-semibold px-2 py-1 rounded-full ${priorityColors[t.priority]}`}
                >
                  {t.priority}
                </span>
                <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                  {t.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
