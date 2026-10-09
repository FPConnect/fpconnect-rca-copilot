const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const PREVIEW_MODE = process.env.NEXT_PUBLIC_PREVIEW_MODE === "true";

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
  return sessionStorage.getItem("auth_token");
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
  last_check: string;
}

export interface Ticket {
  id: number;
  title: string;
  status: string;
  priority: string;
}

export interface CreateTicketPayload {
  title: string;
  priority: string;
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
  refresh_token?: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  phone_number?: string;
  verification_code?: string;
}

export interface VerificationCodePayload {
  email: string;
  phone_number: string;
}

export interface VerificationCodeResponse {
  status: string;
  to: string;
  provider: string;
  expires_in_seconds: number;
  verification_code?: string | null;
}

export interface UserProfile {
  id: number;
  email: string;
  full_name?: string | null;
  phone_number?: string | null;
  role: string;
  access_level?: number;
}

export interface UpdateProfilePayload {
  email?: string;
  full_name?: string;
  phone_number?: string;
}

export interface Playbook {
  id: number;
  title: string;
  equipment: string;
  steps: string;
  files?: string | null;
}

export interface CreatePlaybookPayload {
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
  sla_compliance: number;
  days_to_expire?: number | null;
  alert?: string | null;
}

export interface AnalyzeResponse {
  ticket_id: number;
  root_cause: string;
  explanation: string;
  recommendation: string;
}

export interface SmsResponse {
  status: string;
  to: string;
  provider: string;
  delivered: boolean;
}

const TICKETS_STORAGE_KEY = "fpconnect_preview_tickets";
const LEGACY_PREVIEW_USERS_KEY = "fpconnect_preview_users";

const FALLBACK_MACHINES: Machine[] = [
  {
    id: 1,
    code: "MRI-01",
    name: "MRI Scanner",
    location: "Radiologia",
    status: "online",
    type: "imaging",
    last_check: "2026-04-15T08:30:00-03:00",
  },
  {
    id: 2,
    code: "ECG-02",
    name: "ECG Monitor",
    location: "UTI",
    status: "warning",
    type: "monitoring",
    last_check: "2026-04-15T08:26:00-03:00",
  },
  {
    id: 3,
    code: "VENT-03",
    name: "Ventilator",
    location: "UTI 2",
    status: "online",
    type: "life-support",
    last_check: "2026-04-15T08:31:00-03:00",
  },
  {
    id: 4,
    code: "DEF-04",
    name: "Defibrillator",
    location: "Emergência",
    status: "offline",
    type: "life-support",
    last_check: "2026-04-15T07:45:00-03:00",
  },
];


const FALLBACK_PLAYBOOKS: Playbook[] = [
  { id: 1, title: "Troca e validação de sensor SpO2", equipment: "Monitor Multiparamétrico", steps: "1. Isolar leito.\n2. Trocar cabo/sensor.\n3. Validar curva e alarmes.\n4. Registrar evento.", files: null },
  { id: 2, title: "Diagnóstico de circuito ventilatório obstruído", equipment: "Ventilador Pulmonar", steps: "1. Verificar circuito.\n2. Inspecionar filtro HME.\n3. Rodar autoteste.\n4. Liberar com checklist.", files: null },
];

const FALLBACK_CONTRACTS: SLAContract[] = [
  { id: 1, equipment: "Ventilador Pulmonar", vendor: "MedTech Care", response_time_hours: 4, sla_compliance: 97.5, days_to_expire: 20, alert: "Vencimento próximo" },
  { id: 2, equipment: "Ressonância Magnética 1.5T", vendor: "Imagem Prime", response_time_hours: 8, sla_compliance: 94, days_to_expire: 75, alert: null },
];

const FALLBACK_TICKETS: Ticket[] = [
  { id: 101, title: "Ventilador UTI com alarmes intermitentes", status: "open", priority: "critical" },
  { id: 102, title: "Monitor ECG com latência alta", status: "in_progress", priority: "high" },
  { id: 103, title: "Calibração preventiva do MRI Scanner", status: "resolved", priority: "medium" },
];

