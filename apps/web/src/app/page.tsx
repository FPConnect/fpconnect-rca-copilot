import Link from "next/link";
import { ShieldCheck, Activity, Siren, ArrowRight, Server, Clock3, Stethoscope } from "lucide-react";

const HIGHLIGHTS = [
  {
    icon: Activity,
    title: "Observabilidade em tempo real",
    description: "Monitore disponibilidade, alertas e comportamento de equipamentos críticos em um único painel.",
  },
  {
    icon: Siren,
    title: "Resposta rápida a incidentes",
    description: "Abra e acompanhe tickets com contexto técnico para acelerar análise RCA e reduzir MTTR.",
  },
  {
    icon: ShieldCheck,
    title: "Confiabilidade operacional",
    description: "Padronize verificações e priorize riscos para manter continuidade clínica e segurança do paciente.",
  },
];

const KPI = [
  { label: "Equipamentos monitoráveis", value: "1.200+", icon: Server },
  { label: "Redução média de MTTR", value: "-32%", icon: Clock3 },
  { label: "SLA de disponibilidade", value: "99,9%", icon: Stethoscope },
];

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.25),_transparent_45%),radial-gradient(circle_at_80%_20%,_rgba(59,130,246,0.2),_transparent_35%)]" />
      <div className="relative mx-auto max-w-6xl px-6 pb-16 pt-12 md:pt-20">
        <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-200">
          <ShieldCheck size={14} /> Plataforma de monitoramento para operações hospitalares
        </div>

        <div className="mt-6 grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <h1 className="text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
              Visibilidade total para
              <span className="block bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent">
                Engenharia Clínica e TI Biomédica
              </span>
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg">
              O FPConnect centraliza monitoramento, alertas, tickets e histórico operacional para sua equipe tomar
              decisões rápidas e reduzir indisponibilidade de equipamentos de missão crítica.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-300"
              >
                Acessar plataforma <ArrowRight size={16} />
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-600 px-5 py-3 text-sm font-semibold text-slate-200 transition hover:border-cyan-300 hover:text-cyan-200"
              >
                Ver dashboard demo
              </Link>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-700/80 bg-slate-900/70 p-5 shadow-2xl shadow-cyan-950/30 backdrop-blur">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Indicadores operacionais</p>
            <div className="mt-4 space-y-3">
              {KPI.map(({ label, value, icon: Icon }) => (
                <div key={label} className="flex items-center justify-between rounded-xl border border-slate-700 bg-slate-900 px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="rounded-lg bg-cyan-500/15 p-2 text-cyan-300">
                      <Icon size={16} />
                    </span>
                    <span className="text-sm text-slate-300">{label}</span>
                  </div>
                  <strong className="text-lg text-white">{value}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        <section className="mt-14 grid gap-4 md:grid-cols-3">
          {HIGHLIGHTS.map(({ icon: Icon, title, description }) => (
            <article key={title} className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5 shadow-lg shadow-slate-900/50">
              <div className="mb-3 inline-flex rounded-lg bg-cyan-500/15 p-2 text-cyan-300">
                <Icon size={18} />
              </div>
              <h2 className="text-lg font-bold text-white">{title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{description}</p>
            </article>
          ))}
        </section>
      </div>
    </div>
  );
}
