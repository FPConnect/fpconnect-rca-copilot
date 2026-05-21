"use client";

import { useState } from "react";
import { Bell, User, ChevronDown, LogOut, Settings, Menu, Search, HelpCircle } from "lucide-react";
import Link from "next/link";
import { useNotifications } from "@/contexts/NotificationContext";
import { useSidebar } from "@/contexts/SidebarContext";
import { useAuth } from "@/contexts/AuthContext";

export default function Header() {
  const [userOpen, setUserOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { unreadCount, markAllRead } = useNotifications();
  const { toggle } = useSidebar();
  const { logout } = useAuth();

  const faqQuestions = [
    { q: "Como cadastrar um novo equipamento?", a: "Acesse o menu Máquinas e clique em 'Novo Equipamento'." },
    { q: "Como visualizar alertas?", a: "Clique no ícone de sino no cabeçalho para ver todos os alertas." },
    { q: "Como gerar relatórios?", a: "Acesse o menu Métricas e selecione o período desejado." },
    { q: "Como abrir um chamado?", a: "Vá em Tickets e clique em 'Novo Ticket'." },
    { q: "Como configurar notificações?", a: "Acesse Configurações > Notificações para personalizar." },
  ];

  const filteredFAQs = faqQuestions.filter(
    (item) =>
      item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.a.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 md:px-6 sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          aria-label="Abrir menu"
        >
          <Menu size={20} />
        </button>
        <h1 className="text-base font-semibold text-gray-700 hidden sm:block">
          Healthcare Equipment Monitor
        </h1>
      </div>

      <div className="flex items-center gap-4 ml-auto">
        {/* Search Bar */}
        <div className="relative">
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
            aria-label="Buscar"
          >
            <Search size={20} />
          </button>
          {searchOpen && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-100 py-3 px-4 z-20">
              <input
                type="text"
                placeholder="Buscar nas FAQs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <div className="mt-3 max-h-64 overflow-y-auto">
                {filteredFAQs.length > 0 ? (
                  filteredFAQs.map((item, idx) => (
                    <div key={idx} className="mb-3 pb-3 border-b border-gray-100 last:border-0 last:mb-0 last:pb-0">
                      <p className="text-sm font-medium text-gray-800">{item.q}</p>
                      <p className="text-xs text-gray-500 mt-1">{item.a}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 text-center py-2">Nenhuma pergunta encontrada.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* FAQ Link */}
        <Link
          href="#faq"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
        >
          <HelpCircle size={20} />
          <span className="text-sm font-medium hidden sm:block">Ajuda / FAQs</span>
        </Link>

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
              <button
                onClick={() => { logout(); setUserOpen(false); }}
                className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-50"
              >
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
