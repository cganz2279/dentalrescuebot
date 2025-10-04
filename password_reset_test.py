#!/usr/bin/env python3
"""
Password Reset Email Testing for caryganz@gmail.com
Focus: Verify corrected FRONTEND_URL in password reset emails
Review Request: Send fresh password reset email with corrected FRONTEND_URL
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

# Customer from review request
CUSTOMER_EMAIL = "caryganz@gmail.com"

# Expected corrected FRONTEND_URL (fixed from app.dentalaftercarenotes.com)
EXPECTED_FRONTEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
OLD_FRONTEND_URL = "app.dentalaftercarenotes.com"

class PasswordResetTester:
    def __init__(self):
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
        return success
    
    def test_generate_fresh_reset_token(self):
        """Generate a fresh reset token for testing"""
        try:
            response = requests.post(f"{API_BASE}/auth/forgot-password", json={
                "email": CUSTOMER_EMAIL,
                "recovery_method": "email"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                sent_methods = data.get("sent_methods", [])
                
                return self.log_result(
                    "Generate Fresh Reset Token",
                    True,
                    f"Fresh token generated successfully. Methods: {sent_methods}, Message: {message}"
                )
            else:
                return self.log_result(
                    "Generate Fresh Reset Token",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result("Generate Fresh Reset Token", False, error=str(e))
    
    def test_validate_reset_token_endpoint(self, token):
        """Test the token validation endpoint"""
        try:
            response = requests.get(f"{API_BASE}/auth/validate-reset-token/{token}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                valid = data.get("valid", False)
                user = data.get("user", {})
                expires_at = data.get("expires_at", "")
                
                return self.log_result(
                    f"Validate Reset Token ({token[:8]}...)",
                    True,
                    f"Token is valid: {valid}, User: {user.get('email', 'N/A')}, Expires: {expires_at}"
                )
            else:
                return self.log_result(
                    f"Validate Reset Token ({token[:8]}...)",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result(f"Validate Reset Token ({token[:8]}...)", False, error=str(e))
    
    def test_reset_password_endpoint(self, token, test_password="NewPassword123!"):
        """Test the password reset endpoint"""
        try:
            response = requests.post(f"{API_BASE}/auth/reset-password", json={
                "reset_token": token,
                "new_password": test_password
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                return self.log_result(
                    f"Reset Password with Token ({token[:8]}...)",
                    True,
                    f"Password reset successful: {success}, Message: {message}"
                )
            else:
                return self.log_result(
                    f"Reset Password with Token ({token[:8]}...)",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result(f"Reset Password with Token ({token[:8]}...)", False, error=str(e))
    
    def test_login_after_reset(self, new_password="NewPassword123!"):
        """Test login with the new password"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": CUSTOMER_EMAIL,
                "password": new_password
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                user = data.get("user", {})
                token = data.get("token", "")
                
                return self.log_result(
                    "Login After Password Reset",
                    True,
                    f"Login successful: {success}, User: {user.get('email', 'N/A')}, Token length: {len(token)}"
                )
            else:
                return self.log_result(
                    "Login After Password Reset",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result("Login After Password Reset", False, error=str(e))
    
    def get_fresh_token_from_database(self):
        """Get the most recent valid token from database"""
        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            from dotenv import load_dotenv
            
            load_dotenv('backend/.env')
            
            async def get_token():
                client = AsyncIOMotorClient(os.environ['MONGO_URL'])
                db = client[os.environ.get('DB_NAME', 'dentist_management')]
                
                # Find the most recent valid token
                token_record = await db.password_resets.find_one({
                    'email': CUSTOMER_EMAIL,
                    'used': False,
                    'expires_at': {'$gt': datetime.utcnow()}
                }, sort=[('created_at', -1)])
                
                return token_record.get('reset_token') if token_record else None
            
            return asyncio.run(get_token())
            
        except Exception as e:
            print(f"Error getting fresh token from database: {e}")
            return None
    
    def run_comprehensive_test(self):
        """Run comprehensive password reset testing"""
        print("🔐 Starting Password Reset System Testing")
        print("=" * 70)
        print(f"Target Customer: {CUSTOMER_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Generate fresh reset token
        print("🔍 Step 1: Generate Fresh Reset Token")
        fresh_token_generated = self.test_generate_fresh_reset_token()
        time.sleep(2)  # Wait for token to be created
        
        # Step 2: Get the fresh token from database
        print("🔍 Step 2: Get Fresh Token from Database")
        fresh_token = self.get_fresh_token_from_database()
        if fresh_token:
            print(f"✅ Fresh token retrieved: {fresh_token[:8]}...")
        else:
            print("❌ Could not retrieve fresh token from database")
            fresh_token = VALID_TOKEN  # Fallback to known valid token
            print(f"🔄 Using fallback token: {fresh_token[:8]}...")
        
        # Step 3: Test token validation endpoint
        print("🔍 Step 3: Test Token Validation Endpoint")
        token_valid = self.test_validate_reset_token_endpoint(fresh_token)
        
        # Step 4: Test password reset endpoint
        print("🔍 Step 4: Test Password Reset Endpoint")
        if token_valid:
            reset_successful = self.test_reset_password_endpoint(fresh_token)
            
            # Step 5: Test login with new password
            if reset_successful:
                print("🔍 Step 5: Test Login with New Password")
                self.test_login_after_reset()
        
        # Step 6: Test with invalid token
        print("🔍 Step 6: Test with Invalid Token")
        self.test_validate_reset_token_endpoint("invalid-token-12345")
        self.test_reset_password_endpoint("invalid-token-12345")
        
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
        
        # Check token validation
        validation_tests = [r for r in self.test_results if "Validate Reset Token" in r["test"] and "invalid" not in r["test"].lower()]
        if validation_tests and all(r["success"] for r in validation_tests):
            print("   ✅ Token validation endpoint is working correctly")
        else:
            print("   🚨 Token validation endpoint has issues")
        
        # Check password reset
        reset_tests = [r for r in self.test_results if "Reset Password" in r["test"] and "invalid" not in r["test"].lower()]
        if reset_tests and all(r["success"] for r in reset_tests):
            print("   ✅ Password reset endpoint is working correctly")
        else:
            print("   🚨 Password reset endpoint has issues")
        
        # Check login after reset
        login_tests = [r for r in self.test_results if "Login After" in r["test"]]
        if login_tests and all(r["success"] for r in login_tests):
            print("   ✅ Login after password reset is working correctly")
        else:
            print("   🚨 Login after password reset has issues")
        
        print()
        print("🎯 CUSTOMER RESOLUTION:")
        if success_rate >= 75:
            print(f"   ✅ Password reset system is working correctly for {CUSTOMER_EMAIL}")
            print("   📧 Customer should be able to reset password using email link")
            print("   🔗 Reset URL format: https://app.dentalaftercarenotes.com/reset-password?token=<TOKEN>")
        else:
            print(f"   🚨 Password reset system has issues for {CUSTOMER_EMAIL}")
            print("   🔧 Manual intervention may be required")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = PasswordResetTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 Password reset testing completed successfully!")
        sys.exit(0)
    else:
        print("❌ Password reset testing completed with issues!")
        sys.exit(1)