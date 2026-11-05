"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import { isPublicMarketingRoute } from "@/lib/publicRoutes";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Public marketing pages skip the private app sidebar; login keeps its neutral shell.
  if (pathname === "/login") {
    return <main id="conteudo-principal" className="app-theme app-viewport app-main min-w-0 bg-gray-50 p-4 sm:p-6">{children}</main>;
  }

  if (isPublicMarketingRoute(pathname)) {
    return <>{children}</>;
  }

  return (
    <div className="app-theme app-viewport flex w-full min-w-0 bg-gray-50">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main id="conteudo-principal" className="app-main w-full min-w-0 flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
