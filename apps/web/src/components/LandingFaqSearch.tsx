"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";

const FAQ_ITEMS = [
  {
    question: "Como cadastrar um novo equipamento?",
    answer: "Acesse o menu Máquinas e clique em 'Novo Equipamento'.",
  },
  {
    question: "Como visualizar alertas?",
    answer: "Clique no ícone de sino no cabeçalho para ver todos os alertas.",
  },
  {
    question: "Como gerar relatórios?",
    answer: "Acesse o menu Métricas e selecione o período desejado.",
  },
  {
    question: "Como abrir um chamado?",
    answer: "Vá em Tickets e clique em 'Novo Ticket'.",
  },
  {
    question: "Como configurar notificações?",
    answer: "Acesse Configurações > Notificações para personalizar.",
  },
];

export default function LandingFaqSearch() {
  const [query, setQuery] = useState("");

  const filteredFaqs = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return FAQ_ITEMS;

    return FAQ_ITEMS.filter((item) => {
      const content = `${item.question} ${item.answer}`.toLowerCase();
      return content.includes(normalizedQuery);
    });
  }, [query]);

  return (
    <div className="space-y-4">
      <label className="relative block">
        <span className="sr-only">Buscar nas FAQs...</span>
        <Search
          size={18}
          className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
          aria-hidden="true"
        />
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Buscar nas FAQs..."
          className="w-full rounded-xl border border-slate-700 bg-slate-950/70 py-3 pl-11 pr-4 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-400/20"
        />
      </label>

      <div className="grid gap-3 md:grid-cols-2">
        {filteredFaqs.length > 0 ? (
          filteredFaqs.map((item) => (
            <article key={item.question} className="rounded-xl border border-slate-700 bg-slate-950/60 p-4">
              <h3 className="text-sm font-black text-white">{item.question}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{item.answer}</p>
            </article>
          ))
        ) : (
          <p className="rounded-xl border border-slate-700 bg-slate-950/60 p-4 text-sm text-slate-300">
            Nenhuma pergunta encontrada.
          </p>
        )}
      </div>
    </div>
  );
}
