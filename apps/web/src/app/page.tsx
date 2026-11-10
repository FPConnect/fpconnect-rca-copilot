"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Check,
  Clock3,
  Languages,
  MessageCircle,
  FileSearch,
  Server,
  ShieldCheck,
  Stethoscope,
  Target,
} from "lucide-react";
import BrandLogo from "@/components/BrandLogo";
import {
  setLanguagePreference,
  useLanguagePreference,
} from "@/components/LanguageRuntime";
import { APP_NAME } from "@/lib/brand";

type Locale = "pt" | "en";
type PlanKey = "basic" | "premium" | "vip" | "consultoria";

const planOrder: PlanKey[] = ["basic", "premium", "vip", "consultoria"];

const copy = {
  pt: {
    languageLabel: "Selecionar idioma",
    brandTagline: "Inteligência operacional para a saúde",
    heroAlt: "Profissional de tecnologia em saúde analisando indicadores operacionais anonimizados",
    badge: "Inteligência de dados para operações MedTech",
    headline: "Transforme ordens de serviço em prioridades de ação",
    subtitle:
      `${APP_NAME} organiza chamados, logs e histórico de equipamentos para apoiar triagem, revisão de hipóteses de causa raiz e acompanhamento de disponibilidade. A decisão técnica permanece com a equipe responsável.`,
    cta: "Conversar sobre o piloto",
    secondaryCta: "Acessar plataforma",
    resourceCta: "Checklist gratuito de OS",
    resourceHeading: "Antes de medir, qualifique os registros.",
    resourceDescription: "Use oito perguntas práticas para identificar lacunas em históricos de manutenção, sem expor dados sensíveis.",
    resourceLink: "Ver checklist gratuito",
    solutionsLink: "Conhecer soluções",
    pilotReference: "Referência do piloto de indicadores",
    kpis: [
      { label: "Ordens de serviço", value: "Até 300", icon: Server },
      { label: "Fonte, equipe ou linha", value: "1", icon: Stethoscope },
      { label: "Prazo-alvo", value: "10 dias úteis", icon: Clock3 },
    ],
    sectionEyebrow: "Decisão operacional com contexto",
    sectionTitle: "Dados técnicos organizados para quem precisa agir.",
    highlights: [
      {
        icon: Activity,
        title: "Visibilidade operacional",
        description: "Reúna tickets, histórico e indicadores disponíveis em uma leitura consistente da operação.",
      },
      {
        icon: Target,
        title: "Contexto para incidentes",
        description: "Estruture evidências e hipóteses de causa raiz para revisão da equipe técnica responsável.",
      },
      {
        icon: ShieldCheck,
        title: "Governança rastreável",
        description: "Organize prioridades, playbooks e decisões sem substituir validações técnicas ou manutenção.",
      },
    ],
    pilotEyebrow: "Piloto de indicadores",
    pilotTitle: "O que sua equipe pode aprender com uma amostra de OS",
    pilotIntro:
      "Com até 300 ordens de serviço de uma fonte, equipe ou linha, o piloto organiza os registros disponíveis em um dashboard e uma triagem estruturada para apoiar a revisão da operação.",
    pilotOutcomes: [
      {
        title: "Volume, idade e fluxo",
        description: "Observe como os registros se distribuem por período, fila e tempo de ciclo, quando esses campos estão disponíveis.",
      },
      {
        title: "Qualidade do histórico",
        description: "Identifique campos ausentes ou inconsistências que limitam a leitura dos indicadores na amostra.",
      },
      {
        title: "Prioridades para revisão",
        description: "Reúna recorrências e hipóteses com contexto para a equipe técnica confirmar próximos passos.",
      },
    ],
    pilotCta: "Conhecer o diagnóstico de entrada",
    processTitle: "Do dado disponível à decisão revisada",
    process: [
      { number: "01", title: "Definir", text: "Confirmamos objetivo, fonte, amostra, acessos e critérios de aceite." },
      { number: "02", title: "Organizar", text: "Estruturamos o histórico e os indicadores dentro do escopo acordado." },
      { number: "03", title: "Revisar", text: "A equipe valida hipóteses, prioridades e próximos passos com rastreabilidade." },
    ],
    plansTitle: "Escopos claros para começar",
    plansText: "Cada proposta é dimensionada após confirmar dados, integrações, requisitos de segurança, nível de suporte e critérios de aceite.",
    chooseTitle: "Selecione um escopo",
    planHint: "O investimento é apresentado em proposta comercial após o enquadramento técnico da operação.",
    plans: {
      basic: {
        name: "Diagnóstico de suporte",
        label: "Escopo inicial",
        cta: "Conversar sobre diagnóstico",
        description: "Até 100 ordens de serviço, uma fonte, entrevista, gargalos e plano. Prazo-alvo: 5 dias úteis.",
        included: ["Até 100 ordens de serviço", "Uma fonte de dados", "Entrevista, gargalos e plano"],
      },
      premium: {
        name: "Piloto de indicadores",
        label: "Oferta recomendada",
        cta: "Conversar sobre o piloto",
        description: "Até 300 OS, uma fonte, equipe ou linha, dashboard e triagem. Prazo-alvo: 10 dias úteis.",
        included: ["Análise de até 300 ordens de serviço", "Uma fonte, equipe ou linha", "Dashboard e triagem"],
      },
      vip: {
        name: "Piloto + automação assistida",
        label: "Escopo ampliado",
        cta: "Validar escopo do piloto",
        description: "Piloto de indicadores, um fluxo e uma integração após validação técnica. Prazo-alvo: 15 dias úteis.",
        included: ["Escopo do piloto de indicadores", "Um fluxo de automação assistida", "Uma integração validada"],
      },
      consultoria: {
        name: "Recorrência",
        label: "Hipótese a validar",
        cta: "Validar hipótese de recorrência",
        description: "Faixa e escopo preliminares a validar após pilotos pagos. Prazo e disponibilidade a definir.",
        included: ["Dashboard, ritual de revisão e monitoramento como hipóteses de escopo"],
      },
    },
  },
  en: {
    languageLabel: "Select language",
    brandTagline: "Operational intelligence for healthcare",
    heroAlt: "Healthcare technology professional reviewing anonymized operational indicators",
    badge: "Data intelligence for MedTech operations",
    headline: "Turn service records into priorities for action",
    subtitle:
      `${APP_NAME} organizes service records, logs and equipment history to support triage, root-cause hypothesis review and availability tracking. Technical decisions remain with the responsible team.`,
    cta: "Discuss the pilot",
    secondaryCta: "Access platform",
    resourceCta: "Free work-order checklist (PT)",
    resourceHeading: "Check your records before measuring.",
    resourceDescription: "Eight practical questions to uncover service-record gaps before analytics. The resource is currently in Portuguese.",
    resourceLink: "Open free checklist (PT)",
    solutionsLink: "Explore solutions",
    pilotReference: "Metrics pilot reference",
    kpis: [
      { label: "Service orders", value: "Up to 300", icon: Server },
      { label: "Source, team or line", value: "1", icon: Stethoscope },
      { label: "Target timeline", value: "10 business days", icon: Clock3 },
    ],
    sectionEyebrow: "Operational decisions with context",
    sectionTitle: "Technical data organized for the people who need to act.",
    highlights: [
      {
        icon: Activity,
        title: "Operational visibility",
        description: "Bring together available tickets, history and indicators in a consistent operational view.",
      },
      {
        icon: Target,
        title: "Incident context",
        description: "Structure evidence and root-cause hypotheses for review by the responsible technical team.",
      },
      {
        icon: ShieldCheck,
        title: "Traceable governance",
        description: "Organize priorities, playbooks and decisions without replacing technical validation or maintenance.",
      },
    ],
    pilotEyebrow: "Metrics pilot",
    pilotTitle: "What your team can learn from a service-order sample",
    pilotIntro:
      "Using up to 300 service orders from one source, team or line, the pilot organizes available records into a dashboard and structured triage to support operational review.",
    pilotOutcomes: [
      {
        title: "Volume, age and flow",
        description: "Review how records are distributed over time, across queues and by cycle time when those fields are available.",
      },
      {
        title: "History quality",
        description: "Identify missing fields or inconsistencies that limit how indicators in the sample can be interpreted.",
      },
      {
        title: "Priorities for review",
        description: "Bring recurring issues and contextualized hypotheses together for the technical team to validate next steps.",
      },
    ],
    pilotCta: "Explore the entry diagnostic",
    processTitle: "From available data to reviewed decisions",
    process: [
      { number: "01", title: "Define", text: "We confirm the objective, source, sample, access and acceptance criteria." },
      { number: "02", title: "Organize", text: "We structure history and indicators within the agreed scope." },
      { number: "03", title: "Review", text: "The team validates hypotheses, priorities and next steps with traceability." },
    ],
    plansTitle: "Clear scopes to get started",
    plansText: "Each proposal is sized after confirming data, integrations, security requirements, support level and acceptance criteria.",
    chooseTitle: "Select a scope",
    planHint: "Investment is presented in a commercial proposal after the operation is technically scoped.",
    plans: {
      basic: {
        name: "Support diagnosis",
        label: "Initial scope",
        cta: "Discuss the diagnosis",
        description: "Up to 100 service orders, one source, interview, bottlenecks and plan. Target: 5 business days.",
        included: ["Up to 100 service orders", "One data source", "Interview, bottlenecks and plan"],
      },
      premium: {
        name: "Metrics pilot",
        label: "Recommended offer",
        cta: "Discuss the pilot",
        description: "Up to 300 service orders, one source, team or line, dashboard and triage. Target: 10 business days.",
        included: ["Analysis of up to 300 service orders", "One source, team or line", "Dashboard and triage"],
      },
      vip: {
        name: "Pilot + assisted automation",
        label: "Expanded scope",
        cta: "Validate pilot scope",
        description: "Metrics pilot, one workflow and one integration after technical validation. Target: 15 business days.",
        included: ["Metrics pilot scope", "One assisted automation workflow", "One validated integration"],
      },
      consultoria: {
        name: "Recurring service",
        label: "Hypothesis to validate",
        cta: "Validate recurring-service hypothesis",
        description: "Preliminary range and scope to validate after paid pilots. Timeline and availability to be defined.",
        included: ["Dashboard, review routine and monitoring as scope hypotheses"],
      },
    },
  },
} as const;

