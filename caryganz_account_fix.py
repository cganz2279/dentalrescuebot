#!/usr/bin/env python3
"""
URGENT: caryganz@gmail.com Account Fix
Manually create the account with proper password since webhook failed
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

def manually_create_account():
    """Manually create account using admin endpoint"""
    print("🔧 MANUALLY CREATING ACCOUNT FOR caryganz@gmail.com...")
    
    # Admin login first
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
            
            # Create practice account
            practice_data = {
                "practiceName": "Cary Ganz Dental Practice",
                "adminEmail": "caryganz@gmail.com",
                "tempPassword": "CaryGanz123!",  # Strong password
                "adminFirstName": "Cary",
                "adminLastName": "Ganz",
                "subscriptionType": "trial"
            }
            
            try:
                create_response = requests.post(f"{BACKEND_URL}/api/admin/create-practice", 
                                              json=practice_data, headers=headers)
                print(f"Create practice response status: {create_response.status_code}")
                
                if create_response.status_code == 200:
                    data = create_response.json()
                    print("✅ Practice account created successfully!")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    
                    # Extract credentials
                    practice_id = data.get('practice_id')
                    email = data.get('admin_email', 'caryganz@gmail.com')
                    password = data.get('admin_password', 'CaryGanz123!')
                    
                    print(f"\n🎯 LOGIN CREDENTIALS:")
                    print(f"   Email: {email}")
                    print(f"   Password: {password}")
                    print(f"   Practice ID: {practice_id}")
                    
                    return email, password, practice_id
                else:
                    print(f"❌ Failed to create practice: {create_response.status_code}")
                    print(f"Response: {create_response.text}")
                    return None, None, None
                    
            except Exception as e:
                print(f"❌ Error creating practice: {str(e)}")
                return None, None, None
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Error with admin access: {str(e)}")
        return None, None, None

def test_new_login(email, password):
    """Test login with the new credentials"""
    print(f"\n🔐 TESTING LOGIN WITH NEW CREDENTIALS...")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    login_url = f"{BACKEND_URL}/api/auth/login"
    credentials = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"   Token: {data.get('token', 'No token')[:50]}...")
            print(f"   Practice ID: {data.get('practice_id', 'No practice ID')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
        return False

def send_welcome_email(email, password, practice_name):
    """Send welcome email with credentials"""
    print(f"\n📧 SENDING WELCOME EMAIL...")
    
    # Admin login first
    admin_credentials = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/admin/login", json=admin_credentials)
        if login_response.status_code == 200:
            admin_token = login_response.json().get('token')
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Send welcome email
            email_data = {
                "practice_id": "manual-creation",
                "admin_email": email,
                "practice_name": practice_name,
                "admin_password": password
            }
            
            email_response = requests.post(f"{BACKEND_URL}/api/admin/send-welcome-email", 
                                         json=email_data, headers=headers)
            
            if email_response.status_code == 200:
                print("✅ Welcome email sent successfully!")
                return True
            else:
                print(f"❌ Failed to send welcome email: {email_response.status_code}")
                print(f"Response: {email_response.text}")
                return False
        else:
            print(f"❌ Admin login failed for email sending")
            return False
            
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")
        return False

def main():
    print("🚨 URGENT: MANUAL ACCOUNT CREATION FOR caryganz@gmail.com")
    print("=" * 70)
    print("Creating account manually since SamCart webhook failed to create proper login")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Creation time: {datetime.utcnow().isoformat()}Z")
    print("=" * 70)
    
    # Step 1: Manually create account
    email, password, practice_id = manually_create_account()
    
    if not email or not password:
        print("\n❌ FAILED TO CREATE ACCOUNT")
        print("Manual intervention required - contact system administrator")
        return
    
    # Step 2: Test login
    login_success = test_new_login(email, password)
    
    # Step 3: Send welcome email
    email_sent = send_welcome_email(email, password, "Cary Ganz Dental Practice")
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 ACCOUNT CREATION SUMMARY")
    print("=" * 70)
    
    if email and password:
        print("✅ Account created successfully")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Practice ID: {practice_id}")
    else:
        print("❌ Account creation failed")
    
    if login_success:
        print("✅ Login working correctly")
    else:
        print("❌ Login still not working")
    
    if email_sent:
        print("✅ Welcome email sent")
    else:
        print("❌ Welcome email failed")
    
    print("\n🎯 USER INSTRUCTIONS:")
    if login_success:
        print("✅ ACCOUNT IS NOW READY!")
        print(f"   User can login at: https://app.dentalaftercarenotes.com/login")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print("   Welcome email sent with login instructions")
    else:
        print("❌ ACCOUNT STILL HAS ISSUES")
        print("   Further investigation required")
        print("   User should contact support")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()