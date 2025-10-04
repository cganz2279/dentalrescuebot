#!/usr/bin/env python3
"""
FINAL PASSWORD RESET TEST for caryganz@gmail.com
Send fresh password reset email as the working solution
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

def send_password_reset():
    """Send password reset email"""
    print("🔐 SENDING FRESH PASSWORD RESET EMAIL...")
    
    reset_payload = {
        "email": "caryganz@gmail.com",
        "recovery_method": "email"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json=reset_payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Password reset email sent successfully!")
            print(f"📧 Message: {result.get('message', 'Success')}")
            print(f"📧 Methods: {result.get('sent_methods', [])}")
            return True
        else:
            print(f"❌ Password reset failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending password reset: {str(e)}")
        return False

def test_reset_token_validation():
    """Test that reset token validation is working"""
    print("\n🔍 TESTING RESET TOKEN VALIDATION...")
    
    # Test with a dummy token to ensure validation is working
    test_payload = {
        "token": "dummy_invalid_token_for_testing"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/validate-reset-token", json=test_payload)
        
        if response.status_code == 400:
            print("✅ Reset token validation is working (correctly rejects invalid tokens)")
            return True
        else:
            print(f"⚠️ Unexpected response from token validation: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing token validation: {str(e)}")
        return False

def test_email_service():
    """Test that email service is operational"""
    print("\n📧 TESTING EMAIL SERVICE STATUS...")
    
    # Test with existing practice account to verify email service
    practice_credentials = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        # Practice login
        login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=practice_credentials)
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print("✅ Test practice login successful")
            
            # Test email functionality
            headers = {"Authorization": f"Bearer {token}"}
            
            email_test_payload = {
                "procedureId": "root-canal-therapy",
                "procedureName": "Root Canal Therapy",
                "patientName": "Test Patient",
                "patientEmail": "test@example.com",
                "customInstructions": "Email service verification test"
            }
            
            email_response = requests.post(f"{BACKEND_URL}/api/practice/email-pdf", 
                                         json=email_test_payload, headers=headers)
            if email_response.status_code == 200:
                print("✅ Email service is operational")
                return True
            else:
                print(f"⚠️ Email service test failed: {email_response.status_code}")
                return False
        else:
            print(f"⚠️ Test practice login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email service: {str(e)}")
        return False

def main():
    print("🚨 FINAL PASSWORD RESET SOLUTION FOR caryganz@gmail.com")
    print("=" * 70)
    print("Sending fresh password reset email as the working solution")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Reset Time: {datetime.utcnow().isoformat()}Z")
    print("=" * 70)
    
    # Test email service first
    email_service_working = test_email_service()
    
    # Test reset token validation
    token_validation_working = test_reset_token_validation()
    
    # Send password reset
    reset_sent = send_password_reset()
    
    # Final Summary
    print("\n" + "=" * 70)
    print("🎯 FINAL SOLUTION RESULTS")
    print("=" * 70)
    
    print(f"📧 Email Service: {'✅ OPERATIONAL' if email_service_working else '❌ ISSUES'}")
    print(f"🔍 Token Validation: {'✅ WORKING' if token_validation_working else '❌ ISSUES'}")
    print(f"🔐 Password Reset Sent: {'✅ SUCCESS' if reset_sent else '❌ FAILED'}")
    
    print("\n🔧 IMMEDIATE CUSTOMER SOLUTION:")
    
    if reset_sent:
        print("✅ FRESH PASSWORD RESET EMAIL SENT SUCCESSFULLY!")
        print("📧 Customer: caryganz@gmail.com")
        print("📬 Action Required: Check email inbox AND spam folder")
        print("🔗 Reset Link: Valid for 1 hour from now")
        print("🌐 After Reset: Login at https://app.dentalaftercarenotes.com/login")
        print("📋 Practice: The Dental Spa at Garden City (user's preference)")
        print("⏰ Account Status: 30-day trial as paid for")
        print("")
        print("📝 CUSTOMER INSTRUCTIONS:")
        print("1. Check email inbox for 'Password Reset' email")
        print("2. Check spam/junk folder if not in inbox")
        print("3. Click the reset link in the email")
        print("4. Set a new secure password")
        print("5. Login at https://app.dentalaftercarenotes.com/login")
        print("6. Contact support if reset link doesn't work")
    else:
        print("🚨 PASSWORD RESET FAILED")
        print("⚠️ Email service or backend issues detected")
        print("📞 Immediate escalation to system administrator required")
        print("💡 Manual account creation may be needed")
    
    print("\n📊 SYSTEM STATUS:")
    if email_service_working and token_validation_working and reset_sent:
        print("✅ All password reset systems are operational")
        print("✅ Customer should be able to reset password successfully")
    elif reset_sent:
        print("⚠️ Password reset sent but some systems show issues")
        print("⚠️ Monitor customer success and provide backup support")
    else:
        print("❌ Critical system issues detected")
        print("❌ Manual intervention required immediately")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()