function readPreviewTickets(): Ticket[] {
  if (typeof window === "undefined") return FALLBACK_TICKETS;
  try {
    const raw = localStorage.getItem(TICKETS_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Ticket[]) : FALLBACK_TICKETS;
  } catch {
    return FALLBACK_TICKETS;
  }
}

function writePreviewTickets(tickets: Ticket[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TICKETS_STORAGE_KEY, JSON.stringify(tickets));
}

function clearLegacyPreviewCredentials() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(LEGACY_PREVIEW_USERS_KEY);
  localStorage.removeItem("auth_token");
}

async function login(data: LoginPayload): Promise<LoginResponse> {
  clearLegacyPreviewCredentials();
  return request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

async function sendVerificationCode(data: VerificationCodePayload): Promise<VerificationCodeResponse> {
  return request<VerificationCodeResponse>("/auth/verification-code", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

async function register(data: RegisterPayload): Promise<UserProfile> {
  const path = data.verification_code ? "/auth/register/verify" : "/auth/register";
  return request<UserProfile>(path, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

async function getMe(): Promise<UserProfile> {
  return request<UserProfile>("/auth/me");
}

async function updateMe(data: UpdateProfilePayload): Promise<UserProfile> {
  return request<UserProfile>("/auth/me", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

async function sendSmsNotification(message: string): Promise<SmsResponse> {
  return request<SmsResponse>("/notifications/sms", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

async function withFallback<T>(requestFn: () => Promise<T>, fallbackFn: () => T): Promise<T> {
  try {
    return await requestFn();
  } catch (error) {
    if (!PREVIEW_MODE) throw error;
    return fallbackFn();
  }
}

async function createPlaybook(data: CreatePlaybookPayload): Promise<Playbook> {
  return withFallback(
    () => request<Playbook>("/playbooks/", { method: "POST", body: JSON.stringify(data) }),
    () => ({ id: Date.now(), ...data }),
  );
}

async function analyzeIncident(ticketId: number): Promise<AnalyzeResponse> {
  return withFallback(
    () =>
      request<AnalyzeResponse>("/analyze", {
        method: "POST",
        body: JSON.stringify({ ticket_id: ticketId }),
      }),
    () => ({
      ticket_id: ticketId,
      root_cause: "Falha intermitente em sensor ou conexão do equipamento",
      explanation: "Diagnóstico em modo preview baseado nos chamados clínicos locais. Valide cabos, sensores, histórico de alarmes e condições de uso antes de liberar o equipamento.",
      recommendation: "Isolar o equipamento, executar checklist funcional, substituir acessórios suspeitos e registrar evidências no chamado.",
    }),
  );
}

async function createTicket(data: CreateTicketPayload): Promise<Ticket> {
  return withFallback(
    () => request<Ticket>("/tickets", { method: "POST", body: JSON.stringify(data) }),
    () => {
      const tickets = readPreviewTickets();
      const ticket: Ticket = {
        id: Date.now(),
        title: data.title,
        priority: data.priority,
        status: "open",
      };
      writePreviewTickets([ticket, ...tickets]);
      return ticket;
    },
  );
}

export const api = {
  health: () => withFallback(() => request<HealthStatus>("/health"), () => ({ status: "ok", version: "preview" })),
  login,
  register,
  sendVerificationCode,
  getMe,
  updateMe,
  clearLegacyPreviewCredentials,
  sendSmsNotification,
  analyzeIncident,
  getPlaybooks: () => withFallback(() => request<Playbook[]>("/playbooks/"), () => FALLBACK_PLAYBOOKS),
  createPlaybook,
  getContracts: () => withFallback(() => request<SLAContract[]>("/contracts/"), () => FALLBACK_CONTRACTS),
  getMachines: () => withFallback(() => request<Machine[]>("/machines"), () => FALLBACK_MACHINES),
  getTickets: () => withFallback(() => request<Ticket[]>("/tickets"), readPreviewTickets),
  createTicket,
};
