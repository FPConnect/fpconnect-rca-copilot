import { apiRequest, ApiError, User } from "./api";

export interface SecureSessionStore {
  getItem(): Promise<string | null>;
  setItem(value: string): Promise<void>;
  removeItem(): Promise<void>;
  // Deletes only this session's token slot, never a later session's pointer.
  removeStaleItem(): Promise<void>;
}

interface TokenPair { access: string; refresh: string | null }
export interface AuthenticatedSession { client: SessionClient; user: User }
export interface Organization { id: number; slug: string; name: string }
export interface SelectedMembership { role: string; accessLevel: number }
export interface RequestClient {
  request<T>(path: string, options?: { method?: string; body?: unknown }): Promise<T>;
}
export class SessionRemovalError extends Error {
  constructor() {
    super("Could not remove the saved session. Retry before sharing this device; clearing app data would erase legacy drafts.");
  }
}
export class UnsupportedSessionPlatformError extends Error {
  constructor() { super("Sign-in requires native secure storage; web is not supported."); }
}
export function requireNativeSessionStorage(platform: string): void {
  if (platform === "web") throw new UnsupportedSessionPlatformError();
}
export function restoreErrorMessage(error: unknown): string {
  return error instanceof ApiError || error instanceof SessionRemovalError ||
    error instanceof UnsupportedSessionPlatformError ? error.message : "Could not restore session securely.";
}

function parsePair(value: unknown): TokenPair {
  if (!value || typeof value !== "object") throw new ApiError("server", "Invalid authentication response.");
  const result = value as { access_token?: unknown; refresh_token?: unknown };
  if (typeof result.access_token !== "string" || !result.access_token.trim() ||
      typeof result.refresh_token !== "string" || !result.refresh_token.trim()) {
    throw new ApiError("server", "Invalid authentication response.");
  }
  return { access: result.access_token, refresh: result.refresh_token };
}

function decodeStored(raw: string): TokenPair {
  // The earlier prototype stored just an access token under this key.
  if (!raw.startsWith("{")) return { access: raw, refresh: null };
  try {
    const pair = JSON.parse(raw);
    if (typeof pair.access === "string" && pair.access.trim() &&
        (pair.refresh === null || (typeof pair.refresh === "string" && pair.refresh.trim()))) return pair;
  } catch { /* Invalid stored value is not a session. */ }
  throw new ApiError("auth", "Saved session is invalid. Sign in again.");
}

export class SessionClient {
  private refreshInFlight: Promise<void> | null = null;
  private active = true;
  constructor(private store: SecureSessionStore, private pair: TokenPair) {}

  async persist(): Promise<void> {
    try { await this.store.setItem(JSON.stringify(this.pair)); }
    catch { throw new ApiError("auth", "Could not securely save the session. Sign in again."); }
  }

  private refresh(): Promise<void> {
    if (this.refreshInFlight) return this.refreshInFlight;
    const work = async () => {
      if (!this.active || !this.pair.refresh) throw new ApiError("auth", "Session expired. Sign in again.", 401);
      const next = parsePair(await apiRequest<unknown>("/auth/refresh", {
        method: "POST", body: { refresh_token: this.pair.refresh },
      }));
      if (!this.active) throw new ApiError("auth", "Session ended.", 401);
      try { await this.store.setItem(JSON.stringify(next)); }
      catch {
        if (!this.active) {
          try { await this.store.removeStaleItem(); } catch { /* No active pointer remains. */ }
        }
        throw new ApiError("auth", "Could not securely save the session. Sign in again.");
      }
      if (!this.active) {
        try { await this.store.removeStaleItem(); } catch { /* Local sign-out already removed the active session pointer. */ }
        throw new ApiError("auth", "Session ended.", 401);
      }
      this.pair = next;
    };
    const pending = work().finally(() => { this.refreshInFlight = null; });
    this.refreshInFlight = pending;
    return pending;
  }

  async request<T>(path: string, options: { method?: string; body?: unknown; organizationId?: number } = {}): Promise<T> {
    if (!this.active) throw new ApiError("auth", "Session ended.", 401);
    const originalAccess = this.pair.access;
    try {
      const result = await apiRequest<T>(path, { ...options, token: originalAccess });
      if (!this.active) throw new ApiError("auth", "Session ended.", 401);
      return result;
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401 || !this.active) throw error;
      // Another request may already have refreshed this access token.
      if (this.pair.access === originalAccess) await this.refresh();
      if (!this.active) throw new ApiError("auth", "Session ended.", 401);
      const result = await apiRequest<T>(path, { ...options, token: this.pair.access });
      if (!this.active) throw new ApiError("auth", "Session ended.", 401);
      return result;
    }
  }

  async close(): Promise<void> {
    this.active = false;
    try { await this.store.removeItem(); } catch { throw new SessionRemovalError(); }
  }
}

function validateUser(user: User): User {
  if (!user || !Number.isSafeInteger(user.id) || user.id <= 0 ||
      typeof user.email !== "string" || !user.email ||
      !Number.isInteger(user.access_level) || user.access_level < 1 || user.access_level > 5 ||
      (user.full_name !== null && typeof user.full_name !== "string")) {
    throw new ApiError("server", "API returned an invalid account response.");
  }
  return user;
}

export async function getCurrentUser(client: SessionClient): Promise<User> {
  return validateUser(await client.request<User>("/auth/me"));
}

export async function discoverOrganizations(client: SessionClient): Promise<Organization[]> {
  const result = await client.request<unknown>("/auth/organizations");
  if (!Array.isArray(result) || !result.every(org => org && Number.isSafeInteger(org.id) && org.id > 0 &&
      typeof org.slug === "string" && typeof org.name === "string")) {
    throw new ApiError("server", "API returned an invalid organization list.");
  }
  return result as Organization[];
}

export async function selectOrganization(client: SessionClient, id: number): Promise<{ client: RequestClient; membership: SelectedMembership }> {
  if (!Number.isSafeInteger(id) || id <= 0) throw new ApiError("validation", "Invalid organization selection.");
  const result = await client.request<{ organization_id: number; role: string; access_level: number }>("/auth/select-organization", { method: "POST", organizationId: id });
  const roles: Record<string, number> = { visitor: 1, user: 2, manager: 3, admin: 4, master: 5 };
  if (!result || result.organization_id !== id || !Object.prototype.hasOwnProperty.call(roles, result.role) ||
      roles[result.role] !== result.access_level) throw new ApiError("server", "API returned an invalid organization selection.");
  // Capture an immutable selector so in-flight requests never switch organizations.
  return {
    membership: { role: result.role, accessLevel: result.access_level },
    client: { request: <T,>(path: string, options: { method?: string; body?: unknown } = {}) =>
      client.request<T>(path, { ...options, organizationId: id }) },
  };
}

export async function signInAndStore(store: SecureSessionStore, email: string, password: string): Promise<AuthenticatedSession> {
  const pair = parsePair(await apiRequest<unknown>("/auth/login", { method: "POST", body: { email, password } }));
  const client = new SessionClient(store, pair);
  const user = validateUser(await apiRequest<User>("/auth/me", { token: pair.access }));
  await client.persist();
  return { client, user };
}

export async function restoreSession(store: SecureSessionStore): Promise<AuthenticatedSession | null> {
  const raw = await store.getItem();
  if (!raw) return null;
  const client = new SessionClient(store, decodeStored(raw));
  try {
    return { client, user: await getCurrentUser(client) };
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) await client.close();
    throw error;
  }
}
