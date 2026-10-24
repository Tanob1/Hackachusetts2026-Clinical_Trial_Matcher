# Clinical Trial Patient Matcher 🏥

**Hackachusetts 2026 Project**

Connecting patients with relevant clinical trials using intelligent matching algorithms.

## Problem

Patients with unique medical conditions struggle to find relevant clinical trials, while trials face recruitment challenges. Manual search is time-consuming and often misses opportunities.

## Solution

An intelligent matching system that:
- Analyzes patient medical profiles (demographics, conditions, medications)
- Matches against 3,131+ clinical trials recruiting in Massachusetts
- Ranks trials by relevance and proximity
- Provides instant, personalized results

## Tech Stack

- **Backend**: Python Flask REST API
- **Database**: SQLite (3,131 trials + 5 sample patients)
- **Matching**: Keyword-based algorithm with age eligibility scoring
- **Frontend**: HTML/CSS/JS (coming soon)
- **Mobile**: React Native (in development by teammate)

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher.git
cd Hackachusetts2026-Clinical_Trial_Matcher
```

### 2. Set up Python environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize database
```bash
python database.py
python data/load_data.py
```

### 4. Run the server
```bash
python app.py
```

Server runs at: **http://localhost:5000**

## API Documentation

See **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** for complete API reference.

### Quick API Test

```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sarah.chen","password":"demo123"}'

# Get matches for Sarah (patient ID 1)
curl http://localhost:5000/api/matches/1?max_distance=25
```

## Sample Patients

All use password: demo123

| Username | Name | Age | Conditions |
|----------|------|-----|------------|
| sarah.chen | Sarah Chen | 42 | Breast Cancer |
| john.smith | John Smith | 55 | Diabetes, Hypertension |
| maria.garcia | Maria Garcia | 68 | COPD, Heart Disease |
| david.lee | David Lee | 34 | Depression, Anxiety |
| emily.brown | Emily Brown | 45 | Multiple Sclerosis |

## Matching Algorithm

**Score Calculation**:
- **Condition Overlap**: 30 points per matching condition keyword
- **Age Eligibility**: 20 points if patient age within trial range
- **Maximum Score**: 100 points

**Example**:
- Patient: "Breast Cancer" (Age 42)
- Trial: "Advanced Breast Cancer" (Ages 18-75)
- Score: 30 (condition) + 20 (age) = **50/100 (50% match)**

## Project Structure

```
clinical-trial-matcher/
├── app.py                 # Flask API server
├── database.py            # Database setup and queries
├── matching.py            # Matching algorithm
├── requirements.txt       # Python dependencies
├── trials.db             # SQLite database (gitignored)
├── data/
│   └── load_data.py      # Data loading script
├── templates/            # HTML templates (coming soon)
├── static/              # CSS/JS (coming soon)
└── API_DOCUMENTATION.md  # Complete API docs
```

## For Mobile App Developers

1. **Start the backend server**: python app.py
2. **Base URL**: http://localhost:5000 (or your computer's IP)
3. **Read**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. **Test endpoints**: Use Postman or curl
5. **CORS enabled**: Cross-origin requests allowed for development

### Mobile App Flow

```
1. POST /login → Get session cookie
2. GET /api/patient/me → Get patient profile
3. GET /api/matches/{patient_id} → Get matched trials
4. GET /api/trials/{trial_id} → Get trial details
```

## Current Status

✅ **Completed**:
- Database schema and sample data (3,131 trials, 5 patients)
- REST API with authentication
- Matching algorithm (keyword + age-based)
- API documentation
- CORS support for mobile development

🚧 **In Progress**:
- Web UI (dashboard, trial cards, filters)
- Mobile app (React Native)

📅 **Next Steps**:
- Enhanced matching (medical terminology normalization)
- Real FHIR integration with hospitals
- Advanced filtering and search
- User profile management

## Team

- **Backend & Matching Engine**: [Your name]
- **Mobile App**: [Teammate name]

## Demo

**2-Minute Pitch**:
1. Problem: Patients can't find relevant trials
2. Login as Sarah (breast cancer patient)
3. See 18 matched trials ranked by relevance
4. Filter by distance (25 miles) → 8 nearby trials
5. View trial details with match explanation
6. Switch to John (diabetes) → different results
7. Impact: Instant matching saves lives

## License

MIT License - Hackachusetts 2026

## Acknowledgments

- Clinical trial data: ClinicalTrials.gov
- Hospital data: Massachusetts Department of Public Health
- Hackachusetts 2026 organizers

---

**Questions?** Open an issue or contact the team.

🚀 Built in 6 hours for Hackachusetts 2026
