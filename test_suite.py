"""
Comprehensive test suite for Clinical Trial Matcher
Tests API endpoints, matching algorithm, and database queries
"""
import sys
import requests
import json
from time import time

BASE_URL = "http://localhost:5000"
session = requests.Session()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"     {details}")

def test_health_check():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200 and response.json()['status'] == 'healthy'
        print_test("Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_login(username="sarah.chen", password="demo123"):
    """Test login functionality"""
    try:
        response = session.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        passed = response.status_code == 200 and data['success']
        print_test(f"Login ({username})", passed, f"User ID: {data.get('user', {}).get('id')}")
        return passed
    except Exception as e:
        print_test(f"Login ({username})", False, str(e))
        return False

def test_invalid_login():
    """Test invalid login"""
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "invalid", "password": "wrong"}
        )
        passed = response.status_code == 401
        print_test("Invalid Login (should fail)", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Invalid Login", False, str(e))
        return False

def test_get_patient_profile():
    """Test getting patient profile"""
    try:
        response = session.get(f"{BASE_URL}/api/patient/me")
        data = response.json()
        passed = response.status_code == 200 and 'name' in data
        print_test("Get Patient Profile", passed, f"Name: {data.get('name')}, Conditions: {data.get('conditions')}")
        return passed, data
    except Exception as e:
        print_test("Get Patient Profile", False, str(e))
        return False, None

def test_get_matches(patient_id, max_distance=50):
    """Test matching algorithm"""
    try:
        start_time = time()
        response = session.get(f"{BASE_URL}/api/matches/{patient_id}?max_distance={max_distance}")
        elapsed = (time() - start_time) * 1000
        
        data = response.json()
        match_count = len(data.get('matches', []))
        passed = response.status_code == 200 and match_count > 0
        
        print_test(
            f"Get Matches (distance={max_distance}mi)", 
            passed, 
            f"Found {match_count} matches in {elapsed:.0f}ms"
        )
        return passed, data, elapsed
    except Exception as e:
        print_test("Get Matches", False, str(e))
        return False, None, 0

def test_match_filters(patient_id):
    """Test match filtering"""
    try:
        # Test distance filter
        response = session.get(f"{BASE_URL}/api/matches/{patient_id}?max_distance=10")
        matches_10mi = len(response.json()['matches'])
        
        response = session.get(f"{BASE_URL}/api/matches/{patient_id}?max_distance=100")
        matches_100mi = len(response.json()['matches'])
        
        passed = matches_100mi >= matches_10mi
        print_test(
            "Distance Filter", 
            passed, 
            f"10mi: {matches_10mi}, 100mi: {matches_100mi}"
        )
        
        # Test phase filter
        response = session.get(f"{BASE_URL}/api/matches/{patient_id}?phase=PHASE3")
        phase3_matches = len(response.json()['matches'])
        print_test(
            "Phase Filter", 
            True, 
            f"Phase 3 trials: {phase3_matches}"
        )
        
        return passed
    except Exception as e:
        print_test("Match Filters", False, str(e))
        return False

def test_trial_details(trial_id=1):
    """Test getting trial details"""
    try:
        response = requests.get(f"{BASE_URL}/api/trials/{trial_id}")
        data = response.json()
        passed = response.status_code == 200 and 'nct_id' in data
        print_test("Get Trial Details", passed, f"NCT ID: {data.get('nct_id')}")
        return passed
    except Exception as e:
        print_test("Get Trial Details", False, str(e))
        return False

def test_search_trials():
    """Test trial search"""
    try:
        response = requests.get(f"{BASE_URL}/api/trials/search?q=diabetes&limit=10")
        data = response.json()
        passed = response.status_code == 200 and len(data['results']) > 0
        print_test("Search Trials", passed, f"Found {len(data['results'])} results for 'diabetes'")
        return passed
    except Exception as e:
        print_test("Search Trials", False, str(e))
        return False

def test_demo_patients():
    """Test demo patients endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/demo/patients")
        data = response.json()
        passed = response.status_code == 200 and len(data['patients']) == 5
        print_test("Get Demo Patients", passed, f"Found {len(data['patients'])} patients")
        return passed
    except Exception as e:
        print_test("Get Demo Patients", False, str(e))
        return False

def test_logout():
    """Test logout"""
    try:
        response = session.post(f"{BASE_URL}/logout")
        data = response.json()
        passed = response.status_code == 200 and data['success']
        print_test("Logout", passed)
        return passed
    except Exception as e:
        print_test("Logout", False, str(e))
        return False

def test_all_patients():
    """Test matching for all sample patients"""
    patients = [
        ("sarah.chen", "Breast Cancer"),
        ("john.smith", "Diabetes, Hypertension"),
        ("maria.garcia", "COPD, Heart Disease"),
        ("david.lee", "Depression, Anxiety"),
        ("emily.brown", "Multiple Sclerosis")
    ]
    
    print(f"\n{Colors.BLUE}Testing all sample patients...{Colors.END}")
    
    for username, conditions in patients:
        test_login(username)
        passed, patient = test_get_patient_profile()
        if passed:
            test_get_matches(patient['id'])
    
    return True

def performance_test():
    """Test system performance"""
    print(f"\n{Colors.BLUE}Performance Testing...{Colors.END}")
    
    test_login()
    passed, patient = test_get_patient_profile()
    
    if not passed:
        return False
    
    # Test multiple distance filters
    distances = [10, 25, 50, 100]
    total_time = 0
    
    for dist in distances:
        passed, data, elapsed = test_get_matches(patient['id'], dist)
        total_time += elapsed
    
    avg_time = total_time / len(distances)
    performance_ok = avg_time < 2000  # Should be under 2 seconds
    
    print_test(
        "Performance Test", 
        performance_ok, 
        f"Avg response time: {avg_time:.0f}ms (target: <2000ms)"
    )
    
    return performance_ok

def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Clinical Trial Matcher - Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    results = []
    
    # Basic functionality tests
    print(f"{Colors.YELLOW}Basic Functionality Tests:{Colors.END}")
    results.append(test_health_check())
    results.append(test_invalid_login())
    results.append(test_login())
    results.append(test_get_patient_profile()[0])
    results.append(test_demo_patients())
    
    # Matching tests
    print(f"\n{Colors.YELLOW}Matching Engine Tests:{Colors.END}")
    passed, patient = test_get_patient_profile()
    if passed:
        results.append(test_get_matches(patient['id'])[0])
        results.append(test_match_filters(patient['id']))
    
    # Trial data tests
    print(f"\n{Colors.YELLOW}Trial Data Tests:{Colors.END}")
    results.append(test_trial_details())
    results.append(test_search_trials())
    
    # Multi-patient tests
    test_all_patients()
    
    # Performance tests
    results.append(performance_test())
    
    # Logout test
    print(f"\n{Colors.YELLOW}Cleanup:{Colors.END}")
    results.append(test_logout())
    
    # Summary
    passed_count = sum(results)
    total_count = len(results)
    success_rate = (passed_count / total_count) * 100
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary:{Colors.END}")
    print(f"  Total Tests: {total_count}")
    print(f"  Passed: {Colors.GREEN}{passed_count}{Colors.END}")
    print(f"  Failed: {Colors.RED}{total_count - passed_count}{Colors.END}")
    print(f"  Success Rate: {Colors.GREEN if success_rate == 100 else Colors.YELLOW}{success_rate:.1f}%{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if success_rate == 100:
        print(f"{Colors.GREEN}🎉 All tests passed! System is production-ready.{Colors.END}\n")
    elif success_rate >= 80:
        print(f"{Colors.YELLOW}⚠️  Most tests passed, but some issues need attention.{Colors.END}\n")
    else:
        print(f"{Colors.RED}❌ Multiple test failures. System needs fixes.{Colors.END}\n")
    
    return success_rate == 100

if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite error: {e}{Colors.END}")
        sys.exit(1)
