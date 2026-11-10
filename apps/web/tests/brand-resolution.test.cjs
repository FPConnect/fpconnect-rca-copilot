const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const sharp = require("sharp");

const brand = path.resolve(__dirname, "../public/brand");

test("landing artwork has enough source pixels for its capped 2x display", async () => {
  const hero = await sharp(path.join(brand, "opspecta-hero.png")).metadata();
  const portuguese = await sharp(path.join(brand, "opspecta-brand-banner.jpg")).metadata();
  const english = await sharp(path.join(brand, "opspecta-brand-banner-en.png")).metadata();
  const logo = await sharp(path.join(brand, "opspecta-logo.png")).metadata();

  assert.ok(Math.min(hero.width, hero.height * 4 / 3) >= 620 * 2);
  assert.ok(portuguese.width >= 546 * 2);
  assert.ok(english.width >= 546 * 2);
  assert.ok(logo.width >= 44 * 2 && logo.height >= 44 * 2);
});
