# Provider Portal Quick MVP - Complete Spec

## requirements.md

### Feature: Hospital Provider Portal (Quick MVP)

Minimal provider portal enabling doctors to search patients and send trial referrals via QR codes.

#### User Flow
1. Doctor logs in at /provider
2. Doctor searches for patient by name
3. Doctor views patient's matched trials  
4. Doctor clicks "Send Referral" on a trial
5. QR code is generated and displayed
6. Patient can scan QR with mobile app (future integration)

#### Core Requirements
- R1: Provider authentication (login/logout)
- R2: Patient search by name
- R3: Display patient profile with matched trials (reuse existing matching engine)
- R4: Generate QR code referrals with unique codes
- R5: Store referrals in database
- R6: Display QR codes for printing/scanning

#### Out of Scope (Quick MVP)
- Audit logging (full version)
- Dashboard statistics
- Referral status tracking
- Referral history
- Role-based access control
- Mobile app QR scanner integration (separate phase)

---

## design.md

### Architecture

#### Database Schema
**New Tables (2):**

\\\sql
-- Providers (doctors/nurses)
CREATE TABLE providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    hospital_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Referrals (QR code referrals)
CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_code TEXT UNIQUE NOT NULL,          -- Format: REF-20250130-A8K2
    provider_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    trial_id INTEGER NOT NULL,
    provider_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers (id),
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (trial_id) REFERENCES trials (id)
);
\\\

**Seed Data:**
- 2 demo providers: Dr. Jane Smith, Dr. Robert Jones
- Password: provider123 (hashed)

#### Routes

\\\python
# Provider Portal Routes
GET  /provider                      # Login page
POST /provider/login                # Authenticate provider
POST /provider/logout               # End session
GET  /provider/search               # Search page (main page, requires auth)
GET  /provider/patient/<int:id>     # Patient profile + matched trials
POST /provider/referral/create      # Create referral + generate QR
GET  /provider/referral/<code>      # Display QR code
\\\

#### Session Management
- Patient sessions: user_id, username
- Provider sessions: provider_id, provider_name, provider_email
- Separate authentication paths (no interference)

#### QR Code Data Format
\\\json
{
  "type": "trial_referral",
  "referral_code": "REF-20250130-A8K2",
  "trial_nct_id": "NCT12345678",
  "provider_name": "Dr. Jane Smith",
  "hospital": "Massachusetts General Hospital",
  "timestamp": "2025-01-30T14:23:00Z"
}
\\\

### UI Design

**Page Flow:**
1. Login → 2. Search → 3. Patient Profile → 4. QR Code

**Styling:** Minimal Bootstrap (match existing patient portal)

---

## tasks.md

### Implementation Tasks

#### Task 1: Database Setup
**Description:** Add provider tables and seed data to database.py

**Subtasks:**
- 1.1: Add init_provider_tables() function
- 1.2: Add create_demo_providers() function  
- 1.3: Add provider query functions: get_provider_by_email(), search_patients(), get_patient_by_id(), create_referral(), get_referral_by_code()
- 1.4: Update __main__ to call provider init functions
- 1.5: Run python database.py to create tables

**Acceptance Criteria:**
- ✅ providers table created
- ✅ eferrals table created
- ✅ 2 demo providers seeded
- ✅ Can query: SELECT * FROM providers;

---

#### Task 2: Install QR Code Library
**Description:** Add qrcode dependency

**Subtasks:**
- 2.1: Add qrcode[pil] to requirements.txt
- 2.2: Run pip install qrcode[pil]

**Acceptance Criteria:**
- ✅ import qrcode works without error

---

#### Task 3: Provider Authentication
**Description:** Add provider login/logout routes to app.py

**Subtasks:**
- 3.1: Add provider_login_required decorator
- 3.2: Add GET /provider route (login page)
- 3.3: Add POST /provider/login route (authenticate)
- 3.4: Add POST /provider/logout route
- 3.5: Create 	emplates/provider_login.html

**Acceptance Criteria:**
- ✅ Can access /provider and see login form
- ✅ Can login with dr.smith@hospital.org / provider123
- ✅ Session stores provider_id
- ✅ Logout clears session

---

#### Task 4: Patient Search
**Description:** Add patient search functionality

**Subtasks:**
- 4.1: Add GET /provider/search route (requires auth)
- 4.2: Add search logic (calls database.search_patients())
- 4.3: Create 	emplates/provider_search.html
- 4.4: Add search form + results list

**Acceptance Criteria:**
- ✅ Search page shows after login
- ✅ Can search "Sarah" and find Sarah Chen
- ✅ Can search "John" and find John Smith
- ✅ Results show: name, age, gender, conditions

---

#### Task 5: Patient Profile View
**Description:** Display patient info and matched trials

**Subtasks:**
- 5.1: Add GET /provider/patient/<int:patient_id> route
- 5.2: Get patient from database
- 5.3: Call matching.get_matches(patient) to get trials
- 5.4: Create 	emplates/provider_patient.html
- 5.5: Display patient info + trial cards with "Send Referral" buttons

**Acceptance Criteria:**
- ✅ Clicking patient in search opens their profile
- ✅ Patient demographics displayed
- ✅ Matched trials shown with scores
- ✅ Each trial has "Send Referral" button

---

#### Task 6: QR Code Generation
**Description:** Generate and display QR code referrals

**Subtasks:**
- 6.1: Add POST /provider/referral/create route
  - Generate unique code: REF-{date}-{random}
  - Save to database
  - Redirect to QR display
- 6.2: Add GET /provider/referral/<code> route
  - Get referral from database
  - Generate QR code (base64 image)
  - Render template
- 6.3: Create 	emplates/provider_referral.html
- 6.4: Display QR code with patient/trial info

**Acceptance Criteria:**
- ✅ Clicking "Send Referral" creates referral in database
- ✅ QR code displays on screen
- ✅ QR code encodes JSON with referral data
- ✅ Can query: SELECT * FROM referrals ORDER BY id DESC LIMIT 1;

---

#### Task 7: End-to-End Testing
**Description:** Test complete workflow

**Test Cases:**
- TC1: Login as Dr. Smith
- TC2: Search for "Sarah Chen"
- TC3: View Sarah's profile and matches
- TC4: Create referral for top trial
- TC5: Verify QR code displays
- TC6: Verify referral in database
- TC7: Logout and verify session cleared

**Acceptance Criteria:**
- ✅ All test cases pass
- ✅ No errors in console
- ✅ Complete flow takes < 2 minutes

---

## Estimated Time

| Task | Time |
|------|------|
| 1. Database | 15 min |
| 2. QR Library | 2 min |
| 3. Authentication | 20 min |
| 4. Search | 15 min |
| 5. Patient Profile | 20 min |
| 6. QR Generation | 25 min |
| 7. Testing | 10 min |
| **Total** | **~1.8 hours** |

---

## Demo Credentials

**Providers:**
- Email: dr.smith@hospital.org / Password: provider123
- Email: dr.jones@hospital.org / Password: provider123

**Patients (existing):**
- sarah.chen / demo123
- john.smith / demo123
- (etc.)

---

**Status:** Ready for task execution
