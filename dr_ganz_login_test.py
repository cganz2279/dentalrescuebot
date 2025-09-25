#!/usr/bin/env python3
"""
Backend Test for Dr. Ganz Login Functionality
Testing specific login issue with cganz2279@gmail.com / password123
"""

import asyncio
import aiohttp
import json
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Configuration
BACKEND_URL = "https://postopcare-1.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

class LoginTestSuite:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🔧 Test Setup Complete")
        print(f"   Backend URL: {BACKEND_URL}")
        print(f"   MongoDB URL: {MONGO_URL}")
        print(f"   Database: {DB_NAME}")
        print(f"   Test Email: {TEST_EMAIL}")
        print()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        self.client.close()
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def test_1_user_exists_in_database(self):
        """Test 1: Verify user exists in database"""
        try:
            user = await self.db.users.find_one({"email": TEST_EMAIL.lower()})
            
            if not user:
                self.log_result("User Exists in Database", False, f"User {TEST_EMAIL} not found in database")
                return False
                
            # Check user details
            details = []
            details.append(f"User ID: {user.get('id', 'N/A')}")
            details.append(f"Name: {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
            details.append(f"Role: {user.get('role', 'N/A')}")
            details.append(f"Practice ID: {user.get('practiceId', 'N/A')}")
            details.append(f"Active: {user.get('isActive', 'N/A')}")
            details.append(f"Email Verified: {user.get('isEmailVerified', 'N/A')}")
            
            self.log_result("User Exists in Database", True, " | ".join(details))
            return user
            
        except Exception as e:
            self.log_result("User Exists in Database", False, f"Database error: {str(e)}")
            return False
            
    async def test_2_password_hash_verification(self):
        """Test 2: Verify password hash matches"""
        try:
            user = await self.db.users.find_one({"email": TEST_EMAIL.lower()})
            
            if not user:
                self.log_result("Password Hash Verification", False, "User not found")
                return False
                
            stored_hash = user.get('password')
            if not stored_hash:
                self.log_result("Password Hash Verification", False, "No password hash found in database")
                return False
                
            # Verify password using bcrypt
            password_matches = bcrypt.checkpw(TEST_PASSWORD.encode('utf-8'), stored_hash.encode('utf-8'))
            
            details = f"Password hash verification: {'MATCH' if password_matches else 'NO MATCH'}"
            self.log_result("Password Hash Verification", password_matches, details)
            return password_matches
            
        except Exception as e:
            self.log_result("Password Hash Verification", False, f"Error: {str(e)}")
            return False
            
    async def test_3_practice_association(self):
        """Test 3: Verify user is properly linked to practice"""
        try:
            user = await self.db.users.find_one({"email": TEST_EMAIL.lower()})
            
            if not user:
                self.log_result("Practice Association", False, "User not found")
                return False
                
            practice_id = user.get('practiceId')
            if not practice_id:
                self.log_result("Practice Association", False, "User has no practice ID")
                return False
                
            # Find the practice
            practice = await self.db.practices.find_one({"id": practice_id})
            
            if not practice:
                self.log_result("Practice Association", False, f"Practice {practice_id} not found")
                return False
                
            details = []
            details.append(f"Practice ID: {practice_id}")
            details.append(f"Practice Name: {practice.get('name', 'N/A')}")
            details.append(f"Practice Email: {practice.get('email', 'N/A')}")
            details.append(f"Practice Active: {practice.get('isActive', 'N/A')}")
            
            self.log_result("Practice Association", True, " | ".join(details))
            return practice
            
        except Exception as e:
            self.log_result("Practice Association", False, f"Error: {str(e)}")
            return False
            
    async def test_4_login_api_call(self):
        """Test 4: Test login API endpoint"""
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check response structure
                        success = response_data.get('success', False)
                        user_data = response_data.get('user', {})
                        token = response_data.get('token', '')
                        practice_data = response_data.get('practice', {})
                        
                        details = []
                        details.append(f"Success: {success}")
                        details.append(f"Token present: {'Yes' if token else 'No'}")
                        details.append(f"User ID: {user_data.get('id', 'N/A')}")
                        details.append(f"Practice: {practice_data.get('name', 'N/A') if practice_data else 'None'}")
                        
                        self.log_result("Login API Call", success, " | ".join(details))
                        return response_data if success else False
                        
                    except json.JSONDecodeError:
                        self.log_result("Login API Call", False, f"Invalid JSON response: {response_text}")
                        return False
                        
                else:
                    self.log_result("Login API Call", False, f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Login API Call", False, f"Request error: {str(e)}")
            return False
            
    async def test_5_jwt_token_validation(self):
        """Test 5: Test JWT token generation and validation"""
        try:
            # First get a token from login
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    self.log_result("JWT Token Validation", False, "Login failed, cannot test token")
                    return False
                    
                response_data = await response.json()
                token = response_data.get('token')
                
                if not token:
                    self.log_result("JWT Token Validation", False, "No token returned from login")
                    return False
                    
            # Test the token with /auth/me endpoint
            async with self.session.get(
                f"{BACKEND_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            ) as response:
                
                if response.status == 200:
                    user_data = await response.json()
                    
                    details = []
                    details.append(f"Token valid: Yes")
                    details.append(f"User ID: {user_data.get('user', {}).get('id', 'N/A')}")
                    details.append(f"Email: {user_data.get('user', {}).get('email', 'N/A')}")
                    
                    self.log_result("JWT Token Validation", True, " | ".join(details))
                    return True
                    
                else:
                    response_text = await response.text()
                    self.log_result("JWT Token Validation", False, f"Token validation failed: HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_result("JWT Token Validation", False, f"Error: {str(e)}")
            return False
            
    async def test_6_user_active_status(self):
        """Test 6: Verify user is active and can login"""
        try:
            user = await self.db.users.find_one({"email": TEST_EMAIL.lower()})
            
            if not user:
                self.log_result("User Active Status", False, "User not found")
                return False
                
            is_active = user.get('isActive', False)
            is_email_verified = user.get('isEmailVerified', False)
            
            details = []
            details.append(f"isActive: {is_active}")
            details.append(f"isEmailVerified: {is_email_verified}")
            
            # Check if user should be able to login
            can_login = is_active and is_email_verified
            
            self.log_result("User Active Status", can_login, " | ".join(details))
            return can_login
            
        except Exception as e:
            self.log_result("User Active Status", False, f"Error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all login tests"""
        print("🎯 TESTING DR. GANZ LOGIN FUNCTIONALITY")
        print("=" * 60)
        print()
        
        await self.setup()
        
        # Run tests in sequence
        user_exists = await self.test_1_user_exists_in_database()
        password_valid = await self.test_2_password_hash_verification()
        practice_linked = await self.test_3_practice_association()
        user_active = await self.test_6_user_active_status()
        login_success = await self.test_4_login_api_call()
        token_valid = await self.test_5_jwt_token_validation()
        
        # Summary
        print("=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            
        print()
        print(f"OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Login functionality is working correctly")
        else:
            print("⚠️  SOME TESTS FAILED - Login functionality has issues")
            
        # Identify root cause
        print()
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        if not user_exists:
            print("❌ CRITICAL: User does not exist in database")
        elif not user_active:
            print("❌ CRITICAL: User exists but is not active or email not verified")
        elif not password_valid:
            print("❌ CRITICAL: Password hash does not match")
        elif not practice_linked:
            print("⚠️  WARNING: User exists but practice association has issues")
        elif not login_success:
            print("❌ CRITICAL: Login API call failed")
        elif not token_valid:
            print("❌ CRITICAL: JWT token generation/validation failed")
        else:
            print("✅ All components working correctly")
            
        await self.cleanup()

async def main():
    """Main test runner"""
    test_suite = LoginTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())