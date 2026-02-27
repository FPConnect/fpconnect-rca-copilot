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

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, text);
  }
  return res.json() as Promise<T>;
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
}

export interface CreateTicketPayload {
  title: string;
  priority: string;
}

export interface HealthStatus {
  status: string;
  version?: string;
}

export const api = {
  health: () => request<HealthStatus>("/health"),
  getMachines: () => request<Machine[]>("/machines"),
  getTickets: () => request<Ticket[]>("/tickets"),
  createTicket: (data: CreateTicketPayload) =>
    request<Ticket>("/tickets", { method: "POST", body: JSON.stringify(data) }),
};
