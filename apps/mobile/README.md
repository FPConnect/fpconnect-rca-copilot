# Mobile App (Expo)

## Prototype limitations and setup

This app is not approved for customer or patient information. The integrated
tenant foundation requires independent review and PostgreSQL, storage and
migration rehearsal. Regulatory, backup/restore and device/release validation
gates remain open. Stored equipment status is not verified live telemetry.

Set `EXPO_PUBLIC_API_URL` to the HTTPS origin of a reachable test API **before**
starting Expo (for example `$env:EXPO_PUBLIC_API_URL="https://test.example"` in
PowerShell). There is deliberately no localhost or HTTP fallback; use a trusted
HTTPS development endpoint and test-only data. Expo public variables are bundled
into the client, so never put secrets in them.

Native sign-in calls `/auth/login`, verifies `/auth/me`, and stores the access and
refresh token pair together in Expo SecureStore. On launch it verifies the saved
session. A 401 triggers one refresh and at most one retry of the rejected
request; concurrent refreshes share one exchange. A rejected/expired refresh
requires sign-in again. Transient errors retain the saved session. Older
access-only sessions can be used until their access token expires. Sessions use
separate secure-storage slots: sign-out does not wait for a pending network
refresh, and an obsolete refresh write cannot overwrite a subsequent session.
Legacy offline draft keys are not changed during session migration or sign-out.

The current backend issues a new refresh token but does **not** invalidate the
old one during refresh; client replacement is not server-side replay protection.
Sign-out removes local tokens but does not revoke them at the server. Web sign-in
is disabled because this secure storage path is native-only.

The tenant-foundation backend exposes `GET /auth/organizations` and
`POST /auth/select-organization`. After sign-in or restart, explicitly select
an active organization; switching revalidates the new selection. Every
organization-scoped request includes `X-Organization-Id`, including after
refresh. A 403 does not automatically retry with another organization.
Selection returns a membership role and access level; the server checks live
membership on every operation, and `/auth/me` is not used for tenant authority.
Online ticket creation is available to selected memberships at access level 2
or higher for test workflows; the API enforces the current membership on every
request, including after a role change.
Do not treat this client as evidence of isolation or use customer data. If
secure-token removal fails, retry it from the sign-in screen; do not clear app
data as a workaround if legacy drafts must be preserved.

Ticket creation is online-only and requires access level 2. This enables scoped
test workflows, not customer or patient data use. A durable, non-sensitive
local marker is written before submission and retained even after a successful
response, so a crash before the user sees the result cannot invite a duplicate.
After every submission, verify the server list for the organization used in that
submission and acknowledge the warning before creating another. The guard does
not record which organization submitted the request; switch back to the original
organization or ask its administrator before acknowledging it. A network failure, 5xx, invalid success response, interrupted
app, or other ambiguous response likewise leaves creation blocked; contact an
administrator if necessary. A manual acknowledgement does not prove a ticket
was or was not created.
There is no server idempotency key or automatic retry after ambiguous ticket
failures; a 401 rejected by the backend authentication dependency may be retried
once after refresh. Existing legacy offline
drafts remain in their previous unencrypted AsyncStorage keys, are not displayed,
sent or deleted, and require a separately designed secure recovery/migration
before offline functionality can return. Do not clear application data if those
drafts are needed. The dashboard covers only the first 100 visible tickets.

`npm test` executes service tests and fails if the test file is absent. It does
not replace device, UI, secure-storage or end-to-end testing. To test the
mobile service against the integrated FastAPI application using a disposable
in-memory SQLite database, install the API dependencies, set `MOBILE_TEST_PYTHON`
to the absolute path of that Python executable, then run `npm run test:integration`
from `apps/mobile`. This runs FastAPI's in-process test
client, not a network/TLS or PostgreSQL test. On 2026-11-09,
`npm audit --omit=dev` with Expo 54.0.38 and expo-router 6.0.24 reported
6 high, 16 moderate and 1 low advisories.
The existing CI critical-only threshold does not block high findings; SDK-major
upgrades require a separate compatibility and security review.

On 2026-11-09 a non-forced `npm audit fix` was tested: production findings fell
to 5 high, 15 moderate and 1 low, while Expo Doctor, typecheck and 24 service
tests passed. The attempted lockfile changes were restored because high
advisories remained and npm proposed breaking Expo changes for some of them.
The restored lockfile again reports 6 high, 16 moderate and 1 low. The attempt
updated `fast-uri` 3.1.8→3.1.9, `glob` 13.0.6→13.0.7 and `node-forge`
1.4.0→1.4.3, and relocated Expo CLI dependencies with `semver` and `ws`
updates; `package.json` was unchanged.

Before release, review the affected dependency paths and runtime exposure, check
for supported upstream patches, and plan an Expo SDK upgrade with device and
release-build regression tests if needed. Resolve or formally accept remaining
advisories under the project's security policy; do not treat the current
critical-only CI threshold as clearance of high findings.

## Testing on a physical device (Android or iOS)

### Prerequisites

1. Install [Node.js 18+](https://nodejs.org)
2. Install **Expo Go** on your phone:
   - [Android — Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS — App Store](https://apps.apple.com/app/expo-go/id982107779)
3. Make sure your phone and computer are on the **same Wi-Fi network**

### Steps

```bash
cd apps/mobile
npm install
npm start          # starts the Expo dev server and shows a QR code
```

Open **Expo Go** on your phone and scan the QR code shown in the terminal.  
The app will load directly on your device — no cable required.

Or, from the repository root:

```bash
make install-mobile   # install dependencies
make dev-mobile       # start the Expo dev server
```

### Target a specific platform

```bash
npm run android   # Android emulator or connected device via USB
npm run ios       # iOS simulator (macOS only)
npm run web       # open in browser (Expo Web)
```

---

## Known-good startup checklist (Android & iOS)

## If `Missing script` appears

You are not on the latest commit in `apps/mobile`.

Run:

```bash
cd apps/mobile
git rev-parse --short HEAD
npm run
```

You must see scripts `doctor`, `start:go`, `start:dev-client`, and `test` in the list.

From repository root:

```bash
cd apps/mobile
npm run reinstall
npm run doctor
npm start
```

If you are using a **development build** (not Expo Go), use:

```bash
npm run start:dev-client
```

## Why this matters

If Metro reports mismatched package versions (e.g. `expo-router@4`, `react-native@0.76`, `react@18`), your local install is still using stale dependencies.

This app expects SDK 54-compatible versions declared in `package.json`.

## Quick validation

```bash
npm ls expo expo-dev-client expo-router react react-native
```

Expected major versions:

- `expo@54.x`
- `expo-dev-client@6.x`
- `expo-router@6.x`
- `react@19.1.0`
- `react-native@0.81.5`

## Run tests

```bash
npm test
# or from the repository root:
make test-mobile
```

## Manual reset only

```bash
npm run clean
```

To also remove the lockfile (full reset):

```bash
npm run clean:all
```
