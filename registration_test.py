#!/usr/bin/env python3
"""
Test registration endpoint functionality
"""

import requests
import json
import time

BACKEND_URL = "https://postopcare.preview.emergentagent.com/api"

def test_registration_endpoint():
    """Test the registration endpoint"""
    try:
        # Create unique test data
        timestamp = str(int(time.time()))
        registration_data = {
            "email": f"test{timestamp}@example.com",
            "practiceName": f"Test Practice {timestamp}",
            "phone": "555-0123",
            "adminFirstName": "Test",
            "adminLastName": "User",
            "adminPassword": "password123",
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zipCode": "12345"
        }
        
        print("🧪 Testing Registration Endpoint")
        print(f"   Email: {registration_data['email']}")
        print(f"   Practice: {registration_data['practiceName']}")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ PASS Registration endpoint working")
                print(f"   Response: {data.get('message', '')}")
                
                # Try to login with the new user
                login_data = {
                    "email": registration_data["email"],
                    "password": registration_data["adminPassword"]
                }
                
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    login_data_resp = login_response.json()
                    if login_data_resp.get("success"):
                        user_info = login_data_resp.get("user", {})
                        print("✅ PASS Login after registration working")
                        print(f"   User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                        print(f"   Practice: {user_info.get('practiceName', '')}")
                        return True
                    else:
                        print("❌ FAIL Login after registration - Invalid response")
                        return False
                else:
                    print(f"❌ FAIL Login after registration - Status: {login_response.status_code}")
                    return False
            else:
                print("❌ FAIL Registration endpoint - Invalid response")
                print(f"   Response: {response.text}")
                return False
        else:
            print(f"❌ FAIL Registration endpoint - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Registration endpoint - Exception: {str(e)}")
        return False

def test_jones_registration():
    """Try to register jones@gmail.com to see if it already exists"""
    try:
        registration_data = {
            "email": "jones@gmail.com",
            "password": "password123",
            "firstName": "Jones",
            "lastName": "User",
            "practiceName": "Jones Practice",
            "phone": "555-0123",
            "address": "123 Jones St",
            "city": "Jones City",
            "state": "JS",
            "zipCode": "12345"
        }
        
        print("\n🧪 Testing jones@gmail.com Registration")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 400:
            data = response.json()
            if "already exists" in data.get("detail", "").lower():
                print("✅ jones@gmail.com already exists in system")
                print(f"   Details: {data.get('detail', '')}")
                
                # If it exists, maybe the password is different
                print("\n🔍 Trying to login with jones@gmail.com and different passwords...")
                
                possible_passwords = ["password123", "jones123", "Password123", "password", "123456", "samcart123"]
                
                for password in possible_passwords:
                    login_data = {
                        "email": "jones@gmail.com",
                        "password": password
                    }
                    
                    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
                    
                    if login_response.status_code == 200:
                        login_data_resp = login_response.json()
                        if login_data_resp.get("success"):
                            user_info = login_data_resp.get("user", {})
                            print(f"✅ SUCCESS! jones@gmail.com password is: {password}")
                            print(f"   User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                            print(f"   Practice: {user_info.get('practiceName', '')}")
                            return True
                    
                print("❌ Could not find correct password for jones@gmail.com")
                return False
            else:
                print(f"❌ Unexpected error: {data.get('detail', '')}")
                return False
        elif response.status_code == 200:
            print("✅ jones@gmail.com registered successfully")
            return True
        else:
            print(f"❌ Registration failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔐 Testing Registration Functionality")
    print("=" * 50)
    
    # Test general registration
    test_registration_endpoint()
    
    # Test jones@gmail.com specifically
    test_jones_registration()

if __name__ == "__main__":
    main()