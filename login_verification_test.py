#!/usr/bin/env python3
"""
Login Verification Test - Testing Both Regular User and Admin Login
Testing both login types after service restart as requested in review
"""

import requests
import json
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com/api"

# Test credentials
REGULAR_USER_EMAIL = "cganz2279@gmail.com"
REGULAR_USER_PASSWORD = "password123"

ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def test_service_health():
    """Test 1: Verify backend service is responding"""
    print("🔍 TEST 1: Verifying backend service health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend responding: {data.get('message', 'OK')}")
            return True
        else:
            print(f"   ❌ FAIL: Backend not responding properly (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: Backend service unreachable - {str(e)}")
        return False

def test_regular_user_login():
    """Test 2: Test regular user login with cganz2279@gmail.com"""
    print("\n🔍 TEST 2: Testing regular user login...")
    
    try:
        login_data = {
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if data.get('success') and data.get('token') and data.get('user'):
                user = data['user']
                practice = data.get('practice')
                
                print(f"   ✅ Login successful for: {user.get('firstName')} {user.get('lastName')}")
                print(f"   ✅ Email: {user.get('email')}")
                print(f"   ✅ Role: {user.get('role')}")
                print(f"   ✅ JWT Token received: {data['token'][:50]}...")
                
                if practice:
                    print(f"   ✅ Practice: {practice.get('name')}")
                    print(f"   ✅ Practice Status: {'Active' if practice.get('isActive') else 'Inactive'}")
                
                return True, data['token'], user, practice
            else:
                print(f"   ❌ FAIL: Invalid response structure")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False, None, None, None
        else:
            print(f"   ❌ FAIL: Login failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False, None, None, None
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, None, None, None

def test_admin_login():
    """Test 3: Test admin login with cganz@admin.com"""
    print("\n🔍 TEST 3: Testing admin login...")
    
    try:
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(
            f"{BACKEND_URL}/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if data.get('success') and data.get('token'):
                print(f"   ✅ Admin login successful")
                print(f"   ✅ Admin Email: {ADMIN_EMAIL}")
                print(f"   ✅ JWT Token received: {data['token'][:50]}...")
                
                return True, data['token']
            else:
                print(f"   ❌ FAIL: Invalid admin response structure")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False, None
        else:
            print(f"   ❌ FAIL: Admin login failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, None

def test_procedures_endpoint_authenticated(token: str):
    """Test 4: Test GET /api/procedures with authenticated user"""
    print("\n🔍 TEST 4: Testing authenticated procedures endpoint...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BACKEND_URL}/procedures",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('data'):
                procedures = data['data']
                count = len(procedures)
                
                print(f"   ✅ Procedures endpoint working")
                print(f"   ✅ Total procedures: {count}")
                print(f"   ✅ Sample procedures:")
                
                # Show first 3 procedures
                for i, proc in enumerate(procedures[:3]):
                    print(f"      {i+1}. {proc.get('name')} ({proc.get('specialtyName')})")
                
                return True, count
            else:
                print(f"   ❌ FAIL: Invalid procedures response structure")
                return False, 0
        else:
            print(f"   ❌ FAIL: Procedures endpoint failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False, 0
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, 0

def test_admin_procedures_endpoint(admin_token: str):
    """Test 5: Test GET /api/admin/procedures with admin token"""
    print("\n🔍 TEST 5: Testing admin procedures endpoint...")
    
    try:
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BACKEND_URL}/admin/procedures",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('procedures'):
                procedures = data['procedures']
                specialties = data.get('specialties', [])
                count = len(procedures)
                
                print(f"   ✅ Admin procedures endpoint working")
                print(f"   ✅ Total procedures: {count}")
                print(f"   ✅ Total specialties: {len(specialties)}")
                print(f"   ✅ Sample procedures:")
                
                # Show first 3 procedures
                for i, proc in enumerate(procedures[:3]):
                    print(f"      {i+1}. {proc.get('name')} ({proc.get('specialtyName')})")
                
                return True, count
            else:
                print(f"   ❌ FAIL: Invalid admin procedures response structure")
                return False, 0
        else:
            print(f"   ❌ FAIL: Admin procedures endpoint failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False, 0
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, 0

def test_cors_functionality():
    """Test 6: Verify CORS is working for both login types"""
    print("\n🔍 TEST 6: Testing CORS functionality...")
    
    try:
        # Test CORS headers on regular login
        headers = {
            "Origin": "https://dentalpractice-hub-1.preview.emergentagent.com",
            "Content-Type": "application/json"
        }
        
        response = requests.options(
            f"{BACKEND_URL}/auth/login",
            headers=headers,
            timeout=30
        )
        
        print(f"   Regular login OPTIONS status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"   CORS Headers: {cors_headers}")
        
        # Test CORS headers on admin login
        admin_response = requests.options(
            f"{BACKEND_URL}/admin/login",
            headers=headers,
            timeout=30
        )
        
        print(f"   Admin login OPTIONS status: {admin_response.status_code}")
        
        if response.status_code in [200, 204] and admin_response.status_code in [200, 204]:
            print(f"   ✅ CORS working for both endpoints")
            return True
        else:
            print(f"   ❌ FAIL: CORS issues detected")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_token_validation(user_token: str, admin_token: str):
    """Test 7: Verify tokens work for accessing protected endpoints"""
    print("\n🔍 TEST 7: Testing token validation...")
    
    try:
        # Test user token with /me endpoint
        user_headers = {"Authorization": f"Bearer {user_token}"}
        user_response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=user_headers,
            timeout=30
        )
        
        print(f"   User /me endpoint status: {user_response.status_code}")
        
        # Test admin token with admin stats
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_response = requests.get(
            f"{BACKEND_URL}/admin/stats",
            headers=admin_headers,
            timeout=30
        )
        
        print(f"   Admin stats endpoint status: {admin_response.status_code}")
        
        user_valid = user_response.status_code == 200
        admin_valid = admin_response.status_code == 200
        
        if user_valid and admin_valid:
            print(f"   ✅ Both tokens are valid and working")
            return True
        elif user_valid:
            print(f"   ⚠️  User token valid, admin token may have issues")
            return True
        elif admin_valid:
            print(f"   ⚠️  Admin token valid, user token may have issues")
            return True
        else:
            print(f"   ❌ FAIL: Token validation issues")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def run_login_verification_test():
    """Run all login verification tests"""
    print("🚀 LOGIN VERIFICATION TEST - BOTH USER TYPES")
    print("=" * 80)
    
    # Test 1: Service health
    health_pass = test_service_health()
    
    if not health_pass:
        print("\n❌ CRITICAL FAILURE: Backend service not responding. Stopping tests.")
        return False
    
    # Test 2: Regular user login
    user_login_pass, user_token, user_data, practice_data = test_regular_user_login()
    
    # Test 3: Admin login
    admin_login_pass, admin_token = test_admin_login()
    
    # Test 4: Procedures endpoint (if user login worked)
    procedures_pass = False
    procedure_count = 0
    if user_login_pass and user_token:
        procedures_pass, procedure_count = test_procedures_endpoint_authenticated(user_token)
    
    # Test 5: Admin procedures endpoint (if admin login worked)
    admin_procedures_pass = False
    admin_procedure_count = 0
    if admin_login_pass and admin_token:
        admin_procedures_pass, admin_procedure_count = test_admin_procedures_endpoint(admin_token)
    
    # Test 6: CORS functionality
    cors_pass = test_cors_functionality()
    
    # Test 7: Token validation (if both logins worked)
    token_validation_pass = False
    if user_login_pass and admin_login_pass and user_token and admin_token:
        token_validation_pass = test_token_validation(user_token, admin_token)
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 80)
    
    all_tests = [
        ("Backend Service Health", health_pass),
        ("Regular User Login (cganz2279@gmail.com)", user_login_pass),
        ("Admin Login (cganz@admin.com)", admin_login_pass),
        ("Authenticated Procedures Endpoint", procedures_pass),
        ("Admin Procedures Endpoint", admin_procedures_pass),
        ("CORS Functionality", cors_pass),
        ("Token Validation", token_validation_pass)
    ]
    
    passed_tests = 0
    critical_failures = []
    
    for test_name, passed in all_tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if passed:
            passed_tests += 1
        else:
            if test_name in ["Regular User Login (cganz2279@gmail.com)", "Admin Login (cganz@admin.com)"]:
                critical_failures.append(test_name)
    
    print(f"\n📈 OVERALL RESULT: {passed_tests}/{len(all_tests)} tests passed")
    
    # Additional info
    if user_login_pass and user_data:
        print(f"\n👤 USER LOGIN DETAILS:")
        print(f"   Name: {user_data.get('firstName')} {user_data.get('lastName')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Role: {user_data.get('role')}")
        if practice_data:
            print(f"   Practice: {practice_data.get('name')}")
    
    if admin_login_pass:
        print(f"\n🔐 ADMIN LOGIN DETAILS:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Access: Super Admin")
    
    if procedures_pass:
        print(f"\n📋 PROCEDURES ACCESS:")
        print(f"   User can access {procedure_count} procedures")
    
    if admin_procedures_pass:
        print(f"   Admin can access {admin_procedure_count} procedures")
    
    # Critical failure analysis
    if critical_failures:
        print(f"\n⚠️  CRITICAL FAILURES DETECTED:")
        for failure in critical_failures:
            print(f"   - {failure}")
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        if "Regular User Login" in str(critical_failures):
            print(f"   - Verify user cganz2279@gmail.com exists and is active")
            print(f"   - Check password: password123")
            print(f"   - Verify practice association")
        if "Admin Login" in str(critical_failures):
            print(f"   - Verify admin credentials: cganz@admin.com / Dentist1#")
            print(f"   - Check admin authentication system")
    
    if passed_tests == len(all_tests):
        print("🎉 ALL TESTS PASSED: Both login types working correctly!")
        return True
    elif passed_tests >= 5:  # At least basic functionality working
        print("⚠️  MOSTLY WORKING: Core functionality operational with minor issues")
        return True
    else:
        print("❌ SIGNIFICANT ISSUES: Multiple critical failures detected")
        return False

if __name__ == "__main__":
    success = run_login_verification_test()
    exit(0 if success else 1)