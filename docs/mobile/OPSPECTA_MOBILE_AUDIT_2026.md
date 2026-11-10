# OPSPECTA mobile audit

**Assessment date:** 2026-11-09
**Scope:** `apps/mobile` source, API integration, local ticket queue, Expo configuration, dependency audit and mobile CI. This is a code review and static validation, not a penetration test or physical-device/release-build test.

## Executive assessment

The mobile app is an Expo prototype, not a production client for operational or customer data. It has a typed navigation shell and a local ticket draft queue, but no sign-in/session lifecycle, no API-backed dashboard or equipment inventory, no behavioral test suite, and several settings actions that only display success dialogs. The ticket-sync path is not currently wired to the API's authenticated contract.

Do not use the dashboard, equipment statuses or seeded tickets as live fleet data. Do not onboard customer information until authentication, organization isolation, local data protection and the release gates below are addressed.

## Findings

| Priority | Finding | Evidence and impact |
|---|---|---|
| **P0 — release blocker** | Ticket synchronization has no authenticated session. | The screen calls `syncPendingTickets()` without a token ([tickets.tsx](../../apps/mobile/app/tickets.tsx)); the service makes the POST with an optional token ([offlineTickets.ts](../../apps/mobile/src/services/offlineTickets.ts)), while the API create route requires access level 2 ([tickets.py](../../apps/api/app/api/routes/tickets.py)). There is no mobile sign-in screen or session provider. In practice, queued ticket creation cannot satisfy the server contract; failed authorization is then labeled as an offline failure. |
| **P0 — release blocker** | Tenant/customer isolation is not supplied by the mobile app or demonstrated by the baseline API. | There is no organization context or membership selection in the app. A mobile client cannot provide a substitute for server-side authorization; this must be resolved at the API boundary before real multi-customer records are used. See the [security gap register](../security/OPSPECTA_SECURITY_GAPS.md). |
| **P1 — misleading operational state** | Dashboard, activity and machine inventory are hard-coded sample values. | The dashboard declares fixed metrics and recent activity ([index.tsx](../../apps/mobile/app/index.tsx)); the machine screen declares six equipment records with apparent online/offline states and recent check times ([machines.tsx](../../apps/mobile/app/machines.tsx)). Without a persistent demo label, these can be mistaken for real equipment state, including life-support equipment. |
| **P1 — false synchronization state** | Seed tickets appear to be server records. | The initial local ticket dataset assigns `serverId` values and `syncStatus: "synced"` to fabricated examples ([offlineTickets.ts](../../apps/mobile/src/services/offlineTickets.ts)). This makes sample data indistinguishable from actual API data in the ticket list. |
| **P1 — dependency risk** | Production dependency audit reports high-severity advisories, but CI only fails at critical severity. | `npm audit --omit=dev` reported **6 high, 16 moderate and 1 low** advisories at assessment time. The audit identifies `expo-router`/`query-string` and other transitive packages among the high findings. CI uses `--audit-level=critical` ([test-mobile.yml](../../.github/workflows/test-mobile.yml)), so these high findings do not fail the job. The automatic suggested Expo/Router upgrades are major-version changes; do not apply `npm audit fix --force` without a compatible Expo SDK upgrade and regression testing. |
| **P1 — no behavioral verification** | The mobile test command is a successful placeholder. | `npm test` only prints `No tests yet` and exits 0 ([package.json](../../apps/mobile/package.json)); CI runs that command ([test-mobile.yml](../../.github/workflows/test-mobile.yml)). A green job currently does not verify ticket creation/sync, persistence, screen states or error behavior. |
| **P1 — environment configuration** | API URL falls back to localhost. | `EXPO_PUBLIC_API_URL` defaults to `http://localhost:8000` ([offlineTickets.ts](../../apps/mobile/src/services/offlineTickets.ts)). On a physical phone, localhost refers to that phone, not the developer workstation or production API. Missing configuration therefore cannot result in a valid remote connection. |
| **P2 — local privacy and durability** | Ticket content is stored in unencrypted AsyncStorage; queue writes are separate operations. | Ticket and queue JSON use AsyncStorage ([offlineTickets.ts](../../apps/mobile/src/services/offlineTickets.ts)); creating a ticket writes the ticket list and queue concurrently rather than transactionally. Device loss, app-data extraction, storage corruption or a partial write can expose or orphan unsynced service data. |
| **P2 — error handling and retry semantics** | Sync treats all failures as offline and lacks automatic connectivity-driven retry. | A broad catch marks every rejected response—including authorization, validation and server errors—as offline and requeues it ([offlineTickets.ts](../../apps/mobile/src/services/offlineTickets.ts)). Sync runs at bootstrap and on button press ([tickets.tsx](../../apps/mobile/app/tickets.tsx)); the installed NetInfo dependency is not used. There is also no server idempotency key, so retrying after a server-side create but before receiving its response may create a duplicate. |
| **P2 — settings are previews** | Profile, theme and notification controls are not persisted or connected to backend/device behavior. | Profile save and notification save show success alerts without saving; theme changes only local component state ([settings.tsx](../../apps/mobile/app/settings.tsx)). Data export is explicitly unavailable. These controls should be labeled as preview or implemented before being presented as functional settings. |
| **P2 — malformed local state** | Stored JSON is parsed without runtime validation or recovery. | `readJson` casts `JSON.parse` directly to the requested type ([offlineTickets.ts](../../apps/mobile/src/services/offlineTickets.ts)). A corrupted or obsolete stored value can reject app bootstrap or break screen rendering; TypeScript types do not validate persisted data. |

## Validation performed

- `npm run typecheck`: passed.
- `npm run doctor`: **18/18 checks passed**.
- `npm test`: exited successfully but ran **no tests**.
- `npm audit --omit=dev`: **6 high, 16 moderate, 1 low** advisories reported; CI threshold does not block high severity.
- No emulator, physical device, production API, release build, or customer data was used.

## Recommended remediation order

1. Define and implement mobile authentication, secure session storage, expiry/logout behavior and an authenticated API client. Confirm server authorization and tenant scope first.
2. Remove sample fleet/ticket records from operational views or make demo state unmistakable and impossible to confuse with live data.
3. Replace dashboard/equipment placeholders with the authorized API contract and explicit loading, empty, error and stale-data states.
4. Add service and screen tests for login, create-while-offline, sync success, authorization/validation/server failures, restart persistence and duplicate retry behavior. Make CI fail when the test runner has no tests.
5. Protect any customer service data stored offline, validate/version local schemas, make queue updates recoverable, and define idempotent retry behavior.
6. Resolve dependency advisories through a compatible SDK patch or a planned Expo SDK upgrade; document any remaining risk and set an explicit severity policy.
7. Make profile/preferences controls actually persist, or label/disable them as preview.
8. Run device-level tests and a signed release-build review before describing the app as production-ready.

These are recommendations, not changes made by this audit. No dependency upgrade, authentication design or customer-data workflow was assumed.
