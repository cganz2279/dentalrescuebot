#!/usr/bin/env python3
"""
Login Functionality Test
Testing the login endpoint and authentication system for user cganz2279@gmail.com
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BACKEND_URL = "https://postopcare-1.preview.emergentagent.com/api"

# Test credentials
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def test_login_endpoint_direct():
    """Test 1: Direct login endpoint test with curl-like request"""
    print("🔍 TEST 1: Testing login endpoint directly...")
    
    try:
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"   Making POST request to: {BACKEND_URL}/auth/login")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Password: {'*' * len(TEST_PASSWORD)}")
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LOGIN SUCCESS: Status 200")
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for JWT token (could be 'token' or 'access_token')
            token = data.get('token') or data.get('access_token')
            if token:
                print(f"   ✅ JWT Token received: {token[:50]}...")
                return True, token, data
            else:
                print(f"   ❌ No token in response")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False, None, data
        else:
            print(f"   ❌ LOGIN FAILED: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error response (text): {response.text}")
            return False, None, None
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, None, None

def test_authentication_service_health():
    """Test 2: Check if authentication service is running properly"""
    print("\n🔍 TEST 2: Testing authentication service health...")
    
    try:
        # Test basic API health
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"   API Root Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Backend API is responding")
        else:
            print("   ❌ Backend API not responding properly")
            return False
        
        # Test auth endpoint availability
        response = requests.options(f"{BACKEND_URL}/auth/login", timeout=10)
        print(f"   Auth endpoint OPTIONS: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print("   ✅ Auth endpoint is available")
            return True
        else:
            print("   ❌ Auth endpoint not available")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_jwt_token_validation(token: str):
    """Test 3: Verify JWT token is working"""
    print("\n🔍 TEST 3: Testing JWT token validation...")
    
    if not token:
        print("   ❌ No token provided for validation")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test a protected endpoint
        response = requests.get(
            f"{BACKEND_URL}/practice/dashboard",
            headers=headers,
            timeout=30
        )
        
        print(f"   Protected endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ JWT token is valid and working")
            data = response.json()
            print(f"   Practice data received: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
            return True
        elif response.status_code == 401:
            print("   ❌ JWT token is invalid or expired")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error text: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_failed_login_attempts():
    """Test 4: Test error handling with wrong credentials"""
    print("\n🔍 TEST 4: Testing failed login attempts...")
    
    test_cases = [
        {"email": TEST_EMAIL, "password": "wrongpassword", "case": "Wrong password"},
        {"email": "wrong@email.com", "password": TEST_PASSWORD, "case": "Wrong email"},
        {"email": "", "password": TEST_PASSWORD, "case": "Empty email"},
        {"email": TEST_EMAIL, "password": "", "case": "Empty password"}
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"   Testing: {test_case['case']}")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": test_case["email"], "password": test_case["password"]},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"     Status: {response.status_code}")
            
            if response.status_code in [400, 401, 422]:
                print(f"     ✅ Correctly rejected with status {response.status_code}")
            else:
                print(f"     ❌ Unexpected status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"     ❌ ERROR: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("   ✅ Error handling is working correctly")
    else:
        print("   ❌ Some error handling issues found")
    
    return all_passed

def test_user_account_status():
    """Test 5: Check user account status in database (indirect test)"""
    print("\n🔍 TEST 5: Testing user account status...")
    
    # We can't directly access the database, but we can infer account status
    # from login attempts and error messages
    
    try:
        # Try login with correct credentials
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Login attempt status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Account is ACTIVE and accessible")
            
            # Check if user data is returned
            if 'user' in data:
                user_data = data['user']
                print(f"   User ID: {user_data.get('id', 'N/A')}")
                print(f"   Email: {user_data.get('email', 'N/A')}")
                print(f"   Practice: {user_data.get('practice_name', 'N/A')}")
            
            return True
            
        elif response.status_code == 401:
            error_data = response.json()
            error_msg = error_data.get('detail', 'Unknown error')
            
            if 'disabled' in error_msg.lower() or 'inactive' in error_msg.lower():
                print("   ❌ Account appears to be DISABLED or INACTIVE")
            elif 'password' in error_msg.lower():
                print("   ❌ Password appears to be incorrect")
            elif 'email' in error_msg.lower() or 'user' in error_msg.lower():
                print("   ❌ User account may not exist")
            else:
                print(f"   ❌ Authentication failed: {error_msg}")
            
            return False
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def test_session_persistence():
    """Test 6: Test if login sessions persist correctly"""
    print("\n🔍 TEST 6: Testing session persistence...")
    
    try:
        # First login
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if login_response.status_code != 200:
            print("   ❌ Initial login failed")
            return False
        
        token = login_response.json().get('token') or login_response.json().get('access_token')
        if not token:
            print("   ❌ No token received")
            return False
        
        print("   ✅ Initial login successful")
        
        # Wait a moment
        time.sleep(2)
        
        # Test token after delay
        headers = {"Authorization": f"Bearer {token}"}
        test_response = requests.get(
            f"{BACKEND_URL}/practice/dashboard",
            headers=headers,
            timeout=30
        )
        
        if test_response.status_code == 200:
            print("   ✅ Session persists after delay")
            return True
        else:
            print(f"   ❌ Session lost after delay: {test_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def run_login_tests():
    """Run all login functionality tests"""
    print("🚀 LOGIN FUNCTIONALITY TEST")
    print("=" * 60)
    print(f"Testing login for: {TEST_EMAIL}")
    print("=" * 60)
    
    # Test 1: Direct login
    login_success, token, login_data = test_login_endpoint_direct()
    
    # Test 2: Service health
    service_health = test_authentication_service_health()
    
    # Test 3: JWT validation (only if we have a token)
    jwt_valid = False
    if token:
        jwt_valid = test_jwt_token_validation(token)
    
    # Test 4: Error handling
    error_handling = test_failed_login_attempts()
    
    # Test 5: Account status
    account_status = test_user_account_status()
    
    # Test 6: Session persistence
    session_persistence = test_session_persistence()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 LOGIN TEST RESULTS:")
    print("=" * 60)
    
    all_tests = [
        ("Direct Login Endpoint", login_success),
        ("Authentication Service Health", service_health),
        ("JWT Token Validation", jwt_valid),
        ("Error Handling", error_handling),
        ("User Account Status", account_status),
        ("Session Persistence", session_persistence)
    ]
    
    passed_tests = 0
    critical_failures = []
    
    for test_name, passed in all_tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if passed:
            passed_tests += 1
        else:
            if test_name in ["Direct Login Endpoint", "User Account Status"]:
                critical_failures.append(test_name)
    
    print(f"\n📈 OVERALL RESULT: {passed_tests}/{len(all_tests)} tests passed")
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES: {', '.join(critical_failures)}")
        print("   These failures indicate the login system is not working properly.")
    
    if passed_tests == len(all_tests):
        print("🎉 ALL TESTS PASSED: Login system is working correctly!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED: Login system has issues")
        return False

if __name__ == "__main__":
    success = run_login_tests()
    exit(0 if success else 1)