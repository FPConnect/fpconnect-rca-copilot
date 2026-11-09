import { ApiError, Machine, Ticket } from "./api";
import { RequestClient } from "./session";

type Validator<T> = (value: unknown) => value is T;

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export const isTicket: Validator<Ticket> = (value): value is Ticket =>
  isRecord(value) && Number.isSafeInteger(value.id) && (value.id as number) > 0 &&
  typeof value.title === "string" && typeof value.status === "string" &&
  typeof value.priority === "string";

export const isMachine: Validator<Machine> = (value): value is Machine =>
  isRecord(value) && Number.isSafeInteger(value.id) && (value.id as number) > 0 &&
  typeof value.code === "string" && typeof value.name === "string" &&
  typeof value.location === "string" && typeof value.type === "string" &&
  typeof value.status === "string" && typeof value.last_check === "string";

export async function fetchList<T>(path: string, client: RequestClient, validate: Validator<T>): Promise<T[]> {
  const result = await client.request<unknown>(path);
  if (!Array.isArray(result) || !result.every(validate)) {
    throw new ApiError("server", "API returned an invalid list response.");
  }
  return result;
}
