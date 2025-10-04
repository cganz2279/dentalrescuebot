#!/usr/bin/env python3
"""
URGENT LOGIN INVESTIGATION TEST
Testing login functionality issue reported by user: "Login doesn't work unless you are active"
"""

import requests
import json
import sys
from datetime import datetime
import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class LoginInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_email = TEST_EMAIL
        self.test_password = TEST_PASSWORD
        self.results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {details}")
        
    def test_login_endpoint_direct(self):
        """Test 1: Direct POST to login endpoint"""
        print("\n=== TEST 1: DIRECT LOGIN ENDPOINT TEST ===")
        
        try:
            url = f"{self.backend_url}/api/auth/login"
            payload = {
                "email": self.test_email,
                "password": self.test_password
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            print(f"Making POST request to: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
                
                # Check if login was successful
                if response_data.get("success"):
                    user_data = response_data.get("user", {})
                    token = response_data.get("token")
                    practice = response_data.get("practice")
                    
                    self.log_result(
                        "Direct Login Test", 
                        "✅ PASS", 
                        f"Login successful. User: {user_data.get('firstName')} {user_data.get('lastName')}, Role: {user_data.get('role')}, Active: {user_data.get('isActive')}"
                    )
                    
                    # Store token for further tests
                    self.auth_token = token
                    self.user_data = user_data
                    self.practice_data = practice
                    
                    return True
                else:
                    self.log_result("Direct Login Test", "❌ FAIL", f"Login failed: {response_data}")
                    return False
            else:
                error_text = response.text
                self.log_result("Direct Login Test", "❌ FAIL", f"HTTP {response.status_code}: {error_text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Direct Login Test", "❌ FAIL", f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_result("Direct Login Test", "❌ FAIL", f"Unexpected error: {str(e)}")
            return False
    
    def test_authentication_service_health(self):
        """Test 2: Check authentication service health"""
        print("\n=== TEST 2: AUTHENTICATION SERVICE HEALTH ===")
        
        try:
            # Test basic API health
            url = f"{self.backend_url}/api/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.log_result("API Health Check", "✅ PASS", f"API is responding: {response.json()}")
            else:
                self.log_result("API Health Check", "❌ FAIL", f"API health check failed: {response.status_code}")
                
            # Test auth endpoint availability
            auth_url = f"{self.backend_url}/api/auth/me"
            headers = {"Authorization": f"Bearer invalid_token"}
            response = requests.get(auth_url, headers=headers, timeout=10)
            
            # We expect 401 for invalid token, which means auth service is working
            if response.status_code == 401:
                self.log_result("Auth Service Check", "✅ PASS", "Auth service is responding correctly to invalid tokens")
            else:
                self.log_result("Auth Service Check", "⚠️ WARN", f"Unexpected auth response: {response.status_code}")
                
        except Exception as e:
            self.log_result("Authentication Service Health", "❌ FAIL", f"Service health check failed: {str(e)}")
    
    async def test_user_account_status(self):
        """Test 3: Check user account status in database"""
        print("\n=== TEST 3: USER ACCOUNT STATUS IN DATABASE ===")
        
        try:
            # Connect to MongoDB
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'dentist_management')
            
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client[db_name]
            
            print(f"Connecting to MongoDB: {mongo_url}")
            print(f"Database: {db_name}")
            
            # Find user by email
            user = await db.users.find_one({"email": self.test_email.lower()})
            
            if user:
                user_info = {
                    "id": user.get("id"),
                    "email": user.get("email"),
                    "firstName": user.get("firstName"),
                    "lastName": user.get("lastName"),
                    "role": user.get("role"),
                    "isActive": user.get("isActive"),
                    "isEmailVerified": user.get("isEmailVerified"),
                    "practiceId": user.get("practiceId"),
                    "loginCount": user.get("loginCount", 0),
                    "lastLoginAt": user.get("lastLoginAt"),
                    "createdAt": user.get("createdAt"),
                    "updatedAt": user.get("updatedAt")
                }
                
                print(f"User found in database: {json.dumps(user_info, indent=2, default=str)}")
                
                # Check if user is active
                if user.get("isActive", True):
                    self.log_result("User Account Status", "✅ PASS", f"User account is ACTIVE. Login count: {user.get('loginCount', 0)}")
                else:
                    self.log_result("User Account Status", "❌ FAIL", "User account is INACTIVE")
                
                # Check practice status if applicable
                if user.get("practiceId"):
                    practice = await db.practices.find_one({"id": user["practiceId"]})
                    if practice:
                        practice_info = {
                            "id": practice.get("id"),
                            "name": practice.get("name"),
                            "isActive": practice.get("isActive"),
                            "subscription": practice.get("subscription", {})
                        }
                        print(f"Practice info: {json.dumps(practice_info, indent=2, default=str)}")
                        
                        if practice.get("isActive", True):
                            self.log_result("Practice Status", "✅ PASS", f"Practice '{practice.get('name')}' is ACTIVE")
                        else:
                            self.log_result("Practice Status", "❌ FAIL", f"Practice '{practice.get('name')}' is INACTIVE")
                    else:
                        self.log_result("Practice Status", "❌ FAIL", f"Practice not found for ID: {user['practiceId']}")
                
            else:
                self.log_result("User Account Status", "❌ FAIL", f"User not found in database: {self.test_email}")
            
            client.close()
            
        except Exception as e:
            self.log_result("User Account Status", "❌ FAIL", f"Database check failed: {str(e)}")
    
    def test_session_management(self):
        """Test 4: Test session management and token validation"""
        print("\n=== TEST 4: SESSION MANAGEMENT TEST ===")
        
        if not hasattr(self, 'auth_token'):
            self.log_result("Session Management", "❌ SKIP", "No auth token available from login test")
            return
        
        try:
            # Test token validation
            url = f"{self.backend_url}/api/auth/me"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                self.log_result("Token Validation", "✅ PASS", f"Token is valid. User: {user_info.get('user', {}).get('email')}")
                
                # Test multiple requests with same token
                for i in range(3):
                    test_response = requests.get(url, headers=headers, timeout=10)
                    if test_response.status_code != 200:
                        self.log_result("Session Persistence", "❌ FAIL", f"Token failed on request {i+1}")
                        return
                
                self.log_result("Session Persistence", "✅ PASS", "Token works consistently across multiple requests")
                
            else:
                self.log_result("Token Validation", "❌ FAIL", f"Token validation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Session Management", "❌ FAIL", f"Session test failed: {str(e)}")
    
    def test_login_without_activity(self):
        """Test 5: Test login when no recent activity (simulating user's issue)"""
        print("\n=== TEST 5: LOGIN WITHOUT RECENT ACTIVITY TEST ===")
        
        try:
            # Wait a moment to simulate inactivity
            print("Simulating period of inactivity...")
            import time
            time.sleep(2)
            
            # Try login again
            url = f"{self.backend_url}/api/auth/login"
            payload = {
                "email": self.test_email,
                "password": self.test_password
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    self.log_result("Login After Inactivity", "✅ PASS", "Login successful after period of inactivity")
                else:
                    self.log_result("Login After Inactivity", "❌ FAIL", f"Login failed after inactivity: {response_data}")
            else:
                self.log_result("Login After Inactivity", "❌ FAIL", f"Login failed after inactivity: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Login After Inactivity", "❌ FAIL", f"Inactivity test failed: {str(e)}")
    
    def test_concurrent_login_attempts(self):
        """Test 6: Test multiple concurrent login attempts"""
        print("\n=== TEST 6: CONCURRENT LOGIN ATTEMPTS TEST ===")
        
        try:
            import threading
            import time
            
            results = []
            
            def login_attempt(attempt_num):
                try:
                    url = f"{self.backend_url}/api/auth/login"
                    payload = {
                        "email": self.test_email,
                        "password": self.test_password
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    results.append({
                        "attempt": attempt_num,
                        "status": response.status_code,
                        "success": response.status_code == 200 and response.json().get("success", False)
                    })
                except Exception as e:
                    results.append({
                        "attempt": attempt_num,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Start 3 concurrent login attempts
            threads = []
            for i in range(3):
                thread = threading.Thread(target=login_attempt, args=(i+1,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            successful_logins = sum(1 for r in results if r.get("success", False))
            
            if successful_logins == 3:
                self.log_result("Concurrent Logins", "✅ PASS", f"All {successful_logins}/3 concurrent login attempts successful")
            else:
                self.log_result("Concurrent Logins", "⚠️ WARN", f"Only {successful_logins}/3 concurrent login attempts successful")
                print(f"Concurrent login results: {results}")
                
        except Exception as e:
            self.log_result("Concurrent Logins", "❌ FAIL", f"Concurrent login test failed: {str(e)}")
    
    async def run_investigation(self):
        """Run all investigation tests"""
        print("🔍 STARTING URGENT LOGIN INVESTIGATION")
        print(f"Testing login for: {self.test_email}")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)
        
        # Run tests in sequence
        login_success = self.test_login_endpoint_direct()
        self.test_authentication_service_health()
        await self.test_user_account_status()
        
        if login_success:
            self.test_session_management()
        
        self.test_login_without_activity()
        self.test_concurrent_login_attempts()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate investigation summary"""
        print("\n" + "=" * 60)
        print("🔍 LOGIN INVESTIGATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r["status"])
        failed = sum(1 for r in self.results if "❌ FAIL" in r["status"])
        warnings = sum(1 for r in self.results if "⚠️ WARN" in r["status"])
        skipped = sum(1 for r in self.results if "❌ SKIP" in r["status"])
        
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"⏭️ Skipped: {skipped}")
        print()
        
        # Show all results
        for result in self.results:
            print(f"[{result['status']}] {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        # Determine overall status
        if failed == 0:
            print("🎉 INVESTIGATION RESULT: LOGIN FUNCTIONALITY APPEARS TO BE WORKING")
            print("The user's issue may be related to:")
            print("- Browser cache/cookies")
            print("- Network connectivity issues")
            print("- Frontend JavaScript errors")
            print("- Session timeout on frontend")
        else:
            print("🚨 INVESTIGATION RESULT: LOGIN ISSUES DETECTED")
            print("Critical issues found that need immediate attention:")
            for result in self.results:
                if "❌ FAIL" in result["status"]:
                    print(f"- {result['test']}: {result['details']}")

async def main():
    """Main function to run the investigation"""
    investigator = LoginInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())