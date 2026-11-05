import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: ["/", "/recursos", "/solucoes", "/demonstracao", "/ia-responsavel", "/privacidade", "/diagnostic"],
        // The product contains account and service records. Never advertise
        // authenticated routes to search engines.
        disallow: [
          "/login", "/dashboard", "/tickets", "/machines", "/analyze",
          "/settings", "/reports", "/playbooks", "/api", "/profile",
        ],
      },
    ],
    sitemap: "https://www.fpconnect.tec.br/sitemap.xml",
    host: "https://www.fpconnect.tec.br",
  };
}
