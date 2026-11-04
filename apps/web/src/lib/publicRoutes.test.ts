import { isPublicMarketingRoute } from "./publicRoutes";

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
});
