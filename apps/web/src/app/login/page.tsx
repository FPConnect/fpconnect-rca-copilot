"use client";

import { FormEvent, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/services/api";

const DEFAULT_PHONE = "+55 47 99678-9861";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("Master");
  const [email, setEmail] = useState("master@fpconnect.com");
  const [phone, setPhone] = useState(DEFAULT_PHONE);
  const [password, setPassword] = useState("Master@2024Secure!");
  const [confirmPassword, setConfirmPassword] = useState("Master@2024Secure!");
  const [verificationCode, setVerificationCode] = useState("");
  const [verificationSent, setVerificationSent] = useState(false);
  const [info, setInfo] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isRegister = mode === "register";

  const validateRegistrationFields = () => {
    if (password.length < 8) {
      setError("A senha deve ter pelo menos 8 caracteres.");
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
    } catch {
      setError(
        isRegister
          ? verificationSent
            ? "Não foi possível criar a conta. Verifique o código informado."
            : "Não foi possível enviar o código de verificação."
          : "Credenciais inválidas.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] grid place-items-center px-4">
      <form onSubmit={onSubmit} className="bg-white w-full max-w-md rounded-lg shadow p-6 space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isRegister ? "Criar conta" : "Entrar"}
          </h1>
          <p className="text-sm text-gray-500 mt-2">
            {isRegister
              ? "Cadastre seu usuário e confirme o código enviado por SMS para acessar o FPConnect RCA Copilot."
              : "Acesse a plataforma FPConnect RCA Copilot. Recomenda-se começar com a conta Master."}
          </p>
        </div>

        {!isRegister && (
          <div className="rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-900 space-y-1">
            <p className="font-semibold">Contas de teste disponíveis</p>
            <p>Master (5): master@fpconnect.com / Master@2024Secure!</p>
            <p>Administrador (4): admin_teste@fpconnect.com / Admin@123</p>
            <p>Gerente (3): gerente_teste@fpconnect.com / Gerente@123</p>
            <p>Usuário (2): usuario_teste@fpconnect.com / Usuario@123</p>
            <p>Visitante (1): visitante_teste@fpconnect.com / Visitante@123</p>
          </div>
        )}

        {isRegister && (
          <input
            className="w-full border rounded-lg px-3 py-2"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Nome"
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
            required
          />
        )}
        <input
          className="w-full border rounded-lg px-3 py-2"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Senha"
          required
        />

        {isRegister && (
          <input
            className="w-full border rounded-lg px-3 py-2"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Confirmar senha"
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
            required
          />
        )}

        {info && <p className="text-sm text-green-700">{info}</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          disabled={loading}
          className="w-full bg-blue-600 text-white rounded-lg px-3 py-2 hover:bg-blue-700 disabled:opacity-60"
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
        <button
          type="button"
          onClick={() => {
            setMode(isRegister ? "login" : "register");
            setVerificationSent(false);
            setVerificationCode("");
            setInfo("");
            setError("");
          }}
          className="w-full text-sm text-blue-700 hover:text-blue-900"
        >
          {isRegister ? "Já tenho conta" : "Criar novo usuário"}
        </button>
      </form>
    </div>
  );
}
