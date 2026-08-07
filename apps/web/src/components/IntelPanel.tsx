"use client";

import { useEffect, useMemo, useState } from "react";
import { RefreshCw, Radar, Languages, Filter } from "lucide-react";

import { api, IntelItem } from "@/services/api";
import { useNotifications } from "@/contexts/NotificationContext";
import { useSystemPreferences } from "@/contexts/SystemPreferencesContext";

type Lang = "pt" | "en";

export default function IntelPanel() {
  const [items, setItems] = useState<IntelItem[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [topic, setTopic] = useState<string>("");
  const [lang, setLang] = useState<Lang>("pt");
  const [busy, setBusy] = useState(false);
  const { addNotification } = useNotifications();
  const { preferences, formatDateTime } = useSystemPreferences();

  async function loadTopics() {
    try {
      const t = await api.getIntelTopics();
      setTopics(t.topics || []);
    } catch {
      // ignore
    }
  }

  async function loadItems() {
    setBusy(true);
    try {
      const data = await api.getIntelItems(topic || undefined, 50);
      setItems(data);
    } catch {
      addNotification(
        "error",
        "Radar indisponível",
        "Não foi possível carregar o Radar. Verifique o backend (API).",
      );
    } finally {
      setBusy(false);
    }
  }

  async function runIngest() {
    setBusy(true);
    try {
      const r = await api.runIntelIngestOnce();
      addNotification(
        "success",
        "Radar atualizado",
        `Ingest concluído: ${r.inserted} novos, ${r.skipped} repetidos.`,
      );
      await loadItems();
    } catch {
      addNotification(
        "error",
        "Falha no ingest",
        "Não foi possível atualizar as fontes. Tente novamente.",
      );
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    loadTopics();
    loadItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setLang(preferences.language === "en-US" ? "en" : "pt");
  }, [preferences.language]);

  useEffect(() => {
    loadItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topic]);

  useEffect(() => {
    if (!preferences.refreshRate || preferences.refreshRate <= 0) {
      return;
    }

    const timer = window.setInterval(() => {
      loadItems();
    }, preferences.refreshRate * 1000);

    return () => window.clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preferences.refreshRate, topic]);

  const rendered = useMemo(() => {
    return items.map((it) => {
      const summary = lang === "pt" ? it.summary_pt : it.summary_en;
      const when = it.published_at ? formatDateTime(it.published_at) : "";
      return (
        <div key={it.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="text-xs text-gray-500">
                {it.source}
                {it.topic ? <span> • {it.topic}</span> : null}
                {when ? <span> • {when}</span> : null}
              </div>
              <h3 className="mt-1 text-sm font-semibold text-gray-900 break-words">
                {it.title}
              </h3>
            </div>
            <a
              className="text-xs text-blue-600 hover:underline whitespace-nowrap"
              href={it.url}
              target="_blank"
              rel="noreferrer"
            >
              Abrir
            </a>
          </div>
          {summary ? (
            <p className="mt-3 text-sm text-gray-600 leading-relaxed">{summary}</p>
          ) : (
            <p className="mt-3 text-sm text-gray-400">
              Sem resumo disponível.
            </p>
          )}
        </div>
      );
    });
  }, [formatDateTime, items, lang]);

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-col md:flex-row md:items-center gap-3">
        <div className="flex items-center gap-2 text-gray-800 font-semibold">
          <Radar size={18} className="text-blue-600" />
          Radar (Intel)
        </div>

        <div className="flex-1" />

        <div className="flex flex-wrap gap-2 items-center">
          <button
            onClick={runIngest}
            disabled={busy}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
          >
            <RefreshCw size={16} className={busy ? "animate-spin" : ""} />
            Atualizar fontes
          </button>

          <div className="relative">
            <Filter size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="pl-9 pr-3 py-2 rounded-lg border border-gray-200 text-sm bg-white"
            >
              <option value="">Todos os tópicos</option>
              {topics.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setLang(lang === "pt" ? "en" : "pt")}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white hover:bg-gray-50"
            aria-label="Trocar idioma"
          >
            <Languages size={16} className="text-gray-500" />
            {lang === "pt" ? "PT" : "EN"}
          </button>

          <button
            onClick={loadItems}
            disabled={busy}
            className="px-3 py-2 rounded-lg border border-gray-200 text-sm bg-white hover:bg-gray-50 disabled:opacity-60"
          >
            Recarregar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">{rendered}</div>
      {!busy && items.length === 0 ? (
        <div className="text-sm text-gray-500">
          Nenhum item ainda. Clique em <b>Atualizar fontes</b> para ingerir.
        </div>
      ) : null}
    </div>
  );
}
