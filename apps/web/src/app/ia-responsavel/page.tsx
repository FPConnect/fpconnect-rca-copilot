import type { Metadata } from "next";
import Link from "next/link";
import {
  Accessibility, ArrowRight, CircleCheck, Eye, Scale, ShieldCheck,
  LockKeyhole, UserRoundCheck, TriangleAlert,
} from "lucide-react";
import BrandLogo from "@/components/BrandLogo";

export const metadata: Metadata = {
  title: "IA responsável e revisão humana | OPSPECTA",
  description: "Como a OPSPECTA incorpora princípios de justiça, segurança, privacidade, inclusão, transparência e responsabilização no uso assistivo de IA.",
  alternates: { canonical: "/ia-responsavel" },
  openGraph: {
    title: "IA responsável | OPSPECTA",
    description: "Princípios, mecanismos técnicos adotados e pontos de validação pendentes.",
    url: "/ia-responsavel",
  },
};

const principles = [
  {
    title: "Fairness · Justiça",
    icon: Scale,
    approach: "Avaliar a qualidade dos dados, evitar o uso de atributos demográficos na priorização de equipamento e verificar resultados entre categorias relevantes de operação.",
    implemented: "A regra exploratória de prioridade usa somente histórico, data de manutenção e horas de operação; não utiliza características pessoais.",
    pending: "Ainda não há auditoria quantitativa de viés em bases reais autorizadas.",
  },
  {
    title: "Reliability and Safety · Confiabilidade e segurança",
    icon: ShieldCheck,
    approach: "Tratar saídas automatizadas como hipóteses, rejeitar entradas inválidas e não permitir que um número heurístico se apresente como probabilidade de falha.",
    implemented: "O fluxo de análise exige revisão antes de gravar uma conclusão, e o índice de prioridade não informa uma data prevista de falha.",
    pending: "Faltam avaliação prospectiva, testes com dados reais autorizados, limites operacionais específicos e validação externa.",
  },
  {
    title: "Privacy and Security · Privacidade e segurança",
    icon: LockKeyhole,
    approach: "Minimizar informações, usar autenticação e limitar chamadas externas. Não enviar registros de pacientes ou credenciais a serviços públicos.",
    implemented: "O uso de IA externa para RCA está desativado por padrão; eventual habilitação exige permissão do ambiente e manifestação explícita por solicitação. Logs de revisão registram metadados, não o texto dos chamados.",
    pending: "A detecção de informações sensíveis é parcial; qualquer implantação com dados reais exige avaliação de privacidade, testes de segurança e governança de retenção.",
  },
  {
    title: "Inclusiveness · Inclusão",
    icon: Accessibility,
    approach: "Usar linguagem compreensível, elementos navegáveis e informação que não dependa somente de cores; continuar melhorando português e inglês.",
    implemented: "Conteúdo explicativo, navegação por links e rótulos textuais das hipóteses nos fluxos revisados.",
    pending: "Não foi realizada auditoria WCAG completa com tecnologias assistivas e usuários de diferentes perfis.",
  },
  {
    title: "Transparency · Transparência",
    icon: Eye,
    approach: "Explicar a origem, limites e o significado real de índices e sugestões, sem prometer diagnósticos ou resultados não comprovados.",
    implemented: "A interface identifica hipóteses não confirmadas, a demonstração utiliza dados fictícios e o índice exploratório declara não ser previsão validada.",
    pending: "Explicações específicas de fontes e qualidade de evidência precisam evoluir conforme dados e casos de uso.",
  },
  {
    title: "Accountability · Responsabilização",
    icon: UserRoundCheck,
    approach: "Manter decisão técnica com profissional qualificado, restringir confirmação por permissão e registrar o responsável pela revisão.",
    implemented: "Confirmação de análise restrita a função autorizada, com evento de auditoria e marcação de revisão humana. Um usuário comum não pode confirmar causa pela atualização genérica do chamado.",
    pending: "Definir procedimento organizacional formal, gestão de incidentes de IA, prazos de retenção e auditoria independente.",
  },
];

