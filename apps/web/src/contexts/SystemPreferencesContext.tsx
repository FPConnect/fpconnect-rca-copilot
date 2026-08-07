"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export interface SystemPrefs {
  theme: "light" | "dark" | "system";
  language: "pt-BR" | "en-US";
  timezone: string;
  refreshRate: number;
}

interface SystemPreferencesContextValue {
  preferences: SystemPrefs;
  resolvedTheme: "light" | "dark";
  savePreferences: (next: SystemPrefs) => void;
  resetPreferences: () => void;
  formatDateTime: (
    value: string | number | Date,
    options?: Intl.DateTimeFormatOptions,
  ) => string;
}

const STORAGE_KEY = "fpconnect_system_preferences";

export const DEFAULT_SYSTEM_PREFS: SystemPrefs = {
  theme: "light",
  language: "pt-BR",
  timezone: "America/Sao_Paulo",
  refreshRate: 30,
};

const SystemPreferencesContext =
  createContext<SystemPreferencesContextValue | null>(null);

function coercePreferences(value: unknown): SystemPrefs {
  if (!value || typeof value !== "object") {
    return DEFAULT_SYSTEM_PREFS;
  }

  const input = value as Partial<SystemPrefs>;
  const theme =
    input.theme === "dark" || input.theme === "system"
      ? input.theme
      : "light";
  const language = input.language === "en-US" ? "en-US" : "pt-BR";
  const timezone =
    typeof input.timezone === "string" && input.timezone.trim()
      ? input.timezone.trim()
      : DEFAULT_SYSTEM_PREFS.timezone;
  const refreshRate = Number(input.refreshRate);

  return {
    theme,
    language,
    timezone,
    refreshRate: Number.isFinite(refreshRate) && refreshRate > 0
      ? refreshRate
      : DEFAULT_SYSTEM_PREFS.refreshRate,
  };
}

function readStoredPreferences(): SystemPrefs {
  if (typeof window === "undefined") {
    return DEFAULT_SYSTEM_PREFS;
  }

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return DEFAULT_SYSTEM_PREFS;
    }
    return coercePreferences(JSON.parse(raw));
  } catch {
    return DEFAULT_SYSTEM_PREFS;
  }
}

function resolveTheme(theme: SystemPrefs["theme"]): "light" | "dark" {
  if (theme === "system") {
    if (
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      return "dark";
    }
    return "light";
  }

  return theme;
}

export function SystemPreferencesProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [preferences, setPreferences] = useState<SystemPrefs>(readStoredPreferences);
  const [resolvedTheme, setResolvedTheme] = useState<"light" | "dark">(
    resolveTheme(readStoredPreferences().theme),
  );

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    } catch {
      // ignore storage errors
    }
  }, [preferences]);

  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;
    const nextResolvedTheme = resolveTheme(preferences.theme);

    setResolvedTheme(nextResolvedTheme);
    root.lang = preferences.language;
    root.dataset.theme = preferences.theme;
    root.dataset.resolvedTheme = nextResolvedTheme;
    root.dataset.timezone = preferences.timezone;
    root.dataset.refreshRate = String(preferences.refreshRate);
    root.classList.toggle("dark", nextResolvedTheme === "dark");
    body.classList.toggle("dark", nextResolvedTheme === "dark");
    body.style.colorScheme = nextResolvedTheme;
  }, [preferences]);

  useEffect(() => {
    if (preferences.theme !== "system" || !window.matchMedia) {
      return;
    }

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const sync = () => setResolvedTheme(media.matches ? "dark" : "light");

    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, [preferences.theme]);

  const savePreferences = useCallback((next: SystemPrefs) => {
    setPreferences(coercePreferences(next));
  }, []);

  const resetPreferences = useCallback(() => {
    setPreferences(DEFAULT_SYSTEM_PREFS);
  }, []);

  const formatDateTime = useCallback(
    (value: string | number | Date, options?: Intl.DateTimeFormatOptions) => {
      try {
        const date = value instanceof Date ? value : new Date(value);
        return new Intl.DateTimeFormat(preferences.language, {
          dateStyle: "short",
          timeStyle: "short",
          timeZone: preferences.timezone,
          ...options,
        }).format(date);
      } catch {
        return String(value);
      }
    },
    [preferences.language, preferences.timezone],
  );

  const contextValue = useMemo<SystemPreferencesContextValue>(
    () => ({
      preferences,
      resolvedTheme,
      savePreferences,
      resetPreferences,
      formatDateTime,
    }),
    [formatDateTime, preferences, resetPreferences, resolvedTheme, savePreferences],
  );

  return (
    <SystemPreferencesContext.Provider value={contextValue}>
      {children}
    </SystemPreferencesContext.Provider>
  );
}

export function useSystemPreferences(): SystemPreferencesContextValue {
  const ctx = useContext(SystemPreferencesContext);
  if (!ctx) {
    throw new Error(
      "useSystemPreferences must be used within SystemPreferencesProvider",
    );
  }
  return ctx;
}