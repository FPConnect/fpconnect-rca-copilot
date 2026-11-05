import type { MetadataRoute } from "next";

const domain = "https://www.fpconnect.tec.br";
const publicPaths = [
  { path: "/", priority: 1.0 },
  { path: "/solucoes", priority: 0.9 },
  { path: "/diagnostic", priority: 0.9 },
  { path: "/recursos", priority: 0.8 },
  { path: "/demonstracao", priority: 0.8 },
  { path: "/ia-responsavel", priority: 0.6 },
  { path: "/privacidade", priority: 0.4 },
];

export default function sitemap(): MetadataRoute.Sitemap {
  return publicPaths.map(({ path, priority }) => ({
    url: domain + path,
    lastModified: new Date("2026-11-04T00:00:00-03:00"),
    changeFrequency: "monthly",
    priority,
  }));
}
