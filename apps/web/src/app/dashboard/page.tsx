import Link from "next/link";
import {
  Monitor,
  HeartPulse,
  Bell,
  Ticket,
  BarChart2,
  Settings,
} from "lucide-react";

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
    { label: "Tickets Abertos", value: 12, color: "bg-yellow-100 text-yellow-800" },
    { label: "Em Progresso", value: 5, color: "bg-blue-100 text-blue-800" },
    { label: "Resolvidos Hoje", value: 8, color: "bg-green-100 text-green-800" },
    { label: "Críticos", value: 2, color: "bg-red-100 text-red-800" },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {metrics.map((m) => (
          <div key={m.label} className={`rounded-xl p-6 ${m.color} shadow`}>
            <div className="text-4xl font-bold">{m.value}</div>
            <div className="text-sm font-medium mt-1">{m.label}</div>
          </div>
        ))}
      </div>

      {/* Getting started */}
      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-1">
          Primeiros Passos
        </h2>
        <p className="text-sm text-gray-500 mb-5">
          Bem-vindo ao FPConnect! Siga as etapas abaixo para começar a monitorar
          seus equipamentos.
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
          Atividade Recente
        </h2>
        <p className="text-gray-500">Nenhuma atividade recente para exibir.</p>
      </div>
    </div>
  );
}
