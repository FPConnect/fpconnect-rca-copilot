import Link from "next/link";
import {
  ArrowRight,
  Brain,
  ClipboardList,
  FileText,
  MessageSquareText,
  SearchCheck,
  ShieldCheck,
} from "lucide-react";
import { EVIDENCE_COPILOT_CASES } from "@/lib/differentiators";

const evidenceTone = {
  manual: "bg-blue-50 text-blue-800 border-blue-200",
  history: "bg-emerald-50 text-emerald-800 border-emerald-200",
  telemetry: "bg-violet-50 text-violet-800 border-violet-200",
  external: "bg-orange-50 text-orange-800 border-orange-200",
  checklist: "bg-slate-100 text-slate-800 border-slate-200",
};

export default function EvidenceCopilotPage() {
  const averageConfidence = Math.round(
    EVIDENCE_COPILOT_CASES.reduce((sum, item) => sum + item.confidence, 0) /
      EVIDENCE_COPILOT_CASES.length,
  );

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="border-b border-slate-200 pb-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-700">
              <Brain size={14} />
              RCA Copilot com evidencia
            </div>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">
              O tecnico nao recebe uma resposta generica; recebe um pacote tecnico defensavel.
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-600 md:text-base">
              Cada analise combina sintomas, manuais, historico, telemetria, sinais externos e perguntas guiadas. O resultado vira checklist de contencao, mensagem para fornecedor e rascunho CAPA/RCA.
            </p>
          </div>
          <Link
            href="/value-engine"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800"
          >
            Ver motor de valor
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="border-l-4 border-blue-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Casos RCA prontos</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{EVIDENCE_COPILOT_CASES.length}</p>
        </div>
        <div className="border-l-4 border-emerald-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Confianca media</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{averageConfidence}%</p>
        </div>
        <div className="border-l-4 border-orange-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Pacotes OEM</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">2</p>
        </div>
        <div className="border-l-4 border-violet-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Evidencias anexadas</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">
            {EVIDENCE_COPILOT_CASES.reduce((sum, item) => sum + item.evidence.length, 0)}
          </p>
        </div>
      </section>

      <section className="space-y-5">
        {EVIDENCE_COPILOT_CASES.map((item) => (
          <article key={item.id} className="border border-slate-200 bg-white shadow-sm">
            <div className="grid gap-0 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="border-b border-slate-200 p-5 lg:border-b-0 lg:border-r">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-slate-900 px-2.5 py-1 text-xs font-semibold text-white">
                    {item.id}
                  </span>
                  <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                    {item.confidence}% confianca
                  </span>
                </div>
                <h2 className="mt-3 text-2xl font-bold text-slate-950">{item.ticketTitle}</h2>
                <p className="mt-1 text-sm text-slate-500">
                  {item.assetName} | {item.assetId}
                </p>

                <div className="mt-5 space-y-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                      <SearchCheck size={16} />
                      Sintoma
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{item.symptom}</p>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                      <ShieldCheck size={16} />
                      Causa provavel
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{item.probableCause}</p>
                  </div>
                </div>

                <div className="mt-5 border border-blue-100 bg-blue-50 p-4">
                  <div className="flex items-center gap-2 text-sm font-semibold text-blue-950">
                    <ClipboardList size={16} />
                    Contencao guiada
                  </div>
                  <ol className="mt-3 space-y-2">
                    {item.containmentSteps.map((step, index) => (
                      <li key={step} className="flex gap-3 text-sm leading-5 text-blue-950">
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-700 text-xs font-bold text-white">
                          {index + 1}
                        </span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>

              <div className="p-5">
                <div className="grid gap-4 xl:grid-cols-2">
                  <div>
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Evidencias usadas</h3>
                    <div className="mt-3 space-y-3">
                      {item.evidence.map((evidence) => (
                        <div key={`${item.id}-${evidence.label}`} className="border border-slate-100 bg-slate-50 p-3">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${evidenceTone[evidence.type]}`}>
                              {evidence.type}
                            </span>
                            <span className="text-xs font-semibold text-slate-700">{evidence.label}</span>
                          </div>
                          <p className="mt-2 text-xs leading-5 text-slate-600">{evidence.excerpt}</p>
                          <p className="mt-2 text-xs font-semibold text-emerald-700">{evidence.confidenceImpact}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Perguntas inteligentes</h3>
                    <ul className="mt-3 space-y-2">
                      {item.guidedQuestions.map((question) => (
                        <li key={question} className="border-l-4 border-slate-300 bg-slate-50 p-3 text-sm leading-5 text-slate-700">
                          {question}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 xl:grid-cols-2">
                  <div className="border border-orange-100 bg-orange-50 p-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-orange-950">
                      <MessageSquareText size={16} />
                      Mensagem para OEM
                    </div>
                    <p className="mt-2 text-sm leading-6 text-orange-950">{item.oemMessage}</p>
                  </div>
                  <div className="border border-emerald-100 bg-emerald-50 p-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-emerald-950">
                      <FileText size={16} />
                      Rascunho CAPA/RCA
                    </div>
                    <p className="mt-2 text-sm leading-6 text-emerald-950">{item.capaDraft}</p>
                  </div>
                </div>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
