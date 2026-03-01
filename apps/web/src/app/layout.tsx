import type { Metadata } from "next";
import "./globals.css";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
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
    <html lang="en">
      <body>
        <NotificationProvider>
          <SidebarProvider>
            <div className="flex min-h-screen bg-gray-50">
              <Sidebar />
              <div className="flex-1 flex flex-col min-w-0">
                <Header />
                <main className="flex-1 p-6">{children}</main>
              </div>
            </div>
            <ToastManager />
          </SidebarProvider>
        </NotificationProvider>
      </body>
    </html>
  );
}
