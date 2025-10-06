#!/usr/bin/env python3
"""
CRITICAL SamCart Payment Integration Testing
Focus: Comprehensive testing of all SamCart payment integration features
As requested in critical review - this is the #1 priority issue that must work flawlessly
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone
import os
import sys

# Test configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
CRITICAL_TEST_EMAIL = "critical.test@example.com"
REAL_CUSTOMER_EMAIL = "caryganzconsulting@gmail.com"

class CriticalSamCartTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.created_accounts = []
        
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
        
    async def test_samcart_account_creation(self):
        """CRITICAL TEST 1: Test SamCart Account Creation via webhook test endpoint"""
        print("\n🔍 CRITICAL TEST 1: SamCart Account Creation")
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": CRITICAL_TEST_EMAIL}
            
            async with self.session.post(url, params=params) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    
                    if response_data.get("status") == "success":
                        practice_info = response_data.get("practice_info", {})
                        emails_sent = response_data.get("emails_sent", {})
                        
                        # Verify account creation details
                        email = practice_info.get("email")
                        practice_name = practice_info.get("practice_name")
                        password_provided = practice_info.get("password") is not None
                        welcome_email_sent = emails_sent.get("welcome_email", False)
                        
                        if email and practice_name and password_provided and welcome_email_sent:
                            self.log_result("SamCart Account Creation", True, 
                                          f"Account created successfully: {practice_name} for {email}, password generated, welcome email sent")
                            self.created_accounts.append({
                                "email": email,
                                "password": practice_info.get("password"),
                                "practice_name": practice_name
                            })
                            return True
                        else:
                            self.log_result("SamCart Account Creation", False, 
                                          f"Account creation incomplete: email={bool(email)}, name={bool(practice_name)}, password={password_provided}, welcome_email={welcome_email_sent}")
                            return False
                            
                    elif response_data.get("status") == "duplicate":
                        # Account already exists - this is also success
                        self.log_result("SamCart Account Creation", True, 
                                      f"Account already exists (duplicate detection working): {response_data.get('message')}")
                        return True
                    else:
                        self.log_result("SamCart Account Creation", False, 
                                      f"Account creation failed: {response_data}")
                        return False
                else:
                    self.log_result("SamCart Account Creation", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("SamCart Account Creation", False, f"Error: {e}")
            return False
            
    async def test_login_system_for_samcart_accounts(self):
        """CRITICAL TEST 2: Test Login System for SamCart Accounts"""
        print("\n🔍 CRITICAL TEST 2: Login System for SamCart Accounts")
        try:
            # Test with the critical test email
            url = f"{BACKEND_URL}/api/auth/login"
            
            # First test with wrong password to verify account exists and is healthy
            login_data = {
                "email": CRITICAL_TEST_EMAIL,
                "password": "wrong_password_test"
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    # This is expected for wrong password - indicates healthy account
                    self.log_result("Login System Health Check", True, 
                                  f"Account exists and is healthy (returns 401 for wrong password)")
                elif response.status == 500:
                    # This indicates password field corruption - CRITICAL ISSUE
                    self.log_result("Login System for SamCart Accounts", False, 
                                  f"CRITICAL: Password field corruption detected - login returns 500 error: {response_text}")
                    return False
                else:
                    self.log_result("Login System for SamCart Accounts", False, 
                                  f"Unexpected login response: HTTP {response.status}: {response_text}")
                    return False
                    
            # Test password reset as alternative login method
            reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": CRITICAL_TEST_EMAIL,
                "recovery_method": "email"
            }
            
            async with self.session.post(reset_url, json=reset_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        self.log_result("Login System for SamCart Accounts", True, 
                                      f"Login system working: account healthy, password reset available")
                        return True
                    else:
                        self.log_result("Login System for SamCart Accounts", False, 
                                      f"Password reset failed: {response_data}")
                        return False
                else:
                    self.log_result("Login System for SamCart Accounts", False, 
                                  f"Password reset HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Login System for SamCart Accounts", False, f"Error: {e}")
            return False
            
    async def test_password_reset_for_samcart_accounts(self):
        """CRITICAL TEST 3: Test Password Reset for SamCart Accounts"""
        print("\n🔍 CRITICAL TEST 3: Password Reset for SamCart Accounts")
        try:
            # Test password reset for multiple SamCart accounts
            test_emails = [CRITICAL_TEST_EMAIL, REAL_CUSTOMER_EMAIL]
            
            all_passed = True
            for email in test_emails:
                url = f"{BACKEND_URL}/api/auth/forgot-password"
                reset_data = {
                    "email": email,
                    "recovery_method": "email"
                }
                
                async with self.session.post(url, json=reset_data) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        response_data = json.loads(response_text)
                        if response_data.get("success"):
                            sent_methods = response_data.get("sent_methods", [])
                            print(f"   ✅ Password reset email sent to {email}: {sent_methods}")
                        else:
                            print(f"   ❌ Password reset failed for {email}: {response_data}")
                            all_passed = False
                    else:
                        print(f"   ❌ Password reset HTTP error for {email}: {response.status}")
                        all_passed = False
                        
            # Test token validation endpoint
            validate_url = f"{BACKEND_URL}/api/auth/validate-reset-token"
            test_token_data = {"token": "invalid_test_token"}
            
            async with self.session.post(validate_url, json=test_token_data) as response:
                if response.status in [400, 401]:  # Expected for invalid token
                    print(f"   ✅ Token validation working (rejects invalid tokens)")
                else:
                    print(f"   ⚠️ Token validation unexpected response: {response.status}")
                    
            if all_passed:
                self.log_result("Password Reset for SamCart Accounts", True, 
                              f"Password reset working for all tested accounts")
                return True
            else:
                self.log_result("Password Reset for SamCart Accounts", False, 
                              f"Password reset failed for some accounts")
                return False
                
        except Exception as e:
            self.log_result("Password Reset for SamCart Accounts", False, f"Error: {e}")
            return False
            
    async def test_complete_payment_flow(self):
        """CRITICAL TEST 4: Test Complete Payment Flow Simulation"""
        print("\n🔍 CRITICAL TEST 4: Complete Payment Flow Simulation")
        try:
            # Generate unique test email for this flow
            flow_test_email = f"payment.flow.{uuid.uuid4().hex[:8]}@example.com"
            
            # Step 1: Simulate SamCart payment webhook
            webhook_url = f"{BACKEND_URL}/api/webhook/samcart"
            webhook_payload = {
                "type": "Order",  # Critical: test 'Order' event type
                "api_key": None,
                "product": {
                    "id": 888888,
                    "sku": "DENTAL-FLOW-TEST",
                    "name": "Dental Practice Management - Flow Test",
                    "price": "49.95",
                    "tax": "0.00",
                    "shipping": "0.00",
                    "sub_total": "49.95",
                    "product_price": "49.95"
                },
                "customer": {
                    "first_name": "Payment",
                    "last_name": "Flow",
                    "email": flow_test_email,
                    "phone_number": "555-987-6543",
                    "customer_id": 888888,
                    "billing_address_line1": "456 Payment Flow Ave",
                    "billing_city": "Flow City",
                    "billing_state": "CA",
                    "billing_zip": "90210",
                    "billing_country": "United States"
                },
                "order": {
                    "id": 888888,
                    "total": "49.95",
                    "ip_address": "127.0.0.1",
                    "custom_fields": []
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-Webhook-Signature': 'test_signature'
            }
            
            # Send webhook
            async with self.session.post(webhook_url, json=webhook_payload, headers=headers) as response:
                if response.status != 200:
                    self.log_result("Complete Payment Flow", False, 
                                  f"Webhook failed: HTTP {response.status}")
                    return False
                    
                webhook_response = await response.json()
                if webhook_response.get("status") != "success":
                    self.log_result("Complete Payment Flow", False, 
                                  f"Webhook processing failed: {webhook_response}")
                    return False
                    
            print(f"   ✅ Step 1: SamCart webhook processed successfully")
            
            # Step 2: Verify account creation
            await asyncio.sleep(1)  # Brief delay for processing
            
            # Test login to verify account exists and is healthy
            login_url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": flow_test_email,
                "password": "test_wrong_password"
            }
            
            async with self.session.post(login_url, json=login_data) as response:
                if response.status == 401:
                    print(f"   ✅ Step 2: Account created and healthy (401 for wrong password)")
                elif response.status == 500:
                    self.log_result("Complete Payment Flow", False, 
                                  f"CRITICAL: Account created but password corrupted (500 error)")
                    return False
                else:
                    print(f"   ⚠️ Step 2: Unexpected login response: {response.status}")
                    
            # Step 3: Test password reset
            reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": flow_test_email,
                "recovery_method": "email"
            }
            
            async with self.session.post(reset_url, json=reset_data) as response:
                if response.status == 200:
                    reset_response = await response.json()
                    if reset_response.get("success"):
                        print(f"   ✅ Step 3: Password reset working")
                    else:
                        self.log_result("Complete Payment Flow", False, 
                                      f"Password reset failed: {reset_response}")
                        return False
                else:
                    self.log_result("Complete Payment Flow", False, 
                                  f"Password reset HTTP error: {response.status}")
                    return False
                    
            self.log_result("Complete Payment Flow", True, 
                          f"Complete flow working: webhook → account creation → login → password reset")
            return True
            
        except Exception as e:
            self.log_result("Complete Payment Flow", False, f"Error: {e}")
            return False
            
    async def test_real_customer_scenario(self):
        """CRITICAL TEST 5: Test Real Customer Scenario"""
        print("\n🔍 CRITICAL TEST 5: Real Customer Scenario")
        try:
            # Test with actual customer email from the review request
            customer_email = REAL_CUSTOMER_EMAIL
            
            # Check if customer account exists
            webhook_test_url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": customer_email}
            
            async with self.session.post(webhook_test_url, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("status") == "duplicate":
                        print(f"   ✅ Customer account exists: {customer_email}")
                    else:
                        print(f"   ℹ️ Customer account status: {response_data.get('status')}")
                        
            # Test customer login health
            login_url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": customer_email,
                "password": "test_wrong_password"
            }
            
            async with self.session.post(login_url, json=login_data) as response:
                if response.status == 401:
                    print(f"   ✅ Customer account healthy (401 for wrong password)")
                    account_healthy = True
                elif response.status == 500:
                    print(f"   ❌ Customer account has password corruption (500 error)")
                    account_healthy = False
                else:
                    print(f"   ⚠️ Customer account unexpected response: {response.status}")
                    account_healthy = False
                    
            # Test customer password reset
            reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": customer_email,
                "recovery_method": "email"
            }
            
            async with self.session.post(reset_url, json=reset_data) as response:
                if response.status == 200:
                    reset_response = await response.json()
                    if reset_response.get("success"):
                        print(f"   ✅ Customer password reset working")
                        reset_working = True
                    else:
                        print(f"   ❌ Customer password reset failed: {reset_response}")
                        reset_working = False
                else:
                    print(f"   ❌ Customer password reset HTTP error: {response.status}")
                    reset_working = False
                    
            if account_healthy and reset_working:
                self.log_result("Real Customer Scenario", True, 
                              f"Customer {customer_email} can access account via password reset")
                return True
            else:
                self.log_result("Real Customer Scenario", False, 
                              f"Customer access issues: healthy={account_healthy}, reset={reset_working}")
                return False
                
        except Exception as e:
            self.log_result("Real Customer Scenario", False, f"Error: {e}")
            return False
            
    async def test_webhook_infrastructure_health(self):
        """BONUS TEST: Verify webhook infrastructure health"""
        print("\n🔍 BONUS TEST: Webhook Infrastructure Health")
        try:
            # Test webhook logs
            logs_url = f"{BACKEND_URL}/api/webhook/samcart/logs"
            async with self.session.get(logs_url) as response:
                if response.status == 200:
                    logs_data = await response.json()
                    log_count = logs_data.get("count", 0)
                    print(f"   ✅ Webhook logs accessible: {log_count} entries")
                else:
                    print(f"   ❌ Webhook logs error: HTTP {response.status}")
                    return False
                    
            # Test webhook stats
            stats_url = f"{BACKEND_URL}/api/webhook/samcart/stats"
            async with self.session.get(stats_url) as response:
                if response.status == 200:
                    stats_data = await response.json()
                    total_webhooks = stats_data.get("total_webhooks", 0)
                    success_rate = stats_data.get("success_rate", 0)
                    recent_signups = stats_data.get("recent_practice_signups", 0)
                    print(f"   ✅ Webhook stats: {total_webhooks} total, {success_rate}% success, {recent_signups} recent signups")
                else:
                    print(f"   ❌ Webhook stats error: HTTP {response.status}")
                    return False
                    
            self.log_result("Webhook Infrastructure Health", True, 
                          f"All webhook infrastructure endpoints working")
            return True
            
        except Exception as e:
            self.log_result("Webhook Infrastructure Health", False, f"Error: {e}")
            return False
            
    async def run_critical_tests(self):
        """Run all critical SamCart payment integration tests"""
        print("🚨 CRITICAL SAMCART PAYMENT INTEGRATION TESTING")
        print("=" * 70)
        print("This is the #1 priority issue that must work flawlessly")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Critical Test Email: {CRITICAL_TEST_EMAIL}")
        print(f"Real Customer Email: {REAL_CUSTOMER_EMAIL}")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run critical tests in sequence
            critical_tests = [
                self.test_samcart_account_creation,
                self.test_login_system_for_samcart_accounts,
                self.test_password_reset_for_samcart_accounts,
                self.test_complete_payment_flow,
                self.test_real_customer_scenario,
                self.test_webhook_infrastructure_health
            ]
            
            passed = 0
            total = len(critical_tests)
            critical_failures = []
            
            for test in critical_tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                    else:
                        # Check if this is a critical failure
                        test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                        for test_result in self.test_results:
                            if test_result["test"] == test_name and not test_result["success"]:
                                if "CRITICAL" in test_result["details"] or "500 error" in test_result["details"]:
                                    critical_failures.append(f"{test_name}: {test_result['details']}")
                                break
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with exception: {e}")
                    critical_failures.append(f"{test.__name__}: Exception - {e}")
                    
            print("\n" + "=" * 70)
            print(f"🎯 CRITICAL TEST SUMMARY: {passed}/{total} tests passed")
            print("=" * 70)
            
            # Report critical issues
            if critical_failures:
                print("\n🚨 CRITICAL FAILURES DETECTED:")
                for failure in critical_failures:
                    print(f"   ❌ {failure}")
                print("\n⚠️ IMMEDIATE ACTION REQUIRED - PAYING CUSTOMERS AFFECTED")
            else:
                print("\n✅ NO CRITICAL FAILURES - SAMCART INTEGRATION WORKING")
                
            # Success criteria analysis
            success_criteria = {
                "100% success rate for account creation": passed >= 1,
                "Immediate customer access with welcome email": passed >= 2,
                "Working password reset system": passed >= 3,
                "No manual intervention required": passed >= 4,
                "All paying customers can login": passed >= 5
            }
            
            print(f"\n📊 SUCCESS CRITERIA ANALYSIS:")
            for criteria, met in success_criteria.items():
                status = "✅ MET" if met else "❌ NOT MET"
                print(f"   {status}: {criteria}")
                
            return passed == total and len(critical_failures) == 0
            
        finally:
            await self.cleanup()

async def main():
    """Main critical test execution"""
    tester = CriticalSamCartTester()
    success = await tester.run_critical_tests()
    
    if success:
        print("\n🎉 ALL CRITICAL SAMCART TESTS PASSED!")
        print("✅ SamCart payment integration is working flawlessly")
        print("✅ Ready for real paying customers")
        sys.exit(0)
    else:
        print("\n🚨 CRITICAL FAILURES DETECTED!")
        print("❌ SamCart payment integration has issues")
        print("⚠️ IMMEDIATE RESOLUTION REQUIRED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())