"use client";

import { FormEvent, useState } from "react";
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
      <form onSubmit={onSubmit} className="w-full max-w-md space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-lg sm:p-7">
        <BrandLogo />
        <div>
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
            className="w-full border rounded-lg px-3 py-2"
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
          className="w-full border rounded-lg px-3 py-2"
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
          className="w-full border rounded-lg px-3 py-2"
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
            className="w-full border rounded-lg px-3 py-2"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Confirmar senha"
            aria-label="Confirmar senha"
            autoComplete="new-password"
            required
          />
        )}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          disabled={loading}
          className="w-full min-h-11 bg-[#071a3d] text-white rounded-lg px-3 py-2 hover:bg-[#0a7f86] disabled:opacity-60"
          type="submit"
        >
          {loading
            ? "Aguarde..."
            : isRegister
              ? "Criar conta"
              : "Entrar"}
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
      </form>
    </div>
  );
}
