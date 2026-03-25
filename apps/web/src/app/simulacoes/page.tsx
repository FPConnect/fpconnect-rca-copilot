import Link from "next/link";
import { ArrowRight, Brain, Radar, ShieldAlert, WalletCards } from "lucide-react";

const simulationSteps = [
  {
    title: "1. Abrir com dor operacional",
    description:
      "Comece em Tickets para mostrar fila crítica, escalonamento e decisão rápida em equipamentos sensíveis.",
    href: "/tickets",
    cta: "Abrir tickets",
    icon: ShieldAlert,
  },
  {
    title: "2. Conectar com inteligência externa",
    description:
      "Leve a conversa para Radar e demonstre como recalls, alertas e sinais públicos entram no contexto operacional.",
    href: "/intel",
    cta: "Abrir radar",
    icon: Radar,
  },
  {
    title: "3. Abrir o centro de simulacao total",
    description:
      "Mostre o produto inteiro operando com cenarios plausiveis, relatarios exportaveis e material de pos-venda em um unico ambiente.",
    href: "/agent",
    cta: "Abrir centro de simulacao",
    icon: Brain,
  },
  {
    title: "4. Fechar em ROI e expansão",
    description:
      "Finalize em Demo Recursos ou Métricas para defender expansão de contrato, previsibilidade e redução de downtime.",
    href: "/demo-recursos",
    cta: "Abrir demo de recursos",
    icon: WalletCards,
  },
];

const prompts = [
  "Quais tickets parecem mais críticos hoje e por quê?",
  "Se eu fosse diretor clínico, o que deveria escalar agora?",
  "Quais modulos do software o cliente passa a usar na primeira semana?",
  "Como justificar economicamente ampliar a cobertura preditiva?",
];

export default function SimulacoesPage() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6 rounded-3xl border border-cyan-200 bg-gradient-to-r from-slate-950 via-blue-950 to-cyan-900 p-8 text-white shadow-sm">
        <div className="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-100">
          Novo formato de demo
        </div>
        <h2 className="mt-4 text-3xl font-bold leading-tight">
          Abra a demo institucional autoplay com cursor guiado, explicação de métricas e narração pronta para apresentação.
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-200">
          Essa versão funciona como um vídeo institucional interativo dentro do software e foi desenhada para uso em reuniões com clientes.
        </p>
        <Link
          href="/demo-institucional"
          className="mt-5 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 hover:bg-slate-100"
        >
          Abrir demo institucional
          <ArrowRight size={16} />
        </Link>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
          Roteiro de simulação comercial
        </div>
        <h1 className="mt-4 text-3xl font-bold text-slate-900">
          Trilha pronta para demonstrar valor em reuniões de venda
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-600">
          Esta sequência foi organizada para você conduzir uma conversa clara: problema, contexto, inteligência, ação assistida e impacto financeiro. Cada etapa abre uma tela já preparada para simulação no ambiente online.
        </p>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {simulationSteps.map(({ title, description, href, cta, icon: Icon }) => (
          <div key={href} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
                <Icon size={20} />
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p>
                <Link href={href} className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-700 hover:text-blue-800">
                  {cta}
                  <ArrowRight size={16} />
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
        <h2 className="text-lg font-semibold text-emerald-900">Perguntas prontas para usar na demonstração</h2>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          {prompts.map((prompt) => (
            <div key={prompt} className="rounded-xl border border-emerald-100 bg-white px-4 py-3 text-sm text-slate-700">
              {prompt}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}