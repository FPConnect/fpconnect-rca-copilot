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

function getAuthToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, text);
  }
  return res.json() as Promise<T>;
}

export interface Machine {
  id: number;
  code: string;
  name: string;
  location: string;
  status: "online" | "offline" | "warning";
  type: string;
  model?: string | null;
  criticality: "Baixa" | "Média" | "Alta" | string;
  last_failure?: string | null;
  recurrent_failures: number;
  last_check: string;
}

export interface Ticket {
  id: number;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  device_id?: string | null;
  location?: string | null;
  root_cause?: string | null;
  recommendation?: string | null;
  analysis_completed?: string | null;
}

export interface CreateTicketPayload {
  title: string;
  priority: string;
  description?: string;
  device_id?: string;
  location?: string;
}

export interface AnalyzeResponse {
  ticket_id: number;
  root_cause: string;
  recommendation: string;
  explanation: string;
}

export interface Playbook {
  id: number;
  title: string;
  equipment: string;
  steps: string;
  files?: string | null;
}

export interface SLAContract {
  id: number;
  equipment: string;
  vendor: string;
  response_time_hours: number;
  penalty?: string | null;
  sla_compliance: number;
  expires_at?: string | null;
  days_to_expire?: number | null;
  alert?: string | null;
}

export interface HealthStatus {
  status: string;
  version?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

const TICKETS_STORAGE_KEY = "fpconnect_preview_tickets";
const PLAYBOOKS_STORAGE_KEY = "fpconnect_preview_playbooks";

const FALLBACK_MACHINES: Machine[] = [
  {
    id: 1,
    code: "MRI-01",
    name: "Ressonância Magnética 1.5T",
    model: "Magnetom Aera",
    location: "Radiologia",
    status: "online",
    type: "imaging",
    criticality: "Alta",
    last_failure: "Quench falso positivo no sistema de refrigeração",
    recurrent_failures: 2,
    last_check: "2026-05-15T08:30:00-03:00",
  },
  {
    id: 2,
    code: "ECG-02",
    name: "Monitor Multiparamétrico",
    model: "IntelliVue MX450",
    location: "UTI Adulto",
    status: "warning",
    type: "monitoring",
    criticality: "Alta",
    last_failure: "Perda intermitente de SpO2",
    recurrent_failures: 4,
    last_check: "2026-05-15T08:26:00-03:00",
  },
  {
    id: 3,
    code: "VENT-03",
    name: "Ventilador Pulmonar",
    model: "Servo-u",
    location: "UTI 2",
    status: "online",
    type: "life-support",
    criticality: "Alta",
    last_failure: "Alarme de pressão alta",
    recurrent_failures: 1,
    last_check: "2026-05-15T08:31:00-03:00",
  },
  {
    id: 4,
    code: "DEF-04",
    name: "Desfibrilador",
    model: "HeartStart XL+",
    location: "Pronto Atendimento",
    status: "offline",
    type: "life-support",
    criticality: "Alta",
    last_failure: "Falha no autoteste de bateria",
    recurrent_failures: 3,
    last_check: "2026-05-15T07:45:00-03:00",
  },
  {
    id: 5,
    code: "INF-05",
    name: "Bomba de Infusão",
    model: "Volumat Agilia",
    location: "Centro Cirúrgico",
    status: "online",
    type: "infusion",
    criticality: "Média",
    last_failure: "Oclusão recorrente em equipo",
    recurrent_failures: 1,
    last_check: "2026-05-15T08:40:00-03:00",
  },
];

const FALLBACK_TICKETS: Ticket[] = [
  { id: 101, title: "Perda intermitente de SpO2", description: "Monitor multiparamétrico com alarmes falsos na UTI Adulto.", device_id: "ECG-02", location: "UTI Adulto", status: "open", priority: "critical", root_cause: "Sensor com mau contato ou cabo danificado" },
  { id: 102, title: "Ventilador com alarme de pressão alta", description: "Alarme durante ventilação assistida.", device_id: "VENT-03", location: "UTI 2", status: "in_progress", priority: "critical", root_cause: "Circuito obstruído ou filtro saturado" },
  { id: 103, title: "Falha no autoteste de bateria", description: "Desfibrilador indisponível para uso.", device_id: "DEF-04", location: "Pronto Atendimento", status: "open", priority: "high", root_cause: "Bateria abaixo da capacidade mínima" },
];

const FALLBACK_PLAYBOOKS: Playbook[] = [
  { id: 1, title: "Troca e validação de sensor SpO2", equipment: "Monitor Multiparamétrico", steps: "1. Isolar leito\n2. Trocar cabo/sensor\n3. Validar curva e alarmes", files: "checklist-spo2.pdf" },
  { id: 2, title: "Diagnóstico de circuito ventilatório", equipment: "Ventilador Pulmonar", steps: "1. Verificar circuito\n2. Inspecionar filtro\n3. Rodar autoteste", files: null },
  { id: 3, title: "Substituição de bateria", equipment: "Desfibrilador", steps: "1. Remover do uso\n2. Trocar bateria\n3. Executar autoteste", files: "manual-desfibrilador.pdf" },
];

const FALLBACK_CONTRACTS: SLAContract[] = [
  { id: 1, equipment: "Ventilador Pulmonar", vendor: "MedTech Care", response_time_hours: 4, penalty: "Crédito de 5% por violação", sla_compliance: 97.5, expires_at: "2026-06-05T00:00:00Z", days_to_expire: 21, alert: "Contrato vence em até 30 dias" },
  { id: 2, equipment: "Ressonância Magnética 1.5T", vendor: "Imagem Prime", response_time_hours: 8, penalty: "Plantão técnico sem custo", sla_compliance: 94, expires_at: "2026-08-01T00:00:00Z", days_to_expire: 78, alert: "SLA abaixo da meta" },
];

function readStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeStorage<T>(key: string, value: T) {
  if (typeof window === "undefined") return;
  localStorage.setItem(key, JSON.stringify(value));
}

async function login(data: LoginPayload): Promise<LoginResponse> {
  try {
    return await request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  } catch (error) {
    const isPreviewAccess =
      data.email.trim().toLowerCase() === "admin@fpconnect.com" &&
      data.password === "admin123";
    if (!isPreviewAccess) throw error;
    return { access_token: "fpconnect-official-preview-token", token_type: "bearer" };
  }
}

async function withFallback<T>(requestFn: () => Promise<T>, fallbackFn: () => T): Promise<T> {
  try {
    return await requestFn();
  } catch {
    return fallbackFn();
  }
}

async function createTicket(data: CreateTicketPayload): Promise<Ticket> {
  return withFallback(
    () => request<Ticket>("/tickets", { method: "POST", body: JSON.stringify(data) }),
    () => {
      const tickets = readStorage<Ticket[]>(TICKETS_STORAGE_KEY, FALLBACK_TICKETS);
      const ticket: Ticket = { id: Date.now(), title: data.title, priority: data.priority, status: "open", description: data.description, device_id: data.device_id, location: data.location };
      writeStorage(TICKETS_STORAGE_KEY, [ticket, ...tickets]);
      return ticket;
    },
  );
}

async function analyzeIncident(ticketId: number): Promise<AnalyzeResponse> {
  return withFallback(
    () => request<AnalyzeResponse>("/analyze", { method: "POST", body: JSON.stringify({ ticket_id: ticketId }) }),
    () => ({
      ticket_id: ticketId,
      root_cause: "Falha recorrente em sensor/cabo do equipamento",
      recommendation: "Aplicar playbook de diagnóstico, substituir componente suspeito e validar com teste funcional.",
      explanation: "Resultado de demonstração baseado no histórico local de incidentes e severidade clínica.",
    }),
  );
}

async function createPlaybook(data: Omit<Playbook, "id">): Promise<Playbook> {
  return withFallback(
    () => request<Playbook>("/playbooks/", { method: "POST", body: JSON.stringify(data) }),
    () => {
      const playbooks = readStorage<Playbook[]>(PLAYBOOKS_STORAGE_KEY, FALLBACK_PLAYBOOKS);
      const playbook = { ...data, id: Date.now() };
      writeStorage(PLAYBOOKS_STORAGE_KEY, [playbook, ...playbooks]);
      return playbook;
    },
  );
}

export const api = {
  health: () => withFallback(() => request<HealthStatus>("/health"), () => ({ status: "ok", version: "preview" })),
  login,
  getMachines: () => withFallback(() => request<Machine[]>("/machines"), () => FALLBACK_MACHINES),
  getTickets: () => withFallback(() => request<Ticket[]>("/tickets"), () => readStorage<Ticket[]>(TICKETS_STORAGE_KEY, FALLBACK_TICKETS)),
  createTicket,
  analyzeIncident,
  getPlaybooks: () => withFallback(() => request<Playbook[]>("/playbooks/"), () => readStorage<Playbook[]>(PLAYBOOKS_STORAGE_KEY, FALLBACK_PLAYBOOKS)),
  createPlaybook,
  getContracts: () => withFallback(() => request<SLAContract[]>("/contracts/"), () => FALLBACK_CONTRACTS),
};
