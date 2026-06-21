"use client";

import { useMemo, useState } from "react";
import { UserPlus } from "lucide-react";
import SearchBar from "@/components/SearchBar";
import FilterBar from "@/components/FilterBar";

const USERS = [
  { id: 1, name: "Master", email: "master@fpconnect.com", role: "master", accessLevel: 5, status: "active" },
  { id: 2, name: "Administrador", email: "admin_teste@fpconnect.com", role: "admin", accessLevel: 4, status: "active" },
  { id: 3, name: "Gerente", email: "gerente_teste@fpconnect.com", role: "manager", accessLevel: 3, status: "active" },
  { id: 4, name: "Usuário", email: "usuario_teste@fpconnect.com", role: "user", accessLevel: 2, status: "active" },
  { id: 5, name: "Visitante", email: "visitante_teste@fpconnect.com", role: "visitor", accessLevel: 1, status: "active" },
];

const ROLE_COLORS: Record<string, string> = {
  master: "bg-amber-100 text-amber-800",
  admin: "bg-purple-100 text-purple-700",
  manager: "bg-blue-100 text-blue-700",
  user: "bg-green-100 text-green-700",
  visitor: "bg-gray-100 text-gray-700",
};

const FILTERS = [
  {
    key: "role",
    label: "Perfil",
    options: [
      { label: "Master", value: "master" },
      { label: "Administrador", value: "admin" },
      { label: "Gerente", value: "manager" },
      { label: "Usuário", value: "user" },
      { label: "Visitante", value: "visitor" },
    ],
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

export default function AccessControlPage() {
  const [users] = useState(USERS);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return users.filter((u) => {
      const matchSearch =
        !q ||
        u.name.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q);
      const matchRole = !filters.role || u.role === filters.role;
      const matchStatus = !filters.status || u.status === filters.status;
      return matchSearch && matchRole && matchStatus;
    });
  }, [users, search, filters]);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Controle de Acesso</h1>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          <UserPlus size={16} />
          Novo Usuário
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar
          placeholder="Pesquisar usuários..."
          value={search}
          onChange={setSearch}
          className="w-64"
        />
        <FilterBar
          filters={FILTERS}
          values={filters}
          onChange={(key, value) => setFilters((p) => ({ ...p, [key]: value }))}
          onClear={() => setFilters({})}
        />
      </div>

      <div className="bg-white rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm min-w-[600px]">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["Nome", "Email", "Perfil", "Nível", "Status", "Ações"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                  Nenhum usuário encontrado.
                </td>
              </tr>
            ) : (
              filtered.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{u.name}</td>
                  <td className="px-4 py-3 text-gray-600">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${ROLE_COLORS[u.role]}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                      {u.accessLevel}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${u.status === "active" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {u.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button className="text-xs text-blue-600 hover:underline">Editar</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
