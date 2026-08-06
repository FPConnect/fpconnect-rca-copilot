import Link from "next/link";
import {
  ArrowRight,
  BadgeDollarSign,
  BarChart3,
  BriefcaseBusiness,
  CircleDollarSign,
  FileText,
  LineChart,
  Target,
} from "lucide-react";
import { VALUE_ENGINE_SCENARIOS } from "@/lib/differentiators";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

const renewalTone = {
  low: "bg-emerald-50 text-emerald-800 border-emerald-200",
  medium: "bg-amber-50 text-amber-800 border-amber-200",
  high: "bg-red-50 text-red-800 border-red-200",
};

const renewalLabel = {
  low: "baixo",
  medium: "médio",
  high: "alto",
};

export default function ValueEnginePage() {
  const totalAvoidedLoss = VALUE_ENGINE_SCENARIOS.reduce((sum, item) => sum + item.avoidedLossBRL, 0);
  const totalExpansion = VALUE_ENGINE_SCENARIOS.reduce((sum, item) => sum + item.renewalExpansionBRL, 0);
  const totalProtectedAssets = VALUE_ENGINE_SCENARIOS.reduce((sum, item) => sum + item.protectedAssets, 0);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="border-b border-slate-200 pb-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-700">
              <CircleDollarSign size={14} />
              FPConnect Motor de Valor
            </div>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">
              Transforme engenharia clínica em dinheiro protegido, risco reduzido e renovação.
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-600 md:text-base">
              O sistema deixa de entregar apenas relatórios operacionais. Ele gera uma narrativa executiva de ROI, expansão contratual e valor de pós-venda para diretoria, financeiro e patrocinador do contrato.
            </p>
          </div>
          <Link
            href="/risk-radar"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800"
          >
            Voltar ao Radar de Risco
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="border-l-4 border-emerald-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Perda evitada demonstrável</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{formatCurrency(totalAvoidedLoss)}</p>
          <p className="mt-1 text-xs text-slate-500">Base para conversa com diretoria e financeiro.</p>
        </div>
        <div className="border-l-4 border-blue-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Upsell recomendado</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{formatCurrency(totalExpansion)}</p>
          <p className="mt-1 text-xs text-slate-500">Pacotes de expansão defendidos por evidências.</p>
        </div>
        <div className="border-l-4 border-violet-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Ativos críticos protegidos</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{totalProtectedAssets}</p>
          <p className="mt-1 text-xs text-slate-500">Escopo premium de monitoramento e RCA.</p>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <aside className="space-y-4">
          <div className="border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <BriefcaseBusiness size={16} />
              Como vender diferente
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              A conversa deixa de ser &quot;temos painel e chamados&quot; e vira &quot;protegemos X reais, reduzimos Y horas de indisponibilidade e sabemos onde expandir o contrato&quot;.
            </p>
          </div>
          <div className="border border-emerald-200 bg-emerald-50 p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-emerald-950">
              <Target size={16} />
              Oferta premium sugerida
            </div>
            <ul className="mt-3 space-y-2 text-sm leading-5 text-emerald-950">
              <li>Radar de Risco para compliance, recall e cibersegurança.</li>
              <li>RCA Copilot com evidências e pacote para fabricante.</li>
              <li>Relatório mensal executivo de ROI e renovação.</li>
            </ul>
          </div>
          <div className="border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <FileText size={16} />
              Entregáveis que geram renovação
            </div>
            <ul className="mt-3 space-y-2 text-sm leading-5 text-slate-600">
              <li>Resumo executivo mensal para diretoria.</li>
              <li>Ranking de ativos que justificam expansão.</li>
              <li>Pacote de evidências para qualidade, auditoria e fornecedor.</li>
              <li>Comparativo antes/depois de SLA, MTTR e disponibilidade.</li>
            </ul>
          </div>
        </aside>

        <div className="space-y-5">
          {VALUE_ENGINE_SCENARIOS.map((scenario) => (
            <article key={scenario.id} className="border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-100 p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-slate-900 px-2.5 py-1 text-xs font-semibold text-white">
                    {scenario.period}
                  </span>
                  <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${renewalTone[scenario.renewalRisk]}`}>
                    risco de renovação {renewalLabel[scenario.renewalRisk]}
                  </span>
                </div>
                <h2 className="mt-3 text-2xl font-bold text-slate-950">{scenario.clientProfile}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{scenario.executiveNarrative}</p>
              </div>

              <div className="grid gap-0 border-b border-slate-100 md:grid-cols-3">
                <div className="border-b border-slate-100 p-4 md:border-b-0 md:border-r">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
                    <BarChart3 size={14} />
                    Horas evitadas
                  </div>
                  <p className="mt-1 text-2xl font-bold text-slate-950">{scenario.avoidedDowntimeHours} h</p>
                </div>
                <div className="border-b border-slate-100 p-4 md:border-b-0 md:border-r">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
                    <BadgeDollarSign size={14} />
                    Perda evitada
                  </div>
                  <p className="mt-1 text-2xl font-bold text-slate-950">{formatCurrency(scenario.avoidedLossBRL)}</p>
                </div>
                <div className="p-4">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
                    <LineChart size={14} />
                    Expansão
                  </div>
                  <p className="mt-1 text-2xl font-bold text-slate-950">{formatCurrency(scenario.renewalExpansionBRL)}</p>
                </div>
              </div>

              <div className="grid gap-5 p-5 lg:grid-cols-2">
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Alavancas de valor</h3>
                  <div className="mt-3 space-y-3">
                    {scenario.levers.map((lever) => (
                      <div key={lever.label} className="border border-slate-100 bg-slate-50 p-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-slate-900">{lever.label}</p>
                          <p className="text-sm font-bold text-emerald-700">{lever.value}</p>
                        </div>
                        <p className="mt-1 text-xs leading-5 text-slate-600">{lever.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Perguntas de diretoria</h3>
                  <ul className="mt-3 space-y-2">
                    {scenario.boardQuestions.map((question) => (
                      <li key={question} className="border-l-4 border-emerald-400 bg-emerald-50 p-3 text-sm leading-5 text-emerald-950">
                        {question}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4 border border-blue-100 bg-blue-50 p-4">
                    <p className="text-sm font-semibold text-blue-950">Oferta recomendada</p>
                    <p className="mt-2 text-sm leading-6 text-blue-950">{scenario.recommendedOffer}</p>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
