# LinkRTC

A mobile app that matches a person's medical profile against real clinical
trials from [ClinicalTrials.gov](https://clinicaltrials.gov). **Fully offline** —
3,131 Massachusetts recruiting trials are bundled inside the app, so it needs no
server, no account, and no internet connection.

> This is an informational matching tool, not medical advice. It does not
> diagnose, treat, or tell anyone to join a study. Final eligibility is always
> determined by the trial team.

## What it does

- Opens to a sign-in screen (any email + any 8+ character password works — there
  is no real account system in this offline build).
- Loads with a pre-filled demo medical profile so the match feed is populated
  immediately.
- Lets you edit your profile: conditions, medications, allergies, history, etc.
- Runs the matching engine **on the device** (condition overlap, recruiting-first
  ordering) and shows a feed of relevant trials.
- Browse trial details, save trials, and open the full study on ClinicalTrials.gov.

All data (profile, saved trials) is stored locally on the phone.

## Tech

- React Native + Expo (SDK 58)
- TypeScript
- On-device matching engine in `src/data/matching.ts` (ported from the original
  FastAPI backend's logic)
- Bundled trial dataset in `src/data/trials.json`

## Project layout

```
src/
  api/        offline data layer (profile, trials, auth, settings — all local)
  data/       bundled trials.json, on-device matching engine, local store
  screens/    Onboarding (sign-in), MatchFeed, TrialDetail, SavedTrials,
              Settings, MedicalProfile
  navigation/ app navigator (tabs + stack)
  context/    auth context
  utils/      condition list, cache helpers
android/      native Android project (used to build the APK)
```

## Run it in development

```bash
npm install
npx expo start
```

Scan the QR code with Expo Go, or press `a` for an Android emulator.

## Build a standalone APK (no Expo Go needed)

Requires the Android SDK and JDK 17.

```bash
cd android
./gradlew assembleRelease
```

The installable APK lands at
`android/app/build/outputs/apk/release/app-release.apk`.

## Data source

Trials were exported from the ClinicalTrials.gov v2 API (Massachusetts,
recruiting). Each bundled record holds: NCT id, title, phase, conditions, city,
and recruiting status.
