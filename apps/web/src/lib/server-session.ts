import "server-only";

export const SESSION_COOKIE = "fpconnect_session";

// The API validates the token and expiry and looks up the user. Never trust cookie presence.
export async function isValidSession(token: string | undefined): Promise<boolean> {
  if (!token || token.startsWith("fpconnect-preview-token-")) return false;
  const base = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL;
  if (!base) return false;
  try {
    const url = new URL(`${base.replace(/\/$/, "")}/auth/me`);
    if (process.env.NODE_ENV === "production" && url.protocol !== "https:") return false;
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) return false;
    const user = await response.json();
    return Boolean(user && Number.isInteger(user.id) && user.id > 0 && user.is_active !== false);
  } catch {
    return false;
  }
}
