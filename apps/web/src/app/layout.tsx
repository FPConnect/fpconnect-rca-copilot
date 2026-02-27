import type { Metadata } from "next";
import "./globals.css";

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
      <body>{children}</body>
    </html>
  );
}
