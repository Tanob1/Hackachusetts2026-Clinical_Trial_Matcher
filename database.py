"""
Database setup and queries for Clinical Trial Matcher
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    create_sample_patients()
    print("\n✅ Database setup complete!")
