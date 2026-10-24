import database

conn = database.get_db()
users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
trials = conn.execute("SELECT COUNT(*) FROM trials").fetchone()[0]

print(f"✅ Database Status:")
print(f"   Users: {users}")
print(f"   Patients: {patients}")
print(f"   Trials: {trials}")

# Show sample data
patient = database.get_patient_by_user_id(1)
print(f"\n📋 Sample Patient:")
print(f"   Name: {patient['name']}")
print(f"   Age: {patient['age']}")
print(f"   Conditions: {patient['conditions']}")

trial = database.get_trial_by_id(1)
print(f"\n🔬 Sample Trial:")
print(f"   NCT ID: {trial['nct_id']}")
print(f"   Title: {trial['title'][:60]}...")
print(f"   Conditions: {trial['conditions']}")
print(f"   Distance from Boston: {trial['distance_from_boston']} miles")
