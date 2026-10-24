# Specification Documents Summary

## Overview
This folder contains comprehensive specifications for the Clinical Trial Matcher project, including current system documentation and new feature requirements for the Hospital Provider Portal.

---

## Documents Created

### 1. **CURRENT_SYSTEM_SPECS.md** (27.7 KB)
Complete breakdown of ALL existing system components.

**Contents:**
- ✅ System Overview & Architecture
- ✅ Flask Web Server Specifications (app.py, matching.py, medical_codes.py)
- ✅ FastAPI Backend Specifications (server/)
- ✅ React Native Mobile App Specifications (LinkRTC)
- ✅ Database Schema (SQLite - 4 tables, 3,131 trials)
- ✅ API Endpoint Documentation
- ✅ Matching Engine Algorithm (ICD-10 + keyword matching)
- ✅ Medical Code Intelligence (60+ conditions mapped)
- ✅ Performance Metrics (18.7x cache improvement)
- ✅ Testing & Deployment Instructions
- ✅ File Structure & Dependencies

**Use this document to:**
- Understand what currently exists
- Reference existing APIs and data structures
- See how components integrate
- Find file locations and code patterns

---

### 2. **PROVIDER_PORTAL_REQUIREMENTS.md** (28.3 KB)
Complete requirements specification for the NEW Hospital Provider Portal feature.

**Contents:**
- ✅ Executive Summary & Problem Statement
- ✅ Goals & Objectives
- ✅ 7 User Epics with Acceptance Criteria
- ✅ Functional Requirements (FR1-FR7)
- ✅ Non-Functional Requirements (Performance, Security, Usability)
- ✅ Technical Requirements (Flask routes, database schema, QR codes)
- ✅ Database Schema Changes (3 new tables)
- ✅ Mobile App Integration Details
- ✅ Security & Compliance (HIPAA considerations)
- ✅ Success Criteria & Acceptance Tests
- ✅ Out of Scope Items
- ✅ Risk Analysis & Mitigations
- ✅ Development Phase Plan
- ✅ UI/UX Guidelines

**Use this document to:**
- Understand what needs to be built
- See all feature requirements
- Reference database changes needed
- Plan implementation tasks
- Test against acceptance criteria

---

## System Architecture Overview

### Current System (3 Components)
`
┌─────────────────────┐
│  Flask Web UI       │  ← Patients use this
│  Port 5000          │
└─────────────────────┘

┌─────────────────────┐
│  FastAPI Server     │  ← Mobile app connects here
│  Port 8000          │
└─────────────────────┘

┌─────────────────────┐
│  Mobile App         │  ← Patients use this (offline)
│  LinkRTC (Expo)     │
└─────────────────────┘
`

### After Provider Portal (4 Components)
`
┌─────────────────────┐
│  Flask Web UI       │  ← Patients
│  Port 5000          │
└─────────────────────┘

┌─────────────────────┐
│  PROVIDER PORTAL    │  ← NEW: Doctors/Providers ⭐
│  Flask /provider/*  │
└─────────┬───────────┘
          │
          │ (sends referrals via QR codes)
          │
          v
┌─────────────────────┐
│  Mobile App         │  ← Patients scan QR codes
│  + Referral Scanner │  ← NEW: Scan feature ⭐
└─────────────────────┘

┌─────────────────────┐
│  FastAPI Server     │  ← API for mobile
│  Port 8000          │
└─────────────────────┘
`

---

## Key Features Being Added

### 1. Provider Authentication
- New login portal for hospital staff
- Role-based access (Doctor, Nurse, Coordinator, Admin)
- Separate from patient authentication

### 2. Patient Search
- Search by name or ID
- View patient demographics and conditions
- See matched clinical trials

### 3. QR Code Referrals
- Provider selects a trial for a patient
- Generates unique QR code
- Patient scans with mobile app
- Referral appears in app with provider notes

### 4. Audit Logging
- Track all provider actions
- Compliance and security
- Admin can review logs

### 5. Mobile App Integration
- New "Scan Referral" feature
- New "Referrals" screen
- Offline support

