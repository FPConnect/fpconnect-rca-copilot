"use client";

import { X } from "lucide-react";
import { useEffect, useRef } from "react";
import type { Notification, NotificationType } from "@/contexts/NotificationContext";

const TYPE_STYLES: Record<
  NotificationType,
  { bg: string; border: string; icon: string; title: string }
> = {
  success: {
    bg: "bg-green-50",
    border: "border-green-400",
    icon: "✓",
    title: "text-green-800",
  },
  error: {
    bg: "bg-red-50",
    border: "border-red-400",
    icon: "✕",
    title: "text-red-800",
  },
  warning: {
    bg: "bg-yellow-50",
    border: "border-yellow-400",
    icon: "⚠",
    title: "text-yellow-800",
  },
  info: {
    bg: "bg-blue-50",
    border: "border-blue-400",
    icon: "ℹ",
    title: "text-blue-800",
  },
};

interface ToastItemProps {
  notification: Notification;
  onRemove: (id: string) => void;
}

function ToastItem({ notification, onRemove }: ToastItemProps) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    timerRef.current = setTimeout(() => onRemove(notification.id), 5000);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [notification.id, onRemove]);

  const styles = TYPE_STYLES[notification.type];

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-xl shadow-lg border-l-4 ${styles.bg} ${styles.border} max-w-sm w-full animate-in slide-in-from-right`}
      role="alert"
    >
      <span className={`text-lg font-bold ${styles.title}`}>
        {styles.icon}
      </span>
      <div className="flex-1 min-w-0">
        <p className={`font-semibold text-sm ${styles.title}`}>
          {notification.title}
        </p>
        {notification.message && (
          <p className="text-xs text-gray-600 mt-0.5">{notification.message}</p>
        )}
      </div>
      <button
        onClick={() => onRemove(notification.id)}
        className="text-gray-400 hover:text-gray-600 flex-shrink-0"
        aria-label="Fechar notificação"
      >
        <X size={16} />
      </button>
    </div>
  );
}

interface ToastContainerProps {
  notifications: Notification[];
  onRemove: (id: string) => void;
}

export default function ToastContainer({
  notifications,
  onRemove,
}: ToastContainerProps) {
  const toasts = notifications.filter((n) => !n.read).slice(0, 5);
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((n) => (
        <ToastItem key={n.id} notification={n} onRemove={onRemove} />
      ))}
    </div>
  );
}
