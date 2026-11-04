/**
 * Explicit public marketing routes. Keep authenticated product routes private.
 *
 * Security: never infer that a route is public from an arbitrary prefix. Only
 * the marketing subpaths deliberately listed here may skip the auth gate.
 */
export const PUBLIC_MARKETING_ROUTES = new Set([
  "/",
  "/login",
  "/diagnostic",
  "/recursos",
  "/solucoes",
  "/demonstracao",
  "/ia-responsavel",
  "/privacidade",
]);

export function isPublicMarketingRoute(pathname: string): boolean {
  if (!pathname) return false;
  const normalized = pathname.length > 1 && pathname.endsWith("/")
    ? pathname.slice(0, -1)
    : pathname;
  return PUBLIC_MARKETING_ROUTES.has(normalized);
}
