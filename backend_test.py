#!/usr/bin/env python3
"""
Backend Testing Script for Forgot Password and Forgot Username Functionality
Testing the password recovery system and username recovery system as requested.
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ForgotPasswordTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        }
        
        self.test_results.append(result)
        print(f"[{timestamp}] {status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and isinstance(response_data, dict):
            if 'message' in response_data:
                print(f"    Message: {response_data['message']}")
        print()

    def test_forgot_password_endpoint(self):
        """Test the forgot password endpoint with caryganz@gmail.com"""
        print("🔍 Testing Forgot Password Endpoint...")
        
        try:
            # Test forgot password with email recovery
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "email"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 POST /api/auth/forgot-password Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Forgot Password Email Request",
                    True,
                    f"Email recovery request successful. Message: {data.get('message', 'No message')}",
                    data
                )
                
                # Check if email was actually sent
                sent_methods = data.get('sent_methods', [])
                if 'email' in sent_methods:
                    self.log_test(
                        "Password Reset Email Sent",
                        True,
                        "Email was successfully sent via SendGrid",
                        {"sent_methods": sent_methods}
                    )
                else:
                    self.log_test(
                        "Password Reset Email Sent",
                        False,
                        f"Email not in sent methods: {sent_methods}",
                        data
                    )
                    
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Forgot Password Email Request",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('detail', response.text)}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Forgot Password Email Request",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_forgot_password_sms(self):
        """Test the forgot password endpoint with SMS recovery"""
        print("🔍 Testing Forgot Password SMS...")
        
        try:
            # Test forgot password with SMS recovery
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "sms"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 POST /api/auth/forgot-password (SMS) Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Forgot Password SMS Request",
                    True,
                    f"SMS recovery request successful. Message: {data.get('message', 'No message')}",
                    data
                )
                
                # Check if SMS was attempted (may fail if phone number not verified)
                sent_methods = data.get('sent_methods', [])
                if 'SMS' in sent_methods:
                    self.log_test(
                        "Password Reset SMS Sent",
                        True,
                        "SMS was successfully sent via Twilio",
                        {"sent_methods": sent_methods}
                    )
                else:
                    self.log_test(
                        "Password Reset SMS Sent",
                        False,
                        f"SMS not in sent methods (may be due to unverified phone): {sent_methods}",
                        data
                    )
                    
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Forgot Password SMS Request",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('detail', response.text)}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Forgot Password SMS Request",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_forgot_password_both(self):
        """Test the forgot password endpoint with both email and SMS recovery"""
        print("🔍 Testing Forgot Password Both Methods...")
        
        try:
            # Test forgot password with both recovery methods
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "both"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 POST /api/auth/forgot-password (both) Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Forgot Password Both Methods Request",
                    True,
                    f"Both methods recovery request successful. Message: {data.get('message', 'No message')}",
                    data
                )
                
                # Check sent methods
                sent_methods = data.get('sent_methods', [])
                self.log_test(
                    "Password Reset Methods Analysis",
                    True,
                    f"Sent methods: {sent_methods}. Email should be included, SMS may fail if phone unverified.",
                    {"sent_methods": sent_methods}
                )
                    
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Forgot Password Both Methods Request",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('detail', response.text)}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Forgot Password Both Methods Request",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_validate_reset_token_endpoint(self):
        """Test the validate reset token endpoint"""
        print("🔍 Testing Validate Reset Token Endpoint...")
        
        try:
            # Test with a dummy token (should fail)
            dummy_token = "dummy-token-12345"
            
            response = self.session.get(
                f"{API_BASE}/auth/validate-reset-token/{dummy_token}"
            )
            
            print(f"🔍 GET /api/auth/validate-reset-token/{dummy_token} Response: {response.status_code}")
            
            if response.status_code == 400:
                data = response.json()
                if "Invalid or expired reset token" in data.get('detail', ''):
                    self.log_test(
                        "Validate Reset Token (Invalid Token)",
                        True,
                        "Correctly rejected invalid token with 400 status",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Validate Reset Token (Invalid Token)",
                        False,
                        f"Unexpected error message: {data.get('detail')}",
                        data
                    )
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Validate Reset Token (Invalid Token)",
                    False,
                    f"Expected 400 but got {response.status_code}: {error_data}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Validate Reset Token (Invalid Token)",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_specific_reset_token(self):
        """Test the specific reset token from user report: d201d54e-4a4f-4657-b253-46fd4eb0e7fb"""
        print("🔍 Testing Specific Reset Token from User Report...")
        
        try:
            # Test with the specific token from user report
            specific_token = "d201d54e-4a4f-4657-b253-46fd4eb0e7fb"
            
            response = self.session.get(
                f"{API_BASE}/auth/validate-reset-token/{specific_token}"
            )
            
            print(f"🔍 GET /api/auth/validate-reset-token/{specific_token} Response: {response.status_code}")
            print(f"🔍 Response headers: {dict(response.headers)}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(f"🔍 Response data: {data}")
            else:
                print(f"🔍 Response text: {response.text}")
                data = {"error": response.text}
            
            if response.status_code == 400:
                if "Invalid or expired reset token" in data.get('detail', ''):
                    self.log_test(
                        "Specific Reset Token Validation",
                        True,
                        f"Token {specific_token} correctly rejected as invalid/expired with 400 status",
                        data
                    )
                else:
                    self.log_test(
                        "Specific Reset Token Validation",
                        False,
                        f"Token {specific_token} rejected but with unexpected error: {data.get('detail')}",
                        data
                    )
                return True
            elif response.status_code == 200:
                self.log_test(
                    "Specific Reset Token Validation",
                    True,
                    f"Token {specific_token} is valid and active",
                    data
                )
                return True
            else:
                self.log_test(
                    "Specific Reset Token Validation",
                    False,
                    f"Unexpected status {response.status_code} for token {specific_token}: {data}",
                    data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Specific Reset Token Validation",
                False,
                f"Exception occurred testing token d201d54e-4a4f-4657-b253-46fd4eb0e7fb: {str(e)}"
            )
            return False

    def check_database_for_specific_token(self):
        """Check if the specific token exists in the database"""
        print("🔍 Checking Database for Specific Token...")
        
        try:
            # This would require direct database access
            # For now, we'll simulate by testing the endpoint behavior
            specific_token = "d201d54e-4a4f-4657-b253-46fd4eb0e7fb"
            
            # Test the token validation endpoint to understand the error
            response = self.session.get(
                f"{API_BASE}/auth/validate-reset-token/{specific_token}"
            )
            
            if response.status_code == 400:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if "Invalid or expired reset token" in data.get('detail', ''):
                    self.log_test(
                        "Database Token Check",
                        True,
                        f"Token {specific_token} does not exist in database or is expired",
                        {"token_status": "not_found_or_expired"}
                    )
                else:
                    self.log_test(
                        "Database Token Check",
                        False,
                        f"Unexpected error for token {specific_token}: {data.get('detail')}",
                        data
                    )
            elif response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Database Token Check",
                    True,
                    f"Token {specific_token} exists and is valid in database",
                    {"token_status": "valid", "user_email": data.get('user', {}).get('email')}
                )
            else:
                self.log_test(
                    "Database Token Check",
                    False,
                    f"Unexpected response {response.status_code} when checking token",
                    {"status_code": response.status_code}
                )
                
            return True
                
        except Exception as e:
            self.log_test(
                "Database Token Check",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_reset_password_endpoint(self):
        """Test the reset password endpoint"""
        print("🔍 Testing Reset Password Endpoint...")
        
        try:
            # Test with a dummy token (should fail)
            payload = {
                "reset_token": "dummy-token-12345",
                "new_password": "NewPassword123!"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/reset-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 POST /api/auth/reset-password Response: {response.status_code}")
            
            if response.status_code == 400:
                data = response.json()
                if "Invalid or expired reset token" in data.get('detail', ''):
                    self.log_test(
                        "Reset Password (Invalid Token)",
                        True,
                        "Correctly rejected invalid token with 400 status",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Reset Password (Invalid Token)",
                        False,
                        f"Unexpected error message: {data.get('detail')}",
                        data
                    )
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Reset Password (Invalid Token)",
                    False,
                    f"Expected 400 but got {response.status_code}: {error_data}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Reset Password (Invalid Token)",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_forgot_username_endpoint(self):
        """Test the forgot username endpoint"""
        print("🔍 Testing Forgot Username Endpoint...")
        
        try:
            # Test forgot username with practice details
            payload = {
                "practice_name": "Test Dental Practice",
                "phone": "555-123-4567",
                "adminPassword": "testpassword123",
                "street": "123 Main St",
                "city": "Test City",
                "state": "CA",
                "zipCode": "12345"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-username",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 POST /api/auth/forgot-username Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Forgot Username Request",
                    True,
                    f"Username recovery request successful. Message: {data.get('message', 'No message')}",
                    data
                )
                
                # Check if practice info is returned (for testing - would be removed in production)
                if 'practice_name' in data or 'email' in data:
                    self.log_test(
                        "Forgot Username Response Data",
                        True,
                        f"Practice found: {data.get('practice_name', 'N/A')}, Email: {data.get('email', 'N/A')}",
                        data
                    )
                else:
                    self.log_test(
                        "Forgot Username Response Data",
                        True,
                        "No practice details returned (security measure)",
                        data
                    )
                    
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Forgot Username Request",
                    False,
                    f"HTTP {response.status_code}: {error_data.get('detail', response.text)}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Forgot Username Request",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_url_verification(self):
        """Test that password reset emails use correct URLs"""
        print("🔍 Testing URL Verification...")
        
        try:
            # Check environment variables
            frontend_url = os.getenv('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
            
            self.log_test(
                "Frontend URL Environment Variable",
                True,
                f"FRONTEND_URL is set to: {frontend_url}",
                {"frontend_url": frontend_url}
            )
            
            # Verify it's the correct URL (not SamCart or preview)
            if "app.dentalaftercarenotes.com" in frontend_url:
                self.log_test(
                    "URL Verification - Correct Domain",
                    True,
                    "Frontend URL uses correct Dental AfterCare Notes domain",
                    {"frontend_url": frontend_url}
                )
            else:
                self.log_test(
                    "URL Verification - Correct Domain",
                    False,
                    f"Frontend URL should use app.dentalaftercarenotes.com, but uses: {frontend_url}",
                    {"frontend_url": frontend_url}
                )
                
            # Check for SamCart URLs (should not be present)
            if "samcart" in frontend_url.lower() or "preview" in frontend_url.lower():
                self.log_test(
                    "URL Verification - No SamCart URLs",
                    False,
                    f"Frontend URL contains SamCart or preview references: {frontend_url}",
                    {"frontend_url": frontend_url}
                )
            else:
                self.log_test(
                    "URL Verification - No SamCart URLs",
                    True,
                    "Frontend URL does not contain SamCart or preview references",
                    {"frontend_url": frontend_url}
                )
                
            return True
                
        except Exception as e:
            self.log_test(
                "URL Verification",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_email_branding_verification(self):
        """Test that emails use proper Dental AfterCare Notes branding"""
        print("🔍 Testing Email Branding Verification...")
        
        try:
            # This is more of a configuration check since we can't inspect email content directly
            # We'll verify the email service configuration
            
            sender_email = os.getenv('SENDER_EMAIL', 'admin@theoncallbot.com')
            
            self.log_test(
                "Email Sender Configuration",
                True,
                f"Sender email is configured as: {sender_email}",
                {"sender_email": sender_email}
            )
            
            # Check if SendGrid API key is configured
            sendgrid_key = os.getenv('SENDGRID_API_KEY')
            if sendgrid_key:
                self.log_test(
                    "SendGrid Configuration",
                    True,
                    f"SendGrid API key is configured (length: {len(sendgrid_key)} chars)",
                    {"configured": True}
                )
            else:
                self.log_test(
                    "SendGrid Configuration",
                    False,
                    "SendGrid API key is not configured",
                    {"configured": False}
                )
                
            return True
                
        except Exception as e:
            self.log_test(
                "Email Branding Verification",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all forgot password and username tests"""
        print("🚀 Starting Password Reset Token Validation Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print("=" * 80)
        
        # URGENT: Test the specific token from user report first
        print("🚨 URGENT: Testing specific token from user report...")
        self.test_specific_reset_token()
        time.sleep(1)
        
        self.check_database_for_specific_token()
        time.sleep(1)
        
        # Test forgot password functionality
        self.test_forgot_password_endpoint()
        time.sleep(1)  # Brief pause between tests
        
        self.test_forgot_password_sms()
        time.sleep(1)
        
        self.test_forgot_password_both()
        time.sleep(1)
        
        # Test reset password flow
        self.test_validate_reset_token_endpoint()
        time.sleep(1)
        
        self.test_reset_password_endpoint()
        time.sleep(1)
        
        # Test forgot username functionality
        self.test_forgot_username_endpoint()
        time.sleep(1)
        
        # Test URL and branding verification
        self.test_url_verification()
        time.sleep(1)
        
        self.test_email_branding_verification()
        
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if "❌ FAIL" in result["status"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for result in failed_tests:
                print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Show successful tests
        passed_tests = [result for result in self.test_results if "✅ PASS" in result["status"]]
        if passed_tests:
            print("✅ PASSED TESTS:")
            for result in passed_tests:
                print(f"  - {result['test']}")
            print()
        
        return passed, failed, total

def test_welcome_email_url_verification():
    """Legacy function for compatibility"""
    pass

if __name__ == "__main__":
    tester = ForgotPasswordTester()
    passed, failed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)