"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { APP_NAME } from "@/lib/brand";
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
    badge: "Inteligência de dados para assistência técnica MedTech",
    title: ["Transforme dados", "em"],
    titleAccent: ["decisões de", "assistência técnica"],
    subtitle:
      `${APP_NAME} organiza chamados, logs e histórico de equipamentos para apoiar triagem, revisão de hipóteses de causa raiz e acompanhamento de disponibilidade. A análise é assistiva: a validação e a decisão técnica continuam com a equipe responsável.`,
    cta: "Conversar sobre um piloto",
    secondaryCta: "Acessar plataforma",
    kpiTitle: "Referência do piloto de indicadores",
    kpis: [
      { label: "Ordens de serviço", value: "Até 300", icon: Server },
      { label: "Fonte / equipe / linha", value: "1", icon: Clock3 },
      { label: "Prazo-alvo", value: "10 dias úteis", icon: Stethoscope },
    ],
    highlights: [
      {
        icon: Activity,
        title: "Visibilidade dos dados disponíveis",
        description: "Reúna tickets, histórico e indicadores; atualização e integrações são definidas no piloto.",
      },
      {
        icon: Target,
        title: "Contexto para incidentes",
        description: "Organize contexto técnico e hipóteses de causa raiz para revisão da equipe responsável.",
      },
      {
        icon: ShieldCheck,
        title: "Revisão técnica",
        description: "Organize playbooks e prioridades para revisão da equipe responsável. A plataforma não executa manutenção.",
      },
    ],
    evidenceTitle: "Demonstração, piloto e resultado medido",
    evidenceText: "A demonstração apresenta funcionalidades com dados ilustrativos. O piloto valida o uso com uma amostra autorizada da sua operação. Um resultado só será apresentado como caso medido com período, amostra, cálculo e autorização documentados. Não prometemos redução percentual de MTTR nem disponibilidade garantida.",
    privacyText: "Compartilhe apenas dados autorizados, sem identificação de pacientes, credenciais ou informações confidenciais de terceiros. Canal, acesso e retenção são combinados antes do envio.",
    experimentEyebrow: `Experimente ${APP_NAME}`,
    experimentTitle: "Defina escopo e critérios antes de contratar.",
    experimentText:
      "O piloto de indicadores contempla até 300 ordens de serviço e uma fonte, equipe ou linha. Amostra, acesso, entregáveis, disponibilidade e critérios são confirmados antes da contratação; o prazo-alvo é de 10 dias úteis.",
    plansMiniTitle: "Escopos de trabalho",
    plansMiniText: "Opções de diagnóstico e piloto com escopo, fonte de dados e prazo-alvo explícitos.",
    institutional: [
      {
        title: "Missão",
        text: "Dar previsibilidade à engenharia clínica e à TI biomédica, conectando dados técnicos, risco e decisão operacional.",
      },
      {
        title: "Visão",
        text: "Objetivo: avaliar como dados operacionais podem apoiar a priorização de ativos e a discussão de indisponibilidade.",
      },
      {
        title: "Valores",
        text: "Evidência antes de opinião, segurança do paciente, simplicidade para a equipe técnica e governança rastreável.",
      },
      {
        title: "Quem somos",
        text: "Proposta em validação: apoiar equipes MedTech na organização de dados técnicos, revisão de hipóteses e acompanhamento operacional.",
      },
      {
        title: "Ajuda / FAQs",
        text: "O escopo é combinado antes do trabalho. Integrações dependem da validação de acesso, dados, campos e limites técnicos.",
      },
    ],
    pricingHeroTitle: "Escopos de diagnóstico e piloto",
    pricingHeroSubtitle:
      "Valores e prazos-alvo de referência. Escopo, dados, acesso e disponibilidade são confirmados antes da contratação.",
    seePlans: "Ver escopos",
    sales: "Falar com vendas",
    chooseTitle: "Escolha um escopo para avaliar",
    chooseText:
      "Cada oferta depende da confirmação da fonte, qualidade dos dados, acesso e objetivo. A recorrência permanece uma hipótese a validar após pilotos pagos.",
    resourceScale: "Opções de escopo",
    planHint:
      "Os prazos são alvos de planejamento, sujeitos à disponibilidade e à validação dos dados e acessos antes do início.",
    customSales: "Confirme escopo e disponibilidade antes da contratação",
    plans: {
      basic: {
        name: "Diagnóstico de suporte",
        label: "Escopo inicial",
        price: "R$ 2.500",
        cta: "Conversar sobre diagnóstico",
        description: "Até 100 OS, 1 fonte, entrevista, gargalos e plano. Prazo-alvo: 5 dias úteis.",
        included: [
          "Análise de até 100 ordens de serviço",
          "Uma fonte de dados",
          "Entrevista, gargalos e plano",
        ],
        excluded: [],
      },
      premium: {
        name: "Piloto de indicadores",
        label: "Oferta recomendada",
        price: "R$ 4.900",
        cta: "Conversar sobre o piloto",
        description: "Até 300 OS, 1 fonte/equipe/linha, dashboard e triagem. Prazo-alvo: 10 dias úteis.",
        included: [
          "Análise de até 300 ordens de serviço",
          "Uma fonte, equipe ou linha",
          "Dashboard e triagem",
        ],
        excluded: [],
      },
      vip: {
        name: "Piloto + automação assistida",
        label: "Escopo ampliado",
        price: "R$ 9.500",
        cta: "Validar escopo do piloto",
        description: "Piloto de indicadores + 1 fluxo e 1 integração, após validação técnica. Prazo-alvo: 15 dias úteis.",
        included: [
          "Escopo do piloto de indicadores",
          "Um fluxo de automação assistida",
          "Uma integração validada",
        ],
        excluded: [],
      },
      consultoria: {
        name: "Recorrência",
        label: "Hipótese a validar",
        price: "R$ 1.500–3.000/mês",
        cta: "Validar hipótese de recorrência",
        description: "Faixa e escopo preliminares, a validar após pilotos pagos. Prazo e disponibilidade a definir.",
        included: [
          "Dashboard, ritual e monitoramento são hipóteses de escopo a validar",
        ],
        excluded: [],
      },
    },
  },
  en: {
    badge: "Data intelligence for MedTech technical service",
    title: ["Turn service data into"],
    titleAccent: ["technical service", "decisions"],
    subtitle:
      `${APP_NAME} organizes service records, logs and equipment history to support triage, review of root-cause hypotheses and availability tracking. Analysis is assistive: validation and technical decisions remain with the responsible team.`,
    cta: "Discuss a pilot",
    secondaryCta: "Access platform",
    kpiTitle: "Metrics pilot reference",
    kpis: [
      { label: "Service orders", value: "Up to 300", icon: Server },
      { label: "Source / team / service line", value: "1", icon: Clock3 },
      { label: "Target timeline", value: "10 business days", icon: Stethoscope },
    ],
    highlights: [
      {
        icon: Activity,
        title: "Visibility into available data",
        description: "Bring together tickets, history and indicators; updates and integrations are defined in the pilot.",
      },
      {
        icon: Target,
        title: "Incident context",
        description: "Organize technical context and root cause hypotheses for review by the responsible team.",
      },
      {
        icon: ShieldCheck,
        title: "Technical review",
        description: "Organize playbooks and priorities for review by the responsible team. The platform does not perform maintenance.",
      },
    ],
    evidenceTitle: "Demonstration, pilot and measured results",
    evidenceText: "The demonstration presents features using illustrative data. A pilot validates use with an authorized sample from your operation. Results will only be presented as measured cases with a documented period, sample, calculation and authorization. We do not promise a percentage reduction in MTTR or guaranteed availability.",
    privacyText: "Share only authorized data, without patient identifiers, credentials or third-party confidential information. Transfer channel, access and retention are agreed before sharing.",
    experimentEyebrow: `Try ${APP_NAME}`,
    experimentTitle: "Agree on scope and criteria before contracting.",
    experimentText:
      "The metrics pilot covers up to 300 service orders and one source, team or service line. Sample, access, deliverables, availability and criteria are confirmed before contracting; the target timeline is 10 business days.",
    plansMiniTitle: "Work scopes",
    plansMiniText: "Diagnostic and pilot options with explicit data sources, scope and target timelines.",
    institutional: [
      {
        title: "Mission",
        text: "Bring predictability to clinical engineering and biomedical IT by connecting technical data, risk and operational decisions.",
      },
      {
        title: "Vision",
        text: "Objective: assess how operational data can support asset prioritization and downtime discussions.",
      },
      {
        title: "Values",
        text: "Evidence before opinion, patient safety, simplicity for technical teams and traceable governance.",
      },
      {
        title: "About us",
        text: "Proposal under validation: support MedTech teams in organizing technical data, reviewing hypotheses and tracking operations.",
      },
      {
        title: "Help / FAQs",
        text: "Scope is agreed before work begins. Integrations depend on validating access, data, fields and technical limits.",
      },
    ],
    pricingHeroTitle: "Diagnostic and pilot scopes",
    pricingHeroSubtitle:
      "Reference prices and target timelines. Scope, data, access and availability are confirmed before contracting.",
    seePlans: "View scopes",
    sales: "Talk to sales",
    chooseTitle: "Choose a scope to evaluate",
    chooseText:
      "Each offer depends on confirming the source, data quality, access and objective. Recurring service remains a hypothesis to validate after paid pilots.",
    resourceScale: "Scope options",
    planHint:
      "Timelines are planning targets, subject to availability and validation of data and access before work begins.",
    customSales: "Confirm scope and availability before contracting",
    plans: {
      basic: {
        name: "Support diagnosis",
        label: "Initial scope",
        price: "R$ 2,500",
        cta: "Discuss the diagnosis",
        description: "Up to 100 service orders, 1 source, interview, bottlenecks and action plan. Target: 5 business days.",
        included: [
          "Analysis of up to 100 service orders",
          "One data source",
          "Interview, bottlenecks and action plan",
        ],
        excluded: [],
      },
      premium: {
        name: "Metrics pilot",
        label: "Recommended offer",
        price: "R$ 4,900",
        cta: "Discuss the pilot",
        description: "Up to 300 service orders, 1 source/team/service line, dashboard and triage. Target: 10 business days.",
        included: [
          "Analysis of up to 300 service orders",
          "One source, team or service line",
          "Dashboard and triage",
        ],
        excluded: [],
      },
      vip: {
        name: "Pilot + assisted automation",
        label: "Expanded scope",
        price: "R$ 9,500",
        cta: "Validate pilot scope",
        description: "Metrics pilot + 1 workflow and 1 integration, after technical validation. Target: 15 business days.",
        included: [
          "Metrics pilot scope",
          "One assisted automation workflow",
          "One validated integration",
        ],
        excluded: [],
      },
      consultoria: {
        name: "Recurring service",
        label: "Hypothesis to validate",
        price: "R$ 1,500–3,000/month",
        cta: "Validate recurring-service hypothesis",
        description: "Preliminary price range and scope, to validate after paid pilots. Timeline and availability to be defined.",
        included: [
          "Dashboard, review routine and monitoring are scope hypotheses to validate",
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
                  href="https://wa.me/5547996789861"
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
                    <strong className="text-lg text-white">{value}</strong>
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

      <section className="mx-auto max-w-[1440px] px-6 py-12 sm:px-8">
        <h2 className="text-2xl font-black">{t.evidenceTitle}</h2>
        <p className="mt-4 max-w-5xl leading-7 text-slate-200">{t.evidenceText}</p>
        <p className="mt-4 max-w-5xl leading-7 text-slate-300">{t.privacyText}</p>
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
              {APP_NAME}
            </div>
            <Link
              href="https://wa.me/5547996789861"
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
                href="https://wa.me/5547996789861"
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
                <div className="grid gap-8">
                  <div>
                    <h4 className="text-2xl font-black text-white">{t.chooseTitle}</h4>
                    <p className="mt-3 max-w-3xl text-base leading-7 text-slate-300">{t.chooseText}</p>
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
                          href="https://wa.me/5547996789861"
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
