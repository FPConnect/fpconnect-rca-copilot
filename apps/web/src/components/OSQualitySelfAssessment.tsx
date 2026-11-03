"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, CheckSquare2 } from "lucide-react";

const questions = [
  "Identificador do equipamento consistente e rastreável",
  "Datas de abertura, atendimento e conclusão utilizáveis",
  "Sintoma registrado como observação, não como causa confirmada",
  "Hipótese distinta da evidência que a sustenta",
  "Testes e resultados documentados de forma verificável",
  "Espera por peças, acesso e aprovações distinguível do reparo",
  "Encerramento com situação e pendências identificáveis",
  "Relação com atendimentos anteriores registrada quando pertinente",
];

export default function OSQualitySelfAssessment() {
  const [answers, setAnswers] = useState<boolean[]>(() => questions.map(() => false));
  const total = answers.filter(Boolean).length;

  return (
    <section aria-labelledby="autoteste-title" className="border-y border-slate-200 bg-white px-5 py-14 sm:px-8">
      <div className="mx-auto max-w-[1080px]">
        <div className="flex items-center gap-2">
          <CheckSquare2 className="text-[#0a7f86]" size={25} aria-hidden="true" />
          <h2 id="autoteste-title" className="text-2xl font-black sm:text-3xl">Autoavaliação rápida</h2>
        </div>
        <p className="mt-4 max-w-3xl leading-7 text-slate-700">
          Marque apenas os campos que sua equipe consegue verificar na maioria das OS amostradas.
          O resultado é uma triagem educativa; não representa auditoria nem conformidade normativa.
          Nenhuma informação digitada ou marcada aqui é enviada à OPSPECTA.
        </p>
        <div className="mt-8 grid gap-3 md:grid-cols-2">
          {questions.map((q, i) => (
            <label key={q} className="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 bg-[#f4f8fa] p-4 text-sm font-semibold leading-6">
              <input
                type="checkbox"
                checked={answers[i]}
                onChange={(event) => {
                  setAnswers((old) => old.map((value, j) => j === i ? event.target.checked : value));
                }}
                className="mt-1 h-5 w-5 shrink-0 accent-[#0a7f86]"
              />
              <span>{q}</span>
            </label>
          ))}
        </div>
        <div className="mt-7 rounded-lg bg-[#eaf9f8] p-6" aria-live="polite" aria-atomic="true">
          <p className="text-xs font-black uppercase tracking-wide text-[#075c63]">Itens verificados</p>
          <p className="mt-2 text-3xl font-black">{total} de {questions.length}</p>
          <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200" aria-hidden="true">
            <div className="h-full bg-[#0a7f86] transition-all" style={{ width: `${(total / questions.length) * 100}%` }} />
          </div>
          <p className="mt-4 text-sm leading-7 text-slate-700">
            {total < 4
              ? "Há várias lacunas que podem limitar a interpretação do histórico. Comece pela padronização dos registros."
              : total < 7
                ? "Há uma base inicial, mas as lacunas restantes podem distorcer indicadores e análise de reincidências."
                : "A maioria dos itens básicos foi verificada. Ainda é necessário testar consistência, amostra, finalidade e critérios técnicos antes de concluir."}
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button type="button" onClick={() => setAnswers(questions.map(() => false))} className="min-h-11 rounded-lg border border-[#0a7f86] px-4 py-2 font-bold text-[#075c63] hover:bg-white">
              Limpar respostas
            </button>
            <Link href="/diagnostic" className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-[#071a3d] px-4 py-2 font-bold text-white hover:bg-[#0a7f86]">
              Conhecer diagnóstico <ArrowRight size={16} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
