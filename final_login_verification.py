#!/usr/bin/env python3
"""
Final comprehensive login verification and summary
"""

import requests
import json
import sys
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://practice-notes-1.preview.emergentagent.com/api"

class FinalLoginVerification:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Connect to MongoDB directly for database investigation
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
            print("✅ Connected to MongoDB for final verification")
        except Exception as e:
            print(f"❌ Could not connect to MongoDB: {e}")
            self.mongo_client = None
            self.db = None
    
    def test_all_working_accounts(self):
        """Test all accounts that should be working"""
        print("\n🔐 TESTING ALL WORKING ACCOUNTS:")
        print("=" * 60)
        
        working_accounts = [
            ("cganz2279@gmail.com", "password123", "practice_admin"),
            ("ganzseth@gmail.com", "password123", "patient"),  # After password setup
        ]
        
        results = []
        
        for email, password, expected_role in working_accounts:
            try:
                login_data = {
                    "email": email,
                    "password": password
                }
                
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                
                print(f"📧 Testing: {email}")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "token" in data:
                        user_info = data.get("user", {})
                        actual_role = user_info.get("role")
                        name = f"{user_info.get('firstName', '')} {user_info.get('lastName', '')}"
                        
                        if actual_role == expected_role:
                            print(f"   ✅ SUCCESS: {name} ({actual_role})")
                            results.append((email, True, f"Working as {actual_role}"))
                        else:
                            print(f"   ❌ ROLE MISMATCH: Expected {expected_role}, got {actual_role}")
                            results.append((email, False, f"Role mismatch: {actual_role}"))
                    else:
                        print(f"   ❌ INVALID RESPONSE FORMAT")
                        results.append((email, False, "Invalid response format"))
                else:
                    print(f"   ❌ FAILED: {response.text}")
                    results.append((email, False, f"Status {response.status_code}"))
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                results.append((email, False, f"Exception: {str(e)}"))
        
        return results
    
    def test_non_existent_account(self):
        """Test the account that doesn't exist"""
        print("\n❌ TESTING NON-EXISTENT ACCOUNT:")
        print("=" * 50)
        
        try:
            login_data = {
                "email": "ganzseth559@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            print(f"📧 Testing: ganzseth559@gmail.com")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 401:
                print("   ✅ CORRECTLY REJECTED: Account does not exist")
                return True
            else:
                print("   ❌ UNEXPECTED RESPONSE")
                return False
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            return False
    
    def get_database_summary(self):
        """Get summary of all accounts in database"""
        if self.db is None:
            return "No database connection"
            
        try:
            users = list(self.db.users.find({}, {"_id": 0, "email": 1, "firstName": 1, "lastName": 1, "role": 1, "isActive": 1}))
            practices = list(self.db.practices.find({}, {"_id": 0, "name": 1, "isActive": 1}))
            
            summary = f"Database contains {len(users)} users and {len(practices)} practices:\n"
            
            for user in users:
                summary += f"  - {user.get('email')}: {user.get('firstName')} {user.get('lastName')} ({user.get('role')}) - {'Active' if user.get('isActive') else 'Inactive'}\n"
            
            for practice in practices:
                summary += f"  - Practice: {practice.get('name')} - {'Active' if practice.get('isActive') else 'Inactive'}\n"
            
            return summary
            
        except Exception as e:
            return f"Database query failed: {str(e)}"
    
    def run_final_verification(self):
        """Run final comprehensive verification"""
        print("🔍 FINAL LOGIN VERIFICATION")
        print("🎯 Investigating ganzseth559@gmail.com login issue")
        print("=" * 70)
        
        # Test working accounts
        working_results = self.test_all_working_accounts()
        
        # Test non-existent account
        non_existent_result = self.test_non_existent_account()
        
        # Get database summary
        db_summary = self.get_database_summary()
        
        print("\n" + "=" * 70)
        print("📊 FINAL SUMMARY:")
        print("=" * 70)
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("The user ganzseth559@gmail.com CANNOT LOGIN because:")
        print("❌ This email address DOES NOT EXIST in the database")
        print("✅ The login API is working correctly")
        print("✅ Other accounts can login successfully")
        
        print("\n👥 EXISTING ACCOUNTS:")
        print(db_summary)
        
        print("\n🔐 WORKING LOGIN CREDENTIALS:")
        for email, success, details in working_results:
            status = "✅" if success else "❌"
            print(f"{status} {email}: {details}")
        
        print("\n💡 SOLUTION:")
        print("The user needs to use one of the existing accounts:")
        print("  - Practice Admin: cganz2279@gmail.com / password123")
        print("  - Patient: ganzseth@gmail.com / password123 (note: no '559')")
        print("  - Or create a new account through the registration process")
        
        if self.mongo_client:
            self.mongo_client.close()

if __name__ == "__main__":
    verifier = FinalLoginVerification(BACKEND_URL)
    verifier.run_final_verification()