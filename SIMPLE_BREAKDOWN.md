# Clinical Trial Matcher - Simple Breakdown

## 🎯 What Is This Project?

A system that helps patients find clinical trials that match their medical conditions. It has **3 parts**:

1. **Patient Website** (for patients at home)
2. **Mobile App** (for patients on the go)
3. **Provider Portal** (for doctors - TO BE BUILT)

---

## 📱 **PART 1: Mobile App (LinkRTC)**

### What It Does
Patients can find clinical trials on their phone **without needing internet**.

### Key Features
✅ **Works Offline** - All 3,131 trials stored on the phone  
✅ **Sign In** - Any email + 8+ character password (no real account needed)  
✅ **Pre-filled Demo Profile** - Opens with example medical conditions  
✅ **Edit Your Profile**
   - Add your medical conditions (diabetes, cancer, etc.)
   - Add medications
   - Add allergies
   - Add medical history

✅ **Match Feed** - See trials that match YOUR conditions  
✅ **Match Scores** - Shows how well each trial matches (0-100%)  
✅ **Save Trials** - Bookmark trials you're interested in  
✅ **Trial Details** - Full information about each study  
✅ **Open in Browser** - Link to official ClinicalTrials.gov page

### Technology
- React Native (works on Android & iOS)
- Expo framework
- TypeScript
- All data stored locally on phone

### How to Run It
\\\ash
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
npx expo start --web
\\\
Opens at: http://localhost:19006

---

## 💻 **PART 2: Patient Website (Flask Web Dashboard)**

### What It Does
Patients can find clinical trials in their web browser.

### Key Features
✅ **Login Page** - 5 demo patient accounts  
✅ **Patient Dashboard** - See your profile and matched trials  
✅ **Smart Matching** - Uses medical codes (ICD-10) to find better matches
   - Breast Cancer → Matches "Breast Neoplasm", "Mammary Cancer", etc.
   - Diabetes → Matches "Type 2 Diabetes Mellitus", "T2DM", etc.

✅ **Match Scores** - Shows WHY each trial matched
   - "Perfect match: Breast Cancer ↔ Breast Cancer (ICD-10: C50)"
   - "Age 42 within range (18-65)"
   - Match percentage: 85%

✅ **Filters**
   - Distance: Within 50 or 100 miles
   - Phase: Phase 1, 2, 3, or 4 trials

✅ **Switch Demo Patients** - Try different medical profiles  
✅ **Trial Search** - Search by keyword  
✅ **Trial Details** - Full study information

### Smart Features
🧠 **Medical Intelligence**
   - 60+ conditions mapped to ICD-10 medical codes
   - Recognizes synonyms (e.g., "heart attack" = "myocardial infarction")
   - Keyword matching for complex conditions

⚡ **Super Fast**
   - First search: ~374ms
   - Cached search: ~20ms
   - **18.7x faster** with caching!

### Demo Accounts
| Username | Password | Patient Info |
|----------|----------|--------------|
| sarah.chen | demo123 | 42F, Breast Cancer |
| john.smith | demo123 | 55M, Diabetes, Hypertension |
| maria.garcia | demo123 | 68F, COPD, Heart Disease |
| david.lee | demo123 | 34M, Depression, Anxiety |
| emily.brown | demo123 | 45F, Multiple Sclerosis |

### Technology
- Python Flask
- SQLite database
- Jinja2 templates
- Bootstrap CSS

### How to Run It
\\\ash
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
.\venv\Scripts\activate
python app.py
\\\
Opens at: http://localhost:5000

---

## 🏥 **PART 3: Provider Portal (TO BE BUILT)**

### What It Will Do
Doctors can search for patients and send trial recommendations directly to their mobile app.

### Planned Features
✅ **Doctor Login** - Separate portal for healthcare providers  
✅ **Patient Search** - Find patients by name or ID  
✅ **View Patient Matches** - See which trials match each patient  
✅ **Send Referral via QR Code**
   1. Doctor selects a trial for a patient
   2. Adds notes: "I think this trial is good for you"
   3. Generates a QR code
   4. Patient scans QR with their phone
   5. Trial recommendation appears in their app!

✅ **Audit Log** - Track all doctor actions (for security)  
✅ **Dashboard** - See referrals sent today/this week

