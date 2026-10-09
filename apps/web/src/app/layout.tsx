import type { Metadata } from "next";
import "@fontsource-variable/manrope/wght.css";
import "./globals.css";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
import ToastManager from "@/components/ToastManager";
import AppShell from "@/components/AppShell";
import { AuthProvider } from "@/contexts/AuthContext";
import AuthGuard from "@/components/AuthGuard";
import LanguageRuntime from "@/components/LanguageRuntime";
import ThemeBootstrap from "@/components/ThemeBootstrap";
import { APP_NAME } from "@/lib/brand";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://fpconnect.tec.br";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: `${APP_NAME} | Inteligência operacional para a saúde`,
  description:
    "Dados, histórico técnico e contexto operacional para decisões mais rápidas e confiáveis em tecnologia para a saúde.",
  applicationName: APP_NAME,
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: APP_NAME,
    title: `${APP_NAME} | Performance de tecnologia em saúde`,
    description: "Inteligência operacional para equipes de engenharia clínica, assistência técnica e TI em saúde.",
    images: [{ url: "/brand/opspecta-social-card.jpeg", width: 828, height: 459, alt: `${APP_NAME} - Performance de tecnologia em saúde` }],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body>
        <ThemeBootstrap />
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
