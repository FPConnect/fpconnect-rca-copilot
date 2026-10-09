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
  Server,
  ShieldCheck,
  Stethoscope,
  Target,
} from "lucide-react";
import BrandLogo from "@/components/BrandLogo";
import { setLanguagePreference } from "@/components/LanguageRuntime";
import { APP_NAME } from "@/lib/brand";

type Locale = "pt" | "en";
type PlanKey = "basic" | "premium" | "vip" | "consultoria";

const planOrder: PlanKey[] = ["basic", "premium", "vip", "consultoria"];

const copy = {
  pt: {
    languageLabel: "Selecionar idioma",
    badge: "Inteligência de dados para operações MedTech",
    headline: "Performance de tecnologia em saúde",
    subtitle:
      `${APP_NAME} organiza chamados, logs e histórico de equipamentos para apoiar triagem, revisão de hipóteses de causa raiz e acompanhamento de disponibilidade. A decisão técnica permanece com a equipe responsável.`,
    cta: "Fale com nossa equipe",
    secondaryCta: "Acessar plataforma",
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
    evidenceTitle: "Demonstração não é resultado medido.",
    evidenceText:
      "A demonstração usa dados ilustrativos. O piloto valida o uso com uma amostra autorizada da operação. Um resultado só é apresentado como medido quando período, amostra, cálculo e autorização estão documentados.",
    privacyText:
      "Não envie identificação de pacientes, credenciais ou informações confidenciais de terceiros. Canal, acesso e retenção são definidos antes de qualquer compartilhamento.",
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
    badge: "Data intelligence for MedTech operations",
    headline: "Healthcare technology performance",
    subtitle:
      `${APP_NAME} organizes service records, logs and equipment history to support triage, root-cause hypothesis review and availability tracking. Technical decisions remain with the responsible team.`,
    cta: "Talk to our team",
    secondaryCta: "Access platform",
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
    evidenceTitle: "A demonstration is not a measured result.",
    evidenceText:
      "The demonstration uses illustrative data. A pilot validates use with an authorized operational sample. Results are only presented as measured when the period, sample, calculation and authorization are documented.",
    privacyText:
      "Do not send patient identifiers, credentials or third-party confidential information. Transfer channel, access and retention are defined before any data is shared.",
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
  const [locale, setLocale] = useState<Locale>("pt");
  const [activePlan, setActivePlan] = useState<PlanKey>("premium");
  const t = copy[locale];
  const active = useMemo(() => t.plans[activePlan], [activePlan, t.plans]);

  const handleLocaleChange = (nextLocale: Locale) => {
    setLanguagePreference(nextLocale === "pt" ? "pt-BR" : "en-US");
    setLocale(nextLocale);
  };

  useEffect(() => {
    const previousLanguage = document.documentElement.lang;
    document.documentElement.lang = locale === "pt" ? "pt-BR" : "en-US";

    return () => {
      document.documentElement.lang = previousLanguage;
    };
  }, [locale]);

  return (
    <main className="min-h-screen bg-white text-[#071a3d]" data-no-translate>
      <section className="relative min-h-[680px] overflow-hidden border-b border-slate-200 bg-white">
        <Image
          src="/brand/opspecta-hero.png"
          alt="Profissional de tecnologia em saúde analisando indicadores operacionais anonimizados"
          fill
          priority
          sizes="100vw"
          className="object-cover object-center"
        />
        <div className="absolute inset-y-0 left-0 w-full bg-white/95 md:w-[72%] md:bg-white/90 lg:w-[61%]" />

        <div className="relative mx-auto flex min-h-[680px] w-full max-w-[1440px] flex-col px-5 sm:px-8 lg:px-10">
          <nav className="flex min-h-20 items-center justify-between gap-4 border-b border-slate-200/80">
            <BrandLogo />
            <div
              className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white p-1 text-sm font-bold shadow-sm"
              aria-label={t.languageLabel}
            >
              <Languages size={16} className="ml-2 text-[#0a7f86]" aria-hidden="true" />
              <button
                type="button"
                aria-pressed={locale === "pt"}
                onClick={() => handleLocaleChange("pt")}
                className={`min-h-9 rounded-md px-3 ${locale === "pt" ? "bg-[#071a3d] text-white" : "text-slate-600"}`}
              >
                Português
              </button>
              <button
                type="button"
                aria-pressed={locale === "en"}
                onClick={() => handleLocaleChange("en")}
                className={`min-h-9 rounded-md px-3 ${locale === "en" ? "bg-[#071a3d] text-white" : "text-slate-600"}`}
              >
                English
              </button>
            </div>
          </nav>

          <div className="flex flex-1 items-center py-10">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-[#1bbdb6]/40 bg-white/85 px-4 py-2 text-sm font-bold text-[#075c63]">
                <ShieldCheck size={16} aria-hidden="true" />
                {t.badge}
              </div>
              <h1
                className="brand-wordmark mt-7 text-[3.25rem] leading-[0.92] text-[#071a3d] sm:text-[4.25rem]"
                data-brand-wordmark
              >
                {APP_NAME}
              </h1>
              <p className="mt-5 max-w-xl text-3xl font-bold leading-tight text-[#0a7f86]">{t.headline}</p>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">{t.subtitle}</p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link
                  href="https://wa.me/5547996789861"
                  className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[#071a3d] px-6 font-bold text-white shadow-lg transition hover:bg-[#0a7f86]"
                >
                  <MessageCircle size={19} aria-hidden="true" />
                  {t.cta}
                </Link>
                <Link
                  href="/login"
                  className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg border border-[#071a3d] bg-white/90 px-6 font-bold text-[#071a3d] transition hover:border-[#0a7f86] hover:text-[#0a7f86]"
                >
                  {t.secondaryCta}
                  <ArrowRight size={18} aria-hidden="true" />
                </Link>
              </div>

              <div className="mt-9 border-y border-slate-300 bg-white/80 py-4">
                <p className="mb-3 text-xs font-bold uppercase text-slate-500">{t.pilotReference}</p>
                <div className="grid gap-4 sm:grid-cols-3">
                  {t.kpis.map(({ label, value, icon: Icon }) => (
                    <div key={label} className="flex items-center gap-3 border-slate-200 sm:border-r sm:last:border-r-0">
                      <Icon size={19} className="shrink-0 text-[#0a7f86]" aria-hidden="true" />
                      <span>
                        <strong className="block text-base text-[#071a3d]">{value}</strong>
                        <span className="block text-xs text-slate-600">{label}</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-[#f4f8fa] py-16">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <p className="text-sm font-black uppercase text-[#0a7f86]">{t.sectionEyebrow}</p>
          <h2 className="mt-3 max-w-3xl text-4xl font-black leading-tight text-[#071a3d]">{t.sectionTitle}</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {t.highlights.map(({ icon: Icon, title, description }) => (
              <article key={title} className="rounded-lg border border-slate-200 bg-white p-7 shadow-sm">
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-lg bg-[#dff8f6] text-[#08777c]">
                  <Icon size={22} aria-hidden="true" />
                </span>
                <h3 className="mt-6 text-xl font-black text-[#071a3d]">{title}</h3>
                <p className="mt-3 leading-7 text-slate-600">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#071a33] py-14 text-white">
        <div className="mx-auto grid max-w-[1280px] gap-8 px-5 sm:px-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <BarChart3 size={34} className="text-[#22d7cf]" aria-hidden="true" />
            <h2 className="mt-5 text-3xl font-black leading-tight">{t.evidenceTitle}</h2>
          </div>
          <div className="border-l border-slate-600 pl-6">
            <p className="text-lg leading-8 text-slate-100">{t.evidenceText}</p>
            <p className="mt-4 text-sm leading-6 text-slate-300">{t.privacyText}</p>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <h2 className="text-4xl font-black text-[#071a3d]">{t.processTitle}</h2>
          <div className="mt-10 grid gap-8 md:grid-cols-3">
            {t.process.map((step) => (
              <article key={step.number} className="border-t-4 border-[#18c8c0] pt-5">
                <span className="text-sm font-black text-[#0a7f86]">{step.number}</span>
                <h3 className="mt-3 text-2xl font-black text-[#071a3d]">{step.title}</h3>
                <p className="mt-3 leading-7 text-slate-600">{step.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="plans" className="border-y border-slate-200 bg-[#f4f8fa] py-16">
        <div className="mx-auto max-w-[1280px] px-5 sm:px-8">
          <div className="max-w-4xl">
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
                  onClick={() => setActivePlan(planKey)}
                  className={`min-h-28 rounded-lg border p-5 text-left transition ${
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

          <div className="mt-8 grid gap-8 rounded-lg border border-slate-200 bg-white p-7 shadow-sm lg:grid-cols-[1fr_0.8fr] lg:p-9">
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
                href="https://wa.me/5547996789861"
                className="mt-7 inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[#18c8c0] px-6 font-black text-[#071a3d] transition hover:bg-[#39ddd5]"
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
          <p className="text-sm text-slate-500">© {new Date().getFullYear()} {APP_NAME}. Inteligência operacional para a saúde.</p>
        </div>
      </footer>
    </main>
  );
}
