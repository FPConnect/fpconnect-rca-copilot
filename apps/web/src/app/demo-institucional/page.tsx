"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  BellRing,
  ClipboardList,
  FileText,
  Maximize2,
  Mic,
  MicOff,
  Pause,
  Play,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  TicketPlus,
} from "lucide-react";

import FPConnectLogo from "@/components/FPConnectLogo";
import { DEMO_STEPS, KPI_EXPLANATIONS, type SceneId } from "@/lib/demo-institucional";

function cx(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

function SceneNavigation({ scene }: { scene: SceneId }) {
  const items: Array<{ key: SceneId; label: string }> = [
    { key: "dashboard", label: "Painel" },
    { key: "tickets", label: "Tickets" },
    { key: "logs", label: "Logs" },
    { key: "metrics", label: "Relatórios" },
    { key: "roi", label: "ROI" },
  ];

  return (
    <aside className="flex h-full flex-col justify-between border-r border-white/10 bg-slate-950/85 p-5 text-white">
      <div>
        <FPConnectLogo subtitle="Demo institucional" theme="dark" size="sm" />
        <div className="mt-8 space-y-2 text-sm">
          {items.map((item) => (
            <div
              key={item.key}
              className={cx(
                "rounded-2xl px-4 py-3 transition",
                scene === item.key ? "bg-cyan-400/15 text-white ring-1 ring-cyan-300/40" : "text-slate-300",
              )}
            >
              {item.label}
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4 text-xs text-cyan-100">
        Modo cliente ativo<br />
        Cursor guiado, legenda institucional e narração automática.
      </div>
    </aside>
  );
}

function DashboardScene({ highlight }: { highlight: boolean }) {
  const cards = [
    { label: "Tickets abertos", value: "12", tone: "bg-amber-50 text-amber-900" },
    { label: "Em progresso", value: "5", tone: "bg-blue-50 text-blue-900" },
    { label: "Resolvidos hoje", value: "8", tone: "bg-emerald-50 text-emerald-900" },
    { label: "Críticos", value: "2", tone: "bg-rose-50 text-rose-900" },
  ];

  return (
    <div className="space-y-5 p-6">
      <div className="rounded-[28px] bg-gradient-to-r from-slate-950 via-blue-950 to-cyan-900 p-6 text-white shadow-2xl">
        <div className="inline-flex rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-cyan-100">
          Demo online para clientes
        </div>
        <h2 className="mt-4 max-w-3xl text-3xl font-semibold leading-tight">
          Demonstre risco, indisponibilidade e valor de resposta em menos de um minuto.
        </h2>
      </div>
      <div className="grid grid-cols-4 gap-4">
        {cards.map((card, index) => {
          const isFocus = highlight && index === 3;
          return (
            <div
              key={card.label}
              className={cx(
                "rounded-3xl p-5 shadow-sm transition",
                card.tone,
                isFocus && "ring-4 ring-cyan-300 shadow-[0_0_0_10px_rgba(34,211,238,0.12)]",
              )}
            >
              <div className="text-xs uppercase tracking-wide opacity-70">{card.label}</div>
              <div className="mt-2 text-4xl font-bold">{card.value}</div>
            </div>
          );
        })}
      </div>
      <div className="grid grid-cols-[1.3fr_1fr] gap-4">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm font-semibold text-slate-900">Narrativa de venda</div>
          <div className="mt-4 space-y-3 text-sm text-slate-600">
            <div className="rounded-2xl bg-slate-50 p-4">1. Abrimos pela dor operacional que gera pressão no contrato e na equipe.</div>
            <div className="rounded-2xl bg-slate-50 p-4">2. Comprovamos capacidade de reação com ticket, rastreabilidade e relatório.</div>
            <div className="rounded-2xl bg-slate-50 p-4">3. Fechamos em ROI, expansão e material executivo para comitê.</div>
          </div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm font-semibold text-slate-900">Ativos sob pressão</div>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-2xl bg-rose-50 px-4 py-3 text-rose-900">
              <span>MRI Scanner</span>
              <span>Risco alto</span>
            </div>
            <div className="flex items-center justify-between rounded-2xl bg-amber-50 px-4 py-3 text-amber-900">
              <span>ECG Monitor</span>
              <span>Latência</span>
            </div>
            <div className="flex items-center justify-between rounded-2xl bg-emerald-50 px-4 py-3 text-emerald-900">
              <span>Ventilator</span>
              <span>Estável</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TicketsScene({ mode }: { mode: "create" | "triage" }) {
  const highlightCreate = mode === "create";
  const highlightRow = mode === "triage";

  return (
    <div className="grid h-full grid-cols-[1.05fr_1.2fr] gap-5 p-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <TicketPlus size={18} className="text-blue-600" />
          Novo ticket
        </div>
        <div className="mt-5 space-y-4 text-sm">
          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Título</div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-800">
              Tomógrafo da UTI com falha intermitente e risco de parada
            </div>
          </div>
          <div>
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Descrição</div>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700">
              Equipamento apresentou oscilação no módulo de resfriamento durante a rotina de exames.
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-rose-900">
              Prioridade sugerida: crítica
            </div>
            <div className="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-blue-900">
              Resolução prevista: 2h
            </div>
          </div>
          <button
            type="button"
            className={cx(
              "w-full rounded-2xl px-4 py-3 text-sm font-semibold text-white transition",
              highlightCreate ? "bg-blue-700 ring-4 ring-cyan-300" : "bg-blue-600",
            )}
          >
            Criar ticket
          </button>
        </div>
      </div>
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <ShieldAlert size={18} className="text-rose-600" />
          Fila priorizada
        </div>
        <div className="mt-5 space-y-3 text-sm">
          {[
            {
              id: "FP-248",
              title: "Tomógrafo da UTI com falha intermitente",
              priority: "Crítico",
              eta: "2h",
            },
            { id: "FP-241", title: "Latência no ECG do bloco cirúrgico", priority: "Alto", eta: "6h" },
            { id: "FP-239", title: "Alarme recorrente no ventilador reserva", priority: "Médio", eta: "12h" },
          ].map((ticket, index) => {
            const isFocus = highlightRow && index === 0;
            return (
              <div
                key={ticket.id}
                className={cx(
                  "rounded-2xl border border-slate-200 px-4 py-4 transition",
                  isFocus && "border-cyan-300 bg-cyan-50 ring-4 ring-cyan-200/70",
                )}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">{ticket.id}</div>
                    <div className="mt-1 font-semibold text-slate-900">{ticket.title}</div>
                  </div>
                  <div className="text-right">
                    <div className={cx(
                      "rounded-full px-3 py-1 text-xs font-semibold",
                      index === 0 ? "bg-rose-100 text-rose-900" : index === 1 ? "bg-amber-100 text-amber-900" : "bg-blue-100 text-blue-900",
                    )}>
                      {ticket.priority}
                    </div>
                    <div className="mt-2 text-xs text-slate-500">ETA {ticket.eta}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function LogsScene({ highlight }: { highlight: boolean }) {
  const rows = [
    ["Ticket criado", "Ana Lima", "Tomógrafo da UTI", "10/03 09:42"],
    ["Prioridade recalculada", "Sistema", "Risco crítico", "10/03 09:43"],
    ["Alerta reconhecido", "Carlos Rocha", "MRI Scanner", "10/03 09:45"],
    ["Exportação PDF", "Maria Santos", "Histórico completo", "10/03 09:48"],
  ];

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div>
          <div className="text-sm font-semibold text-slate-900">Histórico de incidentes</div>
          <div className="mt-1 text-sm text-slate-500">Rastro completo para operação, auditoria e qualidade.</div>
        </div>
        <div className="flex gap-3 text-sm">
          {[
            { label: "Exportar PDF", tone: "bg-blue-600 text-white", active: highlight },
            { label: "Exportar Excel", tone: "bg-emerald-600 text-white" },
            { label: "Exportar PNG", tone: "bg-slate-200 text-slate-900" },
          ].map((action) => (
            <button
              key={action.label}
              type="button"
              className={cx(
                "rounded-2xl px-4 py-2.5 font-semibold transition",
                action.tone,
                action.active && "ring-4 ring-cyan-300",
              )}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid grid-cols-[1.1fr_0.9fr_1fr_0.8fr] gap-3 border-b border-slate-200 pb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <div>Ação</div>
          <div>Usuário</div>
          <div>Recurso</div>
          <div>Data</div>
        </div>
        <div className="mt-3 space-y-2 text-sm">
          {rows.map((row, index) => (
            <div
              key={row.join("-")}
              className={cx(
                "grid grid-cols-[1.1fr_0.9fr_1fr_0.8fr] gap-3 rounded-2xl px-4 py-3 text-slate-700",
                index === 0 ? "bg-cyan-50 text-cyan-950" : "bg-slate-50",
                highlight && index === 0 && "ring-4 ring-cyan-200/70",
              )}
            >
              {row.map((cell) => (
                <div key={cell}>{cell}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricsScene({ highlightCards, highlightExport }: { highlightCards: boolean; highlightExport: boolean }) {
  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-900">Métricas de performance</div>
          <div className="mt-1 text-sm text-slate-500">Leitura guiada para operação, engenharia clínica e diretoria.</div>
        </div>
        <button
          type="button"
          className={cx(
            "rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition",
            highlightExport && "ring-4 ring-cyan-300",
          )}
        >
          Exportar relatório
        </button>
      </div>
      <div className="grid grid-cols-4 gap-4">
        {KPI_EXPLANATIONS.map((item) => (
          <div
            key={item.label}
            className={cx(
              "rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition",
              highlightCards && "ring-4 ring-cyan-200/70",
            )}
          >
            <div className="text-xs uppercase tracking-wide text-slate-400">{item.label}</div>
            <div className="mt-3 text-3xl font-bold text-slate-900">{item.value}</div>
            <div className="mt-3 text-sm leading-relaxed text-slate-600">{item.description}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-[1.15fr_0.85fr] gap-4">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm font-semibold text-slate-900">Uptime por equipamento</div>
          <div className="mt-4 space-y-3">
            {[
              ["MRI Scanner", 99],
              ["ECG Monitor", 94],
              ["Ventilator", 100],
              ["Defibrillator", 78],
            ].map(([label, value]) => (
              <div key={String(label)}>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-600">
                  <span>{label}</span>
                  <span>{value}%</span>
                </div>
                <div className="h-3 rounded-full bg-slate-100">
                  <div
                    className={cx(
                      "h-3 rounded-full",
                      Number(value) >= 99 ? "bg-emerald-500" : Number(value) >= 90 ? "bg-amber-400" : "bg-rose-500",
                    )}
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-slate-950 p-5 text-white shadow-sm">
          <div className="text-sm font-semibold text-cyan-100">Como vender essa leitura</div>
          <div className="mt-4 space-y-3 text-sm text-slate-200">
            <div className="rounded-2xl bg-white/5 p-4">Uptime alto significa continuidade assistencial e menor interrupção de agenda clínica.</div>
            <div className="rounded-2xl bg-white/5 p-4">MTBF traduz confiabilidade técnica e previsibilidade para manutenção baseada em risco.</div>
            <div className="rounded-2xl bg-white/5 p-4">MTTR curto mostra velocidade de resposta e capacidade de proteger SLA.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function RoiScene({ highlight }: { highlight: boolean }) {
  return (
    <div className="grid h-full grid-cols-[1.15fr_0.85fr] gap-5 p-6">
      <div className="rounded-[30px] bg-gradient-to-br from-slate-950 via-blue-950 to-cyan-900 p-7 text-white shadow-2xl">
        <div className="inline-flex rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-cyan-100">
          Fechamento comercial
        </div>
        <h2 className="mt-5 text-4xl font-semibold leading-tight">
          Transforme disponibilidade protegida em expansão contratual.
        </h2>
        <div className="mt-6 grid grid-cols-3 gap-3 text-sm">
          {[
            ["Economia estimada", "R$ 142,3 mil"],
            ["Downtime evitado", "48 horas"],
            ["ROI anual", "137%"],
          ].map(([label, value], index) => (
            <div
              key={String(label)}
              className={cx(
                "rounded-3xl border border-white/10 bg-white/10 p-4 backdrop-blur-sm",
                highlight && index === 2 && "ring-4 ring-cyan-300",
              )}
            >
              <div className="text-xs uppercase tracking-wide text-cyan-100/80">{label}</div>
              <div className="mt-2 text-2xl font-bold">{value}</div>
            </div>
          ))}
        </div>
        <div className="mt-6 rounded-3xl border border-white/10 bg-white/10 p-5 text-sm text-slate-100">
          O material já sai pronto para diretoria, engenharia clínica e coordenação operacional, encurtando o caminho entre demonstração, proposta e aprovação.
        </div>
      </div>
      <div className="space-y-4">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm font-semibold text-slate-900">Mensagem final para o cliente</div>
          <div className="mt-4 space-y-3 text-sm text-slate-600">
            <div className="rounded-2xl bg-slate-50 p-4">Menos indisponibilidade não planejada.</div>
            <div className="rounded-2xl bg-slate-50 p-4">Mais previsibilidade para equipes clínicas e manutenção.</div>
            <div className="rounded-2xl bg-slate-50 p-4">Mais argumento executivo para renovação e ampliação de escopo.</div>
          </div>
        </div>
        <button
          type="button"
          className="flex w-full items-center justify-center gap-2 rounded-3xl bg-slate-950 px-5 py-4 text-sm font-semibold text-white"
        >
          Avançar para proposta comercial
          <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
}

export default function DemoInstitucionalPage() {
  const [stepIndex, setStepIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [audioStatus, setAudioStatus] = useState<"ready" | "loading" | "playing" | "error">("ready");
  const [audioProvider, setAudioProvider] = useState("Narração humana via TTS");
  const frameRef = useRef<HTMLDivElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const currentStep = DEMO_STEPS[stepIndex];

  useEffect(() => {
    if (isPaused) {
      return;
    }

    const timer = window.setTimeout(() => {
      setStepIndex((current) => (current + 1) % DEMO_STEPS.length);
    }, currentStep.durationMs);

    return () => {
      window.clearTimeout(timer);
    };
  }, [currentStep.durationMs, isPaused]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }

    audio.pause();
    audio.currentTime = 0;
    if (isMuted || isPaused) {
      setAudioStatus("ready");
      return;
    }

    const audioUrl = `/api/demo-narration?step=${encodeURIComponent(currentStep.id)}`;
    setAudioStatus("loading");
    setAudioProvider("Narração humana via TTS");
    audio.src = audioUrl;
    const playPromise = audio.play();
    if (playPromise) {
      playPromise
        .then(() => {
          setAudioStatus("playing");
        })
        .catch(async () => {
          try {
            const response = await fetch(audioUrl, { cache: "no-store" });
            const payload = await response.json();
            setAudioStatus("error");
            setAudioProvider(
              payload?.error === "Human narration provider not configured"
                ? "Configure OPENAI_API_KEY para voz humana"
                : "Falha ao carregar narração humana",
            );
          } catch {
            setAudioStatus("error");
            setAudioProvider("Falha ao carregar narração humana");
          }
        });
    }

    return () => {
      audio.pause();
      audio.currentTime = 0;
    };
  }, [currentStep.id, isMuted, isPaused]);

  async function toggleFullscreen() {
    if (!frameRef.current) {
      return;
    }

    if (document.fullscreenElement) {
      await document.exitFullscreen();
      return;
    }

    await frameRef.current.requestFullscreen();
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.12),_transparent_22%),linear-gradient(135deg,_#f5f7fb_0%,_#e9eef7_50%,_#dbe6f4_100%)] px-6 py-8 text-slate-900">
      <audio
        ref={audioRef}
        preload="auto"
        onPlaying={() => setAudioStatus("playing")}
        onEnded={() => setAudioStatus("ready")}
        onPause={() => setAudioStatus((current) => (current === "error" ? current : "ready"))}
        onError={() => {
          setAudioStatus("error");
          setAudioProvider("Falha ao carregar narração humana");
        }}
      />
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-200 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-800">
              <Sparkles size={14} />
              Demo institucional autoplay
            </div>
            <h1 className="mt-4 max-w-4xl text-4xl font-semibold leading-tight text-slate-950">
              Simulação passo a passo para apresentar o FPConnect como um produto pronto para clientes.
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-600">
              Esta experiência foi desenhada como vídeo institucional navegável: cursor sintético, roteiro comercial, explicação de indicadores, criação de ticket, trilha auditável e fechamento em ROI.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setIsPaused((value) => !value)}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white"
            >
              {isPaused ? <Play size={16} /> : <Pause size={16} />}
              {isPaused ? "Retomar" : "Pausar"}
            </button>
            <button
              type="button"
              onClick={() => {
                setStepIndex(0);
                setIsPaused(false);
              }}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900"
            >
              <RotateCcw size={16} />
              Reiniciar
            </button>
            <button
              type="button"
              onClick={() => setIsMuted((value) => !value)}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900"
            >
              {isMuted ? <MicOff size={16} /> : <Mic size={16} />}
              {isMuted ? "Ativar narração" : "Silenciar narração"}
            </button>
            <button
              type="button"
              onClick={toggleFullscreen}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900"
            >
              <Maximize2 size={16} />
              Tela cheia
            </button>
          </div>
        </div>

        <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-slate-600">
          <div className="rounded-full border border-slate-300 bg-white px-3 py-1.5">
            Etapa {stepIndex + 1} de {DEMO_STEPS.length}: <span className="font-semibold text-slate-900">{currentStep.title}</span>
          </div>
          <div className="rounded-full border border-slate-300 bg-white px-3 py-1.5">
            Foco atual: <span className="font-semibold text-slate-900">{currentStep.focusLabel}</span>
          </div>
          <div className="rounded-full border border-slate-300 bg-white px-3 py-1.5">
            Voz: <span className="font-semibold text-slate-900">{audioProvider}</span>
          </div>
          <div className="rounded-full border border-slate-300 bg-white px-3 py-1.5">
            Áudio: <span className="font-semibold text-slate-900">{audioStatus === "loading" ? "Carregando" : audioStatus === "playing" ? "Tocando" : audioStatus === "error" ? "Indisponível" : "Pronto"}</span>
          </div>
        </div>

        <div ref={frameRef} className="overflow-hidden rounded-[36px] border border-white/60 bg-white/80 shadow-[0_40px_120px_rgba(15,23,42,0.16)] backdrop-blur-xl">
          <div className="grid min-h-[760px] grid-cols-[240px_1fr]">
            <SceneNavigation scene={currentStep.scene} />
            <div className="relative overflow-hidden bg-slate-100">
              {currentStep.scene === "dashboard" ? <DashboardScene highlight={currentStep.id === "dashboard-risk"} /> : null}
              {currentStep.scene === "tickets" ? (
                <TicketsScene mode={currentStep.id === "ticket-create" ? "create" : "triage"} />
              ) : null}
              {currentStep.scene === "logs" ? <LogsScene highlight={currentStep.id === "logs-audit"} /> : null}
              {currentStep.scene === "metrics" ? (
                <MetricsScene
                  highlightCards={currentStep.id === "metrics-explain"}
                  highlightExport={currentStep.id === "report-export"}
                />
              ) : null}
              {currentStep.scene === "roi" ? <RoiScene highlight={currentStep.id === "roi-close"} /> : null}

              <div className="pointer-events-none absolute inset-x-0 bottom-0 p-6">
                <div className="max-w-3xl rounded-[28px] border border-white/50 bg-white/92 p-5 shadow-2xl backdrop-blur-xl">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-700">
                    <BellRing size={14} />
                    Narração atual
                  </div>
                  <div className="mt-3 text-lg font-semibold text-slate-950">{currentStep.title}</div>
                  <div className="mt-2 text-sm leading-relaxed text-slate-600">{currentStep.caption}</div>
                </div>
              </div>

              <div
                className={cx(
                  "pointer-events-none absolute z-20 h-7 w-7 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-slate-950 shadow-[0_10px_24px_rgba(15,23,42,0.34)] transition-all duration-700 ease-out",
                  currentStep.click && "scale-110 shadow-[0_0_0_10px_rgba(34,211,238,0.18)]",
                )}
                style={{ left: `${currentStep.x}%`, top: `${currentStep.y}%` }}
              >
                <div className="absolute left-1/2 top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300" />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[28px] border border-white/60 bg-white/80 p-5 shadow-[0_20px_60px_rgba(15,23,42,0.08)] backdrop-blur-xl">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <ClipboardList size={18} className="text-cyan-700" />
              Sequência da demo institucional
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {DEMO_STEPS.map((step, index) => (
                <button
                  key={step.id}
                  type="button"
                  onClick={() => {
                    setStepIndex(index);
                    setIsPaused(true);
                  }}
                  className={cx(
                    "rounded-2xl border px-4 py-4 text-left transition",
                    index === stepIndex
                      ? "border-cyan-300 bg-cyan-50 text-cyan-950"
                      : "border-slate-200 bg-white text-slate-700 hover:border-slate-300",
                  )}
                >
                  <div className="text-xs font-semibold uppercase tracking-wide opacity-70">Etapa {index + 1}</div>
                  <div className="mt-2 font-semibold">{step.title}</div>
                  <div className="mt-1 text-sm opacity-80">{step.focusLabel}</div>
                </button>
              ))}
            </div>
          </div>
          <div className="rounded-[28px] border border-white/60 bg-white/80 p-5 shadow-[0_20px_60px_rgba(15,23,42,0.08)] backdrop-blur-xl">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <FileText size={18} className="text-cyan-700" />
              Como usar com clientes
            </div>
            <div className="mt-4 space-y-3 text-sm leading-relaxed text-slate-600">
              <div className="rounded-2xl bg-slate-50 p-4">Use esta página em tela cheia como vídeo institucional navegável durante reuniões e feiras.</div>
              <div className="rounded-2xl bg-slate-50 p-4">A narração agora é servida por TTS de alta qualidade no servidor. Para voz humana, configure OPENAI_API_KEY e, se quiser, DEMO_NARRATION_VOICE.</div>
              <div className="rounded-2xl bg-slate-50 p-4">Se você gravar locução real em MP3, basta colocar os arquivos em <span className="font-semibold">public/narration/demo-institucional</span> com o nome de cada etapa, como <span className="font-semibold">dashboard-risk.mp3</span>.</div>
              <div className="rounded-2xl bg-slate-50 p-4">Se quiser transformar isso em vídeo, o caminho mais simples é gravar esta demo em tela cheia e reutilizar o resultado nas apresentações.</div>
            </div>
            <div className="mt-4 flex flex-wrap gap-3">
              <Link
                href="/simulacoes"
                className="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white"
              >
                Voltar ao roteiro comercial
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}