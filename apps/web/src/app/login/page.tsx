"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/services/api";
import BrandLogo from "@/components/BrandLogo";

const registrationEnabled = process.env.NEXT_PUBLIC_REGISTRATION_ENABLED === "true";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isRegister = registrationEnabled && mode === "register";

  const validateRegistrationFields = (): boolean => {
    const hasRequiredPasswordComplexity =
      password.length >= 12 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /\d/.test(password) &&
      /[^A-Za-z0-9]/.test(password);
    if (!hasRequiredPasswordComplexity) {
      setError("Use ao menos 12 caracteres, com maiúscula, minúscula, número e símbolo.");
      return false;
    }
    if (password !== confirmPassword) {
      setError("As senhas não coincidem.");
      return false;
    }
    return true;
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (isRegister) {
        if (!validateRegistrationFields()) return;
        await register({
          email,
          password,
          full_name: name,
        });
      } else {
        await login(email, password);
      }
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401 && !isRegister) {
        setError("Credenciais inválidas.");
      } else if (requestError instanceof ApiError && requestError.status === 403 && isRegister) {
        setError("O cadastro não está liberado para este e-mail.");
      } else if (requestError instanceof ApiError && requestError.status === 400 && isRegister) {
        setError("Já existe uma conta para este e-mail.");
      } else if (requestError instanceof ApiError && requestError.status === 422 && isRegister) {
        setError("Use ao menos 12 caracteres, com maiúscula, minúscula, número e símbolo.");
      } else if (requestError instanceof ApiError && requestError.status >= 500) {
        setError("O serviço de autenticação está temporariamente indisponível.");
      } else if (requestError instanceof ApiError) {
        setError(isRegister ? "Não foi possível criar a conta." : "Não foi possível entrar. Tente novamente.");
      } else {
        setError("Não foi possível conectar à plataforma. Verifique sua conexão e tente novamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="brand-surface grid min-h-[calc(100dvh-2rem)] place-items-center py-4">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-3xl border border-[#dfeae7] bg-white shadow-xl lg:grid-cols-2">
        <div className="marketing-hero flex min-h-60 flex-col justify-between bg-[#07172c] p-7 text-white sm:p-10 lg:min-h-[590px]">
          <Link href="/" aria-label="OPSPECTA"><BrandLogo inverse /></Link>
          <div className="mt-12 max-w-md">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#8ce7dc]">Inteligência operacional</p>
            <p className="mt-4 font-[family-name:var(--font-brand-display)] text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">Mais contexto. Melhores decisões.</p>
            <p className="mt-4 max-w-sm leading-7 text-[#b8cbd3]">Informações organizadas para apoiar sua equipe em cada etapa da operação.</p>
          </div>
          <p className="mt-10 text-xs text-[#b8cbd3]">OPSPECTA · Tecnologia a serviço da saúde</p>
        </div>
      <form onSubmit={onSubmit} className="flex flex-col justify-center gap-4 bg-white p-7 sm:p-10">
        <div className="mb-2">
          <h1 className="text-2xl font-bold text-[#071a3d]">
            {isRegister ? "Criar conta" : "Entrar"}
          </h1>
          <p className="text-sm text-gray-500 mt-2">
            {isRegister
              ? "Crie sua conta autorizada para acessar a plataforma."
              : "Acesse a plataforma com sua conta autorizada."}
          </p>
        </div>
        {isRegister && (
          <input
            className="min-h-12 w-full rounded-xl border border-[#d8e2e2] bg-[#f9fbfa] px-4 py-2 outline-none focus:border-[#0a827b] focus:ring-2 focus:ring-[#0a827b]/20"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Nome"
            aria-label="Nome"
            autoComplete="name"
            required
          />
        )}
        <input
          className="min-h-12 w-full rounded-xl border border-[#d8e2e2] bg-[#f9fbfa] px-4 py-2 outline-none focus:border-[#0a827b] focus:ring-2 focus:ring-[#0a827b]/20"
          type="email"
          value={email}
          onChange={(event) => {
            setEmail(event.target.value);
          }}
          placeholder="Email"
          aria-label="Email"
          autoComplete="email"
          required
        />
        <input
          className="min-h-12 w-full rounded-xl border border-[#d8e2e2] bg-[#f9fbfa] px-4 py-2 outline-none focus:border-[#0a827b] focus:ring-2 focus:ring-[#0a827b]/20"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Senha"
          aria-label="Senha"
          autoComplete={isRegister ? "new-password" : "current-password"}
          required
        />
        {isRegister && (
          <p className="text-xs text-slate-500">
            Use ao menos 12 caracteres, com maiúscula, minúscula, número e símbolo.
          </p>
        )}

        {isRegister && (
          <input
            className="min-h-12 w-full rounded-xl border border-[#d8e2e2] bg-[#f9fbfa] px-4 py-2 outline-none focus:border-[#0a827b] focus:ring-2 focus:ring-[#0a827b]/20"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Confirmar senha"
            aria-label="Confirmar senha"
            autoComplete="new-password"
            required
          />
        )}
        {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        <button
          disabled={loading}
          className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#0b554f] px-4 py-2 font-bold text-white transition hover:bg-[#073e3b] disabled:opacity-60"
          type="submit"
        >
          {loading
            ? "Aguarde..."
            : isRegister
              ? "Criar conta"
              : "Entrar"}
          {!loading && <ArrowRight size={18} aria-hidden="true" />}
        </button>
        {registrationEnabled && (
          <button
            type="button"
            onClick={() => {
              setMode(isRegister ? "login" : "register");
              setError("");
            }}
            className="w-full text-sm text-[#0a7f86] hover:text-[#071a3d]"
          >
            {isRegister ? "Já tenho conta" : "Criar novo usuário"}
          </button>
        )}
        <div className="mt-3 flex items-center justify-center gap-2 border-t border-[#e1e9e7] pt-5 text-xs text-slate-500">
          <ShieldCheck size={16} aria-hidden="true" />
          <span>Acesso restrito a contas autorizadas</span>
        </div>
      </form>
      </div>
    </div>
  );
}
