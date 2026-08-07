import Link from "next/link";
import {
  Monitor,
  HeartPulse,
  Bell,
  Ticket,
  BarChart2,
  Settings,
  Sparkles,
  ShieldAlert,
  Activity,
  Brain,
  ArrowRight,
} from "lucide-react";
import FPConnectLogo from "@/components/FPConnectLogo";

const ONBOARDING_STEPS = [
  {
    href: "/machines",
    icon: Monitor,
    title: "Cadastre suas máquinas",
    description: "Adicione os equipamentos hospitalares que deseja monitorar.",
  },
  {
    href: "/health-checks",
    icon: HeartPulse,
    title: "Configure verificações de saúde",
    description: "Defina verificações periódicas de disponibilidade para cada equipamento.",
  },
  {
    href: "/alerts",
    icon: Bell,
    title: "Ative alertas",
    description: "Receba notificações em tempo real quando um equipamento apresentar falha.",
  },
  {
    href: "/tickets",
    icon: Ticket,
    title: "Gerencie tickets",
    description: "Abra e acompanhe chamados de manutenção corretiva e preventiva.",
  },
  {
    href: "/metrics",
    icon: BarChart2,
    title: "Acompanhe métricas",
    description: "Visualize indicadores de disponibilidade e desempenho do seu parque.",
  },
  {
    href: "/settings",
    icon: Settings,
    title: "Personalize as configurações",
    description: "Ajuste idioma, fuso horário e preferências de notificação.",
  },
];

export default function DashboardPage() {
  const metrics = [
    { label: "Tickets Abertos", value: 12, color: "bg-yellow-100 text-yellow-800", href: "/tickets?status=open" },
    { label: "Em Progresso", value: 5, color: "bg-blue-100 text-blue-800", href: "/tickets?status=in_progress" },
    { label: "Resolvidos Hoje", value: 8, color: "bg-green-100 text-green-800", href: "/tickets?status=resolved" },
    { label: "Críticos", value: 2, color: "bg-red-100 text-red-800", href: "/tickets?priority=critical" },
  ];

  const scenarios = [
    {
      href: "/demo-institucional",
      icon: Sparkles,
      title: "Demo institucional autoplay",
      description: "Execute uma apresentação com cursor guiado, narração e explicação passo a passo pronta para clientes.",
    },
    {
      href: "/simulacoes",
      icon: Sparkles,
      title: "Roteiro guiado de venda",
      description: "Abra uma trilha pronta para demonstrar operação, risco, ROI e ação assistida por copiloto.",
    },
    {
      href: "/tickets",
      icon: ShieldAlert,
      title: "Simular incidente crítico",
      description: "Mostre priorização de tickets, escalonamento e orientação técnica em linguagem natural.",
    },
    {
      href: "/intel",
      icon: Activity,
      title: "Simular radar operacional",
      description: "Apresente recalls, tendências e sinais externos que ajudam a antecipar indisponibilidade.",
    },
    {
      href: "/agent",
      icon: Brain,
      title: "Abrir centro de simulação",
      description: "Mostre todas as ferramentas do produto, relatórios e métricas de pós-venda em um único fluxo.",
    },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-950 via-blue-950 to-cyan-900 p-8 text-white mb-8">
        <div className="absolute -right-12 -top-16 h-40 w-40 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute right-8 bottom-0 h-24 w-24 rounded-full bg-blue-300/10 blur-2xl" />
        <div className="relative">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-cyan-100">
                FPConnect Demo Online
              </div>
            </div>
            <div className="md:shrink-0">
              <FPConnectLogo
                subtitle="Disponibilidade e RCA"
                theme="dark"
                size="lg"
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur-sm"
              />
            </div>
          </div>
          <h1 className="mt-4 text-3xl md:text-4xl font-bold max-w-3xl leading-tight">
            Demonstre redução de indisponibilidade, resposta mais rápida e priorização inteligente sem preparar backend para cada reunião.
          </h1>
          <p className="mt-4 max-w-2xl text-sm md:text-base text-slate-200 leading-relaxed">
            Esta versão está pronta para simulação comercial: tickets, radar, métricas e copiloto operam em modo demo estável no navegador para acelerar apresentações e testes de narrativa de venda.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/simulacoes" className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 hover:bg-slate-100">
              Abrir roteiro de simulação
              <ArrowRight size={16} />
            </Link>
            <Link href="/agent" className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/15">
              Abrir centro de simulação
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {metrics.map((m) => (
          <Link key={m.label} href={m.href} className={`rounded-xl p-6 ${m.color} shadow cursor-pointer transition hover:scale-105 focus:scale-105 outline-none`} tabIndex={0}>
            <div className="text-4xl font-bold">{m.value}</div>
            <div className="text-sm font-medium mt-1">{m.label}</div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {scenarios.map(({ href, icon: Icon, title, description }) => (
          <Link
            key={href}
            href={href}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md hover:border-blue-200 transition"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                <Icon size={20} />
              </div>
              <div>
                <h2 className="text-base font-semibold text-slate-900">{title}</h2>
                <p className="mt-1 text-sm leading-relaxed text-slate-600">{description}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Getting started */}
      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-1">
          Trilha de Demonstração
        </h2>
        <p className="text-sm text-gray-500 mb-5">
          Use esta sequência para conduzir a conversa comercial do diagnóstico até a proposta de valor.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ONBOARDING_STEPS.map(({ href, icon: Icon, title, description }, index) => (
            <Link
              key={href}
              href={href}
              className="flex items-start gap-3 p-4 rounded-lg border border-gray-100 hover:border-blue-200 hover:bg-blue-50 transition-colors group"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold text-sm group-hover:bg-blue-600 group-hover:text-white transition-colors">
                {index + 1}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 mb-0.5">
                  <Icon size={14} className="text-blue-500 flex-shrink-0" />
                  <p className="text-sm font-semibold text-gray-800">{title}</p>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Argumentos rápidos para venda
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-600">
          <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
            <div className="font-semibold text-slate-900 mb-1">Menos indisponibilidade</div>
            <p>Mostre monitoramento, priorização e resposta mais rápida em ativos críticos sem depender de planilhas manuais.</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
            <div className="font-semibold text-slate-900 mb-1">Mais previsibilidade</div>
            <p>Use métricas, histórico e radar externo para defender manutenção baseada em risco e impacto clínico.</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-4 border border-slate-100">
            <div className="font-semibold text-slate-900 mb-1">Mais velocidade comercial</div>
            <p>Conduza simulações no navegador, personalize a conversa e valide narrativa antes de integrar ambiente real do cliente.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
