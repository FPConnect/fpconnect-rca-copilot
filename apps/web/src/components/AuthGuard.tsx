"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  // Public marketing routes never require a login or wait for session validation.
  const isPublicRoute =
    pathname === "/" ||
    pathname === "/login" ||
    pathname === "/diagnostic" ||
    pathname === "/recursos" ||
    pathname === "/solucoes" ||
    pathname.startsWith("/recursos/");

  useEffect(() => {
    if (isLoading || isPublicRoute) return;

    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, isPublicRoute, router]);

  if (isPublicRoute) return <>{children}</>;

  if (isLoading) {
    return <div className="app-theme app-viewport grid place-items-center p-6 text-sm text-gray-500">Carregando sessão...</div>;
  }

  if (!isAuthenticated) {
    return <div className="app-theme app-viewport grid place-items-center p-6 text-sm text-gray-500">Redirecionando para login...</div>;
  }

  return <>{children}</>;
}
