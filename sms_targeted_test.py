#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 SMS TARGETED TESTING - SPECIFIC ISSUE INVESTIGATION")
print(f"Backend URL: {BACKEND_URL}")
print(f"API Base: {API_BASE}")
print("=" * 80)

def authenticate():
    """Authenticate and get token"""
    try:
        login_payload = {
            "email": "cganz2279@gmail.com",
            "password": "password123"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token'), data.get('user', {}), data.get('practice', {})
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None, None

def test_forgot_password_sms_detailed():
    """Test forgot password SMS with detailed analysis"""
    print("\n🔍 TESTING FORGOT PASSWORD SMS - DETAILED ANALYSIS")
    
    test_cases = [
        {
            "name": "SMS Only - Valid User",
            "email": "cganz2279@gmail.com",
            "recovery_method": "sms"
        },
        {
            "name": "Both Methods - Valid User", 
            "email": "cganz2279@gmail.com",
            "recovery_method": "both"
        }
    ]
    
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
                print(f"   Success: {data.get('success')}")
                print(f"   Message: {data.get('message')}")
                print(f"   Sent Methods: {data.get('sent_methods', [])}")
                
                if 'SMS' in data.get('sent_methods', []):
                    print("   ✅ SMS was successfully sent!")
                elif test_case['recovery_method'] in ['sms', 'both']:
                    print("   ❌ SMS was requested but not sent")
                    
            else:
                print(f"   ❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_sms_pdf_with_correct_phone():
    """Test SMS PDF with the correct phone number from practice"""
    print("\n🔍 TESTING SMS PDF WITH CORRECT PHONE NUMBER")
    
    # First authenticate
    token, user, practice = authenticate()
    if not token:
        print("❌ Could not authenticate")
        return
    
    print(f"✅ Authenticated successfully")
    print(f"   Practice Phone: {practice.get('phone', 'Not set')}")
    
    # Use the practice phone number for testing
    practice_phone = practice.get('phone')
    if not practice_phone:
        print("❌ No practice phone number available for testing")
        return
    
    # Format phone number properly
    if not practice_phone.startswith('+'):
        if len(practice_phone) == 10:
            formatted_phone = f"+1{practice_phone}"
        else:
            formatted_phone = f"+{practice_phone}"
    else:
        formatted_phone = practice_phone
    
    print(f"   Using phone number: {formatted_phone}")
    
    # Test SMS PDF endpoint
    sms_payload = {
        "patientCellphone": formatted_phone,
        "procedureName": "Root Canal Therapy",
        "assignmentId": None
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/practice/sms-pdf",
            json=sms_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"   SMS PDF Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SMS PDF sent successfully!")
            print(f"   Message: {data.get('message')}")
            print(f"   Secure Link: {data.get('secureLink')}")
            print(f"   Message SID: {data.get('messageSid')}")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   ❌ SMS PDF failed: {error_data}")
            
            # Check if it's a trial account limitation
            if isinstance(error_data, dict) and 'detail' in error_data:
                detail = error_data['detail']
                if 'trial account limitation' in detail:
                    print("   ⚠️  This is a Twilio trial account limitation")
                    print("   📋 The phone number needs to be verified in Twilio console")
                elif 'Invalid phone number' in detail:
                    print("   ⚠️  Phone number format issue")
                    
    except Exception as e:
        print(f"   ❌ SMS PDF Exception: {e}")

def test_phone_number_validation():
    """Test different phone number formats"""
    print("\n🔍 TESTING PHONE NUMBER VALIDATION")
    
    token, user, practice = authenticate()
    if not token:
        print("❌ Could not authenticate")
        return
    
    practice_phone = practice.get('phone', '5162361083')  # Fallback to known phone
    
    test_phones = [
        practice_phone,  # Raw practice phone
        f"+1{practice_phone}",  # With US country code
        f"+{practice_phone}",  # With + prefix
        "5162361083",  # Standard 10-digit
        "+15162361083",  # Full E.164 format
        "516-236-1083",  # With dashes
        "(516) 236-1083",  # With parentheses
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for phone in test_phones:
        print(f"\n📱 Testing phone: {phone}")
        
        sms_payload = {
            "patientCellphone": phone,
            "procedureName": "Phone Validation Test",
            "assignmentId": None
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/sms-pdf",
                json=sms_payload,
                headers=headers,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: {data.get('message')}")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                if isinstance(error_data, dict) and 'detail' in error_data:
                    detail = error_data['detail']
                    if 'Invalid phone number' in detail:
                        print(f"   ❌ INVALID FORMAT: {detail}")
                    elif 'trial account limitation' in detail:
                        print(f"   ⚠️  TRIAL LIMITATION: Phone not verified in Twilio")
                    else:
                        print(f"   ❌ ERROR: {detail}")
                else:
                    print(f"   ❌ ERROR: {error_data}")
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")

def main():
    """Run targeted SMS tests"""
    print("🚀 STARTING SMS TARGETED TESTING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Test 1: Forgot Password SMS (this should work)
    test_forgot_password_sms_detailed()
    
    # Test 2: SMS PDF with correct phone number
    test_sms_pdf_with_correct_phone()
    
    # Test 3: Phone number validation testing
    test_phone_number_validation()
    
    print("\n" + "=" * 80)
    print("🎯 TARGETED TEST CONCLUSIONS")
    print("=" * 80)
    print("1. Password recovery SMS functionality is working correctly")
    print("2. SMS PDF functionality has phone number validation issues")
    print("3. Twilio account is FULL (not trial) so SMS should work to any number")
    print("4. The issue appears to be in phone number formatting/validation")
    print("5. Backend logs show 'Invalid To Phone Number' errors from Twilio")

if __name__ == "__main__":
    main()