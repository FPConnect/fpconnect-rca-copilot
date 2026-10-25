"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Loader2, Pencil, ShieldCheck, UserPlus, X } from "lucide-react";
import AccessGuard from "@/components/AccessGuard";
import FilterBar from "@/components/FilterBar";
import SearchBar from "@/components/SearchBar";
import { useAuth } from "@/contexts/AuthContext";
import { api, ApiError, CreateManagedUserPayload, ManagedRole, ManagedUser } from "@/services/api";

const ROLE_LEVELS: Record<ManagedRole, number> = {
  master: 5,
  admin: 4,
  manager: 3,
  user: 2,
  visitor: 1,
};

const ROLE_LABELS: Record<ManagedRole, string> = {
  master: "Master",
  admin: "Administrador",
  manager: "Gerente",
  user: "Usuário",
  visitor: "Visitante",
};

const ROLE_COLORS: Record<ManagedRole, string> = {
  master: "bg-amber-100 text-amber-800",
  admin: "bg-cyan-100 text-cyan-800",
  manager: "bg-blue-100 text-blue-800",
  user: "bg-emerald-100 text-emerald-800",
  visitor: "bg-slate-100 text-slate-700",
};

const ROLE_OPTIONS: Array<{ value: Exclude<ManagedRole, "master">; label: string }> = [
  { value: "admin", label: "Administrador" },
  { value: "manager", label: "Gerente" },
  { value: "user", label: "Usuário" },
  { value: "visitor", label: "Visitante" },
];

const FILTERS = [
  {
    key: "role",
    label: "Perfil",
    options: Object.entries(ROLE_LABELS).map(([value, label]) => ({ value, label })),
  },
  {
    key: "status",
    label: "Status",
    options: [
      { label: "Ativo", value: "active" },
      { label: "Inativo", value: "inactive" },
    ],
  },
];

const EMPTY_CREATE_FORM: CreateManagedUserPayload = {
  email: "",
  password: "",
  full_name: "",
  phone_number: "",
  role: "user",
};

function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) return "Não foi possível concluir a operação.";
  try {
    const body = JSON.parse(error.message) as { detail?: string | { password?: string[] } };
    if (typeof body.detail === "string") return body.detail;
    if (body.detail && typeof body.detail === "object" && body.detail.password) {
      return `A senha não atende aos requisitos: ${body.detail.password.join(", ")}.`;
    }
  } catch {
    // The API can return a plain-text error at infrastructure boundaries.
  }
  return "Não foi possível concluir a operação.";
}

