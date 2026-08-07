import Link from "next/link";
import {
  ShieldCheck,
  Activity,
  Siren,
  ArrowRight,
  Server,
  Clock3,
  Stethoscope,
  Sparkles,
  ChevronRight,
  Quote,
  Target,
  Eye,
  HeartHandshake,
  Building2,
  HelpCircle,
  CheckCircle2,
} from "lucide-react";
import LandingLanguageSwitcher from "@/components/LandingLanguageSwitcher";
import LandingFaqSearch from "@/components/LandingFaqSearch";

const NAV_LINKS = [
  { href: "#missao", label: "Missão" },
  { href: "#visao", label: "Visão" },
  { href: "#valores", label: "Valores" },
  { href: "#quem-somos", label: "Quem somos" },
  { href: "#faq", label: "Ajuda / FAQs" },
];

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

const INSTITUTIONAL = [
  {
    id: "missao",
    icon: Target,
    title: "Missão",
    description:
      "Conectar engenharia clínica, TI biomédica e operação hospitalar em uma plataforma única para reduzir indisponibilidade, acelerar resposta a incidentes e proteger a segurança do paciente.",
  },
  {
    id: "visao",
    icon: Eye,
    title: "Visão",
    description:
      "Ser a plataforma de referência para operações hospitalares orientadas por dados, tornando cada decisão de disponibilidade, manutenção e risco mais rápida, rastreável e confiável.",
  },
];

const VALUES = [
  {
    title: "Segurança do paciente",
    description: "Toda priorização parte do impacto clínico e da continuidade assistencial.",
  },
  {
    title: "Confiabilidade operacional",
    description: "Alertas, tickets e métricas precisam sustentar decisões consistentes no dia a dia.",
  },
  {
    title: "Clareza para decisão",
    description: "Dados técnicos devem virar contexto simples para gestores, equipes e fornecedores.",
  },
  {
    title: "Rastreabilidade",
    description: "Cada ocorrência deve manter histórico, responsável, evidência e evolução visíveis.",
  },
];

const PAID_PLANS = [
  {
    name: "Premium",
    price: "R$ 1.500/mês",
    summary: "Operação clínica completa com diagnóstico inteligente e colaboração de equipe.",
    features: ["RCA avançado", "Playbooks operacionais", "Relatórios executivos", "Suporte prioritário"],
  },
  {
    name: "VIP",
    price: "R$ 4.900/mês",
    summary: "Para operações críticas com alta disponibilidade e governança multiunidade.",
    features: ["Tudo do Premium", "Contratos/SLA avançados", "Prioridade máxima de processamento", "Acompanhamento estratégico"],
  },
  {
    name: "Consultoria",
    price: "R$ 15.000/mês",
    summary: "Plano consultivo para transformação operacional com apoio especialista dedicado.",
    features: ["Tudo do VIP", "Squad consultivo", "Roadmap de eficiência", "Implantação assistida"],
  },
];

