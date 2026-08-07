"use client";

import { useEffect, useState } from "react";
import { Languages } from "lucide-react";
import { notifyLanguageChanged } from "@/components/LanguageRuntime";

const SYSTEM_STORAGE_KEY = "fpconnect_system_preferences";

type Language = "pt-BR" | "en-US";

function readLanguage(): Language {
  try {
    const raw = localStorage.getItem(SYSTEM_STORAGE_KEY);
    const language = raw ? JSON.parse(raw).language : "pt-BR";
    return language === "en-US" ? "en-US" : "pt-BR";
  } catch {
    return "pt-BR";
  }
}

function writeLanguage(language: Language) {
  try {
    const raw = localStorage.getItem(SYSTEM_STORAGE_KEY);
    const current = raw ? JSON.parse(raw) : {};
    localStorage.setItem(
      SYSTEM_STORAGE_KEY,
      JSON.stringify({ ...current, language }),
    );
  } catch {
    localStorage.setItem(SYSTEM_STORAGE_KEY, JSON.stringify({ language }));
  }
}

export default function LandingLanguageSwitcher() {
  const [language, setLanguage] = useState<Language>("pt-BR");

  useEffect(() => {
    setLanguage(readLanguage());
  }, []);

  const selectLanguage = (nextLanguage: Language) => {
    setLanguage(nextLanguage);
    writeLanguage(nextLanguage);
    notifyLanguageChanged();
  };

  return (
    <div
      className="inline-flex items-center gap-1 rounded-full border border-slate-700 bg-slate-900/70 p-1 text-xs font-bold text-slate-200 shadow-lg shadow-slate-950/30"
      data-no-translate
      aria-label="Selecionar idioma"
    >
      <Languages size={14} className="ml-2 text-cyan-300" aria-hidden="true" />
      {[
        { value: "pt-BR" as const, label: "Português" },
        { value: "en-US" as const, label: "English" },
      ].map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={language === option.value}
          onClick={() => selectLanguage(option.value)}
          className={`min-w-20 rounded-full px-3 py-1.5 transition ${
            language === option.value
              ? "bg-cyan-400 text-slate-950"
              : "text-slate-300 hover:bg-slate-800 hover:text-white"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
