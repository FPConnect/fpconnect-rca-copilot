import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import { ApiError, apiRequest, apiUrl } from "../src/services/api";
import { discoverOrganizations, selectOrganization, restoreSession, signInAndStore, SecureSessionStore, SessionClient, SessionRemovalError, requireNativeSessionStorage, restoreErrorMessage } from "../src/services/session";
import { createSessionStore, openSessionStore } from "../src/services/secureSessionStorage";
import { fetchList, isMachine, isTicket } from "../src/services/lists";
import { acknowledgeUnconfirmedTicket, createTicket, hasUnconfirmedTicket, MarkerStorage } from "../src/services/ticketCreate";

const originalFetch = globalThis.fetch;
process.env.EXPO_PUBLIC_API_URL = "https://example.test";
afterEach(() => { globalThis.fetch = originalFetch; });
const user = { id: 5, email: "test@example.test", full_name: null, access_level: 2 };
function response(data: unknown, status = 200) { return new Response(JSON.stringify(data), { status }); }
function store(initial: string | null = null): SecureSessionStore {
  let value = initial;
  return { async getItem() { return value; }, async setItem(v) { value = v; }, async removeItem() { value = null; }, async removeStaleItem() { value = null; } };
}
function marker(): MarkerStorage {
  const map = new Map<string, string>();
  return { async getItem(k) { return map.get(k) ?? null; }, async setItem(k, v) { map.set(k, v); }, async removeItem(k) { map.delete(k); } };
}
function client(storage = store()) { return new SessionClient(storage, { access: "old", refresh: "refresh-old" }); }
function auth(init?: RequestInit) { return (init?.headers as Record<string, string>)?.Authorization; }
function orgHeader(init?: RequestInit) { return (init?.headers as Record<string, string>)?.["X-Organization-Id"]; }

test("discover and validate organizations and use immutable selection on protected calls", async () => {
  const c = client(); let calls = 0;
  globalThis.fetch = async (input, init) => {
    calls++;
    if (calls === 1) {
      assert.ok(String(input).endsWith("/auth/organizations"));
      assert.equal(orgHeader(init), undefined);
      return response([{ id: 2, slug: "first", name: "First" }, { id: 3, slug: "second", name: "Second" }]);
    }
    if (calls === 2 || calls === 3) {
      assert.ok(String(input).endsWith("/auth/select-organization"));
      return response({ organization_id: Number(orgHeader(init)) });
    }
    return response({ selector: orgHeader(init) });
  };
  assert.equal((await discoverOrganizations(c)).length, 2);
  const first = await selectOrganization(c, 2);
  const second = await selectOrganization(c, 3);
  assert.deepEqual(await first.request("/machines/"), { selector: "2" });
  assert.deepEqual(await second.request("/machines/"), { selector: "3" });
});

test("membership discovery and selection fail closed", async () => {
  const c = client();
  globalThis.fetch = async () => response([]);
  assert.deepEqual(await discoverOrganizations(c), []);
  globalThis.fetch = async () => response([{ id: -1, slug: "bad", name: "Bad" }]);
  await assert.rejects(discoverOrganizations(c), /invalid organization list/);
  globalThis.fetch = async () => response({}, 403);
  await assert.rejects(selectOrganization(c, 5), (e: unknown) => e instanceof ApiError && e.status === 403);
  globalThis.fetch = async () => response({ organization_id: 6 });
  await assert.rejects(selectOrganization(c, 5), /invalid organization selection/);
  await assert.rejects(selectOrganization(c, 0), /Invalid organization selection/);
});

test("refresh retains selected organization header but never sends it to refresh", async () => {
  const c = client(); let calls = 0;
  globalThis.fetch = async (input, init) => {
    calls++;
    if (calls === 1) return response({ organization_id: 2 });
    if (calls === 2) { assert.equal(orgHeader(init), "2"); return response({}, 401); }
    if (calls === 3) {
      assert.ok(String(input).endsWith("/auth/refresh"));
      assert.equal(orgHeader(init), undefined);
      return response({ access_token: "new", refresh_token: "new-refresh" });
    }
    assert.equal(orgHeader(init), "2"); assert.equal(auth(init), "Bearer new");
    return response([]);
  };
  const scoped = await selectOrganization(c, 2);
  assert.deepEqual(await scoped.request("/machines/"), []);
  assert.equal(calls, 4);
});

test("login verifies account before securely storing both tokens", async () => {
  const s = store(); let calls = 0;
  globalThis.fetch = async (input, init) => {
    calls++;
    if (calls === 1) {
      assert.equal(String(input), "https://example.test/auth/login");
      assert.deepEqual(JSON.parse(String(init?.body)), { email: "test@example.test", password: "password" });
      return response({ access_token: "access", refresh_token: "refresh" });
    }
    assert.equal(auth(init), "Bearer access");
    assert.equal(await s.getItem(), null);
    return response(user);
  };
  assert.equal((await signInAndStore(s, "test@example.test", "password")).user.id, 5);
  assert.deepEqual(JSON.parse((await s.getItem())!), { access: "access", refresh: "refresh" });
});