---

## Database Changes

### New Tables (3)
1. **providers** - Provider accounts (doctors, nurses, etc.)
2. **referrals** - Trial referrals sent by providers
3. **provider_audit_log** - Audit trail of all actions

### Existing Tables (4)
1. **users** - Patient accounts
2. **patients** - Patient profiles
3. **trials** - 3,131 clinical trials
4. **sqlite_sequence** - SQLite internal

---

## Technology Stack

### Backend (No Changes)
- **Python 3.x**
- **Flask** (web framework)
- **SQLite** (database)
- **Werkzeug** (password hashing)

### New Dependencies
- **qrcode[pil]** - QR code generation

### Frontend (Minimal Changes)
- **Jinja2** templates
- **Bootstrap or Tailwind** (match existing UI)
- **Vanilla JavaScript** (for AJAX search)

### Mobile (Small Changes)
- **React Native / Expo**
- **expo-barcode-scanner** - NEW
- **expo-camera** - NEW

---

## Demo Workflow

### Complete Provider-to-Patient Flow
1. **Provider logs in** to /provider portal
2. **Provider searches** for patient "Sarah Chen"
3. **Provider views** Sarah's matched trials (existing matching engine)
4. **Provider selects** top match and clicks "Send Referral"
5. **Provider adds notes**: "This trial looks promising for you"
6. **System generates** unique QR code
7. **Provider shows QR** to patient (in-person) or prints it
8. **Patient opens** LinkRTC mobile app
9. **Patient taps** "Scan Referral"
10. **Patient scans** QR code with camera
11. **Referral appears** in app with trial details + provider notes
12. **Patient can** view trial, save it, or decline
13. **Status updates** back to provider portal (viewed/accepted/declined)

**Total time:** < 2 minutes 🚀

---

## Next Steps

### Option A: Start Implementation Immediately
Use the requirements document to begin coding:
1. Create database schema
2. Build provider authentication
3. Build patient search
4. Build QR code generation
5. Integrate with mobile app

### Option B: Create Design Specification First
Create detailed design document covering:
- UI mockups/wireframes
- API endpoint details
- Component architecture
- State management
- Error handling flows

### Recommendation
For an MVP, you can proceed directly to implementation using the requirements document. The requirements are detailed enough to guide development.

---

## Files to Reference

### For Backend Work
- pp.py - Flask main (add provider routes here)
- database.py - Database functions (add provider queries)
- matching.py - Matching engine (no changes needed)
- 	emplates/ - HTML templates (create provider pages)

### For Mobile Work
- App.tsx - Main entry point
- src/screens/ - Add ReferralsScreen, ScanReferralScreen
- src/api/ - Add referrals.ts
- src/navigation/ - Add referrals tab

### For Testing
- 	est_suite.py - Add provider tests
- 	est_performance.py - Test QR code generation speed

---

## Quick Start Commands

### Run Flask (Current System)
\\\ash
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
.\venv\Scripts\activate
python app.py
\\\

### Run Mobile App
\\\ash
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
npx expo start --web
\\\

### Initialize Database (After Adding Provider Tables)
\\\ash
python database.py  # Will need to add provider setup
\\\

---

## Documentation Standards

Both specification documents follow these standards:
- ✅ Markdown format
- ✅ Table of contents
- ✅ Numbered sections
- ✅ Code examples
- ✅ Acceptance criteria
- ✅ Technical details
- ✅ Security considerations
- ✅ Risk analysis

---

## Questions & Clarifications

If you need clarification on any requirement or specification:
1. Check CURRENT_SYSTEM_SPECS.md for "how it works now"
2. Check PROVIDER_PORTAL_REQUIREMENTS.md for "what to build"
3. Compare both to see integration points

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 30, 2025 | Initial specifications created |

---

## Document Metadata

- **Project:** Clinical Trial Matcher - Hospital Provider Portal
- **Type:** Specification Summary
- **Status:** Complete - Ready for Implementation
- **Target:** Hackathon MVP

---

**Ready to build! 🚀**
