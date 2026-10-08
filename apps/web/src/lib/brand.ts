export function getAppName() {
  return process.env.NEXT_PUBLIC_APP_NAME?.trim() || "OPSPECTA";
}

export const APP_NAME = getAppName();