const TESTIMONIALS = [
  {
    quote:
      "Com o FPConnect, reduzimos o tempo entre o alerta e a tomada de decisão. O time de engenharia clínica ganhou previsibilidade.",
    author: "Mariana F.",
    role: "Coordenadora de Engenharia Clínica",
  },
  {
    quote:
      "A visão de incidentes e causa raiz trouxe clareza para priorização. Hoje atuamos de forma muito mais proativa.",
    author: "Rafael S.",
    role: "Gestor de Operações Hospitalares",
  },
];

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.25),_transparent_45%),radial-gradient(circle_at_80%_20%,_rgba(59,130,246,0.2),_transparent_35%)]" />
      <div className="relative mx-auto max-w-6xl px-6 pb-16 pt-12 md:pt-20">
        <div className="mb-10 flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <Link href="/" className="inline-flex flex-col leading-none">
              <span className="text-lg font-black text-white">FPConnect</span>
              <span className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-200">
                Technologies
              </span>
            </Link>
            <LandingLanguageSwitcher />
          </div>
          <nav
            aria-label="Navegação institucional"
            className="flex flex-wrap gap-2 text-xs font-bold text-slate-300"
          >
            {NAV_LINKS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-full border border-slate-700 bg-slate-900/60 px-3 py-2 transition hover:border-cyan-300 hover:text-cyan-100"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

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
              O FPConnect centraliza monitoramento, alertas, tickets e histórico operacional para sua equipe tomar decisões rápidas e reduzir indisponibilidade de equipamentos de missão crítica.
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
                Ver painel operacional
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

        <section className="mt-16 grid gap-4 lg:grid-cols-2">
          {INSTITUTIONAL.map(({ id, icon: Icon, title, description }) => (
            <article
              key={title}
              id={id}
              className="scroll-mt-8 rounded-2xl border border-slate-700 bg-slate-900/70 p-6 shadow-lg shadow-slate-900/50"
            >
              <div className="mb-4 inline-flex rounded-xl bg-cyan-500/15 p-3 text-cyan-300">
                <Icon size={22} />
              </div>
              <h2 className="text-2xl font-black text-white">{title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-slate-300 sm:text-base">{description}</p>
            </article>
          ))}
        </section>

        <section id="valores" className="mt-12 scroll-mt-8">
          <div className="mb-5 flex items-center gap-3">
            <span className="inline-flex rounded-xl bg-emerald-500/15 p-3 text-emerald-300">
              <HeartHandshake size={22} />
            </span>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-200">
                Cultura operacional
              </p>
              <h2 className="text-2xl font-black text-white">Valores</h2>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {VALUES.map((value) => (
              <article key={value.title} className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
                <CheckCircle2 size={18} className="text-emerald-300" />
                <h3 className="mt-3 text-base font-black text-white">{value.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-300">{value.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section
          id="quem-somos"
          className="mt-12 scroll-mt-8 rounded-2xl border border-slate-700 bg-slate-900/70 p-6 shadow-xl shadow-slate-900/40"
        >
          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
            <div>
              <div className="mb-4 inline-flex rounded-xl bg-blue-500/15 p-3 text-blue-300">
                <Building2 size={22} />
              </div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-200">Institucional</p>
              <h2 className="mt-2 text-2xl font-black text-white">Quem somos</h2>
            </div>
            <div className="space-y-3 text-sm leading-relaxed text-slate-300 sm:text-base">
              <p>
                Somos a FPConnect Technologies, uma empresa focada em tecnologia para engenharia clínica, TI biomédica e operações hospitalares.
              </p>
              <p>
                Criamos uma plataforma para centralizar monitoramento, chamados, histórico e métricas de disponibilidade em ambientes de missão crítica.
              </p>
              <p>
                Nosso compromisso é entregar uma operação mais previsível, rastreável e preparada para tomada de decisão.
              </p>
            </div>
          </div>
        </section>

        <section className="mt-14 rounded-2xl border border-emerald-400/30 bg-emerald-500/10 p-6 shadow-lg shadow-emerald-950/30">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div className="max-w-2xl">
              <p className="inline-flex items-center gap-2 rounded-full border border-emerald-300/40 bg-emerald-400/15 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-emerald-200">
                <Sparkles size={14} /> Degustação gratuita
              </p>
              <h2 className="mt-3 text-2xl font-black text-white sm:text-3xl">Plano Basic para experimentar sem custo</h2>
              <p className="mt-2 text-sm leading-relaxed text-emerald-100/90 sm:text-base">
                Acesse o modo gratuito com limite máximo para conhecer a experiência do FPConnect sem compromisso. Ideal para validação inicial com sua equipe.
              </p>
            </div>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-emerald-300"
            >
              Testar plano Basic <ChevronRight size={16} />
            </Link>
          </div>
        </section>

        <section className="mt-12">
          <details className="group rounded-2xl border border-slate-700 bg-slate-900/70 p-6 shadow-xl shadow-slate-900/40">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-200">Menu</p>
                <h2 className="mt-1 text-2xl font-black text-white">Planos</h2>
                <p className="mt-1 text-sm text-slate-300">Abra para visualizar os planos pagos em formato de carrossel.</p>
              </div>
              <span className="rounded-full border border-slate-600 px-3 py-1 text-xs font-semibold text-slate-200 group-open:bg-cyan-500/20 group-open:text-cyan-100">
                Abrir / Fechar
              </span>
            </summary>

            <div className="mt-6 overflow-x-auto pb-2">
              <div className="flex snap-x snap-mandatory gap-4">
                {PAID_PLANS.map((plan) => (
                  <article
                    key={plan.name}
                    className="min-w-[260px] max-w-[320px] shrink-0 snap-start rounded-2xl border border-slate-700 bg-slate-950/70 p-5"
                  >
                    <h3 className="text-xl font-black text-white">{plan.name}</h3>
                    <p className="mt-2 text-2xl font-black text-cyan-200">{plan.price}</p>
                    <p className="mt-2 text-sm text-slate-300">{plan.summary}</p>
                    <ul className="mt-4 space-y-2 text-sm text-slate-200">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-start gap-2">
                          <span className="mt-1 h-1.5 w-1.5 rounded-full bg-cyan-300" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Link
                      href="/login"
                      className="mt-5 inline-flex items-center gap-2 rounded-lg border border-cyan-400/50 px-4 py-2 text-sm font-bold text-cyan-200 hover:bg-cyan-500/10"
                    >
                      Quero este plano <ArrowRight size={14} />
                    </Link>
                  </article>
                ))}
              </div>
            </div>
          </details>
        </section>

        <section className="mt-12 grid gap-4 md:grid-cols-2">
          {TESTIMONIALS.map((item) => (
            <article key={item.author} className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
              <Quote size={18} className="text-cyan-300" />
              <p className="mt-3 text-sm leading-relaxed text-slate-200">“{item.quote}”</p>
              <p className="mt-4 text-sm font-bold text-white">{item.author}</p>
              <p className="text-xs text-slate-400">{item.role}</p>
            </article>
          ))}
        </section>

        <section
          id="faq"
          className="mt-12 scroll-mt-8 rounded-2xl border border-slate-700 bg-slate-900/70 p-6 shadow-xl shadow-slate-900/40"
        >
          <div className="mb-5 flex items-center gap-3">
            <span className="inline-flex rounded-xl bg-amber-500/15 p-3 text-amber-300">
              <HelpCircle size={22} />
            </span>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-200">Suporte</p>
              <h2 className="text-2xl font-black text-white">Ajuda / FAQs</h2>
            </div>
          </div>
          <LandingFaqSearch />
        </section>

        <footer className="mt-14 border-t border-slate-800 pt-6 text-center text-sm text-slate-400">
          FPConnect™ - Marca registrada. © 2026 Todos os direitos reservados.
        </footer>
      </div>
    </div>
  );
}
