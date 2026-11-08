import type { MetadataRoute } from "next";

const siteUrl = "https://www.fpconnect.tec.br";

const publicPaths = [
  { path: "/", priority: 1.0 },
  { path: "/solucoes", priority: 0.9 },
  { path: "/diagnostic", priority: 0.9 },
  { path: "/recursos", priority: 0.8 },
  { path: "/demonstracao", priority: 0.8 },
  { path: "/ia-responsavel", priority: 0.6 },
] as const;

export default function sitemap(): MetadataRoute.Sitemap {
  return publicPaths.map(({ path, priority }) => ({
    url: `${siteUrl}${path}`,
    changeFrequency: "monthly",
    priority,
  }));
}
