export type FailureKind = "configuration" | "auth" | "validation" | "server" | "network";

export class ApiError extends Error {
  constructor(public kind: FailureKind, message: string, public status?: number) {
    super(message);
  }
}

export function apiUrl(): string {
  const raw = process.env.EXPO_PUBLIC_API_URL?.trim();
  try {
    if (!raw || !/^https:\/\/[^/?#\\]+\/?$/i.test(raw) || /[\s@\\?#]/.test(raw)) throw new Error();
    const url = new URL(raw);
    if (url.protocol !== "https:" || !url.hostname || url.username || url.password ||
        url.pathname !== "/" || url.search || url.hash) throw new Error();
    return url.origin;
  } catch {
    throw new ApiError("configuration", "Set EXPO_PUBLIC_API_URL to a valid HTTPS origin without a path, credentials, query or fragment.");
  }
}

export async function apiRequest<T>(
  path: string,
  options: { method?: string; token?: string; body?: unknown; organizationId?: number } = {},
): Promise<T> {
  const url = apiUrl() + path;
  let response: Response;
  try {
    response = await fetch(url, {
      method: options.method ?? "GET",
      headers: {
        ...(options.body === undefined ? {} : { "Content-Type": "application/json" }),
        ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
        ...(options.organizationId === undefined ? {} : { "X-Organization-Id": String(options.organizationId) }),
      },
      ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }),
    });
  } catch {
    throw new ApiError("network", "Network request failed; the outcome may be unknown.");
  }
  if (!response.ok) {
    if (response.status === 503) {
      throw new ApiError("server", "Service unavailable. Some operations may be disabled until tenant isolation is complete.", response.status);
    }
    const kind = response.status === 401 || response.status === 403 ? "auth"
      : response.status >= 400 && response.status < 500 && response.status !== 408 && response.status !== 429
        ? "validation" : "server";
    throw new ApiError(kind, `API request failed (${response.status}).`, response.status);
  }
  try {
    return await response.json() as T;
  } catch {
    throw new ApiError("server", "API returned an invalid response.");
  }
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  access_level: number;
}

export interface Ticket {
  id: number;
  title: string;
  status: string;
  priority: string;
}

export interface Machine {
  id: number;
  code: string;
  name: string;
  location: string;
  type: string;
  status: string;
  last_check: string;
}
