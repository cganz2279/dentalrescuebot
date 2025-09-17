#!/usr/bin/env python3
"""
Edit Functionality Backend Testing Script
Review Request: Test edit button functionality for procedure assignments
- Authentication Test: Verify login with cganz2279@gmail.com/password123
- Procedure Assignment Retrieval: Test GET /api/practice/assignment/{assignment_id}
- Edit Functionality: Test PUT /api/practice/assignment/{assignment_id}
- Dentist List: Test GET /api/practice/doctors for dropdown population
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

class EditFunctionalityTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.practice_id = None
        self.test_results = []
        self.test_assignment_id = None
        
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
                        "Login should work with corrected backend URL"
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
    
    def test_dentist_list(self):
        """Test 2: GET /api/practice/doctors to ensure dentist dropdown will populate"""
        print("👨‍⚕️ Testing Dentist List...")
        
        if not self.jwt_token:
            self.log_test(
                "Dentist List Test",
                False,
                "Cannot test dentist list - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/doctors")
            
            if response.status_code == 200:
                data = response.json()
                doctors_data = data.get("data", []) if data.get("success") else data
                
                if isinstance(doctors_data, list):
                    self.log_test(
                        "Dentist List Test",
                        True,
                        f"Successfully retrieved {len(doctors_data)} dentist(s). Dentists: {[doc.get('name', 'Unknown') for doc in doctors_data]}",
                        "Should return list of dentists for dropdown population"
                    )
                    return True
                else:
                    self.log_test(
                        "Dentist List Test",
                        False,
                        f"Unexpected response format: {type(doctors_data)} - {doctors_data}",
                        "Should return array of dentist objects"
                    )
                    return False
            else:
                self.log_test(
                    "Dentist List Test",
                    False,
                    f"Failed to get dentist list - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with dentist list"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Dentist List Test",
                False,
                f"Dentist list request failed: {str(e)}",
                "Should successfully retrieve dentist list"
            )
            return False
    
    def create_test_assignment(self):
        """Create a test procedure assignment for testing edit functionality"""
        print("📝 Creating Test Procedure Assignment...")
        
        if not self.jwt_token:
            self.log_test(
                "Create Test Assignment",
                False,
                "Cannot create test assignment - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            # First, get available patients
            patients_response = self.session.get(f"{BACKEND_URL}/practice/patients")
            if patients_response.status_code != 200:
                self.log_test(
                    "Create Test Assignment",
                    False,
                    f"Failed to get patients - Status: {patients_response.status_code}",
                    "Need patients to create assignment"
                )
                return False
            
            patients_data = patients_response.json()
            patients = patients_data.get("data", []) if patients_data.get("success") else patients_data
            
            if not patients:
                self.log_test(
                    "Create Test Assignment",
                    False,
                    "No patients available to create assignment",
                    "Need at least one patient"
                )
                return False
            
            # Get available procedures
            procedures_response = self.session.get(f"{BACKEND_URL}/procedures")
            if procedures_response.status_code != 200:
                self.log_test(
                    "Create Test Assignment",
                    False,
                    f"Failed to get procedures - Status: {procedures_response.status_code}",
                    "Need procedures to create assignment"
                )
                return False
            
            procedures_data = procedures_response.json()
            procedures = procedures_data.get("data", []) if procedures_data.get("success") else procedures_data
            
            if not procedures:
                self.log_test(
                    "Create Test Assignment",
                    False,
                    "No procedures available to create assignment",
                    "Need at least one procedure"
                )
                return False
            
            # Create test assignment
            test_assignment = {
                "patientId": patients[0].get("id"),
                "procedureId": procedures[0].get("id"),
                "notes": "Test assignment for edit functionality testing",
                "status": "assigned"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/assign-procedure",
                json=test_assignment,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                assignment_data = data.get("data", {}) if data.get("success") else data
                self.test_assignment_id = assignment_data.get("id")
                
                if self.test_assignment_id:
                    self.log_test(
                        "Create Test Assignment",
                        True,
                        f"Successfully created test assignment with ID: {self.test_assignment_id}",
                        "Should create assignment for testing edit functionality"
                    )
                    return True
                else:
                    self.log_test(
                        "Create Test Assignment",
                        False,
                        f"Assignment created but no ID returned: {assignment_data}",
                        "Should return assignment ID"
                    )
                    return False
            else:
                self.log_test(
                    "Create Test Assignment",
                    False,
                    f"Failed to create assignment - Status: {response.status_code}, Response: {response.text}",
                    "Should create assignment successfully"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Create Test Assignment",
                False,
                f"Create assignment request failed: {str(e)}",
                "Should successfully create test assignment"
            )
            return False
    
    def test_assignment_retrieval(self):
        """Test 3: GET /api/practice/assignment/{assignment_id}"""
        print("📋 Testing Procedure Assignment Retrieval...")
        
        if not self.jwt_token:
            self.log_test(
                "Assignment Retrieval Test",
                False,
                "Cannot test assignment retrieval - no JWT token available",
                "Requires valid authentication"
            )
            return False
        
        if not self.test_assignment_id:
            self.log_test(
                "Assignment Retrieval Test",
                False,
                "Cannot test assignment retrieval - no test assignment ID available",
                "Requires test assignment to be created first"
            )
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/assignment/{self.test_assignment_id}")
            
            if response.status_code == 200:
                data = response.json()
                assignment_data = data.get("data", {}) if data.get("success") else data
                
                if assignment_data.get("id") == self.test_assignment_id:
                    self.log_test(
                        "Assignment Retrieval Test",
                        True,
                        f"Successfully retrieved assignment. ID: {assignment_data.get('id')}, Patient: {assignment_data.get('patientId')}, Procedure: {assignment_data.get('procedureId')}, Status: {assignment_data.get('status')}",
                        "Should retrieve assignment details for editing"
                    )
                    return True
                else:
                    self.log_test(
                        "Assignment Retrieval Test",
                        False,
                        f"Retrieved assignment but ID mismatch. Expected: {self.test_assignment_id}, Got: {assignment_data.get('id')}",
                        "Should return correct assignment"
                    )
                    return False
            else:
                self.log_test(
                    "Assignment Retrieval Test",
                    False,
                    f"Failed to retrieve assignment - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with assignment details"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Assignment Retrieval Test",
                False,
                f"Assignment retrieval request failed: {str(e)}",
                "Should successfully retrieve assignment"
            )
            return False
    
    def test_assignment_update(self):
        """Test 4: PUT /api/practice/assignment/{assignment_id}"""
        print("✏️ Testing Procedure Assignment Update...")
        
        if not self.jwt_token:
            self.log_test(
                "Assignment Update Test",
                False,
                "Cannot test assignment update - no JWT token available",
                "Requires valid authentication"
            )
            return False
        
        if not self.test_assignment_id:
            self.log_test(
                "Assignment Update Test",
                False,
                "Cannot test assignment update - no test assignment ID available",
                "Requires test assignment to be created first"
            )
            return False
            
        try:
            # Update the assignment with new data
            updated_assignment = {
                "notes": "Updated test assignment for edit functionality testing - EDITED",
                "status": "completed"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/practice/assignment/{self.test_assignment_id}",
                json=updated_assignment,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                assignment_data = data.get("data", {}) if data.get("success") else data
                
                # Verify the update was successful
                if (assignment_data.get("notes") == updated_assignment["notes"] and 
                    assignment_data.get("status") == updated_assignment["status"]):
                    self.log_test(
                        "Assignment Update Test",
                        True,
                        f"Successfully updated assignment. New notes: '{assignment_data.get('notes')}', New status: '{assignment_data.get('status')}'",
                        "Should update assignment with new data"
                    )
                    return True
                else:
                    self.log_test(
                        "Assignment Update Test",
                        False,
                        f"Update response received but data not updated correctly. Expected notes: '{updated_assignment['notes']}', Got: '{assignment_data.get('notes')}'. Expected status: '{updated_assignment['status']}', Got: '{assignment_data.get('status')}'",
                        "Should update assignment fields correctly"
                    )
                    return False
            else:
                self.log_test(
                    "Assignment Update Test",
                    False,
                    f"Failed to update assignment - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with updated assignment"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Assignment Update Test",
                False,
                f"Assignment update request failed: {str(e)}",
                "Should successfully update assignment"
            )
            return False
    
    def cleanup_test_assignment(self):
        """Clean up the test assignment"""
        if self.test_assignment_id and self.jwt_token:
            try:
                response = self.session.delete(f"{BACKEND_URL}/practice/assignment/{self.test_assignment_id}")
                if response.status_code in [200, 204]:
                    print(f"🧹 Cleaned up test assignment: {self.test_assignment_id}")
                else:
                    print(f"⚠️ Could not clean up test assignment: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error cleaning up test assignment: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Edit Functionality Backend Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        try:
            # Test 1: Authentication
            auth_success = self.test_authentication()
            
            # Test 2: Dentist List (only if authentication succeeded)
            dentist_success = False
            if auth_success:
                dentist_success = self.test_dentist_list()
            
            # Test 3: Create Test Assignment (only if authentication succeeded)
            create_success = False
            if auth_success:
                create_success = self.create_test_assignment()
            
            # Test 4: Assignment Retrieval (only if test assignment created)
            retrieval_success = False
            if create_success:
                retrieval_success = self.test_assignment_retrieval()
            
            # Test 5: Assignment Update (only if retrieval succeeded)
            update_success = False
            if retrieval_success:
                update_success = self.test_assignment_update()
            
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
            print("🎯 EDIT FUNCTIONALITY ANALYSIS:")
            print(f"✅ Authentication Test: {'PASSED' if auth_success else 'FAILED'}")
            print(f"✅ Dentist List Test: {'PASSED' if dentist_success else 'FAILED'}")
            print(f"✅ Assignment Creation: {'PASSED' if create_success else 'FAILED'}")
            print(f"✅ Assignment Retrieval Test: {'PASSED' if retrieval_success else 'FAILED'}")
            print(f"✅ Assignment Update Test: {'PASSED' if update_success else 'FAILED'}")
            
            if auth_success and dentist_success and retrieval_success and update_success:
                print("\n🎉 ALL CRITICAL TESTS PASSED - Edit functionality backend is working!")
            else:
                print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - see details above")
            
            return passed_tests == total_tests
            
        finally:
            # Always try to clean up
            self.cleanup_test_assignment()

if __name__ == "__main__":
    tester = EditFunctionalityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)