export default function ResponsibleAiPage() {
  return (
    <main id="conteudo-principal" className="min-h-screen bg-[#f5f8fa] text-[#071a3d]">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1120px] flex-wrap items-center justify-between gap-5 px-5 py-5 sm:px-8">
          <Link href="/" aria-label="OPSPECTA página inicial"><BrandLogo /></Link>
          <nav aria-label="Navegação institucional" className="flex flex-wrap gap-4 text-sm font-bold">
            <Link href="/solucoes" className="hover:text-[#0a7f86]">Soluções</Link>
            <Link href="/recursos" className="hover:text-[#0a7f86]">Checklist</Link>
            <Link href="/diagnostic" className="hover:text-[#0a7f86]">Diagnóstico</Link>
          </nav>
        </div>
      </header>
      <section className="bg-[#071a3d] px-5 py-16 text-white sm:px-8">
        <div className="mx-auto max-w-[1120px]">
          <p className="text-sm font-black uppercase tracking-wide text-[#66efe5]">Princípios de desenvolvimento e governança</p>
          <h1 className="mt-5 max-w-4xl text-4xl font-black leading-tight sm:text-5xl">IA responsável na OPSPECTA</h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-200">
            Tratamos dados operacionais de serviços MedTech como evidências para investigação e revisão humana,
            não como autorização para diagnóstico clínico, intervenção física ou conclusão automática de causa raiz.
          </p>
          <div className="mt-7 flex max-w-3xl gap-3 rounded-lg border border-[#5ee9e0]/50 bg-white/10 p-5 text-sm leading-7">
            <TriangleAlert size={23} className="mt-1 shrink-0 text-[#66efe5]" aria-hidden="true" />
            <p><strong>Atenção:</strong> estes são princípios e controles em implantação, não certificação, auditoria independente ou demonstração de conformidade integral com normas. Resultados e aplicações exigem verificação por caso de uso.</p>
          </div>
        </div>
      </section>
      <section className="mx-auto max-w-[1120px] px-5 py-14 sm:px-8" aria-labelledby="principles-title">
        <h2 id="principles-title" className="text-3xl font-black">Os seis princípios e seu estágio de aplicação</h2>
        <p className="mt-4 max-w-3xl leading-7 text-slate-700">
          Nossa organização dos princípios acompanha o referencial público da Microsoft de IA responsável.
          O referencial orienta a análise; não implica parceria ou endosso da Microsoft.
        </p>
        <div className="mt-8 grid gap-5 md:grid-cols-2">
          {principles.map((p) => (
            <article key={p.title} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <p.icon size={25} className="shrink-0 text-[#0a7f86]" aria-hidden="true" />
                <h3 className="text-xl font-black">{p.title}</h3>
              </div>
              <p className="mt-4 leading-7 text-slate-700">{p.approach}</p>
              <div className="mt-5 rounded-lg bg-[#eaf9f8] p-4">
                <p className="flex items-center gap-2 text-sm font-black text-[#075c63]"><CircleCheck size={16} aria-hidden="true" /> Controle desenvolvido no código</p>
                <p className="mt-2 text-sm leading-6 text-slate-700">{p.implemented}</p>
              </div>
              <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
                <p className="text-sm font-black text-amber-900">Validação pendente</p>
                <p className="mt-2 text-sm leading-6 text-amber-900">{p.pending}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="border-y border-slate-200 bg-white px-5 py-12 sm:px-8">
        <div className="mx-auto max-w-[1120px]">
          <h2 className="text-2xl font-black">Fontes e limites de uso</h2>
          <p className="mt-4 max-w-3xl leading-7 text-slate-700">
            Os princípios são baseados em orientações públicas. As funções de apoio analítico da OPSPECTA
            não foram validadas para prever falha de equipamento médico, determinar causalidade clínica,
            liberar dispositivos ou substituir as responsabilidades de profissionais e fabricantes.
          </p>
          <ul className="mt-5 list-disc space-y-2 pl-6 text-sm text-[#075c63]">
            <li><a href="https://www.microsoft.com/en-us/ai/principles-and-approach" target="_blank" rel="noopener noreferrer" className="font-semibold underline underline-offset-4">Microsoft — Responsible AI principles</a></li>
            <li><a href="https://airc.nist.gov/airmf-resources/playbook/" target="_blank" rel="noopener noreferrer" className="font-semibold underline underline-offset-4">NIST — AI Risk Management Framework Playbook</a></li>
          </ul>
          <Link href="/solucoes" className="mt-8 inline-flex min-h-12 items-center gap-2 rounded-lg bg-[#071a3d] px-5 py-3 font-bold text-white hover:bg-[#0a7f86]">
            Conhecer soluções OPSPECTA <ArrowRight size={17} aria-hidden="true" />
          </Link>
        </div>
      </section>
    </main>
  );
}
