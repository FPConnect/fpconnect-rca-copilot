"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Monitor,
  HeartPulse,
  Bell,
  BarChart2,
  Wrench,
  ShieldCheck,
  History,
  Settings,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/machines", label: "Máquinas", icon: Monitor },
  { href: "/health-checks", label: "Health Checks", icon: HeartPulse },
  { href: "/alerts", label: "Alertas", icon: Bell },
  { href: "/metrics", label: "Métricas", icon: BarChart2 },
  { href: "/maintenance", label: "Manutenção", icon: Wrench },
  { href: "/access-control", label: "Controle de Acesso", icon: ShieldCheck },
  { href: "/history", label: "Histórico", icon: History },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-gray-900 text-white flex flex-col">
      <div className="px-6 py-5 border-b border-gray-700">
        <span className="text-xl font-bold tracking-tight text-blue-400">
          FPConnect
        </span>
        <span className="block text-xs text-gray-400 mt-0.5">RCA Copilot</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-blue-600 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="px-3 py-4 border-t border-gray-700">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <Settings size={18} />
          Configurações
        </Link>
      </div>
    </aside>
  );
}