export default function AccessControlPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<ManagedUser | null>(null);
  const [createForm, setCreateForm] = useState<CreateManagedUserPayload>(EMPTY_CREATE_FORM);
  const [editRole, setEditRole] = useState<Exclude<ManagedRole, "master">>("user");
  const [editActive, setEditActive] = useState(true);

  const actorLevel = currentUser?.access_level ?? 0;
  const availableRoles = useMemo(
    () => ROLE_OPTIONS.filter((option) => ROLE_LEVELS[option.value] < actorLevel),
    [actorLevel],
  );

  useEffect(() => {
    let active = true;
    api.getUsers()
      .then((accounts) => {
        if (active) setUsers(accounts);
      })
      .catch((loadError: unknown) => {
        if (active) setError(errorMessage(loadError));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return users.filter((account) => {
      const statusValue = account.is_active ? "active" : "inactive";
      const matchesSearch =
        !query ||
        (account.full_name ?? "").toLowerCase().includes(query) ||
        account.email.toLowerCase().includes(query);
      return (
        matchesSearch &&
        (!filters.role || account.role === filters.role) &&
        (!filters.status || statusValue === filters.status)
      );
    });
  }, [filters, search, users]);

  function canManage(account: ManagedUser) {
    return account.id !== currentUser?.id && account.access_level < actorLevel;
  }

  function openEdit(account: ManagedUser) {
    if (!canManage(account) || account.role === "master") return;
    setError("");
    setSuccess("");
    setEditRole(account.role);
    setEditActive(account.is_active);
    setEditing(account);
  }

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const created = await api.createManagedUser({
        ...createForm,
        email: createForm.email.trim(),
        full_name: createForm.full_name?.trim() || undefined,
        phone_number: createForm.phone_number?.trim() || undefined,
      });
      setUsers((current) => [created, ...current]);
      setCreateForm({ ...EMPTY_CREATE_FORM, role: availableRoles.at(-1)?.value ?? "visitor" });
      setCreateOpen(false);
      setSuccess("Usuário criado com acesso limitado ao perfil selecionado.");
    } catch (createError) {
      setError(errorMessage(createError));
    } finally {
      setSaving(false);
    }
  }

  async function updateAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editing) return;
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const updated = await api.updateManagedUser(editing.id, { role: editRole, is_active: editActive });
      setUsers((current) => current.map((account) => (account.id === updated.id ? updated : account)));
      setEditing(null);
      setSuccess("Acesso atualizado. As sessões anteriores desse usuário foram revogadas.");
    } catch (updateError) {
      setError(errorMessage(updateError));
    } finally {
      setSaving(false);
    }
  }

  return (
    <AccessGuard minimum={4}>
      <main className="mx-auto max-w-6xl">
        <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-cyan-700">
              <ShieldCheck size={17} aria-hidden="true" />
              Administração de identidades
            </div>
            <h1 className="text-3xl font-bold text-slate-950">Controle de Acesso</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-600">
              Perfis superiores administram somente níveis subordinados. Alterações de acesso revogam sessões existentes.
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              setError("");
              setSuccess("");
              setCreateForm((current) => ({
                ...current,
                role: availableRoles.some((role) => role.value === current.role)
                  ? current.role
                  : availableRoles[0].value,
              }));
              setCreateOpen(true);
            }}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 text-sm font-semibold text-white transition-colors hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!availableRoles.length}
          >
            <UserPlus size={17} aria-hidden="true" />
            Novo Usuário
          </button>
        </header>

        {error && (
          <div role="alert" className="mb-4 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            <AlertCircle className="mt-0.5 shrink-0" size={16} aria-hidden="true" />
            {error}
          </div>
        )}
        {success && (
          <div role="status" className="mb-4 flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
            <CheckCircle2 className="mt-0.5 shrink-0" size={16} aria-hidden="true" />
            {success}
          </div>
        )}

        <div className="mb-4 flex flex-wrap gap-3">
          <SearchBar placeholder="Pesquisar usuários..." value={search} onChange={setSearch} className="w-full sm:w-72" />
          <FilterBar
            filters={FILTERS}
            values={filters}
            onChange={(key, value) => setFilters((current) => ({ ...current, [key]: value }))}
            onClear={() => setFilters({})}
          />
        </div>

        <section className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm" aria-label="Usuários cadastrados">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {["Nome", "Email", "Perfil", "Nível", "Status", "Ações"].map((heading) => (
                  <th key={heading} className="px-4 py-3 text-left font-semibold text-slate-600">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-slate-500"><Loader2 className="mx-auto mb-2 animate-spin" size={22} aria-hidden="true" />Carregando usuários...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-slate-500">Nenhum usuário encontrado.</td></tr>
              ) : filtered.map((account) => (
                <tr key={account.id} className="transition-colors hover:bg-slate-50">
                  <td className="px-4 py-3 font-semibold text-slate-950">
                    {account.full_name || "Sem nome informado"}
                    {account.id === currentUser?.id && <span className="ml-2 text-xs font-medium text-cyan-700">Sua conta</span>}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{account.email}</td>
                  <td className="px-4 py-3"><span className={`rounded-full px-2 py-1 text-xs font-semibold ${ROLE_COLORS[account.role]}`}>{ROLE_LABELS[account.role]}</span></td>
                  <td className="px-4 py-3 font-semibold text-slate-700">{account.access_level}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${account.is_active ? "text-emerald-700" : "text-slate-500"}`}>
                      <span className={`h-2 w-2 rounded-full ${account.is_active ? "bg-emerald-500" : "bg-slate-300"}`} />
                      {account.is_active ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {canManage(account) ? (
                      <button type="button" onClick={() => openEdit(account)} className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-semibold text-cyan-800 hover:bg-cyan-50" aria-label={`Editar ${account.email}`}>
                        <Pencil size={14} aria-hidden="true" />Editar
                      </button>
                    ) : <span className="text-xs text-slate-400">Protegido</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>

      {createOpen && (
        <div className="modal-layer fixed inset-0 z-50 flex items-start justify-center bg-slate-950/60 px-4 sm:items-center" role="presentation">
          <section role="dialog" aria-modal="true" aria-labelledby="create-user-title" className="modal-panel my-auto w-full max-w-lg rounded-lg bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div><h2 id="create-user-title" className="text-xl font-bold text-slate-950">Criar novo usuário</h2><p className="mt-1 text-sm text-slate-500">Defina o nível inicial e uma senha temporária segura.</p></div>
              <button type="button" onClick={() => setCreateOpen(false)} className="rounded-md p-2 text-slate-500 hover:bg-slate-100" aria-label="Fechar"><X size={18} /></button>
            </div>
            <form onSubmit={createAccount} className="grid gap-4 p-6 sm:grid-cols-2">
              <label className="grid gap-1.5 text-sm font-semibold text-slate-700 sm:col-span-2">Nome completo<input required maxLength={120} value={createForm.full_name} onChange={(event) => setCreateForm((current) => ({ ...current, full_name: event.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100" /></label>
              <label className="grid gap-1.5 text-sm font-semibold text-slate-700 sm:col-span-2">Email<input required type="email" value={createForm.email} onChange={(event) => setCreateForm((current) => ({ ...current, email: event.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100" /></label>
              <label className="grid gap-1.5 text-sm font-semibold text-slate-700">Telefone<input maxLength={32} value={createForm.phone_number} onChange={(event) => setCreateForm((current) => ({ ...current, phone_number: event.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100" /></label>
              <label className="grid gap-1.5 text-sm font-semibold text-slate-700">Perfil<select value={createForm.role} onChange={(event) => setCreateForm((current) => ({ ...current, role: event.target.value as Exclude<ManagedRole, "master"> }))} className="rounded-lg border border-slate-300 bg-white px-3 py-2.5 font-normal outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100">{availableRoles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}</select></label>
              <label className="grid gap-1.5 text-sm font-semibold text-slate-700 sm:col-span-2">Senha temporária<input required type="password" minLength={12} maxLength={72} value={createForm.password} onChange={(event) => setCreateForm((current) => ({ ...current, password: event.target.value }))} className="rounded-lg border border-slate-300 px-3 py-2.5 font-normal outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100" /><span className="text-xs font-normal text-slate-500">Mínimo de 12 caracteres, com maiúscula, minúscula, número e símbolo.</span></label>
              <div className="flex justify-end gap-3 border-t border-slate-200 pt-4 sm:col-span-2">
                <button type="button" onClick={() => setCreateOpen(false)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">Cancelar</button>
                <button type="submit" disabled={saving} className="inline-flex min-w-32 items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:opacity-50">{saving && <Loader2 className="animate-spin" size={16} />}Criar usuário</button>
              </div>
            </form>
          </section>
        </div>
      )}

      {editing && (
        <div className="modal-layer fixed inset-0 z-50 flex items-start justify-center bg-slate-950/60 px-4 sm:items-center" role="presentation">
          <section role="dialog" aria-modal="true" aria-labelledby="edit-user-title" className="modal-panel my-auto w-full max-w-md rounded-lg bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div><h2 id="edit-user-title" className="text-xl font-bold text-slate-950">Editar acesso</h2><p className="mt-1 text-sm text-slate-500">{editing.email}</p></div>
              <button type="button" onClick={() => setEditing(null)} className="rounded-md p-2 text-slate-500 hover:bg-slate-100" aria-label="Fechar"><X size={18} /></button>
            </div>
            <form onSubmit={updateAccount} className="grid gap-5 p-6">
              <label className="grid gap-1.5 text-sm font-semibold text-slate-700">Perfil<select value={editRole} onChange={(event) => setEditRole(event.target.value as Exclude<ManagedRole, "master">)} className="rounded-lg border border-slate-300 bg-white px-3 py-2.5 font-normal outline-none focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100">{availableRoles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}</select></label>
              <label className="flex items-center justify-between gap-4 rounded-lg border border-slate-200 px-4 py-3">
                <span><span className="block text-sm font-semibold text-slate-800">Conta ativa</span><span className="mt-0.5 block text-xs text-slate-500">Desativar impede novos acessos e encerra sessões existentes.</span></span>
                <input type="checkbox" checked={editActive} onChange={(event) => setEditActive(event.target.checked)} className="h-5 w-5 accent-cyan-700" />
              </label>
              <div className="flex justify-end gap-3 border-t border-slate-200 pt-4">
                <button type="button" onClick={() => setEditing(null)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">Cancelar</button>
                <button type="submit" disabled={saving} className="inline-flex min-w-32 items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:opacity-50">{saving && <Loader2 className="animate-spin" size={16} />}Salvar acesso</button>
              </div>
            </form>
          </section>
        </div>
      )}
    </AccessGuard>
  );
}
