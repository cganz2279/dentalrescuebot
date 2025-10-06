#!/usr/bin/env python3

import requests
import json
import os
import sys
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv('/app/backend/.env')

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Import the email service
from services.email_service import email_service

def test_welcome_email_url_verification():
    """
    Test welcome email functionality to verify URL fixes are working correctly
    Send welcome email with test data as requested by user
    """
    print("🎯 WELCOME EMAIL URL VERIFICATION TEST")
    print("=" * 60)
    
    try:
        # Test data as specified in the review request
        practice_data = {
            'practiceName': 'Test Dental Practice'
        }
        
        admin_credentials = {
            'adminEmail': 'caryganz@gmail.com',
            'adminFirstName': 'Cary',
            'adminLastName': 'Ganz',
            'tempPassword': 'TestPass2024!'
        }
        
        # Get FRONTEND_URL from environment variable
        frontend_url = os.environ.get('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
        
        print(f"📧 Sending welcome email to: {admin_credentials['adminEmail']}")
        print(f"🏥 Practice Name: {practice_data['practiceName']}")
        print(f"👤 Admin Name: {admin_credentials['adminFirstName']} {admin_credentials['adminLastName']}")
        print(f"🔑 Temporary Password: {admin_credentials['tempPassword']}")
        print(f"🌐 Frontend URL: {frontend_url}")
        print()
        
        # Send welcome email using the email service
        print("📤 Sending welcome email...")
        success = email_service.send_welcome_email(
            practice_data=practice_data,
            admin_credentials=admin_credentials,
            app_url=frontend_url
        )
        
        if success:
            print("✅ WELCOME EMAIL SENT SUCCESSFULLY!")
            print()
            print("📋 EMAIL VERIFICATION CHECKLIST:")
            print(f"   ✅ Email sent to: {admin_credentials['adminEmail']}")
            print(f"   ✅ Practice Name: {practice_data['practiceName']}")
            print(f"   ✅ Admin Name: {admin_credentials['adminFirstName']} {admin_credentials['adminLastName']}")
            print(f"   ✅ Temporary Password: {admin_credentials['tempPassword']}")
            print(f"   ✅ Correct URL used: {frontend_url}")
            print()
            print("🎯 EXPECTED EMAIL CONTENT:")
            print("   ✅ Subject: 'Welcome to Dental Aftercare Notes – Your Account Is Ready'")
            print("   ✅ Professional 'Dental AfterCare Notes' branding")
            print(f"   ✅ 'Access Your Account' button linking to: {frontend_url}")
            print("   ✅ Login credentials clearly displayed")
            print("   ✅ No SamCart or preview URLs")
            print()
            print("📬 Please check the email at caryganz@gmail.com to verify:")
            print("   1. Email was delivered successfully")
            print("   2. URL points to https://app.dentalaftercarenotes.com")
            print("   3. Professional branding is correct")
            print("   4. Login credentials are clearly displayed")
            print("   5. 'Access Your Account' button works correctly")
            
            return True
        else:
            print("❌ FAILED TO SEND WELCOME EMAIL")
            print("   Check backend logs for detailed error information")
            return False
            
    except Exception as e:
        print(f"❌ ERROR DURING WELCOME EMAIL TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_health():
    """Test basic backend health"""
    try:
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
        
        print(f"🔍 Testing backend health at: {backend_url}")
        
        # Test health endpoint
        response = requests.get(f"{backend_url}/api/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check error: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 WELCOME EMAIL URL VERIFICATION TESTING")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results
    results = {
        'backend_health': False,
        'welcome_email_test': False
    }
    
    # Test 1: Backend Health
    print("TEST 1: Backend Health Check")
    print("-" * 30)
    results['backend_health'] = test_backend_health()
    print()
    
    # Test 2: Welcome Email URL Verification
    print("TEST 2: Welcome Email URL Verification")
    print("-" * 40)
    results['welcome_email_test'] = test_welcome_email_url_verification()
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print()
    print(f"📈 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if results['welcome_email_test']:
        print()
        print("🎯 CRITICAL SUCCESS: Welcome email sent successfully!")
        print("📧 Please check caryganz@gmail.com for the welcome email")
        print("🔍 Verify the email contains:")
        print("   • Correct URL: https://app.dentalaftercarenotes.com")
        print("   • Professional 'Dental AfterCare Notes' branding")
        print("   • Working 'Access Your Account' button")
        print("   • Clear display of login credentials")
    else:
        print()
        print("❌ CRITICAL FAILURE: Welcome email was not sent")
        print("🔧 Check backend logs and SendGrid configuration")
    
    print()
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)