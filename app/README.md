# Clinical Trial Matcher — Mobile App

Cross-platform mobile app (iOS + Android) built with React Native (Expo). It
lets a patient create a medical profile, browse clinical trials that may be
relevant, and save or express interest. The backend is a **separate repository**
and this app talks to it only over REST.

## ⚠️ Disclaimer

This is **informational matching, not medical advice**. It does not diagnose,
treat, or tell you to join any study. Talk to your doctor or the study team
before acting.

## Stack

- **React Native + Expo** (SDK 58)
- **React Navigation v7**
- Screens: Onboarding (Sign In / Create Account), Medical Profile, Match Feed,
  Trial Detail, Saved Trials, Settings
- Offline cache of last-loaded matches (non-identified data only)
- Tokens stored in `expo-secure-store` (Keychain / Keystore)

## Prerequisites

- Node.js 20+
- The Expo Go app on your phone (matching SDK 58), or an iOS/Android emulator
- The backend server running and reachable

## Quick start

```bash
npm install
cp .env.example .env
# Set the backend URL. For a physical phone, use your computer's LAN IP, e.g.:
#   EXPO_PUBLIC_API_URL=http://192.168.1.50:8000
npx expo start
```

Scan the QR with Expo Go, or press `i` / `a` for a simulator.

Demo login (after the server is seeded): `demo@trialmatcher.app` / `demodemo123`

> Note: if your machine's file-watch limit is low, start with
> `CI=1 npx expo start` to disable the watcher (no hot reload, but it runs).

## Configuration

| Env var | Purpose |
|---|---|
| `EXPO_PUBLIC_API_URL` | Base URL of the backend (default `http://localhost:8000`) |

`localhost` only works on a simulator running on the same machine as the server.
A physical phone must use the computer's LAN IP.

## Layout

```
App.tsx            root component
src/
  api/             axios client + endpoint wrappers (token attach + refresh)
  context/         AuthContext (sign in / register / logout)
  navigation/      stack + tabs
  screens/         the six screens
  utils/           offline cache, condition list
app.json           Expo config
```

> Not committed (see `.gitignore`): `node_modules/`, `.expo/`, `.env`, logs.
