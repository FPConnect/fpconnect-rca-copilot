import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ClipboardCheck, FileSearch, ShieldCheck } from "lucide-react";
import BrandLogo from "@/components/BrandLogo";

export const metadata: Metadata = {
  title: "Checklist de qualidade de ordens de serviço | OPSPECTA",
  description:
    "Checklist gratuito para avaliar a qualidade de registros de manutenção MedTech, distinguir fatos de hipóteses e preparar uma análise operacional responsável.",
  alternates: { canonical: "/recursos" },
  openGraph: {
    title: "Checklist gratuito de OS | OPSPECTA",
    description: "Oito verificações práticas para tornar históricos de serviço mais úteis e rastreáveis.",
    url: "/recursos",
  },
};

const checklist = [
  {
    title: "1. Identificação do ativo",
    detail: "A OS identifica um equipamento e sua categoria de forma consistente, com um código interno confiável? Evite dados pessoais desnecessários.",
  },
  {
    title: "2. Linha do tempo verificável",
    detail: "Abertura, chegada, diagnóstico, início/fim do reparo e encerramento têm datas e horários válidos? Campos ausentes são explicitados?",
  },
  {
    title: "3. Sintoma descrito como observação",
    detail: "A descrição informa o que foi observado, em qual condição e com qual mensagem/código, sem confundir hipótese com causa confirmada?",
  },
  {
    title: "4. Hipótese separada da evidência",
    detail: "A possível causa está identificada como hipótese quando ainda não há teste ou evidência suficiente para confirmá-la?",
  },
  {
    title: "5. Ações e testes registrados",
    detail: "É possível saber que teste foi executado, por quem, em qual contexto e com qual resultado, sem divulgar credenciais ou dados de pacientes?",
  },
  {
    title: "6. Esperas classificadas",
    detail: "Tempo aguardando peça, aprovação, acesso, suporte remoto e outros bloqueios está diferenciado do tempo de intervenção técnica?",
  },
  {
    title: "7. Encerramento com resultado",
    detail: "Consta o resultado final (resolvido, monitorar, encaminhado ou não reproduzido), os critérios de validação e os pendentes?",
  },
  {
    title: "8. Recorrências rastreáveis",
    detail: "Há vínculo possível com atendimentos anteriores do mesmo ativo, distinguindo retorno técnico de um novo problema independente?",
  },
];

export default function RecursosPage() {
  return (
    <main className="min-h-screen bg-[#f4f8fa] text-[#071a3d]">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1080px] flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8">
          <Link href="/" aria-label="Voltar à página inicial da OPSPECTA">
            <BrandLogo />
          </Link>
          <nav aria-label="Recursos e contato" className="flex flex-wrap items-center gap-4 text-sm font-semibold">
            <Link className="hover:text-[#0a7f86]" href="/">Início</Link>
            <Link className="hover:text-[#0a7f86]" href="/diagnostic">Diagnóstico</Link>
          </nav>
        </div>
      </header>

      <section className="bg-white px-5 py-14 sm:px-8">
        <div className="mx-auto max-w-[1080px]">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#18c8c0] bg-[#e8fbf9] px-4 py-2 text-sm font-bold text-[#075c63]">
            <ClipboardCheck size={17} aria-hidden="true" />
            Recurso gratuito · OPSPECTA
          </div>
          <h1 className="mt-6 max-w-4xl text-3xl font-black leading-tight sm:text-5xl">
            Sua ordem de serviço está pronta para gerar inteligência operacional?
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-700">
            Oito verificações para avaliar a consistência de registros técnicos antes de calcular
            MTTR, investigar reincidências ou construir dashboards.
          </p>
          <p className="mt-5 max-w-3xl rounded-lg border-l-4 border-[#0a7f86] bg-[#f4f8fa] px-5 py-4 text-sm leading-7 text-slate-700">
            Este material é educativo e não substitui manutenção, análise técnica, normas dos
            fabricantes ou validação por profissionais responsáveis. Não compartilhe dados de pacientes,
            credenciais ou informações confidenciais em formulários públicos.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-[1080px] px-5 py-14 sm:px-8" aria-labelledby="checklist-title">
        <div className="flex items-center gap-3">
          <FileSearch className="text-[#0a7f86]" size={26} aria-hidden="true" />
          <h2 id="checklist-title" className="text-2xl font-black sm:text-3xl">Checklist de qualidade de OS</h2>
        </div>
        <p className="mt-3 text-slate-700">Use cada pergunta como critério de revisão. Registre exemplos de inconsistência sem expor informações sensíveis.</p>
        <ol className="mt-8 grid list-none gap-4 md:grid-cols-2">
          {checklist.map((item) => (
            <li key={item.title} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-bold">{item.title}</h3>
              <p className="mt-3 leading-7 text-slate-700">{item.detail}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="border-y border-slate-200 bg-white px-5 py-12 sm:px-8">
        <div className="mx-auto max-w-[1080px]">
          <h2 className="text-2xl font-black">Exemplo de avaliação (ilustrativo)</h2>
          <p className="mt-4 max-w-3xl leading-7 text-slate-700">
            Em uma amostra hipotética de 100 OS, se 30 não registram o motivo da espera,
            a primeira decisão não é afirmar que o reparo foi lento: é qualificar esse dado,
            definir o campo obrigatório e validar a diferença entre tempo de intervenção e tempo parado.
            Nenhum número deste exemplo representa um cliente ou resultado da OPSPECTA.
          </p>
        </div>
      </section>

      <section className="bg-[#071a3d] px-5 py-14 text-white sm:px-8">
        <div className="mx-auto flex max-w-[1080px] flex-col items-start gap-5 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[#43e2d9]"><ShieldCheck size={19} aria-hidden="true" /><span className="text-sm font-bold uppercase">Próximo passo</span></div>
            <h2 className="mt-3 text-2xl font-black">Quer avaliar os registros reais da sua operação?</h2>
            <p className="mt-2 max-w-2xl text-slate-200">Conheça o escopo do diagnóstico remoto da OPSPECTA, sujeito à validação de dados, segurança e proposta.</p>
          </div>
          <Link href="/diagnostic" className="inline-flex min-h-12 shrink-0 items-center gap-2 rounded-lg bg-[#18c8c0] px-5 py-3 font-bold text-[#071a3d] hover:bg-[#3addd7]">
            Ver diagnóstico <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>
      <footer className="mx-auto max-w-[1080px] px-5 py-8 text-sm text-slate-600 sm:px-8">
        © {new Date().getFullYear()} OPSPECTA · Inteligência operacional para a saúde.
      </footer>
    </main>
  );
}
