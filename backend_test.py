#!/usr/bin/env python3
"""
Backend Testing Script for PDF Generation with Practice Office Hours and Emergency Contact
Review Request: Test authentication, practice settings, and procedure API endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://postop-care.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.practice_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, expected_result=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected_result,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if expected_result:
            print(f"   Expected: {expected_result}")
        print()
        
    def test_authentication(self):
        """Test 1: Authentication with cganz2279@gmail.com/password123"""
        print("🔐 Testing Authentication...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": "cganz2279@gmail.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.jwt_token = data["token"]
                    self.practice_id = data.get("user", {}).get("practiceId")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.jwt_token}"
                    })
                    
                    self.log_test(
                        "Authentication Test",
                        True,
                        f"Successfully authenticated. User: {data.get('user', {}).get('email')}, Role: {data.get('user', {}).get('role')}, Practice: {data.get('user', {}).get('practiceName', 'N/A')}",
                        "Login should work and return JWT token with practice info"
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication Test",
                        False,
                        f"Login successful but no token in response: {data}",
                        "Should return JWT token"
                    )
                    return False
            else:
                self.log_test(
                    "Authentication Test",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}",
                    "Should return 200 with JWT token"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication Test",
                False,
                f"Authentication request failed: {str(e)}",
                "Should successfully connect and authenticate"
            )
            return False
    
    def test_practice_settings(self):
        """Test 2: Verify practice has officeHours and emergencyContact fields"""
        print("🏥 Testing Practice Settings...")
        
        if not self.jwt_token:
            self.log_test(
                "Practice Settings Test",
                False,
                "Cannot test practice settings - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/practice")
            
            if response.status_code == 200:
                data = response.json()
                practice_data = data.get("data", {}) if data.get("success") else data
                
                # Check for officeHours and emergencyContact fields
                office_hours = practice_data.get("officeHours")
                emergency_contact = practice_data.get("emergencyContact")
                
                if office_hours is not None and emergency_contact is not None:
                    self.log_test(
                        "Practice Settings Test",
                        True,
                        f"Practice contains both fields - Office Hours: '{office_hours}', Emergency Contact: '{emergency_contact}'",
                        "Practice should have officeHours and emergencyContact fields"
                    )
                    return True
                else:
                    missing_fields = []
                    if office_hours is None:
                        missing_fields.append("officeHours")
                    if emergency_contact is None:
                        missing_fields.append("emergencyContact")
                    
                    self.log_test(
                        "Practice Settings Test",
                        False,
                        f"Practice missing fields: {missing_fields}. Available fields: {list(practice_data.keys())}",
                        "Practice should have both officeHours and emergencyContact fields"
                    )
                    return False
            else:
                self.log_test(
                    "Practice Settings Test",
                    False,
                    f"Failed to get practice info - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with practice information"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Practice Settings Test",
                False,
                f"Practice settings request failed: {str(e)}",
                "Should successfully retrieve practice information"
            )
            return False
    
    def test_procedure_api(self):
        """Test 3: Test GET /api/procedures/root-canal-therapy for practice information"""
        print("🦷 Testing Procedure API...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                procedure_data = data.get("data", {}) if data.get("success") else data
                
                # Check if procedure includes practice information
                practice_office_hours = procedure_data.get("practiceOfficeHours")
                practice_emergency_contact = procedure_data.get("practiceEmergencyContact")
                
                # According to the review request, the procedure endpoint should NOT include practice info
                if practice_office_hours is None and practice_emergency_contact is None:
                    self.log_test(
                        "Procedure API Test",
                        True,
                        f"Procedure endpoint correctly does NOT include practice info. Available fields: {list(procedure_data.keys())}",
                        "Procedure endpoint should NOT include practice info (frontend adds it)"
                    )
                    return True
                else:
                    self.log_test(
                        "Procedure API Test",
                        False,
                        f"Procedure endpoint unexpectedly includes practice info - practiceOfficeHours: {practice_office_hours}, practiceEmergencyContact: {practice_emergency_contact}",
                        "Procedure endpoint should NOT include practice info"
                    )
                    return False
            else:
                self.log_test(
                    "Procedure API Test",
                    False,
                    f"Failed to get procedure info - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with procedure information"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Procedure API Test",
                False,
                f"Procedure API request failed: {str(e)}",
                "Should successfully retrieve procedure information"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting PDF Generation Backend Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        
        # Test 2: Practice Settings (only if authentication succeeded)
        practice_success = False
        if auth_success:
            practice_success = self.test_practice_settings()
        
        # Test 3: Procedure API (can run independently)
        procedure_success = self.test_procedure_api()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print()
        print("🎯 REVIEW REQUEST ANALYSIS:")
        print(f"✅ Authentication Test: {'PASSED' if auth_success else 'FAILED'}")
        print(f"✅ Practice Settings Test: {'PASSED' if practice_success else 'FAILED'}")  
        print(f"✅ Procedure API Test: {'PASSED' if procedure_success else 'FAILED'}")
        
        if auth_success and practice_success and procedure_success:
            print("\n🎉 ALL TESTS PASSED - PDF generation backend is ready!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - see details above")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)