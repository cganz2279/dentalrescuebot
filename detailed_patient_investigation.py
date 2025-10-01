#!/usr/bin/env python3
"""
Detailed investigation of patient account issues
"""

import requests
import json
import sys
from typing import Dict, Any, List
import pymongo
from pymongo import MongoClient
import os
import bcrypt

# Get backend URL from frontend .env file
BACKEND_URL = "https://dental-portal-debug.preview.emergentagent.com/api"

class DetailedPatientInvestigator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Connect to MongoDB directly for database investigation
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
            print("✅ Connected to MongoDB for detailed investigation")
        except Exception as e:
            print(f"❌ Could not connect to MongoDB: {e}")
            self.mongo_client = None
            self.db = None
    
    def investigate_patient_password_issue(self):
        """Investigate why ganzseth@gmail.com login is failing with 500 error"""
        if self.db is None:
            print("❌ No database connection")
            return
            
        try:
            print("\n🔍 DETAILED PATIENT ACCOUNT INVESTIGATION:")
            print("=" * 60)
            
            # Get the patient account details
            patient = self.db.users.find_one({"email": "ganzseth@gmail.com"})
            
            if not patient:
                print("❌ Patient ganzseth@gmail.com not found")
                return
            
            print(f"📧 Email: {patient.get('email')}")
            print(f"👤 Name: {patient.get('firstName')} {patient.get('lastName')}")
            print(f"🎭 Role: {patient.get('role')}")
            print(f"🟢 Active: {patient.get('isActive')}")
            print(f"🏥 Practice ID: {patient.get('practiceId')}")
            print(f"📅 Created: {patient.get('createdAt')}")
            print(f"📅 Updated: {patient.get('updatedAt')}")
            print(f"🔐 Has Password Field: {'Yes' if 'password' in patient else 'No'}")
            
            if 'password' in patient:
                password_hash = patient['password']
                print(f"🔐 Password Hash Length: {len(password_hash)}")
                print(f"🔐 Password Hash Preview: {password_hash[:20]}...")
                
                # Test if the password hash is valid bcrypt
                try:
                    # Try to verify a test password to see if hash is valid
                    test_result = bcrypt.checkpw(b"test", password_hash.encode('utf-8'))
                    print("🔐 Password Hash Format: Valid bcrypt hash")
                except Exception as e:
                    print(f"🔐 Password Hash Format: Invalid or corrupted - {e}")
            
            print(f"📧 Email Verified: {patient.get('isEmailVerified')}")
            print(f"👥 Invited By: {patient.get('invitedBy')}")
            print(f"📅 Invited At: {patient.get('invitedAt')}")
            print(f"🔢 Login Count: {patient.get('loginCount', 0)}")
            print(f"📅 Last Login: {patient.get('lastLoginAt', 'Never')}")
            
            # Check if practice exists and is active
            practice_id = patient.get('practiceId')
            if practice_id:
                practice = self.db.practices.find_one({"id": practice_id})
                if practice:
                    print(f"\n🏥 PRACTICE DETAILS:")
                    print(f"   Name: {practice.get('name')}")
                    print(f"   Active: {practice.get('isActive')}")
                    print(f"   Subscription Status: {practice.get('subscription', {}).get('status')}")
                else:
                    print(f"\n❌ Practice with ID {practice_id} not found!")
            
        except Exception as e:
            print(f"❌ Investigation failed: {e}")
    
    def test_patient_password_setup(self):
        """Test if patient needs password setup"""
        print(f"\n🔧 TESTING PATIENT PASSWORD SETUP:")
        print("=" * 50)
        
        try:
            # Try to set up password for ganzseth@gmail.com
            setup_data = {
                "email": "ganzseth@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/patient-setup", json=setup_data)
            
            print(f"🔑 Password Setup Request Status: {response.status_code}")
            print(f"🔑 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Password setup successful - patient should now be able to login")
                return True
            else:
                print("❌ Password setup failed")
                return False
                
        except Exception as e:
            print(f"❌ Password setup test failed: {e}")
            return False
    
    def test_patient_login_after_setup(self):
        """Test patient login after password setup"""
        print(f"\n🔐 TESTING PATIENT LOGIN AFTER SETUP:")
        print("=" * 50)
        
        try:
            login_data = {
                "email": "ganzseth@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            print(f"🔑 Login Status: {response.status_code}")
            print(f"🔑 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    print(f"✅ LOGIN SUCCESS! Logged in as {user_info.get('firstName')} {user_info.get('lastName')} ({user_info.get('role')})")
                    return True
            
            print("❌ Login still failing")
            return False
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    def check_all_patient_accounts(self):
        """Check all patient accounts for similar issues"""
        if self.db is None:
            return
            
        try:
            print(f"\n👥 CHECKING ALL PATIENT ACCOUNTS:")
            print("=" * 50)
            
            patients = list(self.db.users.find({"role": "patient"}))
            
            for i, patient in enumerate(patients, 1):
                email = patient.get('email')
                has_password = 'password' in patient and patient['password']
                is_active = patient.get('isActive', False)
                
                print(f"{i}. {email}")
                print(f"   Active: {is_active}")
                print(f"   Has Password: {has_password}")
                
                if has_password:
                    try:
                        # Test if password hash is valid
                        password_hash = patient['password']
                        bcrypt.checkpw(b"test", password_hash.encode('utf-8'))
                        print(f"   Password Hash: Valid")
                    except:
                        print(f"   Password Hash: Invalid/Corrupted")
                
                print()
                
        except Exception as e:
            print(f"❌ Patient accounts check failed: {e}")
    
    def run_detailed_investigation(self):
        """Run detailed investigation"""
        print("🔍 DETAILED PATIENT ACCOUNT INVESTIGATION")
        print("🎯 Focus: ganzseth@gmail.com login issues")
        print("=" * 70)
        
        # 1. Investigate the specific patient account
        self.investigate_patient_password_issue()
        
        # 2. Check all patient accounts for similar issues
        self.check_all_patient_accounts()
        
        # 3. Test patient password setup
        setup_success = self.test_patient_password_setup()
        
        # 4. If setup was successful, test login
        if setup_success:
            self.test_patient_login_after_setup()
        
        if self.mongo_client:
            self.mongo_client.close()

if __name__ == "__main__":
    investigator = DetailedPatientInvestigator(BACKEND_URL)
    investigator.run_detailed_investigation()