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
  Ticket,
} from "lucide-react";
import { useNotifications } from "@/contexts/NotificationContext";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/machines", label: "Máquinas", icon: Monitor },
  { href: "/health-checks", label: "Health Checks", icon: HeartPulse },
  { href: "/alerts", label: "Alertas", icon: Bell },
  { href: "/tickets", label: "Tickets", icon: Ticket },
  { href: "/metrics", label: "Métricas", icon: BarChart2 },
  { href: "/maintenance", label: "Manutenção", icon: Wrench },
  { href: "/access-control", label: "Controle de Acesso", icon: ShieldCheck },
  { href: "/history", label: "Histórico", icon: History },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { unreadCount } = useNotifications();

  return (
    <aside className="w-64 min-h-screen bg-gray-900 text-white flex flex-col">
      <div className="px-6 py-5 border-b border-gray-700">
        <span className="text-xl font-bold tracking-tight text-blue-400">
          FPConnect
        </span>
        <span className="block text-xs text-gray-400 mt-0.5">Technologies</span>
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
        <Link
          href="/notifications"
          className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            pathname === "/notifications"
              ? "bg-blue-600 text-white"
              : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <Bell size={18} />
          <span className="flex-1">Notificações</span>
          {unreadCount > 0 && (
            <span className="px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </Link>
      </nav>
      <div className="px-3 py-4 border-t border-gray-700">
        <Link
          href="/settings"
          className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            pathname === "/settings"
              ? "bg-blue-600 text-white"
              : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <Settings size={18} />
          Configurações
        </Link>
      </div>
    </aside>
  );
}

