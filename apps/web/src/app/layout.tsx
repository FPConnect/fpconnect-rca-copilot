import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import { NotificationProvider } from "@/contexts/NotificationContext";
import ToastManager from "@/components/ToastManager";

export const metadata: Metadata = {
  title: "FPConnect RCA Copilot",
  description: "RCA Copilot & Availability Engine for Healthcare/MedTech",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-gray-50">
        <NotificationProvider>
          <Sidebar />
          <div className="flex flex-col flex-1 min-w-0">
            <Header />
            <main className="flex-1 p-6 overflow-auto">{children}</main>
          </div>
          <ToastManager />
        </NotificationProvider>
      </body>
    </html>
  );
}
