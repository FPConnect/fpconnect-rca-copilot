"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name?: string;
    phone_number?: string;
    verification_code?: string;
  }) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function establishServerSession(token: string | null) {
  const response = await fetch("/api/session", {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    cache: "no-store",
  });
  return response.ok;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.clearLegacyPreviewCredentials();
    const stored = sessionStorage.getItem("auth_token");
    establishServerSession(stored).then((valid) => {
      if (valid && stored) setToken(stored);
      else sessionStorage.removeItem("auth_token");
    }).catch(() => {
      sessionStorage.removeItem("auth_token");
    }).finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await api.login({ email, password });
    if (!(await establishServerSession(result.access_token))) {
      throw new Error("Não foi possível validar a sessão no servidor.");
    }
    sessionStorage.setItem("auth_token", result.access_token);
    setToken(result.access_token);
    router.push("/dashboard");
    router.refresh();
  }, [router]);

  const register = useCallback(async (data: {
    email: string;
    password: string;
    full_name?: string;
    phone_number?: string;
    verification_code?: string;
  }) => {
    await api.register(data);
    await login(data.email, data.password);
  }, [login]);

  const logout = useCallback(() => {
    sessionStorage.removeItem("auth_token");
    setToken(null);
    void establishServerSession(null).catch(() => {
      // The server independently revalidates the short-lived cookie on every request.
    });
  }, []);

  const value = useMemo(
    () => ({ token, isAuthenticated: Boolean(token), isLoading, login, register, logout }),
    [token, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
