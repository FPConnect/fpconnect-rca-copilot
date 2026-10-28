"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated && pathname !== "/login" && pathname !== "/") {
      router.replace("/login");
    }

  }, [isAuthenticated, isLoading, pathname, router]);

  // Public pages must render even while session validation is pending.
  if (pathname === "/" || pathname === "/login") return <>{children}</>;

  if (isLoading) {
    return <div className="app-theme app-viewport grid place-items-center p-6 text-sm text-gray-500">Carregando sessão...</div>;
  }

  if (!isAuthenticated && pathname !== "/login" && pathname !== "/") {
    return <div className="app-theme app-viewport grid place-items-center p-6 text-sm text-gray-500">Redirecionando para login...</div>;
  }

  return <>{children}</>;
}
