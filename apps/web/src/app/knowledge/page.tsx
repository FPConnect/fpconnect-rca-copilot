"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { BookOpenCheck, CheckCircle2, FilePlus2, Filter, LockKeyhole, ShieldCheck } from "lucide-react";

import AccessGuard from "@/components/AccessGuard";
import { useAuth } from "@/contexts/AuthContext";
import {
  api,
  type KnowledgeArticle,
  type KnowledgeArticleDraft,
  type KnowledgeCategory,
  type KnowledgeFilters,
  type KnowledgeLegacy,
  type KnowledgeWorkspace,
} from "@/services/api";

const categoryLabels: Record<KnowledgeCategory, string> = {
  operations: "Operações e indicadores",
  equipment: "Equipamentos e ativos",
  connectivity: "Conectividade",
  software: "Software",
  quality: "Qualidade e rastreabilidade",
  documentation: "Documentação",
  other: "Outros",
};
const visibilityLabels: Record<string, string> = {
  private: "Privado",
  workspace: "Organização autorizada",
  global: "Compartilhado após revisão",
};
const statusLabels: Record<string, string> = {
  draft: "Rascunho",
  in_review: "Aguardando revisão",
  approved: "Aprovado",
  rejected: "Reprovado",
  archived: "Arquivado",
};

const emptyDraft: KnowledgeArticleDraft = {
  title: "",
  content: "",
  category: "operations",
  tags: [],
  visibility: "private",
  workspace_id: null,
  equipment_family: "",
  manufacturer: "",
  model_code: "",
  failure_code: "",
  source_ref: "",
};

const emptyFilters = {
  q: "", category: "", workspace_id: "", visibility: "", review_status: "",
  manufacturer: "", equipment_family: "", failure_code: "", tag: "",
};

type View = "acervo" | "novo" | "revisao" | "administracao";

function friendlyError(error: unknown) {
  if (error instanceof Error) {
    try {
      const json = JSON.parse(error.message);
      if (typeof json.detail === "string") return json.detail;
    } catch { /* API may return plain text */ }
  }
  return "Não foi possível concluir a operação. Verifique suas permissões e tente novamente.";
}

