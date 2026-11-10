import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { test } from "node:test";
import assert from "node:assert/strict";
import { ApiError } from "../src/services/api";
import { discoverOrganizations, selectOrganization, signInAndStore } from "../src/services/session";
import { createTicket, hasUnconfirmedTicket } from "../src/services/ticketCreate";

test("mobile client uses real disposable FastAPI membership and ticket boundaries", async () => {
  const python = process.env.MOBILE_TEST_PYTHON;
  assert.ok(python, "Set MOBILE_TEST_PYTHON to the API virtualenv Python");
  const api = spawn(python, ["-u", "../mobile/tests/disposable_api.py"], {
    cwd: "../api", env: { ...process.env, PYTHONPATH: ".", APP_ENV: "development", SEED_TEST_ACCOUNTS: "false" }, stdio: ["pipe", "pipe", "inherit"],
  });
  const lines = createInterface({ input: api.stdout })[Symbol.asyncIterator]();
  const originalFetch = globalThis.fetch;
  const oldUrl = process.env.EXPO_PUBLIC_API_URL;
  process.env.EXPO_PUBLIC_API_URL = "https://disposable.example.test";
  globalThis.fetch = async (input, init) => {
    const url = new URL(String(input));
    api.stdin.write(JSON.stringify({
      method: init?.method ?? "GET", path: url.pathname + url.search,
      headers: init?.headers ?? {}, body: init?.body,
    }) + "\n");
    const next = await lines.next();
    if (next.done) throw new Error("Disposable API stopped");
    const result = JSON.parse(next.value);
    if (result.error) throw new Error(result.error);
    return new Response(result.body, { status: result.status, headers: { "content-type": "application/json" } });
  };
  let token: string | null = null;
  const store = { async getItem() { return token; }, async setItem(v: string) { token = v; }, async removeItem() { token = null; }, async removeStaleItem() { token = null; } };
  try {
    const session = await signInAndStore(store, "mobile@example.com", "SyntheticPass123!");
    assert.equal(session.user.access_level, 5);
    assert.equal((await discoverOrganizations(session.client)).length, 2);
    const first = await selectOrganization(session.client, 1);
    const second = await selectOrganization(session.client, 2);
    assert.equal(first.membership.accessLevel, 2);
    assert.equal(second.membership.accessLevel, 1);
    const ticketsA = await first.client.request<Array<{ title: string }>>("/tickets/");
    const ticketsB = await second.client.request<Array<{ title: string }>>("/tickets/");
    assert.deepEqual(ticketsA.map(t => t.title), ["One ticket"]);
    assert.deepEqual(ticketsB.map(t => t.title), ["Two ticket"]);
    const markers = new Map<string, string>();
    const markerStore = {
      async getItem(key: string) { return markers.get(key) ?? null; },
      async setItem(key: string, value: string) { markers.set(key, value); },
      async removeItem(key: string) { markers.delete(key); },
    };
    const created = await createTicket(markerStore, first.client, "Synthetic new ticket", "high");
    assert.ok(created.id > 0);
    assert.equal(created.title, "Synthetic new ticket");
    assert.equal(created.priority, "high");
    assert.equal(await hasUnconfirmedTicket(markerStore), true);
    const afterA = await first.client.request<Array<{ id: number }>>("/tickets/");
    const afterB = await second.client.request<Array<{ id: number }>>("/tickets/");
    assert.ok(afterA.some(ticket => ticket.id === created.id));
    assert.ok(!afterB.some(ticket => ticket.id === created.id));
    await assert.rejects(second.client.request("/tickets/", { method: "POST", body: { title: "Not allowed" } }),
      (error: unknown) => error instanceof ApiError && error.status === 403);
    await assert.rejects(session.client.request("/machines/"),
      (error: unknown) => error instanceof ApiError && error.status === 422);
  } finally {
    globalThis.fetch = originalFetch;
    process.env.EXPO_PUBLIC_API_URL = oldUrl;
    api.stdin.end();
    api.kill();
  }
});
