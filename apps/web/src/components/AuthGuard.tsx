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

    if (!isAuthenticated && pathname !== "/login") {
      router.replace("/login");
    }

    if (isAuthenticated && pathname === "/login") {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) {
    return <div className="p-6 text-sm text-gray-500">Carregando sessão...</div>;
  }

  if (!isAuthenticated && pathname !== "/login") {
    return <div className="p-6 text-sm text-gray-500">Redirecionando para login...</div>;
  }

  return <>{children}</>;
}
