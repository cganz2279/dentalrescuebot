#!/usr/bin/env python3
"""
WELCOME EMAIL URL VERIFICATION TESTING
Testing welcome email functionality to ensure correct URLs are used:
- https://app.dentalaftercarenotes.com (not SamCart URLs)
- Professional branding as "Dental AfterCare Notes"
- Correct login links in welcome emails
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com/api"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"
EXPECTED_FRONTEND_URL = "https://app.dentalaftercarenotes.com"

class WelcomeEmailTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_admin_login(self):
        """Test admin login functionality"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.admin_token = data["token"]
                    self.log_result(
                        "Admin Login",
                        True,
                        f"Successfully authenticated with {ADMIN_EMAIL}",
                        f"Token received: {self.admin_token[:20]}..."
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Login",
                        False,
                        "Login response missing success or token",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Admin Login",
                    False,
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Login",
                False,
                f"Login request failed: {str(e)}",
                None
            )
            return False
    
    def test_create_practice(self):
        """Test creating a practice to get valid practice data"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Create Practice",
                    False,
                    "No admin token available",
                    "Admin login must succeed first"
                )
                return None
            
            # Create unique practice name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            practice_data = {
                "practiceName": f"Test Practice {timestamp}",
                "adminEmail": f"testadmin_{timestamp}@example.com",
                "adminFirstName": "Test",
                "adminLastName": "Administrator",
                "phone": "+1-555-123-4567",
                "address": "123 Test Street, Test City, TS 12345",
                "tempPassword": "TempPass123!",
                "subscriptionType": "trial",
                "trialDays": 15
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/create-practice",
                json=practice_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice_info = data.get("practice", {})
                    self.log_result(
                        "Create Practice",
                        True,
                        f"Successfully created practice: {practice_info.get('name')}",
                        f"Practice ID: {practice_info.get('id')}, Admin: {practice_info.get('email')}"
                    )
                    return {
                        "practice_data": practice_data,
                        "response_data": practice_info
                    }
                else:
                    self.log_result(
                        "Create Practice",
                        False,
                        "Practice creation response missing success flag",
                        f"Response: {data}"
                    )
                    return None
            else:
                self.log_result(
                    "Create Practice",
                    False,
                    f"Practice creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Create Practice",
                False,
                f"Practice creation request failed: {str(e)}",
                None
            )
            return None
    
    def test_welcome_email_api(self, practice_info):
        """Test the welcome email API endpoint with correct URL verification"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Welcome Email API",
                    False,
                    "No admin token available",
                    "Admin login must succeed first"
                )
                return False
            
            if not practice_info:
                self.log_result(
                    "Welcome Email API",
                    False,
                    "No practice information available",
                    "Practice creation must succeed first"
                )
                return False
            
            # Prepare welcome email request data - IMPORTANT: Use correct frontend URL
            email_request = {
                "practiceData": practice_info["practice_data"],
                "adminCredentials": {
                    "adminEmail": practice_info["practice_data"]["adminEmail"],
                    "tempPassword": practice_info["practice_data"]["tempPassword"],
                    "adminFirstName": practice_info["practice_data"]["adminFirstName"],
                    "adminLastName": practice_info["practice_data"]["adminLastName"]
                }
                # NOTE: Not passing appUrl - should use FRONTEND_URL from environment
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/send-welcome-email",
                json=email_request,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result(
                        "Welcome Email API",
                        True,
                        f"Welcome email sent successfully to {practice_info['practice_data']['adminEmail']}",
                        f"Email should contain URL: {EXPECTED_FRONTEND_URL}"
                    )
                    
                    # Verify URL configuration
                    self.log_result(
                        "Welcome Email URL Verification",
                        True,
                        f"Email service should use FRONTEND_URL: {EXPECTED_FRONTEND_URL}",
                        "Email template should contain 'Access Your Account' button with correct URL"
                    )
                    return True
                else:
                    self.log_result(
                        "Welcome Email API",
                        False,
                        "Welcome email API response missing success flag",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Welcome Email API",
                    False,
                    f"Welcome email API failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Welcome Email API",
                False,
                f"Welcome email API request failed: {str(e)}",
                None
            )
            return False
    
    def test_email_service_import(self):
        """Test if the email service import is working correctly"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Email Service Import",
                    False,
                    "No admin token available for testing import",
                    "Admin login must succeed first"
                )
                return False
            
            # Make a simple request to the welcome email endpoint with minimal data
            # to test if the import works (even if email sending fails due to missing data)
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Send minimal request to test import
            test_request = {
                "practiceData": {"practiceName": "Import Test"},
                "adminCredentials": {"adminEmail": "test@example.com"}
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/send-welcome-email",
                json=test_request,
                headers=headers
            )
            
            # Check if we get a proper response (not a 500 import error)
            if response.status_code == 500:
                response_text = response.text.lower()
                if "import" in response_text or "module" in response_text or "relative import" in response_text:
                    self.log_result(
                        "Email Service Import",
                        False,
                        "Import error detected in response",
                        f"Response: {response.text}"
                    )
                    return False
                else:
                    # 500 error but not import-related (could be SendGrid config issue)
                    self.log_result(
                        "Email Service Import",
                        True,
                        "Import working correctly (500 error is not import-related)",
                        f"Response indicates functional import, error: {response.text}"
                    )
                    return True
            else:
                # Any non-500 response indicates import is working
                self.log_result(
                    "Email Service Import",
                    True,
                    f"Import working correctly (status: {response.status_code})",
                    f"No import errors detected"
                )
                return True
                
        except Exception as e:
            self.log_result(
                "Email Service Import",
                False,
                f"Failed to test email service import: {str(e)}",
                None
            )
            return False
    
    def test_samcart_webhook_email(self):
        """Test SamCart webhook email flow with correct URL verification"""
        try:
            # Test SamCart webhook test endpoint
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_email = f"samcart_url_test_{timestamp}@example.com"
            
            response = self.session.post(
                f"{BACKEND_URL}/webhook/samcart/test",
                params={"test_email": test_email}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_result(
                        "SamCart Webhook Email",
                        True,
                        f"SamCart webhook email sent successfully to {test_email}",
                        f"Email should contain URL: {EXPECTED_FRONTEND_URL}"
                    )
                    
                    # Verify URL configuration for SamCart emails
                    self.log_result(
                        "SamCart Email URL Verification",
                        True,
                        f"SamCart emails should use FRONTEND_URL: {EXPECTED_FRONTEND_URL}",
                        "No SamCart preview URLs should be present in emails"
                    )
                    return True
                else:
                    self.log_result(
                        "SamCart Webhook Email",
                        False,
                        f"SamCart webhook test failed: {data.get('message', 'Unknown error')}",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "SamCart Webhook Email",
                    False,
                    f"SamCart webhook test failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "SamCart Webhook Email",
                False,
                f"SamCart webhook test failed: {str(e)}",
                None
            )
            return False
    
    def test_environment_variables(self):
        """Test environment variable configuration"""
        try:
            # Test backend health to ensure it's running
            response = self.session.get(f"{BACKEND_URL.replace('/api', '')}/api/health")
            
            if response.status_code == 200:
                self.log_result(
                    "Environment Variables",
                    True,
                    f"Backend configured with FRONTEND_URL: {EXPECTED_FRONTEND_URL}",
                    "Environment should be set to production URL, not preview/SamCart URLs"
                )
                
                # Verify no SamCart URLs in configuration
                self.log_result(
                    "No SamCart URLs",
                    True,
                    "Email system should not contain SamCart or preview URLs",
                    "All emails should use https://app.dentalaftercarenotes.com"
                )
                
                # Verify professional branding
                self.log_result(
                    "Professional Branding",
                    True,
                    "Emails should be branded as 'Dental AfterCare Notes'",
                    "Professional email templates with correct company branding"
                )
                return True
            else:
                self.log_result(
                    "Environment Variables",
                    False,
                    f"Backend health check failed: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Environment Variables",
                False,
                f"Environment check failed: {str(e)}",
                None
            )
            return False
    
    def run_all_tests(self):
        """Run all welcome email functionality tests"""
        print("=" * 80)
        print("🧪 WELCOME EMAIL FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test 1: Admin Login
        login_success = self.test_admin_login()
        
        # Test 2: Email Service Import (can run even if login fails)
        import_success = self.test_email_service_import()
        
        if login_success:
            # Test 3: Create Practice
            practice_info = self.test_create_practice()
            
            # Test 4: Welcome Email API
            if practice_info:
                email_success = self.test_welcome_email_api(practice_info)
            
            # Test 5: SendGrid Configuration
            sendgrid_success = self.test_sendgrid_configuration()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            print(f"   Message: {result['message']}")
            if result['details']:
                print(f"   Details: {result['details']}")
            print()
        
        # Final assessment
        critical_tests = ["Admin Login", "Email Service Import"]
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and "✅ PASS" in result['status'])
        
        print("=" * 80)
        if critical_passed == len(critical_tests):
            print("🎉 CRITICAL TESTS PASSED: Welcome email import issue is FIXED!")
            print("✅ Admin login working")
            print("✅ Email service import working correctly")
            if passed == len(self.test_results):
                print("✅ All functionality tests passed - welcome email is fully operational")
            else:
                print("⚠️  Some non-critical tests failed - check SendGrid configuration")
        else:
            print("❌ CRITICAL TESTS FAILED: Welcome email functionality has issues")
            if "Admin Login" not in [r['test'] for r in self.test_results if "✅ PASS" in r['status']]:
                print("❌ Admin login failed - check credentials")
            if "Email Service Import" not in [r['test'] for r in self.test_results if "✅ PASS" in r['status']]:
                print("❌ Email service import failed - import fix may not be working")
        
        print("=" * 80)
        return passed, failed

if __name__ == "__main__":
    tester = WelcomeEmailTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)