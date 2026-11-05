import sitemap from "@/app/sitemap";
import robots from "@/app/robots";
import { isPublicMarketingRoute } from "@/lib/publicRoutes";

describe("OPSPECTA public-only discovery and privacy", () => {
  it("lists only explicitly approved marketing content in the XML sitemap", () => {
    const addresses = sitemap().map((entry) => new URL(entry.url));
    expect(addresses.length).toBeGreaterThanOrEqual(7);
    for (const address of addresses) {
      expect(address.host).toBe("www.fpconnect.tec.br");
      expect(isPublicMarketingRoute(address.pathname)).toBe(true);
    }
    expect(addresses.map((item) => item.pathname)).toContain("/privacidade");
    expect(addresses.map((item) => item.pathname)).not.toContain("/dashboard");
  });

  it("prevents authenticated product paths from being offered to crawlers", () => {
    const config = robots();
    const rules = JSON.stringify(config.rules);
    for (const route of ["/login", "/tickets", "/analyze", "/dashboard", "/api"]) {
      expect(rules).toContain(route);
    }
    expect(config.sitemap).toBe("https://www.fpconnect.tec.br/sitemap.xml");
  });
});
