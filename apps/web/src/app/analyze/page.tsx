"use client";

import { useEffect, useState } from "react";
import { api, AnalyzeResponse } from "@/services/api";

export default function AnalyzePage() {
  const [ticketId, setTicketId] = useState("101");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setTicketId(params.get("ticket_id") ?? "101");
  }, []);

  const handleAnalyze = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await api.analyzeIncident(Number(ticketId), description);
      setResult(response);
    } catch {
      setError("Não foi possível concluir a análise. Verifique o chamado e tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Análise técnica assistiva</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Gerar hipótese técnica para revisão</h1>
        <p className="mt-2 text-sm text-slate-600">Use os registros autorizados para obter uma hipótese de investigação, nunca um diagnóstico confirmado. Não envie dados de pacientes, credenciais nem registros confidenciais em campos livres.</p>
      </section>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={handleAnalyze} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <label className="text-sm font-semibold text-slate-700" htmlFor="ticketId">Chamado</label>
          <input id="ticketId" value={ticketId} onChange={(event) => setTicketId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2" />
          <label className="mt-5 block text-sm font-semibold text-slate-700" htmlFor="description">Descrição da Ocorrência</label>
          <textarea id="description" value={description} onChange={(event) => setDescription(event.target.value)} rows={8} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3" />
          <button type="submit" disabled={loading} className="mt-5 w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-60">
            {loading ? "Analisando..." : "Gerar hipótese (não confirmada)"}
          </button>
          {error && <p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}
        </form>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Hipótese técnica — revisão humana obrigatória</h2>
          {result ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-xl bg-amber-50 p-4"><p className="text-xs font-semibold uppercase text-amber-800">Hipótese não confirmada</p><p className="mt-1 font-semibold text-amber-950">{result.root_cause}</p></div>
              <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold uppercase text-slate-500">Explicação</p><p className="mt-1 text-sm text-slate-700">{result.explanation}</p></div>
              <div role="status" className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">A análise automatizada NÃO confirma causa raiz, não autoriza reparo ou liberação de equipamento e não substitui o procedimento do fabricante. Um responsável técnico deve avaliar as evidências e confirmar a conclusão pelo fluxo autorizado.</div>
              <div className="rounded-xl bg-blue-50 p-4"><p className="text-xs font-semibold uppercase text-blue-700">Próximos Passos</p><p className="mt-1 text-sm font-medium text-blue-950">{result.recommendation}</p></div>
            </div>
          ) : (
            <div className="mt-5 rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
              O sistema poderá sugerir hipóteses e limites de evidência. Nenhuma sugestão deve ser tratada como conclusão técnica ou clínica.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
