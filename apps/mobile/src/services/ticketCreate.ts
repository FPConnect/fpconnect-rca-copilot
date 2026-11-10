import { ApiError, Ticket } from "./api";
import { RequestClient } from "./session";

export interface MarkerStorage {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

const KEY = "fpconnect.ticket.create.unconfirmed.v1";
let inFlight = false;

// Persist before sending. If the process dies after the server commits, never retry automatically.
export async function createTicket(storage: MarkerStorage, client: RequestClient, title: string, priority: string): Promise<Ticket> {
  if (inFlight) throw new Error("A ticket submission is already in progress.");
  inFlight = true;
  try {
    if (await storage.getItem(KEY)) throw new Error("Reconcile the previous submission before creating another ticket.");
    await storage.setItem(KEY, "unconfirmed");
    try {
      const ticket = await client.request<Ticket>("/tickets/", { method: "POST", body: { title, priority } });
      if (!Number.isInteger(ticket?.id)) throw new ApiError("server", "Invalid ticket response.");
      // Do not clear the guard here: a crash before the UI confirms success
      // would otherwise make a completed request appear safe to repeat.
      return ticket;
    } catch (error) {
      // Only a definitive rejection can be safely retried without idempotency support.
      if (error instanceof ApiError && (error.kind === "configuration" || [400, 401, 403, 404, 422].includes(error.status ?? 0))) {
        await storage.removeItem(KEY);
      }
      throw error;
    }
  } finally {
    inFlight = false;
  }
}

export async function hasUnconfirmedTicket(storage: MarkerStorage): Promise<boolean> {
  return !!(await storage.getItem(KEY));
}

export async function acknowledgeUnconfirmedTicket(storage: MarkerStorage): Promise<void> {
  if (inFlight) throw new Error("A ticket submission is in progress.");
  await storage.removeItem(KEY);
}
