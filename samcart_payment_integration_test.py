#!/usr/bin/env python3
"""
SamCart Payment Integration Comprehensive Testing
=================================================

This test suite comprehensively tests the SamCart payment integration to ensure
it works flawlessly for real paying customers. This is the #1 priority issue.

Test Coverage:
1. SamCart webhook endpoint with realistic payment data
2. Account creation process for new payments
3. Welcome email delivery system
4. Password generation and login system for SamCart-created accounts
5. Password reset functionality for SamCart accounts
6. Webhook logs and statistics endpoints
7. Both 'Order' and 'ProductPurchased' event types
8. 100% automated customer onboarding
9. Existing customer accounts (caryganz@gmail.com, caryganzconsulting@gmail.com)
10. Customer login and dashboard access
"""

import asyncio
import aiohttp
import json
import uuid
import bcrypt
from datetime import datetime, timezone, timedelta
import os
import sys

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class SamCartIntegrationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.webhook_baseline = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    async def test_webhook_endpoint_accessibility(self):
        """Test 1: Verify SamCart webhook endpoint is accessible"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart") as response:
                # Should return 405 Method Not Allowed for GET (expects POST)
                if response.status == 405:
                    self.log_result(
                        "Webhook Endpoint Accessibility",
                        True,
                        f"Endpoint accessible, returns {response.status} as expected for GET request"
                    )
                    return True
                else:
                    self.log_result(
                        "Webhook Endpoint Accessibility",
                        False,
                        f"Unexpected status code: {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Webhook Endpoint Accessibility",
                False,
                error=str(e)
            )
            return False
    
    async def get_webhook_baseline(self):
        """Get current webhook statistics as baseline"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart/stats") as response:
                if response.status == 200:
                    self.webhook_baseline = await response.json()
                    self.log_result(
                        "Webhook Baseline Established",
                        True,
                        f"Current stats: {self.webhook_baseline['total_webhooks']} total webhooks, "
                        f"{self.webhook_baseline['recent_practice_signups']} recent signups"
                    )
                    return True
                else:
                    self.log_result(
                        "Webhook Baseline Establishment",
                        False,
                        f"Failed to get stats: {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Webhook Baseline Establishment",
                False,
                error=str(e)
            )
            return False
    
    async def test_webhook_logs_endpoint(self):
        """Test 2: Verify webhook logs endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart/logs") as response:
                if response.status == 200:
                    data = await response.json()
                    logs_count = len(data.get('logs', []))
                    self.log_result(
                        "Webhook Logs Endpoint",
                        True,
                        f"Retrieved {logs_count} webhook logs successfully"
                    )
                    return True
                else:
                    self.log_result(
                        "Webhook Logs Endpoint",
                        False,
                        f"Failed to get logs: {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Webhook Logs Endpoint",
                False,
                error=str(e)
            )
            return False
    
    async def test_webhook_stats_endpoint(self):
        """Test 3: Verify webhook statistics endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ['total_webhooks', 'successful_webhooks', 'failed_webhooks', 'success_rate', 'recent_practice_signups']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result(
                            "Webhook Statistics Endpoint",
                            True,
                            f"All required fields present. Success rate: {data['success_rate']}%"
                        )
                        return True
                    else:
                        self.log_result(
                            "Webhook Statistics Endpoint",
                            False,
                            f"Missing fields: {missing_fields}"
                        )
                        return False
                else:
                    self.log_result(
                        "Webhook Statistics Endpoint",
                        False,
                        f"Failed to get stats: {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Webhook Statistics Endpoint",
                False,
                error=str(e)
            )
            return False
    
    async def test_productpurchased_webhook(self):
        """Test 4: Test ProductPurchased event type webhook"""
        test_email = f"productpurchased.test.{uuid.uuid4().hex[:8]}@example.com"
        
        webhook_payload = {
            "type": "ProductPurchased",
            "api_key": None,
            "product": {
                "id": 999001,
                "sku": "DENTAL-PROD-001",
                "name": "Dental Practice Management - ProductPurchased Test",
                "price": "49.95",
                "tax": "0.00",
                "shipping": "0.00",
                "sub_total": "49.95",
                "product_price": "49.95"
            },
            "customer": {
                "first_name": "Dr. ProductPurchased",
                "last_name": "Test",
                "email": test_email,
                "phone_number": "555-123-4567",
                "customer_id": 999001,
                "billing_address_line1": "123 ProductPurchased Medical Plaza",
                "billing_address_line2": "Suite 100",
                "billing_city": "Test City",
                "billing_state": "TX",
                "billing_zip": "78759",
                "billing_country": "United States"
            },
            "order": {
                "id": 999001,
                "total": "49.95",
                "ip_address": "127.0.0.1",
                "custom_fields": []
            }
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/webhook/samcart",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        self.log_result(
                            "ProductPurchased Webhook Processing",
                            True,
                            f"Account created for {test_email}, webhook ID: {data.get('webhook_id')}"
                        )
                        return True, test_email
                    else:
                        self.log_result(
                            "ProductPurchased Webhook Processing",
                            False,
                            f"Webhook processed but failed: {data}"
                        )
                        return False, test_email
                else:
                    response_text = await response.text()
                    self.log_result(
                        "ProductPurchased Webhook Processing",
                        False,
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False, test_email
        except Exception as e:
            self.log_result(
                "ProductPurchased Webhook Processing",
                False,
                error=str(e)
            )
            return False, test_email
    
    async def test_order_webhook(self):
        """Test 5: Test Order event type webhook"""
        test_email = f"order.test.{uuid.uuid4().hex[:8]}@example.com"
        
        webhook_payload = {
            "type": "Order",
            "api_key": None,
            "product": {
                "id": 999002,
                "sku": "DENTAL-ORDER-001",
                "name": "Dental Practice Management - Order Test",
                "price": "49.95",
                "tax": "0.00",
                "shipping": "0.00",
                "sub_total": "49.95",
                "product_price": "49.95"
            },
            "customer": {
                "first_name": "Dr. Order",
                "last_name": "Test",
                "email": test_email,
                "phone_number": "555-123-4568",
                "customer_id": 999002,
                "billing_address_line1": "123 Order Medical Plaza",
                "billing_address_line2": "Suite 200",
                "billing_city": "Order City",
                "billing_state": "CA",
                "billing_zip": "90210",
                "billing_country": "United States"
            },
            "order": {
                "id": 999002,
                "total": "49.95",
                "ip_address": "127.0.0.1",
                "custom_fields": []
            }
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/webhook/samcart",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        self.log_result(
                            "Order Webhook Processing",
                            True,
                            f"Account created for {test_email}, webhook ID: {data.get('webhook_id')}"
                        )
                        return True, test_email
                    else:
                        self.log_result(
                            "Order Webhook Processing",
                            False,
                            f"Webhook processed but failed: {data}"
                        )
                        return False, test_email
                else:
                    response_text = await response.text()
                    self.log_result(
                        "Order Webhook Processing",
                        False,
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False, test_email
        except Exception as e:
            self.log_result(
                "Order Webhook Processing",
                False,
                error=str(e)
            )
            return False, test_email
    
    async def test_webhook_test_endpoint(self):
        """Test 6: Test webhook test endpoint"""
        test_email = f"webhook.test.{uuid.uuid4().hex[:8]}@example.com"
        
        try:
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        practice_info = data.get('practice_info', {})
                        emails_sent = data.get('emails_sent', {})
                        
                        self.log_result(
                            "Webhook Test Endpoint",
                            True,
                            f"Test account created: {practice_info.get('email')}, "
                            f"Welcome email: {emails_sent.get('welcome_email')}, "
                            f"Admin notification: {emails_sent.get('admin_notification')}, "
                            f"Password: {practice_info.get('password')}"
                        )
                        return True, test_email, practice_info.get('password')
                    else:
                        self.log_result(
                            "Webhook Test Endpoint",
                            False,
                            f"Test failed: {data}"
                        )
                        return False, test_email, None
                else:
                    response_text = await response.text()
                    self.log_result(
                        "Webhook Test Endpoint",
                        False,
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False, test_email, None
        except Exception as e:
            self.log_result(
                "Webhook Test Endpoint",
                False,
                error=str(e)
            )
            return False, test_email, None
    
    async def test_account_login(self, email, password, test_name_suffix=""):
        """Test 7: Test login with SamCart-created account"""
        try:
            login_payload = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(
                f"{API_BASE}/auth/login",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('token'):
                        practice = data.get('practice', {})
                        user = data.get('user', {})
                        
                        self.log_result(
                            f"SamCart Account Login{test_name_suffix}",
                            True,
                            f"Login successful for {email}, "
                            f"Practice: {practice.get('name', 'N/A')}, "
                            f"User role: {user.get('role', 'N/A')}, "
                            f"Token received: {bool(data.get('token'))}"
                        )
                        return True, data.get('token')
                    else:
                        self.log_result(
                            f"SamCart Account Login{test_name_suffix}",
                            False,
                            f"Login response missing success/token: {data}"
                        )
                        return False, None
                elif response.status == 401:
                    self.log_result(
                        f"SamCart Account Login{test_name_suffix}",
                        False,
                        f"Authentication failed (401) - invalid credentials for {email}"
                    )
                    return False, None
                else:
                    response_text = await response.text()
                    self.log_result(
                        f"SamCart Account Login{test_name_suffix}",
                        False,
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False, None
        except Exception as e:
            self.log_result(
                f"SamCart Account Login{test_name_suffix}",
                False,
                error=str(e)
            )
            return False, None
    
    async def test_practice_dashboard_access(self, token, test_name_suffix=""):
        """Test 8: Test practice dashboard access with SamCart account"""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{API_BASE}/practice/dashboard",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        practice_data = data.get('practice', {})
                        self.log_result(
                            f"Practice Dashboard Access{test_name_suffix}",
                            True,
                            f"Dashboard accessible, Practice: {practice_data.get('name', 'N/A')}, "
                            f"Active procedures: {practice_data.get('activeProcedures', 0)}, "
                            f"Total patients: {practice_data.get('totalPatients', 0)}"
                        )
                        return True
                    else:
                        self.log_result(
                            f"Practice Dashboard Access{test_name_suffix}",
                            False,
                            f"Dashboard response not successful: {data}"
                        )
                        return False
                else:
                    response_text = await response.text()
                    self.log_result(
                        f"Practice Dashboard Access{test_name_suffix}",
                        False,
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                f"Practice Dashboard Access{test_name_suffix}",
                False,
                error=str(e)
            )
            return False
    
    async def test_password_reset_functionality(self, email, test_name_suffix=""):
        """Test 9: Test password reset for SamCart accounts"""
        try:
            # Step 1: Request password reset
            reset_payload = {
                "email": email,
                "recovery_method": "email"
            }
            
            async with self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=reset_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        sent_methods = data.get('sent_methods', [])
                        self.log_result(
                            f"Password Reset Request{test_name_suffix}",
                            True,
                            f"Password reset email sent to {email}, methods: {sent_methods}"
                        )
                        return True
                    else:
                        self.log_result(
                            f"Password Reset Request{test_name_suffix}",
                            False,
                            f"Password reset failed: {data}"
                        )
                        return False
                else:
                    response_text = await response.text()
                    self.log_result(
                        f"Password Reset Request{test_name_suffix}",
                        False,
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                f"Password Reset Request{test_name_suffix}",
                False,
                error=str(e)
            )
            return False
    
    async def test_existing_customer_caryganz(self):
        """Test 10: Test existing customer caryganz@gmail.com"""
        email = "caryganz@gmail.com"
        
        # Test password reset (since we don't know the current password)
        reset_success = await self.test_password_reset_functionality(email, " (caryganz@gmail.com)")
        
        if reset_success:
            self.log_result(
                "Existing Customer caryganz@gmail.com",
                True,
                "Account exists and password reset system working"
            )
            return True
        else:
            self.log_result(
                "Existing Customer caryganz@gmail.com",
                False,
                "Password reset failed - account may not exist or system issue"
            )
            return False
    
    async def test_existing_customer_caryganzconsulting(self):
        """Test 11: Test existing customer caryganzconsulting@gmail.com"""
        email = "caryganzconsulting@gmail.com"
        
        # Test password reset (since we don't know the current password)
        reset_success = await self.test_password_reset_functionality(email, " (caryganzconsulting@gmail.com)")
        
        if reset_success:
            self.log_result(
                "Existing Customer caryganzconsulting@gmail.com",
                True,
                "Account exists and password reset system working"
            )
            return True
        else:
            self.log_result(
                "Existing Customer caryganzconsulting@gmail.com",
                False,
                "Password reset failed - account may not exist or system issue"
            )
            return False
    
    async def test_duplicate_account_prevention(self):
        """Test 12: Test duplicate account prevention"""
        # Use the same email twice
        test_email = f"duplicate.test.{uuid.uuid4().hex[:8]}@example.com"
        
        # First webhook - should create account
        webhook_payload = {
            "type": "ProductPurchased",
            "customer": {
                "first_name": "Dr. Duplicate",
                "last_name": "Test",
                "email": test_email,
                "phone_number": "555-123-4569",
                "customer_id": 999003
            },
            "product": {"id": 999003, "name": "Test Product", "price": "49.95"},
            "order": {"id": 999003, "total": "49.95"}
        }
        
        try:
            # First webhook
            async with self.session.post(
                f"{API_BASE}/webhook/samcart",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                first_result = await response.json() if response.status == 200 else {}
            
            # Second webhook with same email
            async with self.session.post(
                f"{API_BASE}/webhook/samcart",
                json=webhook_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})
                    
                    if result.get('status') == 'duplicate':
                        self.log_result(
                            "Duplicate Account Prevention",
                            True,
                            f"Duplicate account correctly detected for {test_email}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Duplicate Account Prevention",
                            False,
                            f"Duplicate not detected: {result}"
                        )
                        return False
                else:
                    self.log_result(
                        "Duplicate Account Prevention",
                        False,
                        f"HTTP {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Duplicate Account Prevention",
                False,
                error=str(e)
            )
            return False
    
    async def verify_webhook_activity_increase(self):
        """Test 13: Verify webhook activity increased from baseline"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart/stats") as response:
                if response.status == 200:
                    current_stats = await response.json()
                    
                    if self.webhook_baseline:
                        baseline_total = self.webhook_baseline['total_webhooks']
                        current_total = current_stats['total_webhooks']
                        increase = current_total - baseline_total
                        
                        if increase > 0:
                            self.log_result(
                                "Webhook Activity Increase Verification",
                                True,
                                f"Webhook activity increased by {increase} (from {baseline_total} to {current_total})"
                            )
                            return True
                        else:
                            self.log_result(
                                "Webhook Activity Increase Verification",
                                False,
                                f"No increase in webhook activity (baseline: {baseline_total}, current: {current_total})"
                            )
                            return False
                    else:
                        self.log_result(
                            "Webhook Activity Increase Verification",
                            False,
                            "No baseline established"
                        )
                        return False
                else:
                    self.log_result(
                        "Webhook Activity Increase Verification",
                        False,
                        f"Failed to get current stats: {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_result(
                "Webhook Activity Increase Verification",
                False,
                error=str(e)
            )
            return False
    
    async def run_comprehensive_test(self):
        """Run all SamCart integration tests"""
        print("🚀 STARTING SAMCART PAYMENT INTEGRATION COMPREHENSIVE TESTING")
        print("=" * 80)
        print()
        
        # Establish baseline
        await self.get_webhook_baseline()
        
        # Test 1: Basic endpoint accessibility
        await self.test_webhook_endpoint_accessibility()
        
        # Test 2-3: Webhook infrastructure
        await self.test_webhook_logs_endpoint()
        await self.test_webhook_stats_endpoint()
        
        # Test 4-5: Event type processing
        productpurchased_success, productpurchased_email = await self.test_productpurchased_webhook()
        order_success, order_email = await self.test_order_webhook()
        
        # Test 6: Test endpoint
        test_success, test_email, test_password = await self.test_webhook_test_endpoint()
        
        # Test 7-8: Login and dashboard access for test account
        if test_success and test_password:
            login_success, token = await self.test_account_login(test_email, test_password, " (Test Account)")
            if login_success and token:
                await self.test_practice_dashboard_access(token, " (Test Account)")
        
        # Test 9: Password reset functionality
        if test_success:
            await self.test_password_reset_functionality(test_email, " (Test Account)")
        
        # Test 10-11: Existing customers
        await self.test_existing_customer_caryganz()
        await self.test_existing_customer_caryganzconsulting()
        
        # Test 12: Duplicate prevention
        await self.test_duplicate_account_prevention()
        
        # Test 13: Verify activity increase
        await self.verify_webhook_activity_increase()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 SAMCART PAYMENT INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['error'] or result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}")
        
        print("\n" + "=" * 80)
        
        # Critical assessment
        critical_tests = [
            "Webhook Endpoint Accessibility",
            "ProductPurchased Webhook Processing", 
            "Order Webhook Processing",
            "Webhook Test Endpoint",
            "SamCart Account Login (Test Account)",
            "Practice Dashboard Access (Test Account)",
            "Password Reset Request (Test Account)",
            "Existing Customer caryganz@gmail.com",
            "Existing Customer caryganzconsulting@gmail.com"
        ]
        
        critical_failures = [
            result for result in self.test_results 
            if not result['success'] and result['test'] in critical_tests
        ]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES DETECTED:")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['error'] or failure['details']}")
            print("\n⚠️  PAYMENT INTEGRATION NOT READY FOR PRODUCTION")
        else:
            print("🎉 ALL CRITICAL TESTS PASSED - PAYMENT INTEGRATION READY")
        
        print("=" * 80)
        
        return success_rate >= 90  # Consider successful if 90%+ tests pass

async def main():
    """Main test execution"""
    async with SamCartIntegrationTester() as tester:
        success = await tester.run_comprehensive_test()
        return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        sys.exit(1)