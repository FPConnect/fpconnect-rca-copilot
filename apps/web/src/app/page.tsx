"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Check,
  Clock3,
  Languages,
  Layers3,
  Server,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Target,
  X,
} from "lucide-react";

type Locale = "pt" | "en";
type PlanKey = "basic" | "premium" | "vip" | "consultoria";

const planOrder: PlanKey[] = ["basic", "premium", "vip", "consultoria"];

const copy = {
  pt: {
    badge: "Plataforma de monitoramento para operações hospitalares",
    title: ["Visibilidade total", "para"],
    titleAccent: ["Engenharia Clínica e", "TI Biomédica"],
    subtitle:
      "O FPConnect centraliza monitoramento, alertas, tickets e histórico operacional para sua equipe tomar decisões rápidas e reduzir indisponibilidade de equipamentos de missão crítica.",
    cta: "Acessar plataforma",
    secondaryCta: "Ver painel operacional",
    kpiTitle: "Indicadores operacionais",
    kpis: [
      { label: "Equipamentos monitoráveis", value: "1.200+", icon: Server },
      { label: "Redução média de MTTR", value: "-32%", icon: Clock3 },
      { label: "SLA de disponibilidade", value: "99,9%", icon: Stethoscope },
    ],
    highlights: [
      {
        icon: Activity,
        title: "Observabilidade em tempo real",
        description: "Monitore disponibilidade, alertas e comportamento de equipamentos críticos em um único painel.",
      },
      {
        icon: Target,
        title: "Resposta rápida a incidentes",
        description: "Abra e acompanhe tickets com contexto técnico para acelerar análise RCA e reduzir MTTR.",
      },
      {
        icon: ShieldCheck,
        title: "Confiabilidade operacional",
        description: "Padronize verificações e priorize riscos para manter continuidade clínica e segurança do paciente.",
      },
    ],
    experimentEyebrow: "Experimente o FPConnect",
    experimentTitle: "Conheça a plataforma com uma visão inicial da operação clínica.",
    experimentText:
      "Use o Basic para abrir a primeira conversa comercial com dados, fluxo de chamados e visão executiva do que pode evoluir para operação assistida.",
    plansMiniTitle: "Planos",
    plansMiniText: "Recursos para evoluir da visão inicial para operação assistida, gestão de SLA e implantação executiva.",
    institutional: [
      {
        title: "Missão",
        text: "Dar previsibilidade à engenharia clínica e à TI biomédica, conectando dados técnicos, risco e decisão operacional.",
      },
      {
        title: "Visão",
        text: "Ser a camada de inteligência operacional que hospitais usam para reduzir downtime e proteger equipamentos críticos.",
      },
      {
        title: "Valores",
        text: "Evidência antes de opinião, segurança do paciente, simplicidade para a equipe técnica e governança rastreável.",
      },
      {
        title: "Quem somos",
        text: "A FPConnect combina engenharia clínica, automação e software para transformar manutenção em gestão proativa.",
      },
      {
        title: "Ajuda / FAQs",
        text: "O piloto pode começar pequeno, com dados disponíveis, e evoluir para integrações, RCA Copilot, SLA e playbooks.",
      },
    ],
    pricingHeroTitle: "Planos para operar engenharia clínica com mais previsibilidade",
    pricingHeroSubtitle:
      "Comece no Basic demonstrativo, avance para operação real no Premium, use o VIP para SLA crítico e contrate Consultoria para implantação assistida.",
    seePlans: "Ver planos",
    sales: "Falar com vendas",
    chooseTitle: "Escolha como sua equipe vai operar",
    chooseText:
      "Premium e VIP são concluídos com a equipe comercial após apresentação e negociação. Consultoria é dimensionada caso a caso.",
    monthly: "Mensal",
    annual: "Anual",
    annualDiscount: "-17%",
    resourceScale: "Escala de recursos",
    planHint:
      "Comece com uma visão inicial e avance quando precisar de chamados, RCA Copilot, playbooks, SLA e acompanhamento consultivo.",
    customSales: "Atendimento comercial personalizado",
    plans: {
      basic: {
        name: "Basic",
        label: "Visão inicial",
        price: "Grátis",
        cta: "Experimentar grátis",
        description: "Visão inicial para conhecer o FPConnect com recursos limitados.",
        included: [
          "Visão inicial do painel operacional",
          "Acesso ao ambiente de demonstração",
          "Solicitação de proposta comercial",
        ],
        excluded: [
          "Gestão real de chamados e equipamentos",
          "Diagnóstico RCA Copilot",
          "Gestão de contratos e SLA",
          "Suporte prioritário",
        ],
      },
      premium: {
        name: "Premium",
        label: "Operação assistida",
        price: "Sob proposta",
        cta: "Solicitar proposta",
        description: "Operação real com chamados, ativos, alertas e relatórios para a engenharia clínica.",
        included: [
          "Tudo do Basic",
          "Gestão real de chamados e equipamentos",
          "Painel de disponibilidade e MTTR",
          "Alertas operacionais",
          "Relatórios gerenciais",
        ],
        excluded: ["SLA crítico avançado", "Implantação executiva completa"],
      },
      vip: {
        name: "VIP",
        label: "SLA crítico",
        price: "Sob contrato",
        cta: "Falar com vendas",
        description: "Camada para operação crítica com acompanhamento, SLA e priorização de riscos.",
        included: [
          "Tudo do Premium",
          "RCA Copilot",
          "Playbooks operacionais",
          "Gestão de contratos e SLA",
          "Suporte prioritário",
        ],
        excluded: ["Consultoria presencial sob diagnóstico"],
      },
      consultoria: {
        name: "Consultoria",
        label: "Implantação executiva",
        price: "Sob diagnóstico",
        cta: "Saiba mais pelo WhatsApp.",
        description: "Para hospitais e redes que precisam de implantação assistida e governança executiva.",
        included: [
          "Tudo do VIP",
          "Diagnóstico de maturidade da operação",
          "Implantação assistida com plano de adoção",
          "Treinamento para engenharia clínica e TI",
          "Rituais mensais de melhoria operacional",
          "Governança executiva com indicadores de risco",
        ],
        excluded: [],
      },
    },
  },
  en: {
    badge: "Monitoring platform for hospital operations",
    title: ["Total visibility for"],
    titleAccent: ["Clinical Engineering and", "Biomedical IT"],
    subtitle:
      "FPConnect centralizes monitoring, alerts, tickets and operational history so your team can make faster decisions and reduce downtime for mission-critical equipment.",
    cta: "Access platform",
    secondaryCta: "View operations dashboard",
    kpiTitle: "Operational indicators",
    kpis: [
      { label: "Monitorable assets", value: "1,200+", icon: Server },
      { label: "Average MTTR reduction", value: "-32%", icon: Clock3 },
      { label: "Availability SLA", value: "99.9%", icon: Stethoscope },
    ],
    highlights: [
      {
        icon: Activity,
        title: "Real-time observability",
        description: "Monitor availability, alerts and critical equipment behavior from one operational panel.",
      },
      {
        icon: Target,
        title: "Fast incident response",
        description: "Open and track tickets with technical context to accelerate RCA and reduce MTTR.",
      },
      {
        icon: ShieldCheck,
        title: "Operational reliability",
        description: "Standardize checks and prioritize risk to protect clinical continuity and patient safety.",
      },
    ],
    experimentEyebrow: "Try FPConnect",
    experimentTitle: "Explore the platform with an initial view of clinical operations.",
    experimentText:
      "Use Basic to start the commercial conversation with data, ticket flow and an executive view of what can evolve into assisted operations.",
    plansMiniTitle: "Plans",
    plansMiniText: "Resources to evolve from initial visibility to assisted operations, SLA management and executive rollout.",
    institutional: [
      {
        title: "Mission",
        text: "Bring predictability to clinical engineering and biomedical IT by connecting technical data, risk and operational decisions.",
      },
      {
        title: "Vision",
        text: "Become the operational intelligence layer hospitals use to reduce downtime and protect critical equipment.",
      },
      {
        title: "Values",
        text: "Evidence before opinion, patient safety, simplicity for technical teams and traceable governance.",
      },
      {
        title: "About us",
        text: "FPConnect combines clinical engineering, automation and software to turn maintenance into proactive management.",
      },
      {
        title: "Help / FAQs",
        text: "The pilot can start small, using available data, and evolve to integrations, RCA Copilot, SLA and playbooks.",
      },
    ],
    pricingHeroTitle: "Plans to run clinical engineering with more predictability",
    pricingHeroSubtitle:
      "Start with the Basic demo, move to real operations with Premium, use VIP for critical SLA and hire Consulting for assisted rollout.",
    seePlans: "View plans",
    sales: "Talk to sales",
    chooseTitle: "Choose how your team will operate",
    chooseText:
      "Premium and VIP are closed with the commercial team after presentation and negotiation. Consulting is scoped case by case.",
    monthly: "Monthly",
    annual: "Annual",
    annualDiscount: "-17%",
    resourceScale: "Resource scale",
    planHint:
      "Start with initial visibility and advance when you need tickets, RCA Copilot, playbooks, SLA and consultative follow-up.",
    customSales: "Personalized commercial support",
    plans: {
      basic: {
        name: "Basic",
        label: "Initial visibility",
        price: "Free",
        cta: "Try free",
        description: "Initial view to understand FPConnect with limited resources.",
        included: [
          "Initial operational dashboard",
          "Demo environment access",
          "Commercial proposal request",
        ],
        excluded: [
          "Real ticket and asset management",
          "RCA Copilot diagnosis",
          "Contract and SLA management",
          "Priority support",
        ],
      },
      premium: {
        name: "Premium",
        label: "Assisted operations",
        price: "By proposal",
        cta: "Request proposal",
        description: "Real operations with tickets, assets, alerts and reports for clinical engineering.",
        included: [
          "Everything in Basic",
          "Real ticket and asset management",
          "Availability and MTTR dashboard",
          "Operational alerts",
          "Management reports",
        ],
        excluded: ["Advanced critical SLA", "Full executive rollout"],
      },
      vip: {
        name: "VIP",
        label: "Critical SLA",
        price: "By contract",
        cta: "Talk to sales",
        description: "Layer for critical operations with follow-up, SLA and risk prioritization.",
        included: [
          "Everything in Premium",
          "RCA Copilot",
          "Operational playbooks",
          "Contract and SLA management",
          "Priority support",
        ],
        excluded: ["On-site consulting scoped by diagnosis"],
      },
      consultoria: {
        name: "Consulting",
        label: "Executive rollout",
        price: "By diagnosis",
        cta: "Learn more via WhatsApp.",
        description: "For hospitals and networks that need assisted rollout and executive governance.",
        included: [
          "Everything in VIP",
          "Operational maturity diagnosis",
          "Assisted rollout with adoption plan",
          "Training for clinical engineering and IT",
          "Monthly operational improvement rituals",
          "Executive governance with risk indicators",
        ],
        excluded: [],
      },
    },
  },
} as const;

