const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");

test("authenticated shell reserves mobile-safe width and padding", () => {
  const source = read("src/components/AppShell.tsx");
  assert.match(source, /app-theme app-viewport flex w-full min-w-0/);
  assert.match(source, /app-main w-full min-w-0 flex-1 p-4 sm:p-6/);
});

test("portrait layout follows the dynamic viewport and mobile safe areas", () => {
  const css = read("src/app/globals.css");
  const sidebar = read("src/components/Sidebar.tsx");
  const modal = read("src/components/Modal.tsx");

  assert.match(css, /\.app-viewport[\s\S]*min-height: 100dvh/);
  assert.match(css, /\.app-main[\s\S]*safe-area-inset-bottom/);
  assert.match(css, /\.mobile-navigation[\s\S]*height: 100dvh[\s\S]*overflow-y: auto/);
  assert.match(css, /\.modal-layer[\s\S]*safe-area-inset-top[\s\S]*safe-area-inset-bottom/);
  assert.match(sidebar, /mobile-navigation flex w-64/);
  assert.match(modal, /modal-layer fixed inset-0/);
  assert.match(modal, /modal-panel relative my-auto/);
});

test("public and transitional screens use the same dynamic viewport contract", () => {
  const landing = read("src/app/page.tsx");
  const diagnostic = read("src/app/diagnostic/page.tsx");
  const authGuard = read("src/components/AuthGuard.tsx");

  assert.match(landing, /brand-surface app-viewport/);
  assert.match(landing, /BrandLogo compact className="sm:hidden"/);
  assert.match(diagnostic, /brand-surface app-viewport/);
  assert.match(diagnostic, /BrandLogo compact className="sm:hidden"/);
  assert.match(authGuard, /app-theme app-viewport grid place-items-center/);
});

test("ticket creation and ticket rows stack before the small breakpoint", () => {
  const source = read("src/app/tickets/page.tsx");
  assert.match(source, /grid grid-cols-1 gap-3 sm:grid-cols-\[minmax\(0,1fr\)_auto_auto\]/);
  assert.match(source, /w-full min-w-0 rounded-lg border/);
  assert.match(source, /flex min-w-0 flex-col gap-3 rounded-xl/);
  assert.match(source, /flex w-full flex-wrap items-center gap-2 sm:w-auto/);
  assert.doesNotMatch(source, /<div className="flex gap-3">/);
});

test("shared search and filters can shrink without widening the viewport", () => {
  const search = read("src/components/SearchBar.tsx");
  const filters = read("src/components/FilterBar.tsx");
  const css = read("src/app/globals.css");

  assert.match(search, /relative flex min-w-0 items-center/);
  assert.match(filters, /grid w-full min-w-0 grid-cols-1/);
  assert.match(filters, /min-w-0 flex-1 rounded-lg border/);
  assert.match(css, /\.app-theme :where\(input, select, textarea\)/);
  assert.match(css, /min-width: 0/);
  assert.match(css, /max-width: 100%/);
});

test("remaining fixed-width product controls become fluid in portrait mode", () => {
  const history = read("src/app/history/page.tsx");
  const playbooks = read("src/app/playbooks/page.tsx");
  const strategicMoats = read("src/app/strategic-moats/page.tsx");
  const settings = read("src/app/settings/page.tsx");

  assert.match(history, /className="w-full sm:w-64"/);
  assert.match(playbooks, /className="w-full sm:w-96"/);
  assert.match(strategicMoats, /w-full min-w-0 grid-cols-3/);
  assert.match(settings, /flex flex-col gap-3 pt-2 sm:flex-row/);
  assert.match(settings, /w-full rounded-lg border border-red-200/);
});
