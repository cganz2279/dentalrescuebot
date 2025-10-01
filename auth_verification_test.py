#!/usr/bin/env python3
"""
Authentication Verification Test for Dental Application
Tests login with specific existing users mentioned in review request
"""

import requests
import json

BACKEND_URL = "https://dental-portal-debug.preview.emergentagent.com/api"

def test_user_login(email, password, expected_name=None):
    """Test login for a specific user"""
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "token" in data:
                user_info = data.get("user", {})
                name = f"{user_info.get('firstName', '')} {user_info.get('lastName', '')}"
                role = user_info.get('role', '')
                practice = user_info.get('practiceName', '')
                
                print(f"✅ PASS Login for {email}")
                print(f"   User: {name} ({role})")
                if practice:
                    print(f"   Practice: {practice}")
                return True, data["token"]
            else:
                print(f"❌ FAIL Login for {email} - Invalid response format")
                return False, None
        else:
            print(f"❌ FAIL Login for {email} - Status: {response.status_code}")
            if response.status_code == 401:
                print(f"   Details: Invalid credentials")
            else:
                print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ FAIL Login for {email} - Exception: {str(e)}")
        return False, None

def test_token_validation(token, email):
    """Test token validation by accessing protected endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/practice/dashboard", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                dashboard_data = data.get("data", {})
                practice_name = dashboard_data.get("practice", {}).get("name", "")
                patient_count = len(dashboard_data.get("patients", []))
                procedure_count = len(dashboard_data.get("recentProcedures", []))
                
                print(f"✅ PASS Token validation for {email}")
                print(f"   Dashboard loaded: {practice_name}")
                print(f"   Patients: {patient_count}, Recent procedures: {procedure_count}")
                return True
            else:
                print(f"❌ FAIL Token validation for {email} - Invalid response")
                return False
        else:
            print(f"❌ FAIL Token validation for {email} - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Token validation for {email} - Exception: {str(e)}")
        return False

def main():
    """Test authentication for specific users mentioned in review request"""
    print("🔐 Testing Authentication for Existing Users")
    print("=" * 60)
    
    # Test users mentioned in review request
    test_users = [
        ("admin@smithdental.com", "password123"),
        ("jones@gmail.com", "password123"),
        ("completenew@gmail.com", "password123")
    ]
    
    passed_logins = 0
    passed_tokens = 0
    total_users = len(test_users)
    
    for email, password in test_users:
        print(f"\n🧪 Testing user: {email}")
        success, token = test_user_login(email, password)
        
        if success:
            passed_logins += 1
            # Test token validation
            if test_token_validation(token, email):
                passed_tokens += 1
        
        print()  # Add spacing
    
    print("=" * 60)
    print(f"📊 Authentication Results:")
    print(f"   Login Tests: {passed_logins}/{total_users} passed")
    print(f"   Token Validation: {passed_tokens}/{total_users} passed")
    
    if passed_logins == total_users and passed_tokens == total_users:
        print("🎉 All authentication tests passed!")
        return True
    else:
        print("⚠️  Some authentication tests failed.")
        return False

if __name__ == "__main__":
    main()