test("bad login/account response and secure storage failure cannot activate session", async () => {
  for (const bad of [null, {}, { access_token: "access" }]) {
    globalThis.fetch = async () => response(bad);
    await assert.rejects(signInAndStore(store(), "a", "b"), /Invalid authentication/);
  }
  let calls = 0;
  globalThis.fetch = async () => ++calls === 1 ? response({ access_token: "a", refresh_token: "r" }) : response({});
  const s = store();
  await assert.rejects(signInAndStore(s, "a", "b"), /invalid account/);
  assert.equal(await s.getItem(), null);
  calls = 0; s.setItem = async () => { throw new Error("private storage details"); };
  globalThis.fetch = async () => ++calls === 1 ? response({ access_token: "a", refresh_token: "r" }) : response(user);
  await assert.rejects(signInAndStore(s, "a", "b"), (e: unknown) => e instanceof ApiError && !e.message.includes("private"));
});

test("refresh on 401 stores new pair then retries once", async () => {
  const s = store(); const c = client(s); let calls = 0;
  globalThis.fetch = async (input, init) => {
    calls++;
    if (calls === 1) { assert.equal(auth(init), "Bearer old"); return response({}, 401); }
    if (calls === 2) {
      assert.equal(String(input), "https://example.test/auth/refresh");
      assert.deepEqual(JSON.parse(String(init?.body)), { refresh_token: "refresh-old" });
      return response({ access_token: "new", refresh_token: "refresh-new" });
    }
    assert.equal(auth(init), "Bearer new");
    assert.deepEqual(JSON.parse((await s.getItem())!), { access: "new", refresh: "refresh-new" });
    return response({ ok: true });
  };
  assert.deepEqual(await c.request("/tickets/"), { ok: true });
  assert.equal(calls, 3);
});

test("simultaneous 401s share one refresh and retry with new token", async () => {
  const c = client(); let refreshes = 0; let initial = 0;
  globalThis.fetch = async (input, init) => {
    if (String(input).endsWith("/auth/refresh")) { refreshes++; return response({ access_token: "new", refresh_token: "new-refresh" }); }
    if (auth(init) === "Bearer old") { initial++; await new Promise(resolve => setTimeout(resolve, 5)); return response({}, 401); }
    return response({ ok: true });
  };
  await Promise.all([c.request("/one"), c.request("/two")]);
  assert.equal(initial, 2); assert.equal(refreshes, 1);
});

test("refresh failure, 403, and second 401 never loop", async () => {
  for (const scenario of ["refresh401", "retry401", "forbidden", "network", "malformed"]) {
    let calls = 0;
    globalThis.fetch = async () => {
      calls++;
      if (scenario === "forbidden") return response({}, 403);
      if (calls === 1) return response({}, 401);
      if (scenario === "network") throw new Error("private network error");
      if (scenario === "malformed") return response({});
      if (scenario === "refresh401" || calls === 3) return response({}, 401);
      return response({ access_token: "new", refresh_token: "new-refresh" });
    };
    await assert.rejects(client().request("/tickets/"));
    assert.equal(calls, scenario === "forbidden" ? 1 : scenario === "retry401" ? 3 : 2);
  }
});

test("refresh persistence failure prevents retry", async () => {
  const s = store(); s.setItem = async () => { throw new Error("secret"); };
  let calls = 0;
  globalThis.fetch = async () => ++calls === 1 ? response({}, 401) : response({ access_token: "new", refresh_token: "new-refresh" });
  await assert.rejects(client(s).request("/tickets/"), (e: unknown) => e instanceof ApiError && !e.message.includes("secret"));
  assert.equal(calls, 2);
});

test("restore refreshes expired access, clears revoked sessions, preserves transient failures", async () => {
  const initial = JSON.stringify({ access: "old", refresh: "refresh-old" });
  const s = store(initial); let calls = 0;
  globalThis.fetch = async () => ++calls === 1 ? response({}, 401)
    : calls === 2 ? response({ access_token: "new", refresh_token: "new-refresh" }) : response(user);
  assert.equal((await restoreSession(s))?.user.id, 5);
  assert.equal(JSON.parse((await s.getItem())!).refresh, "new-refresh");
  const expired = store(initial); calls = 0;
  globalThis.fetch = async () => { calls++; return response({}, 401); };
  await assert.rejects(restoreSession(expired)); assert.equal(await expired.getItem(), null);
  const offline = store(initial);
  globalThis.fetch = async () => { throw new Error("private details"); };
  await assert.rejects(restoreSession(offline)); assert.equal(await offline.getItem(), initial);
});

