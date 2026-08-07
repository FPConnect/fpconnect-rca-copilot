"use client";

import { Trash2, CheckCheck } from "lucide-react";
import { useNotifications } from "@/contexts/NotificationContext";
import type { NotificationType } from "@/contexts/NotificationContext";

const TYPE_LABELS: Record<NotificationType, string> = {
  success: "Sucesso",
  error: "Erro",
  warning: "Aviso",
  info: "Info",
};

const TYPE_STYLES: Record<
  NotificationType,
  { bg: string; badge: string; dot: string }
> = {
  success: {
    bg: "bg-green-50",
    badge: "bg-green-100 text-green-700",
    dot: "bg-green-500",
  },
  error: {
    bg: "bg-red-50",
    badge: "bg-red-100 text-red-700",
    dot: "bg-red-500",
  },
  warning: {
    bg: "bg-yellow-50",
    badge: "bg-yellow-100 text-yellow-700",
    dot: "bg-yellow-500",
  },
  info: {
    bg: "bg-blue-50",
    badge: "bg-blue-100 text-blue-700",
    dot: "bg-blue-500",
  },
};

function formatDate(iso: string): string {
  try {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

export default function NotificationsPage() {
  const { notifications, unreadCount, markAllRead, remove, clearAll } =
    useNotifications();

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notificações</h1>
          {unreadCount > 0 && (
            <p className="text-sm text-gray-500 mt-1">
              {unreadCount} não lida{unreadCount !== 1 ? "s" : ""}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              className="flex items-center gap-2 text-sm px-3 py-2 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
            >
              <CheckCheck size={16} />
              Marcar todas como lidas
            </button>
          )}
          {notifications.length > 0 && (
            <button
              onClick={clearAll}
              className="flex items-center gap-2 text-sm px-3 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors"
            >
              <Trash2 size={16} />
              Limpar tudo
            </button>
          )}
        </div>
      </div>

      {notifications.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-12 text-center">
          <p className="text-gray-400 text-lg">Nenhuma notificação.</p>
          <p className="text-gray-300 text-sm mt-1">
            As notificações aparecerão aqui.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => {
            const styles = TYPE_STYLES[n.type];
            return (
              <div
                key={n.id}
                className={`flex items-start gap-4 p-4 rounded-xl border ${
                  !n.read ? styles.bg : "bg-white"
                } border-gray-100 shadow-sm`}
              >
                <div
                  className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                    !n.read ? styles.dot : "bg-gray-300"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded-full ${styles.badge}`}
                    >
                      {TYPE_LABELS[n.type]}
                    </span>
                    {!n.read && (
                      <span className="text-xs font-medium text-blue-600">
                        Nova
                      </span>
                    )}
                  </div>
                  <p className="font-medium text-gray-900 text-sm">
                    {n.title}
                  </p>
                  {n.message && (
                    <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDate(n.createdAt)}
                  </p>
                </div>
                <button
                  onClick={() => remove(n.id)}
                  className="text-gray-300 hover:text-red-500 transition-colors flex-shrink-0"
                  aria-label="Remover notificação"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
