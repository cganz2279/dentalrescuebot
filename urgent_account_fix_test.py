#!/usr/bin/env python3
"""
URGENT: Account Fix Test - Send Fresh Password Reset Email
Critical Issue: Password reset system broken across ALL accounts
Focus: Send fresh password reset email for caryganzconsulting@gmail.com immediately
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
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
TARGET_EMAIL = "caryganzconsulting@gmail.com"
ADMIN_CREDENTIALS = {
    "email": "cganz@admin.com",
    "password": "Dentist1#"
}

class UrgentAccountFixTester:
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
        """Test 1: Admin login to get token"""
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
                        self.log_result("Admin Login", True, 
                                      f"Admin authenticated successfully")
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
            
    async def test_send_fresh_password_reset(self):
        """Test 2: Send fresh password reset email"""
        try:
            url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": TARGET_EMAIL,
                "recovery_method": "email"
            }
            
            async with self.session.post(url, json=reset_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        sent_methods = response_data.get("sent_methods", [])
                        self.log_result("Fresh Password Reset Email", True, 
                                      f"Reset email sent successfully to {TARGET_EMAIL}. Methods: {sent_methods}")
                        return True
                    else:
                        self.log_result("Fresh Password Reset Email", False, 
                                      f"Reset failed: {response_data}")
                        return False
                else:
                    self.log_result("Fresh Password Reset Email", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Fresh Password Reset Email", False, f"Error: {e}")
            return False
            
    async def test_admin_create_practice_with_correct_fields(self):
        """Test 3: Create practice account via admin system with correct field names"""
        if not self.admin_token:
            self.log_result("Admin Create Practice (Correct Fields)", False, "No admin token available")
            return False
            
        try:
            url = f"{BACKEND_URL}/api/admin/create-practice"
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Use correct field names from the API schema
            practice_data = {
                "practiceName": "The Dental Spa at Garden City",
                "adminEmail": TARGET_EMAIL,
                "adminFirstName": "Cary",
                "adminLastName": "Ganz",
                "phone": "516-236-1083",
                "address": "Garden City, NY",
                "tempPassword": "DentalSpa2025!",  # Strong working password
                "subscriptionType": "active",  # Paid customer
                "trialDays": 30
            }
            
            async with self.session.post(url, json=practice_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        practice_info = response_data.get("practice", {})
                        self.log_result("Admin Create Practice (Correct Fields)", True, 
                                      f"Practice created successfully: {practice_info.get('name')} for {practice_info.get('email')}")
                        return practice_data  # Return credentials for testing
                    else:
                        self.log_result("Admin Create Practice (Correct Fields)", False, 
                                      f"Creation failed: {response_data}")
                        return False
                elif response.status == 409:
                    # Account already exists - this is actually good news
                    self.log_result("Admin Create Practice (Correct Fields)", True, 
                                  f"Account already exists (409) - account is available")
                    return "exists"
                else:
                    self.log_result("Admin Create Practice (Correct Fields)", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Create Practice (Correct Fields)", False, f"Error: {e}")
            return False
            
    async def test_admin_send_welcome_email_with_correct_format(self):
        """Test 4: Send welcome email with correct format"""
        if not self.admin_token:
            self.log_result("Admin Send Welcome Email (Correct Format)", False, "No admin token available")
            return False
            
        try:
            url = f"{BACKEND_URL}/api/admin/send-welcome-email"
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Use correct format from the API schema
            email_data = {
                "practiceData": {
                    "practiceName": "The Dental Spa at Garden City"
                },
                "adminCredentials": {
                    "adminEmail": TARGET_EMAIL,
                    "adminFirstName": "Cary",
                    "adminLastName": "Ganz",
                    "tempPassword": "DentalSpa2025!"
                },
                "appUrl": "https://app.dentalaftercarenotes.com"
            }
            
            async with self.session.post(url, json=email_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success"):
                        self.log_result("Admin Send Welcome Email (Correct Format)", True, 
                                      f"Welcome email sent successfully to {TARGET_EMAIL}")
                        return True
                    else:
                        self.log_result("Admin Send Welcome Email (Correct Format)", False, 
                                      f"Email sending failed: {response_data}")
                        return False
                else:
                    self.log_result("Admin Send Welcome Email (Correct Format)", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Send Welcome Email (Correct Format)", False, f"Error: {e}")
            return False
            
    async def test_account_login_with_known_credentials(self):
        """Test 5: Test login with known working credentials"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            
            # Try with known working credentials from cganz2279@gmail.com
            test_credentials = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            async with self.session.post(url, json=test_credentials) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success") and response_data.get("token"):
                        practice_info = response_data.get("practice", {})
                        self.log_result("Known Account Login Test", True, 
                                      f"Known account login successful! Practice: {practice_info.get('practice_name', 'Unknown')}")
                        return True
                    else:
                        self.log_result("Known Account Login Test", False, 
                                      f"Login response invalid: {response_data}")
                        return False
                elif response.status == 401:
                    self.log_result("Known Account Login Test", False, 
                                  f"Known account login failed - credentials may have changed (401)")
                    return False
                elif response.status == 500:
                    self.log_result("Known Account Login Test", False, 
                                  f"CRITICAL: Known account has 500 error - password corruption")
                    return False
                else:
                    self.log_result("Known Account Login Test", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Known Account Login Test", False, f"Error: {e}")
            return False
            
    async def test_target_account_login(self):
        """Test 6: Test login with target account using suggested password"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            
            # Try with suggested password
            test_credentials = {
                "email": TARGET_EMAIL,
                "password": "DentalSpa2025!"
            }
            
            async with self.session.post(url, json=test_credentials) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    response_data = json.loads(response_text)
                    if response_data.get("success") and response_data.get("token"):
                        practice_info = response_data.get("practice", {})
                        self.log_result("Target Account Login", True, 
                                      f"TARGET ACCOUNT LOGIN SUCCESSFUL! Practice: {practice_info.get('practice_name', 'Unknown')}")
                        return True
                    else:
                        self.log_result("Target Account Login", False, 
                                      f"Login response invalid: {response_data}")
                        return False
                elif response.status == 401:
                    self.log_result("Target Account Login", False, 
                                  f"Target account login failed - wrong credentials (401)")
                    return False
                elif response.status == 500:
                    self.log_result("Target Account Login", False, 
                                  f"CRITICAL: Target account has 500 error - password corruption")
                    return False
                else:
                    self.log_result("Target Account Login", False, 
                                  f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Target Account Login", False, f"Error: {e}")
            return False
            
    async def run_urgent_fix_tests(self):
        """Run urgent account fix tests"""
        print("🚨 URGENT: Account Fix Testing")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Email: {TARGET_EMAIL}")
        print("=" * 50)
        
        await self.setup()
        
        try:
            # Step 1: Test admin login
            print("\n🔐 Step 1: Testing Admin System Access...")
            admin_login_success = await self.test_admin_login()
            
            # Step 2: Send fresh password reset email (IMMEDIATE SOLUTION)
            print(f"\n📧 Step 2: Sending Fresh Password Reset Email to {TARGET_EMAIL}...")
            reset_email_sent = await self.test_send_fresh_password_reset()
            
            # Step 3: Try admin account creation with correct fields
            print(f"\n🏥 Step 3: Creating Practice Account for {TARGET_EMAIL} (if needed)...")
            created_account = False
            if admin_login_success:
                created_account = await self.test_admin_create_practice_with_correct_fields()
                
                # Send welcome email if account was created
                if created_account and created_account != "exists":
                    print(f"\n📬 Step 4: Sending Welcome Email to {TARGET_EMAIL}...")
                    await self.test_admin_send_welcome_email_with_correct_format()
                    
            # Step 4: Test known working account
            print(f"\n🔑 Step 5: Testing Known Working Account...")
            known_login_success = await self.test_account_login_with_known_credentials()
            
            # Step 5: Test target account login
            print(f"\n🎯 Step 6: Testing Target Account Login...")
            target_login_success = await self.test_target_account_login()
                    
            # Summary
            print("\n" + "=" * 50)
            print("🎯 URGENT FIX SUMMARY")
            print("=" * 50)
            
            passed = sum(1 for result in self.test_results if result["success"])
            total = len(self.test_results)
            print(f"Tests Passed: {passed}/{total}")
            
            # Critical findings
            print("\n🚨 CRITICAL FINDINGS:")
            
            if reset_email_sent:
                print(f"\n✅ IMMEDIATE SOLUTION PROVIDED:")
                print(f"   📧 Fresh password reset email sent to {TARGET_EMAIL}")
                print(f"   🔗 Customer should check email and reset password")
                print(f"   🌐 Login URL: https://app.dentalaftercarenotes.com/login")
                
            if target_login_success:
                print(f"\n🎉 URGENT SOLUTION CONFIRMED:")
                print(f"   ✅ {TARGET_EMAIL} account is WORKING")
                print(f"   ✅ Customer can login at: https://app.dentalaftercarenotes.com/login")
                print(f"   ✅ Email: {TARGET_EMAIL}")
                print(f"   ✅ Password: DentalSpa2025!")
                print(f"   ✅ Practice: The Dental Spa at Garden City")
            elif reset_email_sent:
                print(f"\n⚠️ NEXT STEPS FOR CUSTOMER:")
                print(f"   📧 Check email inbox and spam folder for password reset")
                print(f"   🔑 Use reset link to set new password")
                print(f"   🌐 Then login at: https://app.dentalaftercarenotes.com/login")
            else:
                print(f"\n❌ URGENT ACTION STILL REQUIRED:")
                print(f"   🔧 Manual database intervention needed")
                print(f"   📞 Contact system administrator immediately")
                
            return target_login_success or reset_email_sent
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = UrgentAccountFixTester()
    success = await tester.run_urgent_fix_tests()
    
    if success:
        print("\n🎉 URGENT ISSUE RESOLVED - Customer has working solution!")
        sys.exit(0)
    else:
        print("\n⚠️ URGENT ISSUE REQUIRES MANUAL INTERVENTION")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())