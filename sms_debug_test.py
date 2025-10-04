#!/usr/bin/env python3

import requests
import json
import os
import sys
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dentalpractice-hub-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 SMS FUNCTIONALITY DEBUG TESTING")
print(f"Backend URL: {BACKEND_URL}")
print(f"API Base: {API_BASE}")
print("=" * 80)

def test_health_check():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_twilio_configuration():
    """Test Twilio configuration by checking environment variables"""
    print("\n🔍 TESTING TWILIO CONFIGURATION")
    
    # Read backend .env file to check Twilio config
    try:
        with open('/app/backend/.env', 'r') as f:
            env_content = f.read()
            
        twilio_vars = {}
        for line in env_content.split('\n'):
            if line.startswith('TWILIO_'):
                key, value = line.split('=', 1)
                twilio_vars[key] = value
        
        print(f"📋 Twilio Configuration Found:")
        for key, value in twilio_vars.items():
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   {key}: {masked_value}")
        
        required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
        missing_vars = [var for var in required_vars if var not in twilio_vars]
        
        if missing_vars:
            print(f"❌ Missing Twilio configuration: {missing_vars}")
            return False, twilio_vars
        else:
            print("✅ All required Twilio configuration variables present")
            return True, twilio_vars
            
    except Exception as e:
        print(f"❌ Error reading Twilio configuration: {e}")
        return False, {}

def test_twilio_direct_connection(twilio_vars):
    """Test direct Twilio connection"""
    print("\n🔍 TESTING DIRECT TWILIO CONNECTION")
    
    try:
        # Import Twilio and test connection
        from twilio.rest import Client
        
        twilio_sid = twilio_vars.get('TWILIO_ACCOUNT_SID')
        twilio_token = twilio_vars.get('TWILIO_AUTH_TOKEN')
        twilio_phone = twilio_vars.get('TWILIO_PHONE_NUMBER')
        
        if not all([twilio_sid, twilio_token, twilio_phone]):
            print("❌ Missing Twilio credentials")
            return False
        
        print(f"   Account SID: {twilio_sid[:8]}...")
        print(f"   Auth Token: {twilio_token[:8]}...")
        print(f"   Phone Number: {twilio_phone}")
        
        # Test Twilio client connection
        client = Client(twilio_sid, twilio_token)
        
        # Try to get account info to verify credentials
        account = client.api.accounts(twilio_sid).fetch()
        print(f"✅ Twilio connection successful")
        print(f"   Account Status: {account.status}")
        print(f"   Account Name: {account.friendly_name}")
        print(f"   Account Type: {account.type}")
        
        # Check if it's a trial account
        if account.type == 'Trial':
            print("⚠️  This is a TRIAL ACCOUNT - SMS can only be sent to verified numbers")
            
            # Try to get verified phone numbers
            try:
                verified_numbers = client.outgoing_caller_ids.list()
                print(f"   Verified phone numbers: {len(verified_numbers)}")
                for number in verified_numbers:
                    print(f"     - {number.phone_number}")
            except Exception as e:
                print(f"   Could not retrieve verified numbers: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Twilio library not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Twilio connection failed: {e}")
        print(f"   Error details: {str(e)}")
        return False

