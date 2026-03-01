# Mobile App (Expo)

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
