"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { isPublicMarketingRoute } from "@/lib/publicRoutes";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  // Public routes are explicitly allowlisted; authenticated app routes stay private.
  const isPublicRoute = isPublicMarketingRoute(pathname);

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
