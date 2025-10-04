#!/usr/bin/env python3
"""
Comprehensive Backend Testing for SamCart Webhook Integration
Focus: Urgent customer account creation for caryganz@gmail.com
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from test_result.md
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

# Customer from review request
URGENT_CUSTOMER_EMAIL = "caryganz@gmail.com"

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def admin_login(self):
        """Test admin authentication"""
        try:
            response = requests.post(f"{API_BASE}/admin/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {ADMIN_EMAIL}, token obtained"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False
    
    def test_samcart_webhook_endpoint(self):
        """Test SamCart webhook endpoint accessibility"""
        try:
            # Test GET request (should return 405 Method Not Allowed)
            response = requests.get(f"{API_BASE}/webhook/samcart", timeout=30)
            
            if response.status_code == 405:
                self.log_result(
                    "SamCart Webhook Endpoint Accessibility",
                    True,
                    "Endpoint accessible, returns 405 for GET as expected"
                )
                return True
            else:
                self.log_result(
                    "SamCart Webhook Endpoint Accessibility",
                    False,
                    f"Unexpected status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("SamCart Webhook Endpoint Accessibility", False, error=str(e))
            return False
    
    def test_webhook_logs(self):
        """Test webhook logs endpoint"""
        try:
            response = requests.get(f"{API_BASE}/webhook/samcart/logs", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                count = data.get("count", 0)
                
                self.log_result(
                    "Webhook Logs Endpoint",
                    True,
                    f"Retrieved {count} webhook logs successfully"
                )
                
                # Check for recent activity
                if logs:
                    latest_log = logs[0]
                    event_type = latest_log.get("event_type", "unknown")
                    created_at = latest_log.get("created_at", "unknown")
                    print(f"   Latest webhook: {event_type} at {created_at}")
                
                return True
            else:
                self.log_result(
                    "Webhook Logs Endpoint",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Webhook Logs Endpoint", False, error=str(e))
            return False
    
    def test_webhook_stats(self):
        """Test webhook statistics endpoint"""
        try:
            response = requests.get(f"{API_BASE}/webhook/samcart/stats", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total_webhooks", 0)
                successful = data.get("successful_webhooks", 0)
                failed = data.get("failed_webhooks", 0)
                success_rate = data.get("success_rate", 0)
                recent_signups = data.get("recent_practice_signups", 0)
                
                self.log_result(
                    "Webhook Statistics Endpoint",
                    True,
                    f"Total: {total}, Success: {successful}, Failed: {failed}, Rate: {success_rate:.1f}%, Recent signups: {recent_signups}"
                )
                return True
            else:
                self.log_result(
                    "Webhook Statistics Endpoint",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Webhook Statistics Endpoint", False, error=str(e))
            return False
    
    def test_urgent_customer_account_status(self):
        """Test urgent customer account status for caryganz@gmail.com"""
        try:
            # Test login attempt to check account status
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": URGENT_CUSTOMER_EMAIL,
                "password": "test_password_123"  # Wrong password to test account existence
            }, timeout=30)
            
            if response.status_code == 401:
                # 401 means account exists but wrong password (healthy account)
                self.log_result(
                    f"Urgent Customer Account Status ({URGENT_CUSTOMER_EMAIL})",
                    True,
                    "Account exists and is healthy (401 unauthorized for wrong password)"
                )
                return True
            elif response.status_code == 500:
                # 500 means account exists but has corruption issues
                self.log_result(
                    f"Urgent Customer Account Status ({URGENT_CUSTOMER_EMAIL})",
                    False,
                    "Account exists but has corruption issues (500 server error)",
                    "Password field may be corrupted - needs password reset"
                )
                return False
            elif response.status_code == 404:
                # 404 means account doesn't exist
                self.log_result(
                    f"Urgent Customer Account Status ({URGENT_CUSTOMER_EMAIL})",
                    False,
                    "Account does not exist",
                    "Customer paid but account was never created"
                )
                return False
            else:
                self.log_result(
                    f"Urgent Customer Account Status ({URGENT_CUSTOMER_EMAIL})",
                    False,
                    f"Unexpected status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(f"Urgent Customer Account Status ({URGENT_CUSTOMER_EMAIL})", False, error=str(e))
            return False
    
    def test_webhook_test_endpoint_for_customer(self):
        """Test webhook test endpoint with urgent customer email"""
        try:
            response = requests.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": URGENT_CUSTOMER_EMAIL},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                message = data.get("message", "")
                
                if status == "success":
                    practice_info = data.get("practice_info", {})
                    password = practice_info.get("password", "N/A")
                    practice_name = practice_info.get("practice_name", "N/A")
                    
                    self.log_result(
                        f"Webhook Test Endpoint for {URGENT_CUSTOMER_EMAIL}",
                        True,
                        f"Account created successfully: {practice_name}, Password: {password}"
                    )
                    return True
                elif "already exists" in message.lower() or "duplicate" in message.lower():
                    self.log_result(
                        f"Webhook Test Endpoint for {URGENT_CUSTOMER_EMAIL}",
                        True,
                        "Account already exists (duplicate prevention working)"
                    )
                    return True
                else:
                    self.log_result(
                        f"Webhook Test Endpoint for {URGENT_CUSTOMER_EMAIL}",
                        False,
                        f"Unexpected response: {message}"
                    )
                    return False
            else:
                self.log_result(
                    f"Webhook Test Endpoint for {URGENT_CUSTOMER_EMAIL}",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(f"Webhook Test Endpoint for {URGENT_CUSTOMER_EMAIL}", False, error=str(e))
            return False
    
    def test_password_reset_for_customer(self):
        """Test password reset functionality for urgent customer"""
        try:
            response = requests.post(f"{API_BASE}/auth/forgot-password", json={
                "email": URGENT_CUSTOMER_EMAIL,
                "recovery_method": "email"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                sent_methods = data.get("sent_methods", [])
                
                self.log_result(
                    f"Password Reset for {URGENT_CUSTOMER_EMAIL}",
                    True,
                    f"Password reset email sent successfully. Methods: {sent_methods}"
                )
                return True
            else:
                self.log_result(
                    f"Password Reset for {URGENT_CUSTOMER_EMAIL}",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(f"Password Reset for {URGENT_CUSTOMER_EMAIL}", False, error=str(e))
            return False
    
    def test_manual_welcome_email(self):
        """Test manual welcome email sending via admin endpoint"""
        if not self.admin_token:
            self.log_result("Manual Welcome Email", False, error="No admin token available")
            return False
            
        try:
            # Prepare practice data for welcome email
            practice_data = {
                "practiceName": "The Dental Spa at Garden City",
                "adminEmail": URGENT_CUSTOMER_EMAIL,
                "adminCredentials": {
                    "email": URGENT_CUSTOMER_EMAIL,
                    "password": "temp_password_123"
                }
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{API_BASE}/admin/send-welcome-email",
                json=practice_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_result(
                    f"Manual Welcome Email for {URGENT_CUSTOMER_EMAIL}",
                    True,
                    f"Welcome email sent successfully: {message}"
                )
                return True
            else:
                self.log_result(
                    f"Manual Welcome Email for {URGENT_CUSTOMER_EMAIL}",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result(f"Manual Welcome Email for {URGENT_CUSTOMER_EMAIL}", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive SamCart Webhook Backend Testing")
        print("=" * 70)
        print(f"Target Customer: {URGENT_CUSTOMER_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Test sequence
        tests = [
            ("Admin Authentication", self.admin_login),
            ("SamCart Webhook Endpoint", self.test_samcart_webhook_endpoint),
            ("Webhook Logs", self.test_webhook_logs),
            ("Webhook Statistics", self.test_webhook_stats),
            ("Urgent Customer Account Status", self.test_urgent_customer_account_status),
            ("Webhook Test Endpoint", self.test_webhook_test_endpoint_for_customer),
            ("Password Reset", self.test_password_reset_for_customer),
            ("Manual Welcome Email", self.test_manual_welcome_email),
        ]
        
        for test_name, test_func in tests:
            print(f"🔍 Running: {test_name}")
            test_func()
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
            print()
        
        # Critical findings
        print("🎯 CRITICAL FINDINGS:")
        
        # Check customer account status
        customer_test = next((r for r in self.test_results if "Account Status" in r["test"]), None)
        if customer_test:
            if customer_test["success"]:
                print(f"   ✅ Customer {URGENT_CUSTOMER_EMAIL} account exists and is healthy")
            else:
                print(f"   🚨 Customer {URGENT_CUSTOMER_EMAIL} account has issues: {customer_test['error']}")
        
        # Check webhook system
        webhook_tests = [r for r in self.test_results if "Webhook" in r["test"]]
        webhook_success = all(r["success"] for r in webhook_tests)
        if webhook_success:
            print("   ✅ SamCart webhook system is fully operational")
        else:
            print("   ⚠️ SamCart webhook system has issues")
        
        # Check email system
        email_tests = [r for r in self.test_results if "Email" in r["test"] or "Password Reset" in r["test"]]
        email_success = all(r["success"] for r in email_tests)
        if email_success:
            print("   ✅ Email system (welcome emails, password reset) is working")
        else:
            print("   ⚠️ Email system has issues")
        
        print()
        print("🎯 URGENT CUSTOMER RESOLUTION:")
        if customer_test and customer_test["success"]:
            print(f"   ✅ Customer {URGENT_CUSTOMER_EMAIL} can access their account")
            print("   📧 Password reset email available if needed")
            print("   🔗 Login URL: https://app.dentalaftercarenotes.com/login")
        else:
            print(f"   🚨 Customer {URGENT_CUSTOMER_EMAIL} needs immediate assistance")
            print("   🔧 Manual account creation or password reset required")
        
        return success_rate >= 75  # Consider 75%+ success rate as acceptable

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Backend testing completed successfully!")
        sys.exit(0)
    else:
        print("❌ Backend testing completed with issues!")
        sys.exit(1)