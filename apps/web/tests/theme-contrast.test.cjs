const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const css = fs.readFileSync(path.join(root, "src/app/globals.css"), "utf8");
const appShell = fs.readFileSync(path.join(root, "src/components/AppShell.tsx"), "utf8");

function luminance(hex) {
  const channels = hex.match(/[a-f\d]{2}/gi).map((value) => {
    const channel = Number.parseInt(value, 16) / 255;
    return channel <= 0.03928
      ? channel / 12.92
      : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function contrast(foreground, background) {
  const lighter = Math.max(luminance(foreground), luminance(background));
  const darker = Math.min(luminance(foreground), luminance(background));
  return (lighter + 0.05) / (darker + 0.05);
}

test("dark theme maps gray and slate utilities inside the product shell", () => {
  assert.match(appShell, /app-theme flex min-h-screen/);
  assert.match(appShell, /app-theme min-h-screen bg-gray-50/);

  for (const utility of [
    "text-gray-900",
    "text-gray-600",
    "text-slate-950",
    "text-slate-600",
    "bg-gray-50",
    "bg-slate-50",
    "border-slate-200",
    "divide-slate-100",
  ]) {
    assert.match(css, new RegExp(`app-theme \\.${utility}`));
  }
});

test("dark product colors meet WCAG AA contrast for regular text", () => {
  const surfaces = ["#111827", "#1f2937"];
  const foregrounds = ["#f8fafc", "#cbd5e1"];

  for (const surface of surfaces) {
    for (const foreground of foregrounds) {
      assert.ok(
        contrast(foreground, surface) >= 4.5,
        `${foreground} on ${surface} must meet the 4.5:1 contrast threshold`,
      );
    }
  }
});

test("public landing page is not recolored by authenticated dark mode", () => {
  assert.doesNotMatch(css, /html\.dark body\s*\{/);
  assert.doesNotMatch(css, /html\.dark \.brand-surface/);
});
