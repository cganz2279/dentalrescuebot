#!/usr/bin/env python3
"""
URGENT LOGIN INVESTIGATION
Investigating login issue for ganzseth559@gmail.com as requested in review
"""

import requests
import json
import sys
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"

class UrgentLoginInvestigator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Connect to MongoDB directly for database investigation
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
            print("✅ Connected to MongoDB for database investigation")
        except Exception as e:
            print(f"❌ Could not connect to MongoDB: {e}")
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
    
    def investigate_database_accounts(self):
        """Check what accounts exist in the database"""
        if self.db is None:
            self.log_test("Database Account Investigation", False, "No database connection")
            return False
            
        try:
            print("\n🔍 INVESTIGATING DATABASE ACCOUNTS:")
            print("=" * 50)
            
            # Check users collection
            users = list(self.db.users.find({}, {"_id": 0, "email": 1, "firstName": 1, "lastName": 1, "role": 1, "isActive": 1, "practiceId": 1}))
            
            print(f"📊 TOTAL USERS FOUND: {len(users)}")
            print("\n👥 ALL USERS IN DATABASE:")
            
            target_emails = []
            ganz_seth_accounts = []
            practice_admins = []
            
            for i, user in enumerate(users, 1):
                email = user.get("email", "")
                firstName = user.get("firstName", "")
                lastName = user.get("lastName", "")
                role = user.get("role", "")
                isActive = user.get("isActive", False)
                practiceId = user.get("practiceId", "")
                
                print(f"{i}. Email: {email}")
                print(f"   Name: {firstName} {lastName}")
                print(f"   Role: {role}")
                print(f"   Active: {isActive}")
                print(f"   Practice ID: {practiceId}")
                print()
                
                # Check for target emails
                if email == "ganzseth559@gmail.com":
                    target_emails.append(("ganzseth559@gmail.com", user))
                elif email == "ganzseth@gmail.com":
                    target_emails.append(("ganzseth@gmail.com", user))
                
                # Check for accounts with "ganz" or "seth"
                if "ganz" in email.lower() or "seth" in email.lower():
                    ganz_seth_accounts.append(user)
                
                # Check for practice admins
                if role == "practice_admin":
                    practice_admins.append(user)
            
            print("\n🎯 TARGET EMAIL INVESTIGATION:")
            print("=" * 40)
            if target_emails:
                for email, user in target_emails:
                    print(f"✅ FOUND: {email}")
                    print(f"   Status: {'Active' if user.get('isActive') else 'Inactive'}")
                    print(f"   Role: {user.get('role')}")
                    print(f"   Practice ID: {user.get('practiceId')}")
            else:
                print("❌ ganzseth559@gmail.com NOT FOUND")
                print("❌ ganzseth@gmail.com NOT FOUND")
            
            print("\n🔍 ACCOUNTS WITH 'GANZ' OR 'SETH':")
            print("=" * 40)
            if ganz_seth_accounts:
                for user in ganz_seth_accounts:
                    print(f"📧 {user.get('email')}")
                    print(f"   Name: {user.get('firstName')} {user.get('lastName')}")
                    print(f"   Role: {user.get('role')}")
                    print(f"   Active: {user.get('isActive')}")
                    print()
            else:
                print("❌ No accounts found with 'ganz' or 'seth' in email")
            
            print("\n👨‍💼 ALL PRACTICE ADMIN ACCOUNTS:")
            print("=" * 40)
            if practice_admins:
                for user in practice_admins:
                    print(f"📧 {user.get('email')}")
                    print(f"   Name: {user.get('firstName')} {user.get('lastName')}")
                    print(f"   Active: {user.get('isActive')}")
                    print(f"   Practice ID: {user.get('practiceId')}")
                    print()
            else:
                print("❌ No practice admin accounts found")
            
            # Check practices collection
            practices = list(self.db.practices.find({}, {"_id": 0, "name": 1, "isActive": 1, "id": 1}))
            print(f"\n🏥 PRACTICES IN DATABASE ({len(practices)} total):")
            print("=" * 40)
            for practice in practices:
                print(f"🏥 {practice.get('name')}")
                print(f"   ID: {practice.get('id')}")
                print(f"   Active: {practice.get('isActive')}")
                print()
            
            self.log_test("Database Account Investigation", True, 
                        f"Found {len(users)} users, {len(practice_admins)} practice admins, {len(ganz_seth_accounts)} ganz/seth accounts")
            return True
            
        except Exception as e:
            self.log_test("Database Account Investigation", False, f"Exception: {str(e)}")
            return False
    
    def test_login_api_basic(self):
        """Test if the basic login API endpoint is working at all"""
        try:
            # Test with a known working account from test_result.md
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    self.log_test("Basic Login API Test", True, 
                                f"Login API working - logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    self.log_test("Basic Login API Test", False, "Invalid response format")
                    return False
            else:
                self.log_test("Basic Login API Test", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Basic Login API Test", False, f"Exception: {str(e)}")
            return False
    
    def test_target_email_login(self):
        """Test login with ganzseth559@gmail.com and common passwords"""
        target_email = "ganzseth559@gmail.com"
        common_passwords = ["password123", "password", "Dentist1#"]
        
        print(f"\n🔐 TESTING LOGIN FOR: {target_email}")
        print("=" * 50)
        
        for password in common_passwords:
            try:
                login_data = {
                    "email": target_email,
                    "password": password
                }
                
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                
                print(f"🔑 Testing password: {password}")
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "token" in data:
                        user_info = data.get("user", {})
                        self.log_test(f"Login Test ({target_email} / {password})", True, 
                                    f"SUCCESS! Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                        return True
                    else:
                        print(f"   Response: {response.text}")
                        self.log_test(f"Login Test ({target_email} / {password})", False, "Invalid response format")
                else:
                    print(f"   Response: {response.text}")
                    self.log_test(f"Login Test ({target_email} / {password})", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Login Test ({target_email} / {password})", False, f"Exception: {str(e)}")
        
        return False
    
    def test_alternative_ganz_emails(self):
        """Test login with alternative ganz emails found in database"""
        if self.db is None:
            return False
            
        try:
            # Find all emails with 'ganz' in them
            ganz_users = list(self.db.users.find(
                {"email": {"$regex": "ganz", "$options": "i"}}, 
                {"email": 1, "firstName": 1, "lastName": 1, "role": 1, "isActive": 1}
            ))
            
            if not ganz_users:
                self.log_test("Alternative Ganz Email Login Test", False, "No ganz emails found in database")
                return False
            
            print(f"\n🔍 TESTING ALTERNATIVE GANZ EMAILS:")
            print("=" * 50)
            
            common_passwords = ["password123", "password", "Dentist1#"]
            
            for user in ganz_users:
                email = user.get("email")
                is_active = user.get("isActive", False)
                
                print(f"\n📧 Testing: {email}")
                print(f"   Active: {is_active}")
                print(f"   Role: {user.get('role')}")
                
                if not is_active:
                    print("   ⚠️  Account is INACTIVE - login may fail")
                
                for password in common_passwords:
                    try:
                        login_data = {
                            "email": email,
                            "password": password
                        }
                        
                        response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                        
                        print(f"   🔑 Password: {password} -> Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success") and "token" in data:
                                user_info = data.get("user", {})
                                self.log_test(f"Alternative Login ({email} / {password})", True, 
                                            f"SUCCESS! Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                                return True
                        
                    except Exception as e:
                        print(f"   ❌ Exception: {str(e)}")
            
            self.log_test("Alternative Ganz Email Login Test", False, "No successful logins with ganz emails")
            return False
            
        except Exception as e:
            self.log_test("Alternative Ganz Email Login Test", False, f"Exception: {str(e)}")
            return False
    
    def check_account_status(self):
        """Check if ganzseth559@gmail.com exists but is inactive/disabled"""
        if self.db is None:
            return False
            
        try:
            target_email = "ganzseth559@gmail.com"
            user = self.db.users.find_one({"email": target_email})
            
            if user:
                print(f"\n📋 ACCOUNT STATUS FOR {target_email}:")
                print("=" * 50)
                print(f"✅ Account EXISTS in database")
                print(f"📧 Email: {user.get('email')}")
                print(f"👤 Name: {user.get('firstName')} {user.get('lastName')}")
                print(f"🎭 Role: {user.get('role')}")
                print(f"🟢 Active: {user.get('isActive', False)}")
                print(f"🏥 Practice ID: {user.get('practiceId')}")
                print(f"📅 Created: {user.get('createdAt')}")
                print(f"🔐 Has Password: {'Yes' if user.get('password') else 'No'}")
                
                if not user.get('isActive', False):
                    self.log_test("Account Status Check", True, 
                                f"Account EXISTS but is INACTIVE - this explains login failure")
                else:
                    self.log_test("Account Status Check", True, 
                                f"Account EXISTS and is ACTIVE - login should work")
                return True
            else:
                print(f"\n❌ ACCOUNT STATUS FOR {target_email}:")
                print("=" * 50)
                print(f"❌ Account DOES NOT EXIST in database")
                self.log_test("Account Status Check", True, 
                            f"Account DOES NOT EXIST - this explains login failure")
                return True
                
        except Exception as e:
            self.log_test("Account Status Check", False, f"Exception: {str(e)}")
            return False
    
    def run_urgent_investigation(self):
        """Run urgent login investigation as requested"""
        print("🚨 URGENT LOGIN INVESTIGATION")
        print("🎯 Target: ganzseth559@gmail.com")
        print("📋 User reports: 'nothing works'")
        print("=" * 70)
        
        # 1. Check what accounts exist in the database
        print("\n1️⃣ CHECKING DATABASE ACCOUNTS...")
        self.investigate_database_accounts()
        
        # 2. Check if target account exists but is inactive
        print("\n2️⃣ CHECKING TARGET ACCOUNT STATUS...")
        self.check_account_status()
        
        # 3. Test basic login API functionality
        print("\n3️⃣ TESTING BASIC LOGIN API...")
        self.test_login_api_basic()
        
        # 4. Test login with target email and common passwords
        print("\n4️⃣ TESTING TARGET EMAIL LOGIN...")
        self.test_target_email_login()
        
        # 5. Test alternative ganz emails
        print("\n5️⃣ TESTING ALTERNATIVE GANZ EMAILS...")
        self.test_alternative_ganz_emails()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 INVESTIGATION SUMMARY:")
        print("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        if self.mongo_client:
            self.mongo_client.close()

if __name__ == "__main__":
    investigator = UrgentLoginInvestigator(BACKEND_URL)
    investigator.run_urgent_investigation()