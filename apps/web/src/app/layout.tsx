import type { Metadata } from "next";
import "./globals.css";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
import { SystemPreferencesProvider } from "@/contexts/SystemPreferencesContext";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
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
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="bg-gray-50 text-gray-900 transition-colors dark:bg-gray-950 dark:text-gray-100">
        <SystemPreferencesProvider>
          <NotificationProvider>
            <SidebarProvider>
              <div className="flex min-h-screen bg-gray-50 transition-colors dark:bg-gray-950">
                <Sidebar />
                <div className="flex-1 flex flex-col min-w-0">
                  <Header />
                  <main className="flex-1 p-6">{children}</main>
                </div>
              </div>
              <ToastManager />
            </SidebarProvider>
          </NotificationProvider>
        </SystemPreferencesProvider>
      </body>
    </html>
  );
}
