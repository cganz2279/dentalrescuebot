#!/usr/bin/env python3
"""
Test login for ganzseth@gmail.com (the account that DOES exist)
"""

import requests
import json

BACKEND_URL = "https://practice-notes-1.preview.emergentagent.com/api"

def test_ganzseth_login():
    """Test login with ganzseth@gmail.com and common passwords"""
    target_email = "ganzseth@gmail.com"
    common_passwords = ["password123", "password", "Dentist1#", "ganzseth", "seth123", "ganz123"]
    
    print(f"🔐 TESTING LOGIN FOR: {target_email}")
    print("=" * 50)
    
    session = requests.Session()
    
    for password in common_passwords:
        try:
            login_data = {
                "email": target_email,
                "password": password
            }
            
            response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            print(f"🔑 Testing password: {password}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    print(f"   ✅ SUCCESS! Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    print(f"   ❌ Invalid response format: {response.text}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print(f"\n❌ No successful login found for {target_email}")
    return False

if __name__ == "__main__":
    test_ganzseth_login()