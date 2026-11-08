import { isPublicMarketingRoute } from "./publicRoutes";
import robots from "@/app/robots";
import sitemap from "@/app/sitemap";

describe("OPSPECTA public marketing routes", () => {
  it.each([
    "/",
    "/login",
    "/diagnostic",
    "/recursos",
    "/solucoes",
    "/demonstracao",
    "/ia-responsavel",
    "/recursos/",
  ])("makes only explicitly allowed public routes accessible: %s", (path) => {
    expect(isPublicMarketingRoute(path)).toBe(true);
  });

  it.each([
    "/dashboard",
    "/tickets",
    "/settings",
    "/maintenance",
    "/api/session",
    "/recursos/private",
    "/solucoes/admin",
    "/diagnostic/records",
    "/login/reset/admin",
    "/",
  ].filter((route) => route !== "/"))(
    "never makes authenticated routes public: %s",
    (path) => {
      expect(isPublicMarketingRoute(path)).toBe(false);
    },
  );

  it("rejects missing paths", () => {
    expect(isPublicMarketingRoute("")).toBe(false);
  });

  it("publishes only existing marketing pages in the canonical sitemap", () => {
    const entries = sitemap();

    expect(entries.map(({ url }) => url)).toEqual([
      "https://www.fpconnect.tec.br/",
      "https://www.fpconnect.tec.br/solucoes",
      "https://www.fpconnect.tec.br/diagnostic",
      "https://www.fpconnect.tec.br/recursos",
      "https://www.fpconnect.tec.br/demonstracao",
      "https://www.fpconnect.tec.br/ia-responsavel",
    ]);
    expect(entries.every(({ url }) => isPublicMarketingRoute(new URL(url).pathname))).toBe(true);
  });

  it("points crawlers to the sitemap without listing private product pages", () => {
    const metadata = robots();
    const rule = Array.isArray(metadata.rules) ? metadata.rules[0] : metadata.rules;

    expect(metadata.host).toBe("https://www.fpconnect.tec.br");
    expect(metadata.sitemap).toBe("https://www.fpconnect.tec.br/sitemap.xml");
    expect(rule.disallow).toContain("/dashboard");
    expect(rule.disallow).toContain("/api/");
  });
});
