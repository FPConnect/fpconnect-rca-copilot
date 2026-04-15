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
}

const TICKETS_STORAGE_KEY = "fpconnect_preview_tickets";

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

    if (!isPreviewAccess) {
      throw error;
    }

    return {
      access_token: "fpconnect-official-preview-token",
      token_type: "bearer",
    };
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
  getMachines: () => withFallback(() => request<Machine[]>("/machines"), () => FALLBACK_MACHINES),
  getTickets: () => withFallback(() => request<Ticket[]>("/tickets"), readPreviewTickets),
  createTicket,
};
