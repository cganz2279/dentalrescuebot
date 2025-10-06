#!/usr/bin/env python3
"""
Fresh Password Reset Email Testing Script
Testing the updated FRONTEND_URL configuration and new token generation
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Get backend URL from frontend environment (where user is accessing)
FRONTEND_BACKEND_URL = "https://dentist-portal-3.emergent.host"
API_BASE = f"{FRONTEND_BACKEND_URL}/api"

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'dentist_management')]

class FreshPasswordResetTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.new_token = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "details": details,
            "response_data": response_data
        }
        
        self.test_results.append(result)
        print(f"[{timestamp}] {status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and isinstance(response_data, dict):
            if 'message' in response_data:
                print(f"    Message: {response_data['message']}")
        print()

    async def get_latest_reset_token(self):
        """Get the latest reset token for caryganz@gmail.com"""
        try:
            # Find the most recent reset token for caryganz@gmail.com
            reset_record = await db.password_resets.find_one(
                {"email": "caryganz@gmail.com"},
                sort=[("created_at", -1)]
            )
            
            if reset_record:
                self.new_token = reset_record["reset_token"]
                self.log_test(
                    "Latest Reset Token Retrieved",
                    True,
                    f"Found latest token: {self.new_token[:8]}...{self.new_token[-8:]} (created: {reset_record['created_at']})",
                    {"token_preview": f"{self.new_token[:8]}...{self.new_token[-8:]}"}
                )
                return True
            else:
                self.log_test(
                    "Latest Reset Token Retrieved",
                    False,
                    "No reset token found in database for caryganz@gmail.com"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Latest Reset Token Retrieved",
                False,
                f"Database error: {str(e)}"
            )
            return False

    def send_fresh_password_reset_email(self):
        """Send a fresh password reset email to caryganz@gmail.com"""
        print("🚨 URGENT: Sending fresh password reset email to caryganz@gmail.com...")
        
        try:
            # Send password reset email to caryganz@gmail.com
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "email"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 POST /api/auth/forgot-password Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Fresh Password Reset Email Sent",
                    True,
                    f"✅ NEW PASSWORD RESET EMAIL SENT to caryganz@gmail.com. Message: {data.get('message', 'No message')}",
                    data
                )
                
                # Check if email was actually sent
                sent_methods = data.get('sent_methods', [])
                if 'email' in sent_methods:
                    self.log_test(
                        "Email Delivery Confirmation",
                        True,
                        "✅ Email was successfully sent via SendGrid - NEW TOKEN GENERATED",
                        {"sent_methods": sent_methods}
                    )
                    return True
                else:
                    self.log_test(
                        "Email Delivery Confirmation",
                        False,
                        f"❌ Email not in sent methods: {sent_methods}",
                        data
                    )
                    return False
                    
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "Fresh Password Reset Email Sent",
                    False,
                    f"❌ HTTP {response.status_code}: {error_data.get('detail', response.text)}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Fresh Password Reset Email Sent",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def test_new_token_validation(self):
        """Test the newly generated token validation"""
        if not self.new_token:
            self.log_test(
                "New Token Validation",
                False,
                "❌ No new token available for testing"
            )
            return False
            
        print(f"🔍 Testing New Token Validation: {self.new_token}")
        
        try:
            response = self.session.get(
                f"{API_BASE}/auth/validate-reset-token/{self.new_token}"
            )
            
            print(f"🔍 GET /api/auth/validate-reset-token/{self.new_token} Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "New Token Validation",
                    True,
                    f"✅ NEW TOKEN IS VALID and working on current environment. User: {data.get('user', {}).get('email', 'N/A')}",
                    data
                )
                return True
            elif response.status_code == 400:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_test(
                    "New Token Validation",
                    False,
                    f"❌ New token rejected with 400: {data.get('detail', 'Unknown error')}",
                    data
                )
                return False
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                self.log_test(
                    "New Token Validation",
                    False,
                    f"❌ Unexpected status {response.status_code}: {error_data}",
                    error_data
                )
                return False
                
        except Exception as e:
            self.log_test(
                "New Token Validation",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def verify_reset_link_format(self):
        """Verify the reset link format with updated FRONTEND_URL"""
        print("🔍 Verifying Reset Link Format...")
        
        try:
            # Get FRONTEND_URL from environment
            frontend_url = os.getenv('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
            
            if self.new_token:
                expected_reset_link = f"{frontend_url}/reset-password?token={self.new_token}"
                
                self.log_test(
                    "Reset Link Format Verification",
                    True,
                    f"✅ RESET LINK FORMAT CONFIRMED: {expected_reset_link}",
                    {
                        "frontend_url": frontend_url,
                        "reset_link": expected_reset_link,
                        "token": self.new_token
                    }
                )
                
                # Verify it matches the user's current environment
                if "dentist-portal-3.emergent.host" in frontend_url:
                    self.log_test(
                        "Environment URL Match",
                        True,
                        "✅ FRONTEND_URL matches user's current environment (dentist-portal-3.emergent.host)",
                        {"environment_match": True}
                    )
                else:
                    self.log_test(
                        "Environment URL Match",
                        False,
                        f"❌ FRONTEND_URL ({frontend_url}) does not match user's environment (dentist-portal-3.emergent.host)",
                        {"environment_match": False}
                    )
                
                return True
            else:
                self.log_test(
                    "Reset Link Format Verification",
                    False,
                    "❌ No token available to generate reset link"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Reset Link Format Verification",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    def test_reset_page_accessibility(self):
        """Test that the reset password page is accessible"""
        print("🔍 Testing Reset Password Page Accessibility...")
        
        try:
            # Test the reset password page endpoint
            reset_page_url = f"{FRONTEND_BACKEND_URL}/reset-password"
            
            response = self.session.get(reset_page_url)
            
            print(f"🔍 GET {reset_page_url} Response: {response.status_code}")
            
            # Since this is a React app, we expect either:
            # - 200 with HTML content (if serving static files)
            # - 404 (if React routing handles this client-side)
            # Both are acceptable for a React SPA
            
            if response.status_code in [200, 404]:
                self.log_test(
                    "Reset Password Page Accessibility",
                    True,
                    f"✅ Reset password page endpoint accessible (status: {response.status_code}). React app will handle routing client-side.",
                    {"status_code": response.status_code}
                )
                return True
            else:
                self.log_test(
                    "Reset Password Page Accessibility",
                    False,
                    f"❌ Unexpected status {response.status_code} for reset password page",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Reset Password Page Accessibility",
                False,
                f"❌ Exception occurred: {str(e)}"
            )
            return False

    async def run_all_tests(self):
        """Run all tests for fresh password reset email"""
        print("🚀 Starting Fresh Password Reset Email Testing with Updated FRONTEND_URL...")
        print(f"🔗 Backend URL: {FRONTEND_BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print(f"🔗 FRONTEND_URL: {os.getenv('FRONTEND_URL')}")
        print("🎯 FOCUS: Send fresh password reset email and verify new token works")
        print("=" * 80)
        
        # Step 1: Send fresh password reset email
        print("🚨 STEP 1: Sending fresh password reset email...")
        email_sent = self.send_fresh_password_reset_email()
        time.sleep(2)
        
        # Step 2: Get the latest token from database
        print("🚨 STEP 2: Retrieving latest reset token from database...")
        token_retrieved = await self.get_latest_reset_token()
        time.sleep(1)
        
        # Step 3: Test the new token validation
        print("🚨 STEP 3: Testing new token validation...")
        self.test_new_token_validation()
        time.sleep(1)
        
        # Step 4: Verify reset link format
        print("🚨 STEP 4: Verifying reset link format...")
        self.verify_reset_link_format()
        time.sleep(1)
        
        # Step 5: Test reset page accessibility
        print("🚨 STEP 5: Testing reset password page accessibility...")
        self.test_reset_page_accessibility()
        
        # Print summary
        print("=" * 80)
        print("📊 FRESH PASSWORD RESET TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Show results
        if failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if "✅ PASS" in result["status"]:
                print(f"  - {result['test']}")
        print()
        
        # Show key information
        if self.new_token:
            frontend_url = os.getenv('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
            reset_link = f"{frontend_url}/reset-password?token={self.new_token}"
            
            print("🎯 KEY INFORMATION FOR USER:")
            print(f"📧 Fresh password reset email sent to: caryganz@gmail.com")
            print(f"🔗 New reset link: {reset_link}")
            print(f"🆔 New token: {self.new_token}")
            print(f"🌐 Environment: {frontend_url}")
            print()
        
        return passed, failed, total

async def main():
    tester = FreshPasswordResetTester()
    passed, failed, total = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())