function nextPlan(plan: PlanKey, direction: 1 | -1) {
  const index = planOrder.indexOf(plan);
  const nextIndex = (index + direction + planOrder.length) % planOrder.length;
  return planOrder[nextIndex];
}

export default function LandingPage() {
  const [locale, setLocale] = useState<Locale>("pt");
  const [activePlan, setActivePlan] = useState<PlanKey>("basic");
  const t = copy[locale];
  const active = t.plans[activePlan];

  const activePlanIndex = useMemo(() => planOrder.indexOf(activePlan), [activePlan]);

  return (
    <main className="min-h-screen bg-[#020817] text-white" data-no-translate>
      <section className="relative overflow-hidden bg-[linear-gradient(120deg,#06101f_0%,#0b2944_48%,#020817_100%)]">
        <div className="absolute right-6 top-6 z-10 inline-flex items-center gap-2 rounded-full border border-slate-600 bg-slate-900/70 p-1 text-sm font-bold text-slate-200">
          <Languages size={16} className="ml-2 text-cyan-200" />
          <button
            type="button"
            onClick={() => setLocale("pt")}
            className={`rounded-full px-4 py-2 ${locale === "pt" ? "bg-cyan-400 text-slate-950" : "text-slate-100"}`}
          >
            Português
          </button>
          <button
            type="button"
            onClick={() => setLocale("en")}
            className={`rounded-full px-4 py-2 ${locale === "en" ? "bg-cyan-400 text-slate-950" : "text-slate-100"}`}
          >
            English
          </button>
        </div>

        <div className="mx-auto w-full max-w-[1440px] px-6 pb-16 pt-20 sm:px-8 lg:px-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/40 bg-cyan-300/10 px-4 py-2 text-sm font-bold text-cyan-100">
            <ShieldCheck size={15} />
            {t.badge}
          </div>

          <div className="mt-10 grid items-center gap-10 lg:grid-cols-[minmax(0,600px)_minmax(380px,420px)] lg:justify-between">
            <div>
              <h1 className="max-w-4xl text-5xl font-black leading-[1.06] sm:text-6xl lg:text-[3.5rem]">
                {t.title.map((line) => (
                  <span key={line} className="block">
                    {line}
                  </span>
                ))}
                {t.titleAccent.map((line) => (
                  <span key={line} className="block bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent lg:whitespace-nowrap">
                    {line}
                  </span>
                ))}
              </h1>
              <p className="mt-7 max-w-[760px] text-xl leading-8 text-slate-100">
                {t.subtitle}
              </p>

              <div className="mt-9 flex flex-wrap gap-4">
                <Link
                  href="/dashboard"
                  className="inline-flex min-h-12 items-center justify-center gap-3 rounded-lg bg-cyan-400 px-6 text-base font-black text-slate-950 shadow-lg shadow-cyan-950/30 transition hover:bg-cyan-300"
                >
                  {t.cta}
                  <ArrowRight size={19} />
                </Link>
                <Link
                  href="/dashboard"
                  className="inline-flex min-h-12 items-center justify-center rounded-lg border border-slate-500 px-6 text-base font-bold text-white transition hover:border-cyan-300 hover:text-cyan-100"
                >
                  {t.secondaryCta}
                </Link>
              </div>
            </div>

            <aside className="rounded-lg border border-slate-600 bg-slate-900/70 p-6 shadow-2xl shadow-black/20">
              <p className="text-sm font-semibold uppercase text-slate-400">{t.kpiTitle}</p>
              <div className="mt-5 space-y-4">
                {t.kpis.map(({ label, value, icon: Icon }) => (
                  <div key={label} className="flex min-h-16 items-center justify-between rounded-lg border border-slate-600 bg-slate-900 px-5">
                    <div className="flex items-center gap-4">
                      <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-300">
                        <Icon size={20} />
                      </span>
                      <span className="text-base text-slate-300">{label}</span>
                    </div>
                    <strong className="text-2xl text-white">{value}</strong>
                  </div>
                ))}
              </div>
            </aside>
          </div>

          <div className="mt-16 grid gap-5 md:grid-cols-3">
            {t.highlights.map(({ icon: Icon, title, description }) => (
              <article key={title} className="rounded-lg border border-slate-600 bg-slate-900/60 p-7 shadow-lg shadow-black/20">
                <div className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-300">
                  <Icon size={22} />
                </div>
                <h2 className="text-xl font-black text-white">{title}</h2>
                <p className="mt-4 text-base leading-7 text-slate-100">{description}</p>
              </article>
            ))}
          </div>

          <div className="mt-16 grid gap-8 lg:grid-cols-[0.9fr_1fr]">
            <article className="rounded-lg border border-cyan-400/40 bg-cyan-950/35 p-8">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-cyan-400/15 text-cyan-200">
                <Sparkles size={24} />
              </div>
              <p className="mt-6 text-sm font-black uppercase text-cyan-200">{t.experimentEyebrow}</p>
              <h2 className="mt-8 max-w-xl text-4xl font-black leading-tight text-white">
                {t.experimentTitle}
              </h2>
              <p className="mt-5 text-base leading-7 text-slate-200">{t.experimentText}</p>
            </article>
            <a
              href="#plans"
              className="flex min-h-36 items-center gap-7 rounded-lg border border-slate-700 bg-slate-900/60 p-8 transition hover:border-cyan-400/70"
            >
              <span className="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-300">
                <Layers3 size={27} />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-4xl font-black text-white">{t.plansMiniTitle}</span>
                <span className="mt-3 block text-lg leading-7 text-slate-300">{t.plansMiniText}</span>
              </span>
              <ChevronDown size={24} className="text-slate-300" />
            </a>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-800 bg-[#020817]">
        <div className="mx-auto grid w-full max-w-[1440px] gap-4 px-6 py-8 sm:px-8 lg:grid-cols-5 lg:px-8">
          {t.institutional.map((item) => (
            <article key={item.title} className="rounded-lg border border-slate-700 bg-slate-900/55 p-5">
              <h2 className="text-lg font-black text-white">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="plans" className="bg-[#020817]">
        <header className="border-b border-slate-800">
          <div className="mx-auto flex h-20 w-full max-w-[1440px] items-center justify-between px-6 sm:px-8 lg:px-8">
            <div className="flex items-center gap-3 text-2xl font-black text-white">
              <ShieldCheck size={28} className="text-cyan-300" />
              FPConnect
            </div>
            <Link
              href="/dashboard"
              className="inline-flex min-h-11 items-center justify-center gap-3 rounded-lg bg-cyan-400 px-5 text-sm font-black text-slate-950 transition hover:bg-cyan-300"
            >
              {t.cta}
              <ArrowRight size={18} />
            </Link>
          </div>
        </header>

        <div className="mx-auto w-full max-w-[1440px] px-6 py-20 sm:px-8 lg:px-8">
          <div className="max-w-5xl">
            <h2 className="text-5xl font-black leading-tight text-white lg:text-6xl">
              {t.pricingHeroTitle}
            </h2>
            <p className="mt-7 max-w-4xl text-xl leading-8 text-slate-100">
              {t.pricingHeroSubtitle}
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <a
                href="#plan-detail"
                className="inline-flex min-h-12 items-center justify-center rounded-lg bg-cyan-400 px-7 text-base font-black text-slate-950 transition hover:bg-cyan-300"
              >
                {t.seePlans}
              </a>
              <a
                href="mailto:contato@fpconnect.com.br"
                className="inline-flex min-h-12 items-center justify-center rounded-lg border border-slate-600 px-7 text-base font-bold text-white transition hover:border-cyan-300"
              >
                {t.sales}
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800">
          <div className="mx-auto w-full max-w-[1360px] px-6 py-20 sm:px-8 lg:px-8">
            <section className="overflow-hidden rounded-lg border border-slate-700 bg-slate-900/40">
              <div className="flex items-start justify-between gap-5 border-b border-slate-700 px-8 py-7">
                <div className="flex items-start gap-5">
                  <span className="inline-flex h-14 w-14 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-300">
                    <Layers3 size={27} />
                  </span>
                  <div>
                    <h3 className="text-4xl font-black text-white">{t.plansMiniTitle}</h3>
                    <p className="mt-2 max-w-3xl text-lg leading-7 text-slate-300">{t.plansMiniText}</p>
                  </div>
                </div>
                <ChevronUp className="mt-3 shrink-0 text-slate-300" size={24} />
              </div>

              <div className="px-8 py-10">
                <div className="grid gap-8 lg:grid-cols-[1fr_300px] lg:items-start">
                  <div>
                    <h4 className="text-2xl font-black text-white">{t.chooseTitle}</h4>
                    <p className="mt-3 max-w-3xl text-base leading-7 text-slate-300">{t.chooseText}</p>
                  </div>
                  <div className="flex items-center justify-start gap-6 lg:justify-end">
                    <button className="rounded-lg bg-cyan-400 px-7 py-4 text-lg font-black text-white shadow-xl shadow-cyan-950/50">
                      {t.monthly}
                    </button>
                    <div className="h-8 w-px bg-slate-700" />
                    <button className="text-lg font-bold text-slate-300">
                      {t.annual} <span className="ml-1 text-sm">{t.annualDiscount}</span>
                    </button>
                  </div>
                </div>

                <div className="mt-9 rounded-lg border border-slate-700 p-6">
                  <p className="mb-5 text-sm font-black uppercase text-cyan-200">{t.resourceScale}</p>
                  <div className="grid gap-3 md:grid-cols-2">
                    {planOrder.map((planKey) => {
                      const plan = t.plans[planKey];
                      const isActive = activePlan === planKey;
                      return (
                        <button
                          key={plan.name}
                          type="button"
                          onClick={() => setActivePlan(planKey)}
                          className={`rounded-lg border p-5 text-left transition ${
                            isActive
                              ? "border-cyan-300 bg-cyan-950/55"
                              : "border-slate-700 bg-slate-900/60 hover:border-cyan-400/70"
                          }`}
                        >
                          <span className="block text-base font-black text-white">{plan.name}</span>
                          <span className="mt-2 block text-sm text-slate-300">{plan.label}</span>
                        </button>
                      );
                    })}
                  </div>
                  <p className="mt-6 text-base leading-7 text-slate-300">{t.planHint}</p>
                </div>

                <div id="plan-detail" className="mt-8">
                  <div className="grid grid-cols-[44px_1fr_44px] items-start gap-4">
                    <button
                      type="button"
                      onClick={() => setActivePlan(nextPlan(activePlan, -1))}
                      className="mt-10 inline-flex h-11 w-11 items-center justify-center rounded-lg border border-slate-600 text-white transition hover:border-cyan-300"
                      aria-label="Plano anterior"
                    >
                      <ArrowLeft size={19} />
                    </button>

                    <div>
                      <p className="mb-7 text-center text-base text-slate-300">{t.customSales}</p>
                      <article className="mx-auto max-w-2xl rounded-lg border border-slate-700 bg-slate-900/60 p-9">
                        <h4 className="text-3xl font-black text-white">{active.name}</h4>
                        <p className="mt-4 text-base leading-7 text-slate-300">{active.description}</p>
                        <div className="mt-8 text-5xl font-black text-white">{active.price}</div>
                        <Link
                          href={activePlan === "consultoria" ? "https://wa.me/5547996789861" : "/dashboard"}
                          className="mt-8 inline-flex min-h-12 w-full items-center justify-center rounded-lg border border-cyan-300 text-base font-black text-cyan-200 transition hover:bg-cyan-400 hover:text-slate-950"
                        >
                          {active.cta}
                        </Link>

                        <div className="mt-9 space-y-5">
                          {active.included.map((item) => (
                            <div key={item} className="flex items-start gap-4 text-base text-white">
                              <Check size={20} className="mt-0.5 shrink-0 text-emerald-300" />
                              <span>{item}</span>
                            </div>
                          ))}
                          {active.excluded.map((item) => (
                            <div key={item} className="flex items-start gap-4 text-base text-slate-500">
                              <X size={20} className="mt-0.5 shrink-0 text-slate-700" />
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                      </article>

                      <div className="mt-6 flex items-center justify-center gap-2">
                        {planOrder.map((planKey, index) => (
                          <button
                            key={planKey}
                            type="button"
                            onClick={() => setActivePlan(planKey)}
                            className={`h-3 rounded-full transition ${
                              activePlanIndex === index ? "w-8 bg-cyan-300" : "w-3 bg-slate-700"
                            }`}
                            aria-label={`Selecionar ${t.plans[planKey].name}`}
                          />
                        ))}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => setActivePlan(nextPlan(activePlan, 1))}
                      className="mt-10 inline-flex h-11 w-11 items-center justify-center rounded-lg border border-slate-600 text-white transition hover:border-cyan-300"
                      aria-label="Próximo plano"
                    >
                      <ArrowRight size={19} />
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
