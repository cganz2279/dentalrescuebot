#!/usr/bin/env python3
"""
Backend Testing Script for POST-based Patient Delete Endpoint
Review Request: Test new POST /api/practice/patients/{patient_id}/delete endpoint with soft/hard delete functionality
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.practice_id = None
        self.test_results = []
        self.test_patient_id = None
        self.test_patient_id_2 = None
        
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
    
    def create_test_patients(self):
        """Create test patients for delete testing"""
        print("👥 Creating Test Patients...")
        
        if not self.jwt_token:
            self.log_test(
                "Create Test Patients",
                False,
                "Cannot create test patients - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            # Create first test patient
            patient_data_1 = {
                "email": f"test.patient.1.{datetime.now().timestamp()}@example.com",
                "firstName": "Test",
                "lastName": "Patient One",
                "phone": "555-0001"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/patients",
                json=patient_data_1,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data", {}).get("id"):
                    self.test_patient_id = data["data"]["id"]
                    
                    # Create second test patient
                    patient_data_2 = {
                        "email": f"test.patient.2.{datetime.now().timestamp()}@example.com",
                        "firstName": "Test",
                        "lastName": "Patient Two",
                        "phone": "555-0002"
                    }
                    
                    response_2 = self.session.post(
                        f"{BACKEND_URL}/practice/patients",
                        json=patient_data_2,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response_2.status_code == 200:
                        data_2 = response_2.json()
                        if data_2.get("success") and data_2.get("data", {}).get("id"):
                            self.test_patient_id_2 = data_2["data"]["id"]
                            
                            self.log_test(
                                "Create Test Patients",
                                True,
                                f"Successfully created 2 test patients: {self.test_patient_id} and {self.test_patient_id_2}",
                                "Should create test patients for delete testing"
                            )
                            return True
                        else:
                            self.log_test(
                                "Create Test Patients",
                                False,
                                f"Failed to create second test patient: {data_2}",
                                "Should create second test patient"
                            )
                            return False
                    else:
                        self.log_test(
                            "Create Test Patients",
                            False,
                            f"Failed to create second test patient - Status: {response_2.status_code}, Response: {response_2.text}",
                            "Should return 200 with patient data"
                        )
                        return False
                else:
                    self.log_test(
                        "Create Test Patients",
                        False,
                        f"Failed to create first test patient: {data}",
                        "Should create first test patient"
                    )
                    return False
            else:
                self.log_test(
                    "Create Test Patients",
                    False,
                    f"Failed to create first test patient - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with patient data"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Create Test Patients",
                False,
                f"Create test patients request failed: {str(e)}",
                "Should successfully create test patients"
            )
            return False
    
    def test_post_soft_delete(self):
        """Test 2: POST /api/practice/patients/{patient_id}/delete with hard_delete=false"""
        print("🗑️ Testing POST Soft Delete...")
        
        if not self.jwt_token or not self.test_patient_id:
            self.log_test(
                "POST Soft Delete Test",
                False,
                "Cannot test soft delete - no JWT token or test patient available",
                "Requires valid authentication and test patient"
            )
            return False
            
        try:
            response = self.session.post(
                f"{BACKEND_URL}/practice/patients/{self.test_patient_id}/delete",
                json={"hard_delete": False},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    message = data.get("message", "")
                    if "deactivated" in message.lower():
                        self.log_test(
                            "POST Soft Delete Test",
                            True,
                            f"Successfully soft deleted patient. Message: {message}",
                            "Should deactivate patient with hard_delete=false"
                        )
                        return True
                    else:
                        self.log_test(
                            "POST Soft Delete Test",
                            False,
                            f"Unexpected response message: {message}",
                            "Should contain 'deactivated' in message"
                        )
                        return False
                else:
                    self.log_test(
                        "POST Soft Delete Test",
                        False,
                        f"API returned success=false: {data}",
                        "Should return success=true"
                    )
                    return False
            else:
                self.log_test(
                    "POST Soft Delete Test",
                    False,
                    f"Failed to soft delete patient - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with success response"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "POST Soft Delete Test",
                False,
                f"Soft delete request failed: {str(e)}",
                "Should successfully soft delete patient"
            )
            return False
    
    def test_post_hard_delete(self):
        """Test 3: POST /api/practice/patients/{patient_id}/delete with hard_delete=true"""
        print("💥 Testing POST Hard Delete...")
        
        if not self.jwt_token or not self.test_patient_id_2:
            self.log_test(
                "POST Hard Delete Test",
                False,
                "Cannot test hard delete - no JWT token or second test patient available",
                "Requires valid authentication and second test patient"
            )
            return False
            
        try:
            response = self.session.post(
                f"{BACKEND_URL}/practice/patients/{self.test_patient_id_2}/delete",
                json={"hard_delete": True},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    message = data.get("message", "")
                    if "permanently deleted" in message.lower():
                        self.log_test(
                            "POST Hard Delete Test",
                            True,
                            f"Successfully hard deleted patient. Message: {message}",
                            "Should permanently delete patient with hard_delete=true"
                        )
                        return True
                    else:
                        self.log_test(
                            "POST Hard Delete Test",
                            False,
                            f"Unexpected response message: {message}",
                            "Should contain 'permanently deleted' in message"
                        )
                        return False
                else:
                    self.log_test(
                        "POST Hard Delete Test",
                        False,
                        f"API returned success=false: {data}",
                        "Should return success=true"
                    )
                    return False
            else:
                self.log_test(
                    "POST Hard Delete Test",
                    False,
                    f"Failed to hard delete patient - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with success response"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "POST Hard Delete Test",
                False,
                f"Hard delete request failed: {str(e)}",
                "Should successfully hard delete patient"
            )
            return False
    
    def test_patient_list_filtering(self):
        """Test 4: Verify deleted patients don't appear in active patients list"""
        print("📋 Testing Patient List Filtering...")
        
        if not self.jwt_token:
            self.log_test(
                "Patient List Filtering Test",
                False,
                "Cannot test patient list filtering - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patients = data.get("data", [])
                    
                    # Check if soft deleted patient is excluded
                    soft_deleted_found = any(p.get("id") == self.test_patient_id for p in patients)
                    # Check if hard deleted patient is excluded
                    hard_deleted_found = any(p.get("id") == self.test_patient_id_2 for p in patients)
                    
                    if not soft_deleted_found and not hard_deleted_found:
                        self.log_test(
                            "Patient List Filtering Test",
                            True,
                            f"Patient list correctly excludes deleted patients. Found {len(patients)} active patients",
                            "Deleted patients should not appear in active patients list"
                        )
                        return True
                    else:
                        issues = []
                        if soft_deleted_found:
                            issues.append("soft deleted patient still appears")
                        if hard_deleted_found:
                            issues.append("hard deleted patient still appears")
                        
                        self.log_test(
                            "Patient List Filtering Test",
                            False,
                            f"Patient list filtering failed: {', '.join(issues)}",
                            "Deleted patients should not appear in active patients list"
                        )
                        return False
                else:
                    self.log_test(
                        "Patient List Filtering Test",
                        False,
                        f"API returned success=false: {data}",
                        "Should return success=true with patients list"
                    )
                    return False
            else:
                self.log_test(
                    "Patient List Filtering Test",
                    False,
                    f"Failed to get patients list - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with patients list"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Patient List Filtering Test",
                False,
                f"Patient list filtering request failed: {str(e)}",
                "Should successfully retrieve filtered patients list"
            )
            return False
    
    def test_error_handling_nonexistent_patient(self):
        """Test 5: Error handling for non-existent patients"""
        print("🚫 Testing Error Handling for Non-existent Patient...")
        
        if not self.jwt_token:
            self.log_test(
                "Error Handling Test",
                False,
                "Cannot test error handling - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            # Use a fake patient ID
            fake_patient_id = "00000000-0000-0000-0000-000000000000"
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/patients/{fake_patient_id}/delete",
                json={"hard_delete": False},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test(
                        "Error Handling Test",
                        True,
                        f"Correctly returned 404 for non-existent patient: {data.get('detail')}",
                        "Should return 404 with 'not found' message for non-existent patient"
                    )
                    return True
                else:
                    self.log_test(
                        "Error Handling Test",
                        False,
                        f"Returned 404 but unexpected message: {data}",
                        "Should return 'not found' message"
                    )
                    return False
            else:
                self.log_test(
                    "Error Handling Test",
                    False,
                    f"Expected 404 but got {response.status_code}: {response.text}",
                    "Should return 404 for non-existent patient"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Error Handling Test",
                False,
                f"Error handling test request failed: {str(e)}",
                "Should successfully handle non-existent patient error"
            )
            return False
    
    def test_405_method_not_allowed_resolved(self):
        """Test 6: Verify 405 Method Not Allowed error is resolved"""
        print("✅ Testing 405 Method Not Allowed Resolution...")
        
        if not self.jwt_token:
            self.log_test(
                "405 Resolution Test",
                False,
                "Cannot test 405 resolution - no JWT token available",
                "Requires valid authentication"
            )
            return False
            
        try:
            # Create a temporary test patient for this test
            temp_patient_data = {
                "email": f"temp.405.test.{datetime.now().timestamp()}@example.com",
                "firstName": "Temp",
                "lastName": "405Test",
                "phone": "555-0405"
            }
            
            create_response = self.session.post(
                f"{BACKEND_URL}/practice/patients",
                json=temp_patient_data,
                headers={"Content-Type": "application/json"}
            )
            
            if create_response.status_code == 200:
                temp_patient_id = create_response.json().get("data", {}).get("id")
                
                if temp_patient_id:
                    # Test the POST delete endpoint (should work)
                    delete_response = self.session.post(
                        f"{BACKEND_URL}/practice/patients/{temp_patient_id}/delete",
                        json={"hard_delete": True},
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if delete_response.status_code == 200:
                        self.log_test(
                            "405 Resolution Test",
                            True,
                            "POST delete endpoint works correctly - 405 Method Not Allowed error is resolved",
                            "POST delete should work without 405 error"
                        )
                        return True
                    elif delete_response.status_code == 405:
                        self.log_test(
                            "405 Resolution Test",
                            False,
                            "Still getting 405 Method Not Allowed error - issue not resolved",
                            "Should not return 405 error"
                        )
                        return False
                    else:
                        self.log_test(
                            "405 Resolution Test",
                            False,
                            f"Unexpected status code {delete_response.status_code}: {delete_response.text}",
                            "Should return 200 for successful delete"
                        )
                        return False
                else:
                    self.log_test(
                        "405 Resolution Test",
                        False,
                        "Failed to get temp patient ID from create response",
                        "Should create temp patient for testing"
                    )
                    return False
            else:
                self.log_test(
                    "405 Resolution Test",
                    False,
                    f"Failed to create temp patient - Status: {create_response.status_code}",
                    "Should create temp patient for testing"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "405 Resolution Test",
                False,
                f"405 resolution test failed: {str(e)}",
                "Should successfully test POST delete endpoint"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting POST Delete Endpoint Backend Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        
        # Test 2: Create test patients (only if authentication succeeded)
        create_success = False
        if auth_success:
            create_success = self.test_create_test_patients()
        
        # Test 3: POST Soft Delete (only if patients created)
        soft_delete_success = False
        if create_success:
            soft_delete_success = self.test_post_soft_delete()
        
        # Test 4: POST Hard Delete (only if patients created)
        hard_delete_success = False
        if create_success:
            hard_delete_success = self.test_post_hard_delete()
        
        # Test 5: Patient List Filtering (only if deletes worked)
        filtering_success = False
        if soft_delete_success or hard_delete_success:
            filtering_success = self.test_patient_list_filtering()
        
        # Test 6: Error Handling (can run if authenticated)
        error_handling_success = False
        if auth_success:
            error_handling_success = self.test_error_handling_nonexistent_patient()
        
        # Test 7: 405 Resolution Test (can run if authenticated)
        resolution_success = False
        if auth_success:
            resolution_success = self.test_405_method_not_allowed_resolved()
        
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
        print(f"✅ Create Test Patients: {'PASSED' if create_success else 'FAILED'}")  
        print(f"✅ POST Soft Delete Test: {'PASSED' if soft_delete_success else 'FAILED'}")
        print(f"✅ POST Hard Delete Test: {'PASSED' if hard_delete_success else 'FAILED'}")
        print(f"✅ Patient List Filtering: {'PASSED' if filtering_success else 'FAILED'}")
        print(f"✅ Error Handling Test: {'PASSED' if error_handling_success else 'FAILED'}")
        print(f"✅ 405 Resolution Test: {'PASSED' if resolution_success else 'FAILED'}")
        
        if all([auth_success, create_success, soft_delete_success, hard_delete_success, filtering_success, error_handling_success, resolution_success]):
            print("\n🎉 ALL TESTS PASSED - POST delete endpoint is working correctly!")
            print("✅ 405 Method Not Allowed error has been resolved")
            print("✅ Soft delete (hard_delete=false) works correctly")
            print("✅ Hard delete (hard_delete=true) works correctly")
            print("✅ Patient list filtering excludes deleted patients")
            print("✅ Error handling for non-existent patients works")
        else:
            failed_tests = []
            if not auth_success: failed_tests.append("Authentication")
            if not create_success: failed_tests.append("Create Test Patients")
            if not soft_delete_success: failed_tests.append("POST Soft Delete")
            if not hard_delete_success: failed_tests.append("POST Hard Delete")
            if not filtering_success: failed_tests.append("Patient List Filtering")
            if not error_handling_success: failed_tests.append("Error Handling")
            if not resolution_success: failed_tests.append("405 Resolution")
            
            print(f"\n⚠️  {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)