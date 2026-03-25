const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface Machine {
  id: string;
  name: string;
  location: string;
  status: "online" | "offline" | "warning";
  lastCheck: string;
}

export interface Ticket {
  id: number;
  title: string;
  status: string;
  priority: string;
  description?: string | null;
  device_id?: string | null;
  location?: string | null;
  creator_id?: number;
  assignee_id?: number | null;
  escalation_level?: number | null;
}

export interface CreateTicketPayload {
  title: string;
  priority: string;
  description?: string;
  device_id?: string;
  location?: string;
}

export interface HealthStatus {
  status: string;
  version?: string;
}

export interface IntelItem {
  id: number;
  source: string;
  url: string;
  title: string;
  published_at?: string | null;
  fetched_at: string;
  topic?: string | null;
  summary_pt?: string | null;
  summary_en?: string | null;
}

export interface IntelTopics {
  topics: string[];
}

export interface IntelIngestResult {
  inserted: number;
  skipped: number;
  sources: number;
}

export interface AgentChatReply {
  reply: string;
  backend: "rules" | "openai" | string;
}

function shouldUseDemoMode(): boolean {
  if (process.env.NEXT_PUBLIC_DEMO_MODE === "true") {
    return true;
  }

  const pointsToLocalApi =
    API_URL.includes("localhost") || API_URL.includes("127.0.0.1");

  if (!pointsToLocalApi) {
    return false;
  }

  if (typeof window === "undefined") {
    return process.env.VERCEL === "1";
  }

  return !["localhost", "127.0.0.1"].includes(window.location.hostname);
}

const DEMO_TICKETS: Ticket[] = [
  {
    id: 101,
    title: "Ventilador UTI com alarmes intermitentes",
    status: "open",
    priority: "critical",
    description: "Equipe relata interrupções curtas e repetidas durante o turno da noite.",
    location: "UTI 2",
    device_id: "VENT-UTI-02",
    escalation_level: 2,
  },
  {
    id: 102,
    title: "Monitor multiparamétrico com latência no traçado",
    status: "in_progress",
    priority: "high",
    description: "A atualização do display está lenta e o histórico mostra degradação nas últimas 24h.",
    location: "Enfermaria A",
    device_id: "MON-ENF-14",
    escalation_level: 1,
  },
  {
    id: 103,
    title: "ECG da recepção precisa de calibração",
    status: "resolved",
    priority: "medium",
    description: "Calibração concluída e liberada para uso.",
    location: "Recepção",
    device_id: "ECG-REC-01",
    escalation_level: 0,
  },
];

const DEMO_INTEL_ITEMS: IntelItem[] = [
  {
    id: 1,
    source: "FDA Recall Feed",
    url: "https://www.fda.gov/medical-devices/medical-device-recalls",
    title: "Recall preventivo de bomba de infusão por falha intermitente",
    published_at: "2026-03-08T14:30:00Z",
    fetched_at: "2026-03-10T03:00:00Z",
    topic: "recalls",
    summary_pt: "Fabricante orienta inspeção imediata de lote específico devido a parada inesperada em baixa frequência.",
    summary_en: "Manufacturer recommends immediate inspection of a specific lot due to rare unexpected stoppage.",
  },
  {
    id: 2,
    source: "ECRI Alerts",
    url: "https://www.ecri.org/components/HRCAlerts/Pages/default.aspx",
    title: "Boletim sobre manutenção preditiva em equipamentos críticos",
    published_at: "2026-03-07T11:00:00Z",
    fetched_at: "2026-03-10T03:00:00Z",
    topic: "maintenance",
    summary_pt: "Reforça monitoramento de vibração, temperatura e alarmes reincidentes para reduzir indisponibilidade.",
    summary_en: "Highlights vibration, temperature, and repeated alarms monitoring to reduce downtime.",
  },
  {
    id: 3,
    source: "Healthcare IT News",
    url: "https://www.healthcareitnews.com/",
    title: "Hospitais ampliam uso de copilots operacionais para engenharia clínica",
    published_at: "2026-03-06T09:15:00Z",
    fetched_at: "2026-03-10T03:00:00Z",
    topic: "ai",
    summary_pt: "Adoção cresce em times que precisam priorizar chamados, rastrear ativos e antecipar incidentes.",
    summary_en: "Adoption grows among teams prioritizing service calls, tracking assets, and anticipating incidents.",
  },
];

let demoTicketsState = [...DEMO_TICKETS];

