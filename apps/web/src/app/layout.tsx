import type { Metadata } from "next";
import "./globals.css";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
import ToastManager from "@/components/ToastManager";
import AppShell from "@/components/AppShell";
import { AuthProvider } from "@/contexts/AuthContext";
import AuthGuard from "@/components/AuthGuard";
import LanguageRuntime from "@/components/LanguageRuntime";
import { APP_NAME } from "@/lib/brand";

export const metadata: Metadata = {
  title: `${APP_NAME} | Assistência técnica MedTech`,
  description:
    "Organize chamados, histórico técnico e acompanhamento de disponibilidade para apoiar a equipe de assistência técnica MedTech.",
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
                <LanguageRuntime />
              </SidebarProvider>
            </NotificationProvider>
          </AuthGuard>
        </AuthProvider>
      </body>
    </html>
  );
}
