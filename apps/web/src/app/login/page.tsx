"use client";

import { FormEvent, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError, api } from "@/services/api";
import BrandLogo from "@/components/BrandLogo";

const registrationEnabled = process.env.NEXT_PUBLIC_REGISTRATION_ENABLED === "true";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [verificationSent, setVerificationSent] = useState(false);
  const [info, setInfo] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isRegister = registrationEnabled && mode === "register";

  const validateRegistrationFields = (): boolean => {
    if (password.length < 12) {
      setError("A senha deve ter pelo menos 12 caracteres.");
      return false;
    }
    if (password !== confirmPassword) {
      setError("As senhas não coincidem.");
      return false;
    }
    if (phone.replace(/\D/g, "").length < 10) {
      setError("Informe um telefone válido para receber o código de verificação.");
      return false;
    }
    return true;
  };

  const sendVerificationCode = async () => {
    if (!validateRegistrationFields()) return;
    const result = await api.sendVerificationCode({ email, phone_number: phone });
    setVerificationSent(true);
    if (result.verification_code) {
      setVerificationCode(result.verification_code);
      setInfo(`Código de verificação gerado para ${result.to}: ${result.verification_code}`);
    } else {
      setInfo(`Código de verificação enviado para ${result.to}.`);
    }
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setInfo("");
    try {
      if (isRegister) {
        if (!verificationSent) {
          await sendVerificationCode();
          return;
        }
        if (!verificationCode.trim()) {
          setError("Informe o código de verificação recebido por SMS.");
          return;
        }
        await register({
          email,
          password,
          full_name: name,
          phone_number: phone,
          verification_code: verificationCode.trim(),
        });
      } else {
        await login(email, password);
      }
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401 && !isRegister) {
        setError("Credenciais inválidas.");
      } else if (requestError instanceof ApiError && requestError.status === 503 && isRegister && !verificationSent) {
        setError("A verificação por SMS não está configurada nesta implantação.");
      } else if (requestError instanceof ApiError) {
        setError(
          isRegister
            ? verificationSent
              ? "Não foi possível criar a conta. Verifique o código informado."
              : "Não foi possível enviar o código de verificação."
            : "Não foi possível entrar. Tente novamente.",
        );
      } else {
        setError("Não foi possível conectar à plataforma. Verifique sua conexão e tente novamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] grid place-items-center px-4">
      <form onSubmit={onSubmit} className="bg-white w-full max-w-md rounded-lg border border-slate-200 shadow-lg p-7 space-y-4">
        <BrandLogo />
        <div>
          <h1 className="text-2xl font-bold text-[#071a3d]">
            {isRegister ? "Criar conta" : "Entrar"}
          </h1>
          <p className="text-sm text-gray-500 mt-2">
            {isRegister
              ? "Cadastre seu usuário e confirme o código de verificação para continuar."
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
            setVerificationSent(false);
            setVerificationCode("");
          }}
          placeholder="Email"
          aria-label="Email"
          autoComplete="email"
          required
        />

        {isRegister && (
          <input
            className="w-full border rounded-lg px-3 py-2"
            type="tel"
            value={phone}
            onChange={(event) => {
              setPhone(event.target.value);
              setVerificationSent(false);
              setVerificationCode("");
            }}
            placeholder="+55 47 99678-9861"
            aria-label="Telefone"
            autoComplete="tel"
            required
          />
        )}
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

        {isRegister && verificationSent && (
          <input
            className="w-full border rounded-lg px-3 py-2"
            type="text"
            inputMode="numeric"
            value={verificationCode}
            onChange={(event) => setVerificationCode(event.target.value)}
            placeholder="Código de verificação"
            aria-label="Código de verificação"
            autoComplete="one-time-code"
            required
          />
        )}

        {info && <p className="text-sm text-green-700">{info}</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          disabled={loading}
          className="w-full min-h-11 bg-[#071a3d] text-white rounded-lg px-3 py-2 hover:bg-[#0a7f86] disabled:opacity-60"
          type="submit"
        >
          {loading
            ? "Aguarde..."
            : isRegister
              ? verificationSent
                ? "Criar conta"
                : "Enviar código de verificação"
              : "Entrar"}
        </button>
        {registrationEnabled && (
          <button
            type="button"
            onClick={() => {
              setMode(isRegister ? "login" : "register");
              setVerificationSent(false);
              setVerificationCode("");
              setInfo("");
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