test("legacy access-only session expires safely without deleting unrelated data", async () => {
  const s = store("old");
  globalThis.fetch = async () => response({}, 401);
  await assert.rejects(restoreSession(s));
  assert.equal(await s.getItem(), null);
  const failing = store("old"); failing.removeItem = async () => { throw new Error("secret"); };
  await assert.rejects(restoreSession(failing), (e: unknown) => e instanceof SessionRemovalError);
});

test("logout racing refresh cannot restore saved credentials", async () => {
  const s = store(); const c = client(s);
  let release!: () => void; const wait = new Promise<void>(r => { release = r; });
  let started!: () => void; const onStart = new Promise<void>(r => { started = r; });
  s.setItem = async () => { started(); await wait; };
  globalThis.fetch = async (_, init) => auth(init) ? response({}, 401) : response({ access_token: "new", refresh_token: "new-refresh" });
  const pending = c.request("/tickets/");
  await onStart;
  const closing = c.close();
  release();
  await assert.rejects(pending);
  await closing;
  assert.equal(await s.getItem(), null);
});

test("sign-out does not wait for a hung refresh network request", async () => {
  const s = store("saved"); const c = client(s);
  let started!: () => void;
  const onStart = new Promise<void>(resolve => { started = resolve; });
  globalThis.fetch = async (_, init) => {
    if (auth(init)) return response({}, 401);
    started();
    return new Promise<Response>(() => {});
  };
  void c.request("/machines/").catch(() => {});
  await onStart;
  await Promise.race([c.close(), new Promise<never>((_, reject) => setTimeout(() => reject(new Error("logout hung")), 200))]);
  assert.equal(await s.getItem(), null);
});

test("late refresh write cannot resurrect a session or delete a new session", async () => {
  const values = new Map<string, string>();
  let release!: () => void; const wait = new Promise<void>(resolve => { release = resolve; });
  let started!: () => void; const onStart = new Promise<void>(resolve => { started = resolve; });
  let delay = false;
  const disk = {
    async getItem(key: string) { return values.get(key) ?? null; },
    async setItem(key: string, value: string) {
      if (delay && key.startsWith("fpconnect.mobile.session.")) { delay = false; started(); await wait; }
      values.set(key, value);
    },
    async removeItem(key: string) { values.delete(key); },
  };
  const oldStore = await createSessionStore(disk);
  await oldStore.setItem(JSON.stringify({ access: "old", refresh: "refresh-old" }));
  const oldClient = client(oldStore);
  globalThis.fetch = async (_, init) => auth(init) ? response({}, 401) : response({ access_token: "new", refresh_token: "new-refresh" });
  delay = true;
  const pending = oldClient.request("/machines/");
  await onStart;
  await oldClient.close();
  assert.equal(await openSessionStore(disk), null);
  const nextStore = await createSessionStore(disk);
  await nextStore.setItem("new-account-token");
  release();
  await assert.rejects(pending);
  assert.equal(await (await openSessionStore(disk))?.getItem(), "new-account-token");
  assert.equal([...values.keys()].filter(key => key.startsWith("fpconnect.mobile.session.")).length, 1);
});

test("secure storage migration preserves legacy drafts", async () => {
  const values = new Map<string, string>([["fpconnect.mobile.access.v1", "legacy-token"], ["fpconnect.offline.ticketQueue", "legacy-drafts"]]);
  const disk = {
    async getItem(key: string) { return values.get(key) ?? null; },
    async setItem(key: string, value: string) { values.set(key, value); },
    async removeItem(key: string) { values.delete(key); },
  };
  const migrated = await openSessionStore(disk);
  assert.equal(await migrated?.getItem(), "legacy-token");
  await migrated?.removeItem();
  assert.equal(values.get("fpconnect.offline.ticketQueue"), "legacy-drafts");
});

test("web secure-storage error is specific and unexpected errors are sanitized", () => {
  try { requireNativeSessionStorage("web"); assert.fail("web should be rejected"); }
  catch (error) { assert.match(restoreErrorMessage(error), /native secure storage; web is not supported/); }
  assert.equal(restoreErrorMessage(new Error("private internals")), "Could not restore session securely.");
  assert.doesNotThrow(() => requireNativeSessionStorage("ios"));
});

test("API URL accepts only a well-formed HTTPS origin", () => {
  const original = process.env.EXPO_PUBLIC_API_URL;
  try {
    for (const url of ["https://api.example.com", "https://api.example.com:8443/"]) {
      process.env.EXPO_PUBLIC_API_URL = url;
      assert.equal(apiUrl(), url.replace(/\/$/, ""));
    }
    for (const url of ["", "http://example.test", "https://", "https://api.example.com/path",
      "https://api.example.com/?q=test", "https://api.example.com/#fragment", "https://user:pass@api.example.com",
      "https://api.example.com?", "https://api.example.com#", "https://api.example.com\\path",
      "https://bad host", "https://api.example.com:99999"]) {
      process.env.EXPO_PUBLIC_API_URL = url;
      assert.throws(() => apiUrl(), (error: unknown) => error instanceof ApiError && error.kind === "configuration");
    }
  } finally { process.env.EXPO_PUBLIC_API_URL = original; }
});

