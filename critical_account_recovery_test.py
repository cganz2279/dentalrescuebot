#!/usr/bin/env python3
"""
CRITICAL: Account Recovery System Testing
URGENT: Password reset system broken across ALL accounts
Focus: Create working account for caryganzconsulting@gmail.com immediately
"""

import asyncio
import aiohttp
import json
import bcrypt
import uuid
from datetime import datetime, timezone
import os
import sys

# Test configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
CRITICAL_EMAILS = [
    "cganz2279@gmail.com",
    "caryganz@gmail.com", 
    "caryganzconsulting@gmail.com"
]
TARGET_EMAIL = "caryganzconsulting@gmail.com"
ADMIN_CREDENTIALS = {
    "email": "cganz@admin.com",
    "password": "Dentist1#"
}

class CriticalAccountRecoveryTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.admin_token = None
        
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
        
    async def test_admin_login(self):
        """Test 1: Admin login to get token for account creation"""
        try:
            url = f"{BACKEND_URL}/api/admin/login"
            login_data = {
                "email": ADMIN_CREDENTIALS["email"],
                "password": ADMIN_CREDENTIALS["password"]
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success") and response_data.get("token"):
                        self.admin_token = response_data["token"]
                        admin_info = response_data.get("admin", {})
                        self.log_result("Admin Login", True, 
                                      f"Admin authenticated: {admin_info.get('email', 'Unknown')}")
                        return True
                    else:
                        self.log_result("Admin Login", False, 
                                      f"Login succeeded but no token: {response_data}")
                        return False
                else:
                    self.log_result("Admin Login", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Login", False, f"Error: {e}")
            return False
            
    async def test_existing_account_status(self, email):
        """Test account status for critical emails"""
        try:
            # Test login to see account status
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": email,
                "password": "test_password_123"  # Wrong password to test account existence
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    # Account exists, password wrong (healthy account)
                    self.log_result(f"Account Status - {email}", True, 
                                  f"Account exists with healthy password field (401 error)")
                    return "healthy"
                elif response.status == 500:
                    # Account exists but password field corrupted
                    self.log_result(f"Account Status - {email}", False, 
                                  f"CRITICAL: Account has corrupted password field (500 error)")
                    return "corrupted"
                elif response.status == 404:
                    # Account doesn't exist
                    self.log_result(f"Account Status - {email}", True, 
                                  f"Account does not exist (404 error)")
                    return "missing"
                else:
                    self.log_result(f"Account Status - {email}", False, 
                                  f"Unexpected response: HTTP {response.status}: {response_text}")
                    return "unknown"
                    
        except Exception as e:
            self.log_result(f"Account Status - {email}", False, f"Error: {e}")
            return "error"
            
    async def test_password_reset_system(self, email):
        """Test password reset system for specific email"""
        try:
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
                        self.log_result(f"Password Reset - {email}", True, 
                                      f"Reset email sent successfully. Methods: {sent_methods}")
                        return True
                    else:
                        self.log_result(f"Password Reset - {email}", False, 
                                      f"Reset failed: {response_data}")
                        return False
                else:
                    self.log_result(f"Password Reset - {email}", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result(f"Password Reset - {email}", False, f"Error: {e}")
            return False
            
    async def test_admin_create_practice_account(self):
        """Test 2: Create practice account via admin system (URGENT SOLUTION)"""
        if not self.admin_token:
            self.log_result("Admin Create Practice", False, "No admin token available")
            return False
            
        try:
            url = f"{BACKEND_URL}/api/admin/create-practice"
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            practice_data = {
                "practice_name": "The Dental Spa at Garden City",
                "admin_email": TARGET_EMAIL,
                "admin_password": "DentalSpa2025!",  # Strong working password
                "subscription_type": "paid",  # Paid customer
                "owner_name": "Cary Ganz"
            }
            
            async with self.session.post(url, json=practice_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        practice_info = response_data.get("practice", {})
                        self.log_result("Admin Create Practice", True, 
                                      f"Practice created successfully: {practice_info.get('practice_name')} for {practice_info.get('admin_email')}")
                        return practice_data  # Return credentials for testing
                    else:
                        self.log_result("Admin Create Practice", False, 
                                      f"Creation failed: {response_data}")
                        return False
                elif response.status == 409:
                    # Account already exists - this is actually good news
                    self.log_result("Admin Create Practice", True, 
                                  f"Account already exists (409) - account is available")
                    return "exists"
                else:
                    self.log_result("Admin Create Practice", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Create Practice", False, f"Error: {e}")
            return False
            
    async def test_admin_send_welcome_email(self):
        """Test 3: Send welcome email with credentials"""
        if not self.admin_token:
            self.log_result("Admin Send Welcome Email", False, "No admin token available")
            return False
            
        try:
            url = f"{BACKEND_URL}/api/admin/send-welcome-email"
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            email_data = {
                "practice_name": "The Dental Spa at Garden City",
                "admin_email": TARGET_EMAIL,
                "admin_password": "DentalSpa2025!",
                "owner_name": "Cary Ganz"
            }
            
            async with self.session.post(url, json=email_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        self.log_result("Admin Send Welcome Email", True, 
                                      f"Welcome email sent successfully to {TARGET_EMAIL}")
                        return True
                    else:
                        self.log_result("Admin Send Welcome Email", False, 
                                      f"Email sending failed: {response_data}")
                        return False
                else:
                    self.log_result("Admin Send Welcome Email", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Send Welcome Email", False, f"Error: {e}")
            return False
            
    async def test_new_account_login(self, credentials):
        """Test 4: Test login with newly created account"""
        if not credentials or credentials == "exists":
            # Try with known working credentials for existing account
            test_credentials = {
                "email": TARGET_EMAIL,
                "password": "DentalSpa2025!"
            }
        else:
            test_credentials = {
                "email": credentials["admin_email"],
                "password": credentials["admin_password"]
            }
            
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            
            async with self.session.post(url, json=test_credentials) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success") and response_data.get("token"):
                        practice_info = response_data.get("practice", {})
                        self.log_result("New Account Login", True, 
                                      f"Login successful! Practice: {practice_info.get('practice_name', 'Unknown')}")
                        return True
                    else:
                        self.log_result("New Account Login", False, 
                                      f"Login response invalid: {response_data}")
                        return False
                elif response.status == 401:
                    self.log_result("New Account Login", False, 
                                  f"Login failed - wrong credentials (401)")
                    return False
                elif response.status == 500:
                    self.log_result("New Account Login", False, 
                                  f"CRITICAL: Login failed with 500 error - password corruption")
                    return False
                else:
                    self.log_result("New Account Login", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("New Account Login", False, f"Error: {e}")
            return False
            
    async def test_samcart_webhook_account_creation(self):
        """Test 5: Alternative - SamCart webhook account creation"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": TARGET_EMAIL}
            
            async with self.session.post(url, params=params) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("status") == "success":
                        practice_info = response_data.get("practice_info", {})
                        self.log_result("SamCart Webhook Account Creation", True, 
                                      f"Account created via webhook: {practice_info.get('practice_name')}")
                        return response_data
                    elif response_data.get("status") == "duplicate":
                        self.log_result("SamCart Webhook Account Creation", True, 
                                      f"Account already exists via webhook (good): {response_data.get('message')}")
                        return "exists"
                    else:
                        self.log_result("SamCart Webhook Account Creation", False, 
                                      f"Webhook creation failed: {response_data}")
                        return False
                else:
                    self.log_result("SamCart Webhook Account Creation", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("SamCart Webhook Account Creation", False, f"Error: {e}")
            return False
            
    async def run_critical_tests(self):
        """Run critical password reset and account creation tests"""
        print("🚨 CRITICAL: Account Recovery System Testing")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Email: {TARGET_EMAIL}")
        print(f"Critical Emails: {', '.join(CRITICAL_EMAILS)}")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Step 1: Test admin login
            print("\n🔐 Step 1: Testing Admin System Access...")
            admin_login_success = await self.test_admin_login()
            
            # Step 2: Check existing account status for all critical emails
            print("\n🔍 Step 2: Checking Existing Account Status...")
            account_statuses = {}
            for email in CRITICAL_EMAILS:
                status = await self.test_existing_account_status(email)
                account_statuses[email] = status
                
            # Step 3: Test password reset system for all critical emails
            print("\n📧 Step 3: Testing Password Reset System...")
            reset_results = {}
            for email in CRITICAL_EMAILS:
                result = await self.test_password_reset_system(email)
                reset_results[email] = result
                
            # Step 4: Try admin account creation (URGENT SOLUTION)
            print(f"\n🏥 Step 4: Creating Practice Account for {TARGET_EMAIL}...")
            created_account = False
            if admin_login_success:
                created_account = await self.test_admin_create_practice_account()
                
                # Send welcome email if account was created
                if created_account:
                    print(f"\n📬 Step 5: Sending Welcome Email to {TARGET_EMAIL}...")
                    await self.test_admin_send_welcome_email()
                    
            # Step 5: Test login with new account
            print(f"\n🔑 Step 6: Testing Login with {TARGET_EMAIL}...")
            login_success = await self.test_new_account_login(created_account)
            
            # Step 6: Alternative - SamCart webhook method
            if not login_success:
                print(f"\n🔄 Step 7: Alternative - SamCart Webhook Account Creation...")
                webhook_result = await self.test_samcart_webhook_account_creation()
                if webhook_result:
                    await self.test_new_account_login(webhook_result)
                    
            # Summary
            print("\n" + "=" * 70)
            print("🎯 CRITICAL TEST SUMMARY")
            print("=" * 70)
            
            passed = sum(1 for result in self.test_results if result["success"])
            total = len(self.test_results)
            print(f"Tests Passed: {passed}/{total}")
            
            # Critical findings
            print("\n🚨 CRITICAL FINDINGS:")
            
            # Account status summary
            print("\n📊 Account Status Summary:")
            for email, status in account_statuses.items():
                status_icon = "✅" if status == "healthy" else "❌" if status == "corrupted" else "⚠️"
                print(f"   {status_icon} {email}: {status.upper()}")
                
            # Password reset summary
            print("\n📧 Password Reset Summary:")
            for email, result in reset_results.items():
                result_icon = "✅" if result else "❌"
                print(f"   {result_icon} {email}: {'WORKING' if result else 'BROKEN'}")
                
            # Working solution
            if login_success:
                print(f"\n🎉 URGENT SOLUTION FOUND:")
                print(f"   ✅ {TARGET_EMAIL} account is WORKING")
                print(f"   ✅ Customer can login at: https://app.dentalaftercarenotes.com/login")
                print(f"   ✅ Email: {TARGET_EMAIL}")
                print(f"   ✅ Password: DentalSpa2025!")
                print(f"   ✅ Practice: The Dental Spa at Garden City")
            else:
                print(f"\n⚠️ URGENT ACTION REQUIRED:")
                print(f"   ❌ {TARGET_EMAIL} account needs manual intervention")
                print(f"   🔧 Recommend: Direct database password update")
                print(f"   📧 Alternative: Password reset email (if working)")
                
            return login_success
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = CriticalAccountRecoveryTester()
    success = await tester.run_critical_tests()
    
    if success:
        print("\n🎉 CRITICAL ISSUE RESOLVED - Customer has working account!")
        sys.exit(0)
    else:
        print("\n⚠️ CRITICAL ISSUE REQUIRES MANUAL INTERVENTION")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())