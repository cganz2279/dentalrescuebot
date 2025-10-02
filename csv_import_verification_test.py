#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configuration
BASE_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

# MongoDB connection for direct database verification
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

class CSVImportVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.user_id = None
        self.mongo_client = None
        self.db = None
        
    def connect_to_database(self):
        """Connect to MongoDB for direct database verification"""
        try:
            print("🔌 Connecting to MongoDB for direct verification...")
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            
            # Test connection
            self.mongo_client.admin.command('ping')
            print("✅ MongoDB connection successful")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
        
    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with test credentials...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.auth_token = data["token"]
                self.practice_id = data["user"]["practiceId"]
                self.user_id = data["user"]["id"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   Practice ID: {self.practice_id}")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def verify_john_doe_in_database(self):
        """Verify John Doe exists in the users collection with proper fields"""
        print("\n📋 Verifying John Doe in users collection...")
        
        if self.db is None:
            print("❌ Database connection not available")
            return False
        
        try:
            # Search for John Doe by email
            john_doe = self.db.users.find_one({
                "email": "john.doe@email.com",
                "role": "patient"
            })
            
            if not john_doe:
                print("❌ John Doe not found in users collection")
                return False
            
            print("✅ John Doe found in users collection")
            
            # Verify required fields
            required_fields = ["firstName", "lastName", "email", "cellphone", "practiceId"]
            missing_fields = []
            
            for field in required_fields:
                if field not in john_doe or not john_doe[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("✅ All required fields are present")
            
            # Display patient details
            print(f"   First Name: {john_doe.get('firstName')}")
            print(f"   Last Name: {john_doe.get('lastName')}")
            print(f"   Email: {john_doe.get('email')}")
            print(f"   Cellphone: {john_doe.get('cellphone')}")
            print(f"   Practice ID: {john_doe.get('practiceId')}")
            print(f"   Is Active: {john_doe.get('isActive', 'Not set')}")
            print(f"   Created At: {john_doe.get('createdAt', 'Not set')}")
            
            # Verify practice ID matches the authenticated user's practice
            if john_doe.get('practiceId') != self.practice_id:
                print(f"⚠️  John Doe's practice ID ({john_doe.get('practiceId')}) doesn't match authenticated user's practice ID ({self.practice_id})")
                return False
            
            print("✅ John Doe belongs to the correct practice")
            return True
            
        except Exception as e:
            print(f"❌ Database verification error: {e}")
            return False
    
    def test_dashboard_api(self):
        """Test the dashboard API and verify John Doe appears in recentPatients"""
        print("\n🏥 Testing Dashboard API...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code != 200:
            print(f"❌ Dashboard API failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        data = response.json()
        if not data.get("success"):
            print(f"❌ Dashboard API returned error: {data.get('error', 'Unknown error')}")
            return False
        
        print("✅ Dashboard API call successful")
        
        # Check if recentPatients exists
        dashboard_data = data.get("data", {})
        recent_patients = dashboard_data.get("recentPatients", [])
        
        print(f"   Found {len(recent_patients)} recent patients")
        
        # Look for John Doe in recent patients
        john_doe_found = False
        for patient in recent_patients:
            print(f"   Patient: {patient.get('firstName')} {patient.get('lastName')} ({patient.get('email')})")
            
            if (patient.get('firstName', '').lower() == 'john' and 
                patient.get('lastName', '').lower() == 'doe' and
                patient.get('email', '').lower() == 'john.doe@email.com'):
                john_doe_found = True
                print("✅ John Doe found in recent patients!")
                
                # Verify his details in the dashboard response
                print(f"      First Name: {patient.get('firstName')}")
                print(f"      Last Name: {patient.get('lastName')}")
                print(f"      Email: {patient.get('email')}")
                print(f"      Cellphone: {patient.get('cellphone')}")
                print(f"      Status: {patient.get('status')}")
                print(f"      Is Active: {patient.get('isActive')}")
                break
        
        if not john_doe_found:
            print("❌ John Doe NOT found in recent patients array")
            return False
        
        return True
    
    def debug_patient_query(self):
        """Debug the patient query to understand why John Doe might not appear"""
        print("\n🔍 Debugging Patient Query...")
        
        if self.db is None:
            print("❌ Database connection not available")
            return False
        
        try:
            # Check all patients in the practice
            all_patients = list(self.db.users.find({
                "practiceId": self.practice_id,
                "role": "patient"
            }))
            
            print(f"   Total patients in practice: {len(all_patients)}")
            
            # Check active patients
            active_patients = list(self.db.users.find({
                "practiceId": self.practice_id,
                "role": "patient",
                "isActive": True
            }))
            
            print(f"   Active patients in practice: {len(active_patients)}")
            
            # Look specifically for John Doe
            john_doe_variants = [
                {"email": "john.doe@email.com"},
                {"firstName": "John", "lastName": "Doe"},
                {"firstName": {"$regex": "john", "$options": "i"}, "lastName": {"$regex": "doe", "$options": "i"}}
            ]
            
            for i, query in enumerate(john_doe_variants):
                query["practiceId"] = self.practice_id
                query["role"] = "patient"
                
                results = list(self.db.users.find(query))
                print(f"   Query {i+1} ({query}): {len(results)} results")
                
                for result in results:
                    print(f"      Found: {result.get('firstName')} {result.get('lastName')} ({result.get('email')}) - Active: {result.get('isActive')}")
            
            # Check if there are any patients with similar names
            similar_patients = list(self.db.users.find({
                "practiceId": self.practice_id,
                "role": "patient",
                "$or": [
                    {"firstName": {"$regex": "john", "$options": "i"}},
                    {"lastName": {"$regex": "doe", "$options": "i"}},
                    {"email": {"$regex": "john", "$options": "i"}}
                ]
            }))
            
            print(f"   Patients with similar names: {len(similar_patients)}")
            for patient in similar_patients:
                print(f"      {patient.get('firstName')} {patient.get('lastName')} ({patient.get('email')}) - Active: {patient.get('isActive')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Debug query error: {e}")
            return False
    
    def verify_csv_import_success(self):
        """Main verification method that checks all aspects of CSV import"""
        print("\n🎯 Comprehensive CSV Import Verification")
        print("=" * 60)
        
        # Step 1: Database verification
        db_verification = self.verify_john_doe_in_database()
        
        # Step 2: Dashboard API verification
        dashboard_verification = self.test_dashboard_api()
        
        # Step 3: Debug if needed
        if not db_verification or not dashboard_verification:
            print("\n🔍 Running debug analysis...")
            self.debug_patient_query()
        
        return db_verification and dashboard_verification
    
    def run_all_tests(self):
        """Run all CSV import verification tests"""
        print("🚀 Starting CSV Import Verification Tests")
        print("=" * 60)
        
        # Connect to database
        if not self.connect_to_database():
            print("❌ Cannot proceed without database connection")
            return False
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run verification
        success = self.verify_csv_import_success()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CSV IMPORT VERIFICATION SUMMARY")
        print("=" * 60)
        
        if success:
            print("🎉 CSV Import Verification PASSED!")
            print("✅ John Doe was successfully imported and appears in dashboard")
            return True
        else:
            print("❌ CSV Import Verification FAILED!")
            print("⚠️  John Doe was not properly imported or is not appearing in dashboard")
            return False
    
    def cleanup(self):
        """Clean up connections"""
        if self.mongo_client:
            self.mongo_client.close()

def main():
    """Main function to run the tests"""
    tester = CSVImportVerificationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ John Doe CSV import was successful!")
            sys.exit(0)
        else:
            print("\n❌ John Doe CSV import verification failed!")
            sys.exit(1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()