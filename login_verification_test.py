#!/usr/bin/env python3
"""
Login Verification Test
Verify that newly registered users can login successfully
"""

import requests
import json
import time

BACKEND_URL = "https://dental-portal-fix-1.preview.emergentagent.com/api"

def test_login_after_registration():
    """Test login functionality with a newly registered user"""
    try:
        # Create a new user first
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Login Test Practice",
            "email": f"login.test.{timestamp}@logintest.com",
            "phone": "(555) 555-5555",
            "website": "www.logintest.com",
            "adminFirstName": "Login",
            "adminLastName": "Tester",
            "adminPassword": "LoginTest123",
            "street": "123 Login St",
            "city": "Login City",
            "state": "LT",
            "zipCode": "12345"
        }
        
        print("🧪 Testing Login After Registration")
        print(f"   Registering user: {registration_data['email']}")
        
        # Register the user
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code != 200:
            print(f"❌ FAIL: Registration failed: {response.status_code}")
            return False
            
        reg_data = response.json()
        if not reg_data.get('success'):
            print(f"❌ FAIL: Registration not successful: {reg_data}")
            return False
            
        print("✅ Registration successful")
        
        # Now try to login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["adminPassword"]
        }
        
        print(f"   Attempting login with: {login_data['email']}")
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get("success"):
                user_info = login_result.get("user", {})
                practice_info = login_result.get("practice", {})
                
                print("✅ PASS: Login successful after registration")
                print(f"   User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                print(f"   Practice: {practice_info.get('name', 'N/A')}")
                print(f"   Token received: {'Yes' if login_result.get('token') else 'No'}")
                
                # Verify user details match registration
                if (user_info.get('firstName') == registration_data['adminFirstName'] and
                    user_info.get('lastName') == registration_data['adminLastName'] and
                    user_info.get('email') == registration_data['email'] and
                    user_info.get('role') == 'practice_admin'):
                    
                    print("✅ User details match registration data")
                    return True
                else:
                    print("❌ FAIL: User details don't match registration data")
                    return False
            else:
                print(f"❌ FAIL: Login response not successful: {login_result}")
                return False
        else:
            print(f"❌ FAIL: Login failed with status {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during login test: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔐 LOGIN VERIFICATION TESTING")
    print("=" * 50)
    
    success = test_login_after_registration()
    
    if success:
        print("\n🎉 LOGIN VERIFICATION PASSED!")
        print("Registration and login functionality working end-to-end")
    else:
        print("\n⚠️ LOGIN VERIFICATION FAILED!")
        print("There may be an issue with the login system")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)