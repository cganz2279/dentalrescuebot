#!/usr/bin/env python3
"""
URGENT LOGIN AUTHENTICATION TESTING
Focused test to investigate login authentication issues reported by user
"""

import requests
import json
import sys
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class UrgentAuthTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_database_connectivity(self):
        """Test MongoDB connectivity and check users collection"""
        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            
            # Test connection
            client.admin.command('ping')
            
            # Count users
            user_count = db.users.count_documents({})
            
            # Get all users (without passwords)
            users = list(db.users.find({}, {"_id": 0, "password": 0}))
            
            self.log_test("Database Connectivity", True, 
                        f"Connected to MongoDB. Found {user_count} users in database")
            
            # Log user details for debugging
            print("\n📋 USERS IN DATABASE:")
            for user in users:
                print(f"   Email: {user.get('email', 'N/A')}")
                print(f"   Name: {user.get('firstName', '')} {user.get('lastName', '')}")
                print(f"   Role: {user.get('role', 'N/A')}")
                print(f"   Active: {user.get('isActive', 'N/A')}")
                print(f"   Practice ID: {user.get('practiceId', 'N/A')}")
                print("   ---")
            
            client.close()
            return True
            
        except Exception as e:
            self.log_test("Database Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Backend responding: {data}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_login_cganz2279(self):
        """Test login with cganz2279@gmail.com/password123"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            print(f"\n🔍 LOGIN TEST - cganz2279@gmail.com:")
            print(f"   Request URL: {self.base_url}/auth/login")
            print(f"   Request Data: {login_data}")
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    self.log_test("Login cganz2279@gmail.com", True, 
                                f"SUCCESS: Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    self.log_test("Login cganz2279@gmail.com", False, "Invalid response format")
                    return False
            elif response.status_code == 401:
                self.log_test("Login cganz2279@gmail.com", False, f"401 UNAUTHORIZED: {response.text}")
                return False
            else:
                self.log_test("Login cganz2279@gmail.com", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login cganz2279@gmail.com", False, f"Exception: {str(e)}")
            return False
    
    def test_login_ganzseth(self):
        """Test login with ganzseth@gmail.com/password123"""
        try:
            login_data = {
                "email": "ganzseth@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            print(f"\n🔍 LOGIN TEST - ganzseth@gmail.com:")
            print(f"   Request URL: {self.base_url}/auth/login")
            print(f"   Request Data: {login_data}")
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    self.log_test("Login ganzseth@gmail.com", True, 
                                f"SUCCESS: Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    self.log_test("Login ganzseth@gmail.com", False, "Invalid response format")
                    return False
            elif response.status_code == 401:
                self.log_test("Login ganzseth@gmail.com", False, f"401 UNAUTHORIZED: {response.text}")
                return False
            else:
                self.log_test("Login ganzseth@gmail.com", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login ganzseth@gmail.com", False, f"Exception: {str(e)}")
            return False
    
    def test_password_hash_verification(self):
        """Check password hashes in database"""
        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            
            # Get users with their password hashes
            users = list(db.users.find({}, {"email": 1, "password": 1, "firstName": 1, "lastName": 1, "_id": 0}))
            
            print(f"\n🔐 PASSWORD HASH VERIFICATION:")
            for user in users:
                email = user.get('email', 'N/A')
                password_hash = user.get('password', 'N/A')
                name = f"{user.get('firstName', '')} {user.get('lastName', '')}"
                
                print(f"   User: {name} ({email})")
                print(f"   Hash Length: {len(password_hash) if password_hash != 'N/A' else 'N/A'}")
                print(f"   Hash Starts With: {password_hash[:10] if password_hash != 'N/A' else 'N/A'}...")
                
                # Check if hash looks like bcrypt
                if password_hash.startswith('$2b$') or password_hash.startswith('$2a$'):
                    print(f"   Hash Type: bcrypt ✅")
                else:
                    print(f"   Hash Type: Unknown/Invalid ❌")
                print("   ---")
            
            client.close()
            self.log_test("Password Hash Verification", True, f"Checked {len(users)} user password hashes")
            return True
            
        except Exception as e:
            self.log_test("Password Hash Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_direct_password_verification(self):
        """Test password verification directly using bcrypt"""
        try:
            import bcrypt
            
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            
            # Test cganz2279@gmail.com password
            user = db.users.find_one({"email": "cganz2279@gmail.com"})
            if user:
                stored_hash = user.get('password', '')
                test_password = "password123"
                
                print(f"\n🧪 DIRECT PASSWORD VERIFICATION - cganz2279@gmail.com:")
                print(f"   Stored Hash: {stored_hash}")
                print(f"   Test Password: {test_password}")
                
                try:
                    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
                    print(f"   Verification Result: {is_valid}")
                    
                    if is_valid:
                        self.log_test("Direct Password Verification (cganz2279)", True, "Password matches stored hash")
                    else:
                        self.log_test("Direct Password Verification (cganz2279)", False, "Password does NOT match stored hash")
                        
                except Exception as bcrypt_error:
                    self.log_test("Direct Password Verification (cganz2279)", False, f"Bcrypt error: {str(bcrypt_error)}")
            else:
                self.log_test("Direct Password Verification (cganz2279)", False, "User not found in database")
            
            # Test ganzseth@gmail.com password
            user = db.users.find_one({"email": "ganzseth@gmail.com"})
            if user:
                stored_hash = user.get('password', '')
                test_password = "password123"
                
                print(f"\n🧪 DIRECT PASSWORD VERIFICATION - ganzseth@gmail.com:")
                print(f"   Stored Hash: {stored_hash}")
                print(f"   Test Password: {test_password}")
                
                try:
                    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
                    print(f"   Verification Result: {is_valid}")
                    
                    if is_valid:
                        self.log_test("Direct Password Verification (ganzseth)", True, "Password matches stored hash")
                    else:
                        self.log_test("Direct Password Verification (ganzseth)", False, "Password does NOT match stored hash")
                        
                except Exception as bcrypt_error:
                    self.log_test("Direct Password Verification (ganzseth)", False, f"Bcrypt error: {str(bcrypt_error)}")
            else:
                self.log_test("Direct Password Verification (ganzseth)", False, "User not found in database")
            
            client.close()
            return True
            
        except Exception as e:
            self.log_test("Direct Password Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_endpoint_availability(self):
        """Test if auth endpoints are available"""
        try:
            # Test various auth endpoints
            endpoints = [
                "/auth/login",
                "/auth/forgot-password", 
                "/auth/me"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.options(f"{self.base_url}{endpoint}")
                    print(f"   {endpoint}: Status {response.status_code}")
                except Exception as e:
                    print(f"   {endpoint}: Error - {str(e)}")
            
            self.log_test("Auth Endpoint Availability", True, "Checked auth endpoint availability")
            return True
            
        except Exception as e:
            self.log_test("Auth Endpoint Availability", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚨 URGENT LOGIN AUTHENTICATION TESTING")
        print("=" * 50)
        
        # Run tests in order
        self.test_backend_health()
        self.test_database_connectivity()
        self.test_password_hash_verification()
        self.test_direct_password_verification()
        self.test_auth_endpoint_availability()
        self.test_login_cganz2279()
        self.test_login_ganzseth()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY:")
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed < total:
            print("\n🚨 CRITICAL ISSUES FOUND - See details above")
            return False
        else:
            print("\n✅ ALL TESTS PASSED")
            return True

def main():
    tester = UrgentAuthTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()