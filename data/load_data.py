"""
Load clinical trials data from CSV into database
"""
import pandas as pd
import sqlite3
import random

def estimate_distance(city):
    """
    Estimate distance from Boston for Massachusetts cities
    Simple approximation for demo purposes
    """
    if not city or pd.isna(city):
        return random.randint(10, 50)  # Random distance for unknown
    
    city = city.upper().strip()
    
    # Distance estimates in miles from Boston
    distances = {
        'BOSTON': 0,
        'CAMBRIDGE': 3,
        'SOMERVILLE': 4,
        'BROOKLINE': 5,
        'NEWTON': 8,
        'WALTHAM': 10,
        'MEDFORD': 5,
        'EVERETT': 4,
        'QUINCY': 8,
        'SALEM': 16,
        'LYNN': 10,
        'WORCESTER': 45,
        'SPRINGFIELD': 90,
        'LOWELL': 30,
        'NEW BEDFORD': 60,
        'FRAMINGHAM': 20,
        'FALL RIVER': 55,
        'LAWRENCE': 30,
        'TAUNTON': 35,
        'BROCKTON': 20,
        'HYANNIS': 70,
        'NANTUCKET': 90,
        'OAK BLUFFS': 85,
        'NORTHAMPTON': 90,
        'HOLYOKE': 90,
        'PITTSFIELD': 135,
        'GREAT BARRINGTON': 130,
        'GARDNER': 60,
        'SOUTHBRIDGE': 55,
        'NEEDHAM': 12,
        'NEWBURYPORT': 35,
        'BEVERLY': 20,
        'GLOUCESTER': 30
    }
    
    return distances.get(city, random.randint(15, 80))

def estimate_age_range(phase, conditions):
    """
    Estimate age eligibility based on phase and conditions
    Simple heuristic for demo
    """
    # Pediatric conditions
    pediatric_keywords = ['pediatric', 'children', 'child', 'infant', 'neonatal']
    if any(keyword in conditions.lower() for keyword in pediatric_keywords):
        return 1, 17
    
    # Most adult trials
    if phase in ['PHASE1', 'EARLY_PHASE1']:
        return 18, 65  # Phase 1 typically excludes elderly
    elif phase in ['PHASE2', 'PHASE3', 'PHASE4']:
        return 18, 75  # Later phases may include more age ranges
    else:
        return 18, 100  # Observational studies often have wider ranges

def load_trials_from_csv(csv_path, db_path='trials.db'):
    """Load trials from CSV into database"""
    print(f"Loading trials from {csv_path}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} trials in CSV")
    
    # Clean and enhance data
    df['city'] = df['massachusetts_city'].fillna('Boston')  # Default to Boston if empty
    df['distance_from_boston'] = df['city'].apply(estimate_distance)
    
    # Estimate age ranges
    age_ranges = df.apply(
        lambda row: estimate_age_range(row['phase'], row['conditions']), 
        axis=1
    )
    df['min_age'] = age_ranges.apply(lambda x: x[0])
    df['max_age'] = age_ranges.apply(lambda x: x[1])
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert trials
    inserted = 0
    skipped = 0
    
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO trials (nct_id, title, phase, conditions, city, status, min_age, max_age, distance_from_boston)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['nct_id'],
                row['title'],
                row['phase'] if pd.notna(row['phase']) else 'NA',
                row['conditions'],
                row['city'],
                row['status'],
                row['min_age'],
                row['max_age'],
                row['distance_from_boston']
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1  # Trial already exists
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {inserted} trials")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} duplicate trials")
    
    return inserted

if __name__ == '__main__':
    # Path to trials CSV
    csv_path = '../trials/data.csv'
    
    print("Loading clinical trials data...")
    count = load_trials_from_csv(csv_path)
    print(f"\n✅ Successfully loaded {count} trials into database!")
