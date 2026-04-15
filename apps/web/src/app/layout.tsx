import type { Metadata } from "next";
import "./globals.css";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
import ToastManager from "@/components/ToastManager";
import AppShell from "@/components/AppShell";
import { AuthProvider } from "@/contexts/AuthContext";
import AuthGuard from "@/components/AuthGuard";

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
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                var raw = localStorage.getItem('fpconnect_system_preferences');
                var theme = raw ? JSON.parse(raw).theme : 'light';
                var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                var useDark = theme === 'dark' || (theme === 'system' && prefersDark);
                document.documentElement.classList.toggle('dark', useDark);
                document.documentElement.dataset.theme = theme;
              } catch (_) {}
            `,
          }}
        />
      </head>
      <body>
        <AuthProvider>
          <AuthGuard>
            <NotificationProvider>
              <SidebarProvider>
                <AppShell>{children}</AppShell>
                <ToastManager />
              </SidebarProvider>
            </NotificationProvider>
          </AuthGuard>
        </AuthProvider>
      </body>
    </html>
  );
}