def test_forgot_password_sms():
    """Test forgot password with SMS recovery method"""
    print("\n🔍 TESTING FORGOT PASSWORD WITH SMS")
    
    test_cases = [
        {
            "name": "SMS Recovery Method",
            "email": "cganz2279@gmail.com",
            "recovery_method": "sms"
        },
        {
            "name": "Both Recovery Methods",
            "email": "cganz2279@gmail.com", 
            "recovery_method": "both"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📧 Testing: {test_case['name']}")
        print(f"   Email: {test_case['email']}")
        print(f"   Recovery Method: {test_case['recovery_method']}")
        
        try:
            payload = {
                "email": test_case["email"],
                "recovery_method": test_case["recovery_method"]
            }
            
            response = requests.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                
                # Check if SMS was attempted
                sent_methods = data.get('sent_methods', [])
                if 'SMS' in sent_methods:
                    print("   ✅ SMS sending was attempted")
                    results.append({"test": test_case['name'], "status": "SMS_ATTEMPTED", "details": data})
                elif test_case['recovery_method'] in ['sms', 'both']:
                    print("   ⚠️  SMS was requested but not in sent_methods")
                    results.append({"test": test_case['name'], "status": "SMS_NOT_SENT", "details": data})
                else:
                    print("   ✅ Response received (SMS not requested)")
                    results.append({"test": test_case['name'], "status": "SUCCESS", "details": data})
            else:
                error_data = response.text
                print(f"   ❌ Request failed: {error_data}")
                results.append({"test": test_case['name'], "status": "FAILED", "error": error_data})
                
        except Exception as e:
            print(f"   ❌ Exception occurred: {e}")
            results.append({"test": test_case['name'], "status": "EXCEPTION", "error": str(e)})
    
    return results

def test_user_phone_number_lookup():
    """Test if user has phone number in database"""
    print("\n🔍 TESTING USER PHONE NUMBER LOOKUP")
    
    # First authenticate to get access
    try:
        login_payload = {
            "email": "cganz2279@gmail.com",
            "password": "password123"
        }
        
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False, None
        
        login_data = login_response.json()
        token = login_data.get('token')
        user = login_data.get('user', {})
        practice = login_data.get('practice', {})
        
        print(f"✅ Login successful")
        print(f"   User ID: {user.get('id')}")
        print(f"   Practice ID: {user.get('practiceId')}")
        
        # Check user phone number
        user_phone = user.get('phone')
        print(f"   User Phone: {user_phone or 'Not set'}")
        
        # Check practice phone number
        practice_phone = practice.get('phone') if practice else None
        print(f"   Practice Phone: {practice_phone or 'Not set'}")
        
        phone_found = user_phone or practice_phone
        if phone_found:
            print(f"✅ Phone number found for SMS delivery: {phone_found}")
            return True, phone_found
        else:
            print("❌ No phone number found - SMS cannot be sent")
            return False, None
            
    except Exception as e:
        print(f"❌ Error checking phone numbers: {e}")
        return False, None

def test_sms_with_verified_number(twilio_vars):
    """Test SMS sending with a verified number if available"""
    print("\n🔍 TESTING SMS WITH VERIFIED NUMBERS")
    
    try:
        from twilio.rest import Client
        
        twilio_sid = twilio_vars.get('TWILIO_ACCOUNT_SID')
        twilio_token = twilio_vars.get('TWILIO_AUTH_TOKEN')
        twilio_phone = twilio_vars.get('TWILIO_PHONE_NUMBER')
        
        client = Client(twilio_sid, twilio_token)
        
        # Get verified numbers
        verified_numbers = client.outgoing_caller_ids.list()
        
        if not verified_numbers:
            print("❌ No verified phone numbers found for trial account")
            return False
        
        print(f"📱 Found {len(verified_numbers)} verified numbers:")
        for number in verified_numbers:
            print(f"   - {number.phone_number}")
        
        # Try to send a test SMS to the first verified number
        test_number = verified_numbers[0].phone_number
        print(f"\n📤 Attempting to send test SMS to verified number: {test_number}")
        
        try:
            message = client.messages.create(
                body="Test SMS from Dental Practice Portal - Password reset functionality test",
                from_=twilio_phone,
                to=test_number
            )
            
            print(f"✅ SMS sent successfully!")
            print(f"   Message SID: {message.sid}")
            print(f"   Status: {message.status}")
            return True
            
        except Exception as e:
            print(f"❌ SMS sending failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing SMS with verified numbers: {e}")
        return False

def check_backend_logs():
    """Check backend logs for SMS-related errors"""
    print("\n🔍 CHECKING BACKEND LOGS FOR SMS ERRORS")
    
    try:
        import subprocess
        
        # Get backend status
        result = subprocess.run(['sudo', 'supervisorctl', 'status', 'backend'], 
                              capture_output=True, text=True)
        print(f"Backend status: {result.stdout.strip()}")
        
        # Check for recent SMS-related logs
        log_files = [
            '/var/log/supervisor/backend.out.log',
            '/var/log/supervisor/backend.err.log'
        ]
        
        sms_logs_found = False
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    if content.strip():
                        # Look for SMS-related messages
                        lines = content.split('\n')
                        sms_lines = [line for line in lines if 'sms' in line.lower() or 'twilio' in line.lower()]
                        if sms_lines:
                            print(f"\n📋 SMS-related logs in {log_file}:")
                            for line in sms_lines[-10:]:  # Last 10 SMS-related lines
                                print(f"   {line}")
                            sms_logs_found = True
                    else:
                        print(f"📋 {log_file}: Empty")
            except Exception as e:
                print(f"❌ Could not read {log_file}: {e}")
        
        if not sms_logs_found:
            print("📋 No SMS-related logs found in backend logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking backend logs: {e}")
        return False

def main():
    """Run comprehensive SMS debugging tests"""
    print("🚀 STARTING SMS FUNCTIONALITY DEBUG TESTING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    test_results = {}
    
    # Test 1: Backend Health Check
    test_results['health_check'] = test_health_check()
    
    # Test 2: Twilio Configuration
    config_result, twilio_vars = test_twilio_configuration()
    test_results['twilio_config'] = config_result
    
    # Test 3: Direct Twilio Connection
    test_results['twilio_connection'] = test_twilio_direct_connection(twilio_vars)
    
    # Test 4: User Phone Number Lookup
    phone_result, phone_number = test_user_phone_number_lookup()
    test_results['phone_lookup'] = phone_result
    
    # Test 5: SMS with Verified Numbers (if trial account)
    test_results['sms_verified_numbers'] = test_sms_with_verified_number(twilio_vars)
    
    # Test 6: Forgot Password SMS Tests
    test_results['forgot_password_sms'] = test_forgot_password_sms()
    
    # Test 7: Backend Logs Check
    test_results['backend_logs'] = check_backend_logs()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SMS FUNCTIONALITY DEBUG SUMMARY")
    print("=" * 80)
    
    for test_name, result in test_results.items():
        if test_name == 'forgot_password_sms':
            print(f"{test_name}: {len(result)} test cases executed")
            for case in result:
                status_icon = "✅" if case['status'] in ['SUCCESS', 'SMS_ATTEMPTED'] else "❌"
                print(f"  {status_icon} {case['test']}: {case['status']}")
        else:
            status_icon = "✅" if result else "❌"
            print(f"{status_icon} {test_name}: {'PASSED' if result else 'FAILED'}")
    
    # Root Cause Analysis
    print("\n🔍 ROOT CAUSE ANALYSIS:")
    
    if not test_results['health_check']:
        print("❌ CRITICAL: Backend is not accessible")
    elif not test_results['twilio_config']:
        print("❌ CRITICAL: Twilio configuration is incomplete")
    elif not test_results['twilio_connection']:
        print("❌ CRITICAL: Cannot connect to Twilio API")
    elif not test_results['phone_lookup']:
        print("❌ CRITICAL: No phone number found for user/practice")
    elif not test_results['sms_verified_numbers']:
        print("⚠️  LIKELY CAUSE: Twilio trial account limitation - SMS can only be sent to verified numbers")
        print("   SOLUTION: Either verify the target phone number in Twilio console or upgrade to paid account")
    else:
        print("✅ All infrastructure checks passed - issue may be elsewhere")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("1. Check if Twilio account is trial or paid")
    print("2. If trial account, verify target phone numbers in Twilio console")
    print("3. If paid account, check account balance and sending limits")
    print("4. Verify phone number format in database matches E.164 format")
    print("5. Check backend logs for specific Twilio error messages")

if __name__ == "__main__":
    main()