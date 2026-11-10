import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, BarChart3, FileSearch, ShieldCheck } from "lucide-react";
import BrandLogo from "@/components/BrandLogo";

export const metadata: Metadata = {
  title: "Demonstração de análise de OS | OPSPECTA",
  description: "Veja um exemplo inteiramente fictício de revisão de qualidade de ordens de serviço e identificação de gargalos operacionais MedTech.",
  alternates: { canonical: "/demonstracao" },
  openGraph: {
    title: "Demonstração educativa de análise de OS | OPSPECTA",
    description: "Um exemplo fictício mostra como campos ausentes e tempos de espera podem influenciar decisões operacionais.",
    url: "/demonstracao",
  },
};

const examples = [
  {
    id: "OS-001",
    asset: "Imagem-A12",
    issue: "Interrupção registrada durante teste",
    gap: "Motivo de espera não informado",
    level: "Revisar",
  },
  {
    id: "OS-002",
    asset: "Analisador-B04",
    issue: "Falha intermitente relatada",
    gap: "Teste realizado sem resultado documentado",
    level: "Revisar",
  },
  {
    id: "OS-003",
    asset: "Não preenchido",
    issue: "Indisponibilidade sem contexto",
    gap: "Identificador de ativo ausente",
    level: "Revisar",
  },
  {
    id: "OS-004",
    asset: "Imagem-C08",
    issue: "Alerta em investigação",
    gap: "Hipótese distinta da evidência, teste pendente",
    level: "Acompanhar",
  },
];

const checks = [
  { name: "Identificação do ativo", count: 3, total: 12, description: "3 registros não permitem vincular um ativo com segurança." },
  { name: "Motivo de espera", count: 5, total: 12, description: "5 registros não classificam por que o chamado permaneceu aberto." },
  { name: "Resultado do teste", count: 2, total: 12, description: "2 registros referem testes sem registrar seu resultado." },
];

export default function DemonstracaoPage() {
  return (
    <main className="brand-surface marketing-page min-h-screen bg-[#f5f8fa] text-[#071a3d]">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1120px] flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8">
          <Link href="/" aria-label="OPSPECTA início"><BrandLogo /></Link>
          <nav aria-label="Navegação de demonstração" className="flex flex-wrap gap-4 text-sm font-bold">
            <Link href="/solucoes" className="hover:text-[#0a7f86]">Soluções</Link>
            <Link href="/recursos" className="hover:text-[#0a7f86]">Checklist</Link>
            <Link href="/diagnostic" className="hover:text-[#0a7f86]">Diagnóstico</Link>
          </nav>
        </div>
      </header>
      <section className="marketing-hero bg-[#071a3d] px-5 py-16 text-white sm:px-8">
        <div className="mx-auto max-w-[1120px]">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#18c8c0]/70 px-4 py-2 text-sm font-black text-[#66efe5]">
            <FileSearch size={16} aria-hidden="true" /> Demonstrativo educativo · 100% fictício
          </div>
          <h1 className="mt-6 max-w-4xl text-3xl font-black leading-tight sm:text-5xl">O histórico de OS parece completo. Até você examinar os campos.</h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-200">
            Este é um cenário inventado com 12 registros. Ele ilustra como uma análise de qualidade dos dados pode apoiar
            uma equipe de serviço antes de calcular indicadores ou investigar reincidências.
            Não representa dados reais, funcionalidade automatizada em produção nem resultado entregue a clientes.
          </p>
        </div>
      </section>
      <section className="mx-auto max-w-[1120px] px-5 py-14 sm:px-8">
        <div className="flex items-center gap-2"><BarChart3 size={26} className="text-[#0a7f86]" aria-hidden="true" /><h2 className="text-2xl font-black sm:text-3xl">Pontos de atenção no exemplo</h2></div>
        <div className="mt-7 grid gap-4 sm:grid-cols-3">
          {checks.map((item) => (
            <article key={item.name} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-bold text-slate-600">{item.name}</p>
              <p className="mt-3 text-3xl font-black text-[#0a7f86]">{item.count}<span className="text-base font-semibold text-slate-500"> / {item.total} OS</span></p>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full rounded-full bg-[#0a7f86]" style={{ width: `${100 * item.count / item.total}%` }} />
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-700">{item.description}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="border-y border-slate-200 bg-white px-5 py-14 sm:px-8">
        <div className="mx-auto max-w-[1120px]">
          <h2 className="text-2xl font-black sm:text-3xl">Exemplos de registros que exigem revisão</h2>
          <p className="mt-3 text-slate-700">Entradas totalmente fictícias. Não constituem diagnósticos de equipamento nem instruções de manutenção.</p>
          <div className="mt-7 overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full min-w-[650px] text-left text-sm">
              <thead className="bg-[#eaf9f8] text-[#071a3d]">
                <tr><th className="p-4">Registro</th><th className="p-4">Ativo</th><th className="p-4">Descrição</th><th className="p-4">Pergunta de qualidade</th></tr>
              </thead>
              <tbody>
                {examples.map((entry) => (
                  <tr key={entry.id} className="border-t border-slate-200">
                    <td className="p-4 font-bold">{entry.id}</td>
                    <td className="p-4">{entry.asset}</td>
                    <td className="p-4">{entry.issue}</td>
                    <td className="p-4">{entry.gap}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-5 text-sm leading-7 text-slate-700">A lista acima mostra quatro exemplos da amostra fictícia de 12. As contagens do resumo são premissas ilustrativas criadas para esta demonstração; não são inferidas automaticamente das quatro linhas exibidas.</p>
        </div>
      </section>
      <section className="mx-auto max-w-[1120px] px-5 py-14 sm:px-8">
        <div className="flex gap-3 rounded-lg border border-[#18c8c0]/60 bg-[#eaf9f8] p-6">
          <ShieldCheck size={25} className="shrink-0 text-[#075c63]" aria-hidden="true" />
          <div>
            <h2 className="text-lg font-black">O que esse tipo de análise permite discutir?</h2>
            <p className="mt-3 leading-7 text-slate-700">
              Priorização de correções no registro; critérios para separar espera de intervenção;
              hipóteses de reincidência que ainda exigem confirmação; indicadores que podem
              ser interpretados com mais cuidado. Nada disso comprova automaticamente causa raiz,
              redução de paradas, economia ou segurança clínica.
            </p>
          </div>
        </div>
        <div className="mt-10 flex flex-wrap items-center justify-between gap-6">
          <div className="max-w-2xl">
            <h2 className="text-2xl font-black">Quer enquadrar sua própria base de OS?</h2>
            <p className="mt-3 leading-7 text-slate-700">
              O diagnóstico de entrada tem escopo limitado e depende de autorização dos dados,
              viabilidade técnica e proposta comercial. Não envie registros sensíveis por canais públicos.
            </p>
          </div>
          <Link href="/diagnostic" className="inline-flex min-h-12 items-center gap-2 rounded-lg bg-[#071a3d] px-5 py-3 font-bold text-white hover:bg-[#0a7f86]">
            Avaliar diagnóstico <ArrowRight size={18} aria-hidden="true" />
          </Link>
        </div>
      </section>
    </main>
  );
}
