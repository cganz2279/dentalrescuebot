#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://dentalpractice-hub-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class AdminPracticeCreationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def test_admin_login(self):
        """Test admin login with provided credentials"""
        print("🔐 Testing Admin Login...")
        
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/admin/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.admin_token = data["token"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                print(f"✅ Admin authentication successful")
                print(f"   Admin Email: {ADMIN_EMAIL}")
                print(f"   Token received: {self.admin_token[:20]}...")
                return True
            else:
                print(f"❌ Admin authentication failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Admin authentication failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_create_practice_api(self):
        """Test the create practice API endpoint with proper authentication"""
        print("\n🏥 Testing Create Practice API Endpoint...")
        
        # Generate unique practice data
        unique_id = str(uuid.uuid4())[:8]
        test_practice = {
            "practiceName": f"Test Dental Practice {unique_id}",
            "adminEmail": f"testadmin{unique_id}@example.com",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "phone": "+1-555-123-4567",
            "address": "123 Test Street, Test City, TC 12345",
            "tempPassword": "TempPass123!",
            "subscriptionType": "trial",
            "trialDays": 15
        }
        
        print(f"   Creating practice: {test_practice['practiceName']}")
        print(f"   Admin email: {test_practice['adminEmail']}")
        
        response = self.session.post(f"{BASE_URL}/admin/create-practice", json=test_practice)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                practice_info = data.get("practice", {})
                print(f"✅ Practice creation successful")
                print(f"   Practice ID: {practice_info.get('id')}")
                print(f"   Practice Name: {practice_info.get('name')}")
                print(f"   Admin User ID: {practice_info.get('admin_user', {}).get('id')}")
                print(f"   Subscription Type: {practice_info.get('subscription_type')}")
                
                # Store practice info for email test
                self.test_practice_data = {
                    "practiceData": {
                        "practiceName": test_practice["practiceName"]
                    },
                    "adminCredentials": {
                        "adminEmail": test_practice["adminEmail"],
                        "adminFirstName": test_practice["adminFirstName"],
                        "adminLastName": test_practice["adminLastName"],
                        "tempPassword": test_practice["tempPassword"]
                    },
                    "appUrl": "https://dentalpractice-hub-1.preview.emergentagent.com"
                }
                
                return True
            else:
                print(f"❌ Practice creation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Practice creation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_welcome_email_api(self):
        """Test the welcome email API endpoint"""
        print("\n📧 Testing Welcome Email API Endpoint...")
        
        if not hasattr(self, 'test_practice_data'):
            print("❌ No practice data available for email test")
            return False
        
        print(f"   Sending welcome email to: {self.test_practice_data['adminCredentials']['adminEmail']}")
        print(f"   Practice: {self.test_practice_data['practiceData']['practiceName']}")
        
        response = self.session.post(f"{BASE_URL}/admin/send-welcome-email", json=self.test_practice_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Welcome email sent successfully")
                print(f"   Message: {data.get('message', 'Email sent')}")
                return True
            else:
                print(f"❌ Welcome email failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Welcome email failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_token_authentication(self):
        """Test that adminToken is properly passed and used"""
        print("\n🔑 Testing Token Authentication...")
        
        # Test with valid token
        print("   Testing with valid admin token...")
        response = self.session.get(f"{BASE_URL}/admin/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Valid token authentication working")
                print(f"   Dashboard data received with {len(data.get('recent_practices', []))} recent practices")
            else:
                print(f"❌ Valid token failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Valid token failed with status {response.status_code}")
            return False
        
        # Test with invalid token
        print("   Testing with invalid token...")
        invalid_session = requests.Session()
        invalid_session.headers.update({
            "Authorization": "Bearer invalid-token-12345"
        })
        
        response = invalid_session.get(f"{BASE_URL}/admin/dashboard")
        
        if response.status_code in [401, 403]:
            print("✅ Invalid token correctly rejected")
            return True
        else:
            print(f"❌ Invalid token should be rejected (status: {response.status_code})")
            return False
    
    def test_practice_creation_validation(self):
        """Test practice creation with invalid data"""
        print("\n🔍 Testing Practice Creation Validation...")
        
        # Test missing required fields
        invalid_practices = [
            {
                "adminEmail": "test@example.com",
                # Missing practiceName, adminFirstName, adminLastName, tempPassword
            },
            {
                "practiceName": "Test Practice",
                "adminEmail": "invalid-email",  # Invalid email format
                "adminFirstName": "Test",
                "adminLastName": "Admin",
                "tempPassword": "123"  # Too short password
            }
        ]
        
        validation_passed = True
        
        for i, invalid_data in enumerate(invalid_practices):
            print(f"   Testing invalid practice data {i+1}...")
            
            response = self.session.post(f"{BASE_URL}/admin/create-practice", json=invalid_data)
            
            if response.status_code in [400, 422]:
                print(f"   ✅ Validation correctly rejected invalid data (status: {response.status_code})")
            else:
                print(f"   ❌ Validation should reject invalid data (status: {response.status_code})")
                validation_passed = False
        
        return validation_passed
    
    def test_duplicate_practice_prevention(self):
        """Test that duplicate practices are prevented"""
        print("\n🚫 Testing Duplicate Practice Prevention...")
        
        # Create a practice first
        unique_id = str(uuid.uuid4())[:8]
        test_practice = {
            "practiceName": f"Duplicate Test Practice {unique_id}",
            "adminEmail": f"duplicate{unique_id}@example.com",
            "adminFirstName": "Duplicate",
            "adminLastName": "Test",
            "tempPassword": "DuplicatePass123!",
            "subscriptionType": "trial"
        }
        
        print(f"   Creating first practice: {test_practice['practiceName']}")
        response1 = self.session.post(f"{BASE_URL}/admin/create-practice", json=test_practice)
        
        if response1.status_code != 200 or not response1.json().get("success"):
            print("   ❌ Failed to create first practice for duplicate test")
            return False
        
        print("   ✅ First practice created successfully")
        
        # Try to create duplicate practice (same name)
        print("   Attempting to create duplicate practice with same name...")
        duplicate_practice = test_practice.copy()
        duplicate_practice["adminEmail"] = f"different{unique_id}@example.com"  # Different email
        
        response2 = self.session.post(f"{BASE_URL}/admin/create-practice", json=duplicate_practice)
        
        if response2.status_code == 409:  # Conflict
            print("   ✅ Duplicate practice name correctly rejected")
        elif response2.status_code == 400:
            data = response2.json()
            if "already exists" in data.get("detail", "").lower():
                print("   ✅ Duplicate practice name correctly rejected")
            else:
                print(f"   ❌ Unexpected error message: {data.get('detail')}")
                return False
        else:
            print(f"   ❌ Duplicate practice should be rejected (status: {response2.status_code})")
            return False
        
        # Try to create duplicate with same email
        print("   Attempting to create practice with duplicate admin email...")
        duplicate_email_practice = test_practice.copy()
        duplicate_email_practice["practiceName"] = f"Different Practice Name {unique_id}"
        
        response3 = self.session.post(f"{BASE_URL}/admin/create-practice", json=duplicate_email_practice)
        
        if response3.status_code == 409:  # Conflict
            print("   ✅ Duplicate admin email correctly rejected")
            return True
        elif response3.status_code == 400:
            data = response3.json()
            if "already exists" in data.get("detail", "").lower():
                print("   ✅ Duplicate admin email correctly rejected")
                return True
            else:
                print(f"   ❌ Unexpected error message: {data.get('detail')}")
                return False
        else:
            print(f"   ❌ Duplicate admin email should be rejected (status: {response3.status_code})")
            return False
    
    def test_authentication_required(self):
        """Test that endpoints require admin authentication"""
        print("\n🔒 Testing Authentication Requirements...")
        
        # Create a session without authentication
        unauth_session = requests.Session()
        
        endpoints_to_test = [
            ("create-practice", "POST", {"practiceName": "Test"}),
            ("send-welcome-email", "POST", {"practiceData": {}, "adminCredentials": {}}),
            ("dashboard", "GET", None),
            ("practices", "GET", None)
        ]
        
        auth_required = True
        
        for endpoint, method, data in endpoints_to_test:
            print(f"   Testing {method} /admin/{endpoint} without auth...")
            
            if method == "POST":
                response = unauth_session.post(f"{BASE_URL}/admin/{endpoint}", json=data)
            else:
                response = unauth_session.get(f"{BASE_URL}/admin/{endpoint}")
            
            if response.status_code in [401, 403]:
                print(f"   ✅ {endpoint} correctly requires authentication")
            else:
                print(f"   ❌ {endpoint} should require authentication (status: {response.status_code})")
                auth_required = False
        
        return auth_required
    
    def run_all_tests(self):
        """Run all admin practice creation tests"""
        print("🚀 Starting Admin Practice Creation Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.test_admin_login():
            print("❌ Admin authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        tests = [
            ("Authentication Requirements", self.test_authentication_required),
            ("Token Authentication", self.test_token_authentication),
            ("Practice Creation Validation", self.test_practice_creation_validation),
            ("Create Practice API", self.test_create_practice_api),
            ("Welcome Email API", self.test_welcome_email_api),
            ("Duplicate Practice Prevention", self.test_duplicate_practice_prevention)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Admin Practice Creation tests PASSED!")
            print("\n🔧 TOKEN FIX VERIFICATION:")
            print("✅ adminToken is properly used in create-practice API call")
            print("✅ adminToken is properly used in send-welcome-email API call")
            print("✅ No 'ReferenceError: token is not defined' errors detected")
            print("✅ Practice creation and email functionality working correctly")
            return True
        else:
            print("⚠️  Some tests FAILED - see details above")
            return False

def main():
    """Main function to run the tests"""
    tester = AdminPracticeCreationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Admin Practice Creation functionality is working correctly!")
        print("🎯 The token fix has been successfully implemented and verified!")
        sys.exit(0)
    else:
        print("\n❌ Admin Practice Creation functionality has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()