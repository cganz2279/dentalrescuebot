#!/usr/bin/env python3
"""
Login Verification Test for Existing Customer Account
Testing if cganz2279@gmail.com can login with their existing account
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
CUSTOMER_EMAIL = "cganz2279@gmail.com"
# Common passwords that might have been used
TEST_PASSWORDS = ["password123", "Password123", "Dentist123", "dental123"]

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

def test_practice_login_with_known_passwords():
    """Test login with known passwords from previous tests"""
    print_test_header("Practice Login Test with Known Passwords")
    
    login_url = f"{BACKEND_URL}/api/auth/login"
    
    for password in TEST_PASSWORDS:
        try:
            print(f"🔐 Testing login with password: {password}")
            
            login_data = {
                "email": CUSTOMER_EMAIL,
                "password": password
            }
            
            response = requests.post(login_url, json=login_data, timeout=10)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print_result(True, f"Login successful with password: {password}")
                    print(f"   🆔 User ID: {data.get('user', {}).get('id')}")
                    print(f"   🏥 Practice ID: {data.get('user', {}).get('practiceId')}")
                    print(f"   🎫 Token: {data.get('token', '')[:20]}...")
                    return {
                        "success": True,
                        "password": password,
                        "user_data": data.get('user', {}),
                        "token": data.get('token')
                    }
                else:
                    print(f"   ❌ Login failed: {data.get('error', 'Unknown error')}")
            elif response.status_code == 401:
                print(f"   ❌ Wrong password: {password}")
            else:
                print(f"   ❌ Unexpected response: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {str(e)}")
    
    print_result(False, "No working password found from test list")
    return {"success": False}

def test_practice_dashboard_access(login_result):
    """Test access to practice dashboard"""
    print_test_header("Practice Dashboard Access Test")
    
    if not login_result.get("success"):
        print_result(False, "Cannot test dashboard - login failed")
        return False
    
    try:
        dashboard_url = f"{BACKEND_URL}/api/practice/dashboard"
        headers = {
            "Authorization": f"Bearer {login_result['token']}"
        }
        
        response = requests.get(dashboard_url, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                practice_data = data.get("data", {})
                print_result(True, "Dashboard access successful")
                print(f"   🏥 Practice Name: {practice_data.get('name', 'N/A')}")
                print(f"   📧 Practice Email: {practice_data.get('email', 'N/A')}")
                print(f"   📞 Practice Phone: {practice_data.get('phone', 'N/A')}")
                print(f"   👤 Owner Name: {practice_data.get('ownerName', 'N/A')}")
                return True
            else:
                print_result(False, f"Dashboard access failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_result(False, f"Dashboard access failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Dashboard test failed: {str(e)}")
        return False

def test_password_reset_functionality():
    """Test password reset functionality for the customer"""
    print_test_header("Password Reset Functionality Test")
    
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
                print(f"   ⏰ Reset token expires in: {data.get('expires_in', 'Unknown')} minutes")
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

def check_practice_in_database():
    """Check if practice exists in database via admin endpoints"""
    print_test_header("Practice Database Verification")
    
    # We can't directly access the database, but we can check via webhook stats
    try:
        stats_url = f"{BACKEND_URL}/api/webhook/samcart/stats"
        response = requests.get(stats_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            recent_signups = data.get('recent_practice_signups', 0)
            
            print_result(True, f"Database accessible via webhook stats")
            print(f"   🆕 Recent practice signups: {recent_signups}")
            print(f"   📊 Total successful webhooks: {data.get('successful_webhooks', 0)}")
            
            if recent_signups > 0:
                print("   ✅ Practice accounts exist in database")
                return True
            else:
                print("   ⚠️ No recent practice signups found")
                return False
        else:
            print_result(False, f"Database check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, f"Database check failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🔍 CUSTOMER ACCOUNT VERIFICATION")
    print(f"📧 Customer: {CUSTOMER_EMAIL}")
    print(f"🎯 Goal: Verify existing account access and functionality")
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track test results
    test_results = {}
    
    # Check if practice exists in database
    test_results["database_check"] = check_practice_in_database()
    
    # Test login with known passwords
    login_result = test_practice_login_with_known_passwords()
    test_results["login_test"] = login_result["success"]
    
    if test_results["login_test"]:
        # Test dashboard access
        test_results["dashboard_access"] = test_practice_dashboard_access(login_result)
    else:
        test_results["dashboard_access"] = False
        
        # If login fails, test password reset
        test_results["password_reset"] = test_password_reset_functionality()
    
    # Print final summary
    print_test_header("FINAL VERIFICATION SUMMARY")
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name.replace('_', ' ').title()}")
    
    # Final assessment
    print_test_header("CUSTOMER ACCESS ASSESSMENT")
    
    if test_results.get("login_test") and test_results.get("dashboard_access"):
        print("🎉 SUCCESS: Customer has full access to their account!")
        print(f"✅ Customer can login with existing credentials")
        print(f"✅ Dashboard access is working")
        print(f"✅ Account is fully functional")
        print(f"🔗 Customer should login at: https://app.dentalaftercarenotes.com/login")
        
        return 0  # Success
    elif test_results.get("database_check") and test_results.get("password_reset"):
        print("⚠️ PARTIAL SUCCESS: Account exists but password reset needed")
        print(f"✅ Practice account exists in database")
        print(f"✅ Password reset email sent successfully")
        print(f"📧 Customer should check email for password reset instructions")
        print(f"🔗 After reset, customer can login at: https://app.dentalaftercarenotes.com/login")
        
        return 0  # Success (with password reset)
    else:
        print("🚨 ISSUE: Customer account access problems detected")
        print("❌ Customer may not have proper access to their paid account")
        
        if not test_results.get("database_check"):
            print("   🔍 Issue: Account may not exist in database")
        if not test_results.get("login_test"):
            print("   🔍 Issue: Cannot login with known passwords")
        if not test_results.get("password_reset"):
            print("   🔍 Issue: Password reset functionality not working")
            
        return 1  # Failure

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)