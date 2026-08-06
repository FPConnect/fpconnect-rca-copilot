import Link from "next/link";
import {
  Monitor,
  HeartPulse,
  Bell,
  Ticket,
  BarChart2,
  Settings,
  ShieldAlert,
  BookOpenCheck,
  CircleDollarSign,
} from "lucide-react";

type PerformanceStatProps = { title: string; value: string; unit: string; trend: string };

const PerformanceStat = ({ title, value, unit, trend }: PerformanceStatProps) => (
  <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-lg shadow-slate-900/40">
    <p className="text-sm font-medium text-slate-400">{title}</p>
    <div className="mt-2 flex items-baseline gap-2">
      <h3 className="text-3xl font-bold text-white">{value}</h3>
      <span className="text-sm text-slate-500">{unit}</span>
    </div>
    <div className="mt-4 text-xs font-medium text-emerald-400">{trend} vs mês anterior</div>
  </div>
);

const TICKET_CARDS = [
  { label: "Tickets Abertos", value: 12, color: "border-amber-200 bg-amber-50 text-amber-950", accent: "text-amber-700", href: "/tickets" },
  { label: "Em Progresso", value: 5, color: "border-sky-200 bg-sky-50 text-sky-950", accent: "text-sky-700", href: "/tickets" },
  { label: "Resolvidos Hoje", value: 8, color: "border-emerald-200 bg-emerald-50 text-emerald-950", accent: "text-emerald-700", href: "/tickets" },
  { label: "Críticos", value: 2, color: "border-rose-200 bg-rose-50 text-rose-950", accent: "text-rose-700", href: "/tickets" },
];

const ONBOARDING_STEPS = [
  { href: "/risk-radar", icon: ShieldAlert, title: "Ative o Radar de Risco Clínico", description: "Cruze UDI, firmware, recall, cibersegurança e risco regulatório por equipamento." },
  { href: "/evidence-copilot", icon: BookOpenCheck, title: "Use RCA com evidência", description: "Gere causa provável com manuais, histórico, contenção e pacote para fornecedor." },
  { href: "/value-engine", icon: CircleDollarSign, title: "Mostre ROI e renovação", description: "Converta indisponibilidade evitada em valor financeiro e expansão contratual." },
  { href: "/machines", icon: Monitor, title: "Cadastre suas máquinas", description: "Adicione os equipamentos hospitalares que deseja monitorar." },
  { href: "/health-checks", icon: HeartPulse, title: "Configure verificações de saúde", description: "Defina verificações periódicas de disponibilidade para cada equipamento." },
  { href: "/alerts", icon: Bell, title: "Ative alertas", description: "Receba notificações em tempo real quando um equipamento apresentar falha." },
  { href: "/tickets", icon: Ticket, title: "Gerencie tickets", description: "Abra e acompanhe chamados de manutenção corretiva e preventiva." },
  { href: "/metrics", icon: BarChart2, title: "Acompanhe métricas", description: "Visualize indicadores de disponibilidade e desempenho do seu parque." },
  { href: "/settings", icon: Settings, title: "Personalize as configurações", description: "Ajuste idioma, fuso horário e preferências de notificação." },
];

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <section className="rounded-2xl bg-gradient-to-r from-slate-900 via-slate-800 to-cyan-900 p-6 text-white shadow-xl">
        <h1 className="text-3xl font-black tracking-tight">Dashboard Operacional</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-200">
          Acompanhe disponibilidade, risco e performance dos equipamentos em um painel unificado para resposta rápida.
        </p>
      </section>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {TICKET_CARDS.map((m) => (
          <Link
            key={m.label}
            href={m.href}
            className={`rounded-2xl border ${m.color} p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md`}
          >
            <div className={`text-4xl font-black ${m.accent}`}>{m.value}</div>
            <div className="mt-2 text-sm font-semibold">{m.label}</div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <PerformanceStat title="MTTR (Reparo)" value="3.2" unit="horas" trend="-12%" />
        <PerformanceStat title="MTBF (Estabilidade)" value="45" unit="dias" trend="+5%" />
        <PerformanceStat title="Disponibilidade" value="98.8" unit="%" trend="+0.2%" />
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-1 text-xl font-semibold text-gray-900">Primeiros Passos</h2>
        <p className="mb-5 text-sm text-gray-500">
          Configure o FPConnect em poucos minutos para começar a monitorar os equipamentos da sua operação.
        </p>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ONBOARDING_STEPS.map(({ href, icon: Icon, title, description }, index) => (
            <Link
              key={href}
              href={href}
              className="group flex items-start gap-3 rounded-xl border border-gray-100 p-4 transition hover:border-cyan-200 hover:bg-cyan-50"
            >
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-cyan-100 text-sm font-semibold text-cyan-700 transition group-hover:bg-cyan-600 group-hover:text-white">
                {index + 1}
              </div>
              <div className="min-w-0">
                <div className="mb-0.5 flex items-center gap-1.5">
                  <Icon size={14} className="flex-shrink-0 text-cyan-600" />
                  <p className="text-sm font-semibold text-gray-800">{title}</p>
                </div>
                <p className="text-xs leading-relaxed text-gray-500">{description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
