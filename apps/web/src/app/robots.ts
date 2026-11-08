import type { MetadataRoute } from "next";

const siteUrl = "https://www.fpconnect.tec.br";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: [
          "/",
          "/diagnostic",
          "/recursos",
          "/solucoes",
          "/demonstracao",
          "/ia-responsavel",
        ],
        disallow: [
          "/login",
          "/dashboard",
          "/tickets",
          "/machines",
          "/analyze",
          "/settings",
          "/access-control",
          "/alerts",
          "/contracts",
          "/health-checks",
          "/history",
          "/maintenance",
          "/metrics",
          "/notifications",
          "/playbooks",
          "/strategic-moats",
          "/api/",
        ],
      },
    ],
    sitemap: `${siteUrl}/sitemap.xml`,
    host: siteUrl,
  };
}
