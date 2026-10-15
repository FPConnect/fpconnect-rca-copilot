"use client";

import Link from "next/link";
import { ShieldAlert } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function AccessGuard({
  minimum,
  children,
}: {
  minimum: number;
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="p-6 text-sm text-gray-500">Carregando permissões...</div>;
  }

  if (!user || (user.access_level ?? 0) < minimum) {
    return (
      <section role="alert" className="mx-auto max-w-xl border border-amber-200 bg-amber-50 p-6 text-amber-950 shadow-sm">
        <ShieldAlert className="mb-3" aria-hidden="true" />
        <h1 className="text-xl font-bold">Acesso restrito</h1>
        <p className="mt-2 text-sm">
          Sua conta não possui permissão para acessar este módulo.
        </p>
        <Link className="mt-5 inline-flex font-semibold text-blue-700 hover:underline" href="/dashboard">
          Voltar ao dashboard
        </Link>
      </section>
    );
  }

  return <>{children}</>;
}
