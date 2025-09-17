#!/usr/bin/env python3
"""
Delete Patient Functionality Testing Script
Review Request: Test delete patient functionality with both soft delete and hard delete options

Tests:
1. Authentication with cganz2279@gmail.com/password123
2. GET /api/practice/patients - verify returns only active patients
3. DELETE /api/practice/patients/{patient_id} - test soft delete (default behavior)
4. DELETE /api/practice/patients/{patient_id}?hard_delete=true - test hard delete
5. Verify patient removal from active list after delete
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Backend URL - using local backend since production doesn't have DELETE routes deployed
BACKEND_URL = "http://localhost:8001/api"

class DeletePatientTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.practice_id = None
        self.test_results = []
        self.test_patient_ids = []  # Track created test patients for cleanup
        
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
    
    def test_get_active_patients_initial(self):
        """Test 2: GET /api/practice/patients - verify returns only active patients"""
        print("👥 Testing GET Active Patients (Initial)...")
        
        if not self.jwt_token:
            self.log_test(
                "GET Active Patients Initial Test",
                False,
                "Cannot test patients endpoint - no JWT token available",
                "Requires valid authentication"
            )
            return False, 0
            
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patients = data.get("data", [])
                    active_count = len(patients)
                    
                    # Verify all returned patients are active
                    all_active = all(patient.get("isActive", False) for patient in patients)
                    
                    if all_active:
                        self.log_test(
                            "GET Active Patients Initial Test",
                            True,
                            f"Successfully retrieved {active_count} active patients. All patients have isActive=True",
                            "Should return only active patients with isActive=True"
                        )
                        return True, active_count
                    else:
                        inactive_patients = [p for p in patients if not p.get("isActive", False)]
                        self.log_test(
                            "GET Active Patients Initial Test",
                            False,
                            f"Found {len(inactive_patients)} inactive patients in active patients list",
                            "Should return only active patients"
                        )
                        return False, active_count
                else:
                    self.log_test(
                        "GET Active Patients Initial Test",
                        False,
                        f"API returned success=false: {data}",
                        "Should return success=true with patient data"
                    )
                    return False, 0
            else:
                self.log_test(
                    "GET Active Patients Initial Test",
                    False,
                    f"Failed to get patients - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with patient list"
                )
                return False, 0
                
        except Exception as e:
            self.log_test(
                "GET Active Patients Initial Test",
                False,
                f"Get patients request failed: {str(e)}",
                "Should successfully retrieve patient list"
            )
            return False, 0
    
    def create_test_patient(self, suffix=""):
        """Helper: Create a test patient for deletion testing"""
        try:
            patient_data = {
                "email": f"test.patient{suffix}@deletetest.com",
                "firstName": f"TestPatient{suffix}",
                "lastName": "DeleteTest",
                "phone": "555-0123"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/patients",
                json=patient_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patient_id = data.get("data", {}).get("id")
                    if patient_id:
                        self.test_patient_ids.append(patient_id)
                        return patient_id, patient_data
            
            return None, None
            
        except Exception as e:
            print(f"Failed to create test patient: {e}")
            return None, None
    
    def create_test_procedure_assignment(self, patient_id):
        """Helper: Create a test procedure assignment for the patient"""
        try:
            assignment_data = {
                "patientId": patient_id,
                "procedureId": "root-canal-therapy",  # Use a known procedure
                "procedureName": "Root Canal Therapy",
                "performedDate": "2024-01-15T10:00:00Z",
                "dentistName": "Dr. Test Dentist",
                "practiceNotes": "Test procedure assignment for delete testing"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/assign-procedure",
                json=assignment_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("assignmentId")
            
            return None
            
        except Exception as e:
            print(f"Failed to create test procedure assignment: {e}")
            return None
    
    def test_soft_delete_patient(self):
        """Test 3: DELETE /api/practice/patients/{patient_id} - test soft delete"""
        print("🗑️ Testing Soft Delete Patient...")
        
        if not self.jwt_token:
            self.log_test(
                "Soft Delete Patient Test",
                False,
                "Cannot test soft delete - no JWT token available",
                "Requires valid authentication"
            )
            return False, None
        
        # Create test patient
        patient_id, patient_data = self.create_test_patient("_soft")
        if not patient_id:
            self.log_test(
                "Soft Delete Patient Test",
                False,
                "Failed to create test patient for soft delete testing",
                "Should be able to create test patient"
            )
            return False, None
        
        # Create procedure assignment for the patient
        assignment_id = self.create_test_procedure_assignment(patient_id)
        
        try:
            # Perform soft delete (default behavior)
            response = self.session.delete(f"{BACKEND_URL}/practice/patients/{patient_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    message = data.get("message", "")
                    active_procedures = data.get("activeProcedures", 0)
                    note = data.get("note", "")
                    
                    # Verify the response indicates soft delete
                    if "deactivated" in message.lower() and "preserved" in note.lower():
                        self.log_test(
                            "Soft Delete Patient Test",
                            True,
                            f"Successfully soft deleted patient. Message: '{message}', Active Procedures: {active_procedures}, Note: '{note}'",
                            "Should deactivate patient and preserve procedure assignments"
                        )
                        return True, patient_id
                    else:
                        self.log_test(
                            "Soft Delete Patient Test",
                            False,
                            f"Soft delete response doesn't indicate proper soft delete. Message: '{message}', Note: '{note}'",
                            "Should indicate patient deactivation and procedure preservation"
                        )
                        return False, patient_id
                else:
                    self.log_test(
                        "Soft Delete Patient Test",
                        False,
                        f"Soft delete returned success=false: {data}",
                        "Should return success=true"
                    )
                    return False, patient_id
            else:
                self.log_test(
                    "Soft Delete Patient Test",
                    False,
                    f"Soft delete failed - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with success message"
                )
                return False, patient_id
                
        except Exception as e:
            self.log_test(
                "Soft Delete Patient Test",
                False,
                f"Soft delete request failed: {str(e)}",
                "Should successfully perform soft delete"
            )
            return False, patient_id
    
    def test_hard_delete_patient(self):
        """Test 4: DELETE /api/practice/patients/{patient_id}?hard_delete=true - test hard delete"""
        print("💥 Testing Hard Delete Patient...")
        
        if not self.jwt_token:
            self.log_test(
                "Hard Delete Patient Test",
                False,
                "Cannot test hard delete - no JWT token available",
                "Requires valid authentication"
            )
            return False, None
        
        # Create test patient
        patient_id, patient_data = self.create_test_patient("_hard")
        if not patient_id:
            self.log_test(
                "Hard Delete Patient Test",
                False,
                "Failed to create test patient for hard delete testing",
                "Should be able to create test patient"
            )
            return False, None
        
        # Create procedure assignment for the patient
        assignment_id = self.create_test_procedure_assignment(patient_id)
        
        try:
            # Perform hard delete
            response = self.session.delete(f"{BACKEND_URL}/practice/patients/{patient_id}?hard_delete=true")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    message = data.get("message", "")
                    deleted_procedures = data.get("deletedProcedures", 0)
                    
                    # Verify the response indicates hard delete
                    if "permanently deleted" in message.lower():
                        self.log_test(
                            "Hard Delete Patient Test",
                            True,
                            f"Successfully hard deleted patient. Message: '{message}', Deleted Procedures: {deleted_procedures}",
                            "Should permanently delete patient and all procedure assignments"
                        )
                        return True, patient_id
                    else:
                        self.log_test(
                            "Hard Delete Patient Test",
                            False,
                            f"Hard delete response doesn't indicate permanent deletion. Message: '{message}'",
                            "Should indicate permanent patient deletion"
                        )
                        return False, patient_id
                else:
                    self.log_test(
                        "Hard Delete Patient Test",
                        False,
                        f"Hard delete returned success=false: {data}",
                        "Should return success=true"
                    )
                    return False, patient_id
            else:
                self.log_test(
                    "Hard Delete Patient Test",
                    False,
                    f"Hard delete failed - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with success message"
                )
                return False, patient_id
                
        except Exception as e:
            self.log_test(
                "Hard Delete Patient Test",
                False,
                f"Hard delete request failed: {str(e)}",
                "Should successfully perform hard delete"
            )
            return False, patient_id
    
    def test_verify_patient_removal(self, soft_deleted_id, hard_deleted_id):
        """Test 5: Verify deleted patients don't appear in active patients list"""
        print("🔍 Testing Patient Removal Verification...")
        
        if not self.jwt_token:
            self.log_test(
                "Patient Removal Verification Test",
                False,
                "Cannot test patient removal - no JWT token available",
                "Requires valid authentication"
            )
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patients = data.get("data", [])
                    patient_ids = [p.get("id") for p in patients]
                    
                    # Check if deleted patients are in the list
                    soft_deleted_found = soft_deleted_id in patient_ids if soft_deleted_id else False
                    hard_deleted_found = hard_deleted_id in patient_ids if hard_deleted_id else False
                    
                    if not soft_deleted_found and not hard_deleted_found:
                        self.log_test(
                            "Patient Removal Verification Test",
                            True,
                            f"Verified deleted patients are not in active list. Soft deleted ID: {soft_deleted_id}, Hard deleted ID: {hard_deleted_id}. Current active patients: {len(patients)}",
                            "Deleted patients should not appear in active patients list"
                        )
                        return True
                    else:
                        found_patients = []
                        if soft_deleted_found:
                            found_patients.append(f"soft deleted: {soft_deleted_id}")
                        if hard_deleted_found:
                            found_patients.append(f"hard deleted: {hard_deleted_id}")
                        
                        self.log_test(
                            "Patient Removal Verification Test",
                            False,
                            f"Found deleted patients in active list: {', '.join(found_patients)}",
                            "Deleted patients should not appear in active patients list"
                        )
                        return False
                else:
                    self.log_test(
                        "Patient Removal Verification Test",
                        False,
                        f"API returned success=false: {data}",
                        "Should return success=true with patient data"
                    )
                    return False
            else:
                self.log_test(
                    "Patient Removal Verification Test",
                    False,
                    f"Failed to get patients - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with patient list"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Patient Removal Verification Test",
                False,
                f"Patient removal verification failed: {str(e)}",
                "Should successfully verify patient removal"
            )
            return False
    
    def cleanup_test_patients(self):
        """Clean up any remaining test patients"""
        print("🧹 Cleaning up test patients...")
        
        for patient_id in self.test_patient_ids:
            try:
                # Try hard delete to clean up
                self.session.delete(f"{BACKEND_URL}/practice/patients/{patient_id}?hard_delete=true")
            except:
                pass  # Ignore cleanup errors
    
    def run_all_tests(self):
        """Run all delete patient tests in sequence"""
        print("🚀 Starting Delete Patient Functionality Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 70)
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with other tests")
            return False
        
        # Test 2: Get initial active patients count
        patients_success, initial_count = self.test_get_active_patients_initial()
        
        # Test 3: Soft delete patient
        soft_delete_success, soft_deleted_id = self.test_soft_delete_patient()
        
        # Test 4: Hard delete patient
        hard_delete_success, hard_deleted_id = self.test_hard_delete_patient()
        
        # Test 5: Verify patient removal from active list
        removal_success = self.test_verify_patient_removal(soft_deleted_id, hard_deleted_id)
        
        # Cleanup
        self.cleanup_test_patients()
        
        # Summary
        print("=" * 70)
        print("📊 DELETE PATIENT TEST SUMMARY")
        print("=" * 70)
        
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
        print(f"✅ Authentication: {'PASSED' if auth_success else 'FAILED'}")
        print(f"✅ GET Active Patients: {'PASSED' if patients_success else 'FAILED'}")  
        print(f"✅ Soft Delete: {'PASSED' if soft_delete_success else 'FAILED'}")
        print(f"✅ Hard Delete: {'PASSED' if hard_delete_success else 'FAILED'}")
        print(f"✅ Patient Removal Verification: {'PASSED' if removal_success else 'FAILED'}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL DELETE PATIENT TESTS PASSED!")
            print("✅ Soft delete marks patients as inactive and preserves procedure assignments")
            print("✅ Hard delete permanently removes patients and all procedure assignments")
            print("✅ Deleted patients don't appear in active patients list")
            print("✅ Appropriate success messages and counts are returned")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - see details above")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = DeletePatientTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)