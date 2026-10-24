# MOBILE APP ACCESS GUIDE

## Overview

Your Clinical Trial Matcher has a React Native mobile app built with Expo. It connects to the FastAPI backend for patient trial matching on mobile devices.

## Prerequisites

1. **Node.js installed** (version 20+)
   - Check: `node --version`
   - Download: https://nodejs.org/

2. **FastAPI server running**
   The mobile app connects to FastAPI on localhost:8000

## Installation

### Step 1: Install Dependencies
powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/app"
npm install

### Step 2: Configuration Done!
The .env file has been created with:
EXPO_PUBLIC_API_URL=http://localhost:8000

## Running the App

### Option 1: Web Browser (EASIEST)
powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/app"
npx expo start --web

Opens at: http://localhost:19006

### Option 2: Expo Development
powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/app"
npx expo start

Then:
- Press `w` for web browser
- Press `a` for Android emulator (if installed)
- Press `i` for iOS simulator (Mac only)
- Scan QR code with Expo Go app on phone

### Option 3: Physical Phone with Expo Go

1. Install Expo Go on your phone:
   - Android: Play Store
   - iOS: App Store

2. Find your computer IP:
   powershell
   ipconfig
   Look for IPv4 Address (e.g., 192.168.1.100)

3. Update app/.env:
   EXPO_PUBLIC_API_URL=http://YOUR_IP:8000

4. Start Expo and scan QR code

## App Features

- Sign In / Create Account
- Medical Profile (conditions, meds, allergies)
- Match Feed (browse relevant trials)
- Trial Details
- Saved Trials
- Settings

## Demo for Hackathon

**Easiest Demo:**
1. Start FastAPI: uvicorn app.main:app --reload
2. Start mobile in browser: npx expo start --web
3. Show mobile interface in browser

## Troubleshooting

**"Network request failed"**
- Ensure FastAPI is running on localhost:8000
- Check .env file configuration

**"Unable to resolve module"**
powershell
cd app
rm -r node_modules
npm install

**Expo version mismatch**
- Update Expo Go app from store

## Architecture

Mobile App (React Native/Expo)
        ?
  FastAPI Server
        ?
  SQLite Database

Ready to run!
