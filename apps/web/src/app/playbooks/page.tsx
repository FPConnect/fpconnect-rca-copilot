"use client";

import { useEffect, useMemo, useState } from "react";
import SearchBar from "@/components/SearchBar";
import { api, Playbook } from "@/services/api";

export default function PlaybooksPage() {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [search, setSearch] = useState("");
  const [title, setTitle] = useState("");
  const [equipment, setEquipment] = useState("");
  const [steps, setSteps] = useState("");

  useEffect(() => {
    api.getPlaybooks().then(setPlaybooks).catch(() => setPlaybooks([]));
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return playbooks.filter((p) => !q || p.title.toLowerCase().includes(q) || p.equipment.toLowerCase().includes(q));
  }, [playbooks, search]);

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!title || !equipment || !steps) return;
    const playbook = await api.createPlaybook({ title, equipment, steps, files: null });
    setPlaybooks((current) => [playbook, ...current]);
    setTitle(""); setEquipment(""); setSteps("");
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Procedimentos</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Playbooks de reparo</h1>
        <p className="mt-2 text-sm text-slate-600">Padronize ações de engenharia clínica por equipamento, com passos executáveis e arquivos de apoio.</p>
      </section>

      <form onSubmit={create} className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-[1fr_220px_1.5fr_auto]">
        <input aria-label="Título do playbook" placeholder="Título" value={title} onChange={(e) => setTitle(e.target.value)} className="rounded-lg border border-slate-300 px-4 py-2" />
        <input aria-label="Equipamento associado" placeholder="Equipamento associado" value={equipment} onChange={(e) => setEquipment(e.target.value)} className="rounded-lg border border-slate-300 px-4 py-2" />
        <input aria-label="Passos" placeholder="Passos do procedimento" value={steps} onChange={(e) => setSteps(e.target.value)} className="rounded-lg border border-slate-300 px-4 py-2" />
        <button className="rounded-lg bg-slate-900 px-5 py-2 font-semibold text-white">Adicionar</button>
      </form>

      <SearchBar placeholder="Pesquisar playbooks por título ou equipamento..." value={search} onChange={setSearch} className="w-96" />
      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map((playbook) => (
          <article key={playbook.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-bold text-slate-950">{playbook.title}</h2>
            <p className="mt-1 text-sm font-semibold text-blue-700">{playbook.equipment}</p>
            <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm text-slate-700">{playbook.steps}</pre>
            <p className="mt-3 text-xs text-slate-500">Arquivos: {playbook.files ?? "sem anexos"}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
