#!/usr/bin/env python3
"""
URGENT DATA ACCESS TEST
Testing production backend at https://dentist-portal-3.emergent.host/api
User reports no data despite correct .env configuration
"""

import requests
import json
import sys
from datetime import datetime

# Production backend URL from .env file
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_result(success, message, data=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data:
        print(f"📊 Data: {json.dumps(data, indent=2)}")

def test_backend_connectivity():
    """Test 1: Backend Connectivity"""
    print_test_header("BACKEND CONNECTIVITY TEST")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        
        if response.status_code == 200:
            print_result(True, f"Backend is accessible at {BACKEND_URL}")
            print_result(True, f"Response: {response.json()}")
            return True
        else:
            print_result(False, f"Backend returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result(False, f"Cannot connect to {BACKEND_URL} - Connection refused")
        return False
    except requests.exceptions.Timeout:
        print_result(False, f"Connection to {BACKEND_URL} timed out")
        return False
    except Exception as e:
        print_result(False, f"Unexpected error: {str(e)}")
        return False

def test_authentication():
    """Test 2: Authentication Test"""
    print_test_header("AUTHENTICATION TEST")
    
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user_info = data.get('user', {})
            practice_info = data.get('practice', {})
            
            print_result(True, f"Authentication successful for {TEST_EMAIL}")
            print_result(True, f"User Role: {user_info.get('role', 'Unknown')}")
            print_result(True, f"Practice: {practice_info.get('name', 'Unknown')}")
            
            return token, user_info, practice_info
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response.content else f"Status {response.status_code}"
            print_result(False, f"Authentication failed: {error_msg}")
            return None, None, None
            
    except Exception as e:
        print_result(False, f"Authentication error: {str(e)}")
        return None, None, None

def test_dashboard_api(token):
    """Test 3: Dashboard API Test"""
    print_test_header("DASHBOARD API TEST")
    
    if not token:
        print_result(False, "No authentication token available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/practice/dashboard",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            practice_data = data.get('data', {})
            
            print_result(True, "Dashboard API accessible")
            print_result(True, f"Practice Name: {practice_data.get('name', 'Not set')}")
            print_result(True, f"Office Hours: {practice_data.get('officeHours', 'Not set')}")
            print_result(True, f"Emergency Contact: {practice_data.get('emergencyContact', 'Not set')}")
            
            return practice_data
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response.content else f"Status {response.status_code}"
            print_result(False, f"Dashboard API failed: {error_msg}")
            return None
            
    except Exception as e:
        print_result(False, f"Dashboard API error: {str(e)}")
        return None

def test_procedures_count():
    """Test 4: Procedures Count Test"""
    print_test_header("PROCEDURES COUNT TEST")
    
    try:
        # Test public procedures endpoint
        response = requests.get(
            f"{BACKEND_URL}/public/procedures",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            procedures = data.get('data', [])
            count = len(procedures)
            
            print_result(True, f"Procedures endpoint accessible")
            print_result(True, f"Total procedures available: {count}")
            
            if count > 0:
                # Show sample procedures
                sample_procedures = procedures[:3]
                for i, proc in enumerate(sample_procedures, 1):
                    print(f"   {i}. {proc.get('name', 'Unknown')} ({proc.get('specialtyName', 'Unknown')})")
            
            return count
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response.content else f"Status {response.status_code}"
            print_result(False, f"Procedures API failed: {error_msg}")
            return 0
            
    except Exception as e:
        print_result(False, f"Procedures API error: {str(e)}")
        return 0

def test_patients_count(token):
    """Test 5: Patients Count Test"""
    print_test_header("PATIENTS COUNT TEST")
    
    if not token:
        print_result(False, "No authentication token available")
        return 0
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/practice/patients",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            patients = data.get('data', [])
            count = len(patients)
            
            print_result(True, f"Patients endpoint accessible")
            print_result(True, f"Total patients: {count}")
            
            if count > 0:
                # Show sample patients
                sample_patients = patients[:3]
                for i, patient in enumerate(sample_patients, 1):
                    print(f"   {i}. {patient.get('firstName', 'Unknown')} {patient.get('lastName', 'Unknown')}")
            
            return count
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response.content else f"Status {response.status_code}"
            print_result(False, f"Patients API failed: {error_msg}")
            return 0
            
    except Exception as e:
        print_result(False, f"Patients API error: {str(e)}")
        return 0

def main():
    """Run all urgent data access tests"""
    print(f"🚨 URGENT DATA ACCESS TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing production backend: {BACKEND_URL}")
    print(f"User credentials: {TEST_EMAIL}/password123")
    
    # Test results tracking
    results = {
        "backend_accessible": False,
        "authentication_working": False,
        "dashboard_accessible": False,
        "procedures_count": 0,
        "patients_count": 0,
        "token": None,
        "practice_data": None
    }
    
    # Test 1: Backend Connectivity
    results["backend_accessible"] = test_backend_connectivity()
    
    if not results["backend_accessible"]:
        print(f"\n🚨 CRITICAL: Backend server is DOWN or unreachable at {BACKEND_URL}")
        print("This explains why user sees no data - the backend is not responding!")
        return results
    
    # Test 2: Authentication
    token, user_info, practice_info = test_authentication()
    results["authentication_working"] = token is not None
    results["token"] = token
    
    if not results["authentication_working"]:
        print(f"\n🚨 CRITICAL: Authentication FAILED for {TEST_EMAIL}")
        print("User cannot login - this explains the no data issue!")
        return results
    
    # Test 3: Dashboard API
    practice_data = test_dashboard_api(token)
    results["dashboard_accessible"] = practice_data is not None
    results["practice_data"] = practice_data
    
    # Test 4: Procedures Count
    results["procedures_count"] = test_procedures_count()
    
    # Test 5: Patients Count
    results["patients_count"] = test_patients_count(token)
    
    # Final Summary
    print(f"\n{'='*60}")
    print("🎯 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    
    print(f"✅ Backend Accessible: {'YES' if results['backend_accessible'] else 'NO'}")
    print(f"✅ Authentication Working: {'YES' if results['authentication_working'] else 'NO'}")
    print(f"✅ Dashboard API Working: {'YES' if results['dashboard_accessible'] else 'NO'}")
    print(f"📊 Procedures Available: {results['procedures_count']}")
    print(f"👥 Patients Available: {results['patients_count']}")
    
    # Root cause analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    
    if not results["backend_accessible"]:
        print("❌ BACKEND SERVER IS DOWN - This is the root cause of no data!")
    elif not results["authentication_working"]:
        print("❌ AUTHENTICATION FAILURE - User cannot login to access data!")
    elif results["procedures_count"] == 0:
        print("❌ NO PROCEDURES IN DATABASE - Database may be empty!")
    elif results["patients_count"] == 0:
        print("⚠️  NO PATIENTS - This may be expected for new practice")
    else:
        print("✅ ALL SYSTEMS OPERATIONAL - Data should be visible to user")
    
    return results

if __name__ == "__main__":
    main()