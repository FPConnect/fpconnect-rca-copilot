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

export const api = {
  health: () => request<HealthStatus>("/health"),
  login: (data: LoginPayload) =>
    request<LoginResponse>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  getMachines: () => request<Machine[]>("/machines"),
  getTickets: () => request<Ticket[]>("/tickets"),
  createTicket: (data: CreateTicketPayload) =>
    request<Ticket>("/tickets", { method: "POST", body: JSON.stringify(data) }),
};
