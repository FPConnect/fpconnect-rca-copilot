"use client";

import { useLayoutEffect } from "react";

const PREFERENCES_KEY = "fpconnect_system_preferences";

export default function ThemeBootstrap() {
  useLayoutEffect(() => {
    try {
      const raw = localStorage.getItem(PREFERENCES_KEY);
      const theme = raw ? JSON.parse(raw).theme : "light";
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      const useDark = theme === "dark" || (theme === "system" && prefersDark);
      document.documentElement.classList.toggle("dark", useDark);
      document.documentElement.dataset.theme = theme;
    } catch {
      document.documentElement.dataset.theme = "light";
    }
  }, []);

  return null;
}
