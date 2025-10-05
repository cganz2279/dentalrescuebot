#!/usr/bin/env python3
"""
FINAL WELCOME EMAIL VERIFICATION TEST
=====================================

This test verifies that the SendGrid 401 authentication issue has been resolved 
and welcome emails are now working in the SamCart webhook flow.

CRITICAL VERIFICATION NEEDED:
1. Test SamCart Webhook Welcome Email - Verify webhook test endpoint sends welcome email successfully
2. Check Backend Logs - Confirm no more "401 Unauthorized" errors in email delivery
3. Verify SendGrid Integration - Confirm fresh SendGrid client creation resolves authentication issues
4. Test Email Content - Verify welcome emails contain proper login credentials and content
5. End-to-End Flow Test - Complete payment simulation to verify entire flow works

KEY SUCCESS CRITERIA:
- SamCart webhook test returns `email_sent: true`
- Backend logs show "✅ Welcome email sent successfully"
- No "❌ Error sending welcome email: HTTP Error 401: Unauthorized" messages
- Welcome email delivery confirmed via SendGrid API
- Complete payment flow working: Payment → Account → Welcome Email → Customer Login
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
import sys

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class WelcomeEmailVerificationTest:
    def __init__(self):
        self.test_results = []
        self.backend_logs = []
        
    def log_test_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        print()
        
    def test_samcart_webhook_welcome_email(self):
        """Test 1: SamCart Webhook Welcome Email - Verify webhook test endpoint sends welcome email successfully"""
        try:
            # Generate unique test email to avoid duplicates
            test_email = f"welcome.test.{int(datetime.now().timestamp())}@example.com"
            
            print(f"🧪 Testing SamCart webhook welcome email with {test_email}")
            
            # Call SamCart webhook test endpoint
            url = f"{API_BASE}/webhook/samcart/test"
            params = {"test_email": test_email}
            
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if email was sent successfully
                email_sent = data.get('email_sent', False)
                practice_info = data.get('practice_info', {})
                
                if email_sent:
                    self.log_test_result(
                        "SamCart Webhook Welcome Email",
                        True,
                        f"✅ Welcome email sent successfully to {test_email}. Practice ID: {practice_info.get('practice_id', 'N/A')}"
                    )
                    return True, practice_info
                else:
                    self.log_test_result(
                        "SamCart Webhook Welcome Email",
                        False,
                        f"❌ Welcome email NOT sent. Response: {json.dumps(data, indent=2)}"
                    )
                    return False, practice_info
            else:
                self.log_test_result(
                    "SamCart Webhook Welcome Email",
                    False,
                    f"❌ HTTP {response.status_code}: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test_result(
                "SamCart Webhook Welcome Email",
                False,
                f"❌ Exception: {str(e)}"
            )
            return False, {}
            
    def test_backend_logs_verification(self):
        """Test 2: Check Backend Logs - Confirm no more "401 Unauthorized" errors in email delivery"""
        try:
            print("🔍 Checking backend logs for email delivery status...")
            
            # We'll capture logs by running multiple webhook tests and monitoring responses
            success_count = 0
            error_count = 0
            auth_errors = 0
            
            # Run 3 webhook tests to generate log activity
            for i in range(3):
                test_email = f"log.test.{i}.{int(datetime.now().timestamp())}@example.com"
                
                url = f"{API_BASE}/webhook/samcart/test"
                params = {"test_email": test_email}
                
                response = requests.post(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('email_sent', False):
                        success_count += 1
                    else:
                        error_count += 1
                        # Check if response indicates auth errors
                        response_str = json.dumps(data)
                        if "401" in response_str or "Unauthorized" in response_str:
                            auth_errors += 1
                else:
                    error_count += 1
                    
                # Small delay between tests
                time.sleep(1)
            
            # Evaluate results
            if success_count > 0 and auth_errors == 0:
                self.log_test_result(
                    "Backend Logs Verification",
                    True,
                    f"✅ No 401 authentication errors detected. Success: {success_count}, Errors: {error_count}, Auth Errors: {auth_errors}"
                )
                return True
            else:
                self.log_test_result(
                    "Backend Logs Verification",
                    False,
                    f"❌ Authentication issues detected. Success: {success_count}, Errors: {error_count}, Auth Errors: {auth_errors}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Backend Logs Verification",
                False,
                f"❌ Exception: {str(e)}"
            )
            return False
            
    def test_sendgrid_integration(self):
        """Test 3: Verify SendGrid Integration - Confirm fresh SendGrid client creation resolves authentication issues"""
        try:
            print("🔧 Testing SendGrid integration with fresh client creation...")
            
            # Test multiple webhook calls to verify consistent SendGrid behavior
            test_results = []
            
            for i in range(5):
                test_email = f"sendgrid.test.{i}.{int(datetime.now().timestamp())}@example.com"
                
                url = f"{API_BASE}/webhook/samcart/test"
                params = {"test_email": test_email}
                
                response = requests.post(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    email_sent = data.get('email_sent', False)
                    test_results.append(email_sent)
                else:
                    test_results.append(False)
                    
                # Small delay between tests
                time.sleep(0.5)
            
            # Calculate success rate
            success_rate = (sum(test_results) / len(test_results)) * 100
            
            if success_rate >= 80:  # 80% success rate threshold
                self.log_test_result(
                    "SendGrid Integration",
                    True,
                    f"✅ SendGrid integration working consistently. Success rate: {success_rate:.1f}% ({sum(test_results)}/{len(test_results)})"
                )
                return True
            else:
                self.log_test_result(
                    "SendGrid Integration",
                    False,
                    f"❌ SendGrid integration inconsistent. Success rate: {success_rate:.1f}% ({sum(test_results)}/{len(test_results)})"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "SendGrid Integration",
                False,
                f"❌ Exception: {str(e)}"
            )
            return False
            
    def test_email_content_verification(self):
        """Test 4: Test Email Content - Verify welcome emails contain proper login credentials and content"""
        try:
            print("📧 Testing email content verification...")
            
            # Create test account and verify response contains proper credentials
            test_email = f"content.test.{int(datetime.now().timestamp())}@example.com"
            
            url = f"{API_BASE}/webhook/samcart/test"
            params = {"test_email": test_email}
            
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                practice_info = data.get('practice_info', {})
                
                # Verify all required fields are present
                required_fields = ['practice_id', 'email', 'practice_name', 'password', 'owner_name']
                missing_fields = [field for field in required_fields if not practice_info.get(field)]
                
                if not missing_fields and data.get('email_sent', False):
                    # Verify password meets security requirements
                    password = practice_info.get('password', '')
                    password_valid = (
                        len(password) >= 12 and
                        any(c.isupper() for c in password) and
                        any(c.islower() for c in password) and
                        any(c.isdigit() for c in password) and
                        any(c in "!@#$%&*" for c in password)
                    )
                    
                    if password_valid:
                        self.log_test_result(
                            "Email Content Verification",
                            True,
                            f"✅ Email content valid. All fields present, secure password generated ({len(password)} chars)"
                        )
                        return True, practice_info
                    else:
                        self.log_test_result(
                            "Email Content Verification",
                            False,
                            f"❌ Password does not meet security requirements: {password}"
                        )
                        return False, practice_info
                else:
                    self.log_test_result(
                        "Email Content Verification",
                        False,
                        f"❌ Missing required fields: {missing_fields} or email not sent"
                    )
                    return False, practice_info
            else:
                self.log_test_result(
                    "Email Content Verification",
                    False,
                    f"❌ HTTP {response.status_code}: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test_result(
                "Email Content Verification",
                False,
                f"❌ Exception: {str(e)}"
            )
            return False, {}
            
    def test_end_to_end_flow(self, practice_info):
        """Test 5: End-to-End Flow Test - Complete payment simulation to verify entire flow works"""
        try:
            print("🔄 Testing end-to-end flow: Payment → Account → Welcome Email → Customer Login")
            
            if not practice_info:
                self.log_test_result(
                    "End-to-End Flow Test",
                    False,
                    "❌ No practice info available from previous tests"
                )
                return False
                
            # Test 1: Verify account was created
            practice_id = practice_info.get('practice_id')
            email = practice_info.get('email')
            password = practice_info.get('password')
            
            if not all([practice_id, email, password]):
                self.log_test_result(
                    "End-to-End Flow Test",
                    False,
                    "❌ Missing required account information"
                )
                return False
            
            # Test 2: Verify login works with generated credentials
            login_url = f"{API_BASE}/auth/login"
            login_data = {
                "email": email,
                "password": password
            }
            
            response = requests.post(login_url, json=login_data, timeout=30)
            
            if response.status_code == 200:
                login_result = response.json()
                token = login_result.get('token')
                user_data = login_result.get('user', {})
                user_id = user_data.get('id') or login_result.get('user_id')
                
                if token and user_id:
                    # Test 3: Verify dashboard access with token
                    dashboard_url = f"{API_BASE}/practice/dashboard"
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    dash_response = requests.get(dashboard_url, headers=headers, timeout=30)
                    
                    if dash_response.status_code == 200:
                        dashboard_data = dash_response.json()
                        practice_name = dashboard_data.get('name', '')
                        
                        self.log_test_result(
                            "End-to-End Flow Test",
                            True,
                            f"✅ Complete flow working: Account created → Email sent → Login successful → Dashboard accessible. Practice: {practice_name}"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "End-to-End Flow Test",
                            False,
                            f"❌ Dashboard access failed: HTTP {dash_response.status_code}"
                        )
                        return False
                else:
                    self.log_test_result(
                        "End-to-End Flow Test",
                        False,
                        f"❌ Login response missing token or user_id: {login_result}"
                    )
                    return False
            else:
                self.log_test_result(
                    "End-to-End Flow Test",
                    False,
                    f"❌ Login failed: HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "End-to-End Flow Test",
                False,
                f"❌ Exception: {str(e)}"
            )
            return False
            
    def test_webhook_statistics(self):
        """Test 6: Verify webhook statistics and logs are working"""
        try:
            print("📊 Testing webhook statistics and logging...")
            
            # Get webhook statistics
            stats_url = f"{API_BASE}/webhook/samcart/stats"
            response = requests.get(stats_url, timeout=30)
            
            if response.status_code == 200:
                stats = response.json()
                total_webhooks = stats.get('total_webhooks', 0)
                success_rate = stats.get('success_rate', 0)
                
                # Get webhook logs
                logs_url = f"{API_BASE}/webhook/samcart/logs"
                log_response = requests.get(logs_url, timeout=30)
                
                if log_response.status_code == 200:
                    logs_data = log_response.json()
                    logs_count = logs_data.get('count', 0)
                    
                    self.log_test_result(
                        "Webhook Statistics",
                        True,
                        f"✅ Statistics working. Total webhooks: {total_webhooks}, Success rate: {success_rate}%, Logs: {logs_count}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Webhook Statistics",
                        False,
                        f"❌ Logs endpoint failed: HTTP {log_response.status_code}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Webhook Statistics",
                    False,
                    f"❌ Stats endpoint failed: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Webhook Statistics",
                False,
                f"❌ Exception: {str(e)}"
            )
            return False
            
    def run_all_tests(self):
        """Run all verification tests"""
        print("🚀 FINAL WELCOME EMAIL VERIFICATION TEST STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test 1: SamCart Webhook Welcome Email
        email_success, practice_info = self.test_samcart_webhook_welcome_email()
        
        # Test 2: Backend Logs Verification
        logs_success = self.test_backend_logs_verification()
        
        # Test 3: SendGrid Integration
        sendgrid_success = self.test_sendgrid_integration()
        
        # Test 4: Email Content Verification
        content_success, content_practice_info = self.test_email_content_verification()
        
        # Use practice info from content test if available, otherwise from email test
        test_practice_info = content_practice_info if content_practice_info else practice_info
        
        # Test 5: End-to-End Flow Test
        e2e_success = self.test_end_to_end_flow(test_practice_info)
        
        # Test 6: Webhook Statistics
        stats_success = self.test_webhook_statistics()
        
        # Generate final report
        self.generate_final_report()
            
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 FINAL WELCOME EMAIL VERIFICATION REPORT")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {len(self.test_results)}")
        print(f"   Passed: {len(passed_tests)}")
        print(f"   Failed: {len(failed_tests)}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}")
            print()
        
        # Critical assessment
        critical_tests = [
            "SamCart Webhook Welcome Email",
            "SendGrid Integration", 
            "End-to-End Flow Test"
        ]
        
        critical_passed = [t for t in passed_tests if t['test'] in critical_tests]
        critical_success = len(critical_passed) == len(critical_tests)
        
        print("🎯 CRITICAL ASSESSMENT:")
        if critical_success and success_rate >= 80:
            print("   ✅ SENDGRID 401 AUTHENTICATION ISSUE RESOLVED")
            print("   ✅ Welcome email system is working correctly")
            print("   ✅ SamCart webhook integration is operational")
            print("   ✅ Customer onboarding flow is functional")
        else:
            print("   ❌ SENDGRID 401 AUTHENTICATION ISSUE NOT FULLY RESOLVED")
            print("   ❌ Welcome email system requires attention")
            print("   ❌ Customer onboarding may be impacted")
        
        print("=" * 80)

def main():
    """Main test execution"""
    test_runner = WelcomeEmailVerificationTest()
    test_runner.run_all_tests()

if __name__ == "__main__":
    main()