test("create guards ambiguous responses and concurrent retries", async () => {
  for (const status of [500, 408, 429]) {
    const m = marker(); let calls = 0;
    globalThis.fetch = async () => { calls++; return response({}, status); };
    await assert.rejects(createTicket(m, client(), "Test", "medium"));
    assert.equal(await hasUnconfirmedTicket(m), true);
    await assert.rejects(createTicket(m, client(), "Test", "medium"), /Reconcile/);
    assert.equal(calls, 1);
    await acknowledgeUnconfirmedTicket(m);
  }
  const m = marker();
  globalThis.fetch = async () => response({ id: 4 }, 201);
  assert.equal((await createTicket(m, client(), "Test", "medium")).id, 4);
  assert.equal(await hasUnconfirmedTicket(m), true);
});

test("ticket create retries only a rejected authenticated request after refresh", async () => {
  const m = marker(); let calls = 0;
  globalThis.fetch = async (input, init) => {
    calls++;
    if (calls === 1) { assert.equal(auth(init), "Bearer old"); return response({}, 401); }
    if (calls === 2) { assert.ok(String(input).endsWith("/auth/refresh")); return response({ access_token: "new", refresh_token: "new-refresh" }); }
    assert.equal(auth(init), "Bearer new");
    assert.equal(await hasUnconfirmedTicket(m), true);
    return response({ id: 8 }, 201);
  };
  assert.equal((await createTicket(m, client(), "Test", "medium")).id, 8);
  assert.equal(calls, 3);
  assert.equal(await hasUnconfirmedTicket(m), true);
});

test("create rejects parallel submissions and preserves guard on a lost response", async () => {
  const m = marker();
  let release!: () => void; const wait = new Promise<void>(resolve => { release = resolve; });
  let calls = 0;
  globalThis.fetch = async () => { calls++; await wait; throw new Error("response lost"); };
  const first = createTicket(m, client(), "Test", "medium");
  await assert.rejects(createTicket(m, client(), "Test", "medium"), /already in progress/);
  release();
  await assert.rejects(first);
  assert.equal(await hasUnconfirmedTicket(m), true);
  assert.equal(calls, 1);
});

test("definitive ticket rejection clears marker but malformed success does not", async () => {
  for (const status of [403, 422]) {
    const m = marker();
    globalThis.fetch = async () => response({}, status);
    await assert.rejects(createTicket(m, client(), "Test", "medium"));
    assert.equal(await hasUnconfirmedTicket(m), false);
  }
  const m = marker();
  globalThis.fetch = async () => response({});
  await assert.rejects(createTicket(m, client(), "Test", "medium"));
  assert.equal(await hasUnconfirmedTicket(m), true);
});

test("ticket marker storage failure prevents submission", async () => {
  const m = marker(); m.setItem = async () => { throw new Error("storage"); };
  let calls = 0; globalThis.fetch = async () => { calls++; return response({}); };
  await assert.rejects(createTicket(m, client(), "Test", "medium"));
  assert.equal(calls, 0);
});

test("validation and auth errors do not expose server bodies", async () => {
  for (const status of [401, 403, 422, 500, 503]) {
    globalThis.fetch = async () => response({ detail: "private internal data" }, status);
    await assert.rejects(apiRequest("/any"), (e: unknown) => e instanceof ApiError && !e.message.includes("private"));
  }
  process.env.EXPO_PUBLIC_API_URL = "http://localhost:8000";
  try { await assert.rejects(apiRequest("/any"), /HTTPS/); }
  finally { process.env.EXPO_PUBLIC_API_URL = "https://example.test"; }
});

test("list validation rejects malformed records", async () => {
  globalThis.fetch = async () => response([{ id: 1, title: "Test", priority: "medium", status: "open" }]);
  assert.equal((await fetchList("/tickets/", client(), isTicket)).length, 1);
  globalThis.fetch = async () => response([{ id: 1, title: null }]);
  await assert.rejects(fetchList("/tickets/", client(), isTicket), /invalid list/);
  globalThis.fetch = async () => response([{ id: 2, code: "M", name: "Machine", location: "Test", type: "test", status: "unknown", last_check: "2026-01-01" }]);
  assert.equal((await fetchList("/machines/", client(), isMachine)).length, 1);
  globalThis.fetch = async () => response([{ id: 2, location: null }]);
  await assert.rejects(fetchList("/machines/", client(), isMachine), /invalid list/);
});
