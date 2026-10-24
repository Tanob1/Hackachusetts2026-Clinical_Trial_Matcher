# Provider Portal - Quick MVP Requirements

## 🎯 Goal
Build a minimal viable provider portal in the shortest time possible. Core workflow only.

---

## ✅ MVP Scope (What We're Building)

### Core Features Only
1. ✅ Provider login (2 demo accounts)
2. ✅ Patient search by name
3. ✅ View patient profile + matched trials
4. ✅ Generate QR code referral (one-click)
5. ✅ Simple referral display page

### ❌ NOT in Quick MVP
- ❌ Provider registration
- ❌ Audit logging (just basic console logs)
- ❌ Dashboard with stats
- ❌ Referral status tracking
- ❌ Admin features
- ❌ Complex role-based access
- ❌ Referral history list

---

## 📋 User Stories (Simplified)

### Story 1: Provider Login
**As a** doctor  
**I want to** log in quickly  
**So that** I can access the portal

**Acceptance:**
- Login page at /provider
- Email + password
- 2 demo accounts work
- Redirect to search page

### Story 2: Patient Search
**As a** doctor  
**I want to** search for my patient  
**So that** I can find their profile

**Acceptance:**
- Search bar on main page
- Type patient name (partial match)
- Click result to view profile

### Story 3: View Matches
**As a** doctor  
**I want to** see which trials match my patient  
**So that** I can choose what to recommend

**Acceptance:**
- Patient info displayed
- List of matched trials (use existing matching engine)
- "Send Referral" button on each trial

### Story 4: Generate QR Referral
**As a** doctor  
**I want to** generate a QR code  
**So that** my patient can scan it

**Acceptance:**
- Click "Send Referral"
- Optional notes field (simple)
- QR code appears immediately
- Can print or download

---

## 🗄️ Database (Minimal)

### New Tables (2 only)

#### Table 1: providers
\\\sql
CREATE TABLE providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    hospital_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
\\\

#### Table 2: referrals
\\\sql
CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_code TEXT UNIQUE NOT NULL,
    provider_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    trial_id INTEGER NOT NULL,
    provider_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers (id),
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (trial_id) REFERENCES trials (id)
)
\\\

**No audit log table for quick MVP**

---

## 🛣️ Routes (Minimal)

### Provider Routes (5 only)
\\\python
GET  /provider                    # Login page
POST /provider/login              # Login handler
POST /provider/logout             # Logout handler
GET  /provider/search             # Search page (main page after login)
GET  /provider/patient/<id>       # Patient profile + matches
POST /provider/referral/create    # Create referral + generate QR
GET  /provider/referral/<code>    # View QR code
\\\

---

## 🎨 UI (Simple)

### Page 1: Login (/provider)
\\\
┌─────────────────────────────────┐
│  🏥 Provider Portal Login       │
│                                 │
│  Email:    [____________]       │
│  Password: [____________]       │
│                                 │
│  [Login Button]                 │
└─────────────────────────────────┘
\\\

### Page 2: Search (/provider/search)
\\\
┌─────────────────────────────────┐
│  Provider Portal - Dr. Smith    │
│  [Logout]                       │
│                                 │
│  Search Patient:                │
│  [Search: ___________] [Go]     │
│                                 │
│  Results:                       │
│  ┌────────────────────────┐    │
│  │ Sarah Chen, 42F        │    │
│  │ Breast Cancer          │    │
│  └────────────────────────┘    │
│  ┌────────────────────────┐    │
│  │ John Smith, 55M        │    │
│  │ Diabetes, Hypertension │    │
│  └────────────────────────┘    │
└─────────────────────────────────┘
\\\

### Page 3: Patient Profile (/provider/patient/1)
\\\
┌─────────────────────────────────┐
│  Sarah Chen, 42F                │
│  Boston, MA 02115               │
│  Conditions: Breast Cancer      │
│                                 │
│  Matched Trials:                │
│  ┌────────────────────────┐    │
│  │ Phase 3 Breast Cancer  │    │
│  │ Match: 85%             │    │
│  │ Distance: 2 miles      │    │
│  │ [Send Referral]        │    │
│  └────────────────────────┘    │
│  ┌────────────────────────┐    │
│  │ Phase 2 Breast Study   │    │
│  │ Match: 75%             │    │
│  │ Distance: 5 miles      │    │
│  │ [Send Referral]        │    │
│  └────────────────────────┘    │
└─────────────────────────────────┘
\\\

### Page 4: QR Code (/provider/referral/REF-XXX)
\\\
┌─────────────────────────────────┐
│  Referral Created!              │
│                                 │
│  Patient: Sarah Chen            │
│  Trial: Phase 3 Breast Cancer   │
│                                 │
│  ┌───────────────────┐         │
│  │                   │         │
│  │   [QR CODE HERE]  │         │
│  │                   │         │
│  └───────────────────┘         │
│                                 │
│  Patient can scan this with     │
│  the mobile app                 │
│                                 │
│  [Print] [Download] [Back]      │
└─────────────────────────────────┘
\\\

---

## 🔧 Implementation Plan

### Phase 1: Database Setup (10 min)
1. Add create_providers_tables() to database.py
2. Create seed data for 2 providers
3. Run setup script

### Phase 2: Provider Auth (15 min)
1. Add provider login route
2. Add provider session management
3. Create login template (copy patient login, modify)

