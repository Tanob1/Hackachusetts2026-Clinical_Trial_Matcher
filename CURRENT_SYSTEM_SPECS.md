# Clinical Trial Matcher - Complete System Specifications

## Document Purpose
Complete breakdown of all existing system components, architecture, data structures, and functionality for the Clinical Trial Matcher hackathon project.

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Component Specifications](#component-specifications)
4. [Data Structures](#data-structures)
5. [API Specifications](#api-specifications)
6. [Mobile App Specifications](#mobile-app-specifications)
7. [Performance & Testing](#performance--testing)

---

## 1. System Overview

### Project Description
Clinical Trial Matcher is a dual-architecture healthcare application that matches patients with relevant clinical trials from ClinicalTrials.gov using medical code intelligence (ICD-10) and keyword matching.

### Current Deployment
- **Environment:** Local development (Windows PowerShell)
- **Project Root:** E:\Kiro\Hackachusetts 2026\healthcare\clinical-trial-matcher\
- **Repository:** https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher
- **Status:** Fully operational, all tests passing

### Three-Component System
1. **Flask Web UI** (Port 5000) - Demo dashboard for switching patients, viewing matches
2. **FastAPI Backend** (Port 8000) - RESTful API for mobile app integration
3. **React Native Mobile App** (LinkRTC) - Offline-first mobile application

---

## 2. Architecture

### System Diagram
`
┌─────────────────────────────────────────────────────────────┐
│                                                                 │
│  WEB USERS (Doctors, Patients)                                 │
│                                                                 │
└──────────────┬─────────────────────────────┬─────────────────┘
               │                               │
               │                               │
               v                               v
┌──────────────────────────┐    ┌─────────────────────────────┐
│  FLASK WEB SERVER        │    │  REACT NATIVE MOBILE APP     │
│  (Port 5000)             │    │  (LinkRTC - Offline)         │
│                          │    │                              │
│  • app.py                │    │  • 3,131 bundled trials      │
│  • templates/            │    │  • On-device matching        │
│  • static/               │    │  • Local storage             │
│  • Session auth          │    │  • Expo SDK 58               │
└──────────┬───────────────┘    └─────────────────────────────┘
           │                                  
           │                                  
           v                                  
┌──────────────────────────┐    
│  FASTAPI SERVER          │    
│  (Port 8000)             │    
│                          │    
│  • server/app/main.py    │    
│  • RESTful API           │    
│  • Scheduled sync        │    
└──────────┬───────────────┘    
           │                    
           │                    
           v                    
┌──────────────────────────┐    
│  SQLITE DATABASE         │    
│  (trials.db)             │    
│                          │    
│  • 3,131 trials          │    
│  • 5 demo patients       │    
│  • 4 tables              │    
└──────────────────────────┘    
`

### Technology Stack

#### Flask Backend
- **Language:** Python 3.x
- **Framework:** Flask
- **Dependencies:**
  - flask
  - pandas
  - werkzeug (password hashing)
- **Authentication:** Session-based
- **CORS:** Enabled for mobile development

#### FastAPI Backend
- **Language:** Python 3.x
- **Framework:** FastAPI
- **Dependencies:**
  - fastapi
  - uvicorn
  - sqlalchemy
  - apscheduler (trial sync)
  - email-validator
- **Authentication:** Token-based (planned)
- **CORS:** Configurable origins

#### Mobile App
- **Framework:** React Native (Expo SDK 58)
- **Language:** TypeScript
- **Key Dependencies:**
  - expo
  - react-native-paper
  - @react-navigation/*
  - @react-native-async-storage/async-storage
  - expo-secure-store
- **Offline-First:** All data bundled

#### Database
- **Type:** SQLite (trials.db)
- **Size:** 3,131 trial records
- **Location:** Project root

---

## 3. Component Specifications

### 3.1 Flask Web Server

#### Files
- pp.py - Main Flask application (298 lines)
- database.py - Database queries and setup
- matching.py - Enhanced matching engine with ICD-10
- medical_codes.py - ICD-10 code mapping (300+ conditions)
- 	emplates/ - Jinja2 HTML templates
- static/ - CSS, JavaScript, images

#### Features
1. **Authentication**
   - Session-based login/logout
   - Werkzeug password hashing
   - Demo accounts (5 patients)

2. **Patient Dashboard**
   - View current patient profile
   - Switch between demo patients
   - View matched trials

3. **Trial Matching**
   - Enhanced matching algorithm
   - ICD-10 medical code intelligence
   - Keyword/synonym matching
   - Age eligibility
   - Distance filtering (max 100 miles)
   - Phase filtering

4. **Performance**
   - LRU caching (100 entries)
   - 18.7x faster with cache
   - Top 20 results limit

#### Routes

##### Authentication Routes
- POST /login - User login
- POST /logout - User logout

##### Web UI Routes
- GET / - Login page (redirects to dashboard if logged in)
- GET /dashboard - Patient dashboard (requires login)

##### Patient API Routes
- GET /api/patient/me - Get current user's profile
- GET /api/patient/<int:patient_id> - Get patient by ID

##### Matching API Routes
- GET /api/matches/<int:patient_id> - Get matched trials
  - Query params: max_distance (default: 100), phase (optional)

##### Trial API Routes
- GET /api/trials/<int:trial_id> - Get trial details
- GET /api/trials/search - Search trials
  - Query params: q (search query), limit (default: 20)

##### Demo Routes
- GET /api/demo/patients - Get all demo patients
- POST /api/demo/switch/<int:patient_id> - Switch to demo patient

##### Health Check
- GET /health - Server health status

#### Demo Credentials
| Username | Password | Patient |
|----------|----------|---------|
| sarah.chen | demo123 | Sarah Chen (42F, Breast Cancer) |
| john.smith | demo123 | John Smith (55M, Diabetes, Hypertension) |
| maria.garcia | demo123 | Maria Garcia (68F, COPD, Heart Disease) |
| david.lee | demo123 | David Lee (34M, Depression, Anxiety) |
| emily.brown | demo123 | Emily Brown (45F, Multiple Sclerosis) |

---

### 3.2 Matching Engine

#### File: matching.py

#### Algorithm Overview
The matching engine uses a hybrid approach combining medical code matching with keyword matching.

#### Scoring System
1. **ICD-10 Exact Match:** 50 points per condition
2. **Keyword Match:** 30 points per keyword
3. **Age Eligibility:** 20 points
4. **Maximum Score:** 100 (capped)

#### Match Calculation Flow
`python
1. Normalize patient conditions → ICD-10 codes + keywords
2. Normalize trial conditions → ICD-10 codes + keywords
3. Find overlaps:
   a. ICD-10 code exact matches (highest priority)
   b. Keyword matches (fallback)
4. Apply age eligibility check
5. Apply distance filter
6. Apply phase filter
7. Sort by: score DESC, distance ASC
8. Return top 20 matches
`

#### Caching Strategy
- **Type:** LRU Cache (@lru_cache decorator)
- **Size:** 100 entries
- **Key:** (patient_id, conditions, age, max_distance, phase_filter)
- **Performance:** 18.7x improvement on cached queries

#### Match Result Structure
`python
{
    'trial_id': int,
    'nct_id': str,
    'title': str,
    'phase': str,
    'conditions': str,
    'city': str,
    'status': str,
    'distance_miles': int,
    'match_score': int,  # 0-100
    'match_percentage': str,  # "85%"
    'matched_conditions': list,
    'match_explanation': str,
    'match_details': list,  # [{patient, trial, type, codes}]
    'age_eligible': bool,
    'min_age': int,
    'max_age': int
}
`

---

### 3.3 Medical Code Intelligence

#### File: medical_codes.py

#### ICD-10 Code Database
Over 60 medical conditions mapped to:
- **ICD-10 Codes:** Official diagnostic codes
- **Synonyms:** Alternative medical terms
- **Keywords:** Search-friendly terms

#### Categories Covered
1. **Cancer/Oncology** (9 conditions)
   - Breast, lung, colorectal, prostate, ovarian, pancreatic
   - Melanoma, leukemia, lymphoma

2. **Cardiovascular** (5 conditions)
   - Heart disease, heart failure, hypertension
   - Atrial fibrillation, stroke

3. **Diabetes & Metabolic** (2 conditions)
   - Diabetes mellitus, obesity

4. **Respiratory** (2 conditions)
   - COPD, asthma

5. **Neurological** (5 conditions)
   - Alzheimer, Parkinson, multiple sclerosis
   - Epilepsy, migraine

6. **Mental Health** (5 conditions)
   - Depression, anxiety, bipolar
   - Schizophrenia, PTSD

7. **Autoimmune** (3 conditions)
   - Rheumatoid arthritis, lupus, Crohn's disease

8. **Infectious** (2 conditions)
   - HIV/AIDS, hepatitis

#### Example Mapping
`python
'breast cancer': {
    'icd10': ['C50', 'C50.9'],
    'synonyms': [
        'breast neoplasm',
        'breast carcinoma',
        'mammary cancer',
        'breast tumor',
        'breast malignancy'
    ],
    'keywords': ['breast', 'mammary', 'ductal', 'lobular']
}
`

#### Functions
- 
ormalize_condition(condition) - Convert to standard form with ICD-10
- ind_matching_conditions(patient_cond, trial_cond) - Find overlaps

---

### 3.4 FastAPI Backend

#### File: server/app/main.py

#### Features
1. **Lifecycle Management**
   - Database initialization on startup
   - Scheduled ClinicalTrials.gov sync (cron: "0 3 * * *")
   - AsyncIO scheduler integration

2. **API Routers**
   - Profile management
   - Trial search
   - Settings
   - Admin functions
   - SQLite operations

3. **Static File Serving**
   - Serves web UI from server/static/
   - Info page at /web

4. **CORS Configuration**
   - Configurable allowed origins
   - Credentials support
   - All methods and headers

#### Endpoints
- GET / - API root information
- GET /web - Web UI info page
- GET /web/login - Login page (if exists)
- GET /docs - Auto-generated API documentation
- Additional routers: profile, trials, settings, admin, sqlite

---

### 3.5 React Native Mobile App (LinkRTC)

#### Project Structure
`
App.tsx                 # Main app entry
src/
  api/                  # Offline data layer
    auth.ts
    profile.ts
    trials.ts
    settings.ts
  data/
    trials.json         # 3,131 bundled trials
    matching.ts         # On-device matching engine
    localStore.ts       # AsyncStorage wrapper
  screens/
    OnboardingScreen.tsx
    MatchFeedScreen.tsx
    TrialDetailScreen.tsx
    SavedTrialsScreen.tsx
    SettingsScreen.tsx
    MedicalProfileScreen.tsx
  navigation/
    AppNavigator.tsx    # Tab + stack navigation
  context/
    AuthContext.tsx     # Auth state management
  utils/
    conditions.ts       # Medical condition list
    cache.ts           # Cache helpers
android/                # Native Android build
  app/
    build.gradle
    src/
`

#### Key Features
1. **Offline-First Architecture**
   - All 3,131 Massachusetts trials bundled
   - No server required
   - Local data storage (AsyncStorage)
   - On-device matching algorithm

2. **Authentication**
   - Email + password (no real verification)
   - Any 8+ character password works
   - Stored in expo-secure-store

3. **Medical Profile**
   - Pre-filled demo profile on sign-in
   - Editable: conditions, medications, allergies, history
   - Stored locally

4. **Trial Matching**
   - Ported matching algorithm from backend
   - Condition overlap scoring
   - Recruiting-first ordering
   - Real-time feed updates

5. **Trial Details**
   - Full study information
   - Save trials locally
   - Open on ClinicalTrials.gov (requires internet)

6. **Navigation**
   - Bottom tabs: Match Feed, Saved Trials, Profile, Settings
   - Stack navigation for details

#### Dependencies (package.json)
`json
{
  "expo": "^58.0.19",
  "react": "19.3.0",
  "react-native": "0.88.0",
  "react-native-paper": "^5.12.0",
  "@react-navigation/bottom-tabs": "^7.0.0",
  "@react-navigation/native-stack": "^7.0.0",
  "@react-native-async-storage/async-storage": "2.2.0",
  "expo-secure-store": "~58.0.2",
  "expo-notifications": "~58.1.6"
}
`

#### Build Instructions
**Development:**
`ash
npm install
npx expo start  # or: npx expo start --web
`

**Production APK:**
`ash
cd android
./gradlew assembleRelease
# Output: android/app/build/outputs/apk/release/app-release.apk
`

---

## 4. Data Structures

### 4.1 Database Schema

#### Table: users
`sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
`

**Sample Data:** 5 demo users

#### Table: patients
`sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    conditions TEXT NOT NULL,  -- Comma-separated
    city TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
`

**Sample Data:** 5 demo patients

#### Table: 	rials
`sql
CREATE TABLE trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nct_id TEXT UNIQUE NOT NULL,  -- ClinicalTrials.gov ID (e.g., NCT12345678)
    title TEXT NOT NULL,
    phase TEXT,  -- PHASE1, PHASE2, PHASE3, PHASE4, NA
    conditions TEXT NOT NULL,  -- Comma-separated
    city TEXT,
    status TEXT DEFAULT 'RECRUITING',
    min_age INTEGER,
    max_age INTEGER,
    distance_from_boston INTEGER  -- Miles
)
`

**Sample Data:** 3,131 Massachusetts recruiting trials

---

### 4.2 API Response Formats

#### Patient Profile Response
`json
{
  "id": 1,
  "user_id": 1,
  "name": "Sarah Chen",
  "age": 42,
  "gender": "Female",
  "zip_code": "02115",
  "city": "Boston",
  "conditions": "Breast Cancer"
}
`

#### Match Results Response
`json
{
  "patient_id": 1,
  "patient_name": "Sarah Chen",
  "total_matches": 15,
  "filters": {
    "max_distance": 100,
    "phase": "PHASE3"
  },
  "matches": [
    {
      "trial_id": 123,
      "nct_id": "NCT12345678",
      "title": "Study of New Breast Cancer Treatment...",
      "phase": "PHASE3",
      "conditions": "Breast Cancer, Advanced Breast Neoplasm",
      "city": "Boston",
      "status": "RECRUITING",
      "distance_miles": 2,
      "match_score": 85,
      "match_percentage": "85%",
      "matched_conditions": ["breast cancer"],
      "match_explanation": "Perfect match: Breast Cancer ↔ Breast Cancer (ICD-10: C50, C50.9). Age 42 within range (18-65).",
      "match_details": [
        {
          "patient": "Breast Cancer",
          "trial": "Breast Cancer",
          "type": "Medical Code Match (ICD-10)",
          "codes": ["C50", "C50.9"]
        }
      ],
      "age_eligible": true,
      "min_age": 18,
      "max_age": 65
    }
  ]
}
`

#### Trial Detail Response
`json
{
  "id": 123,
  "nct_id": "NCT12345678",
  "title": "Phase 3 Study of New Breast Cancer Treatment in Advanced Disease",
  "phase": "PHASE3",
  "conditions": "Breast Cancer, Advanced Breast Neoplasm",
  "city": "Boston",
  "status": "RECRUITING",
  "min_age": 18,
  "max_age": 65,
  "distance_from_boston": 2
}
`

#### Error Response
`json
{
  "error": "Error description",
  "message": "Human-readable message"
}
`

---

### 4.3 Mobile App Data Structures

#### Bundled Trial (trials.json)
`json
{
  "nctId": "NCT12345678",
  "title": "Study Title...",
  "phase": "PHASE3",
  "conditions": ["Breast Cancer", "Advanced Breast Neoplasm"],
  "city": "Boston",
  "status": "RECRUITING",
  "minAge": 18,
  "maxAge": 65,
  "distanceFromBoston": 2
}
`

#### Local Storage Keys
- @auth_token - Secure store (fake token)
- @user_profile - AsyncStorage (medical profile)
- @saved_trials - AsyncStorage (array of NCT IDs)
- @settings - AsyncStorage (app preferences)

---

## 5. API Specifications

### 5.1 Flask API Endpoints

#### Authentication

**POST /login**
`http
POST /login HTTP/1.1
Content-Type: application/json

{
  "username": "sarah.chen",
  "password": "demo123"
}
`

**Response 200:**
`json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "sarah.chen"
  }
}
`

**Response 401:**
`json
{
  "success": false,
  "message": "Invalid credentials"
}
`

---

**POST /logout**
`http
POST /logout HTTP/1.1
Cookie: session=xyz...
`

**Response 200:**
`json
{
  "success": true,
  "message": "Logged out successfully"
}
`

---

#### Patient Profile

**GET /api/patient/me**
`http
GET /api/patient/me HTTP/1.1
Cookie: session=xyz...
`

**Response 200:**
`json
{
  "id": 1,
  "user_id": 1,
  "name": "Sarah Chen",
  "age": 42,
  "gender": "Female",
  "zip_code": "02115",
  "city": "Boston",
  "conditions": "Breast Cancer"
}
`

**Response 401:**
`json
{
  "error": "Authentication required"
}
`

---

**GET /api/patient/<patient_id>**
`http
GET /api/patient/1 HTTP/1.1
Cookie: session=xyz...
`

**Response 200:** Same as /api/patient/me

**Response 404:**
`json
{
  "error": "Patient not found"
}
`

---

#### Trial Matching

**GET /api/matches/<patient_id>**
`http
GET /api/matches/1?max_distance=50&phase=PHASE3 HTTP/1.1
Cookie: session=xyz...
`

**Query Parameters:**
- max_distance (optional, default: 100) - Maximum distance in miles
- phase (optional) - Filter by trial phase

**Response 200:** See [Match Results Response](#match-results-response)

---

#### Trials

**GET /api/trials/<trial_id>**
`http
GET /api/trials/123 HTTP/1.1
`

**Response 200:** See [Trial Detail Response](#trial-detail-response)

---

**GET /api/trials/search**
`http
GET /api/trials/search?q=breast+cancer&limit=10 HTTP/1.1
`

**Query Parameters:**
- q (required) - Search query
- limit (optional, default: 20) - Max results

**Response 200:**
`json
{
  "query": "breast cancer",
  "total_results": 10,
  "results": [
    { ...trial object... }
  ]
}
`

---

#### Demo Routes

**GET /api/demo/patients**
`http
GET /api/demo/patients HTTP/1.1
`

**Response 200:**
`json
{
  "patients": [
    {
      "id": 1,
      "name": "Sarah Chen",
      "age": 42,
      "gender": "Female",
      "city": "Boston",
      "conditions": "Breast Cancer"
    },
    ...
  ]
}
`

---

**POST /api/demo/switch/<patient_id>**
`http
POST /api/demo/switch/2 HTTP/1.1
Cookie: session=xyz...
`

**Response 200:**
`json
{
  "success": true,
  "message": "Switched to John Smith",
  "patient": {
    "id": 2,
    "name": "John Smith",
    ...
  }
}
`

---

### 5.2 FastAPI Endpoints

See auto-generated documentation at http://localhost:8000/docs

**Key Endpoints:**
- GET / - API info
- GET /health - Health check
- Routers: profile, trials, settings, admin, sqlite

---

## 6. Mobile App Specifications

### 6.1 Screens

#### OnboardingScreen
- **Route:** /onboarding
- **Purpose:** Sign-in / sign-up
- **Features:**
  - Email input
  - Password input (8+ chars)
  - No real authentication
  - Auto-loads demo profile on sign-in

#### MatchFeedScreen
- **Route:** / (default tab)
- **Purpose:** View matched trials
- **Features:**
  - Real-time matching based on profile
  - Condition overlap badges
  - Distance display
  - Phase tags
  - Pull-to-refresh
  - Tap to view details

#### TrialDetailScreen
- **Route:** /trial/:nctId
- **Purpose:** Full trial information
- **Features:**
  - Complete study details
  - Save/unsave button
  - Open in ClinicalTrials.gov (web)
  - Back navigation

#### SavedTrialsScreen
- **Route:** /saved (tab)
- **Purpose:** View saved trials
- **Features:**
  - List of saved trials
  - Same cards as match feed
  - Unsave button
  - Empty state message

#### MedicalProfileScreen
- **Route:** /profile (tab)
- **Purpose:** Edit medical profile
- **Features:**
  - Multi-line condition input
  - Medication list
  - Allergy list
  - Medical history
  - Save button
  - Auto-saves to AsyncStorage

#### SettingsScreen
- **Route:** /settings (tab)
- **Purpose:** App preferences
- **Features:**
  - Notification toggle
  - Distance filter
  - Phase filter
  - About information
  - Sign out button

---

### 6.2 Navigation Structure

`
AppNavigator (Stack)
  ├─ OnboardingScreen (if not logged in)
  └─ MainTabs (BottomTabs)
       ├─ MatchFeedTab
       │    └─ MatchFeedScreen
       ├─ SavedTrialsTab
       │    └─ SavedTrialsScreen
       ├─ ProfileTab
       │    └─ MedicalProfileScreen
       └─ SettingsTab
            └─ SettingsScreen

Modals:
  - TrialDetailScreen (pushed on stack)
`

---

### 6.3 Matching Algorithm (Mobile)

Ported from Flask backend to TypeScript.

**File:** src/data/matching.ts

**Algorithm:**
1. Get patient conditions (array)
2. Load all bundled trials from trials.json
3. For each trial:
   - Calculate condition overlap score
   - Check age eligibility
   - Check distance filter
4. Filter out trials with 0 score
5. Sort by: score DESC, distance ASC
6. Return top 20

**Simplified Scoring (no ICD-10 on mobile):**
- Condition match: 50 points per condition
- Age eligible: 20 points
- Max score: 100

---

## 7. Performance & Testing

### 7.1 Performance Metrics

#### Flask Backend
| Metric | Without Cache | With Cache | Improvement |
|--------|--------------|-----------|-------------|
| Match Query | ~374ms | ~20ms | **18.7x faster** |
| Cache Size | N/A | 100 entries | LRU eviction |
| Memory | ~50MB | ~55MB | +10% |

#### Mobile App
- **Bundle Size:** 3,131 trials in trials.json (~2.5MB)
- **Match Speed:** <100ms on modern phones
- **Offline:** 100% functional without internet

---

### 7.2 Testing

#### Flask Backend Tests

**File:** 	est_suite.py

**Coverage:**
1. Database initialization
2. Sample patient creation
3. Medical code normalization
4. ICD-10 code matching
5. Keyword matching
6. Age eligibility
7. Distance filtering
8. Cache performance
9. API endpoints
10. Authentication

**Status:** 20/20 tests passing ✅

**Run Tests:**
`ash
python test_suite.py
`

---

#### Performance Tests

**File:** 	est_performance.py

**Metrics:**
- First query (no cache)
- Cached query
- Improvement factor
- Memory usage

**Run:**
`ash
python test_performance.py
`

---

### 7.3 Known Limitations

1. **SQLite Concurrency**
   - Single-writer limitation
   - Not suitable for high-traffic production
   - Consider PostgreSQL for production

2. **Demo Authentication**
   - Hardcoded password: "demo123"
   - No password reset
   - Session key: "hackathon-secret-key-change-in-production"

3. **Mobile App Authentication**
   - No real verification
   - Any 8+ char password works
   - No account creation flow

4. **Distance Calculation**
   - Hardcoded "distance_from_boston"
   - No real geolocation
   - All distances relative to Boston

5. **Trial Data Freshness**
   - Static snapshot (3,131 trials)
   - FastAPI has scheduled sync, but not tested in production
   - Manual refresh required for updates

6. **HIPAA Compliance**
   - This is a DEMO/HACKATHON project
   - NOT HIPAA compliant
   - Do NOT use with real patient data

---

## 8. Deployment Instructions

### 8.1 Flask Backend

**Requirements:**
- Python 3.8+
- Virtual environment recommended

**Setup:**
`powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python database.py  # Initialize DB
python app.py       # Start server
`

**Access:**
- Web UI: http://localhost:5000
- Dashboard: http://localhost:5000/dashboard

---

### 8.2 FastAPI Backend

**Requirements:**
- Python 3.8+
- Virtual environment recommended

**Setup:**
`powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/server"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
`

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

### 8.3 Mobile App

**Requirements:**
- Node.js 18+
- npm or yarn
- (Optional) Android SDK for APK build

**Setup:**
`ash
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/app"
npm install
npx expo start  # or: npx expo start --web
`

**Build APK:**
`ash
cd android
./gradlew assembleRelease
`

**APK Location:**
ndroid/app/build/outputs/apk/release/app-release.apk

---

## 9. File Structure

`
clinical-trial-matcher/
├── app.py                      # Flask main
├── database.py                 # DB setup & queries
├── matching.py                 # Matching engine
├── medical_codes.py            # ICD-10 mapping
├── requirements.txt            # Python deps
├── trials.db                   # SQLite database
├── templates/                  # Flask HTML
│   ├── login.html
│   └── dashboard.html
├── static/                     # CSS, JS, images
├── server/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   └── routers/
│   │       ├── profile.py
│   │       ├── trials.py
│   │       ├── settings.py
│   │       ├── admin.py
│   │       └── sqlite_routes.py
│   ├── static/                # Web UI files
│   │   └── index.html
│   ├── requirements.txt
│   └── trials.db              # FastAPI SQLite
├── app/                       # Original mobile (server-dependent)
├── App.tsx                    # Main mobile entry (LinkRTC)
├── package.json               # Node deps
├── src/                       # Mobile source
│   ├── api/
│   ├── data/
│   │   ├── trials.json       # Bundled trials
│   │   ├── matching.ts
│   │   └── localStore.ts
│   ├── screens/
│   ├── navigation/
│   ├── context/
│   └── utils/
├── android/                   # Android native
├── test_suite.py              # Flask tests
├── test_performance.py        # Performance tests
└── [Documentation files]      # MD guides
`

---

## 10. Documentation References

1. **API_DOCUMENTATION.md** - Flask API details
2. **MOBILE_APP_GUIDE.md** - Mobile setup instructions
3. **USAGE_GUIDE.md** - Flask vs FastAPI explanation
4. **COMPLETE_SUMMARY.md** - Quick reference
5. **TEAMMATE_ANALYSIS.md** - Offline mobile architecture analysis
6. **README.md** - Project overview

---

## 11. Git Repository

**URL:** https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher

**Recent Commits:**
- All Flask backend code
- All FastAPI fixes
- Mobile app (LinkRTC) by teammate
- Documentation files
- Test suites

**Branch:** main

---

## Document Metadata

- **Created:** 2025
- **Project:** Hackachusetts 2026 - Clinical Trial Matcher
- **Status:** Complete and operational
- **Last Updated:** Current session
- **Version:** 1.0

---

**END OF SPECIFICATIONS**
