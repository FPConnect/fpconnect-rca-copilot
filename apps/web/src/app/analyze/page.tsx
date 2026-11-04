"use client";

import { useEffect, useState } from "react";
import { api, type AnalyzeResponse } from "@/services/api";

export default function AnalyzePage() {
  const [ticketId, setTicketId] = useState("101");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reviewerLevel, setReviewerLevel] = useState(0);

  // Human confirmation is opt-in and never prefilled from the machine's draft.
  const [confirmedCause, setConfirmedCause] = useState("");
  const [reviewedRecommendation, setReviewedRecommendation] = useState("");
  const [evidenceRefs, setEvidenceRefs] = useState("");
  const [attested, setAttested] = useState(false);
  const [confirmationBusy, setConfirmationBusy] = useState(false);
  const [confirmationMessage, setConfirmationMessage] = useState("");
  const [confirmationError, setConfirmationError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setTicketId(params.get("ticket_id") ?? "101");
    // Server permissions are always enforced independently of this UI check.
    let active = true;
    api.getMe()
      .then((user) => { if (active) setReviewerLevel(user.access_level ?? 0); })
      .catch(() => { if (active) setReviewerLevel(0); });
    return () => { active = false; };
  }, []);

  const handleAnalyze = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setConfirmationMessage("");
    setConfirmationError("");
    setConfirmedCause("");
    setReviewedRecommendation("");
    setEvidenceRefs("");
    setAttested(false);
    try {
      const id = Number(ticketId);
      if (!Number.isSafeInteger(id) || id <= 0) {
        setError("Informe um identificador numérico válido de chamado.");
        return;
      }
      const response = await api.analyzeIncident(id, description);
      setResult(response);
    } catch {
      setError("Não foi possível concluir a análise. Verifique o chamado e tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmation = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!result || reviewerLevel < 3 || !attested) return;
    const refs = evidenceRefs.split(/[\s,;]+/).map((item) => item.trim()).filter(Boolean);
    if (!refs.length) {
      setConfirmationError("Indique ao menos uma referência não sensível de evidência.");
      return;
    }
    setConfirmationBusy(true);
    setConfirmationError("");
    setConfirmationMessage("");
    try {
      const receipt = await api.confirmIncidentAnalysis(result.ticket_id, {
        root_cause: confirmedCause.trim(),
        recommendation: reviewedRecommendation.trim(),
        evidence_refs: refs,
        confirmed: true,
      });
      setConfirmationMessage(
        `Análise confirmada por responsável autorizado (ID ${receipt.reviewer_id}). ` +
        "O evento foi registrado na trilha de auditoria do chamado.",
      );
      setResult(null);
      setAttested(false);
    } catch {
      setConfirmationError("Confirmação não realizada. Verifique sua permissão, o conteúdo e as referências; nenhuma aprovação é presumida.");
    } finally {
      setConfirmationBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Análise técnica assistiva</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Gerar hipótese técnica para revisão</h1>
        <p className="mt-2 text-sm text-slate-600">
          A análise automatizada não comprova causa raiz nem autoriza manutenção.
          Use apenas registros autorizados; não envie dados pessoais, credenciais ou material confidencial em campos livres.
        </p>
      </section>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={handleAnalyze} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <label className="text-sm font-semibold text-slate-700" htmlFor="ticketId">Chamado</label>
          <input id="ticketId" type="number" min="1" required value={ticketId} onChange={(event) => setTicketId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-2" />
          <label className="mt-5 block text-sm font-semibold text-slate-700" htmlFor="description">Contexto técnico autorizado</label>
          <textarea id="description" value={description} onChange={(event) => setDescription(event.target.value)} rows={8} maxLength={4000} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3" />
          <button type="submit" disabled={loading} className="mt-5 w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-60">
            {loading ? "Analisando..." : "Gerar hipótese (não confirmada)"}
          </button>
          {error && <p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}
        </form>

        <section aria-labelledby="hypothesis-title" className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 id="hypothesis-title" className="text-xl font-bold text-slate-950">Hipótese técnica — revisão humana obrigatória</h2>
          {result ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-xl bg-amber-50 p-4">
                <p className="text-xs font-semibold uppercase text-amber-800">Hipótese não confirmada</p>
                <p className="mt-1 font-semibold text-amber-950">{result.root_cause}</p>
              </div>
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase text-slate-500">Explicação e limitações</p>
                <p className="mt-1 text-sm text-slate-700">{result.explanation}</p>
              </div>
              <p role="status" className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
                Resultado não confirmado. Nenhuma sugestão autoriza reparo, liberação de equipamento ou decisão clínica.
                Qualquer causa final exige revisão independente de evidências por responsável habilitado.
              </p>
              <div className="rounded-xl bg-blue-50 p-4">
                <p className="text-xs font-semibold uppercase text-blue-700">Próximos passos gerais</p>
                <p className="mt-1 text-sm font-medium text-blue-950">{result.recommendation}</p>
              </div>
            </div>
          ) : (
            <p className="mt-5 rounded-xl border border-dashed border-slate-300 p-8 text-sm text-slate-600">
              O sistema poderá sugerir hipóteses e limites de evidência.
              Nenhuma sugestão deve ser tratada como conclusão técnica ou clínica.
            </p>
          )}
        </section>
      </div>

      {reviewerLevel >= 3 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="review-title">
          <h2 id="review-title" className="text-xl font-bold text-slate-950">Confirmação independente por responsável autorizado</h2>
          <p className="mt-2 text-sm leading-6 text-slate-700">
            Disponível apenas aos perfis autorizados. Não copie automaticamente a hipótese gerada.
            Reúna evidências e siga os procedimentos técnicos aplicáveis antes de concluir.
            Insira apenas IDs curtos de evidências, nunca dados pessoais ou logs.
          </p>
          {result && (
            <form onSubmit={handleConfirmation} className="mt-6 space-y-4">
              <div>
                <label htmlFor="reviewCause" className="block text-sm font-semibold">Conclusão técnica revisada</label>
                <textarea id="reviewCause" required minLength={5} maxLength={1200} value={confirmedCause} onChange={(event) => setConfirmedCause(event.target.value)} rows={3} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3" />
              </div>
              <div>
                <label htmlFor="reviewRecommendation" className="block text-sm font-semibold">Orientação revisada e autorizada</label>
                <textarea id="reviewRecommendation" required minLength={5} maxLength={2500} value={reviewedRecommendation} onChange={(event) => setReviewedRecommendation(event.target.value)} rows={3} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3" />
              </div>
              <div>
                <label htmlFor="reviewEvidence" className="block text-sm font-semibold">Referências de evidência (ex.: OS-001 TEST-22)</label>
                <input id="reviewEvidence" required maxLength={650} value={evidenceRefs} onChange={(event) => setEvidenceRefs(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3" />
              </div>
              <label className="flex items-start gap-3 text-sm font-semibold leading-6">
                <input type="checkbox" required checked={attested} onChange={(event) => setAttested(event.target.checked)} className="mt-1 h-5 w-5 accent-blue-700" />
                <span>Atesto que revisei independentemente as evidências referenciadas, tenho autorização para confirmar este caso e não estou usando a hipótese automatizada como prova suficiente.</span>
              </label>
              <button type="submit" disabled={confirmationBusy || !attested} className="min-h-12 rounded-lg bg-slate-950 px-6 py-3 font-bold text-white disabled:opacity-50">
                {confirmationBusy ? "Registrando..." : "Confirmar após revisão técnica"}
              </button>
            </form>
          )}
          {confirmationMessage && <p role="status" className="mt-4 rounded-lg bg-emerald-50 p-4 text-sm text-emerald-900">{confirmationMessage}</p>}
          {confirmationError && <p role="alert" className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-900">{confirmationError}</p>}
        </section>
      )}
    </div>
  );
}