### Phase 3: Patient Search (15 min)
1. Add search route
2. Add search template
3. Query patients by name (partial match)

### Phase 4: Patient Profile (15 min)
1. Add patient profile route
2. Use existing matching.py to get matches
3. Create profile template with trial cards

### Phase 5: QR Code Generation (20 min)
1. Install qrcode library: pip install qrcode[pil]
2. Add referral creation route
3. Generate unique referral code
4. Create QR code image
5. Display QR code template

### Phase 6: Testing (10 min)
1. Test login flow
2. Test search
3. Test QR generation
4. End-to-end workflow

**Total Time: ~85 minutes**

---

## 👥 Demo Data

### Providers (2)
\\\python
providers_seed = [
    {
        'email': 'dr.smith@hospital.org',
        'password': 'provider123',
        'name': 'Dr. Jane Smith',
        'hospital_name': 'Massachusetts General Hospital'
    },
    {
        'email': 'dr.jones@hospital.org',
        'password': 'provider123',
        'name': 'Dr. Robert Jones',
        'hospital_name': 'Brigham and Women\\'s Hospital'
    }
]
\\\

### Existing Patients (Already Have 5)
- Sarah Chen (Breast Cancer)
- John Smith (Diabetes, Hypertension)
- Maria Garcia (COPD, Heart Disease)
- David Lee (Depression, Anxiety)
- Emily Brown (Multiple Sclerosis)

---

## 🎯 Success Criteria

### Must Work
✅ Provider logs in with demo credentials  
✅ Provider searches "Sarah" and finds Sarah Chen  
✅ Provider clicks Sarah Chen and sees her matches  
✅ Provider clicks "Send Referral" on top trial  
✅ QR code appears on screen  
✅ Referral is saved in database

### Nice to Have (Skip if Tight on Time)
⏭️ Provider notes field  
⏭️ Download QR as image  
⏭️ Referral history  
⏭️ Pretty CSS styling

---

## 📦 Dependencies

### New Python Package
\\\ash
pip install qrcode[pil]
\\\

### Existing (Already Installed)
- flask
- werkzeug
- sqlite3

---

## 🔒 Security (Simplified for MVP)

### What We're Doing
✅ Password hashing (werkzeug)  
✅ Session-based auth  
✅ Separate provider sessions from patient sessions

### What We're Skipping (For Speed)
⏭️ CSRF protection  
⏭️ Rate limiting  
⏭️ Audit logging  
⏭️ Password complexity requirements

---

## 📝 File Changes

### Files to Modify
1. **database.py** - Add provider functions
2. **app.py** - Add provider routes

### Files to Create
3. **templates/provider_login.html**
4. **templates/provider_search.html**
5. **templates/provider_patient.html**
6. **templates/provider_referral.html**

### Files Unchanged
- matching.py ✅ (reuse as-is)
- medical_codes.py ✅ (reuse as-is)
- Patient routes ✅ (no changes)

---

## 🧪 Testing Checklist

### Manual Test Flow
\\\
1. Open http://localhost:5000/provider
2. Login: dr.smith@hospital.org / provider123
3. Search: "Sarah"
4. Click "Sarah Chen"
5. See matched trials with scores
6. Click "Send Referral" on first trial
7. See QR code
8. Verify referral in database:
   SELECT * FROM referrals ORDER BY id DESC LIMIT 1;
\\\

---

## 🚀 Quick Start (After Implementation)

\\\ash
# Install new dependency
pip install qrcode[pil]

# Initialize database (adds provider tables)
python database.py

# Run server
python app.py

# Open provider portal
http://localhost:5000/provider

# Login
Email: dr.smith@hospital.org
Password: provider123
\\\

---

## 📊 What We're Cutting for Speed

| Feature | Full Version | Quick MVP |
|---------|-------------|-----------|
| Providers | 4 with roles | 2 without roles |
| Audit log | Full table | Just console.log |
| Dashboard | Stats + charts | Just search |
| Referral status | Track status | Just create |
| Referral list | View all | None |
| Provider notes | Rich text | Simple text field |
| QR options | Download/print/link | Just display |
| UI polish | Bootstrap styled | Minimal CSS |

---

## ⏱️ Time Estimate

- **Database:** 10 minutes
- **Auth:** 15 minutes
- **Search:** 15 minutes
- **Patient View:** 15 minutes
- **QR Generation:** 20 minutes
- **Testing:** 10 minutes

**Total: ~85 minutes (1.5 hours)**

---

## 🎬 Demo Script (30 seconds)

\\\
"Now let's see the provider side.

[Open /provider, login as Dr. Smith]

Dr. Smith logs into the provider portal.

[Search for 'Sarah']

She searches for her patient Sarah Chen.

[Click Sarah Chen]

She can see all of Sarah's matched trials with scores.

[Click 'Send Referral' on top trial]

She clicks 'Send Referral' on the best match.

[QR code appears]

A QR code is instantly generated. Sarah can scan this 
with her phone and the trial recommendation appears 
in her mobile app with the doctor's information.

Complete workflow in under 30 seconds!"
\\\

---

## Document Info

- **Type:** Quick MVP Requirements
- **Scope:** Core features only
- **Time:** ~1.5 hours to implement
- **Complexity:** Low (reuses existing code)
- **Status:** Ready to implement

---

**Next Step: Begin implementation with database setup**
