#!/usr/bin/env python3
"""
Comprehensive Backend Testing for SamCart Webhook Email System
Testing the fixed email system with SamCart webhook to ensure future payments work correctly.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import time

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class SamCartWebhookEmailTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test results"""
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
        """Test 1: SamCart Webhook Endpoint Accessibility"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart") as response:
                # Should return 405 Method Not Allowed for GET requests
                if response.status == 405:
                    self.log_test(
                        "SamCart Webhook Endpoint Accessibility",
                        True,
                        f"Endpoint accessible, returns {response.status} as expected for GET request"
                    )
                    return True
                else:
                    self.log_test(
                        "SamCart Webhook Endpoint Accessibility",
                        False,
                        f"Unexpected status code: {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_test(
                "SamCart Webhook Endpoint Accessibility",
                False,
                error=str(e)
            )
            return False

    async def test_webhook_test_endpoint_basic(self):
        """Test 2: SamCart Webhook Test Endpoint Basic Functionality"""
        try:
            test_email = f"webhook.test.{int(time.time())}@example.com"
            
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        practice_info = data.get("practice_info", {})
                        emails_sent = data.get("emails_sent", {})
                        
                        self.log_test(
                            "SamCart Webhook Test Endpoint Basic",
                            True,
                            f"Account created for {practice_info.get('email')}, "
                            f"Welcome email: {emails_sent.get('welcome_email')}, "
                            f"Admin notification: {emails_sent.get('admin_notification')}"
                        )
                        return True, practice_info
                    else:
                        self.log_test(
                            "SamCart Webhook Test Endpoint Basic",
                            False,
                            f"Unexpected response status: {data.get('status')}"
                        )
                        return False, {}
                else:
                    error_text = await response.text()
                    self.log_test(
                        "SamCart Webhook Test Endpoint Basic",
                        False,
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False, {}
                    
        except Exception as e:
            self.log_test(
                "SamCart Webhook Test Endpoint Basic",
                False,
                error=str(e)
            )
            return False, {}

    async def test_email_service_validation(self):
        """Test 3: Email Service Validation - Test SendGrid Integration"""
        try:
            # Test with a unique email to avoid duplicates
            test_email = f"email.service.test.{int(time.time())}@example.com"
            
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    emails_sent = data.get("emails_sent", {})
                    
                    welcome_email_success = emails_sent.get("welcome_email", False)
                    admin_notification_success = emails_sent.get("admin_notification", False)
                    
                    if welcome_email_success and admin_notification_success:
                        self.log_test(
                            "Email Service Validation",
                            True,
                            f"Both welcome email and admin notification sent successfully for {test_email}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Email Service Validation",
                            False,
                            f"Email sending failed - Welcome: {welcome_email_success}, Admin: {admin_notification_success}"
                        )
                        return False
                else:
                    self.log_test(
                        "Email Service Validation",
                        False,
                        f"Test endpoint failed with status {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Email Service Validation",
                False,
                error=str(e)
            )
            return False

    async def test_background_task_email_sending(self):
        """Test 4: Background Task Email Sending - Verify async email processing"""
        try:
            test_email = f"background.task.test.{int(time.time())}@example.com"
            
            # Send webhook test request
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if account was created
                    if data.get("status") == "success":
                        practice_info = data.get("practice_info", {})
                        emails_sent = data.get("emails_sent", {})
                        
                        # Verify both email types were processed
                        welcome_sent = emails_sent.get("welcome_email", False)
                        admin_sent = emails_sent.get("admin_notification", False)
                        
                        if welcome_sent and admin_sent:
                            self.log_test(
                                "Background Task Email Sending",
                                True,
                                f"Background email tasks completed successfully for {test_email}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Background Task Email Sending",
                                False,
                                f"Background email tasks failed - Welcome: {welcome_sent}, Admin: {admin_sent}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Background Task Email Sending",
                            False,
                            f"Account creation failed: {data.get('message', 'Unknown error')}"
                        )
                        return False
                else:
                    self.log_test(
                        "Background Task Email Sending",
                        False,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Background Task Email Sending",
                False,
                error=str(e)
            )
            return False

    async def test_sendgrid_authentication_fix(self):
        """Test 5: SendGrid Authentication Fix - Verify fresh client creation works"""
        try:
            # Test multiple rapid requests to verify authentication consistency
            test_emails = [
                f"auth.test.1.{int(time.time())}@example.com",
                f"auth.test.2.{int(time.time())}@example.com"
            ]
            
            success_count = 0
            
            for test_email in test_emails:
                async with self.session.post(
                    f"{API_BASE}/webhook/samcart/test",
                    params={"test_email": test_email}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            emails_sent = data.get("emails_sent", {})
                            if emails_sent.get("welcome_email") and emails_sent.get("admin_notification"):
                                success_count += 1
                
                # Small delay between requests
                await asyncio.sleep(1)
            
            if success_count == len(test_emails):
                self.log_test(
                    "SendGrid Authentication Fix",
                    True,
                    f"All {success_count}/{len(test_emails)} email authentication tests passed"
                )
                return True
            else:
                self.log_test(
                    "SendGrid Authentication Fix",
                    False,
                    f"Only {success_count}/{len(test_emails)} email authentication tests passed"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "SendGrid Authentication Fix",
                False,
                error=str(e)
            )
            return False

    async def test_end_to_end_payment_flow(self):
        """Test 6: End-to-End Payment Flow Simulation"""
        try:
            # Simulate complete payment process
            customer_email = f"e2e.payment.test.{int(time.time())}@example.com"
            
            # Step 1: Simulate webhook processing
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": customer_email}
            ) as response:
                
                if response.status != 200:
                    self.log_test(
                        "End-to-End Payment Flow",
                        False,
                        f"Webhook processing failed with status {response.status}"
                    )
                    return False
                
                data = await response.json()
                if data.get("status") != "success":
                    self.log_test(
                        "End-to-End Payment Flow",
                        False,
                        f"Account creation failed: {data.get('message')}"
                    )
                    return False
                
                practice_info = data.get("practice_info", {})
                emails_sent = data.get("emails_sent", {})
                
                # Step 2: Verify account creation
                if not practice_info.get("practice_id"):
                    self.log_test(
                        "End-to-End Payment Flow",
                        False,
                        "Practice ID not generated"
                    )
                    return False
                
                # Step 3: Verify email delivery
                if not (emails_sent.get("welcome_email") and emails_sent.get("admin_notification")):
                    self.log_test(
                        "End-to-End Payment Flow",
                        False,
                        f"Email delivery failed - Welcome: {emails_sent.get('welcome_email')}, Admin: {emails_sent.get('admin_notification')}"
                    )
                    return False
                
                # Step 4: Verify login credentials are provided
                if not practice_info.get("password"):
                    self.log_test(
                        "End-to-End Payment Flow",
                        False,
                        "Login password not provided in response"
                    )
                    return False
                
                self.log_test(
                    "End-to-End Payment Flow",
                    True,
                    f"Complete payment flow successful for {customer_email} - "
                    f"Account: {practice_info.get('practice_id')}, "
                    f"Practice: {practice_info.get('practice_name')}, "
                    f"Emails sent successfully"
                )
                return True
                
        except Exception as e:
            self.log_test(
                "End-to-End Payment Flow",
                False,
                error=str(e)
            )
            return False

    async def test_webhook_logs_functionality(self):
        """Test 7: Webhook Logs Functionality"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart/logs") as response:
                if response.status == 200:
                    data = await response.json()
                    logs = data.get("logs", [])
                    
                    self.log_test(
                        "Webhook Logs Functionality",
                        True,
                        f"Retrieved {len(logs)} webhook logs successfully"
                    )
                    return True
                else:
                    self.log_test(
                        "Webhook Logs Functionality",
                        False,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Webhook Logs Functionality",
                False,
                error=str(e)
            )
            return False

    async def test_webhook_stats_functionality(self):
        """Test 8: Webhook Stats Functionality"""
        try:
            async with self.session.get(f"{API_BASE}/webhook/samcart/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    required_fields = ["total_webhooks", "successful_webhooks", "failed_webhooks", "success_rate"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_test(
                            "Webhook Stats Functionality",
                            True,
                            f"Stats retrieved - Total: {data.get('total_webhooks')}, "
                            f"Success Rate: {data.get('success_rate'):.1f}%"
                        )
                        return True
                    else:
                        self.log_test(
                            "Webhook Stats Functionality",
                            False,
                            f"Missing required fields: {missing_fields}"
                        )
                        return False
                else:
                    self.log_test(
                        "Webhook Stats Functionality",
                        False,
                        f"HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Webhook Stats Functionality",
                False,
                error=str(e)
            )
            return False

    async def test_duplicate_account_prevention(self):
        """Test 9: Duplicate Account Prevention"""
        try:
            # Use same email twice
            test_email = f"duplicate.test.{int(time.time())}@example.com"
            
            # First request - should create account
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                
                if response.status != 200:
                    self.log_test(
                        "Duplicate Account Prevention",
                        False,
                        f"First request failed with status {response.status}"
                    )
                    return False
                
                data1 = await response.json()
                if data1.get("status") != "success":
                    self.log_test(
                        "Duplicate Account Prevention",
                        False,
                        f"First account creation failed: {data1.get('message')}"
                    )
                    return False
            
            # Small delay
            await asyncio.sleep(1)
            
            # Second request - should detect duplicate
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                
                if response.status == 200:
                    data2 = await response.json()
                    
                    if data2.get("status") == "duplicate":
                        self.log_test(
                            "Duplicate Account Prevention",
                            True,
                            f"Duplicate detection working correctly for {test_email}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Duplicate Account Prevention",
                            False,
                            f"Expected duplicate status, got: {data2.get('status')}"
                        )
                        return False
                else:
                    self.log_test(
                        "Duplicate Account Prevention",
                        False,
                        f"Second request failed with status {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Duplicate Account Prevention",
                False,
                error=str(e)
            )
            return False

    async def test_environment_variables_access(self):
        """Test 10: Environment Variables Access in Background Tasks"""
        try:
            # This test verifies that environment variables are accessible in background tasks
            # by checking if emails are sent successfully (which requires SENDGRID_API_KEY)
            
            test_email = f"env.vars.test.{int(time.time())}@example.com"
            
            async with self.session.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": test_email}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    emails_sent = data.get("emails_sent", {})
                    
                    # If emails are sent successfully, environment variables are accessible
                    if emails_sent.get("welcome_email") and emails_sent.get("admin_notification"):
                        self.log_test(
                            "Environment Variables Access",
                            True,
                            "Environment variables properly accessible in background tasks"
                        )
                        return True
                    else:
                        self.log_test(
                            "Environment Variables Access",
                            False,
                            "Environment variables not accessible in background tasks (email sending failed)"
                        )
                        return False
                else:
                    self.log_test(
                        "Environment Variables Access",
                        False,
                        f"Test request failed with status {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Environment Variables Access",
                False,
                error=str(e)
            )
            return False

    async def run_all_tests(self):
        """Run all SamCart webhook email tests"""
        print("🚀 Starting SamCart Webhook Email System Testing")
        print("=" * 60)
        print()
        
        await self.setup_session()
        
        try:
            # Run all tests
            tests = [
                self.test_webhook_endpoint_accessibility(),
                self.test_webhook_test_endpoint_basic(),
                self.test_email_service_validation(),
                self.test_background_task_email_sending(),
                self.test_sendgrid_authentication_fix(),
                self.test_end_to_end_payment_flow(),
                self.test_webhook_logs_functionality(),
                self.test_webhook_stats_functionality(),
                self.test_duplicate_account_prevention(),
                self.test_environment_variables_access()
            ]
            
            results = await asyncio.gather(*tests, return_exceptions=True)
            
            # Debug: Print all results
            print("🔍 DEBUG: Individual test results:")
            for i, result in enumerate(results):
                test_name = [
                    "Webhook Endpoint Accessibility",
                    "Webhook Test Endpoint Basic", 
                    "Email Service Validation",
                    "Background Task Email Sending",
                    "SendGrid Authentication Fix",
                    "End-to-End Payment Flow",
                    "Webhook Logs Functionality",
                    "Webhook Stats Functionality", 
                    "Duplicate Account Prevention",
                    "Environment Variables Access"
                ][i]
                print(f"   {i+1}. {test_name}: {result}")
            print()
            
            # Count results
            passed = sum(1 for result in results if result is True)
            failed = len(results) - passed
            
            print("=" * 60)
            print("🎯 TEST SUMMARY")
            print("=" * 60)
            print(f"✅ PASSED: {passed}")
            print(f"❌ FAILED: {failed}")
            print(f"📊 SUCCESS RATE: {(passed/len(results)*100):.1f}%")
            print()
            
            # Show failed tests
            if failed > 0:
                print("❌ FAILED TESTS:")
                for result in self.test_results:
                    if not result["success"]:
                        print(f"   • {result['test']}")
                        if result["error"]:
                            print(f"     Error: {result['error']}")
                print()
            
            # Overall assessment
            if passed == len(results):
                print("🎉 ALL TESTS PASSED - SamCart webhook email system is working correctly!")
                print("✅ Future SamCart payments will automatically send welcome emails")
            elif passed >= len(results) * 0.8:  # 80% pass rate
                print("⚠️ MOSTLY WORKING - Some minor issues detected")
                print("🔧 Review failed tests and fix issues before production")
            else:
                print("🚨 CRITICAL ISSUES DETECTED - Email system needs attention")
                print("❌ Future SamCart payments may not send welcome emails properly")
            
            return passed == len(results)
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = SamCartWebhookEmailTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())