"""
Medical Code Mapping - ICD-10 Lite
Maps common condition names to ICD-10 codes and synonyms
"""

# Common medical conditions with ICD-10 codes and synonyms
MEDICAL_CODES = {
    # Cancer/Oncology
    'breast cancer': {
        'icd10': ['C50', 'C50.9'],
        'synonyms': ['breast neoplasm', 'breast carcinoma', 'mammary cancer', 'breast tumor', 'breast malignancy'],
        'keywords': ['breast', 'mammary', 'ductal', 'lobular']
    },
    'lung cancer': {
        'icd10': ['C34', 'C34.9'],
        'synonyms': ['pulmonary cancer', 'lung carcinoma', 'bronchogenic carcinoma', 'nsclc', 'non-small cell lung cancer'],
        'keywords': ['lung', 'pulmonary', 'bronchogenic', 'nsclc']
    },
    'colorectal cancer': {
        'icd10': ['C18', 'C19', 'C20'],
        'synonyms': ['colon cancer', 'rectal cancer', 'bowel cancer', 'crc'],
        'keywords': ['colon', 'colorectal', 'rectal', 'bowel']
    },
    'prostate cancer': {
        'icd10': ['C61'],
        'synonyms': ['prostatic cancer', 'prostate carcinoma', 'prostate neoplasm'],
        'keywords': ['prostate', 'prostatic']
    },
    'ovarian cancer': {
        'icd10': ['C56'],
        'synonyms': ['ovary cancer', 'ovarian carcinoma', 'ovarian neoplasm'],
        'keywords': ['ovarian', 'ovary']
    },
    'pancreatic cancer': {
        'icd10': ['C25'],
        'synonyms': ['pancreas cancer', 'pancreatic carcinoma', 'pdac'],
        'keywords': ['pancreatic', 'pancreas', 'pdac']
    },
    'melanoma': {
        'icd10': ['C43'],
        'synonyms': ['malignant melanoma', 'skin cancer'],
        'keywords': ['melanoma', 'skin cancer']
    },
    'leukemia': {
        'icd10': ['C91', 'C92', 'C93'],
        'synonyms': ['blood cancer', 'aml', 'cll', 'acute myeloid leukemia', 'chronic lymphocytic leukemia'],
        'keywords': ['leukemia', 'leukaemia', 'aml', 'cll', 'blood cancer']
    },
    'lymphoma': {
        'icd10': ['C81', 'C82', 'C83'],
        'synonyms': ['hodgkin', 'non-hodgkin', 'hodgkins disease'],
        'keywords': ['lymphoma', 'hodgkin', 'non-hodgkin']
    },
    
    # Cardiovascular
    'heart disease': {
        'icd10': ['I25', 'I25.9'],
        'synonyms': ['coronary artery disease', 'cad', 'cardiovascular disease', 'cvd', 'cardiac disease'],
        'keywords': ['heart', 'cardiac', 'coronary', 'cardiovascular', 'cad']
    },
    'heart failure': {
        'icd10': ['I50', 'I50.9'],
        'synonyms': ['chf', 'congestive heart failure', 'cardiac failure'],
        'keywords': ['heart failure', 'chf', 'congestive']
    },
    'hypertension': {
        'icd10': ['I10'],
        'synonyms': ['high blood pressure', 'htn', 'arterial hypertension'],
        'keywords': ['hypertension', 'high blood pressure', 'htn']
    },
    'atrial fibrillation': {
        'icd10': ['I48', 'I48.0'],
        'synonyms': ['afib', 'a-fib', 'atrial fib', 'auricular fibrillation'],
        'keywords': ['atrial fibrillation', 'afib', 'a-fib']
    },
    'stroke': {
        'icd10': ['I63', 'I64'],
        'synonyms': ['cerebrovascular accident', 'cva', 'brain attack'],
        'keywords': ['stroke', 'cva', 'cerebrovascular']
    },
    
    # Diabetes & Metabolic
    'diabetes': {
        'icd10': ['E11', 'E10'],
        'synonyms': ['diabetes mellitus', 'type 2 diabetes', 'type 1 diabetes', 't2dm', 't1dm', 'dm'],
        'keywords': ['diabetes', 'diabetic', 't2dm', 't1dm', 'mellitus']
    },
    'obesity': {
        'icd10': ['E66'],
        'synonyms': ['overweight', 'morbid obesity'],
        'keywords': ['obesity', 'obese', 'overweight']
    },
    
    # Respiratory
    'copd': {
        'icd10': ['J44', 'J44.9'],
        'synonyms': ['chronic obstructive pulmonary disease', 'emphysema', 'chronic bronchitis'],
        'keywords': ['copd', 'emphysema', 'chronic bronchitis', 'obstructive pulmonary']
    },
    'asthma': {
        'icd10': ['J45'],
        'synonyms': ['bronchial asthma', 'asthma bronchiale'],
        'keywords': ['asthma', 'asthmatic']
    },
    
    # Neurological
    'alzheimer': {
        'icd10': ['G30'],
        'synonyms': ['alzheimers disease', 'dementia alzheimer', 'ad'],
        'keywords': ['alzheimer', 'alzheimers']
    },
    'parkinson': {
        'icd10': ['G20'],
        'synonyms': ['parkinsons disease', 'pd', 'parkinsonism'],
        'keywords': ['parkinson', 'parkinsons']
    },
    'multiple sclerosis': {
        'icd10': ['G35'],
        'synonyms': ['ms', 'disseminated sclerosis'],
        'keywords': ['multiple sclerosis', 'ms']
    },
    'epilepsy': {
        'icd10': ['G40'],
        'synonyms': ['seizure disorder', 'epileptic'],
        'keywords': ['epilepsy', 'seizure', 'epileptic']
    },
    'migraine': {
        'icd10': ['G43'],
        'synonyms': ['headache', 'migraine headache'],
        'keywords': ['migraine', 'headache']
    },
    
    # Mental Health
    'depression': {
        'icd10': ['F32', 'F33'],
        'synonyms': ['major depressive disorder', 'mdd', 'clinical depression', 'depressive disorder'],
        'keywords': ['depression', 'depressive', 'mdd']
    },
    'anxiety': {
        'icd10': ['F41'],
        'synonyms': ['anxiety disorder', 'generalized anxiety', 'gad'],
        'keywords': ['anxiety', 'anxious']
    },
    'bipolar': {
        'icd10': ['F31'],
        'synonyms': ['bipolar disorder', 'manic depression', 'manic-depressive'],
        'keywords': ['bipolar', 'manic']
    },
    'schizophrenia': {
        'icd10': ['F20'],
        'synonyms': ['schizophrenic disorder'],
        'keywords': ['schizophrenia', 'schizophrenic']
    },
    'ptsd': {
        'icd10': ['F43.1'],
        'synonyms': ['post-traumatic stress disorder', 'post traumatic stress', 'trauma'],
        'keywords': ['ptsd', 'post-traumatic', 'post traumatic']
    },
    
    # Autoimmune
    'rheumatoid arthritis': {
        'icd10': ['M05', 'M06'],
        'synonyms': ['ra', 'rheumatoid disease', 'arthritis rheumatoid'],
        'keywords': ['rheumatoid', 'arthritis', 'ra']
    },
    'lupus': {
        'icd10': ['M32'],
        'synonyms': ['sle', 'systemic lupus erythematosus', 'lupus erythematosus'],
        'keywords': ['lupus', 'sle']
    },
    'crohn': {
        'icd10': ['K50'],
        'synonyms': ['crohns disease', 'crohn disease', 'regional enteritis', 'ibd'],
        'keywords': ['crohn', 'crohns', 'enteritis']
    },
    
    # Infectious
    'hiv': {
        'icd10': ['B20'],
        'synonyms': ['human immunodeficiency virus', 'aids', 'acquired immunodeficiency'],
        'keywords': ['hiv', 'aids', 'immunodeficiency']
    },
    'hepatitis': {
        'icd10': ['B15', 'B16', 'B17', 'B18', 'B19'],
        'synonyms': ['hepatitis a', 'hepatitis b', 'hepatitis c', 'hep c', 'hep b'],
        'keywords': ['hepatitis', 'hep']
    }
}

