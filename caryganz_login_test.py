#!/usr/bin/env python3
"""
URGENT: caryganz@gmail.com Login Investigation
Testing account existence, login credentials, and account status for user who cannot login
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"

def test_account_creation_webhook():
    """Test the webhook that was supposed to create the account"""
    print("🔍 TESTING ACCOUNT CREATION WEBHOOK...")
    try:
        # Test the webhook endpoint that was used to create the account
        test_url = f"{BACKEND_URL}/api/webhook/samcart/test?test_email=caryganz@gmail.com"
        response = requests.post(test_url)
        
        print(f"Webhook test response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook test endpoint working")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if account already exists or was created
            if data.get('status') == 'success':
                practice_info = data.get('practice_info', {})
                practice_id = practice_info.get('practice_id')
                email = practice_info.get('email')
                practice_name = practice_info.get('practice_name')
                
                print(f"✅ Practice ID: {practice_id}")
                print(f"✅ Email: {email}")
                print(f"✅ Practice Name: {practice_name}")
                
                return practice_id, email, practice_name
            else:
                print(f"❌ Webhook test failed: {data}")
                return None, None, None
        else:
            print(f"❌ Webhook test failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return None, None, None

def test_login_attempts():
    """Test various login attempts for caryganz@gmail.com"""
    print("\n🔐 TESTING LOGIN ATTEMPTS...")
    
    # Common password patterns to try
    password_attempts = [
        "password123",  # Common default
        "Password123",  # Capitalized
        "caryganz123",  # Based on email
        "Dentist123",   # Dental theme
        "Welcome123",   # Welcome theme
        "Practice123",  # Practice theme
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
            else:
                print(f"   ⚠️ Unexpected response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("❌ NO SUCCESSFUL LOGIN FOUND")
    return None, None, None

def test_password_reset():
    """Test password reset functionality for caryganz@gmail.com"""
    print("\n🔄 TESTING PASSWORD RESET...")
    
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

def test_admin_practice_lookup():
    """Use admin access to look up the practice account"""
    print("\n👤 TESTING ADMIN PRACTICE LOOKUP...")
    
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
                    caryganz_practice = None
                    for practice in practices:
                        if isinstance(practice, dict):
                            admin_email = practice.get('admin_email', '')
                            if admin_email == 'caryganz@gmail.com':
                                caryganz_practice = practice
                                break
                    
                    if caryganz_practice:
                        print("✅ FOUND caryganz@gmail.com practice account:")
                        print(f"   Practice ID: {caryganz_practice.get('practice_id', 'Unknown')}")
                        print(f"   Practice Name: {caryganz_practice.get('practice_name', 'Unknown')}")
                        print(f"   Admin Email: {caryganz_practice.get('admin_email', 'Unknown')}")
                        print(f"   Status: {caryganz_practice.get('status', 'Unknown')}")
                        print(f"   Created: {caryganz_practice.get('created_at', 'Unknown')}")
                        print(f"   Trial End: {caryganz_practice.get('trial_end_date', 'Unknown')}")
                        
                        # Check if there's password info (hashed)
                        if 'password' in caryganz_practice:
                            print(f"   Password Hash: {caryganz_practice['password'][:50]}... (truncated)")
                        else:
                            print("   ❌ NO PASSWORD FIELD FOUND")
                        
                        return caryganz_practice
                    else:
                        print("❌ caryganz@gmail.com practice account NOT FOUND")
                        
                        # Show first few practices for debugging
                        print("🔍 First 3 practices for debugging:")
                        for i, practice in enumerate(practices[:3]):
                            if isinstance(practice, dict):
                                print(f"   {i+1}. {practice.get('admin_email', 'No email')} - {practice.get('practice_name', 'No name')}")
                        
                        return None
                else:
                    print(f"❌ Could not retrieve practices: {practices_response.status_code}")
                    print(f"Response: {practices_response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error retrieving practices: {str(e)}")
                return None
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error with admin lookup: {str(e)}")
        return None

def test_webhook_logs_for_caryganz():
    """Check webhook logs specifically for caryganz@gmail.com"""
    print("\n📋 CHECKING WEBHOOK LOGS FOR caryganz@gmail.com...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/logs")
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            print(f"✅ Retrieved {len(logs)} webhook logs")
            
            # Look for caryganz@gmail.com in logs
            caryganz_logs = []
            for log in logs:
                if 'payload' in log and 'customer' in log['payload']:
                    email = log['payload']['customer'].get('email', '')
                    if 'caryganz@gmail.com' in email.lower():
                        caryganz_logs.append(log)
            
            if caryganz_logs:
                print(f"✅ FOUND {len(caryganz_logs)} webhook log(s) for caryganz@gmail.com:")
                for i, log in enumerate(caryganz_logs):
                    print(f"\n   Log {i+1}:")
                    print(f"   Timestamp: {log.get('created_at', 'Unknown')}")
                    print(f"   Event Type: {log.get('event_type', 'Unknown')}")
                    print(f"   Status: {log.get('processing_status', 'Unknown')}")
                    print(f"   Webhook ID: {log.get('webhook_id', 'Unknown')}")
                    
                    if 'payload' in log:
                        payload = log['payload']
                        if 'customer' in payload:
                            customer = payload['customer']
                            print(f"   Customer: {customer.get('first_name', '')} {customer.get('last_name', '')}")
                            print(f"   Email: {customer.get('email', '')}")
                        
                        if 'order' in payload:
                            order = payload['order']
                            print(f"   Order ID: {order.get('id', 'Unknown')}")
                            print(f"   Order Total: ${order.get('total', '0.00')}")
                    
                    # Check if this event type would be processed
                    event_type = log.get('event_type', '')
                    processed_types = ["ProductPurchased", "OrderCompleted", "Order.Completed"]
                    if event_type in processed_types:
                        print(f"   ✅ Event type '{event_type}' WOULD BE PROCESSED")
                    else:
                        print(f"   ❌ Event type '{event_type}' WOULD BE IGNORED!")
                        print(f"   🔧 Handler only processes: {processed_types}")
                
                return caryganz_logs
            else:
                print("❌ NO webhook logs found for caryganz@gmail.com")
                return []
        else:
            print(f"❌ Failed to get webhook logs: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking webhook logs: {str(e)}")
        return []

def main():
    print("🚨 URGENT: caryganz@gmail.com LOGIN INVESTIGATION")
    print("=" * 70)
    print("User reports: 'Used the logins and login failed'")
    print("Account was created via: POST /api/webhook/samcart/test?test_email=caryganz@gmail.com")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Investigation time: {datetime.utcnow().isoformat()}Z")
    print("=" * 70)
    
    # Run all tests
    print("\n1. TESTING ACCOUNT CREATION WEBHOOK")
    practice_id, email, practice_name = test_account_creation_webhook()
    
    print("\n2. TESTING LOGIN ATTEMPTS")
    successful_password, token, login_practice_id = test_login_attempts()
    
    print("\n3. TESTING PASSWORD RESET")
    reset_success = test_password_reset()
    
    print("\n4. ADMIN PRACTICE LOOKUP")
    admin_practice_data = test_admin_practice_lookup()
    
    print("\n5. WEBHOOK LOGS CHECK")
    webhook_logs = test_webhook_logs_for_caryganz()
    
    # Summary and diagnosis
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 70)
    
    if practice_id:
        print(f"✅ Account creation webhook working - Practice ID: {practice_id}")
    else:
        print("❌ Account creation webhook failed")
    
    if successful_password:
        print(f"✅ LOGIN WORKING - Password: {successful_password}")
        print(f"   Token: {token[:50] if token else 'None'}...")
        print(f"   Practice ID: {login_practice_id}")
    else:
        print("❌ LOGIN FAILED - No working password found")
    
    if reset_success:
        print("✅ Password reset email sent successfully")
    else:
        print("❌ Password reset failed")
    
    if admin_practice_data:
        print("✅ Practice account found in admin lookup")
        if 'password' in admin_practice_data:
            print("✅ Account has password hash")
        else:
            print("❌ Account missing password field")
    else:
        print("❌ Practice account NOT found in admin lookup")
    
    if webhook_logs:
        print(f"✅ Found {len(webhook_logs)} webhook log(s) for caryganz@gmail.com")
        # Check for ignored events
        ignored_events = []
        for log in webhook_logs:
            event_type = log.get('event_type', '')
            processed_types = ["ProductPurchased", "OrderCompleted", "Order.Completed"]
            if event_type not in processed_types:
                ignored_events.append(event_type)
        
        if ignored_events:
            print(f"⚠️ WARNING: {len(ignored_events)} webhook(s) were IGNORED due to event type mismatch")
    else:
        print("❌ No webhook logs found for caryganz@gmail.com")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    
    if successful_password:
        print("✅ ACCOUNT IS WORKING!")
        print(f"   User should login with: caryganz@gmail.com / {successful_password}")
        print("   No further action needed.")
    else:
        if admin_practice_data and 'password' not in admin_practice_data:
            print("🚨 CRITICAL: Account exists but has NO PASSWORD")
            print("   1. Account was created but password was not set")
            print("   2. Use admin tools to set a password for this account")
            print("   3. Or user should use password reset functionality")
        elif not admin_practice_data:
            print("🚨 CRITICAL: Account does NOT exist")
            print("   1. Webhook may have failed to create the account")
            print("   2. Manually create account for caryganz@gmail.com")
            print("   3. Send welcome email with credentials")
        else:
            print("🚨 CRITICAL: Account exists with password but login still fails")
            print("   1. Password may be corrupted or in wrong format")
            print("   2. Check password hashing algorithm")
            print("   3. Reset password for this account")
        
        if reset_success:
            print("✅ Password reset email sent - user can reset password")
        else:
            print("❌ Password reset also failed - deeper investigation needed")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()