function parseJsonBody(options?: RequestInit): Record<string, unknown> {
  if (!options?.body || typeof options.body !== "string") {
    return {};
  }

  try {
    return JSON.parse(options.body) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function buildDemoAgentReply(message: string): AgentChatReply {
  const text = message.toLowerCase();

  if (text.includes("crític") || text.includes("critic")) {
    return {
      backend: "rules",
      reply:
        "Os casos mais críticos na simulação são o ventilador da UTI e o monitor com latência. Eu priorizaria contenção clínica, validação de logs e checagem de peças de reposição ainda hoje.",
    };
  }

  if (text.includes("prior")) {
    return {
      backend: "rules",
      reply:
        "Use impacto clínico, frequência de falha e tempo médio de restauração para ordenar a fila. Na base demo, o ventilador deve ficar no topo, seguido pelo monitor com degradação de traçado.",
    };
  }

  return {
    backend: "rules",
    reply:
      "Modo demo ativo. Posso simular priorização de tickets, próximos passos técnicos e argumentos de valor para operação clínica sem depender do backend público.",
  };
}

function demoResponse<T>(path: string, options?: RequestInit): T {
  if (path === "/health") {
    return { status: "ok", version: "demo-web" } as T;
  }

  if (path === "/machines") {
    return [
      { id: "MRI-01", name: "MRI Scanner", location: "Radiologia", status: "online", lastCheck: "2026-03-10T02:45:00Z" },
      { id: "VENT-02", name: "Ventilator", location: "UTI 2", status: "warning", lastCheck: "2026-03-10T02:40:00Z" },
      { id: "ECG-01", name: "ECG Monitor", location: "Recepção", status: "offline", lastCheck: "2026-03-10T01:50:00Z" },
    ] as T;
  }

  if (path === "/tickets" && (!options?.method || options.method === "GET")) {
    return [...demoTicketsState] as T;
  }

  if (path === "/tickets" && options?.method === "POST") {
    const payload = parseJsonBody(options);
    const priority = String(payload.priority ?? "medium");
    const created: Ticket = {
      id: Date.now(),
      title: String(payload.title ?? "Novo ticket"),
      priority,
      description: typeof payload.description === "string" ? payload.description : undefined,
      status: "open",
      device_id: typeof payload.device_id === "string" ? payload.device_id : undefined,
      location: typeof payload.location === "string" ? payload.location : undefined,
      escalation_level: priority === "critical" ? 2 : priority === "high" ? 1 : 0,
    };
    demoTicketsState = [created, ...demoTicketsState];
    return created as T;
  }

  if (path === "/intel/topics") {
    return { topics: ["recalls", "maintenance", "ai"] } as T;
  }

  if (path.startsWith("/intel/items")) {
    const url = new URL(path, "https://demo.fpconnect.local");
    const topic = url.searchParams.get("topic");
    const items = topic
      ? DEMO_INTEL_ITEMS.filter((item) => item.topic === topic)
      : DEMO_INTEL_ITEMS;
    return items as T;
  }

  if (path === "/intel/ingest/once") {
    return { inserted: 3, skipped: 12, sources: 4 } as T;
  }

  if (path === "/agent/chat") {
    const payload = parseJsonBody(options);
    return buildDemoAgentReply(String(payload.message ?? "")) as T;
  }

  if (path === "/agent/tickets/analyze") {
    const payload = parseJsonBody(options);
    const ticket = (payload.ticket as Record<string, unknown> | undefined) ?? {};
    const title = String(ticket.title ?? "ticket selecionado");
    const priority = String(ticket.priority ?? "medium");
    return {
      backend: "rules",
      reply:
        `Para ${title}, eu começaria confirmando impacto clínico, revisando histórico recente e validando causa provável ligada à prioridade ${priority}. Se o sintoma persistir, escale fornecedor e separe equipamento backup antes de encerrar o chamado.`,
    } as T;
  }

  throw new Error(`No demo response configured for ${path}`);
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (shouldUseDemoMode()) {
    return demoResponse<T>(path, options);
  }

  try {
    const res = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...options?.headers },
      ...options,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText);
      throw new ApiError(res.status, text);
    }
    return res.json() as Promise<T>;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    return demoResponse<T>(path, options);
  }
}

export const api = {
  health: () => request<HealthStatus>("/health"),
  getMachines: () => request<Machine[]>("/machines"),
  getTickets: () => request<Ticket[]>("/tickets"),
  createTicket: (data: CreateTicketPayload) =>
    request<Ticket>("/tickets", { method: "POST", body: JSON.stringify(data) }),

  // Intel/Radar
  getIntelTopics: () => request<IntelTopics>("/intel/topics"),
  getIntelItems: (topic?: string, limit: number = 50) => {
    const qs = new URLSearchParams();
    if (topic) qs.set("topic", topic);
    qs.set("limit", String(limit));
    return request<IntelItem[]>(`/intel/items?${qs.toString()}`);
  },
  runIntelIngestOnce: () => request<IntelIngestResult>("/intel/ingest/once", { method: "POST" }),

  // Agent endpoints
  agentChat: (message: string) =>
    request<AgentChatReply>("/agent/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  agentAnalyzeTicket: (ticket: Ticket, question: string) =>
    request<AgentChatReply>("/agent/tickets/analyze", {
      method: "POST",
      body: JSON.stringify({
        ticket: {
          title: ticket.title,
          description: ticket.description ?? undefined,
          priority: ticket.priority,
          status: ticket.status,
        },
        question,
      }),
    }),
};
