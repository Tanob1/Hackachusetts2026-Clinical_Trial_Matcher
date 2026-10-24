"""
Database setup and queries for Clinical Trial Matcher
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

DATABASE = 'trials.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            conditions TEXT NOT NULL,
            city TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Trials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nct_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            phase TEXT,
            conditions TEXT NOT NULL,
            city TEXT,
            status TEXT DEFAULT 'RECRUITING',
            min_age INTEGER,
            max_age INTEGER,
            distance_from_boston INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database schema created successfully")

def create_sample_patients():
    """Create sample patient profiles for demo"""
    conn = get_db()
    cursor = conn.cursor()
    
    sample_patients = [
        {
            'username': 'sarah.chen',
            'password': 'demo123',
            'name': 'Sarah Chen',
            'age': 42,
            'gender': 'Female',
            'zip_code': '02115',
            'city': 'Boston',
            'conditions': 'Breast Cancer'
        },
        {
            'username': 'john.smith',
            'password': 'demo123',
            'name': 'John Smith',
            'age': 55,
            'gender': 'Male',
            'zip_code': '02139',
            'city': 'Cambridge',
            'conditions': 'Diabetes, Hypertension'
        },
        {
            'username': 'maria.garcia',
            'password': 'demo123',
            'name': 'Maria Garcia',
            'age': 68,
            'gender': 'Female',
            'zip_code': '01605',
            'city': 'Worcester',
            'conditions': 'COPD, Heart Disease'
        },
        {
            'username': 'david.lee',
            'password': 'demo123',
            'name': 'David Lee',
            'age': 34,
            'gender': 'Male',
            'zip_code': '01104',
            'city': 'Springfield',
            'conditions': 'Depression, Anxiety'
        },
        {
            'username': 'emily.brown',
            'password': 'demo123',
            'name': 'Emily Brown',
            'age': 45,
            'gender': 'Female',
            'zip_code': '02118',
            'city': 'Boston',
            'conditions': 'Multiple Sclerosis'
        }
    ]
    
    for patient_data in sample_patients:
        # Create user
        try:
            password_hash = generate_password_hash(patient_data['password'])
            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (patient_data['username'], password_hash))
            user_id = cursor.lastrowid
            
            # Create patient profile
            cursor.execute('''
                INSERT INTO patients (user_id, name, age, gender, zip_code, city, conditions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                patient_data['name'],
                patient_data['age'],
                patient_data['gender'],
                patient_data['zip_code'],
                patient_data['city'],
                patient_data['conditions']
            ))
            print(f"✅ Created patient: {patient_data['name']}")
        except sqlite3.IntegrityError:
            print(f"⚠️  User {patient_data['username']} already exists, skipping...")
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_patient_by_user_id(user_id):
    """Get patient profile by user ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE user_id = ?', (user_id,))
    patient = cursor.fetchone()
    conn.close()
    return dict(patient) if patient else None

def get_all_trials():
    """Get all trials"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trials')
    trials = cursor.fetchall()
    conn.close()
    return [dict(trial) for trial in trials]

def get_trial_by_id(trial_id):
    """Get trial by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trials WHERE id = ?', (trial_id,))
    trial = cursor.fetchone()
    conn.close()
    return dict(trial) if trial else None

def verify_password(stored_hash, password):
    """Verify password against hash"""
    return check_password_hash(stored_hash, password)

# ============= Provider Portal Functions =============

def init_provider_tables():
    """Initialize provider portal tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Providers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            hospital_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Referrals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
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
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Provider tables created successfully")

def create_demo_providers():
    """Create demo provider accounts"""
    conn = get_db()
    cursor = conn.cursor()
    
    demo_providers = [
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
            'hospital_name': "Brigham and Women's Hospital"
        }
    ]
    
    for provider_data in demo_providers:
        try:
            password_hash = generate_password_hash(provider_data['password'])
            cursor.execute('''
                INSERT INTO providers (email, password_hash, name, hospital_name)
                VALUES (?, ?, ?, ?)
            ''', (
                provider_data['email'],
                password_hash,
                provider_data['name'],
                provider_data['hospital_name']
            ))
            print(f"✅ Created provider: {provider_data['name']}")
        except sqlite3.IntegrityError:
            print(f"⚠️  Provider {provider_data['email']} already exists, skipping...")
    
    conn.commit()
    conn.close()

def get_provider_by_email(email):
    """Get provider by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM providers WHERE email = ?', (email,))
    provider = cursor.fetchone()
    conn.close()
    return dict(provider) if provider else None

def search_patients(query):
    """Search patients by name (partial match)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM patients 
        WHERE LOWER(name) LIKE LOWER(?)
        ORDER BY name
    ''', (f'%{query}%',))
    patients = cursor.fetchall()
    conn.close()
    return [dict(p) for p in patients]

def get_patient_by_id(patient_id):
    """Get patient by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return dict(patient) if patient else None

def generate_referral_code():
    """Generate unique referral code: REF-YYYYMMDD-XXXX"""
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"REF-{date_str}-{random_str}"

def create_referral(referral_code, provider_id, patient_id, trial_id, provider_notes=''):
    """Create a new referral"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO referrals (referral_code, provider_id, patient_id, trial_id, provider_notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (referral_code, provider_id, patient_id, trial_id, provider_notes))
    referral_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return referral_id

def get_referral_by_code(referral_code):
    """Get referral by code with joined data"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, 
               p.name as provider_name, p.hospital_name,
               pat.name as patient_name, pat.age as patient_age, pat.conditions as patient_conditions,
               t.title as trial_title, t.nct_id, t.phase, t.city
        FROM referrals r
        JOIN providers p ON r.provider_id = p.id
        JOIN patients pat ON r.patient_id = pat.id
        JOIN trials t ON r.trial_id = t.id
        WHERE r.referral_code = ?
    ''', (referral_code,))
    referral = cursor.fetchone()
    conn.close()
    return dict(referral) if referral else None



def update_patient_conditions(user_id, conditions):
    """Update patient's medical conditions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE patients 
        SET conditions = ? 
        WHERE user_id = ?
    ''', (conditions, user_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    create_sample_patients()
    print("\nInitializing provider tables...")
    init_provider_tables()
    create_demo_providers()
    print("\n✅ Database setup complete!")

