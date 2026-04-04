"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "@/services/api";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("auth_token");
    if (stored) setToken(stored);
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const result = await api.login({ email, password });
    localStorage.setItem("auth_token", result.access_token);
    setToken(result.access_token);
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setToken(null);
  };

  const value = useMemo(
    () => ({ token, isAuthenticated: Boolean(token), isLoading, login, logout }),
    [token, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
