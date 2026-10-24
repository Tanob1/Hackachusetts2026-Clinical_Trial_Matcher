# Build the downloadable app (APK)

This makes a real Android app you tap to install. No Expo Go.

The app talks to the server running on **your computer**. Not online yet.
So your computer must be on, running the server, on the same Wi-Fi as the phone.

---

## What is already set up

- The app points at your computer: `http://10.248.45.241:8000` (in the `.env` file).
- `eas.json` tells Expo to build an **APK** (the tap-to-install file).
- Android is allowed to reach a plain `http` server (`usesCleartextTraffic`).

If your computer's Wi-Fi address changes, open `.env` and change the IP.
Find the address with: `ipconfig getifaddr en0`

---

## Build the APK (one time, ~10 min)

You need a free Expo account first. I cannot make it for you.

1. Make a free account at https://expo.dev

2. In this folder, log in:
   ```bash
   npx expo login
   ```

3. Start the build (Expo builds it in the cloud):
   ```bash
   npx eas build --platform android --profile preview
   ```
   The first time, it asks a few questions — accept the defaults.

4. When it finishes, it prints a link. Open the link on your **phone**.
   Download the `.apk` and tap it. Android installs it like any app.
   (You may need to allow "install from this source" once — Android asks.)

---

## Use it

1. Keep the server running on your computer:
   ```bash
   cd ../clinical-trial-matcher-server
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. Phone and computer on the same Wi-Fi.
3. Open the app. Log in: `demo@trialmatcher.app` / `demodemo123`

---

## iPhone

Apple does not allow a simple download-and-tap file.
It needs a paid Apple Developer account ($99/year) and TestFlight.
That is Apple's rule. Android is the easy path.

---

## Later: put the server online

When you want the app to work without your computer on, host the server
(e.g. Railway, Render, Fly.io). Then change the IP in `.env` to that web
address and build the APK again.
