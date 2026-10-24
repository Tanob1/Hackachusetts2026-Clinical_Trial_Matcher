"""
SQLite-compatible routes for web UI.
Uses the SQLite adapter to read Flask database.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.sqlite_adapter import get_sqlite_adapter, SQLiteAdapter
from app.matching import score_trial, MatchResult
from app.models import TrialStatus
from app.deps import get_current_user_sqlite


router = APIRouter(prefix="/api/sqlite", tags=["sqlite"])


# Simple mock user class for matching
class MockUser:
    def __init__(self, data: dict):
        self.id = data['id']
        self.email = data['email']
        self.age = data['age']
        self.sex_assigned_at_birth = data['sex_assigned_at_birth']
        self.latitude = data['latitude']
        self.longitude = data['longitude']


class MockProfile:
    def __init__(self, data: dict):
        self.conditions = data['conditions']
        self.medications = data.get('medications', [])
        self.smoking_status = data.get('smoking_status')
        self.alcohol_use = data.get('alcohol_use')
        self.pregnancy_status = data.get('pregnancy_status')
        self.travel_radius_miles = data.get('travel_radius_miles', 50)


class MockTrial:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


@router.get("/matches")
async def get_matches_sqlite(
    username: str,
    limit: int = 50,
    adapter: SQLiteAdapter = Depends(get_sqlite_adapter)
):
    """Get trial matches using SQLite database."""
    
    # Get user and profile
    email = f"{username}@trialmatcher.local"
    user_data = await adapter.get_user_by_email(email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_data = await adapter.get_medical_profile(email)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get trials
    trials_data = await adapter.get_all_trials(['RECRUITING', 'ACTIVE'])
    
    # Create mock objects for matching engine
    user = MockUser(user_data)
    profile = MockProfile(profile_data)
    
    # Score each trial
    results: List[Dict[str, Any]] = []
    for trial_data in trials_data:
        trial = MockTrial(trial_data)
        
        match = score_trial(
            trial=trial,
            user_conditions=profile.conditions,
            user_meds=profile.medications,
            user_age=user.age,
            user_sex=user.sex_assigned_at_birth.value if hasattr(user.sex_assigned_at_birth, 'value') else str(user.sex_assigned_at_birth),
            user_pregnancy=profile.pregnancy_status.value if profile.pregnancy_status and hasattr(profile.pregnancy_status, 'value') else None,
            user_smoking=profile.smoking_status.value if profile.smoking_status and hasattr(profile.smoking_status, 'value') else None,
            user_lat=user.latitude,
            user_lng=user.longitude,
            travel_radius=profile.travel_radius_miles,
        )
        
        if match is not None:
            results.append({
                "id": trial_data['id'],
                "nct_id": trial_data['nct_id'],
                "title": trial_data['title'],
                "phase": trial_data['phase'],
                "conditions": trial_data['conditions'],
                "sponsor": trial_data.get('sponsor'),
                "locations": trial_data['locations'],
                "eligibility_inclusion": trial_data.get('eligibility_inclusion'),
                "eligibility_exclusion": trial_data.get('eligibility_exclusion'),
                "enrollment_status": trial_data['enrollment_status'].value if hasattr(trial_data['enrollment_status'], 'value') else str(trial_data['enrollment_status']),
                "last_updated": trial_data.get('last_updated'),
                "match_score": match.score,
                "match_strength": match.strength,
                "matched_conditions": match.matched_conditions,
                "nearest_distance_miles": match.nearest_distance_miles,
                "eligibility_summary": match.eligibility_summary,
                "match_explanation": match.match_explanation,
                "icd10_matches": match.icd10_matches,
            })
    
    # Sort by score
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    return results[:limit]


@router.get("/patients")
async def get_patients_sqlite(adapter: SQLiteAdapter = Depends(get_sqlite_adapter)):
    """Get all patients for switcher."""
    conn = adapter.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.username, p.name, p.age, p.conditions 
        FROM users u 
        JOIN patients p ON u.id = p.user_id
    ''')
    
    patients = []
    for row in cursor.fetchall():
        patients.append({
            'username': row['username'],
            'name': row['name'],
            'age': row['age'],
            'conditions': row['conditions'],
        })
    
    conn.close()
    return patients


@router.post("/login")
async def login_sqlite(
    username: str,
    password: str,
    adapter: SQLiteAdapter = Depends(get_sqlite_adapter)
):
    """Login with SQLite database."""
    email = f"{username}@trialmatcher.local"
    user = await adapter.verify_credentials(email, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # For demo, just return success with username
    return {
        "access_token": f"demo-token-{username}",
        "token_type": "bearer",
        "username": username,
    }
