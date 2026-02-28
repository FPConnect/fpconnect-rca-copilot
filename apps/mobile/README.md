# Mobile App (Expo)

## Known-good startup checklist (Android & iOS)

From repository root:

```bash
cd apps/mobile
npm run reinstall
npm run doctor
npm run start:go
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
