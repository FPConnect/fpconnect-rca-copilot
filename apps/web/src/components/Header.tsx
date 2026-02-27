"use client";

import { useState } from "react";
import { Bell, User, ChevronDown, LogOut, Settings } from "lucide-react";
import Link from "next/link";
import { useNotifications } from "@/contexts/NotificationContext";

export default function Header() {
  const [userOpen, setUserOpen] = useState(false);
  const { unreadCount, markAllRead } = useNotifications();

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-10">
      <h1 className="text-base font-semibold text-gray-700 hidden sm:block">
        Healthcare Equipment Monitor
      </h1>

      <div className="flex items-center gap-4 ml-auto">
        {/* Notifications */}
        <Link
          href="/notifications"
          onClick={markAllRead}
          className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          aria-label={`Notificações${unreadCount > 0 ? ` (${unreadCount} não lidas)` : ""}`}
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </Link>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setUserOpen(!userOpen)}
            className="flex items-center gap-2 p-1.5 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="Menu do usuário"
          >
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
              <User size={16} className="text-white" />
            </div>
            <span className="text-sm font-medium hidden sm:block">Admin</span>
            <ChevronDown size={16} />
          </button>
          {userOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-20">
              <Link
                href="/settings"
                onClick={() => setUserOpen(false)}
                className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                <Settings size={16} />
                Configurações
              </Link>
              <button className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-50">
                <LogOut size={16} />
                Sair
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

