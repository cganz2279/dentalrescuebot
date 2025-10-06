#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 SMS FINAL COMPREHENSIVE TEST")
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

def get_test_procedure():
    """Get a test procedure ID"""
    try:
        response = requests.get(f"{API_BASE}/procedures", timeout=10)
        if response.status_code == 200:
            data = response.json()
            procedures = data.get('data', [])
            if procedures:
                return procedures[0]['id'], procedures[0]['name']
        return None, None
    except Exception as e:
        print(f"❌ Error getting procedures: {e}")
        return None, None

def test_forgot_password_sms():
    """Test forgot password SMS functionality"""
    print("\n🔍 TESTING FORGOT PASSWORD SMS FUNCTIONALITY")
    
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
                sent_methods = data.get('sent_methods', [])
                
                if 'SMS' in sent_methods:
                    print("   ✅ SMS sent successfully!")
                    results.append(True)
                else:
                    print("   ❌ SMS not sent")
                    results.append(False)
            else:
                print(f"   ❌ Request failed: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append(False)
    
    return all(results)

def test_sms_pdf_functionality():
    """Test SMS PDF functionality with correct payload"""
    print("\n🔍 TESTING SMS PDF FUNCTIONALITY")
    
    # Authenticate
    token, user, practice = authenticate()
    if not token:
        print("❌ Could not authenticate")
        return False
    
    print(f"✅ Authenticated successfully")
    
    # Get practice phone
    practice_phone = practice.get('phone')
    if not practice_phone:
        print("❌ No practice phone number available")
        return False
    
    # Format phone number
    if not practice_phone.startswith('+'):
        formatted_phone = f"+1{practice_phone}"
    else:
        formatted_phone = practice_phone
    
    print(f"   Using phone: {formatted_phone}")
    
    # Get test procedure
    procedure_id, procedure_name = get_test_procedure()
    if not procedure_id:
        print("❌ Could not get test procedure")
        return False
    
    print(f"   Using procedure: {procedure_name} (ID: {procedure_id})")
    
    # Test SMS PDF with correct payload
    sms_payload = {
        "patientCellphone": formatted_phone,
        "procedureId": procedure_id,
        "procedureName": procedure_name,
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
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   ❌ SMS PDF failed: {error_data}")
            
            # Analyze the error
            if isinstance(error_data, dict) and 'detail' in error_data:
                detail = error_data['detail']
                if 'trial account limitation' in detail:
                    print("   ⚠️  Twilio trial account limitation detected")
                elif 'Invalid phone number' in detail:
                    print("   ⚠️  Phone number validation issue")
                elif 'Unable to create record' in detail:
                    print("   ⚠️  Twilio API error - likely phone number issue")
            
            return False
            
    except Exception as e:
        print(f"   ❌ SMS PDF Exception: {e}")
        return False

def test_phone_number_formats():
    """Test different phone number formats for SMS PDF"""
    print("\n🔍 TESTING PHONE NUMBER FORMATS")
    
    token, user, practice = authenticate()
    if not token:
        return False
    
    procedure_id, procedure_name = get_test_procedure()
    if not procedure_id:
        return False
    
    practice_phone = practice.get('phone', '5162361083')
    
    # Test different formats of the same phone number
    test_phones = [
        "+15162361083",  # E.164 format (should work)
        "5162361083",    # 10-digit US format
        "+1234567890",   # Different test number
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    success_count = 0
    
    for phone in test_phones:
        print(f"\n📱 Testing phone: {phone}")
        
        sms_payload = {
            "patientCellphone": phone,
            "procedureId": procedure_id,
            "procedureName": procedure_name,
            "assignmentId": None
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/sms-pdf",
                json=sms_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                success_count += 1
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                if isinstance(error_data, dict) and 'detail' in error_data:
                    detail = error_data['detail']
                    if 'Invalid phone number' in detail:
                        print(f"   ❌ INVALID FORMAT")
                    elif 'Unable to create record' in detail or 'Invalid \'To\' Phone Number' in detail:
                        print(f"   ❌ TWILIO VALIDATION ERROR")
                    else:
                        print(f"   ❌ OTHER ERROR: {detail}")
                else:
                    print(f"   ❌ ERROR: {error_data}")
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
    
    return success_count > 0

def main():
    """Run comprehensive SMS testing"""
    print("🚀 STARTING COMPREHENSIVE SMS TESTING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Forgot Password SMS (should work)
    results['forgot_password_sms'] = test_forgot_password_sms()
    
    # Test 2: SMS PDF functionality
    results['sms_pdf'] = test_sms_pdf_functionality()
    
    # Test 3: Phone number format testing
    results['phone_formats'] = test_phone_number_formats()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE SMS TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {test_name}: {'PASSED' if result else 'FAILED'}")
    
    # Final Analysis
    print("\n🎯 FINAL ANALYSIS:")
    
    if results['forgot_password_sms']:
        print("✅ Password recovery SMS is working correctly")
    else:
        print("❌ Password recovery SMS has issues")
    
    if results['sms_pdf']:
        print("✅ SMS PDF functionality is working")
    else:
        print("❌ SMS PDF functionality has issues")
        print("   - This could be due to phone number validation")
        print("   - Or Twilio account restrictions")
        print("   - Check backend logs for specific Twilio errors")
    
    if results['phone_formats']:
        print("✅ At least some phone number formats work")
    else:
        print("❌ Phone number format validation issues detected")
    
    # Overall conclusion
    if results['forgot_password_sms'] and not results['sms_pdf']:
        print("\n🔍 CONCLUSION:")
        print("SMS infrastructure is working (password recovery works)")
        print("The issue is specifically with SMS PDF functionality")
        print("This is likely a phone number validation or API payload issue")
    elif not results['forgot_password_sms']:
        print("\n🔍 CONCLUSION:")
        print("SMS infrastructure has fundamental issues")
        print("Check Twilio configuration and phone number setup")
    else:
        print("\n🔍 CONCLUSION:")
        print("SMS functionality appears to be working correctly")

if __name__ == "__main__":
    main()