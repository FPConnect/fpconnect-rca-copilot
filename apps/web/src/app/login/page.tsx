"use client";

import { FormEvent, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@fpconnect.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
    } catch {
      setError("Credenciais inválidas.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] grid place-items-center">
      <form onSubmit={onSubmit} className="bg-white w-full max-w-md rounded-xl shadow p-6 space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Entrar</h1>
        <p className="text-sm text-gray-500">Acesse a plataforma FPConnect RCA Copilot.</p>
        <input className="w-full border rounded-lg px-3 py-2" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
        <input className="w-full border rounded-lg px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Senha" required />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="w-full bg-blue-600 text-white rounded-lg px-3 py-2 hover:bg-blue-700 disabled:opacity-60" type="submit">
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
