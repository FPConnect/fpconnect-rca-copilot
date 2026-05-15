import AsyncStorage from "@react-native-async-storage/async-storage";

export type TicketPriority = "critical" | "high" | "medium" | "low";
export type TicketStatus = "open" | "in_progress" | "resolved" | "closed";
export type TicketSyncStatus = "synced" | "pending" | "syncing" | "failed";

export interface OfflineTicket {
  id: string;
  serverId?: number;
  title: string;
  description?: string;
  status: TicketStatus;
  priority: TicketPriority;
  syncStatus: TicketSyncStatus;
  createdAt: string;
  updatedAt: string;
}

interface PendingTicketCreate {
  localId: string;
  payload: {
    title: string;
    description?: string;
    priority: TicketPriority;
  };
}

const TICKETS_KEY = "fpconnect.offline.tickets";
const QUEUE_KEY = "fpconnect.offline.ticketQueue";
const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export const seedTickets: OfflineTicket[] = [
  {
    id: "seed-1",
    serverId: 1,
    title: "MRI Scanner offline - Ward A",
    status: "open",
    priority: "critical",
    syncStatus: "synced",
    createdAt: new Date(0).toISOString(),
    updatedAt: new Date(0).toISOString(),
  },
  {
    id: "seed-2",
    serverId: 2,
    title: "ECG Monitor slow response",
    status: "in_progress",
    priority: "high",
    syncStatus: "synced",
    createdAt: new Date(0).toISOString(),
    updatedAt: new Date(0).toISOString(),
  },
  {
    id: "seed-3",
    serverId: 3,
    title: "Patient monitor alarm",
    status: "open",
    priority: "medium",
    syncStatus: "synced",
    createdAt: new Date(0).toISOString(),
    updatedAt: new Date(0).toISOString(),
  },
];

async function readJson<T>(key: string, fallback: T): Promise<T> {
  const raw = await AsyncStorage.getItem(key);
  return raw ? (JSON.parse(raw) as T) : fallback;
}

async function writeJson<T>(key: string, value: T): Promise<void> {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

export async function loadOfflineTickets(): Promise<OfflineTicket[]> {
  return readJson<OfflineTicket[]>(TICKETS_KEY, seedTickets);
}

export async function saveOfflineTickets(tickets: OfflineTicket[]): Promise<void> {
  await writeJson(TICKETS_KEY, tickets);
}

export async function createOfflineTicket(input: {
  title: string;
  description?: string;
  priority: TicketPriority;
}): Promise<OfflineTicket> {
  const now = new Date().toISOString();
  const localTicket: OfflineTicket = {
    id: `local-${Date.now()}`,
    title: input.title,
    description: input.description,
    status: "open",
    priority: input.priority,
    syncStatus: "pending",
    createdAt: now,
    updatedAt: now,
  };

  const [tickets, queue] = await Promise.all([
    loadOfflineTickets(),
    readJson<PendingTicketCreate[]>(QUEUE_KEY, []),
  ]);

  await Promise.all([
    saveOfflineTickets([localTicket, ...tickets]),
    writeJson<PendingTicketCreate[]>(QUEUE_KEY, [
      ...queue,
      {
        localId: localTicket.id,
        payload: {
          title: input.title,
          description: input.description,
          priority: input.priority,
        },
      },
    ]),
  ]);

  return localTicket;
}

export async function getPendingTicketCount(): Promise<number> {
  const queue = await readJson<PendingTicketCreate[]>(QUEUE_KEY, []);
  return queue.length;
}

export async function syncPendingTickets(authToken?: string): Promise<{
  synced: number;
  failed: number;
  tickets: OfflineTicket[];
}> {
  const queue = await readJson<PendingTicketCreate[]>(QUEUE_KEY, []);
  let tickets = await loadOfflineTickets();

  if (!queue.length) {
    return { synced: 0, failed: 0, tickets };
  }

  const remaining: PendingTicketCreate[] = [];
  let synced = 0;
  let failed = 0;

  for (const item of queue) {
    tickets = tickets.map((ticket) =>
      ticket.id === item.localId ? { ...ticket, syncStatus: "syncing" } : ticket,
    );
    await saveOfflineTickets(tickets);

    try {
      const response = await fetch(`${API_URL}/tickets/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
        },
        body: JSON.stringify(item.payload),
      });

      if (!response.ok) {
        throw new Error(`Ticket sync failed with status ${response.status}`);
      }

      const created = (await response.json()) as { id: number; status?: TicketStatus };
      tickets = tickets.map((ticket) =>
        ticket.id === item.localId
          ? {
              ...ticket,
              serverId: created.id,
              status: created.status ?? ticket.status,
              syncStatus: "synced",
              updatedAt: new Date().toISOString(),
            }
          : ticket,
      );
      synced += 1;
    } catch {
      tickets = tickets.map((ticket) =>
        ticket.id === item.localId ? { ...ticket, syncStatus: "failed" } : ticket,
      );
      remaining.push(item);
      failed += 1;
    }
  }

  await Promise.all([saveOfflineTickets(tickets), writeJson(QUEUE_KEY, remaining)]);
  return { synced, failed, tickets };
}
