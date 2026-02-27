"use client";

import { useNotifications } from "@/contexts/NotificationContext";
import ToastContainer from "@/components/Toast";

export default function ToastManager() {
  const { notifications, markRead } = useNotifications();

  return (
    <ToastContainer
      notifications={notifications}
      onRemove={markRead}
    />
  );
}
