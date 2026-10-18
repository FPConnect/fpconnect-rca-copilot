"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  ArrowRight,
  Check,
  Clock3,
  FileSearch,
  Languages,
  MessageCircle,
  ShieldCheck,
  Stethoscope,
} from "lucide-react";
import BrandLogo from "@/components/BrandLogo";
import { APP_NAME } from "@/lib/brand";

type Locale = "pt" | "en";

const copy = {
  pt: {
    badge: "Diagnóstico técnico pago · remoto",
    title: "Encontre padrões de falha antes de investir em mais manutenção.",
    subtitle:
      "O OPSPECTA organiza ordens de serviço, logs e códigos de erro para revelar recorrências, gargalos de atendimento e oportunidades de redução de tempo de indisponibilidade. A validação técnica final permanece com a equipe responsável.",
    commercialLabel: "Enquadramento comercial",
    commercialTitle: "Proposta sob medida",
    commercialText: "O investimento é definido após confirmar volume de dados, complexidade, integrações, requisitos de segurança e critérios de aceite.",
    cta: "Solicitar diagnóstico",
    secondary: "Ver plataforma",
    deliverableTitle: "O que você recebe",
    deliverables: [
      "Leitura estruturada de até 100 ordens de serviço ou registros equivalentes",
      "Mapa dos principais padrões de falha, recorrências e gargalos",
      "Indicadores disponíveis de MTTR, frequência e concentração por ativo/categoria",
      "Hipóteses de causa raiz organizadas para revisão da equipe técnica",
      "Relatório executivo com prioridades e plano de ação",
      "Reunião remota de apresentação e próximos passos",
    ],
    inputTitle: "O que precisamos",
    inputs: [
      "Ordens de serviço, tickets, logs ou códigos de erro exportáveis",
      "Contexto básico dos equipamentos ou da operação",
      "Uma pessoa de referência para alinhar escopo e validar interpretações",
    ],
    timelineTitle: "Prazo-alvo",
    timeline: "5 dias úteis após recebimento da amostra acordada",
    scopeTitle: "Escopo inicial",
    scope: "Até 100 registros · 1 fonte de dados · 1 entrevista de alinhamento",
    privacyTitle: "Dados e confidencialidade",
    privacy:
      "Não envie identificação de pacientes, credenciais ou dados confidenciais de terceiros. O canal, acesso e retenção dos arquivos são definidos antes do compartilhamento.",
    nextTitle: "Se o diagnóstico mostrar valor",
    nextText:
      "O próximo passo é um piloto de indicadores com até 300 ordens de serviço, dashboard e triagem estruturada. Automação e integrações entram somente depois de validação técnica e comercial.",
    nextCta: "Quero discutir um piloto",
    fitTitle: "Ideal para",
    fit: "Clínicas, hospitais, distribuidores, fabricantes e operações de suporte técnico com histórico de chamados ou logs e necessidade de reduzir indisponibilidade.",
    note: "Diagnóstico analítico e apoio à decisão. Não substitui manutenção, validação clínica, engenharia responsável ou requisitos regulatórios.",
  },
  en: {
    badge: "Paid technical diagnostic · remote",
    title: "Find failure patterns before spending more on maintenance.",
    subtitle:
      "OPSPECTA organizes service orders, logs and error codes to surface recurring issues, service bottlenecks and opportunities to reduce downtime. Final technical validation remains with the responsible team.",
    commercialLabel: "Commercial scoping",
    commercialTitle: "Tailored proposal",
    commercialText: "Investment is defined after confirming data volume, complexity, integrations, security requirements and acceptance criteria.",
    cta: "Request diagnostic",
    secondary: "View platform",
    deliverableTitle: "What you receive",
    deliverables: [
      "Structured review of up to 100 service orders or equivalent records",
      "Map of recurring failures, patterns and service bottlenecks",
      "Available MTTR, frequency and concentration indicators by asset/category",
      "Root-cause hypotheses organized for technical-team review",
      "Executive report with priorities and action plan",
      "Remote readout meeting and next-step recommendations",
    ],
    inputTitle: "What we need",
    inputs: [
      "Exportable service orders, tickets, logs or error codes",
      "Basic context about the equipment or operation",
      "One operational contact to align scope and validate interpretation",
    ],
    timelineTitle: "Target timeline",
    timeline: "5 business days after receiving the agreed sample",
    scopeTitle: "Initial scope",
    scope: "Up to 100 records · 1 data source · 1 scoping interview",
    privacyTitle: "Data and confidentiality",
    privacy:
      "Do not send patient identifiers, credentials or third-party confidential data. Transfer channel, access and retention are defined before any files are shared.",
    nextTitle: "If the diagnostic proves useful",
    nextText:
      "The next step is a metrics pilot with up to 300 service orders, dashboard and structured triage. Automation and integrations come only after technical and commercial validation.",
    nextCta: "Discuss a pilot",
    fitTitle: "Best fit",
    fit: "Clinics, hospitals, distributors, manufacturers and technical-service operations with ticket or log history and a need to reduce downtime.",
    note: "Analytical diagnostic and decision support only. It does not replace maintenance, clinical validation, responsible engineering or regulatory requirements.",
  },
} as const;

