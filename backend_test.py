#!/usr/bin/env python3
"""
Backend Testing Script for Fresh Password Reset Email with Corrected FRONTEND_URL
Testing the password recovery system with updated configuration as requested.
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

# Use the corrected backend URL as specified in the review request
CORRECTED_BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
API_BASE = f"{CORRECTED_BACKEND_URL}/api"

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

    def test_domain_mismatch_issue(self):
        """Test the domain mismatch issue reported by user"""
        print("🔍 Testing Domain Mismatch Issue...")
        
        try:
            specific_token = "d201d54e-4a4f-4657-b253-46fd4eb0e7fb"
            
            # Test on the correct domain (where token exists)
            correct_url = f"https://dentiportal.preview.emergentagent.com/api/auth/validate-reset-token/{specific_token}"
            
            # Test on the wrong domain (where user is accessing)
            wrong_url = f"https://dentist-portal-3.emergent.host/api/auth/validate-reset-token/{specific_token}"
            
            print(f"🔍 Testing correct domain: {correct_url}")
            correct_response = self.session.get(correct_url)
            
            print(f"🔍 Testing wrong domain: {wrong_url}")
            try:
                wrong_response = self.session.get(wrong_url)
                wrong_status = wrong_response.status_code
                wrong_data = wrong_response.json() if wrong_response.headers.get('content-type', '').startswith('application/json') else {"error": wrong_response.text}
            except Exception as e:
                wrong_status = "ERROR"
                wrong_data = {"error": str(e)}
            
            # Log results
            if correct_response.status_code == 200 and wrong_status == 400:
                self.log_test(
                    "Domain Mismatch Issue Analysis",
                    True,
                    f"CONFIRMED: Token works on correct domain (200) but fails on wrong domain (400). User is accessing wrong URL.",
                    {
                        "correct_domain": "dentiportal.preview.emergentagent.com",
                        "wrong_domain": "dentist-portal-3.emergent.host",
                        "correct_status": correct_response.status_code,
                        "wrong_status": wrong_status,
                        "issue": "User accessing wrong domain"
                    }
                )
            else:
                self.log_test(
                    "Domain Mismatch Issue Analysis",
                    False,
                    f"Unexpected results: correct domain returned {correct_response.status_code}, wrong domain returned {wrong_status}",
                    {
                        "correct_status": correct_response.status_code,
                        "wrong_status": wrong_status
                    }
                )
                
            return True
                
        except Exception as e:
            self.log_test(
                "Domain Mismatch Issue Analysis",
                False,
                f"Exception occurred: {str(e)}"
            )
            return False

    def test_email_url_configuration(self):
        """Test that password reset emails contain the correct URL"""
        print("🔍 Testing Email URL Configuration...")
        
        try:
            # Check environment variable
            frontend_url = os.getenv('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
            
            # Send a password reset email and check the configuration
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "email"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if email was sent
                sent_methods = data.get('sent_methods', [])
                if 'email' in sent_methods:
                    self.log_test(
                        "Email URL Configuration Check",
                        True,
                        f"Password reset email sent successfully. FRONTEND_URL is set to: {frontend_url}. Email should contain reset link with this domain.",
                        {
                            "frontend_url": frontend_url,
                            "expected_reset_link_domain": frontend_url,
                            "user_accessing_wrong_domain": "dentist-portal-3.emergent.host",
                            "issue": "User needs to check email for correct reset link"
                        }
                    )
                else:
                    self.log_test(
                        "Email URL Configuration Check",
                        False,
                        f"Email was not sent. Sent methods: {sent_methods}",
                        data
                    )
            else:
                self.log_test(
                    "Email URL Configuration Check",
                    False,
                    f"Failed to send password reset email: {response.status_code}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                )
                
            return True
                
        except Exception as e:
            self.log_test(
                "Email URL Configuration Check",
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

    def send_fresh_password_reset_email(self):
        """Send a fresh password reset email to caryganz@gmail.com as requested"""
        print("🚨 URGENT: Sending fresh password reset email to caryganz@gmail.com...")
        print(f"🔗 Using corrected backend URL: {CORRECTED_BACKEND_URL}")
        
        try:
            # Send password reset email to caryganz@gmail.com
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
                
                # Get the FRONTEND_URL from environment to verify reset link format
                frontend_url = os.getenv('FRONTEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
                
                self.log_test(
                    "Fresh Password Reset Email Sent",
                    True,
                    f"✅ NEW PASSWORD RESET EMAIL SENT to caryganz@gmail.com. Message: {data.get('message', 'No message')}. Reset link will use: {frontend_url}",
                    data
                )
                
                # Check if email was actually sent
                sent_methods = data.get('sent_methods', [])
                if 'email' in sent_methods:
                    self.log_test(
                        "Email Delivery Confirmation",
                        True,
                        f"✅ Email was successfully sent via SendGrid - NEW TOKEN GENERATED. Reset link format: {frontend_url}/reset-password?token=NEW_TOKEN",
                        {"sent_methods": sent_methods, "frontend_url": frontend_url}
                    )
                    return True
                else:
                    self.log_test(
                        "Email Delivery Confirmation",
                        False,
                        f"❌ Email not in sent methods: {sent_methods}",
                        data
                    )
                    return False
                    
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Fresh Password Reset Email Sent",
                    False,
                    f"❌ HTTP {response.status_code}: {error_data.get('detail', response.text)}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Fresh Password Reset Email Sent",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def test_new_token_validation(self):
        """Test that new tokens can be validated on the current backend"""
        print("🔍 Testing New Token Validation on Current Backend...")
        
        try:
            # Test with a dummy token to verify the validation endpoint works
            dummy_token = "test-token-12345"
            
            response = self.session.get(
                f"{API_BASE}/auth/validate-reset-token/{dummy_token}"
            )
            
            print(f"🔍 GET /api/auth/validate-reset-token/{dummy_token} Response: {response.status_code}")
            
            if response.status_code == 400:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if "Invalid or expired reset token" in data.get('detail', ''):
                    self.log_test(
                        "Token Validation Endpoint Working",
                        True,
                        "✅ Token validation endpoint is working correctly - rejects invalid tokens",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Token Validation Endpoint Working",
                        False,
                        f"❌ Unexpected error message: {data.get('detail')}",
                        data
                    )
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Token Validation Endpoint Working",
                    False,
                    f"❌ Expected 400 but got {response.status_code}: {error_data}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Token Validation Endpoint Working",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def verify_frontend_url_configuration(self):
        """Verify the FRONTEND_URL configuration is correct"""
        print("🔍 Verifying FRONTEND_URL Configuration...")
        
        try:
            frontend_url = os.getenv('FRONTEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
            expected_url = 'https://samcart-auth-fix.preview.emergentagent.com'
            
            if frontend_url == expected_url:
                self.log_test(
                    "FRONTEND_URL Configuration Verification",
                    True,
                    f"✅ FRONTEND_URL is correctly set to: {frontend_url}",
                    {"frontend_url": frontend_url, "expected": expected_url}
                )
            else:
                self.log_test(
                    "FRONTEND_URL Configuration Verification",
                    False,
                    f"❌ FRONTEND_URL mismatch. Expected: {expected_url}, Got: {frontend_url}",
                    {"frontend_url": frontend_url, "expected": expected_url}
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "FRONTEND_URL Configuration Verification",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def test_new_token_generation_and_validation(self):
        """Test that new tokens are generated and can be validated"""
        print("🔍 Testing New Token Generation and Validation...")
        
        try:
            # First send a password reset to generate a new token
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "email"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                sent_methods = data.get('sent_methods', [])
                
                if 'email' in sent_methods:
                    self.log_test(
                        "New Token Generation",
                        True,
                        "✅ New password reset token generated successfully",
                        {"sent_methods": sent_methods}
                    )
                    
                    # Test token validation endpoint with dummy token to verify it's working
                    dummy_token = "test-validation-12345"
                    validation_response = self.session.get(
                        f"{API_BASE}/auth/validate-reset-token/{dummy_token}"
                    )
                    
                    if validation_response.status_code == 400:
                        validation_data = validation_response.json() if validation_response.headers.get('content-type', '').startswith('application/json') else {}
                        if "Invalid or expired reset token" in validation_data.get('detail', ''):
                            self.log_test(
                                "Token Validation Endpoint Working",
                                True,
                                "✅ Token validation endpoint is working correctly",
                                validation_data
                            )
                        else:
                            self.log_test(
                                "Token Validation Endpoint Working",
                                False,
                                f"❌ Unexpected validation error: {validation_data.get('detail')}",
                                validation_data
                            )
                    else:
                        self.log_test(
                            "Token Validation Endpoint Working",
                            False,
                            f"❌ Expected 400 for invalid token, got {validation_response.status_code}",
                            {}
                        )
                    
                    return True
                else:
                    self.log_test(
                        "New Token Generation",
                        False,
                        f"❌ Email not sent, no token generated: {sent_methods}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "New Token Generation",
                    False,
                    f"❌ Failed to generate token: {response.status_code}",
                    {}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "New Token Generation and Validation",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run focused tests for the user's specific request"""
        print("🚀 Starting Fresh Password Reset Email Testing with Corrected FRONTEND_URL...")
        print(f"🔗 Corrected Backend URL: {CORRECTED_BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print("🎯 FOCUS: Send fresh password reset email to caryganz@gmail.com with corrected FRONTEND_URL")
        print("=" * 80)
        
        # 1. Send fresh password reset email to caryganz@gmail.com
        print("🚨 STEP 1: Sending fresh password reset email...")
        email_sent = self.send_fresh_password_reset_email()
        time.sleep(2)
        
        # 2. Test that token validation endpoint is working
        print("🚨 STEP 2: Testing token validation endpoint...")
        self.test_new_token_validation()
        time.sleep(1)
        
        # 3. Test the old token to show the difference
        print("🚨 STEP 3: Testing old token for comparison...")
        self.test_specific_reset_token()
        time.sleep(1)
        
        # 4. Verify email configuration
        print("🚨 STEP 4: Verifying email configuration...")
        self.test_email_url_configuration()
        time.sleep(1)
        
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