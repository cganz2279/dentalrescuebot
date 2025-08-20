#!/usr/bin/env python3
"""
Authentication API Testing for Dental Post-Operative Care App
Focused testing of login credentials and user database state
"""

import requests
import json
import sys
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient

# Get backend URL from frontend .env file
BACKEND_URL = "https://dental-assist-4.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

class AuthTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Connect to MongoDB directly
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            print(f"✅ Connected to MongoDB: {MONGO_URL}/{DB_NAME}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            self.mongo_client = None
            self.db = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def check_database_users(self):
        """Check what users exist in the database"""
        if self.db is None:
            self.log_test("Database User Check", False, "No database connection")
            return False
            
        try:
            users = list(self.db.users.find({}, {"_id": 0, "email": 1, "firstName": 1, "lastName": 1, "role": 1, "isActive": 1, "practiceId": 1}))
            
            print(f"\n📊 Found {len(users)} users in database:")
            for user in users:
                status = "ACTIVE" if user.get("isActive", False) else "INACTIVE"
                print(f"   - {user.get('email', 'NO_EMAIL')} | {user.get('firstName', '')} {user.get('lastName', '')} | Role: {user.get('role', 'NO_ROLE')} | Status: {status}")
            
            # Look specifically for admin@smithdental.com
            admin_user = self.db.users.find_one({"email": "admin@smithdental.com"})
            if admin_user:
                self.log_test("Database User Check", True, f"Found admin@smithdental.com - Active: {admin_user.get('isActive', False)}")
                return True
            else:
                self.log_test("Database User Check", False, "admin@smithdental.com not found in database")
                return False
                
        except Exception as e:
            self.log_test("Database User Check", False, f"Exception: {str(e)}")
            return False
    
    def check_database_practices(self):
        """Check what practices exist in the database"""
        if not self.db:
            self.log_test("Database Practice Check", False, "No database connection")
            return False
            
        try:
            practices = list(self.db.practices.find({}, {"_id": 0, "name": 1, "email": 1, "isActive": 1, "id": 1}))
            
            print(f"\n🏥 Found {len(practices)} practices in database:")
            for practice in practices:
                status = "ACTIVE" if practice.get("isActive", False) else "INACTIVE"
                print(f"   - {practice.get('name', 'NO_NAME')} | {practice.get('email', 'NO_EMAIL')} | Status: {status}")
            
            self.log_test("Database Practice Check", True, f"Found {len(practices)} practices")
            return True
                
        except Exception as e:
            self.log_test("Database Practice Check", False, f"Exception: {str(e)}")
            return False
    
    def test_login_admin_smithdental(self):
        """Test login with admin@smithdental.com / password123"""
        try:
            login_data = {
                "email": "admin@smithdental.com",
                "password": "password123"
            }
            
            print(f"\n🔐 Testing login with admin@smithdental.com / password123")
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response Data: {json.dumps(data, indent=2, default=str)}")
                
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    practice_info = data.get("practice", {})
                    self.log_test("Login admin@smithdental.com", True, 
                                f"SUCCESS - Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')}) from {practice_info.get('name', 'Unknown Practice')}")
                    return True
                else:
                    self.log_test("Login admin@smithdental.com", False, "Invalid response format - missing success or token")
                    return False
            else:
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    self.log_test("Login admin@smithdental.com", False, f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw Response: {response.text}")
                    self.log_test("Login admin@smithdental.com", False, f"Status: {response.status_code}, Raw Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login admin@smithdental.com", False, f"Exception: {str(e)}")
            return False
    
    def test_login_variations(self):
        """Test login with different credential variations"""
        test_credentials = [
            ("admin@smithdental.com", "password123"),
            ("admin@smithdental.com", "Password123"),
            ("admin@smithdental.com", "password"),
            ("Admin@smithdental.com", "password123"),
            ("admin@smithdental.com", "123password"),
        ]
        
        results = []
        for email, password in test_credentials:
            try:
                login_data = {"email": email, "password": password}
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        results.append(f"✅ {email} / {password} - SUCCESS")
                    else:
                        results.append(f"❌ {email} / {password} - Failed (success=false)")
                else:
                    try:
                        error_data = response.json()
                        results.append(f"❌ {email} / {password} - {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                    except:
                        results.append(f"❌ {email} / {password} - {response.status_code}: {response.text}")
                        
            except Exception as e:
                results.append(f"❌ {email} / {password} - Exception: {str(e)}")
        
        print(f"\n🔍 Login Credential Variations Test:")
        for result in results:
            print(f"   {result}")
        
        # Check if any succeeded
        success_count = sum(1 for r in results if "SUCCESS" in r)
        self.log_test("Login Credential Variations", success_count > 0, f"{success_count} out of {len(test_credentials)} credential combinations worked")
        return success_count > 0
    
    def test_other_potential_users(self):
        """Test login with other potential users from database"""
        if not self.db:
            self.log_test("Test Other Users", False, "No database connection")
            return False
            
        try:
            # Get all users with email and check if any have obvious passwords
            users = list(self.db.users.find({"isActive": True}, {"email": 1, "firstName": 1, "lastName": 1, "role": 1}))
            
            test_passwords = ["password123", "password", "123456", "admin", "test"]
            successful_logins = []
            
            for user in users:
                email = user.get("email")
                if not email:
                    continue
                    
                for password in test_passwords:
                    try:
                        login_data = {"email": email, "password": password}
                        response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                user_info = data.get("user", {})
                                successful_logins.append(f"{email} / {password} - {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                                break  # Found working password for this user
                    except:
                        continue
            
            if successful_logins:
                print(f"\n✅ Found {len(successful_logins)} working login credentials:")
                for login in successful_logins:
                    print(f"   - {login}")
                self.log_test("Test Other Users", True, f"Found {len(successful_logins)} working credentials")
                return True
            else:
                self.log_test("Test Other Users", False, "No working credentials found for any users")
                return False
                
        except Exception as e:
            self.log_test("Test Other Users", False, f"Exception: {str(e)}")
            return False
    
    def test_api_health(self):
        """Test if the API is responding"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("API Health Check", True, f"API responding: {data}")
                    return True
                else:
                    self.log_test("API Health Check", False, "API responding but missing message")
                    return False
            else:
                self.log_test("API Health Check", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")
            return False
    
    def run_authentication_tests(self):
        """Run all authentication-focused tests"""
        print(f"🔐 Authentication API Testing for Dental Post-Operative Care App")
        print(f"🔗 Testing against: {self.base_url}")
        print(f"🗄️  Database: {MONGO_URL}/{DB_NAME}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_api_health,
            self.check_database_users,
            self.check_database_practices,
            self.test_login_admin_smithdental,
            self.test_login_variations,
            self.test_other_potential_users,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        print("\n" + "=" * 80)
        print(f"📊 AUTHENTICATION TEST SUMMARY")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {total - passed}")
        print(f"   Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All authentication tests passed!")
        else:
            print("⚠️  Some authentication tests failed - check details above")
        
        return passed == total

def main():
    """Main function"""
    tester = AuthTester(BACKEND_URL)
    success = tester.run_authentication_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()