import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  ClipboardCheck,
  DatabaseZap,
  FileWarning,
  Radar,
  ShieldAlert,
} from "lucide-react";
import { CLINICAL_RISK_ASSETS, type RiskSeverity } from "@/lib/differentiators";

const severityTone: Record<RiskSeverity, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  medium: "bg-amber-100 text-amber-800 border-amber-200",
  low: "bg-emerald-100 text-emerald-800 border-emerald-200",
};

const severityLabel: Record<RiskSeverity, string> = {
  critical: "crítico",
  high: "alto",
  medium: "médio",
  low: "baixo",
};

const statusTone = {
  action_required: "bg-red-50 text-red-700 border-red-200",
  monitor: "bg-amber-50 text-amber-700 border-amber-200",
  cleared: "bg-emerald-50 text-emerald-700 border-emerald-200",
};

const statusLabel = {
  action_required: "ação obrigatória",
  monitor: "monitorar",
  cleared: "liberado",
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function RiskRadarPage() {
  const criticalAssets = CLINICAL_RISK_ASSETS.filter((asset) => asset.status === "action_required");
  const totalImpact = CLINICAL_RISK_ASSETS.reduce((sum, asset) => sum + asset.downtimeImpactBRL, 0);
  const openSignals = CLINICAL_RISK_ASSETS.reduce((sum, asset) => sum + asset.signals.length, 0);

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="border-b border-slate-200 pb-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-red-700">
              <ShieldAlert size={14} />
              FPConnect Radar de Risco Clínico
            </div>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">
              Cruze cada equipamento com recall, cibersegurança, UDI, SBOM e risco regulatório.
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-600 md:text-base">
              O módulo transforma fontes externas em ações por ativo. O hospital não recebe uma lista de notícias: recebe uma fila priorizada por leito, criticidade clínica, firmware, UDI e impacto financeiro.
            </p>
          </div>
          <Link
            href="/evidence-copilot"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800"
          >
            Ver RCA com evidência
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="border-l-4 border-red-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Ativos com ação obrigatória</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{criticalAssets.length}</p>
          <p className="mt-1 text-xs text-slate-500">Fila pronta para engenharia clínica e qualidade.</p>
        </div>
        <div className="border-l-4 border-amber-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Sinais externos correlacionados</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{openSignals}</p>
          <p className="mt-1 text-xs text-slate-500">Recall, cibersegurança, UDI, SBOM e evidências internas.</p>
        </div>
        <div className="border-l-4 border-emerald-500 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Impacto financeiro protegido</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{formatCurrency(totalImpact)}</p>
          <p className="mt-1 text-xs text-slate-500">Estimativa por indisponibilidade evitada em ativos críticos.</p>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="space-y-4">
          {CLINICAL_RISK_ASSETS.map((asset) => (
            <article key={asset.id} className="border border-slate-200 bg-white shadow-sm">
              <div className="flex flex-col gap-4 border-b border-slate-100 p-5 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl font-semibold text-slate-950">{asset.name}</h2>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                      {asset.id}
                    </span>
                    <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusTone[asset.status]}`}>
                      {statusLabel[asset.status]}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-500">
                    {asset.location} | {asset.manufacturer} {asset.model} | Firmware {asset.firmware}
                  </p>
                  <p className="mt-1 text-xs font-mono text-slate-500">UDI {asset.udi}</p>
                </div>
                <div className="min-w-32 border border-slate-200 p-3 text-center">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Pontuação de risco</p>
                  <p className="mt-1 text-4xl font-bold text-red-700">{asset.overallRisk}</p>
                </div>
              </div>

              <div className="grid gap-0 border-b border-slate-100 md:grid-cols-3">
                <div className="border-b border-slate-100 p-4 md:border-b-0 md:border-r">
                  <p className="text-xs font-semibold uppercase text-slate-500">Recall</p>
                  <p className="mt-1 text-2xl font-bold text-slate-950">{asset.recallRisk}</p>
                </div>
                <div className="border-b border-slate-100 p-4 md:border-b-0 md:border-r">
                  <p className="text-xs font-semibold uppercase text-slate-500">Ciber/SBOM</p>
                  <p className="mt-1 text-2xl font-bold text-slate-950">{asset.cyberRisk}</p>
                </div>
                <div className="p-4">
                  <p className="text-xs font-semibold uppercase text-slate-500">Regulatório</p>
                  <p className="mt-1 text-2xl font-bold text-slate-950">{asset.regulatoryRisk}</p>
                </div>
              </div>

              <div className="grid gap-5 p-5 lg:grid-cols-2">
                <div>
                  <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
                    <Radar size={16} />
                    Sinais correlacionados
                  </div>
                  <div className="space-y-3">
                    {asset.signals.map((signal) => (
                      <div key={`${asset.id}-${signal.title}`} className="border border-slate-100 bg-slate-50 p-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${severityTone[signal.severity]}`}>
                            {severityLabel[signal.severity]}
                          </span>
                          <span className="text-xs font-semibold uppercase text-slate-500">{signal.source}</span>
                        </div>
                        <p className="mt-2 text-sm font-semibold text-slate-900">{signal.title}</p>
                        <p className="mt-1 text-xs leading-5 text-slate-600">{signal.evidence}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
                    <ClipboardCheck size={16} />
                    Ações recomendadas
                  </div>
                  <ol className="space-y-2">
                    {asset.recommendedActions.map((action, index) => (
                      <li key={action} className="flex gap-3 text-sm leading-5 text-slate-700">
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">
                          {index + 1}
                        </span>
                        <span>{action}</span>
                      </li>
                    ))}
                  </ol>
                  <div className="mt-4 border border-blue-100 bg-blue-50 p-3 text-sm text-blue-900">
                    <p className="font-semibold">Pacote de auditoria</p>
                    <p className="mt-1 text-xs leading-5">{asset.auditPacket}</p>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>

        <aside className="space-y-4">
          <div className="border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <DatabaseZap size={16} />
              Fontes que viram vantagem
            </div>
            <ul className="mt-4 space-y-3 text-sm leading-5 text-slate-600">
              <li>Feeds openFDA/FDA de recall por família, modelo e ação corretiva.</li>
              <li>AccessGUDID/UDI para rastreabilidade do ativo e acessórios.</li>
              <li>CISA KEV, NVD/CVE, MDS2 e SBOM para risco cibernético por firmware.</li>
              <li>Histórico interno de chamados, manutenção preventiva e RCA para priorização clínica.</li>
            </ul>
          </div>
          <div className="border border-red-200 bg-red-50 p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-red-900">
              <FileWarning size={16} />
              Diferença comercial
            </div>
            <p className="mt-3 text-sm leading-6 text-red-900">
              Concorrentes entregam ordem de serviço. Este módulo entrega uma justificativa executiva: qual ativo está vulnerável, por que importa, quanto custa e qual evidência precisa ser anexada.
            </p>
          </div>
          <div className="border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <AlertTriangle size={16} />
              Próximo passo natural
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Ao clicar no caso, o RCA Copilot deve abrir já com UDI, sinais externos e histórico anexados.
            </p>
            <Link
              href="/evidence-copilot"
              className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-700 hover:text-blue-900"
            >
              Abrir RCA Copilot
              <ArrowRight size={15} />
            </Link>
          </div>
        </aside>
      </section>
    </div>
  );
}
