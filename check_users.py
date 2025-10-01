#!/usr/bin/env python3
"""
Check existing users in the database
"""

import requests
import json

BACKEND_URL = "https://dental-portal-debug.preview.emergentagent.com/api"

def test_admin_login_and_check_users():
    """Login as admin and check what users exist"""
    try:
        # Login as admin first
        login_data = {
            "email": "admin@smithdental.com",
            "password": "password123"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "token" in data:
                token = data["token"]
                print("✅ Admin login successful")
                
                # Try to get patients to see what users exist
                headers = {"Authorization": f"Bearer {token}"}
                patients_response = requests.get(f"{BACKEND_URL}/practice/patients", headers=headers)
                
                if patients_response.status_code == 200:
                    patients_data = patients_response.json()
                    if patients_data.get("success"):
                        patients = patients_data.get("data", [])
                        print(f"\n📋 Found {len(patients)} patients in Smith Dental Practice:")
                        for patient in patients:
                            email = patient.get("email", "")
                            name = f"{patient.get('firstName', '')} {patient.get('lastName', '')}"
                            print(f"   - {name} ({email})")
                
                return True
            else:
                print("❌ Admin login failed - Invalid response")
                return False
        else:
            print(f"❌ Admin login failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_possible_jones_passwords():
    """Test different possible passwords for jones@gmail.com"""
    possible_passwords = [
        "password123",
        "jones123",
        "Password123",
        "password",
        "123456"
    ]
    
    print(f"\n🔍 Testing possible passwords for jones@gmail.com:")
    
    for password in possible_passwords:
        try:
            login_data = {
                "email": "jones@gmail.com",
                "password": password
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    name = f"{user_info.get('firstName', '')} {user_info.get('lastName', '')}"
                    print(f"✅ SUCCESS with password: {password}")
                    print(f"   User: {name} ({user_info.get('role', '')})")
                    return True
            else:
                print(f"❌ Failed with password: {password}")
                
        except Exception as e:
            print(f"❌ Exception with password {password}: {str(e)}")
    
    return False

def main():
    """Main function"""
    print("🔍 Checking Users in Database")
    print("=" * 50)
    
    # Check what users exist
    test_admin_login_and_check_users()
    
    # Try different passwords for jones@gmail.com
    test_possible_jones_passwords()

if __name__ == "__main__":
    main()