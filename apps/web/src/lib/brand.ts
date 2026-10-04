export const DEFAULT_APP_NAME = "OPSPECTA";
export const LEGACY_APP_NAME = "FPConnect";
export const PRODUCT_DESCRIPTOR =
  "Inteligência operacional para serviços e ativos de tecnologia em saúde";

export function getAppName() {
  return process.env.NEXT_PUBLIC_APP_NAME?.trim() || DEFAULT_APP_NAME;
}

export function getBrandTransitionNotice(appName = getAppName()) {
  if (appName === LEGACY_APP_NAME) {
    return `${LEGACY_APP_NAME} é o nome histórico do projeto; ${DEFAULT_APP_NAME} é o nome de trabalho em validação.`;
  }

  return `${appName} — nome de trabalho em validação. Projeto anteriormente denominado ${LEGACY_APP_NAME}.`;
}

export const APP_NAME = getAppName();
export const BRAND_TRANSITION_NOTICE = getBrandTransitionNotice(APP_NAME);
