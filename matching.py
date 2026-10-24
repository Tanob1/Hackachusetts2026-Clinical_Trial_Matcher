"""
Clinical Trial Matching Engine
Keyword-based matching with age eligibility scoring
"""
import database

def calculate_match_score(patient, trial):
    """
    Calculate match score between patient and trial
    Returns dict with score, matched conditions, and explanation
    """
    score = 0
    matched_conditions = []
    explanations = []
    
    # Parse patient conditions (comma-separated, case-insensitive)
    patient_conds = set(c.strip().lower() for c in patient['conditions'].split(','))
    
    # Parse trial conditions (comma-separated, case-insensitive)
    trial_conds = set(c.strip().lower() for c in trial['conditions'].split(','))
    
    # Condition keyword overlap (30 points per match)
    # Check if any patient condition keyword appears in any trial condition
    for p_cond in patient_conds:
        for t_cond in trial_conds:
            if p_cond in t_cond or t_cond in p_cond:
                score += 30
                matched_conditions.append(p_cond)
                explanations.append(f"Matched condition: {p_cond.title()}")
                break  # Avoid double-counting same patient condition
    
    # Age eligibility bonus (20 points)
    age_eligible = False
    if trial['min_age'] and trial['max_age']:
        if trial['min_age'] <= patient['age'] <= trial['max_age']:
            score += 20
            age_eligible = True
            explanations.append(f"Age {patient['age']} is within trial range ({trial['min_age']}-{trial['max_age']})")
        else:
            explanations.append(f"Age {patient['age']} is outside trial range ({trial['min_age']}-{trial['max_age']})")
    
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
        'matched_conditions': list(set(matched_conditions)),  # Remove duplicates
        'match_explanation': explanation,
        'age_eligible': age_eligible,
        'min_age': trial['min_age'],
        'max_age': trial['max_age']
    }

def get_matches(patient, max_distance=100, phase_filter=None):
    """
    Get matched trials for a patient
    
    Args:
        patient: Patient dict with conditions, age, etc.
        max_distance: Maximum distance in miles from patient
        phase_filter: Optional phase filter (e.g., 'PHASE3')
    
    Returns:
        List of matched trials with scores, sorted by relevance
    """
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
        match = calculate_match_score(patient, trial)
        
        # Only include trials with some match
        if match['match_score'] > 0:
            matches.append(match)
    
    # Sort by match score (descending), then by distance (ascending)
    matches.sort(key=lambda x: (x['match_score'], -x['distance_miles']), reverse=True)
    
    # Return top 20 matches
    return matches[:20]

# For testing
if __name__ == '__main__':
    print("Testing matching engine...")
    
    # Get a sample patient
    patient = database.get_patient_by_user_id(1)
    print(f"\nPatient: {patient['name']}")
    print(f"Conditions: {patient['conditions']}")
    print(f"Age: {patient['age']}")
    
    # Get matches
    matches = get_matches(patient, max_distance=50)
    print(f"\nFound {len(matches)} matches within 50 miles")
    
    # Show top 3
    print("\nTop 3 Matches:")
    for i, match in enumerate(matches[:3], 1):
        print(f"\n{i}. {match['title'][:60]}...")
        print(f"   Score: {match['match_percentage']}")
        print(f"   Distance: {match['distance_miles']} miles")
        print(f"   Matched: {', '.join(match['matched_conditions'])}")
        print(f"   Explanation: {match['match_explanation']}")
