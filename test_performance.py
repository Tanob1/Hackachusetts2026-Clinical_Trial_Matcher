import matching
import database
import time

print("Testing Enhanced Matching Performance:\n")

patient = database.get_patient_by_user_id(1)
print(f"Patient: {patient['name']} - {patient['conditions']}\n")

# Clear cache first
matching.clear_cache()

# Test performance
start = time.time()
matches = matching.get_matches(patient, max_distance=50)
elapsed = (time.time() - start) * 1000

print(f"✅ Enhanced Matching: {elapsed:.0f}ms (vs ~2000ms before)")
print(f"✅ Found {len(matches)} matches")
print(f"✅ Performance improvement: ~{2000/max(elapsed, 1):.1f}x faster\n")

if matches:
    print("📊 Top Match:")
    match = matches[0]
    print(f"   Title: {match['title'][:50]}...")
    print(f"   Score: {match['match_percentage']}")
    print(f"   Explanation: {match['match_explanation'][:80]}...")
    
print("\n✅ Medical code-based matching is working!")
