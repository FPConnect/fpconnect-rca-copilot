import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, BarChart3, CheckCircle2, ClipboardList, FileCheck2, ShieldCheck } from "lucide-react";
import BrandLogo from "@/components/BrandLogo";

export const metadata: Metadata = {
  title: "Soluções de inteligência operacional MedTech | OPSPECTA",
  description: "Diagnósticos e pilotos de indicadores para histórico de manutenção, qualidade de OS e gargalos de serviço. Conheça também as novas soluções em avaliação.",
  alternates: { canonical: "/solucoes" },
  openGraph: {
    title: "Soluções OPSPECTA | Inteligência operacional em serviços MedTech",
    description: "Comece pelo diagnóstico de dados e avalie soluções complementares para qualidade de OS, gargalos e reincidências.",
    url: "/solucoes",
  },
};

const now = [
  {
    name: "Diagnóstico de histórico de serviços",
    category: "Oferta de entrada · escopo de referência",
    context: "Para equipes que têm ordens de serviço, mas não sabem se seus dados sustentam decisões.",
    details: "Até 100 OS de uma fonte; entrevista de entendimento; análise de completude, recorrências e gargalos investigáveis; relatório e prioridades a validar.",
    timeline: "Referência: 5 dias úteis, após confirmação de escopo e dados.",
    button: "Solicitar enquadramento",
    href: "/diagnostic",
  },
  {
    name: "Piloto de indicadores operacionais",
    category: "Piloto · escopo de referência",
    context: "Para líderes de operações de assistência técnica que precisam visualizar o que acontece entre a abertura e o encerramento.",
    details: "Até 300 OS; uma fonte, equipe ou linha de serviços; revisão da qualidade dos registros, indicadores selecionados, dashboard e discussão técnica dos resultados.",
    timeline: "Referência: 10 dias úteis, sujeito à viabilidade e critérios de aceite.",
    button: "Conhecer o piloto",
    href: "/",
  },
];

const exploring = [
  {
    label: "Prioridade de teste 1",
    title: "Qualidade e padronização de ordens de serviço",
    impact: "Mapear campos ausentes, divergências de identificação, descrições insuficientes e inconsistências de datas.",
    validate: "Validar acesso a dados exportáveis, taxonomia por família de ativos, indicadores de completude e aceitação pela equipe.",
  },
  {
    label: "Prioridade de teste 2",
    title: "Mapa de espera e gargalos do atendimento",
    impact: "Distinguir tempos de reparo de espera por peça, acesso, aprovação e escalonamento para compreender atrasos.",
    validate: "Confirmar eventos de início/fim, qualidade dos carimbos de tempo e critérios comerciais de SLA.",
  },
  {
    label: "Prioridade de teste 3",
    title: "Radar de reincidências e histórico de investigação",
    impact: "Apoiar a identificação de ocorrências potencialmente relacionadas e produzir resumos de evidências para revisão L2/L3.",
    validate: "Testar se ativo, sintoma e contexto são consistentes; nunca afirmar causalidade ou recomendar ação de segurança crítica sem revisão humana.",
  },
];

