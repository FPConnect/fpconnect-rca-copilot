import Link from "next/link";
import { Activity, AlertTriangle, ClipboardList, Monitor, SearchCheck, ShieldCheck, Wrench } from "lucide-react";

const METRICS = [
  { label: "Incidentes abertos", value: "12", helper: "4 críticos", href: "/tickets", color: "border-red-200 bg-red-50 text-red-900" },
  { label: "Tempo médio de diagnóstico", value: "18 min", helper: "Meta: 30 min", href: "/analyze", color: "border-blue-200 bg-blue-50 text-blue-900" },
  { label: "Equipamentos críticos", value: "7", helper: "2 offline", href: "/machines", color: "border-amber-200 bg-amber-50 text-amber-900" },
  { label: "SLA cumprido", value: "96%", helper: "2 alertas", href: "/contracts", color: "border-emerald-200 bg-emerald-50 text-emerald-900" },
];

const FLOW = [
  { href: "/dashboard", icon: Activity, title: "Dashboard mostra problemas", description: "Métricas destacam incidentes abertos, equipamentos críticos e alertas de contrato." },
  { href: "/tickets", icon: ClipboardList, title: "Abra o incidente", description: "Acesse unidade, severidade, timeline de eventos e causa provável." },
  { href: "/analyze", icon: SearchCheck, title: "Clique em Analisar", description: "O Diagnóstico de Falha gera causa raiz, explicação e próximos passos." },
  { href: "/playbooks", icon: Wrench, title: "Execute o playbook", description: "Siga procedimentos padronizados e anexe evidências técnicas." },
];

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <section className="rounded-2xl bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-7 text-white shadow-xl">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-200">FPConnect Engenharia Clínica</p>
        <h1 className="mt-2 text-3xl font-black tracking-tight">Painel operacional do parque médico</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-200">
          Fluxo claro para priorizar risco assistencial: identifique problemas, abra o chamado, gere diagnóstico de falha e aplique o playbook adequado.
        </p>
      </section>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {METRICS.map((metric) => (
          <Link key={metric.label} href={metric.href} className={`rounded-2xl border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${metric.color}`}>
            <div className="text-3xl font-black">{metric.value}</div>
            <div className="mt-2 text-sm font-semibold">{metric.label}</div>
            <div className="mt-1 text-xs opacity-80">{metric.helper}</div>
          </Link>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Fluxo recomendado de atendimento</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {FLOW.map(({ href, icon: Icon, title, description }) => (
              <Link key={href} href={href} className="group rounded-xl border border-slate-200 p-4 transition hover:border-blue-200 hover:bg-blue-50">
                <Icon className="text-blue-700" size={22} />
                <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-slate-600">{description}</p>
              </Link>
            ))}
          </div>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-950">Alertas prioritários</h2>
          <div className="mt-5 space-y-3">
            <div className="flex gap-3 rounded-xl bg-red-50 p-4 text-sm text-red-900"><AlertTriangle size={20} /><span>Desfibrilador offline no Pronto Atendimento requer ação imediata.</span></div>
            <div className="flex gap-3 rounded-xl bg-amber-50 p-4 text-sm text-amber-900"><Monitor size={20} /><span>Monitor multiparamétrico com 4 falhas recorrentes de SpO2.</span></div>
            <div className="flex gap-3 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-900"><ShieldCheck size={20} /><span>SLA de ventiladores dentro da meta, mas contrato vence em 30 dias.</span></div>
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-lg shadow-slate-900/30"><p className="text-sm text-slate-400">MTTR assistencial</p><h3 className="mt-2 text-3xl font-bold text-white">3,2h</h3><p className="mt-4 text-xs font-medium text-emerald-400">-12% vs mês anterior</p></div>
        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-lg shadow-slate-900/30"><p className="text-sm text-slate-400">Disponibilidade crítica</p><h3 className="mt-2 text-3xl font-bold text-white">98,8%</h3><p className="mt-4 text-xs font-medium text-emerald-400">+0,2% vs mês anterior</p></div>
        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-lg shadow-slate-900/30"><p className="text-sm text-slate-400">Playbooks executados</p><h3 className="mt-2 text-3xl font-bold text-white">24</h3><p className="mt-4 text-xs font-medium text-blue-300">padronização em alta</p></div>
      </div>
    </div>
  );
}