def normalize_condition(condition):
    """
    Normalize a condition name to standard form with medical codes
    Returns: dict with normalized name, ICD-10 codes, and keywords
    """
    condition_lower = condition.lower().strip()
    
    # Direct match
    if condition_lower in MEDICAL_CODES:
        data = MEDICAL_CODES[condition_lower]
        return {
            'original': condition,
            'normalized': condition_lower,
            'icd10': data['icd10'],
            'keywords': data['keywords'],
            'matched': True
        }
    
    # Check synonyms
    for standard_name, data in MEDICAL_CODES.items():
        if condition_lower in data['synonyms']:
            return {
                'original': condition,
                'normalized': standard_name,
                'icd10': data['icd10'],
                'keywords': data['keywords'],
                'matched': True
            }
        
        # Check if condition contains any keyword
        for keyword in data['keywords']:
            if keyword in condition_lower:
                return {
                    'original': condition,
                    'normalized': standard_name,
                    'icd10': data['icd10'],
                    'keywords': data['keywords'],
                    'matched': True
                }
    
    # No match found - return basic normalization
    return {
        'original': condition,
        'normalized': condition_lower,
        'icd10': [],
        'keywords': [condition_lower],
        'matched': False
    }

def find_matching_conditions(patient_conditions, trial_conditions):
    """
    Find matching conditions between patient and trial using medical codes
    Returns: list of matches with scores
    """
    matches = []
    
    # Normalize patient conditions
    patient_normalized = [normalize_condition(c.strip()) for c in patient_conditions.split(',')]
    trial_normalized = [normalize_condition(c.strip()) for c in trial_conditions.split(',')]
    
    for p_cond in patient_normalized:
        for t_cond in trial_normalized:
            match_score = 0
            match_type = None
            
            # Check ICD-10 code match (highest priority)
            if p_cond['icd10'] and t_cond['icd10']:
                common_codes = set(p_cond['icd10']) & set(t_cond['icd10'])
                if common_codes:
                    match_score = 100
                    match_type = 'icd10_exact'
            
            # Check keyword overlap
            if match_score == 0:
                p_keywords = set(p_cond['keywords'])
                t_keywords = set(t_cond['keywords'])
                common_keywords = p_keywords & t_keywords
                
                if common_keywords:
                    match_score = len(common_keywords) * 30
                    match_type = 'keyword'
            
            if match_score > 0:
                matches.append({
                    'patient_condition': p_cond['original'],
                    'trial_condition': t_cond['original'],
                    'normalized_patient': p_cond['normalized'],
                    'normalized_trial': t_cond['normalized'],
                    'match_score': min(match_score, 100),
                    'match_type': match_type,
                    'icd10_codes': list(set(p_cond['icd10']) & set(t_cond['icd10']))
                })
    
    return matches

# For testing
if __name__ == '__main__':
    # Test normalization
    test_conditions = [
        "Breast Cancer",
        "Type 2 Diabetes",
        "Heart Attack",
        "MDD",
        "NSCLC",
        "Unknown Condition"
    ]
    
    print("Testing Medical Code Normalization:\n")
    for condition in test_conditions:
        result = normalize_condition(condition)
        if result['matched']:
            print(f"✅ {condition}")
            print(f"   → Normalized: {result['normalized']}")
            print(f"   → ICD-10: {', '.join(result['icd10'])}")
            print(f"   → Keywords: {', '.join(result['keywords'])}\n")
        else:
            print(f"⚠️  {condition} - No medical code match\n")
    
    # Test matching
    print("\nTesting Condition Matching:")
    patient = "Breast Cancer, Diabetes"
    trial = "Advanced Breast Neoplasm, Type 2 Diabetes Mellitus"
    
    matches = find_matching_conditions(patient, trial)
    print(f"\nPatient: {patient}")
    print(f"Trial: {trial}")
    print(f"\nMatches found: {len(matches)}")
    for match in matches:
        print(f"  - {match['patient_condition']} ↔ {match['trial_condition']}")
        print(f"    Score: {match['match_score']}, Type: {match['match_type']}")