export default function SolucoesPage() {
  return (
    <main id="conteudo-principal" className="min-h-screen bg-[#f5f8fa] text-[#071a3d]">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1120px] flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8">
          <Link href="/" aria-label="Página inicial da OPSPECTA"><BrandLogo /></Link>
          <nav aria-label="Navegação de soluções" className="flex flex-wrap gap-5 text-sm font-bold">
            <Link href="/" className="hover:text-[#0a7f86]">Início</Link>
            <Link href="/recursos" className="hover:text-[#0a7f86]">Checklist gratuito</Link>
            <Link href="/diagnostic" className="hover:text-[#0a7f86]">Diagnóstico</Link>
          </nav>
        </div>
      </header>

      <section className="bg-[#071a3d] px-5 py-16 text-white sm:px-8">
        <div className="mx-auto max-w-[1120px]">
          <span className="rounded-full border border-[#18c8c0]/50 px-4 py-2 text-sm font-bold text-[#5ee9e0]">Soluções OPSPECTA · serviços analíticos B2B</span>
          <h1 className="mt-7 max-w-4xl text-4xl font-black leading-tight sm:text-5xl">Históricos técnicos que ajudam a priorizar decisões.</h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-200">
            Nossa proposta é complementar seus sistemas e especialistas: qualificar registros de serviços MedTech,
            organizar evidências e investigar gargalos, sem substituir manutenção física, diagnóstico clínico
            ou decisões técnicas dos profissionais responsáveis.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/demonstracao" className="inline-flex min-h-12 items-center gap-2 rounded-lg border border-[#18c8c0] px-5 py-3 font-bold text-[#66efe5] hover:bg-white/10">
              Ver exemplo fictício <ArrowRight size={18} aria-hidden="true" />
            </Link>
            <Link href="/diagnostic" className="inline-flex min-h-12 items-center gap-2 rounded-lg bg-[#18c8c0] px-5 py-3 font-black text-[#071a3d] hover:bg-[#43e0d9]">
              Explorar diagnóstico <ArrowRight size={18} aria-hidden="true" />
            </Link>
            <Link href="/recursos" className="inline-flex min-h-12 items-center gap-2 rounded-lg border border-white/70 px-5 py-3 font-bold hover:bg-white/10">
              Checklist gratuito de OS
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1120px] px-5 py-14 sm:px-8">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="text-[#0a7f86]" size={24} aria-hidden="true" />
          <h2 className="text-3xl font-black">Escopos disponíveis para avaliação comercial</h2>
        </div>
        <p className="mt-4 max-w-3xl leading-7 text-slate-700">
          São escopos de referência, não serviços contratados nem resultados garantidos.
          Valor, prazo, segurança, permissões e critérios de aceite são definidos antes de iniciar qualquer trabalho.
        </p>
        <div className="mt-8 grid gap-5 md:grid-cols-2">
          {now.map((offer, index) => (
            <article key={offer.name} className="rounded-xl border border-slate-200 bg-white p-7 shadow-sm">
              {index === 0 ? <ClipboardList className="text-[#0a7f86]" size={28} aria-hidden="true" /> : <BarChart3 className="text-[#0a7f86]" size={28} aria-hidden="true" />}
              <p className="mt-4 text-xs font-black uppercase tracking-wide text-[#0a7f86]">{offer.category}</p>
              <h3 className="mt-3 text-2xl font-black">{offer.name}</h3>
              <p className="mt-3 leading-7 text-slate-700">{offer.context}</p>
              <p className="mt-4 border-l-4 border-[#18c8c0] pl-4 leading-7 text-slate-700">{offer.details}</p>
              <p className="mt-4 text-sm font-semibold text-slate-600">{offer.timeline}</p>
              <Link href={offer.href} className="mt-6 inline-flex min-h-11 items-center gap-2 font-bold text-[#075c63] underline underline-offset-4 hover:text-[#071a3d]">
                {offer.button} <ArrowRight size={17} aria-hidden="true" />
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-slate-200 bg-white px-5 py-14 sm:px-8">
        <div className="mx-auto max-w-[1120px]">
          <div className="flex items-center gap-3">
            <FileCheck2 className="text-[#0a7f86]" size={24} aria-hidden="true" />
            <h2 className="text-3xl font-black">Novas soluções em estudo</h2>
          </div>
          <p className="mt-4 max-w-3xl leading-7 text-slate-700">
            São hipóteses de serviços em validação técnica e comercial. A inclusão nesta página não indica
            funcionalidade de software concluída, disponibilidade imediata, clientes atendidos ou eficácia comprovada.
          </p>
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {exploring.map((offer) => (
              <article key={offer.title} className="rounded-lg border border-slate-200 bg-[#f5f8fa] p-6">
                <p className="text-xs font-black uppercase tracking-wide text-[#0a7f86]">{offer.label}</p>
                <h3 className="mt-3 text-xl font-black">{offer.title}</h3>
                <p className="mt-4 leading-7 text-slate-700">{offer.impact}</p>
                <p className="mt-4 text-sm leading-6 text-slate-600"><strong>Antes de oferecer:</strong> {offer.validate}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1120px] px-5 py-14 sm:px-8">
        <div className="flex gap-3 rounded-lg border border-[#18c8c0]/50 bg-[#eaf9f8] p-6">
          <ShieldCheck size={25} className="shrink-0 text-[#075c63]" aria-hidden="true" />
          <div>
            <h2 className="text-lg font-black">Segurança e finalidade definida</h2>
            <p className="mt-2 leading-7 text-slate-700">
              Não envie pacientes identificáveis, credenciais nem logs confidenciais em formulários públicos.
              Antes de analisar dados reais, definimos autorização, minimização, transferência segura, retenção e revisão humana.
              Serviços analíticos de manutenção não substituem avaliação regulatória de software destinado a fins médicos.
              <Link href="/ia-responsavel" className="mt-3 inline-flex items-center gap-2 font-bold text-[#075c63] underline underline-offset-4">
                Conheça nosso compromisso com IA responsável <ArrowRight size={16} aria-hidden="true" />
              </Link>
            </p>
          </div>
        </div>
        <div className="mt-10">
          <h2 className="text-2xl font-black">Quer discutir qual escopo faz sentido?</h2>
          <p className="mt-3 max-w-3xl leading-7 text-slate-700">Começamos entendendo a situação da operação e a qualidade dos dados disponíveis; não há necessidade de contratar uma plataforma antes dessa avaliação.</p>
          <Link href="/diagnostic" className="mt-5 inline-flex min-h-12 items-center gap-2 rounded-lg bg-[#071a3d] px-5 py-3 font-bold text-white hover:bg-[#0a7f86]">
            Conhecer o diagnóstico <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>
      <footer className="border-t border-slate-200 bg-white px-5 py-8 text-sm text-slate-600 sm:px-8">
        <div className="mx-auto max-w-[1120px]">© {new Date().getFullYear()} OPSPECTA · Inteligência operacional para a saúde. <Link href="/privacidade" className="ml-3 font-bold text-[#075c63] underline underline-offset-4">Privacidade e dados</Link></div>
      </footer>
    </main>
  );
}
