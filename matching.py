"""
Enhanced Clinical Trial Matching Engine
Uses medical codes (ICD-10) + keyword matching + age eligibility
"""
import database
import medical_codes
from functools import lru_cache

# Cache for match results (in-memory for MVP)
_match_cache = {}

def calculate_match_score_enhanced(patient, trial):
    """
    Enhanced match score calculation using medical codes
    Returns dict with score, matched conditions, and explanation
    """
    score = 0
    matched_conditions = []
    explanations = []
    match_details = []
    
    # Use medical code matching
    matches = medical_codes.find_matching_conditions(
        patient['conditions'],
        trial['conditions']
    )
    
    # Calculate score from matches
    for match in matches:
        if match['match_type'] == 'icd10_exact':
            # Perfect match via ICD-10 code
            score += 50  # Higher weight for medical code matches
            matched_conditions.append(match['normalized_patient'])
            match_details.append({
                'patient': match['patient_condition'],
                'trial': match['trial_condition'],
                'type': 'Medical Code Match (ICD-10)',
                'codes': match['icd10_codes']
            })
            explanations.append(
                f"Perfect match: {match['patient_condition']} ↔ {match['trial_condition']} "
                f"(ICD-10: {', '.join(match['icd10_codes'])})"
            )
        elif match['match_type'] == 'keyword':
            # Keyword/synonym match
            score += match['match_score']
            matched_conditions.append(match['normalized_patient'])
            match_details.append({
                'patient': match['patient_condition'],
                'trial': match['trial_condition'],
                'type': 'Keyword Match'
            })
            explanations.append(
                f"Condition match: {match['patient_condition']}"
            )
    
    # Age eligibility bonus (20 points)
    age_eligible = False
    if trial['min_age'] and trial['max_age']:
        if trial['min_age'] <= patient['age'] <= trial['max_age']:
            score += 20
            age_eligible = True
            explanations.append(
                f"Age {patient['age']} within range ({trial['min_age']}-{trial['max_age']})"
            )
    
    # Cap score at 100
    score = min(score, 100)
    
    # Build explanation
    if not matched_conditions:
        explanation = "No direct condition match found"
    else:
        explanation = ". ".join(explanations) + "."
    
    return {
        'trial_id': trial['id'],
        'nct_id': trial['nct_id'],
        'title': trial['title'],
        'phase': trial['phase'],
        'conditions': trial['conditions'],
        'city': trial['city'],
        'status': trial['status'],
        'distance_miles': trial['distance_from_boston'],
        'match_score': score,
        'match_percentage': f"{score}%",
        'matched_conditions': list(set(matched_conditions)),
        'match_explanation': explanation,
        'match_details': match_details,
        'age_eligible': age_eligible,
        'min_age': trial['min_age'],
        'max_age': trial['max_age']
    }

@lru_cache(maxsize=100)
def get_matches_cached(patient_id, patient_conditions, patient_age, max_distance=100, phase_filter=None):
    """
    Cached version of get_matches for performance
    Uses LRU cache to store recent match results
    """
    # This is called from get_matches with cacheable parameters
    return _get_matches_internal(patient_id, patient_conditions, patient_age, max_distance, phase_filter)

def _get_matches_internal(patient_id, patient_conditions, patient_age, max_distance, phase_filter):
    """Internal matching logic"""
    patient = {
        'id': patient_id,
        'conditions': patient_conditions,
        'age': patient_age
    }
    
    # Get all trials
    trials = database.get_all_trials()
    matches = []
    
    for trial in trials:
        # Apply distance filter
        if trial['distance_from_boston'] > max_distance:
            continue
        
        # Apply phase filter
        if phase_filter and trial['phase'] != phase_filter:
            continue
        
        # Calculate match score
        match = calculate_match_score_enhanced(patient, trial)
        
        # Only include trials with some match
        if match['match_score'] > 0:
            matches.append(match)
    
    # Sort by match score (descending), then by distance (ascending)
    matches.sort(key=lambda x: (x['match_score'], -x['distance_miles']), reverse=True)
    
    # Return top 20 matches
    return matches[:20]

def get_matches(patient, max_distance=100, phase_filter=None):
    """
    Get matched trials for a patient
    Uses caching for improved performance
    
    Args:
        patient: Patient dict with conditions, age, etc.
        max_distance: Maximum distance in miles from patient
        phase_filter: Optional phase filter (e.g., 'PHASE3')
    
    Returns:
        List of matched trials with scores, sorted by relevance
    """
    # Use cached version
    return get_matches_cached(
        patient['id'],
        patient['conditions'],
        patient['age'],
        max_distance,
        phase_filter or ''
    )

def clear_cache():
    """Clear the match cache (useful for testing/updates)"""
    get_matches_cached.cache_clear()
    global _match_cache
    _match_cache = {}

# For testing
if __name__ == '__main__':
    print("Testing enhanced matching engine...\n")
    
    # Get a sample patient
    patient = database.get_patient_by_user_id(1)
    print(f"Patient: {patient['name']}")
    print(f"Conditions: {patient['conditions']}")
    print(f"Age: {patient['age']}\n")
    
    # Test performance with timing
    import time
    
    # First call (no cache)
    start = time.time()
    matches = get_matches(patient, max_distance=50)
    elapsed_first = (time.time() - start) * 1000
    
    print(f"First call (no cache): {elapsed_first:.0f}ms")
    print(f"Found {len(matches)} matches within 50 miles\n")
    
    # Second call (with cache)
    start = time.time()
    matches = get_matches(patient, max_distance=50)
    elapsed_cached = (time.time() - start) * 1000
    
    print(f"Second call (cached): {elapsed_cached:.0f}ms")
    print(f"Performance improvement: {(elapsed_first / elapsed_cached):.1f}x faster\n")
    
    # Show top 3 matches
    print("Top 3 Matches (with medical code intelligence):")
    for i, match in enumerate(matches[:3], 1):
        print(f"\n{i}. {match['title'][:60]}...")
        print(f"   Score: {match['match_percentage']} (enhanced algorithm)")
        print(f"   Distance: {match['distance_miles']} miles")
        print(f"   Matched: {', '.join(match['matched_conditions'])}")
        print(f"   Explanation: {match['match_explanation']}")
        if match.get('match_details'):
            for detail in match['match_details']:
                print(f"   • {detail['type']}: {detail['patient']} ↔ {detail['trial']}")
