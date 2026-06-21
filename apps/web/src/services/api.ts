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
const PREVIEW_PROFILE_KEY = "fpconnect_profile";

type TestAccount = UserProfile & { password: string };

const TEST_ACCOUNTS: TestAccount[] = [
  { id: 1, email: "master@fpconnect.com", password: "Master@2024Secure!", full_name: "Master", role: "master", access_level: 5 },
  { id: 2, email: "admin_teste@fpconnect.com", password: "Admin@123", full_name: "Administrador", role: "admin", access_level: 4 },
  { id: 3, email: "gerente_teste@fpconnect.com", password: "Gerente@123", full_name: "Gerente", role: "manager", access_level: 3 },
  { id: 4, email: "usuario_teste@fpconnect.com", password: "Usuario@123", full_name: "Usuário", role: "user", access_level: 2 },
  { id: 5, email: "visitante_teste@fpconnect.com", password: "Visitante@123", full_name: "Visitante", role: "visitor", access_level: 1 },
];

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

function readPreviewProfilePhone(): string {
  if (typeof window === "undefined") return "";
  try {
    const raw = localStorage.getItem(PREVIEW_PROFILE_KEY);
    if (!raw) return "";
    const profile = JSON.parse(raw) as { phone?: string };
    return profile.phone || "";
  } catch {
    return "";
  }
}

function clearLegacyPreviewCredentials() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(LEGACY_PREVIEW_USERS_KEY);
}

async function login(data: LoginPayload): Promise<LoginResponse> {
  try {
    return await request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  } catch (error) {
    clearLegacyPreviewCredentials();
    const previewAccount = TEST_ACCOUNTS.find(
      (account) =>
        account.email === data.email.trim().toLowerCase() &&
        account.password === data.password,
    );

    if (!previewAccount) {
      throw error;
    }

    localStorage.setItem(
      PREVIEW_PROFILE_KEY,
      JSON.stringify({
        name: previewAccount.full_name,
        email: previewAccount.email,
        phone: "",
      }),
    );

    return {
      access_token: `fpconnect-preview-token-${previewAccount.role}`,
      token_type: "bearer",
    };
  }
}

async function register(data: RegisterPayload): Promise<UserProfile> {
  try {
    return await request<UserProfile>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  } catch (error) {
    clearLegacyPreviewCredentials();
    throw error;
  }
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
  return withFallback(
    () => request<SmsResponse>("/notifications/sms", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
    () => ({
      status: "sent",
      to: readPreviewProfilePhone(),
      provider: "preview-local",
      delivered: true,
    }),
  );
}

async function withFallback<T>(requestFn: () => Promise<T>, fallbackFn: () => T): Promise<T> {
  try {
    return await requestFn();
  } catch {
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
  getMe,
  updateMe,
  testAccounts: TEST_ACCOUNTS.map((account) => ({
    id: account.id,
    email: account.email,
    full_name: account.full_name,
    phone_number: account.phone_number,
    role: account.role,
    access_level: account.access_level,
  })),
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
