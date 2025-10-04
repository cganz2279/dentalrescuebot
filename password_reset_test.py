#!/usr/bin/env python3
"""
Password Reset System Testing for caryganz@gmail.com
Focus: Test the specific issue with "Invalid or expired reset token" errors
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

# Valid token from database (most recent)
VALID_TOKEN = "dbb2e957-4239-43cc-af4c-bbd32a35d5ca"

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
    
    def run_all_tests(self):
        """Run all password reset and username recovery tests"""
        print(f"🔐 Password Reset & Username Recovery Testing")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        tests = [
            self.test_forgot_password_valid_email,
            self.test_forgot_password_invalid_email,
            self.test_forgot_username_valid_practice,
            self.test_forgot_username_invalid_practice,
            self.test_validate_reset_token_valid,
            self.test_validate_reset_token_invalid,
            self.test_reset_password_valid_token,
            self.test_reset_password_invalid_token,
            self.test_reset_password_weak_password
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All password reset tests passed! Authentication system is secure.")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the tests"""
    tester = PasswordResetTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()