export default function LandingPage() {
  const languagePreference = useLanguagePreference();
  const locale: Locale = languagePreference === "en-US" ? "en" : "pt";
  const brandBannerSrc = locale === "en"
    ? "/brand/opspecta-brand-banner-en.png"
    : "/brand/opspecta-brand-banner.jpg";
  const [activePlan, setActivePlan] = useState<PlanKey>("premium");
  const t = copy[locale];
  const active = useMemo(() => t.plans[activePlan], [activePlan, t.plans]);

  const handleLocaleChange = (nextLocale: Locale) => {
    setLanguagePreference(nextLocale === "pt" ? "pt-BR" : "en-US");
  };

  useEffect(() => {
    const previousLanguage = document.documentElement.lang;
    document.documentElement.lang = locale === "pt" ? "pt-BR" : "en-US";

    return () => {
      document.documentElement.lang = previousLanguage;
    };
  }, [locale]);

  useEffect(() => {
    const prefersReducedMotion =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion || typeof IntersectionObserver === "undefined") return;

    document.documentElement.classList.add("motion-enabled");
    const elements = Array.from(document.querySelectorAll<HTMLElement>("[data-motion]"));
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("motion-visible");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8%", threshold: 0.12 },
    );

    elements.forEach((element) => observer.observe(element));
    return () => {
      observer.disconnect();
      document.documentElement.classList.remove("motion-enabled");
    };
  }, []);

  return (
    <main className="brand-surface app-viewport bg-white text-[#071a3d]" data-no-translate>
      <section className="landing-hero relative overflow-hidden bg-[#07172c] text-white">
        <div className="landing-orbits pointer-events-none absolute inset-0" aria-hidden="true">
          <span /><span /><span />
        </div>
        <div className="relative mx-auto flex w-full max-w-[1440px] flex-col px-5 sm:px-8 lg:px-12">
          <nav data-motion="fade" className="flex min-h-24 items-center justify-between gap-4 border-b border-white/10">
            <BrandLogo compact className="sm:hidden" inverse />
            <BrandLogo inverse className="hidden sm:inline-flex" />
            <div
              className="inline-flex items-center gap-1 rounded-full border border-white/15 bg-white/5 p-1 text-sm font-bold"
              aria-label={t.languageLabel}
            >
              <Languages size={16} className="ml-2 hidden text-[#81dbd4] sm:block" aria-hidden="true" />
              <button
                type="button"
                aria-pressed={locale === "pt"}
                onClick={() => handleLocaleChange("pt")}
                className={`min-h-9 rounded-full px-3 sm:px-4 ${locale === "pt" ? "bg-white text-[#07172c]" : "text-slate-300 hover:text-white"}`}
              >
                Português
              </button>
              <button
                type="button"
                aria-pressed={locale === "en"}
                onClick={() => handleLocaleChange("en")}
                className={`min-h-9 rounded-full px-3 sm:px-4 ${locale === "en" ? "bg-white text-[#07172c]" : "text-slate-300 hover:text-white"}`}
              >
                English
              </button>
            </div>
          </nav>

          <div className="grid items-center gap-12 py-14 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16 lg:py-24">
            <div className="max-w-2xl">
              <div data-motion className="inline-flex items-center gap-2 text-xs font-extrabold uppercase tracking-[0.16em] text-[#8ce7dc]">
                <span className="h-2 w-2 rounded-full bg-[#70e8da]" aria-hidden="true" />
                {t.badge}
              </div>
              <h1 data-motion className="mt-6 max-w-2xl text-[2.4rem] font-semibold leading-[1.12] tracking-[-0.035em] text-white sm:text-5xl lg:text-[3.6rem]">{t.headline}</h1>
              <p data-motion className="mt-6 max-w-xl text-base leading-7 text-[#b8cbd3] sm:text-lg sm:leading-8">{t.subtitle}</p>
              <div data-motion className="mt-8 flex flex-wrap gap-3">
                <Link
                  href={`https://wa.me/5547996789861?text=${encodeURIComponent(locale === "pt" ? "Olá! Quero conversar sobre o piloto de indicadores da OPSPECTA." : "Hello! I would like to discuss the OPSPECTA metrics pilot.")}`}
                  className="motion-arrow motion-lift inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-[#8ce7dc] px-6 font-bold text-[#07172c] transition hover:bg-[#b2fff3]"
                >
                  <MessageCircle size={19} aria-hidden="true" />
                  {t.cta}
                </Link>
                <Link
                  href="/login"
                  className="motion-arrow motion-lift inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-white/25 px-6 font-bold text-white transition hover:border-[#8ce7dc] hover:bg-white/5"
                >
                  {t.secondaryCta}
                  <ArrowRight size={18} aria-hidden="true" />
                </Link>
                <Link
                  href="/recursos"
                  className="motion-arrow inline-flex min-h-12 items-center justify-center gap-2 px-2 font-bold text-[#a2dcd7] transition hover:text-white"
                >
                  <FileSearch size={18} aria-hidden="true" />
                  {t.resourceCta}
                </Link>
              </div>

              <div data-motion className="mt-10 border-t border-white/15 pt-5">
                <p className="mb-4 text-xs font-bold uppercase tracking-[0.14em] text-[#93aebb]">{t.pilotReference}</p>
                <div className="grid gap-4 sm:grid-cols-3">
                  {t.kpis.map(({ label, value, icon: Icon }) => (
                    <div key={label} className="flex items-center gap-3 border-white/15 sm:border-r sm:last:border-r-0">
                      <Icon size={19} className="shrink-0 text-[#8ce7dc]" aria-hidden="true" />
                      <span>
                        <strong className="block text-base text-white">{value}</strong>
                        <span className="block text-xs text-[#b8cbd3]">{label}</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div data-motion="scale" className="relative mx-auto w-full max-w-[620px]">
              <div className="landing-image relative overflow-hidden rounded-[1.75rem] border border-white/20">
                <Image src="/brand/opspecta-hero.png" alt={t.heroAlt} width={1672} height={941} priority sizes="(max-width: 660px) calc(133.34vw - 53.34px), 827px" className="aspect-[4/3] w-full object-cover object-[72%_center]" />
              </div>
              <div className="relative mx-auto -mt-7 aspect-[22/5] w-[88%] overflow-hidden rounded-xl border border-white/70 bg-white shadow-xl" data-brand-banner>
                <Image src={brandBannerSrc} alt={`${APP_NAME} - ${t.brandTagline}`} fill sizes="(max-width: 660px) 88vw, 546px" className="object-contain" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-[#f5f8f7] py-20 sm:py-24">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <p data-motion className="text-xs font-extrabold uppercase tracking-[0.16em] text-[#087a72]">{t.sectionEyebrow}</p>
          <h2 data-motion className="mt-4 max-w-3xl text-3xl font-semibold leading-tight tracking-tight text-[#10293a] sm:text-4xl">{t.sectionTitle}</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {t.highlights.map(({ icon: Icon, title, description }, index) => (
              <article key={title} data-motion className="motion-lift rounded-2xl border border-[#dfeae7] bg-white p-8" style={{ transitionDelay: `${index * 80}ms` }}>
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[#e1f5f0] text-[#087a72]">
                  <Icon size={22} aria-hidden="true" />
                </span>
                <h3 className="mt-7 text-xl font-semibold text-[#10293a]">{title}</h3>
                <p className="mt-3 leading-7 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-pilot relative overflow-hidden bg-[#07172c] py-20 text-white sm:py-24" aria-labelledby="pilot-learning-heading">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <div data-motion className="max-w-3xl">
            <BarChart3 size={34} className="text-[#22d7cf]" aria-hidden="true" />
            <p className="mt-5 text-sm font-black uppercase tracking-wide text-[#66efe5]">{t.pilotEyebrow}</p>
            <h2 id="pilot-learning-heading" className="mt-3 text-3xl font-black leading-tight">{t.pilotTitle}</h2>
            <p className="mt-4 text-lg leading-8 text-slate-100">{t.pilotIntro}</p>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {t.pilotOutcomes.map((outcome, index) => (
              <article key={outcome.title} data-motion className="rounded-2xl border border-white/15 bg-white/5 p-7" style={{ transitionDelay: `${index * 80}ms` }}>
                <h3 className="text-lg font-black text-white">{outcome.title}</h3>
                <p className="mt-3 leading-7 text-slate-200">{outcome.description}</p>
              </article>
            ))}
          </div>
          <Link
            href="/diagnostic"
            className="motion-arrow motion-lift mt-8 inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[#18c8c0] px-6 font-black text-[#071a3d] transition hover:bg-[#39ddd5]"
          >
            {t.pilotCta}
            <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>

      <section className="py-20 sm:py-24">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <h2 data-motion className="text-4xl font-black text-[#071a3d]">{t.processTitle}</h2>
          <div className="mt-10 grid gap-8 md:grid-cols-3">
            {t.process.map((step, index) => (
              <article key={step.number} data-motion className="border-t border-[#92d9d0] pt-6" style={{ transitionDelay: `${index * 80}ms` }}>
                <span className="text-sm font-black text-[#0a7f86]">{step.number}</span>
                <h3 className="mt-3 text-2xl font-black text-[#071a3d]">{step.title}</h3>
                <p className="mt-3 leading-7 text-slate-600">{step.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-[#dfeae7] bg-[#eff8f5] py-16" aria-labelledby="resources-heading">
        <div className="mx-auto flex max-w-[1280px] flex-col gap-5 px-5 sm:px-8 md:flex-row md:items-center md:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-black uppercase tracking-wide text-[#0a7f86]">{t.resourceCta}</p>
            <h2 id="resources-heading" className="mt-3 text-3xl font-black">{t.resourceHeading}</h2>
            <p className="mt-3 leading-7 text-slate-700">{t.resourceDescription}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link href="/recursos" className="inline-flex min-h-12 shrink-0 items-center gap-2 rounded-lg bg-[#071a3d] px-5 py-3 font-bold text-white hover:bg-[#0a7f86]">
              {t.resourceLink}<ArrowRight size={17} aria-hidden="true" />
            </Link>
            <Link href="/solucoes" className="inline-flex min-h-12 shrink-0 items-center gap-2 rounded-lg border border-[#071a3d] px-5 py-3 font-bold text-[#071a3d] hover:bg-[#e8fbf9]">
              {t.solutionsLink}<ArrowRight size={17} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>

      <section id="plans" className="border-y border-slate-200 bg-[#f5f8f7] py-20 sm:py-24">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <div data-motion className="max-w-4xl">
            <p className="text-sm font-black uppercase text-[#0a7f86]">{t.chooseTitle}</p>
            <h2 className="mt-3 text-4xl font-black text-[#071a3d]">{t.plansTitle}</h2>
            <p className="mt-5 text-lg leading-8 text-slate-600">{t.plansText}</p>
          </div>

          <div className="mt-10 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {planOrder.map((planKey) => {
              const plan = t.plans[planKey];
              const selected = activePlan === planKey;
              return (
                <button
                  key={plan.name}
                  type="button"
                  data-motion
                  aria-pressed={selected}
                  onClick={() => setActivePlan(planKey)}
                  style={{ transitionDelay: `${planOrder.indexOf(planKey) * 70}ms` }}
                  className={`motion-lift min-h-28 rounded-2xl border p-5 text-left transition ${
                    selected
                      ? "border-[#0a7f86] bg-[#071a33] text-white shadow-md"
                      : "border-slate-300 bg-white text-[#071a3d] hover:border-[#0a7f86]"
                  }`}
                >
                  <span className="block font-black">{plan.name}</span>
                  <span className={`mt-2 block text-sm ${selected ? "text-[#9df3ee]" : "text-slate-500"}`}>{plan.label}</span>
                </button>
              );
            })}
          </div>

          <div data-motion className="mt-8 grid gap-8 rounded-2xl border border-[#dfeae7] bg-white p-7 lg:grid-cols-[1fr_0.8fr] lg:p-9">
            <div>
              <p className="text-sm font-bold uppercase text-[#0a7f86]">{active.label}</p>
              <h3 className="mt-3 text-3xl font-black text-[#071a3d]">{active.name}</h3>
              <p className="mt-4 max-w-2xl leading-7 text-slate-600">{active.description}</p>
              <div className="mt-7 space-y-3">
                {active.included.map((item) => (
                  <div key={item} className="flex items-start gap-3 text-slate-700">
                    <Check size={19} className="mt-0.5 shrink-0 text-[#0a7f86]" aria-hidden="true" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex flex-col justify-between border-t border-slate-200 pt-7 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
              <p className="max-w-md text-base leading-7 text-slate-600">{t.planHint}</p>
              <Link
                href={`https://wa.me/5547996789861?text=${encodeURIComponent(locale === "pt" ? `Olá! Quero conversar com a OPSPECTA sobre: ${active.name}.` : `Hello! I would like to discuss ${active.name} with OPSPECTA.`)}`}
                className="motion-arrow motion-lift mt-7 inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[#18c8c0] px-6 font-black text-[#071a3d] transition hover:bg-[#39ddd5]"
              >
                {active.cta}
                <ArrowRight size={18} aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-white py-10">
        <div className="mx-auto flex max-w-[1280px] flex-wrap items-center justify-between gap-6 px-5 sm:px-8">
          <BrandLogo />
          <p className="text-sm text-slate-500">© {new Date().getFullYear()} {APP_NAME}. {t.brandTagline}.</p>
        </div>
      </footer>
    </main>
  );
}
