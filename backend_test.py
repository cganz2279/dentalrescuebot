#!/usr/bin/env python3
"""
Backend Testing Script for Tutorial Delete Functionality
Tests the enhanced tutorial delete endpoint with ID format handling
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class TutorialDeleteTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def test_webhook_endpoint_accessibility(self):
        """Test 1: Verify webhook endpoint is accessible"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart"
            async with self.session.get(url) as response:
                # Webhook should return 405 for GET (Method Not Allowed)
                if response.status == 405:
                    self.log_result("Webhook Endpoint Accessibility", True, 
                                  f"Endpoint accessible, returns 405 for GET as expected")
                    return True
                else:
                    self.log_result("Webhook Endpoint Accessibility", False, 
                                  f"Unexpected status: {response.status}")
                    return False
        except Exception as e:
            self.log_result("Webhook Endpoint Accessibility", False, f"Error: {e}")
            return False
            
    async def test_webhook_order_event_processing(self):
        """Test 2: Test webhook processes 'Order' event type (critical fix)"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart"
            
            # Create test payload with 'Order' event type (the critical issue)
            test_payload = {
                "type": "Order",  # This was the root cause - webhook ignored 'Order' events
                "api_key": None,
                "product": {
                    "id": 999999,
                    "sku": "DENTAL-CRITICAL-TEST",
                    "name": "Dental Practice Management - Critical Test",
                    "price": "49.95",
                    "tax": "0.00",
                    "shipping": "0.00",
                    "sub_total": "49.95",
                    "product_price": "49.95"
                },
                "customer": {
                    "first_name": "Test",
                    "last_name": "Payment",
                    "email": TEST_EMAIL,
                    "phone_number": "555-123-4567",
                    "customer_id": 999999,
                    "billing_address_line1": "123 Test Payment Plaza",
                    "billing_address_line2": "Suite 100",
                    "billing_city": "Test City",
                    "billing_state": "TX",
                    "billing_zip": "78759",
                    "billing_country": "United States"
                },
                "order": {
                    "id": 999999,
                    "total": "49.95",
                    "ip_address": "127.0.0.1",
                    "custom_fields": []
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-Webhook-Signature': 'test_signature'  # For testing
            }
            
            async with self.session.post(url, json=test_payload, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("status") == "success":
                        self.log_result("Webhook Order Event Processing", True, 
                                      f"Order event processed successfully: {response_data.get('result', {}).get('message', 'No message')}")
                        return True
                    else:
                        self.log_result("Webhook Order Event Processing", False, 
                                      f"Webhook processed but failed: {response_data}")
                        return False
                else:
                    self.log_result("Webhook Order Event Processing", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Webhook Order Event Processing", False, f"Error: {e}")
            return False
            
    async def test_account_creation_via_webhook_test_endpoint(self):
        """Test 3: Test account creation using webhook test endpoint"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": TEST_EMAIL}
            
            async with self.session.post(url, params=params) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("status") == "success":
                        practice_info = response_data.get("practice_info", {})
                        self.log_result("Account Creation via Test Endpoint", True, 
                                      f"Account created: {practice_info.get('practice_name')} for {practice_info.get('email')}")
                        return response_data
                    elif response_data.get("status") == "duplicate":
                        self.log_result("Account Creation via Test Endpoint", True, 
                                      f"Account already exists (duplicate detection working): {response_data.get('message')}")
                        return response_data
                    else:
                        self.log_result("Account Creation via Test Endpoint", False, 
                                      f"Account creation failed: {response_data}")
                        return None
                else:
                    self.log_result("Account Creation via Test Endpoint", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return None
                    
        except Exception as e:
            self.log_result("Account Creation via Test Endpoint", False, f"Error: {e}")
            return None
            
    async def test_login_with_created_account(self):
        """Test 4: Test login with account created via webhook (critical test)"""
        try:
            # Test login endpoint to see if it returns proper error messages
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": TEST_EMAIL,
                "password": "test_password_123"  # This should fail but give us info about account state
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    # This is expected for wrong password
                    self.log_result("Login Endpoint Accessibility", True, 
                                  f"Login endpoint accessible, returns 401 for wrong password as expected")
                    return True
                elif response.status == 500:
                    # This indicates password field corruption (the critical issue)
                    self.log_result("Login with Created Account", False, 
                                  f"CRITICAL: Login returns 500 error - indicates password field corruption: {response_text}")
                    return False
                else:
                    self.log_result("Login with Created Account", False, 
                                  f"Unexpected login response: HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Login with Created Account", False, f"Error: {e}")
            return False
            
    async def test_password_reset_functionality(self):
        """Test 5: Test password reset system for webhook-created accounts"""
        try:
            url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": TEST_EMAIL,
                "recovery_method": "email"
            }
            
            async with self.session.post(url, json=reset_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        sent_methods = response_data.get("sent_methods", [])
                        self.log_result("Password Reset Functionality", True, 
                                      f"Password reset email sent successfully. Methods: {sent_methods}")
                        return True
                    else:
                        self.log_result("Password Reset Functionality", False, 
                                      f"Password reset failed: {response_data}")
                        return False
                else:
                    self.log_result("Password Reset Functionality", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Password Reset Functionality", False, f"Error: {e}")
            return False
            
    async def test_webhook_logs_and_stats(self):
        """Test 6: Test webhook logging and statistics"""
        try:
            # Test logs endpoint
            logs_url = f"{BACKEND_URL}/api/webhook/samcart/logs"
            async with self.session.get(logs_url) as response:
                if response.status == 200:
                    logs_data = await response.json()
                    log_count = logs_data.get("count", 0)
                    self.log_result("Webhook Logs Endpoint", True, 
                                  f"Retrieved {log_count} webhook logs")
                else:
                    self.log_result("Webhook Logs Endpoint", False, 
                                  f"HTTP {response.status}")
                    return False
                    
            # Test stats endpoint
            stats_url = f"{BACKEND_URL}/api/webhook/samcart/stats"
            async with self.session.get(stats_url) as response:
                if response.status == 200:
                    stats_data = await response.json()
                    total_webhooks = stats_data.get("total_webhooks", 0)
                    success_rate = stats_data.get("success_rate", 0)
                    self.log_result("Webhook Stats Endpoint", True, 
                                  f"Total webhooks: {total_webhooks}, Success rate: {success_rate}%")
                    return True
                else:
                    self.log_result("Webhook Stats Endpoint", False, 
                                  f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Webhook Logs and Stats", False, f"Error: {e}")
            return False
            
    async def test_email_service_integration(self):
        """Test 7: Test email service integration for welcome emails"""
        try:
            # This is tested indirectly through the webhook test endpoint
            # which should send welcome emails
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": f"email.test.{uuid.uuid4().hex[:8]}@example.com"}
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("status") == "success":
                        emails_sent = response_data.get("emails_sent", {})
                        welcome_email = emails_sent.get("welcome_email", False)
                        admin_notification = emails_sent.get("admin_notification", False)
                        
                        if welcome_email and admin_notification:
                            self.log_result("Email Service Integration", True, 
                                          "Welcome email and admin notification sent successfully")
                            return True
                        else:
                            self.log_result("Email Service Integration", False, 
                                          f"Email sending failed: welcome={welcome_email}, admin={admin_notification}")
                            return False
                    else:
                        self.log_result("Email Service Integration", False, 
                                      f"Test endpoint failed: {response_data}")
                        return False
                else:
                    self.log_result("Email Service Integration", False, 
                                  f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Email Service Integration", False, f"Error: {e}")
            return False
            
    async def run_all_tests(self):
        """Run all SamCart webhook integration tests"""
        print("🚀 Starting SamCart Webhook Integration Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run tests in sequence
            tests = [
                self.test_webhook_endpoint_accessibility,
                self.test_webhook_order_event_processing,
                self.test_account_creation_via_webhook_test_endpoint,
                self.test_login_with_created_account,
                self.test_password_reset_functionality,
                self.test_webhook_logs_and_stats,
                self.test_email_service_integration
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {e}")
                    
            print("\n" + "=" * 60)
            print(f"🎯 TEST SUMMARY: {passed}/{total} tests passed")
            print("=" * 60)
            
            # Analyze critical issues
            critical_issues = []
            for result in self.test_results:
                if not result["success"] and "500 error" in result["details"]:
                    critical_issues.append(f"CRITICAL: {result['test']} - {result['details']}")
                elif not result["success"] and "password" in result["details"].lower():
                    critical_issues.append(f"PASSWORD ISSUE: {result['test']} - {result['details']}")
                    
            if critical_issues:
                print("\n🚨 CRITICAL ISSUES FOUND:")
                for issue in critical_issues:
                    print(f"   {issue}")
            else:
                print("\n✅ No critical password corruption issues detected")
                
            return passed == total
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = SamCartWebhookTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All SamCart webhook integration tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed - check results above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())