# Clinical Trial Matcher - API Documentation

**Base URL**: http://localhost:5000  
**Version**: 1.0  
**Last Updated**: 2026-10-24

## Overview

REST API for the Clinical Trial Patient Matching System. Enables patient authentication, profile management, and clinical trial matching based on medical conditions.

---

## Authentication

All authenticated endpoints require a session cookie. Use the /login endpoint to authenticate.

### Login
**POST** /login

Authenticate user and create session.

**Request Body**:
```json
{
  "username": "sarah.chen",
  "password": "demo123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "sarah.chen"
  }
}
```

**Error Response** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

---

### Logout
**POST** /logout

End user session.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Patient Profile

### Get Current Patient Profile
**GET** /api/patient/me

Get the logged-in patient's profile information.

**Headers**:
- Requires authenticated session

**Response** (200 OK):
```json
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
```

**Error Response** (401 Unauthorized):
```json
{
  "error": "Authentication required"
}
```

---

### Get Patient by ID
**GET** /api/patient/<patient_id>

Get a specific patient's profile (admin or self only).

**Response** (200 OK):
```json
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
```

---

## Trial Matching

### Get Matched Trials
**GET** /api/matches/<patient_id>

Get matched clinical trials for a patient with optional filters.

**Query Parameters**:
- max_distance (optional): Maximum distance in miles (default: 100)
  - Values: 10, 25, 50, 100
- phase (optional): Filter by trial phase
  - Values: PHASE1, PHASE2, PHASE3, PHASE4, EARLY_PHASE1, NA

**Example Request**:
```
GET /api/matches/1?max_distance=25&phase=PHASE3
```

**Response** (200 OK):
```json
{
  "patient_id": 1,
  "patient_name": "Sarah Chen",
  "total_matches": 18,
  "filters": {
    "max_distance": 25,
    "phase": "PHASE3"
  },
  "matches": [
    {
      "trial_id": 42,
      "nct_id": "NCT12345678",
      "title": "Study of Drug X for Advanced Breast Cancer",
      "phase": "PHASE3",
      "conditions": "Breast Cancer, Advanced Breast Cancer",
      "city": "Boston",
      "status": "RECRUITING",
      "distance_miles": 0,
      "match_score": 90,
      "match_percentage": "90%",
      "matched_conditions": ["breast cancer"],
      "match_explanation": "Matched on primary condition: Breast Cancer. Age 42 is within trial range (18-75).",
      "age_eligible": true,
      "min_age": 18,
      "max_age": 75
    },
    {
      "trial_id": 87,
      "nct_id": "NCT87654321",
      "title": "Phase 3 Trial of Immunotherapy for Breast Cancer",
      "phase": "PHASE3",
      "conditions": "Breast Neoplasms, Carcinoma, Ductal, Breast",
      "city": "Cambridge",
      "status": "RECRUITING",
      "distance_miles": 3,
      "match_score": 60,
      "match_percentage": "60%",
      "matched_conditions": ["breast"],
      "match_explanation": "Partial match on condition keywords. Age 42 is within trial range (21-70).",
      "age_eligible": true,
      "min_age": 21,
      "max_age": 70
    }
  ]
}
```

**Response Fields**:
- match_score: 0-100 score based on condition overlap and age eligibility
- matched_conditions: Array of condition keywords that matched
- match_explanation: Human-readable explanation of why the trial matched
- ge_eligible: Boolean indicating if patient's age falls within trial range

---

## Trial Information

### Get Trial Details
**GET** /api/trials/<trial_id>

Get detailed information about a specific clinical trial.

**Response** (200 OK):
```json
{
  "id": 42,
  "nct_id": "NCT12345678",
  "title": "Study of Drug X for Advanced Breast Cancer",
  "phase": "PHASE3",
  "conditions": "Breast Cancer, Advanced Breast Cancer",
  "city": "Boston",
  "status": "RECRUITING",
  "min_age": 18,
  "max_age": 75,
  "distance_from_boston": 0
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Trial not found"
}
```

---

### Search Trials
**GET** /api/trials/search