### Demo Doctors (Planned)
- Dr. Jane Smith (Oncologist, Mass General Hospital)
- Nurse Robert Johnson (Brigham and Women's Hospital)
- Lisa Chen (Clinical Trial Coordinator)
- Admin User (View-only access)

### Status
📝 **Fully specified** - Requirements document ready  
🚧 **Not built yet** - Ready to implement

---

## 🗄️ **Database: What's Stored**

### Current Tables (4)
1. **users** - Patient accounts (5 demo users)
2. **patients** - Patient medical profiles (5 profiles)
3. **trials** - Clinical trials data (**3,131 Massachusetts trials**)
4. **sqlite_sequence** - Database internal table

### Trial Information Includes
- NCT ID (official ClinicalTrials.gov ID)
- Title
- Phase (1, 2, 3, 4, or N/A)
- Conditions treated
- City/Location
- Status (Recruiting, Not Recruiting, etc.)
- Age eligibility (min/max age)
- Distance from Boston

### Coming Soon (3 new tables)
5. **providers** - Doctor/nurse accounts
6. **referrals** - Trial referrals sent by doctors
7. **provider_audit_log** - Security audit trail

---

## 🎬 **How It Works (Complete Flow)**

### Current Flow (Patient-Initiated)
\\\
1. Patient logs into website or opens mobile app
2. Patient enters medical conditions
3. System searches 3,131 trials
4. Smart matching finds best matches using medical codes
5. Patient sees ranked list with scores
6. Patient reads trial details
7. Patient saves interesting trials
\\\

### Future Flow (Doctor-Initiated) - TO BE BUILT
\\\
1. Doctor logs into provider portal
2. Doctor searches for patient "Sarah Chen"
3. Doctor views Sarah's matched trials
4. Doctor selects best trial
5. Doctor adds note: "This looks promising for you"
6. Doctor generates QR code
7. Patient scans QR with mobile app
8. Trial appears in patient's app with doctor's recommendation
9. Patient can accept, save, or decline
\\\

**Total time: Under 2 minutes!**

---

## 🧠 **Smart Matching Algorithm**

### How It Scores Matches (0-100 points)

**Step 1: Medical Code Matching**
- Perfect ICD-10 code match: **+50 points**
  - Example: Patient has "Breast Cancer" (ICD-10: C50)
  - Trial needs "Breast Neoplasm" (ICD-10: C50)
  - ✅ MATCH! +50 points

**Step 2: Keyword Matching**
- Keyword overlap: **+30 points per keyword**
  - Example: Patient has "heart attack"
  - Trial needs "myocardial infarction"
  - Both have keyword "cardiac"
  - ✅ MATCH! +30 points

**Step 3: Age Eligibility**
- Patient age within trial's range: **+20 points**
  - Example: Patient is 42 years old
  - Trial accepts ages 18-65
  - ✅ MATCH! +20 points

**Maximum Score: 100 points (capped)**

### Example Match Explanation
\\\
Patient: Sarah Chen, 42F, Breast Cancer
Trial: Phase 3 Breast Cancer Treatment Study

Match Score: 85%

Breakdown:
✓ Perfect match: Breast Cancer ↔ Breast Cancer (ICD-10: C50, C50.9) [+50 pts]
✓ Age 42 within range (18-65) [+20 pts]
✓ Distance: 2 miles from Boston [+15 pts]

Total: 85 points = 85% match
\\\

---

## 📊 **Statistics**

### Current System
- **3,131** Massachusetts clinical trials
- **60+** medical conditions with ICD-10 codes
- **5** demo patient profiles
- **4** database tables
- **18.7x** performance improvement with caching
- **20/20** tests passing ✅

### Geographic Coverage
- All trials within 100 miles of Boston
- Cities included: Boston, Cambridge, Worcester, Springfield, and more

### Condition Categories Covered
1. Cancer/Oncology (9 types)
2. Cardiovascular (5 conditions)
3. Diabetes & Metabolic (2 conditions)
4. Respiratory (2 conditions)
5. Neurological (5 conditions)
6. Mental Health (5 conditions)
7. Autoimmune (3 conditions)
8. Infectious (2 conditions)

---

## 🚀 **Quick Start Guide**

### To Run Patient Website
\\\ash
# Activate Python environment
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
.\venv\Scripts\activate

# Start Flask server
python app.py

# Open browser to:
http://localhost:5000

# Login with:
Username: sarah.chen
Password: demo123
\\\

### To Run Mobile App (in Browser)
\\\ash
# Start Expo
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
npx expo start --web

# Opens automatically at:
http://localhost:19006

# Sign in with:
Any email + any 8+ character password
\\\

### To View Database
\\\ash
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
python verify_data.py
\\\

---

## 📁 **File Structure (Simplified)**

\\\
clinical-trial-matcher/
│
├── 🌐 WEBSITE (Flask)
│   ├── app.py                    # Main website server
│   ├── database.py               # Database functions
│   ├── matching.py               # Smart matching algorithm
│   ├── medical_codes.py          # ICD-10 code mappings
│   ├── templates/                # HTML pages
│   │   ├── login.html
│   │   └── dashboard.html
│   └── static/                   # CSS, images
│
├── 📱 MOBILE APP
│   ├── App.tsx                   # Mobile app entry point
│   ├── src/
│   │   ├── screens/              # App screens
│   │   │   ├── MatchFeedScreen
│   │   │   ├── TrialDetailScreen
│   │   │   └── SavedTrialsScreen
│   │   ├── data/
│   │   │   ├── trials.json       # 3,131 bundled trials
│   │   │   └── matching.ts       # Mobile matching engine
│   │   └── navigation/           # App navigation
│   └── android/                  # Android build files
│
├── 🗄️ DATABASE
│   └── trials.db                 # SQLite database (3,131 trials)
│
├── 📋 SPECS (NEW!)
│   ├── CURRENT_SYSTEM_SPECS.md           # What exists now
│   ├── PROVIDER_PORTAL_REQUIREMENTS.md   # What to build next
│   └── SPECIFICATIONS_README.md          # Quick reference
│
└── 🧪 TESTS
    ├── test_suite.py             # 20 unit tests
    └── test_performance.py       # Speed tests
\\\

---

## 🎓 **Technology Stack Summary**

### Backend
- **Language:** Python 3.x
- **Web Framework:** Flask
- **Database:** SQLite
- **Password Security:** Werkzeug (bcrypt)

### Frontend (Website)
- **Templates:** Jinja2
- **CSS:** Bootstrap
- **JavaScript:** Vanilla JS

### Mobile App
- **Framework:** React Native
- **Build System:** Expo SDK 58
- **Language:** TypeScript
- **Storage:** AsyncStorage (local)

### External Data Source
- **ClinicalTrials.gov** API (Massachusetts recruiting trials)

---

## ✨ **What Makes This Special**

### 🧠 Medical Intelligence
Not just simple keyword matching - uses official ICD-10 medical codes to understand that:
- "Breast Cancer" = "Breast Neoplasm" = "Mammary Cancer"
- "Diabetes" = "Diabetes Mellitus" = "T2DM"
- "Heart Attack" = "Myocardial Infarction" = "MI"

### ⚡ Lightning Fast
- Caching makes repeated searches **18.7x faster**
- First search: 374ms
- Cached search: 20ms

### 📴 Works Offline
Mobile app has all 3,131 trials built-in. No internet required!

### 🔒 Security
- Passwords hashed (not stored in plain text)
- Session management
- Audit logging (coming in provider portal)

### 🎯 Real Data
All 3,131 trials are real studies from ClinicalTrials.gov:
- Real NCT IDs
- Real trial phases
- Real locations
- Real eligibility criteria

---

## 🎯 **Next Steps**

### ✅ Already Done
- Patient website (Flask) - COMPLETE
- Mobile app (React Native) - COMPLETE
- Smart matching engine - COMPLETE
- Medical code intelligence - COMPLETE
- 3,131 trials loaded - COMPLETE
- Full specifications written - COMPLETE

### 🚧 To Be Built
- Provider portal (doctor login, patient search, QR referrals)
- Mobile app QR scanner
- Audit logging system

### 📝 Ready When You Are
All specifications are written and ready in:
- **PROVIDER_PORTAL_REQUIREMENTS.md** - Everything you need to build it

---

## 🎬 **Demo Script (30 seconds)**

\\\
"Meet Sarah, a 42-year-old breast cancer patient.

[Open website, login as sarah.chen]

She logs into our platform and sees 15 trials that match her condition.

[Show match feed with scores]

Our system uses medical intelligence - it knows 'breast cancer' matches 
'breast neoplasm' and 'mammary cancer' using ICD-10 codes.

[Click on top match]

She can see why each trial matched - this one is 85% because it's for 
breast cancer, she meets the age requirement, and it's only 2 miles away.

[Switch to mobile app]

She can also use our mobile app - completely offline! All 3,131 trials 
are stored on her phone.

[COMING SOON: Show doctor scanning QR code]

Soon, her doctor will be able to send trial recommendations directly to 
her app by generating a QR code she scans with her phone."
\\\

---

## 📞 **Documentation Files**

- **README.md** - Project overview
- **API_DOCUMENTATION.md** - API endpoints
- **MOBILE_APP_GUIDE.md** - Mobile setup
- **CURRENT_SYSTEM_SPECS.md** - Technical details (27KB)
- **PROVIDER_PORTAL_REQUIREMENTS.md** - Provider portal specs (28KB)
- **SPECIFICATIONS_README.md** - Quick reference

---

**Questions? Check the full specifications in the 📋 SPECS folder!**

---

*Document created: January 30, 2025*  
*Project: Hackachusetts 2026 - Clinical Trial Matcher*  
*Status: Patient system complete, Provider portal ready to build*
