"""
SQLite Database Adapter for FastAPI
Bridges Flask SQLite schema to FastAPI models
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
import uuid

from app.models import TrialStatus, SexAssignedAtBirth, SmokingStatus


class SQLiteAdapter:
    """Adapter to read Flask SQLite database with FastAPI-compatible interface."""
    
    def __init__(self, db_path: str = "trials.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    async def get_user_by_email(self, email: str):
        """Get user by email (convert username@trialmatcher.local format)."""
        # Extract username from email
        username = email.split('@')[0] if '@' in email else email
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        
        if not user_row:
            conn.close()
            return None
        
        # Get patient profile
        cursor.execute('SELECT * FROM patients WHERE user_id = ?', (user_row['id'],))
        patient_row = cursor.fetchone()
        
        conn.close()
        
        if not patient_row:
            return None
        
        # Build FastAPI-compatible user dict
        return {
            'id': str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user-{user_row['id']}")),
            'email': f"{user_row['username']}@trialmatcher.local",
            'phone': None,
            'password_hash': user_row['password_hash'],
            'age': patient_row['age'],
            'sex_assigned_at_birth': SexAssignedAtBirth.female if patient_row['gender'].lower() == 'female' else SexAssignedAtBirth.male,
            'location_text': f"{patient_row['city']}, MA {patient_row['zip_code']}",
            'latitude': 42.3601,  # Default Boston
            'longitude': -71.0589,
            'fcm_token': None,
            'notifications_enabled': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }
    
    async def get_medical_profile(self, user_email: str):
        """Get medical profile for user."""
        username = user_email.split('@')[0] if '@' in email else user_email
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return None
        
        # Get patient
        cursor.execute('SELECT * FROM patients WHERE user_id = ?', (user_row['id'],))
        patient_row = cursor.fetchone()
        conn.close()
        
        if not patient_row:
            return None
        
        # Parse conditions (comma-separated)
        conditions = [c.strip() for c in patient_row['conditions'].split(',')]
        
        return {
            'user_id': str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user-{user_row['id']}")),
            'conditions': conditions,
            'medications': [],
            'allergies': [],
            'medical_history': f"Patient: {patient_row['name']}",
            'biomarkers': '',
            'smoking_status': SmokingStatus.never,
            'alcohol_use': None,
            'pregnancy_status': None,
            'travel_radius_miles': 50,
        }
    
    async def get_all_trials(self, status_filter: Optional[List[str]] = None):
        """Get all trials with optional status filter."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status_filter:
            placeholders = ','.join(['?' for _ in status_filter])
            cursor.execute(f'SELECT * FROM trials WHERE status IN ({placeholders})', status_filter)
        else:
            cursor.execute('SELECT * FROM trials')
        
        trials = []
        for row in cursor.fetchall():
            trial = self._convert_trial_row(row)
            trials.append(trial)
        
        conn.close()
        return trials
    
    def _convert_trial_row(self, row):
        """Convert SQLite trial row to FastAPI Trial-compatible dict."""
        # Parse conditions
        conditions = [c.strip() for c in row['conditions'].split(',') if c.strip()]
        
        # Map status
        status_map = {
            'RECRUITING': TrialStatus.recruiting,
            'ACTIVE': TrialStatus.active,
            'COMPLETED': TrialStatus.completed,
        }
        status = status_map.get(row['status'], TrialStatus.recruiting)
        
        # Build location
        city = row['city'] if row['city'] else 'Boston'
        locations = [{
            'city': city,
            'state': 'Massachusetts',
            'country': 'United States',
            'facility': None,
            'lat': 42.3601 if city == 'Boston' else None,
            'lng': -71.0589 if city == 'Boston' else None,
        }]
        
        return {
            'id': str(uuid.uuid5(uuid.NAMESPACE_DNS, f"trial-{row['nct_id']}")),
            'nct_id': row['nct_id'],
            'title': row['title'],
            'brief_summary': None,
            'detailed_description': None,
            'phase': row['phase'],
            'conditions': conditions,
            'keywords': [],
            'sponsor': None,
            'locations': locations,
            'eligibility_inclusion': None,
            'eligibility_exclusion': None,
            'eligibility_sex': 'All',
            'eligibility_min_age': f"{row['min_age']} Years" if row['min_age'] else None,
            'eligibility_max_age': f"{row['max_age']} Years" if row['max_age'] else None,
            'enrollment_status': status,
            'contact_name': None,
            'contact_phone': None,
            'contact_email': None,
            'url': f"https://clinicaltrials.gov/study/{row['nct_id']}",
            'last_updated': datetime.now(),
        }
    
    async def get_trial_by_id(self, trial_id: str):
        """Get single trial by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trials WHERE id = ?', (trial_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._convert_trial_row(row)
    
    async def verify_credentials(self, email: str, password: str):
        """Verify user credentials."""
        from werkzeug.security import check_password_hash
        
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if check_password_hash(user['password_hash'], password):
            return user
        
        return None


# Singleton instance
_adapter = None

def get_sqlite_adapter() -> SQLiteAdapter:
    """Get singleton SQLite adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = SQLiteAdapter()
    return _adapter
