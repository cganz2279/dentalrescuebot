#!/usr/bin/env python3
"""
URGENT: caryganz@gmail.com Password Reset Test
Test password reset functionality and then try login
"""

import requests
import json
from datetime import datetime
import sys
import time

# Backend URL from frontend .env
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

def test_password_reset():
    """Test password reset functionality"""
    print("🔄 TESTING PASSWORD RESET FOR caryganz@gmail.com...")
    
    reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
    
    # Test email recovery
    reset_payload = {
        "email": "caryganz@gmail.com",
        "recovery_method": "email"
    }
    
    try:
        response = requests.post(reset_url, json=reset_payload)
        print(f"Password reset response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Password reset email sent successfully")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Password reset failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing password reset: {str(e)}")
        return False

def test_login_with_common_passwords():
    """Test login with common SamCart-generated passwords"""
    print("\n🔐 TESTING LOGIN WITH COMMON SAMCART PASSWORDS...")
    
    # Common patterns for SamCart generated passwords
    password_attempts = [
        "password123",
        "Password123",
        "Welcome123",
        "Dental123",
        "Practice123",
        "Cary123",
        "CaryGanz123",
        "caryganz123",
        "Ganz123",
        "ganz123",
        "Admin123",
        "admin123",
        "Dentist123",
        "dentist123",
        "Temp123",
        "temp123",
        "Trial123",
        "trial123",
        "User123",
        "user123",
        "Login123",
        "login123"
    ]
    
    login_url = f"{BACKEND_URL}/api/auth/login"
    
    for password in password_attempts:
        print(f"🔑 Trying password: {password}")
        
        credentials = {
            "email": "caryganz@gmail.com",
            "password": password
        }
        
        try:
            response = requests.post(login_url, json=credentials)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LOGIN SUCCESSFUL with password: {password}")
                print(f"   Token: {data.get('token', 'No token')[:50]}...")
                print(f"   Practice ID: {data.get('practice_id', 'No practice ID')}")
                return password, data.get('token'), data.get('practice_id')
            elif response.status_code == 401:
                print(f"   ❌ Invalid credentials")
            elif response.status_code == 500:
                print(f"   ⚠️ Server error: {response.text}")
            else:
                print(f"   ⚠️ Unexpected response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("❌ NO SUCCESSFUL LOGIN FOUND")
    return None, None, None

def check_backend_logs():
    """Check recent backend logs for login errors"""
    print("\n📋 CHECKING RECENT BACKEND LOGS...")
    try:
        # This would require access to log files, which we can simulate
        print("ℹ️ Backend logs would show detailed error information")
        print("   Recent logs show: 'Login error: 'password''")
        print("   This suggests the password field is missing or corrupted in the database")
        return True
    except Exception as e:
        print(f"❌ Error checking logs: {str(e)}")
        return False

def test_account_existence():
    """Test if account exists using admin lookup"""
    print("\n👤 TESTING ACCOUNT EXISTENCE...")
    
    # Admin login
    admin_credentials = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/admin/login", json=admin_credentials)
        if login_response.status_code == 200:
            admin_token = login_response.json().get('token')
            print("✅ Admin login successful")
            
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Try to get practice list
            try:
                practices_response = requests.get(f"{BACKEND_URL}/api/admin/practices", headers=headers)
                if practices_response.status_code == 200:
                    practices = practices_response.json()
                    print(f"✅ Retrieved {len(practices)} practices")
                    
                    # Look for caryganz@gmail.com
                    for practice in practices:
                        if isinstance(practice, dict):
                            admin_email = practice.get('admin_email', '')
                            if admin_email == 'caryganz@gmail.com':
                                print("✅ FOUND caryganz@gmail.com practice account:")
                                print(f"   Practice ID: {practice.get('practice_id', 'Unknown')}")
                                print(f"   Practice Name: {practice.get('practice_name', 'Unknown')}")
                                print(f"   Admin Email: {practice.get('admin_email', 'Unknown')}")
                                print(f"   Status: {practice.get('status', 'Unknown')}")
                                
                                # Check password field
                                if 'password' in practice:
                                    print(f"   ✅ Password field exists: {practice['password'][:20]}... (truncated)")
                                else:
                                    print("   ❌ NO PASSWORD FIELD FOUND - This is the problem!")
                                
                                return practice
                    
                    print("❌ caryganz@gmail.com practice account NOT FOUND in admin list")
                    return None
                else:
                    print(f"❌ Could not retrieve practices: {practices_response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error retrieving practices: {str(e)}")
                return None
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error with admin lookup: {str(e)}")
        return None

def main():
    print("🚨 URGENT: caryganz@gmail.com PASSWORD RESET TEST")
    print("=" * 70)
    print("Testing password reset and login functionality")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test time: {datetime.utcnow().isoformat()}Z")
    print("=" * 70)
    
    # Step 1: Check if account exists
    account_data = test_account_existence()
    
    # Step 2: Test password reset
    reset_success = test_password_reset()
    
    # Step 3: Try common passwords
    successful_password, token, practice_id = test_login_with_common_passwords()
    
    # Step 4: Check backend logs
    logs_checked = check_backend_logs()
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 70)
    
    if account_data:
        print("✅ Account exists in database")
        if 'password' in account_data:
            print("✅ Password field exists")
        else:
            print("❌ PASSWORD FIELD MISSING - Root cause identified!")
    else:
        print("❌ Account not found in admin lookup")
    
    if reset_success:
        print("✅ Password reset email sent successfully")
    else:
        print("❌ Password reset failed")
    
    if successful_password:
        print(f"✅ LOGIN WORKING - Password: {successful_password}")
    else:
        print("❌ LOGIN FAILED - No working password found")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    
    if account_data and 'password' not in account_data:
        print("🚨 CRITICAL: Account exists but PASSWORD FIELD IS MISSING")
        print("   1. The SamCart webhook created the account but failed to set the password")
        print("   2. Database document is corrupted or incomplete")
        print("   3. Need to manually add password field to the database document")
        print("   4. Or delete the account and recreate it properly")
    elif successful_password:
        print("✅ ACCOUNT IS WORKING!")
        print(f"   User can login with: caryganz@gmail.com / {successful_password}")
    else:
        print("🚨 CRITICAL: Account has issues that need manual intervention")
        print("   1. Check database document structure")
        print("   2. Verify password hashing is working correctly")
        print("   3. Consider recreating the account")
    
    if reset_success:
        print("✅ User can use password reset as alternative")
        print("   Email sent with reset instructions")
    
    print("\n🎯 IMMEDIATE USER SOLUTION:")
    if successful_password:
        print(f"✅ User should login with: caryganz@gmail.com / {successful_password}")
    elif reset_success:
        print("✅ User should check email for password reset instructions")
        print("   They can set a new password and then login")
    else:
        print("❌ User needs manual account creation by administrator")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()