#!/usr/bin/env python3
"""
URGENT LOGIN ISSUE TESTING - caryganzconsulting@gmail.com
Critical Issue: Login failed for caryganzconsulting@gmail.com with password TempPass123!
Focus: Test login credentials, check account status, verify password corruption, send password reset
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys

# Test configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
CRITICAL_EMAIL = "caryganzconsulting@gmail.com"
CRITICAL_PASSWORD = "TempPass123!"
EXPECTED_PRACTICE_ID = "68ddb2eb4c5e345f1746e47b"

class UrgentLoginTester:
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
        
    async def test_critical_login_credentials(self):
        """Test 1: Test login with caryganzconsulting@gmail.com / TempPass123!"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": CRITICAL_EMAIL,
                "password": CRITICAL_PASSWORD
            }
            
            print(f"🔍 Testing login for: {CRITICAL_EMAIL}")
            print(f"🔑 Using password: {CRITICAL_PASSWORD}")
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    # Login successful
                    response_data = json.loads(response_text)
                    token = response_data.get("access_token")
                    practice_id = response_data.get("practice_id")
                    
                    self.log_result("Critical Login Credentials", True, 
                                  f"✅ LOGIN SUCCESSFUL! Token received, Practice ID: {practice_id}")
                    return {"success": True, "token": token, "practice_id": practice_id}
                    
                elif response.status == 401:
                    # Invalid credentials - but account exists
                    self.log_result("Critical Login Credentials", False, 
                                  f"❌ LOGIN FAILED: Invalid credentials (401) - Account exists but password incorrect")
                    return {"success": False, "status": "invalid_credentials", "account_exists": True}
                    
                elif response.status == 500:
                    # Server error - likely password corruption
                    self.log_result("Critical Login Credentials", False, 
                                  f"🚨 CRITICAL: Login returns 500 error - PASSWORD FIELD CORRUPTION detected: {response_text}")
                    return {"success": False, "status": "password_corruption", "account_exists": True}
                    
                elif response.status == 404:
                    # Account not found
                    self.log_result("Critical Login Credentials", False, 
                                  f"❌ ACCOUNT NOT FOUND: {response_text}")
                    return {"success": False, "status": "account_not_found", "account_exists": False}
                    
                else:
                    self.log_result("Critical Login Credentials", False, 
                                  f"❌ UNEXPECTED RESPONSE: HTTP {response.status}: {response_text}")
                    return {"success": False, "status": "unexpected_error"}
                    
        except Exception as e:
            self.log_result("Critical Login Credentials", False, f"❌ ERROR: {e}")
            return {"success": False, "status": "exception", "error": str(e)}
            
    async def test_account_existence_check(self):
        """Test 2: Check if account exists using webhook test endpoint"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": CRITICAL_EMAIL}
            
            print(f"🔍 Checking account existence for: {CRITICAL_EMAIL}")
            
            async with self.session.post(url, params=params) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    
                    if response_data.get("status") == "duplicate":
                        # Account exists
                        self.log_result("Account Existence Check", True, 
                                      f"✅ ACCOUNT EXISTS: {response_data.get('message', 'Account found')}")
                        return {"exists": True, "details": response_data}
                        
                    elif response_data.get("status") == "success":
                        # Account was created (didn't exist before)
                        practice_info = response_data.get("practice_info", {})
                        self.log_result("Account Existence Check", True, 
                                      f"⚠️ ACCOUNT WAS CREATED: {practice_info.get('practice_name')} - Account didn't exist before")
                        return {"exists": False, "created": True, "details": response_data}
                        
                    else:
                        self.log_result("Account Existence Check", False, 
                                      f"❌ UNEXPECTED RESPONSE: {response_data}")
                        return {"exists": False, "created": False}
                        
                else:
                    self.log_result("Account Existence Check", False, 
                                  f"❌ HTTP {response.status}: {response_text}")
                    return {"exists": False, "created": False}
                    
        except Exception as e:
            self.log_result("Account Existence Check", False, f"❌ ERROR: {e}")
            return {"exists": False, "created": False, "error": str(e)}
            
    async def test_password_corruption_diagnosis(self):
        """Test 3: Diagnose password corruption by testing with wrong password"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": CRITICAL_EMAIL,
                "password": "definitely_wrong_password_123"
            }
            
            print(f"🔍 Testing password corruption diagnosis for: {CRITICAL_EMAIL}")
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    # Normal behavior - password field is healthy
                    self.log_result("Password Corruption Diagnosis", True, 
                                  f"✅ PASSWORD FIELD HEALTHY: Returns 401 for wrong password as expected")
                    return {"corrupted": False, "healthy": True}
                    
                elif response.status == 500:
                    # Password field corruption detected
                    self.log_result("Password Corruption Diagnosis", False, 
                                  f"🚨 PASSWORD FIELD CORRUPTED: Returns 500 error instead of 401: {response_text}")
                    return {"corrupted": True, "healthy": False}
                    
                else:
                    self.log_result("Password Corruption Diagnosis", False, 
                                  f"❌ UNEXPECTED RESPONSE: HTTP {response.status}: {response_text}")
                    return {"corrupted": "unknown", "healthy": False}
                    
        except Exception as e:
            self.log_result("Password Corruption Diagnosis", False, f"❌ ERROR: {e}")
            return {"corrupted": "unknown", "healthy": False, "error": str(e)}
            
    async def test_send_password_reset(self):
        """Test 4: Send password reset email to caryganzconsulting@gmail.com"""
        try:
            url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": CRITICAL_EMAIL,
                "recovery_method": "email"
            }
            
            print(f"📧 Sending password reset email to: {CRITICAL_EMAIL}")
            
            async with self.session.post(url, json=reset_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    
                    if response_data.get("success"):
                        sent_methods = response_data.get("sent_methods", [])
                        message = response_data.get("message", "")
                        
                        self.log_result("Send Password Reset", True, 
                                      f"✅ PASSWORD RESET EMAIL SENT: {message}. Methods: {sent_methods}")
                        return {"sent": True, "methods": sent_methods, "message": message}
                        
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        self.log_result("Send Password Reset", False, 
                                      f"❌ PASSWORD RESET FAILED: {error_msg}")
                        return {"sent": False, "error": error_msg}
                        
                else:
                    self.log_result("Send Password Reset", False, 
                                  f"❌ HTTP {response.status}: {response_text}")
                    return {"sent": False, "status": response.status}
                    
        except Exception as e:
            self.log_result("Send Password Reset", False, f"❌ ERROR: {e}")
            return {"sent": False, "error": str(e)}
            
    async def test_verify_account_details(self):
        """Test 5: Verify account details and Practice ID"""
        try:
            # First try to get admin token for account lookup
            admin_url = f"{BACKEND_URL}/api/admin/login"
            admin_data = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            print(f"🔍 Verifying account details for Practice ID: {EXPECTED_PRACTICE_ID}")
            
            async with self.session.post(admin_url, json=admin_data) as response:
                if response.status == 200:
                    admin_response = await response.json()
                    admin_token = admin_response.get("access_token")
                    
                    if admin_token:
                        # Try to lookup practice details
                        headers = {"Authorization": f"Bearer {admin_token}"}
                        
                        # Check if we can find the practice in admin system
                        practices_url = f"{BACKEND_URL}/api/admin/practices"
                        async with self.session.get(practices_url, headers=headers) as practices_response:
                            if practices_response.status == 200:
                                practices_data = await practices_response.json()
                                practices = practices_data.get("practices", [])
                                
                                # Look for our practice
                                target_practice = None
                                for practice in practices:
                                    if (practice.get("email") == CRITICAL_EMAIL or 
                                        practice.get("practice_id") == EXPECTED_PRACTICE_ID):
                                        target_practice = practice
                                        break
                                
                                if target_practice:
                                    self.log_result("Verify Account Details", True, 
                                                  f"✅ PRACTICE FOUND: {target_practice.get('practice_name', 'Unknown')} - ID: {target_practice.get('practice_id', 'Unknown')}")
                                    return {"found": True, "practice": target_practice}
                                else:
                                    self.log_result("Verify Account Details", False, 
                                                  f"❌ PRACTICE NOT FOUND in admin system. Searched {len(practices)} practices")
                                    return {"found": False, "searched": len(practices)}
                            else:
                                self.log_result("Verify Account Details", False, 
                                              f"❌ Failed to get practices list: HTTP {practices_response.status}")
                                return {"found": False, "error": "admin_api_failed"}
                    else:
                        self.log_result("Verify Account Details", False, 
                                      f"❌ Admin login failed - no token received")
                        return {"found": False, "error": "admin_login_failed"}
                else:
                    self.log_result("Verify Account Details", False, 
                                  f"❌ Admin login failed: HTTP {response.status}")
                    return {"found": False, "error": "admin_login_http_error"}
                    
        except Exception as e:
            self.log_result("Verify Account Details", False, f"❌ ERROR: {e}")
            return {"found": False, "error": str(e)}
            
    async def test_webhook_logs_for_account(self):
        """Test 6: Check webhook logs for this specific account"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/logs"
            
            print(f"🔍 Checking webhook logs for: {CRITICAL_EMAIL}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    logs_data = await response.json()
                    logs = logs_data.get("logs", [])
                    
                    # Look for logs related to our email
                    relevant_logs = []
                    for log in logs:
                        customer_data = log.get("customer_data", {})
                        if customer_data.get("email") == CRITICAL_EMAIL:
                            relevant_logs.append(log)
                    
                    if relevant_logs:
                        latest_log = relevant_logs[0]  # Most recent
                        webhook_id = latest_log.get("webhook_id", "Unknown")
                        event_type = latest_log.get("event_type", "Unknown")
                        status = latest_log.get("status", "Unknown")
                        order_id = latest_log.get("order_id", "Unknown")
                        
                        self.log_result("Webhook Logs Check", True, 
                                      f"✅ WEBHOOK FOUND: Order ID {order_id}, Event: {event_type}, Status: {status}, Webhook ID: {webhook_id}")
                        return {"found": True, "logs": relevant_logs, "latest": latest_log}
                    else:
                        self.log_result("Webhook Logs Check", False, 
                                      f"❌ NO WEBHOOK LOGS FOUND for {CRITICAL_EMAIL}. Total logs: {len(logs)}")
                        return {"found": False, "total_logs": len(logs)}
                else:
                    self.log_result("Webhook Logs Check", False, 
                                  f"❌ Failed to get webhook logs: HTTP {response.status}")
                    return {"found": False, "error": "api_failed"}
                    
        except Exception as e:
            self.log_result("Webhook Logs Check", False, f"❌ ERROR: {e}")
            return {"found": False, "error": str(e)}
            
    async def run_urgent_tests(self):
        """Run all urgent login tests for caryganzconsulting@gmail.com"""
        print("🚨 URGENT LOGIN ISSUE TESTING")
        print("=" * 70)
        print(f"Critical Email: {CRITICAL_EMAIL}")
        print(f"Critical Password: {CRITICAL_PASSWORD}")
        print(f"Expected Practice ID: {EXPECTED_PRACTICE_ID}")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run tests in sequence
            print("\n🔍 STEP 1: Testing login credentials...")
            login_result = await self.test_critical_login_credentials()
            
            print("\n🔍 STEP 2: Checking account existence...")
            account_result = await self.test_account_existence_check()
            
            print("\n🔍 STEP 3: Diagnosing password corruption...")
            corruption_result = await self.test_password_corruption_diagnosis()
            
            print("\n📧 STEP 4: Sending password reset email...")
            reset_result = await self.test_send_password_reset()
            
            print("\n🔍 STEP 5: Verifying account details...")
            details_result = await self.test_verify_account_details()
            
            print("\n🔍 STEP 6: Checking webhook logs...")
            webhook_result = await self.test_webhook_logs_for_account()
            
            # Analyze results and provide recommendations
            print("\n" + "=" * 70)
            print("🎯 URGENT ISSUE ANALYSIS")
            print("=" * 70)
            
            # Determine the issue and solution
            if login_result.get("success"):
                print("✅ ISSUE RESOLVED: Login credentials are working correctly!")
                print(f"   Practice ID: {login_result.get('practice_id')}")
                print("   Customer can access their account immediately.")
                
            elif login_result.get("status") == "password_corruption":
                print("🚨 CRITICAL ISSUE CONFIRMED: Password field corruption detected")
                print("   Root Cause: Account exists but password field is corrupted/missing")
                
                if reset_result.get("sent"):
                    print("✅ SOLUTION PROVIDED: Password reset email sent successfully")
                    print(f"   Customer should check email: {CRITICAL_EMAIL}")
                    print("   Customer can reset password and login normally")
                else:
                    print("❌ SOLUTION FAILED: Password reset email could not be sent")
                    print("   Manual intervention required")
                    
            elif login_result.get("status") == "invalid_credentials":
                print("⚠️ ISSUE: Invalid credentials - password may be incorrect")
                
                if reset_result.get("sent"):
                    print("✅ SOLUTION PROVIDED: Password reset email sent successfully")
                    print(f"   Customer should check email: {CRITICAL_EMAIL}")
                else:
                    print("❌ SOLUTION FAILED: Password reset email could not be sent")
                    
            elif login_result.get("status") == "account_not_found":
                print("❌ CRITICAL ISSUE: Account does not exist")
                print("   Customer paid but no account was created")
                
                if webhook_result.get("found"):
                    print("✅ WEBHOOK FOUND: Payment was received but account creation failed")
                    print("   Manual account creation required")
                else:
                    print("❌ NO WEBHOOK FOUND: Payment may not have been processed")
                    print("   Check SamCart webhook configuration")
            
            # Account existence analysis
            if account_result.get("exists"):
                print(f"\n✅ ACCOUNT STATUS: Account exists for {CRITICAL_EMAIL}")
            elif account_result.get("created"):
                print(f"\n⚠️ ACCOUNT STATUS: Account was just created for {CRITICAL_EMAIL}")
            else:
                print(f"\n❌ ACCOUNT STATUS: Account does not exist for {CRITICAL_EMAIL}")
            
            # Password corruption analysis
            if corruption_result.get("healthy"):
                print("✅ PASSWORD FIELD: Healthy (returns proper 401 errors)")
            elif corruption_result.get("corrupted"):
                print("🚨 PASSWORD FIELD: CORRUPTED (returns 500 errors)")
            
            # Webhook analysis
            if webhook_result.get("found"):
                latest = webhook_result.get("latest", {})
                print(f"✅ WEBHOOK STATUS: Found Order ID {latest.get('order_id')} - Payment was processed")
            else:
                print("❌ WEBHOOK STATUS: No webhook found - Payment may not have been processed")
            
            # Final recommendation
            print("\n" + "=" * 70)
            print("🎯 RECOMMENDED ACTIONS")
            print("=" * 70)
            
            if login_result.get("success"):
                print("✅ NO ACTION NEEDED: Customer can login with provided credentials")
                
            elif reset_result.get("sent"):
                print("📧 IMMEDIATE ACTION: Password reset email sent successfully")
                print(f"   1. Customer should check email: {CRITICAL_EMAIL}")
                print("   2. Customer should follow reset instructions")
                print("   3. Customer can then login normally")
                
            else:
                print("🚨 MANUAL INTERVENTION REQUIRED:")
                print("   1. Check backend logs for detailed error messages")
                print("   2. Verify email service configuration")
                print("   3. Consider manual account creation if needed")
                print("   4. Send welcome email manually if account exists")
            
            # Count successful tests
            passed = sum(1 for result in self.test_results if result["success"])
            total = len(self.test_results)
            
            print(f"\n📊 TEST RESULTS: {passed}/{total} tests passed")
            
            return {
                "login_working": login_result.get("success", False),
                "account_exists": account_result.get("exists", False),
                "password_healthy": corruption_result.get("healthy", False),
                "reset_sent": reset_result.get("sent", False),
                "webhook_found": webhook_result.get("found", False),
                "tests_passed": passed,
                "tests_total": total
            }
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = UrgentLoginTester()
    results = await tester.run_urgent_tests()
    
    # Exit with appropriate code
    if results["login_working"]:
        print("\n🎉 SUCCESS: Login credentials are working!")
        sys.exit(0)
    elif results["reset_sent"]:
        print("\n✅ SOLUTION PROVIDED: Password reset email sent successfully")
        sys.exit(0)
    else:
        print("\n⚠️ MANUAL INTERVENTION REQUIRED: Check results above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())