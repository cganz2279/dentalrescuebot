#!/usr/bin/env python3
"""
CRITICAL SAMCART WEBHOOK INTEGRATION TESTING
Testing the FIXED SamCart webhook integration with real payload structure
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
import sys

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class SamCartWebhookTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {details}")
    
    def test_real_samcart_webhook_structure(self):
        """Test webhook with real SamCart payload structure"""
        print("\n🔍 Testing Real SamCart Webhook Structure...")
        
        # Real SamCart webhook payload structure based on web research
        real_samcart_payload = {
            "type": "Order",  # Real SamCart event type
            "customer": {
                "email": "test.customer@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890"
            },
            "order": {
                "id": "22677999",
                "total": 49.95,
                "currency": "USD",
                "status": "completed"
            },
            "products": [
                {
                    "id": "dental_aftercare_monthly",
                    "name": "Dental Aftercare Notes - Monthly",
                    "price": 49.95,
                    "transaction_id": "txn_12345"
                }
            ],
            "created_at": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/webhook/samcart",
                json=real_samcart_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test(
                        "Real SamCart Webhook Structure",
                        True,
                        f"Account created successfully for {real_samcart_payload['customer']['email']}"
                    )
                    return data
                elif data.get("status") == "duplicate":
                    self.log_test(
                        "Real SamCart Webhook Structure",
                        True,
                        f"Duplicate account detected (expected behavior)"
                    )
                    return data
                else:
                    self.log_test(
                        "Real SamCart Webhook Structure",
                        False,
                        f"Unexpected status: {data.get('status')}"
                    )
            else:
                self.log_test(
                    "Real SamCart Webhook Structure",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Real SamCart Webhook Structure",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_email_system_functionality(self):
        """Test email system with real customer email"""
        print("\n📧 Testing Email System Functionality...")
        
        # Test with a real-looking email
        test_email = f"cary.test.{int(time.time())}@gmail.com"
        
        try:
            response = requests.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("email_sent"):
                    self.log_test(
                        "Email System Functionality",
                        True,
                        f"Welcome email sent successfully to {test_email}"
                    )
                    return data
                else:
                    self.log_test(
                        "Email System Functionality",
                        False,
                        f"Email not sent: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "Email System Functionality",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Email System Functionality",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_password_reset_for_samcart_customers(self):
        """Test password reset system for SamCart customers"""
        print("\n🔐 Testing Password Reset for SamCart Customers...")
        
        # Use the customer email from previous test
        test_email = "test.customer@example.com"
        
        try:
            # Test forgot password endpoint
            response = requests.post(
                f"{API_BASE}/auth/forgot-password",
                json={
                    "email": test_email,
                    "recovery_method": "email"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "email" in data.get("sent_methods", []):
                    self.log_test(
                        "Password Reset for SamCart Customers",
                        True,
                        f"Password reset email sent successfully to {test_email}"
                    )
                    return True
                else:
                    self.log_test(
                        "Password Reset for SamCart Customers",
                        False,
                        f"Password reset failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "Password Reset for SamCart Customers",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Password Reset for SamCart Customers",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_account_creation_with_real_payload(self):
        """Test account creation with real SamCart payload structure"""
        print("\n👤 Testing Account Creation with Real Payload...")
        
        # Create unique test customer
        timestamp = int(time.time())
        test_customer = {
            "email": f"real.customer.{timestamp}@example.com",
            "first_name": "Dr. Sarah",
            "last_name": "Johnson",
            "practice_name": "Johnson Dental Practice"
        }
        
        # Real SamCart payload structure
        payload = {
            "type": "ProductPurchased",  # Alternative event type
            "customer": {
                "email": test_customer["email"],
                "first_name": test_customer["first_name"],
                "last_name": test_customer["last_name"]
            },
            "order": {
                "id": f"ORD_{timestamp}",
                "total": 49.95,
                "status": "completed"
            },
            "products": [
                {
                    "name": "Dental Aftercare Notes",
                    "price": 49.95
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/webhook/samcart",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    # Verify account was created by testing login
                    practice_id = data.get("practice_id")
                    if practice_id:
                        self.log_test(
                            "Account Creation with Real Payload",
                            True,
                            f"Account created successfully with ID: {practice_id}"
                        )
                        return data
                    else:
                        self.log_test(
                            "Account Creation with Real Payload",
                            False,
                            "Account creation succeeded but no practice ID returned"
                        )
                else:
                    self.log_test(
                        "Account Creation with Real Payload",
                        False,
                        f"Account creation failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "Account Creation with Real Payload",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Account Creation with Real Payload",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None
    
    def test_admin_system_integration(self):
        """Test if SamCart accounts appear in admin system"""
        print("\n🔧 Testing Admin System Integration...")
        
        # First, authenticate as admin
        admin_credentials = {
            "email": "cganz@admin.com",
            "password": "Dentist1#"
        }
        
        try:
            # Admin login
            login_response = requests.post(
                f"{API_BASE}/admin/login",
                json=admin_credentials,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if login_response.status_code != 200:
                self.log_test(
                    "Admin System Integration",
                    False,
                    f"Admin login failed: HTTP {login_response.status_code}"
                )
                return False
            
            admin_data = login_response.json()
            admin_token = admin_data.get("token")
            
            if not admin_token:
                self.log_test(
                    "Admin System Integration",
                    False,
                    "Admin login succeeded but no token returned"
                )
                return False
            
            # Get practices list
            practices_response = requests.get(
                f"{API_BASE}/admin/practices",
                headers={
                    "Authorization": f"Bearer {admin_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if practices_response.status_code == 200:
                practices_data = practices_response.json()
                practices = practices_data.get("practices", [])
                
                # Look for SamCart practices
                samcart_practices = [p for p in practices if p.get("source") == "samcart"]
                
                if samcart_practices:
                    self.log_test(
                        "Admin System Integration",
                        True,
                        f"Found {len(samcart_practices)} SamCart practices in admin system"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin System Integration",
                        False,
                        f"No SamCart practices found in admin system (total practices: {len(practices)})"
                    )
            else:
                self.log_test(
                    "Admin System Integration",
                    False,
                    f"Failed to get practices list: HTTP {practices_response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Admin System Integration",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_webhook_logs_and_stats(self):
        """Test webhook logging and statistics"""
        print("\n📊 Testing Webhook Logs and Statistics...")
        
        try:
            # Test webhook logs
            logs_response = requests.get(
                f"{API_BASE}/webhook/samcart/logs",
                timeout=30
            )
            
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                logs = logs_data.get("logs", [])
                
                # Test webhook stats
                stats_response = requests.get(
                    f"{API_BASE}/webhook/samcart/stats",
                    timeout=30
                )
                
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    total_webhooks = stats_data.get("total_webhooks", 0)
                    success_rate = stats_data.get("success_rate", 0)
                    
                    self.log_test(
                        "Webhook Logs and Statistics",
                        True,
                        f"Logs: {len(logs)} entries, Stats: {total_webhooks} total webhooks, {success_rate}% success rate"
                    )
                    return True
                else:
                    self.log_test(
                        "Webhook Logs and Statistics",
                        False,
                        f"Stats endpoint failed: HTTP {stats_response.status_code}"
                    )
            else:
                self.log_test(
                    "Webhook Logs and Statistics",
                    False,
                    f"Logs endpoint failed: HTTP {logs_response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Webhook Logs and Statistics",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_caryganz_customer_scenario(self):
        """Test the specific customer scenario mentioned in the review"""
        print("\n🎯 Testing caryganz@gmail.com Customer Scenario...")
        
        customer_email = "caryganz@gmail.com"
        
        try:
            # Test password reset for this specific customer
            response = requests.post(
                f"{API_BASE}/auth/forgot-password",
                json={
                    "email": customer_email,
                    "recovery_method": "email"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "caryganz@gmail.com Customer Scenario",
                        True,
                        f"Password reset available for {customer_email}"
                    )
                    
                    # Also test if account exists by checking webhook test endpoint
                    test_response = requests.post(
                        f"{API_BASE}/webhook/samcart/test",
                        params={"test_email": customer_email},
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        test_data = test_response.json()
                        if test_data.get("status") == "duplicate":
                            self.log_test(
                                "caryganz@gmail.com Account Exists",
                                True,
                                f"Account confirmed to exist for {customer_email}"
                            )
                        else:
                            self.log_test(
                                "caryganz@gmail.com Account Exists",
                                False,
                                f"Account status unclear: {test_data.get('status')}"
                            )
                    
                    return True
                else:
                    self.log_test(
                        "caryganz@gmail.com Customer Scenario",
                        False,
                        f"Password reset failed: {data.get('message')}"
                    )
            else:
                self.log_test(
                    "caryganz@gmail.com Customer Scenario",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "caryganz@gmail.com Customer Scenario",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_event_type_processing(self):
        """Test that all SamCart event types are now processed"""
        print("\n🔄 Testing Event Type Processing...")
        
        event_types_to_test = [
            "Order",
            "ProductPurchased", 
            "OrderCompleted",
            "Order.Completed",
            "unknown_event_type"  # Should now be processed instead of ignored
        ]
        
        success_count = 0
        
        for event_type in event_types_to_test:
            test_email = f"event.test.{event_type.lower().replace('.', '_')}@example.com"
            
            payload = {
                "type": event_type,
                "customer": {
                    "email": test_email,
                    "first_name": "Event",
                    "last_name": "Tester"
                },
                "order": {
                    "id": f"TEST_{int(time.time())}_{event_type}",
                    "total": 49.95
                }
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/webhook/samcart",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") in ["success", "duplicate"]:
                        success_count += 1
                        print(f"  ✅ Event type '{event_type}' processed successfully")
                    else:
                        print(f"  ❌ Event type '{event_type}' failed: {data.get('message')}")
                else:
                    print(f"  ❌ Event type '{event_type}' failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Event type '{event_type}' failed: {str(e)}")
        
        if success_count >= 4:  # At least 4 out of 5 should work
            self.log_test(
                "Event Type Processing",
                True,
                f"Successfully processed {success_count}/{len(event_types_to_test)} event types"
            )
            return True
        else:
            self.log_test(
                "Event Type Processing",
                False,
                f"Only processed {success_count}/{len(event_types_to_test)} event types successfully"
            )
            return False
    
    def run_all_tests(self):
        """Run all SamCart webhook integration tests"""
        print("🚀 Starting CRITICAL SamCart Webhook Integration Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Run all tests
        self.test_real_samcart_webhook_structure()
        self.test_email_system_functionality()
        self.test_password_reset_for_samcart_customers()
        self.test_account_creation_with_real_payload()
        self.test_admin_system_integration()
        self.test_webhook_logs_and_stats()
        self.test_caryganz_customer_scenario()
        self.test_event_type_processing()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 SAMCART WEBHOOK INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"  - {test}")
        
        # Critical assessment
        critical_tests = [
            "Real SamCart Webhook Structure",
            "Email System Functionality", 
            "Password Reset for SamCart Customers",
            "Account Creation with Real Payload"
        ]
        
        critical_failures = [test for test in self.failed_tests if test in critical_tests]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED:")
            for test in critical_failures:
                print(f"  - {test}")
            print("\n❌ SAMCART INTEGRATION NOT READY FOR PRODUCTION")
        else:
            print(f"\n🎉 ALL CRITICAL TESTS PASSED")
            print("✅ SAMCART INTEGRATION READY FOR PRODUCTION")
        
        return success_rate >= 75 and len(critical_failures) == 0

if __name__ == "__main__":
    tester = SamCartWebhookTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)