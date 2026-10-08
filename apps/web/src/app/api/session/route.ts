import { NextRequest, NextResponse } from "next/server";
import { isValidSession, SESSION_COOKIE } from "@/lib/server-session";

export async function POST(request: NextRequest) {
  // Next may normalize nextUrl to an internal hostname behind a reverse proxy.
  // Compare the browser's Origin with the HTTP Host received for this request.
  const origin = request.headers.get("origin");
  let sameOrigin = false;
  try {
    const parsed = new URL(origin || "");
    sameOrigin = ["https:", "http:"].includes(parsed.protocol)
      && parsed.host === request.headers.get("host");
  } catch { /* Missing or malformed Origin is rejected. */ }
  if (!sameOrigin) {
    return new NextResponse(null, { status: 403 });
  }
  const authorization = request.headers.get("authorization") || "";
  const token = authorization.startsWith("Bearer ") ? authorization.slice(7) : undefined;
  const valid = await isValidSession(token);
  const response = NextResponse.json({ authenticated: valid }, {
    status: valid ? 200 : 401,
    headers: { "Cache-Control": "no-store" },
  });
  response.cookies.set(SESSION_COOKIE, valid ? token! : "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: valid ? 900 : 0,
  });
  return response;
}
