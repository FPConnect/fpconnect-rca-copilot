"use client";

import { useState } from "react";
import { Bell, User, ChevronDown, LogOut, Settings } from "lucide-react";

const MOCK_NOTIFICATIONS = [
  { id: 1, text: "MRI Scanner offline - Ward A", time: "2 min ago", unread: true },
  { id: 2, text: "ECG Monitor slow response", time: "15 min ago", unread: true },
  { id: 3, text: "Scheduled maintenance due", time: "1 hour ago", unread: false },
];

export default function Header() {
  const [notifOpen, setNotifOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
  const unreadCount = MOCK_NOTIFICATIONS.filter((n) => n.unread).length;

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-10">
      <h1 className="text-base font-semibold text-gray-700 hidden sm:block">
        Healthcare Equipment Monitor
      </h1>

      <div className="flex items-center gap-4 ml-auto">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => {
              setNotifOpen(!notifOpen);
              setUserOpen(false);
            }}
            className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
            aria-label="Notificações"
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>
          {notifOpen && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-20">
              <p className="px-4 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wide">
                Notificações
              </p>
              {MOCK_NOTIFICATIONS.map((n) => (
                <div
                  key={n.id}
                  className={`px-4 py-3 hover:bg-gray-50 cursor-pointer ${n.unread ? "bg-blue-50" : ""}`}
                >
                  <p className="text-sm text-gray-800">{n.text}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{n.time}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => {
              setUserOpen(!userOpen);
              setNotifOpen(false);
            }}
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
              <button className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                <Settings size={16} />
                Configurações
              </button>
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
