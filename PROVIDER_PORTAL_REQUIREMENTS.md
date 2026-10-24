# Hospital Provider Portal - Requirements Specification

## Document Information
- **Project:** Clinical Trial Matcher - Hospital Provider Portal
- **Type:** Feature Addition / MVP
- **Approach:** Requirements-First
- **Target:** Flask Web Application Integration
- **Status:** Specification Phase

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals & Objectives](#goals--objectives)
4. [User Stories](#user-stories)
5. [Functional Requirements](#functional-requirements)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [Technical Requirements](#technical-requirements)
8. [Data Requirements](#data-requirements)
9. [Security & Compliance](#security--compliance)
10. [Integration Requirements](#integration-requirements)
11. [Success Criteria](#success-criteria)
12. [Out of Scope](#out-of-scope)

---

## 1. Executive Summary

### Overview
The Hospital Provider Portal is a new web-based interface that enables healthcare providers (doctors, nurses, clinical coordinators) to search for patients, view matched clinical trials, and send trial referrals directly to patients' mobile app via QR codes.

### Business Value
- **Streamlines Referral Process:** Providers can instantly send trial information to patients
- **Reduces Manual Work:** Eliminates paper-based or email referrals
- **Improves Patient Engagement:** Patients receive referrals directly in their mobile app
- **Demonstrates Clinical Workflow:** Shows complete provider-to-patient trial matching flow

### Target Users
1. **Primary:** Hospital physicians and clinical staff
2. **Secondary:** Clinical trial coordinators
3. **Tertiary:** Hospital administrators (view-only)

### MVP Scope
This specification defines the **Minimum Viable Product** for the hackathon demo:
- Provider authentication
- Patient search by name/ID
- View patient's matched trials
- Generate QR code referrals
- Basic audit logging
- Integration with existing Flask web UI

---

## 2. Problem Statement

### Current Situation
The Clinical Trial Matcher currently has:
- ✅ Patient-facing web dashboard
- ✅ Patient mobile app (offline)
- ✅ Trial matching engine
- ❌ **Missing:** Provider interface to send referrals to patients

### Problems to Solve
1. **Manual Referral Process:** Doctors must manually tell patients about trials or print information
2. **No Patient Search:** Providers cannot look up patient profiles or matched trials
3. **No Digital Handoff:** No way to send trial information from hospital to patient's mobile app
4. **Limited Workflow Demo:** Current system only shows patient-initiated search

### User Pain Points
- **Doctors:** "I want to quickly recommend a trial to my patient during their visit"
- **Clinical Coordinators:** "I need to search for eligible patients for a specific trial"
- **Patients:** "I want to receive trial recommendations from my doctor without writing things down"

---

## 3. Goals & Objectives

### Primary Goals
1. **Enable Provider-Initiated Referrals:** Providers can proactively send trial recommendations to patients
2. **Seamless Patient Discovery:** Providers can search and view patient profiles
3. **Mobile App Integration:** Referrals appear in patient's mobile app
4. **Demo-Ready Workflow:** Complete end-to-end flow for hackathon presentation

### Success Metrics
- Providers can send a referral in < 30 seconds
- QR code successfully delivers referral to mobile app
- Audit log captures all provider actions
- Zero HIPAA violations in demo environment

### MVP Constraints
- **Time:** Hackathon deadline
- **Technology:** Must use Flask (matches existing web stack)
- **Database:** SQLite (sufficient for demo)
- **Deployment:** Local development only
- **Scale:** 5-10 demo providers, 5 demo patients

---

## 4. User Stories

### Epic 1: Provider Authentication
**As a** healthcare provider  
**I want to** log into a secure provider portal  
**So that** I can access patient data and send referrals

**Acceptance Criteria:**
- Providers can log in with email and password
- Different provider roles: Doctor, Nurse, Coordinator, Admin
- Session management with timeout
- Logout functionality

---

### Epic 2: Patient Search
**As a** provider  
**I want to** search for patients by name or ID  
**So that** I can find the right patient quickly

**Acceptance Criteria:**
- Search by patient name (partial match)
- Search by patient ID (exact match)
- Search results show: name, age, gender, city, conditions
- Click on result to view full patient profile
- Handles no results gracefully

---

### Epic 3: View Patient Matches
**As a** provider  
**I want to** see which trials match my patient's conditions  
**So that** I can determine which trial to recommend

**Acceptance Criteria:**
- View patient's demographic information
- View patient's medical conditions
- View list of matched trials (using existing matching engine)
- See match scores and explanations
- See trial details: phase, location, distance, eligibility

---

### Epic 4: Send Trial Referral via QR Code
**As a** provider  
**I want to** generate a QR code for a specific trial referral  
**So that** my patient can scan it with their mobile app

**Acceptance Criteria:**
- Select a trial to refer
- Add optional provider notes (e.g., "I think this is a good fit because...")
- Generate unique QR code
- QR code displays on screen
- QR code can be printed (browser print)
- Referral is saved in database with unique code

---

### Epic 5: Patient Receives Referral (Mobile)
**As a** patient  
**I want to** scan a QR code from my doctor  
**So that** I can see the recommended trial in my app

**Acceptance Criteria:**
- Mobile app has "Scan Referral" feature
- Scanning QR code decodes referral data
- Referral appears in app with doctor's name and notes
- Referral is saved to "Referred Trials" section
- Patient can view trial details
- Patient can mark referral as viewed/accepted/declined

---

### Epic 6: Audit Logging
**As a** hospital administrator  
**I want to** see a log of all provider actions  
**So that** I can ensure compliance and track usage

**Acceptance Criteria:**
- Log provider login/logout
- Log patient searches
- Log patient profile views
- Log referral generation
- Logs include: timestamp, provider ID, action, patient ID, IP address
- Admin can view audit logs (read-only)

---

### Epic 7: Provider Dashboard
**As a** provider  
**I want to** see an overview of my recent activity  
**So that** I can track my referrals

**Acceptance Criteria:**
- Dashboard shows: total referrals sent (today/week/all-time)
- List of recent referrals with status
- Quick search bar
- Navigation to all features

---

## 5. Functional Requirements

### FR1: Authentication & Authorization

#### FR1.1: Provider Login
- **Input:** Email, password
- **Process:** Verify credentials against providers table
- **Output:** Session token, redirect to dashboard
- **Error Handling:** Invalid credentials, account disabled

#### FR1.2: Provider Roles
| Role | Permissions |
|------|-------------|
| **Doctor** | Search patients, view matches, send referrals |
| **Nurse** | Search patients, view matches, send referrals |
| **Coordinator** | Search patients, view matches, send referrals, view all referrals |
| **Admin** | View-only access, view audit logs, manage providers |

#### FR1.3: Session Management
- Session timeout: 30 minutes of inactivity
- Re-authentication required after timeout
- "Remember me" option (optional, low priority)

#### FR1.4: Logout
- Clear session
- Redirect to login page
- Log audit event

---

### FR2: Patient Search

#### FR2.1: Search Interface
- **Input:** Text field (patient name or ID)
- **Search Types:**
  - By name: Partial, case-insensitive match
  - By ID: Exact match
- **Output:** List of matching patients

#### FR2.2: Search Results
- Display: Name, Age, Gender, City, Primary Conditions
- Pagination: 10 results per page (if > 10)
- Sort: By name (ascending), by age (descending)
- Click to view full profile

#### FR2.3: No Results Handling
- Message: "No patients found matching '[query]'"
- Suggestion: "Try searching by full name or patient ID"

---

### FR3: Patient Profile View

#### FR3.1: Patient Information Display
- **Demographics:**
  - Name
  - Age
  - Gender
  - City, Zip Code
- **Medical Information:**
  - Conditions (comma-separated list)
  - (Optional) Medications, allergies - not in MVP

#### FR3.2: Matched Trials Display
- Use existing matching engine (matching.py)
- Display top 10 matches (configurable)
- For each match:
  - Trial title
  - NCT ID
  - Phase
  - Match score (percentage)
  - Distance from patient
  - Eligibility summary
  - "Send Referral" button

#### FR3.3: Trial Details Modal
- Click on trial title to expand
- Shows full trial information (from 	rials table)
- Conditions, age eligibility, location, status

---

### FR4: Referral Generation

#### FR4.1: Referral Creation
- **Trigger:** Provider clicks "Send Referral" button on a trial
- **Input Form:**
  - Trial (pre-selected)
  - Patient (pre-selected)
  - Provider notes (optional, max 500 chars)
  - Urgency (optional): Normal, High
- **Process:**
  1. Generate unique referral code (e.g., REF-20250130-A8K2)
  2. Insert into eferrals table
  3. Log audit event
  4. Generate QR code

#### FR4.2: QR Code Generation
- **Library:** qrcode[pil] (Python)
- **Data Encoded in QR:**
  `json
  {
    "type": "trial_referral",
    "referral_code": "REF-20250130-A8K2",
    "trial_nct_id": "NCT12345678",
    "provider_name": "Dr. Jane Smith",
    "hospital": "Massachusetts General Hospital",
    "timestamp": "2025-01-30T14:23:00Z"
  }
  `
- **QR Code Display:**
  - On-screen image
  - Download button (saves as PNG)
  - Print button (browser print)
  - "Copy link" button (deep link for remote sending)

#### FR4.3: Referral Status Tracking
- **Statuses:**
  - sent - QR code generated, not yet scanned
  - iewed - Patient opened referral in app
  - ccepted - Patient saved trial to their list
  - declined - Patient dismissed referral
  - expired - 30 days passed (optional)

#### FR4.4: Deep Links (Optional for MVP)
- Generate shareable link: linkrtc://referral?code=REF-20250130-A8K2
- Allows remote sending via email/SMS

---

### FR5: Provider Dashboard

#### FR5.1: Dashboard Overview
- **Top Stats:**
  - Referrals sent today
  - Referrals sent this week
  - Total referrals all-time
  - Active patients searched (today)
- **Quick Actions:**
  - Search Patients (prominent search bar)
  - View All Referrals
  - View Audit Log (admin only)

#### FR5.2: Recent Referrals List
- Last 10 referrals sent by this provider
- Columns: Date, Patient Name, Trial (short title), Status
- Click to view referral details
- Filter by status

---

### FR6: Audit Logging

#### FR6.1: Events to Log
| Event | Data Captured |
|-------|---------------|
| Provider login | Provider ID, email, timestamp, IP, success/failure |
| Provider logout | Provider ID, timestamp |
| Patient search | Provider ID, search query, result count, timestamp |
| Patient profile view | Provider ID, patient ID, timestamp, IP |
| Referral created | Provider ID, patient ID, trial ID, referral code, timestamp |
| Referral viewed (by patient) | Referral code, timestamp |

#### FR6.2: Audit Log Viewing (Admin Only)
- Table view with filters
- Filter by: Provider, date range, event type
- Export to CSV (optional)
- No edit/delete capability (append-only log)

---

### FR7: Mobile App Integration

#### FR7.1: QR Code Scanning (Mobile Side)
- New feature: "Scan Referral" button on mobile home screen
- Uses device camera to scan QR code
- Decodes JSON payload
- Validates referral code via API call (or offline validation)

#### FR7.2: Referral Display in Mobile App
- New screen: "Referrals" or "Doctor Recommendations"
- List of scanned referrals
- Shows: Provider name, hospital, trial title, provider notes, date
- Badge for unread referrals

#### FR7.3: Referral Actions (Mobile)
- **View Trial Details:** Opens full trial detail screen
- **Save to My Trials:** Adds to saved trials list
- **Decline:** Removes from list
- **Status Update:** Sends status back to server (if online)

---

## 6. Non-Functional Requirements

### NFR1: Performance
- **Page Load Time:** < 2 seconds
- **Search Results:** < 500ms
- **QR Code Generation:** < 1 second
- **Matching Engine:** Use existing cache (< 50ms for cached results)

### NFR2: Usability
- **Intuitive UI:** Medical professionals with basic computer skills can use without training
- **Mobile-Friendly:** Responsive design (providers may use tablets)
- **Accessibility:** Basic WCAG 2.1 Level A compliance

### NFR3: Reliability
- **Uptime:** Not critical for MVP (local demo)
- **Data Integrity:** All referrals must be saved successfully
- **Error Handling:** Graceful degradation, user-friendly error messages

### NFR4: Scalability (Future)
- **MVP:** 10 concurrent providers, 100 referrals/day
- **Production:** Design allows easy migration to PostgreSQL, Redis caching

### NFR5: Security
- **Password Hashing:** Use werkzeug.security (same as patient auth)
- **Session Management:** Secure, HTTP-only cookies
- **SQL Injection:** Parameterized queries only
- **XSS Protection:** Escape all user inputs

### NFR6: Maintainability
- **Code Quality:** Follow Flask best practices
- **Documentation:** Inline comments, README for setup
- **Testing:** Unit tests for core functions (time permitting)

---

## 7. Technical Requirements

### TR1: Technology Stack

#### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite (	rials.db)
- **Authentication:** Flask sessions + werkzeug password hashing
- **QR Code:** qrcode[pil] library

#### Frontend
- **Template Engine:** Jinja2 (Flask templates)
- **CSS Framework:** Bootstrap 5 or Tailwind CSS (match existing UI)
- **JavaScript:** Vanilla JS or jQuery (lightweight)
- **Icons:** Font Awesome or Material Icons

#### Mobile Integration
- **QR Scanning:** React Native Camera or expo-barcode-scanner
- **Deep Links:** Expo Linking API

---

### TR2: New Flask Routes

#### Provider Portal Routes
`python
# Authentication
GET  /provider              # Login page
POST /provider/login        # Login endpoint
POST /provider/logout       # Logout endpoint

# Dashboard
GET  /provider/dashboard    # Provider dashboard

# Patient Search
GET  /provider/search       # Search page
GET  /provider/api/search   # Search API (AJAX)

# Patient Profile
GET  /provider/patient/<id> # Patient profile + matches

# Referrals
POST /provider/referral/create        # Create referral
GET  /provider/referral/<code>        # View referral details
GET  /provider/referral/<code>/qr     # Get QR code image
GET  /provider/referrals              # List all referrals

# Audit Log
GET  /provider/audit                  # Audit log (admin only)

# API for Mobile App
GET  /api/referral/<code>             # Get referral data (mobile)
POST /api/referral/<code>/status      # Update referral status (mobile)
`

---

### TR3: Database Schema Changes

#### New Table: providers
`sql
CREATE TABLE providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    npi TEXT,  -- National Provider Identifier
    hospital_name TEXT,
    specialty TEXT,
    role TEXT NOT NULL,  -- 'doctor', 'nurse', 'coordinator', 'admin'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
`

#### New Table: eferrals
`sql
CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_code TEXT UNIQUE NOT NULL,
    provider_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    trial_id INTEGER NOT NULL,
    status TEXT DEFAULT 'sent',  -- 'sent', 'viewed', 'accepted', 'declined', 'expired'
    provider_notes TEXT,
    urgency TEXT DEFAULT 'normal',  -- 'normal', 'high'
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewed_at TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers (id),
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (trial_id) REFERENCES trials (id)
)
`

#### New Table: provider_audit_log
`sql
CREATE TABLE provider_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER,
    action TEXT NOT NULL,  -- 'login', 'logout', 'search', 'view_patient', 'create_referral'
    patient_id INTEGER,
    referral_id INTEGER,
    search_query TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers (id),
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (referral_id) REFERENCES referrals (id)
)
`

---

### TR4: Sample Data (Seed Script)

#### Demo Providers
`python
providers_seed = [
    {
        'email': 'dr.smith@mgh.harvard.edu',
        'password': 'provider123',
        'name': 'Dr. Jane Smith',
        'npi': '1234567890',
        'hospital_name': 'Massachusetts General Hospital',
        'specialty': 'Oncology',
        'role': 'doctor'
    },
    {
        'email': 'nurse.johnson@bwh.harvard.edu',
        'password': 'provider123',
        'name': 'Nurse Robert Johnson',
        'npi': '0987654321',
        'hospital_name': 'Brigham and Women\\'s Hospital',
        'specialty': 'General',
        'role': 'nurse'
    },
    {
        'email': 'coordinator@bostonmedical.org',
        'password': 'provider123',
        'name': 'Lisa Chen',
        'npi': None,
        'hospital_name': 'Boston Medical Center',
        'specialty': 'Clinical Trials',
        'role': 'coordinator'
    },
    {
        'email': 'admin@hospital.org',
        'password': 'provider123',
        'name': 'Admin User',
        'npi': None,
        'hospital_name': 'Demo Hospital',
        'specialty': None,
        'role': 'admin'
    }
]
`

---

### TR5: QR Code Implementation

#### Python Code (Backend)
`python
import qrcode
import json
import io
import base64
from datetime import datetime

def generate_referral_qr(referral):
    """
    Generate QR code for a referral
    Returns: base64-encoded PNG image
    """
    # Prepare data
    qr_data = {
        'type': 'trial_referral',
        'referral_code': referral['referral_code'],
        'trial_nct_id': referral['trial_nct_id'],
        'provider_name': referral['provider_name'],
        'hospital': referral['hospital_name'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color='black', back_color='white')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str
`

#### TypeScript Code (Mobile)
`	ypescript
// src/api/referrals.ts
export async function scanReferral(qrData: string) {
  const data = JSON.parse(qrData);
  
  if (data.type !== 'trial_referral') {
    throw new Error('Invalid QR code');
  }
  
  // Validate referral code
  const referral = await fetchReferralData(data.referral_code);
  
  // Save to local storage
  await saveReferralLocally(referral);
  
  // Update status (if online)
  try {
    await updateReferralStatus(data.referral_code, 'viewed');
  } catch (e) {
    // Offline - will sync later
  }
  
  return referral;
}
`

---

### TR6: Mobile App Changes

#### New Files to Create
1. src/screens/ReferralsScreen.tsx - List of received referrals
2. src/screens/ScanReferralScreen.tsx - QR code scanner
3. src/api/referrals.ts - Referral API calls
4. src/components/ReferralCard.tsx - Referral list item

#### Modified Files
1. src/navigation/AppNavigator.tsx - Add referrals tab
2. src/data/localStore.ts - Add referral storage
3. App.tsx - Add deep link handling

#### New Dependencies
`json
{
  "expo-barcode-scanner": "~12.0.0",
  "expo-camera": "~13.0.0"
}
`

---

## 8. Data Requirements

### DR1: Provider Data
- **Minimum:** 4 demo providers (1 per role)
- **Fields:** See providers table schema
- **Passwords:** All use "provider123" for demo

### DR2: Referral Data
- **Sample:** 5-10 pre-generated referrals for demo
- **Variety:** Different patients, trials, statuses

### DR3: Audit Log Data
- **Sample:** 20-30 sample log entries
- **Purpose:** Demonstrate audit functionality

---

## 9. Security & Compliance

### SEC1: HIPAA Considerations
⚠️ **THIS IS A DEMO PROJECT - NOT HIPAA COMPLIANT**

If deployed in a real healthcare setting, would require:
- Encryption at rest and in transit (HTTPS)
- Access controls and role-based permissions
- Audit logging (✅ included in MVP)
- Business Associate Agreements (BAA)
- Data minimization
- Patient consent for data sharing

### SEC2: Authentication Security
- Passwords hashed with werkzeug (bcrypt-equivalent)
- Session cookies: HTTP-only, Secure flag (in production)
- Session timeout: 30 minutes
- No password reset in MVP (demo only)

### SEC3: Authorization
- Role-based access control (RBAC)
- Providers can only see patients (no patient-specific restrictions in MVP)
- Admins can see audit logs
- No patient can access provider portal

### SEC4: Data Protection
- SQL injection prevention: Parameterized queries only
- XSS prevention: Jinja2 auto-escaping
- CSRF protection: Flask-WTF (optional for MVP)
- Input validation on all forms

### SEC5: Audit Trail
- All provider actions logged
- Logs are append-only (no deletion)
- Includes IP address and timestamp
- Admin can review logs

---

## 10. Integration Requirements

### INT1: Existing Flask App Integration
- New provider routes live alongside existing patient routes
- Shared database (	rials.db)
- Shared matching engine (matching.py)
- Separate authentication (providers vs patients)

### INT2: Mobile App Integration
- Mobile app scans QR codes
- Mobile app calls /api/referral/<code> endpoint
- Mobile app updates referral status
- Works offline (referral data cached locally)

### INT3: URL Structure
`
Patient Portal:
  /                     # Patient login
  /dashboard            # Patient dashboard
  /api/patient/*        # Patient API

Provider Portal:
  /provider             # Provider login
  /provider/dashboard   # Provider dashboard
  /provider/api/*       # Provider API

Shared:
  /api/referral/*       # Referral API (used by mobile)
  /api/trials/*         # Trial data (used by both)
`

---

## 11. Success Criteria

### Functional Success
- ✅ Provider can log in
- ✅ Provider can search for patient by name
- ✅ Provider can view patient's matched trials
- ✅ Provider can generate QR code referral
- ✅ Patient can scan QR code in mobile app
- ✅ Referral appears in mobile app with provider details
- ✅ Referral status updates (sent → viewed → accepted)
- ✅ Audit log captures all actions

### Demo Success
- Complete workflow takes < 2 minutes to demonstrate
- UI is professional and intuitive
- QR code scanning works reliably
- No errors or crashes during demo

### Technical Success
- All new routes return correct HTTP status codes
- Database migrations run successfully
- QR code generation works on first try
- Mobile app integration works offline

---

## 12. Out of Scope (Not in MVP)

### Features NOT Included
❌ Two-factor authentication (2FA)  
❌ Password reset flow  
❌ Provider registration (self-service)  
❌ Email/SMS notifications  
❌ Push notifications for referrals  
❌ Patient-provider messaging  
❌ Appointment scheduling  
❌ Integration with EHR systems  
❌ Real-time collaboration (multiple providers)  
❌ Analytics dashboard  
❌ Export referrals to PDF  
❌ Bulk referrals (multiple patients)  
❌ Trial recruitment metrics  
❌ Payment/billing integration  
❌ FHIR API integration  
❌ Internationalization (i18n)  
❌ Dark mode  

### Future Enhancements
These could be added post-MVP:
1. Email/SMS referral delivery (alternative to QR)
2. Provider-to-provider referrals
3. Patient consent management
4. Trial enrollment status tracking
5. Integration with hospital EHR
6. Advanced search filters (by condition, age range, etc.)
7. Referral analytics and reports
8. Mobile app for providers (native iOS/Android)

---

## 13. Risks & Mitigations

### Risk 1: QR Code Scanning Fails
**Likelihood:** Medium  
**Impact:** High (breaks core workflow)  
**Mitigation:**
- Test QR scanning on multiple devices
- Provide alternative: Manual referral code entry
- Use high-quality QR code library
- Include deep link fallback

### Risk 2: SQLite Concurrency Issues
**Likelihood:** Low (MVP)  
**Impact:** Medium  
**Mitigation:**
- Limit concurrent users in demo
- Use write-ahead logging (WAL) mode
- Plan migration to PostgreSQL for production

### Risk 3: Mobile App Offline Sync Issues
**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:**
- Design for offline-first
- Queue status updates for later sync
- Show offline indicator in UI

### Risk 4: Time Constraint (Hackathon Deadline)
**Likelihood:** High  
**Impact:** High  
**Mitigation:**
- Focus on core workflow first
- Deprioritize nice-to-have features
- Use existing Flask templates/styles
- Leverage existing matching engine

---

## 14. Development Plan Overview

### Phase 1: Database & Backend (Day 1)
- Create database schema
- Seed demo providers
- Implement provider authentication
- Build patient search endpoint

### Phase 2: Provider Portal UI (Day 1-2)
- Provider login page
- Provider dashboard
- Patient search page
- Patient profile view

### Phase 3: Referral System (Day 2)
- Referral creation endpoint
- QR code generation
- Referral display page
- Audit logging

### Phase 4: Mobile Integration (Day 2-3)
- Add QR scanner to mobile app
- Add referrals screen
- Test end-to-end workflow

### Phase 5: Testing & Polish (Day 3)
- End-to-end testing
- Bug fixes
- UI polish
- Demo script preparation

---

## 15. Acceptance Testing Scenarios

### Scenario 1: Provider Login
1. Open /provider in browser
2. Enter email: dr.smith@mgh.harvard.edu
3. Enter password: provider123
4. Click "Login"
5. **Expected:** Redirected to /provider/dashboard

### Scenario 2: Search Patient
1. On provider dashboard, enter "Sarah" in search bar
2. Click "Search"
3. **Expected:** Results show "Sarah Chen" with age 42, conditions "Breast Cancer"
4. Click on "Sarah Chen"
5. **Expected:** View patient profile with matched trials

### Scenario 3: Send Referral
1. On Sarah Chen's profile, see matched trials
2. Click "Send Referral" on top match
3. Enter provider notes: "This Phase 3 trial looks promising for you"
4. Click "Generate QR Code"
5. **Expected:** QR code appears on screen
6. **Expected:** Referral saved in database with status "sent"

### Scenario 4: Scan QR Code (Mobile)
1. Open LinkRTC mobile app
2. Tap "Scan Referral" button
3. Point camera at QR code
4. **Expected:** App scans code successfully
5. **Expected:** Referral appears in "Referrals" tab
6. **Expected:** Shows provider name, trial title, provider notes

### Scenario 5: View Audit Log (Admin)
1. Log in as admin user
2. Navigate to "Audit Log"
3. **Expected:** See table of all logged events
4. Filter by provider: "Dr. Jane Smith"
5. **Expected:** See only Dr. Smith's actions

---

## 16. UI/UX Guidelines

### Design Principles
1. **Consistency:** Match existing patient portal design
2. **Clarity:** Medical terminology but user-friendly
3. **Efficiency:** Minimize clicks to complete tasks
4. **Feedback:** Clear success/error messages

### Color Scheme (Match Existing)
- Primary: Blue (#0066cc)
- Success: Green (#28a745)
- Warning: Orange (#ffc107)
- Danger: Red (#dc3545)

### Typography
- Headers: 18-24px, bold
- Body: 14-16px, regular
- Labels: 12-14px, medium

### Key UI Components
- Search bar: Prominent, top of dashboard
- Patient cards: Avatar + name + key info
- Trial cards: Compact, match score badge
- QR code: Large (300x300px), centered, with instructions

---

## Document Metadata

- **Created:** January 30, 2025
- **Last Updated:** January 30, 2025
- **Version:** 1.0 (MVP Requirements)
- **Status:** Ready for Design & Implementation
- **Next Steps:** Create design specification and task breakdown

---

**END OF REQUIREMENTS SPECIFICATION**
