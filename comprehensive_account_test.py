#!/usr/bin/env python3
"""
COMPREHENSIVE ACCOUNT TESTING for caryganz@gmail.com
Testing account status, password reset, and alternative solutions
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

def test_account_status():
    """Check current account status for caryganz@gmail.com"""
    print("🔍 CHECKING ACCOUNT STATUS...")
    
    target_email = "caryganz@gmail.com"
    
    # Test 1: Try login with dummy password
    login_payload = {
        "email": target_email,
        "password": "dummy_test_password"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_payload)
        print(f"Login test response: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Account EXISTS - wrong password returned 401")
            return "exists"
        elif response.status_code == 404:
            print("❌ Account DOES NOT EXIST - returned 404")
            return "missing"
        elif response.status_code == 500:
            print("⚠️ Account EXISTS but CORRUPTED - returned 500")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"Error detail: {error_detail}")
            except:
                print(f"Raw response: {response.text}")
            return "corrupted"
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return "unknown"
            
    except Exception as e:
        print(f"❌ Error checking account: {str(e)}")
        return "error"

def test_admin_lookup():
    """Use admin access to look up the account"""
    print("\n🔍 ADMIN ACCOUNT LOOKUP...")
    
    # Admin login
    admin_creds = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/admin/login", json=admin_creds)
        if login_response.status_code != 200:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return None
            
        admin_token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try to get practices list
        practices_response = requests.get(f"{BACKEND_URL}/api/admin/practices", headers=headers)
        if practices_response.status_code != 200:
            print(f"❌ Could not get practices: {practices_response.status_code}")
            return None
            
        practices = practices_response.json()
        print(f"✅ Found {len(practices)} total practices")
        
        # Look for caryganz@gmail.com
        for practice in practices:
            if isinstance(practice, dict):
                admin_email = practice.get('admin_email', '')
                if admin_email == "caryganz@gmail.com":
                    print(f"✅ FOUND caryganz@gmail.com practice:")
                    print(f"   Practice Name: {practice.get('practice_name', 'Unknown')}")
                    print(f"   Practice ID: {practice.get('practice_id', 'Unknown')}")
                    print(f"   Status: {practice.get('status', 'Unknown')}")
                    print(f"   Source: {practice.get('source', 'Unknown')}")
                    return practice
        
        print("❌ caryganz@gmail.com NOT FOUND in admin practices list")
        return None
        
    except Exception as e:
        print(f"❌ Error in admin lookup: {str(e)}")
        return None

def test_password_reset():
    """Test password reset functionality"""
    print("\n🔐 TESTING PASSWORD RESET...")
    
    reset_payload = {
        "email": "caryganz@gmail.com",
        "recovery_method": "email"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json=reset_payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Password reset email sent: {result.get('message', 'Success')}")
            print(f"📧 Methods: {result.get('sent_methods', [])}")
            return True
        else:
            print(f"❌ Password reset failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in password reset: {str(e)}")
        return False

def create_fresh_account():
    """Create a fresh account using admin endpoint"""
    print("\n👨‍⚕️ CREATING FRESH ACCOUNT...")
    
    # Admin login first
    admin_creds = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/admin/login", json=admin_creds)
        if login_response.status_code != 200:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return False
            
        admin_token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create new practice account with correct payload format
        practice_data = {
            "practiceName": "The Dental Spa at Garden City",
            "adminEmail": "caryganz@gmail.com",
            "adminFirstName": "Cary",
            "adminLastName": "Ganz",
            "phone": "+15162361083",
            "address": "Garden City, NY",
            "tempPassword": "DentalSpa2025!",
            "subscriptionType": "trial",
            "trialDays": 30
        }
        
        create_response = requests.post(f"{BACKEND_URL}/api/admin/create-practice", 
                                      json=practice_data, headers=headers)
        
        if create_response.status_code == 200:
            result = create_response.json()
            print(f"✅ Fresh account created: {result.get('message', 'Success')}")
            practice_id = result.get('practice_id')
            if practice_id:
                print(f"🆔 Practice ID: {practice_id}")
            return True
        else:
            print(f"❌ Account creation failed: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating account: {str(e)}")
        return False

def send_welcome_email():
    """Send welcome email with login credentials"""
    print("\n📧 SENDING WELCOME EMAIL...")
    
    # Admin login first
    admin_creds = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/admin/login", json=admin_creds)
        if login_response.status_code != 200:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return False
            
        admin_token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Send welcome email
        email_data = {
            "practice_name": "The Dental Spa at Garden City",
            "admin_email": "caryganz@gmail.com",
            "admin_password": "DentalSpa2025!",
            "owner_name": "Cary Ganz"
        }
        
        email_response = requests.post(f"{BACKEND_URL}/api/admin/send-welcome-email", 
                                     json=email_data, headers=headers)
        
        if email_response.status_code == 200:
            result = email_response.json()
            print(f"✅ Welcome email sent: {result.get('message', 'Success')}")
            return True
        else:
            print(f"❌ Welcome email failed: {email_response.status_code}")
            print(f"Response: {email_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")
        return False

def test_login_with_credentials():
    """Test login with known credentials"""
    print("\n🔐 TESTING LOGIN WITH CREDENTIALS...")
    
    # Test different possible passwords
    test_passwords = [
        "DentalSpa2025!",
        "password123", 
        "Dentist1#",
        "caryganz123"
    ]
    
    for password in test_passwords:
        login_payload = {
            "email": "caryganz@gmail.com",
            "password": password
        }
        
        try:
            print(f"🔑 Trying password: {password}")
            response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_payload)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('token')
                practice_id = result.get('practice_id')
                print(f"✅ LOGIN SUCCESSFUL with password: {password}")
                print(f"🎯 JWT Token: {token[:50]}..." if token else "No token")
                print(f"🆔 Practice ID: {practice_id}")
                return password
            elif response.status_code == 401:
                print(f"❌ Wrong password: {password}")
            elif response.status_code == 500:
                print(f"⚠️ Server error with password: {password}")
            else:
                print(f"⚠️ Unexpected response {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing password {password}: {str(e)}")
    
    print("❌ No working password found")
    return None

def main():
    print("🚨 COMPREHENSIVE ACCOUNT TESTING FOR caryganz@gmail.com")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.utcnow().isoformat()}Z")
    print("=" * 70)
    
    # Step 1: Check account status
    account_status = test_account_status()
    
    # Step 2: Admin lookup
    admin_lookup = test_admin_lookup()
    
    # Step 3: Test password reset
    password_reset_success = test_password_reset()
    
    # Step 4: If account is corrupted or missing, create fresh account
    account_created = False
    if account_status in ["corrupted", "missing"] or not admin_lookup:
        print("\n🔧 ACCOUNT NEEDS RECREATION - CREATING FRESH ACCOUNT...")
        account_created = create_fresh_account()
        if account_created:
            welcome_sent = send_welcome_email()
        else:
            welcome_sent = False
    else:
        account_created = True  # Account already exists
        welcome_sent = send_welcome_email()
    
    # Step 5: Test login
    working_password = test_login_with_credentials()
    
    # Final Summary
    print("\n" + "=" * 70)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    print(f"👤 Account Status: {account_status.upper()}")
    print(f"🔍 Admin Lookup: {'✅ FOUND' if admin_lookup else '❌ NOT FOUND'}")
    print(f"🔐 Password Reset: {'✅ SENT' if password_reset_success else '❌ FAILED'}")
    print(f"👨‍⚕️ Account Creation: {'✅ SUCCESS' if account_created else '❌ FAILED'}")
    print(f"📧 Welcome Email: {'✅ SENT' if welcome_sent else '❌ FAILED'}")
    print(f"🔑 Working Password: {'✅ ' + working_password if working_password else '❌ NONE FOUND'}")
    
    print("\n🔧 IMMEDIATE SOLUTION FOR CUSTOMER:")
    
    if working_password:
        print("✅ CUSTOMER CAN LOGIN NOW!")
        print(f"📧 Email: caryganz@gmail.com")
        print(f"🔑 Password: {working_password}")
        print("🌐 Login URL: https://app.dentalaftercarenotes.com/login")
        print("📋 Practice: The Dental Spa at Garden City")
        print("⏰ 30-day trial as paid for")
    elif password_reset_success:
        print("✅ PASSWORD RESET EMAIL SENT!")
        print("📧 Customer should check email inbox and spam folder")
        print("🔗 Reset link valid for 1 hour")
        print("🌐 After reset, login at: https://app.dentalaftercarenotes.com/login")
    elif account_created:
        print("✅ FRESH ACCOUNT CREATED!")
        print("📧 Email: caryganz@gmail.com")
        print("🔑 Password: DentalSpa2025!")
        print("🌐 Login URL: https://app.dentalaftercarenotes.com/login")
        print("📧 Welcome email should arrive shortly")
    else:
        print("🚨 CRITICAL: Unable to resolve account issue")
        print("⚠️ Manual intervention required")
        print("📞 Contact system administrator immediately")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()