export default function DiagnosticPage() {
  const [locale, setLocale] = useState<Locale>("pt");
  const t = useMemo(() => copy[locale], [locale]);
  const whatsappHref =
    "https://wa.me/5547996789861?text=" +
    encodeURIComponent(
      locale === "pt"
        ? "Olá! Quero solicitar o OPSPECTA Technical Reliability Diagnostic."
        : "Hi! I would like to request the OPSPECTA Technical Reliability Diagnostic."
    );

  return (
    <main className="brand-surface min-h-screen bg-white text-[#071a3d]" data-no-translate>
      <section className="border-b border-slate-200 bg-[#f4f8fa]">
        <div className="mx-auto max-w-[1180px] px-5 py-5 sm:px-8">
          <nav className="flex items-center justify-between gap-4">
            <Link href="/" aria-label={APP_NAME}>
              <BrandLogo />
            </Link>
            <div className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white p-1 text-sm font-bold">
              <Languages size={16} className="ml-2 text-[#0a7f86]" aria-hidden="true" />
              <button
                type="button"
                onClick={() => setLocale("pt")}
                className={`min-h-9 rounded-md px-3 ${locale === "pt" ? "bg-[#071a3d] text-white" : "text-slate-600"}`}
              >
                PT
              </button>
              <button
                type="button"
                onClick={() => setLocale("en")}
                className={`min-h-9 rounded-md px-3 ${locale === "en" ? "bg-[#071a3d] text-white" : "text-slate-600"}`}
              >
                EN
              </button>
            </div>
          </nav>
        </div>
      </section>

      <section className="bg-white py-16 sm:py-20">
        <div className="mx-auto grid max-w-[1180px] gap-12 px-5 sm:px-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-[#18c8c0]/40 bg-[#e9fbfa] px-4 py-2 text-sm font-black text-[#075c63]">
              <FileSearch size={16} aria-hidden="true" />
              {t.badge}
            </span>
            <h1 className="mt-6 max-w-3xl text-4xl font-black leading-tight text-[#071a3d] sm:text-5xl">
              {t.title}
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-600">{t.subtitle}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href={whatsappHref}
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[#071a3d] px-6 font-black text-white transition hover:bg-[#0a7f86]"
              >
                <MessageCircle size={19} aria-hidden="true" />
                {t.cta}
              </Link>
              <Link
                href="/"
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg border border-[#071a3d] bg-white px-6 font-black text-[#071a3d] transition hover:border-[#0a7f86] hover:text-[#0a7f86]"
              >
                {t.secondary}
                <ArrowRight size={18} aria-hidden="true" />
              </Link>
            </div>
          </div>

          <aside className="rounded-2xl border border-slate-200 bg-[#071a33] p-8 text-white shadow-xl">
            <p className="text-sm font-black uppercase tracking-wide text-[#8eece7]">{t.commercialLabel}</p>
            <p className="mt-3 text-3xl font-black">{t.commercialTitle}</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">{t.commercialText}</p>
            <div className="mt-8 space-y-5 border-t border-slate-600 pt-6">
              <div className="flex gap-3">
                <Clock3 size={20} className="mt-0.5 shrink-0 text-[#22d7cf]" aria-hidden="true" />
                <div>
                  <p className="font-black">{t.timelineTitle}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-300">{t.timeline}</p>
                </div>
              </div>
              <div className="flex gap-3">
                <Stethoscope size={20} className="mt-0.5 shrink-0 text-[#22d7cf]" aria-hidden="true" />
                <div>
                  <p className="font-black">{t.scopeTitle}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-300">{t.scope}</p>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-[#f4f8fa] py-16">
        <div className="mx-auto grid max-w-[1180px] gap-10 px-5 sm:px-8 lg:grid-cols-2">
          <article className="rounded-xl border border-slate-200 bg-white p-7 shadow-sm">
            <h2 className="text-2xl font-black">{t.deliverableTitle}</h2>
            <div className="mt-6 space-y-4">
              {t.deliverables.map((item) => (
                <div key={item} className="flex gap-3 text-slate-700">
                  <Check size={19} className="mt-0.5 shrink-0 text-[#0a7f86]" aria-hidden="true" />
                  <span className="leading-6">{item}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white p-7 shadow-sm">
            <h2 className="text-2xl font-black">{t.inputTitle}</h2>
            <div className="mt-6 space-y-4">
              {t.inputs.map((item) => (
                <div key={item} className="flex gap-3 text-slate-700">
                  <Check size={19} className="mt-0.5 shrink-0 text-[#0a7f86]" aria-hidden="true" />
                  <span className="leading-6">{item}</span>
                </div>
              ))}
            </div>
            <div className="mt-8 rounded-lg border border-[#18c8c0]/40 bg-[#e9fbfa] p-5">
              <div className="flex gap-3">
                <ShieldCheck size={21} className="mt-0.5 shrink-0 text-[#0a7f86]" aria-hidden="true" />
                <div>
                  <h3 className="font-black text-[#071a3d]">{t.privacyTitle}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{t.privacy}</p>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section className="bg-[#071a33] py-16 text-white">
        <div className="mx-auto max-w-[900px] px-5 text-center sm:px-8">
          <h2 className="text-3xl font-black sm:text-4xl">{t.nextTitle}</h2>
          <p className="mx-auto mt-5 max-w-3xl text-lg leading-8 text-slate-200">{t.nextText}</p>
          <Link
            href={whatsappHref}
            className="mt-8 inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-[#18c8c0] px-7 font-black text-[#071a3d] transition hover:bg-[#39ddd5]"
          >
            {t.nextCta}
            <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>

      <section className="bg-white py-12">
        <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
          <h2 className="text-2xl font-black">{t.fitTitle}</h2>
          <p className="mt-3 max-w-4xl leading-7 text-slate-600">{t.fit}</p>
          <p className="mt-6 border-t border-slate-200 pt-5 text-sm leading-6 text-slate-500">{t.note}</p>
        </div>
      </section>
    </main>
  );
}
