"use client";

import { useEffect, useState } from "react";
import { api, AnalyzeResponse } from "@/services/api";

export default function AnalyzePage() {
  const [ticketId, setTicketId] = useState("101");
  const [description, setDescription] = useState("Monitor multiparamétrico apresenta perda intermitente de SpO2 na UTI Adulto.");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setTicketId(params.get("ticket_id") ?? "101");
  }, []);

  const handleAnalyze = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await api.analyzeIncident(Number(ticketId));
      setResult(response);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Diagnóstico de Falha</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Analisar ocorrência e sugerir causa raiz</h1>
        <p className="mt-2 text-sm text-slate-600">Use esta tela após abrir um chamado: informe a ocorrência, acione a análise e siga os próximos passos recomendados.</p>
      </section>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={handleAnalyze} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <label className="text-sm font-semibold text-slate-700" htmlFor="ticketId">Chamado</label>
          <input id="ticketId" value={ticketId} onChange={(event) => setTicketId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2" />
          <label className="mt-5 block text-sm font-semibold text-slate-700" htmlFor="description">Descrição da Ocorrência</label>
          <textarea id="description" value={description} onChange={(event) => setDescription(event.target.value)} rows={8} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3" />
          <button type="submit" disabled={loading} className="mt-5 w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-60">
            {loading ? "Analisando..." : "Analisar falha"}
          </button>
        </form>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Resultado do diagnóstico</h2>
          {result ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-xl bg-red-50 p-4"><p className="text-xs font-semibold uppercase text-red-700">Sugestão de Causa Raiz</p><p className="mt-1 font-semibold text-red-950">{result.root_cause}</p></div>
              <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold uppercase text-slate-500">Explicação</p><p className="mt-1 text-sm text-slate-700">{result.explanation}</p></div>
              <div className="rounded-xl bg-blue-50 p-4"><p className="text-xs font-semibold uppercase text-blue-700">Próximos Passos</p><p className="mt-1 text-sm font-medium text-blue-950">{result.recommendation}</p></div>
            </div>
          ) : (
            <div className="mt-5 rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
              O diagnóstico aparecerá aqui com causa raiz, explicação e próximos passos.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