Search for trials by keyword.

**Query Parameters**:
- q (required): Search query
- limit (optional): Maximum results (default: 20)

**Example Request**:
```
GET /api/trials/search?q=diabetes&limit=10
```

**Response** (200 OK):
```json
{
  "query": "diabetes",
  "total_results": 87,
  "results": [
    {
      "id": 123,
      "nct_id": "NCT11112222",
      "title": "Study of Insulin Therapy for Type 2 Diabetes",
      "phase": "PHASE3",
      "conditions": "Diabetes Mellitus Type 2",
      "city": "Boston",
      "distance_from_boston": 0
    }
  ]
}
```

---

## Demo Endpoints

### Get All Sample Patients
**GET** /api/demo/patients

Get all sample patients for demo/testing purposes.

**Response** (200 OK):
```json
{
  "patients": [
    {
      "id": 1,
      "name": "Sarah Chen",
      "age": 42,
      "conditions": "Breast Cancer",
      "city": "Boston"
    },
    {
      "id": 2,
      "name": "John Smith",
      "age": 55,
      "conditions": "Diabetes, Hypertension",
      "city": "Cambridge"
    }
  ]
}
```

---

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request**:
```json
{
  "error": "Invalid request parameters",
  "details": "max_distance must be one of: 10, 25, 50, 100"
}
```

**401 Unauthorized**:
```json
{
  "error": "Authentication required"
}
```

**404 Not Found**:
```json
{
  "error": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Sample Patients (for testing)

All sample patients use password: demo123

1. **sarah.chen** - Age 42, Female, Boston - "Breast Cancer"
2. **john.smith** - Age 55, Male, Cambridge - "Diabetes, Hypertension"
3. **maria.garcia** - Age 68, Female, Worcester - "COPD, Heart Disease"
4. **david.lee** - Age 34, Male, Springfield - "Depression, Anxiety"
5. **emily.brown** - Age 45, Female, Boston - "Multiple Sclerosis"

---

## Matching Algorithm Details

**Match Score Calculation**:
- **Condition Overlap** (30 points each): Each matching condition keyword adds 30 points
- **Age Eligibility** (20 points): Bonus if patient's age falls within trial's age range
- **Maximum Score**: 100 points

**Ranking**: Results are sorted by match score (descending)

**Example**:
- Patient with "Diabetes, Hypertension" searching trials
- Trial condition: "Diabetes Mellitus Type 2, Hypertension"
- Overlap: "diabetes" + "hypertension" = 60 points
- Patient age 55, trial range 18-75 = +20 points
- **Total: 80/100 (80% match)**

---

## CORS Headers

For mobile/web app development, the API includes CORS headers:
- Access-Control-Allow-Origin: * (development only)
- Access-Control-Allow-Methods: GET, POST, OPTIONS
- Access-Control-Allow-Headers: Content-Type

---

## Rate Limiting

Currently no rate limiting in MVP. Production should implement:
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user

---

## Future Endpoints (Post-Hackathon)

Planned but not yet implemented:
- POST /api/patient/profile - Update patient profile
- POST /api/matches/<trial_id>/save - Save trial to favorites
- GET /api/matches/saved - Get saved trials
- POST /api/trials/<trial_id>/contact - Contact trial coordinator
- GET /api/stats - System statistics

---

## Mobile App Quick Start

1. **Authentication Flow**:
   ```javascript
   // Login
   const response = await fetch('http://localhost:5000/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     credentials: 'include', // Important for session cookies
     body: JSON.stringify({ username: 'sarah.chen', password: 'demo123' })
   });
   ```

2. **Get Patient Profile**:
   ```javascript
   const profile = await fetch('http://localhost:5000/api/patient/me', {
     credentials: 'include'
   }).then(r => r.json());
   ```

3. **Get Matches**:
   ```javascript
   const matches = await fetch(
     http://localhost:5000/api/matches/?max_distance=50,
     { credentials: 'include' }
   ).then(r => r.json());
   ```

---

**Questions?** Contact the backend team or check the pp.py source code.
