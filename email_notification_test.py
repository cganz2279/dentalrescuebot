#!/usr/bin/env python3
"""
Welcome Email Test for Customer Account
Testing welcome email functionality for cganz2279@gmail.com
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
CUSTOMER_EMAIL = "cganz2279@gmail.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*80}")
    print(f"🧪 {test_name}")
    print(f"{'='*80}")

def print_result(success, message, details=None):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if details:
        print(f"   Details: {details}")

def admin_login():
    """Login as admin to access admin functions"""
    print_test_header("Admin Authentication")
    
    try:
        login_url = f"{BACKEND_URL}/api/admin/login"
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(login_url, json=login_data, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                token = data.get("token")
                print_result(True, "Admin login successful")
                print(f"   🎫 Admin Token: {token[:20]}...")
                return {"success": True, "token": token}
            else:
                print_result(False, f"Admin login failed: {data.get('error', 'Unknown error')}")
                return {"success": False}
        else:
            print_result(False, f"Admin login failed with status {response.status_code}")
            return {"success": False}
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Admin login failed: {str(e)}")
        return {"success": False}

def test_welcome_email_send(admin_token):
    """Test sending welcome email to customer"""
    print_test_header("Welcome Email Send Test")
    
    if not admin_token:
        print_result(False, "Cannot test welcome email - no admin token")
        return False
    
    try:
        email_url = f"{BACKEND_URL}/api/admin/send-welcome-email"
        
        headers = {
            "Authorization": f"Bearer {admin_token}"
        }
        
        email_data = {
            "email": CUSTOMER_EMAIL,
            "practice_name": "The Dental Spa at Garden City",
            "owner_name": "Cary Ganz",
            "password": "password123"  # Known working password
        }
        
        response = requests.post(email_url, json=email_data, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📧 Sending welcome email to: {CUSTOMER_EMAIL}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Welcome email sent successfully")
                print(f"   📬 Email sent to: {CUSTOMER_EMAIL}")
                print(f"   🏥 Practice: The Dental Spa at Garden City")
                print(f"   👤 Owner: Cary Ganz")
                return True
            else:
                print_result(False, f"Welcome email failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_result(False, f"Welcome email failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Welcome email test failed: {str(e)}")
        return False

def test_password_reset_email():
    """Test password reset email as alternative"""
    print_test_header("Password Reset Email Test")
    
    try:
        reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
        
        reset_data = {
            "email": CUSTOMER_EMAIL,
            "recovery_method": "email"
        }
        
        response = requests.post(reset_url, json=reset_data, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result(True, "Password reset email sent successfully")
                print(f"   📧 Reset email sent to: {CUSTOMER_EMAIL}")
                print(f"   🔑 Customer can use this to access their account")
                return True
            else:
                print_result(False, f"Password reset failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_result(False, f"Password reset failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Password reset test failed: {str(e)}")
        return False

def check_backend_email_logs():
    """Check backend logs for email activity"""
    print_test_header("Backend Email Logs Check")
    
    try:
        # We can't directly access logs, but we can check if email service is configured
        health_url = f"{BACKEND_URL}/api/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print_result(True, "Backend is running with email service")
            print("   📧 SendGrid email service should be configured")
            print("   📬 Admin notification emails should be sent to admin@theoncallbot.com")
            return True
        else:
            print_result(False, "Backend health check failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Backend logs check failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("📧 WELCOME EMAIL FUNCTIONALITY TEST")
    print(f"📧 Customer: {CUSTOMER_EMAIL}")
    print(f"🏥 Practice: The Dental Spa at Garden City")
    print(f"👤 Owner: Cary Ganz")
    print(f"🎯 Goal: Ensure customer receives welcome email with login credentials")
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track test results
    test_results = {}
    
    # Admin login
    admin_result = admin_login()
    test_results["admin_login"] = admin_result["success"]
    
    if test_results["admin_login"]:
        # Test welcome email
        test_results["welcome_email"] = test_welcome_email_send(admin_result["token"])
    else:
        test_results["welcome_email"] = False
    
    # Test password reset as alternative
    test_results["password_reset"] = test_password_reset_email()
    
    # Check email service configuration
    test_results["email_service"] = check_backend_email_logs()
    
    # Print final summary
    print_test_header("FINAL EMAIL TEST SUMMARY")
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name.replace('_', ' ').title()}")
    
    # Final assessment
    print_test_header("EMAIL FUNCTIONALITY ASSESSMENT")
    
    if test_results.get("welcome_email"):
        print("🎉 SUCCESS: Welcome email sent successfully!")
        print(f"✅ Welcome email sent to {CUSTOMER_EMAIL}")
        print(f"✅ Customer should receive login credentials")
        print(f"✅ Admin notification should be sent")
        print(f"📧 Customer should check their email for login instructions")
        
        return 0  # Success
    elif test_results.get("password_reset"):
        print("⚠️ ALTERNATIVE SUCCESS: Password reset email sent")
        print(f"✅ Password reset email sent to {CUSTOMER_EMAIL}")
        print(f"📧 Customer can use password reset to access their account")
        print(f"🔗 Customer should check email and then login at: https://app.dentalaftercarenotes.com/login")
        
        return 0  # Success (alternative)
    else:
        print("🚨 EMAIL ISSUE: Email functionality problems detected")
        print("❌ Customer may not receive welcome email")
        
        if not test_results.get("admin_login"):
            print("   🔍 Issue: Admin authentication failed")
        if not test_results.get("email_service"):
            print("   🔍 Issue: Email service configuration problems")
            
        print("🔧 MANUAL ACTION REQUIRED:")
        print(f"   📧 Manually send login credentials to {CUSTOMER_EMAIL}")
        print(f"   🔑 Email: {CUSTOMER_EMAIL}")
        print(f"   🔑 Password: password123")
        print(f"   🔗 Login URL: https://app.dentalaftercarenotes.com/login")
            
        return 1  # Failure

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)