function KBPageContent() {
  const { user } = useAuth();
  const isAdmin = (user?.access_level ?? 0) >= 4;
  const [view, setView] = useState<View>("acervo");
  const [filters, setFilters] = useState<Record<string, string>>(emptyFilters);
  const [metadata, setMetadata] = useState<KnowledgeFilters | null>(null);
  const [workspaces, setWorkspaces] = useState<KnowledgeWorkspace[]>([]);
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [reviewQueue, setReviewQueue] = useState<KnowledgeArticle[]>([]);
  const [legacy, setLegacy] = useState<KnowledgeLegacy[]>([]);
  const [draft, setDraft] = useState<KnowledgeArticleDraft>(emptyDraft);
  const [tagsInput, setTagsInput] = useState("");
  const [workspaceSlug, setWorkspaceSlug] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [membershipWorkspace, setMembershipWorkspace] = useState("");
  const [membershipUser, setMembershipUser] = useState("");
  const [memberRole, setMemberRole] = useState<"member" | "manager">("member");
  const [legacyOwner, setLegacyOwner] = useState("");
  const [legacyCategory, setLegacyCategory] = useState<KnowledgeCategory>("documentation");
  const [legacyWorkspace, setLegacyWorkspace] = useState("");
  const [reviewAttested, setReviewAttested] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadArticles = useCallback(async (params: Record<string, string>) => {
    const rows = await api.getKnowledgeArticles(params);
    setArticles(rows);
  }, []);

  const loadMeta = useCallback(async () => {
    const [meta, spaces] = await Promise.all([
      api.getKnowledgeFilters(), api.getKnowledgeWorkspaces(),
    ]);
    setMetadata(meta);
    setWorkspaces(spaces);
  }, []);

  const loadAdmin = useCallback(async () => {
    if (!isAdmin) return;
    const [queue, old] = await Promise.all([
      api.getKnowledgeReviewQueue(), api.getLegacyKnowledge(),
    ]);
    setReviewQueue(queue);
    setLegacy(old);
  }, [isAdmin]);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        await Promise.all([loadMeta(), loadArticles(emptyFilters)]);
        if (isAdmin) await loadAdmin();
      } catch (err) {
        if (alive) setError(friendlyError(err));
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [isAdmin, loadMeta, loadArticles, loadAdmin]);

  async function refresh() {
    await Promise.all([loadMeta(), loadArticles(filters), ...(isAdmin ? [loadAdmin()] : [])]);
  }

  async function runAction(operation: () => Promise<unknown>, success: string) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await operation();
      await refresh();
      setMessage(success);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setBusy(false);
    }
  }

  async function search(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await loadArticles(filters);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setBusy(false);
    }
  }

  async function saveDraft(event: FormEvent) {
    event.preventDefault();
    const tags = tagsInput.split(/[,;]+/).map((x) => x.trim()).filter(Boolean);
    await runAction(
      () => api.createKnowledgeArticle({ ...draft, tags }),
      "Artigo salvo como rascunho privado até sua revisão. Nenhuma publicação foi automática.",
    );
    setView("acervo");
    setDraft(emptyDraft);
    setTagsInput("");
  }

  async function manageWorkspace(event: FormEvent) {
    event.preventDefault();
    await runAction(
      () => api.createKnowledgeWorkspace({ name: workspaceName.trim(), slug: workspaceSlug.trim() }),
      "Espaço de trabalho criado com acesso administrativo explícito.",
    );
    setWorkspaceName("");
    setWorkspaceSlug("");
  }

  async function addWorkspaceMember(event: FormEvent) {
    event.preventDefault();
    await runAction(
      () => api.addKnowledgeMember(Number(membershipWorkspace), Number(membershipUser), memberRole),
      "Acesso ao espaço de trabalho concedido ao usuário selecionado.",
    );
    setMembershipUser("");
  }

  const field = (key: keyof typeof emptyFilters, label: string) => (
    <label className="block text-sm font-semibold text-slate-700" key={key}>
      {label}
      <input
        type="text"
        value={filters[key]}
        onChange={(e) => setFilters((old) => ({ ...old, [key]: e.target.value }))}
        className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
      />
    </label>
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-12">
      <header className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="flex items-center gap-2 text-sm font-bold uppercase text-[#075c63]">
          <BookOpenCheck size={18} /> OPSPECTA · Acervo técnico
        </p>
        <h1 className="mt-2 text-3xl font-black text-[#071a3d]">Base de conhecimento</h1>
        <p className="mt-3 max-w-4xl leading-7 text-slate-700">
          Artigos separados por proprietário e organização, com categorias, etiquetas e
          aprovação humana antes do compartilhamento. Registros históricos sem
          autorização documentada permanecem em quarentena e fora das consultas.
        </p>
        <p className="mt-3 flex items-start gap-2 text-sm leading-6 text-amber-900">
          <LockKeyhole size={17} className="mt-0.5 shrink-0" />
          Não insira dados de pacientes, credenciais, imagens clínicas identificáveis
          ou documentos de terceiros sem autorização, finalidade e canal seguro.
        </p>
      </header>

      <nav aria-label="Áreas da base de conhecimento" className="flex flex-wrap gap-2">
        {([
          ["acervo", "Pesquisar acervo"],
          ["novo", "Novo artigo"],
          ...(isAdmin ? ([["revisao", "Fila de revisão"], ["administracao", "Organizações e legado"]] as const) : []),
        ] as const).map(([key, title]) => (
          <button key={key} type="button" onClick={() => setView(key)}
            aria-current={view === key ? "page" : undefined}
            className={`min-h-11 rounded-lg px-4 py-2 text-sm font-bold ${view === key
              ? "bg-[#071a3d] text-white"
              : "border border-slate-300 bg-white text-[#071a3d] hover:bg-slate-100"}`}>
            {title}
          </button>
        ))}
      </nav>

      {error && <div role="alert" className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm font-semibold text-red-900">{error}</div>}
      {message && <div role="status" className="rounded-lg border border-emerald-300 bg-emerald-50 p-4 text-sm font-semibold text-emerald-900">{message}</div>}

      {view === "acervo" && (
        <>
          <form onSubmit={search} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="flex items-center gap-2 text-xl font-black"><Filter size={20} /> Filtrar conhecimento autorizado</h2>
            <div className="mt-5 grid gap-4 md:grid-cols-3">
              {field("q", "Pesquisar título, conteúdo e tags")}
              <label className="text-sm font-semibold">Categoria
                <select value={filters.category} onChange={(e) => setFilters((x) => ({ ...x, category: e.target.value }))}
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
                  <option value="">Todas</option>
                  {metadata?.categories.map((c) => <option key={c} value={c}>{categoryLabels[c]}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold">Organização autorizada
                <select value={filters.workspace_id} onChange={(e) => setFilters((x) => ({ ...x, workspace_id: e.target.value }))}
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
                  <option value="">Todas as acessíveis</option>
                  {workspaces.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold">Visibilidade
                <select value={filters.visibility} onChange={(e) => setFilters((x) => ({ ...x, visibility: e.target.value }))}
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
                  <option value="">Todas</option>
                  {metadata?.visibilities.map((c) => <option key={c} value={c}>{visibilityLabels[c]}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold">Revisão
                <select value={filters.review_status} onChange={(e) => setFilters((x) => ({ ...x, review_status: e.target.value }))}
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2">
                  <option value="">Todas</option>
                  {metadata?.review_statuses.map((c) => <option key={c} value={c}>{statusLabels[c] ?? c}</option>)}
                </select>
              </label>
              {field("manufacturer", "Fabricante")}
              {field("equipment_family", "Família de equipamento")}
              {field("failure_code", "Código de falha")}
              {field("tag", "Etiqueta exata")}
            </div>
            <div className="mt-5 flex flex-wrap gap-3">
              <button type="submit" disabled={busy} className="min-h-11 rounded-lg bg-[#071a3d] px-5 py-2 font-bold text-white hover:bg-[#0a7f86] disabled:opacity-50">
                Aplicar filtros
              </button>
              <button type="button" onClick={() => {
                setFilters(emptyFilters);
                void runAction(() => loadArticles(emptyFilters), "Filtros limpos.");
              }} className="min-h-11 rounded-lg border border-slate-300 px-5 py-2 font-bold">Limpar filtros</button>
            </div>
          </form>

          <section aria-labelledby="kb-results" className="space-y-4">
            <h2 id="kb-results" className="text-xl font-black">Artigos permitidos ({articles.length})</h2>
            {loading && <p role="status" className="text-sm text-slate-600">Carregando base de conhecimento...</p>}
            {!loading && articles.length === 0 && (
              <div className="rounded-lg border border-slate-200 bg-white p-7 text-sm text-slate-700">
                Nenhum artigo autorizado corresponde aos filtros. Artigos antigos podem estar em quarentena,
                e o conteúdo compartilhado depende de revisão formal.
              </div>
            )}
            {articles.map((article) => (
              <article key={article.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-black uppercase text-[#075c63]">{categoryLabels[article.category] || article.category}</p>
                    <h3 className="mt-2 text-xl font-black text-[#071a3d]">{article.title}</h3>
                    <p className="mt-2 text-sm text-slate-600">
                      {visibilityLabels[article.visibility]} · {statusLabels[article.review_status] ?? article.review_status} · versão {article.version}
                    </p>
                  </div>
                  {article.review_status === "approved" && <span className="flex items-center gap-1 text-sm font-semibold text-[#075c63]"><CheckCircle2 size={16}/> Revisado</span>}
                </div>
                <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-700">{article.content.slice(0, 500)}{article.content.length > 500 ? "…" : ""}</p>
                <p className="mt-3 text-xs text-slate-600">
                  {[article.manufacturer, article.equipment_family, article.model_code, article.failure_code].filter(Boolean).join(" · ")}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {article.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-[#eaf9f8] px-3 py-1 text-xs font-bold text-[#075c63]">#{tag}</span>
                  ))}
                </div>
                <details className="mt-4 rounded-lg border border-slate-200 p-3">
                  <summary className="cursor-pointer text-sm font-bold text-[#075c63]">Ler artigo completo</summary>
                  <p className="mt-4 whitespace-pre-wrap text-sm leading-7">{article.content}</p>
                  {article.source_ref && <p className="mt-3 text-xs text-slate-600">Referência declarada: {article.source_ref}</p>}
                </details>
                {article.owner_id === user?.id && ["draft", "rejected"].includes(article.review_status) && (
                  <button type="button" disabled={busy} onClick={() => {
                    void runAction(() => api.submitKnowledgeArticle(article.id), "Artigo submetido para avaliação independente.");
                  }} className="mt-4 min-h-10 rounded-lg border border-[#0a7f86] px-4 py-2 text-sm font-bold text-[#075c63] disabled:opacity-40">
                    Enviar para revisão
                  </button>
                )}
              </article>
            ))}
          </section>
        </>
      )}

      {view === "novo" && (
        <form onSubmit={saveDraft} className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="flex items-center gap-2 text-2xl font-black"><FilePlus2 size={22}/> Registrar conhecimento</h2>
          <p className="text-sm leading-6 text-slate-700">Todo novo artigo nasce como rascunho. Qualquer compartilhamento exige revisão independente e autorização.</p>
          <label className="block text-sm font-bold">Título
            <input required minLength={5} maxLength={220} value={draft.title} onChange={(e) => setDraft((x) => ({...x, title:e.target.value}))}
              className="mt-2 w-full rounded-lg border border-slate-300 p-3"/>
          </label>
          <label className="block text-sm font-bold">Conteúdo técnico autorizado
            <textarea required minLength={15} maxLength={20000} rows={9} value={draft.content} onChange={(e) => setDraft((x) => ({ ...x, content:e.target.value }))}
              className="mt-2 w-full rounded-lg border border-slate-300 p-3"/>
          </label>
          <div className="grid gap-4 md:grid-cols-3">
            <label className="text-sm font-bold">Categoria
              <select className="mt-2 w-full rounded-lg border border-slate-300 p-3"
                value={draft.category} onChange={(e) => setDraft((x) => ({...x,category:e.target.value as KnowledgeCategory}))}>
                {Object.entries(categoryLabels).map(([id, name]) => <option key={id} value={id}>{name}</option>)}
              </select>
            </label>
            <label className="text-sm font-bold">Visibilidade planejada
              <select className="mt-2 w-full rounded-lg border border-slate-300 p-3"
                value={draft.visibility} onChange={(e) => setDraft((x) => ({
                  ...x, visibility:e.target.value as KnowledgeArticleDraft["visibility"], workspace_id:null,
                }))}>
                <option value="private">Privado</option>
                <option value="workspace">Organização autorizada</option>
                <option value="global">Global, sujeito a aprovação</option>
              </select>
            </label>
            {draft.visibility === "workspace" && (
              <label className="text-sm font-bold">Organização
                <select required className="mt-2 w-full rounded-lg border border-slate-300 p-3"
                  value={draft.workspace_id ?? ""} onChange={(e) => setDraft((x) => ({
                    ...x, workspace_id:e.target.value ? Number(e.target.value) : null,
                  }))}>
                  <option value="">Selecione sua organização</option>
                  {workspaces.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
                </select>
              </label>
            )}
            {([
              ["manufacturer", "Fabricante"],
              ["equipment_family", "Família de equipamento"],
              ["model_code", "Modelo"],
              ["failure_code", "Código de falha"],
              ["source_ref", "Referência interna autorizada"],
            ] as const).map(([key, label]) => (
              <label key={key} className="text-sm font-bold">{label}
                <input maxLength={key === "source_ref" ? 240 : 100} value={draft[key] ?? ""}
                  onChange={(e) => setDraft((x) => ({ ...x, [key]: e.target.value }))}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3"/>
              </label>
            ))}
            <label className="text-sm font-bold">Etiquetas (separadas por vírgula)
              <input maxLength={420} value={tagsInput} onChange={(e) => setTagsInput(e.target.value)}
                placeholder="recorrencia, analise-de-os" className="mt-2 w-full rounded-lg border border-slate-300 p-3"/>
            </label>
          </div>
          <button disabled={busy} type="submit" className="min-h-12 rounded-lg bg-[#071a3d] px-6 py-3 font-bold text-white disabled:opacity-50">
            Salvar rascunho
          </button>
        </form>
      )}

      {isAdmin && view === "revisao" && (
        <section className="space-y-4">
          <h2 className="text-2xl font-black">Fila de aprovação ({reviewQueue.length})</h2>
          <p className="text-sm leading-7 text-slate-700">
            Confirme a autorização de uso e a ausência de informações de pacientes, segredos de clientes e dados não autorizados.
            Um autor não pode aprovar seu próprio artigo. Para conteúdo de organização, a aprovação exige gerente membro daquela organização.
          </p>
          <label className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm font-semibold leading-6">
            <input type="checkbox" checked={reviewAttested} onChange={(e) => setReviewAttested(e.target.checked)}
              className="mt-1 h-5 w-5 accent-[#0a7f86]"/>
            <span>Declaro que farei a revisão independente de direitos de uso, confidencialidade, escopo, validade técnica e visibilidade antes de aprovar um artigo.</span>
          </label>
          {!reviewQueue.length && <p className="rounded-lg bg-white p-5">Nenhum artigo aguardando revisão.</p>}
          {reviewQueue.map((article) => (
            <article key={article.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-xl font-black">{article.title}</h3>
              <p className="mt-2 text-sm text-slate-600">Autor ID {article.owner_id} · {visibilityLabels[article.visibility]} · organização {article.workspace_id ?? "—"}</p>
              <details className="mt-3 rounded-lg border border-slate-200 p-4">
                <summary className="cursor-pointer text-sm font-bold">Conferir texto integral</summary>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-7">{article.content}</p>
              </details>
              <div className="mt-4 flex flex-wrap gap-3">
                {(["approve","reject"] as const).map((decision) => (
                  <button key={decision} disabled={busy || !reviewAttested || article.owner_id === user?.id}
                    type="button" onClick={() => {
                      void runAction(
                        () => api.reviewKnowledgeArticle(article.id, decision),
                        decision === "approve" ? "Artigo aprovado e disponibilizado apenas ao escopo autorizado." : "Artigo devolvido para revisão.",
                      );
                    }}
                    className={`min-h-11 rounded-lg px-5 py-2 text-sm font-bold text-white disabled:opacity-40 ${decision === "approve" ? "bg-[#075c63]" : "bg-slate-700"}`}>
                    {decision === "approve" ? "Aprovar" : "Reprovar"}
                  </button>
                ))}
              </div>
            </article>
          ))}
        </section>
      )}

      {isAdmin && view === "administracao" && (
        <section className="space-y-6">
          <h2 className="text-2xl font-black">Organizações e conteúdo legado</h2>
          <div className="grid gap-5 lg:grid-cols-2">
            <form onSubmit={manageWorkspace} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-black">Criar organização de conhecimento</h3>
              <label className="mt-4 block text-sm font-bold">Nome
                <input required minLength={3} maxLength={160} value={workspaceName} onChange={(e) => setWorkspaceName(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
              <label className="mt-4 block text-sm font-bold">Identificador (minúsculas e hífens)
                <input required minLength={3} maxLength={64} pattern="[a-z0-9]+(-[a-z0-9]+)*" value={workspaceSlug} onChange={(e) => setWorkspaceSlug(e.target.value)}
                  placeholder="clinica-exemplo" className="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
              <button disabled={busy} className="mt-5 min-h-11 rounded-lg bg-[#071a3d] px-5 py-2 font-bold text-white disabled:opacity-40">Criar espaço isolado</button>
            </form>

            <form onSubmit={addWorkspaceMember} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-black">Conceder acesso explícito</h3>
              <label className="mt-4 block text-sm font-bold">Organização
                <select required value={membershipWorkspace} onChange={(e) => setMembershipWorkspace(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3">
                  <option value="">Selecione</option>
                  {workspaces.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
                </select>
              </label>
              <label className="mt-4 block text-sm font-bold">ID de usuário ativo
                <input required type="number" min={1} value={membershipUser} onChange={(e) => setMembershipUser(e.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
              <label className="mt-4 block text-sm font-bold">Papel no espaço
                <select value={memberRole} onChange={(e) => setMemberRole(e.target.value as "member"|"manager")}
                  className="mt-2 w-full rounded-lg border border-slate-300 p-3">
                  <option value="member">Membro</option><option value="manager">Gerente de revisão</option>
                </select>
              </label>
              <button disabled={busy} className="mt-5 min-h-11 rounded-lg bg-[#071a3d] px-5 py-2 font-bold text-white disabled:opacity-40">Adicionar membro</button>
            </form>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="flex items-center gap-2 text-lg font-black"><ShieldCheck size={20}/> Artigos históricos em quarentena ({legacy.length})</h3>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              A classificação não publica nem valida um registro legado. Ela atribui um responsável para
              revisão posterior, com escopo privado ou restrito a uma organização.
              Não selecione compartilhamento global sem passar pelo fluxo independente.
            </p>
            {legacy.length === 0 && <p className="mt-4 text-sm text-slate-700">Nenhum item legado encontrado nesta página do inventário.</p>}
            {legacy.map((old) => (
              <div key={old.id} className="mt-5 rounded-lg border border-slate-200 p-4">
                <p className="text-sm font-bold">Registro #{old.id}: {old.title}</p>
                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                  <label className="text-xs font-semibold">Novo responsável (ID)
                    <input type="number" min={1} value={legacyOwner} onChange={(e) => setLegacyOwner(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-slate-300 p-2"/>
                  </label>
                  <label className="text-xs font-semibold">Categoria
                    <select value={legacyCategory} onChange={(e) => setLegacyCategory(e.target.value as KnowledgeCategory)}
                      className="mt-1 w-full rounded-lg border border-slate-300 p-2">
                      {Object.entries(categoryLabels).map(([key,value]) => <option key={key} value={key}>{value}</option>)}
                    </select>
                  </label>
                  <label className="text-xs font-semibold">Organização (opcional)
                    <select value={legacyWorkspace} onChange={(e) => setLegacyWorkspace(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-slate-300 p-2">
                      <option value="">Privado</option>
                      {workspaces.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
                    </select>
                  </label>
                </div>
                <button disabled={busy || !legacyOwner} type="button"
                  onClick={() => {
                    void runAction(
                      () => api.classifyLegacyKnowledge(old.id, {
                        owner_id:Number(legacyOwner), category:legacyCategory,
                        workspace_id:legacyWorkspace ? Number(legacyWorkspace) : null,
                      }),
                      "Artigo antigo classificado como rascunho. Nenhuma publicação ocorreu.",
                    );
                  }}
                  className="mt-4 min-h-10 rounded-lg border border-[#0a7f86] px-4 py-2 text-sm font-bold text-[#075c63] disabled:opacity-40">
                  Classificar em rascunho
                </button>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default function KnowledgePage() {
  return <AccessGuard minimum={2}><KBPageContent /></AccessGuard>;
}
