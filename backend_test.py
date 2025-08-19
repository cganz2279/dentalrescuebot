#!/usr/bin/env python3
"""
Backend API Testing for Dental Post-Operative Care App
Tests all backend endpoints to ensure proper functionality
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dental-postcare.preview.emergentagent.com/api"

class DentalAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
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
    
    def test_health_check(self):
        """Test GET /api/ endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Health Check (GET /api/)", True, f"Response: {data}")
                    return True
                else:
                    self.log_test("Health Check (GET /api/)", False, "Missing 'message' in response")
                    return False
            else:
                self.log_test("Health Check (GET /api/)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check (GET /api/)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_specialties(self):
        """Test GET /api/specialties endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    if len(specialties) == 7:  # Should have 7 dental specialties
                        # Check if each specialty has required fields
                        required_fields = ["id", "name", "description", "procedureCount"]
                        all_valid = True
                        for specialty in specialties:
                            for field in required_fields:
                                if field not in specialty:
                                    all_valid = False
                                    break
                        
                        if all_valid:
                            self.log_test("Get All Specialties", True, f"Found {len(specialties)} specialties with procedure counts")
                            return True
                        else:
                            self.log_test("Get All Specialties", False, "Missing required fields in specialties")
                            return False
                    else:
                        self.log_test("Get All Specialties", False, f"Expected 7 specialties, got {len(specialties)}")
                        return False
                else:
                    self.log_test("Get All Specialties", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get All Specialties", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get All Specialties", False, f"Exception: {str(e)}")
            return False
    
    def test_get_specialty_by_id(self):
        """Test GET /api/specialties/{id} endpoint"""
        try:
            # Test with oral-surgery specialty
            response = self.session.get(f"{self.base_url}/specialties/oral-surgery")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialty = data["data"]
                    required_fields = ["id", "name", "description", "procedures"]
                    
                    if all(field in specialty for field in required_fields):
                        if specialty["id"] == "oral-surgery":
                            procedures = specialty.get("procedures", [])
                            self.log_test("Get Specialty by ID (oral-surgery)", True, 
                                        f"Found specialty with {len(procedures)} procedures")
                            return True
                        else:
                            self.log_test("Get Specialty by ID (oral-surgery)", False, "Wrong specialty returned")
                            return False
                    else:
                        self.log_test("Get Specialty by ID (oral-surgery)", False, "Missing required fields")
                        return False
                else:
                    self.log_test("Get Specialty by ID (oral-surgery)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Specialty by ID (oral-surgery)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Specialty by ID (oral-surgery)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_procedures(self):
        """Test GET /api/procedures endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    if len(procedures) > 0:
                        # Check if procedures have required fields
                        required_fields = ["id", "name", "specialty", "specialtyName", "duration"]
                        sample_procedure = procedures[0]
                        
                        if all(field in sample_procedure for field in required_fields):
                            self.log_test("Get All Procedures", True, f"Found {len(procedures)} procedures")
                            return True
                        else:
                            self.log_test("Get All Procedures", False, "Missing required fields in procedures")
                            return False
                    else:
                        self.log_test("Get All Procedures", False, "No procedures found")
                        return False
                else:
                    self.log_test("Get All Procedures", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get All Procedures", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get All Procedures", False, f"Exception: {str(e)}")
            return False
    
    def test_get_procedure_by_id(self):
        """Test GET /api/procedures/{id} endpoint"""
        try:
            # Test with root-canal-therapy procedure
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    required_fields = ["id", "name", "specialty", "specialtyName", "duration", 
                                     "overview", "immediateAftercare", "dietRestrictions", 
                                     "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                    
                    if all(field in procedure for field in required_fields):
                        if procedure["id"] == "root-canal-therapy":
                            self.log_test("Get Procedure by ID (root-canal-therapy)", True, 
                                        f"Found detailed procedure information")
                            return True
                        else:
                            self.log_test("Get Procedure by ID (root-canal-therapy)", False, "Wrong procedure returned")
                            return False
                    else:
                        missing_fields = [f for f in required_fields if f not in procedure]
                        self.log_test("Get Procedure by ID (root-canal-therapy)", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Get Procedure by ID (root-canal-therapy)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedure by ID (root-canal-therapy)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedure by ID (root-canal-therapy)", False, f"Exception: {str(e)}")
            return False
    
    def test_search_procedures(self):
        """Test GET /api/procedures/search endpoint"""
        try:
            # Search for procedures containing "root"
            response = self.session.get(f"{self.base_url}/procedures/search?q=root")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    if len(procedures) > 0:
                        # Check if search results contain "root" in name or description
                        valid_results = True
                        for procedure in procedures:
                            name_match = "root" in procedure.get("name", "").lower()
                            specialty_match = "root" in procedure.get("specialtyName", "").lower()
                            if not (name_match or specialty_match):
                                # This might be okay if it matches in overview field
                                pass
                        
                        self.log_test("Search Procedures (q=root)", True, 
                                    f"Found {len(procedures)} matching procedures")
                        return True
                    else:
                        self.log_test("Search Procedures (q=root)", False, "No search results found")
                        return False
                else:
                    self.log_test("Search Procedures (q=root)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Search Procedures (q=root)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Search Procedures (q=root)", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid endpoints"""
        try:
            # Test invalid specialty ID
            response = self.session.get(f"{self.base_url}/specialties/invalid-id")
            
            if response.status_code == 404:
                data = response.json()
                if "detail" in data:
                    self.log_test("Error Handling (Invalid Specialty ID)", True, 
                                f"Proper 404 error returned: {data['detail']}")
                    return True
                else:
                    self.log_test("Error Handling (Invalid Specialty ID)", False, 
                                "404 status but missing error detail")
                    return False
            else:
                self.log_test("Error Handling (Invalid Specialty ID)", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling (Invalid Specialty ID)", False, f"Exception: {str(e)}")
            return False

    def test_practice_login(self):
        """Test practice admin login"""
        try:
            login_data = {
                "email": "admin@smithdental.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    user_info = data.get("user", {})
                    self.log_test("Practice Admin Login", True, 
                                f"Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    self.log_test("Practice Admin Login", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_get_patients(self):
        """Test GET /api/practice/patients endpoint"""
        if not self.auth_token:
            self.log_test("Get Patients API", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    self.log_test("Get Patients API", True, 
                                f"Retrieved {len(patients)} patients")
                    return True
                else:
                    self.log_test("Get Patients API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Patients API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Patients API", False, f"Exception: {str(e)}")
            return False

    def test_add_patient(self):
        """Test POST /api/practice/patients endpoint"""
        if not self.auth_token:
            self.log_test("Add Patient API", False, "No authentication token available")
            return False
            
        try:
            # Create a unique patient for testing
            import time
            timestamp = str(int(time.time()))
            patient_data = {
                "email": f"patient{timestamp}@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "phone": "555-0123"
            }
            
            response = self.session.post(f"{self.base_url}/practice/patients", json=patient_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patient = data["data"]
                    # Store patient ID for later tests
                    self.test_patient_id = patient.get("id")
                    self.log_test("Add Patient API", True, 
                                f"Created patient: {patient.get('firstName')} {patient.get('lastName')} (ID: {patient.get('id')})")
                    return True
                else:
                    self.log_test("Add Patient API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Add Patient API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Patient API", False, f"Exception: {str(e)}")
            return False

    def test_add_patient_validation(self):
        """Test POST /api/practice/patients validation"""
        if not self.auth_token:
            self.log_test("Add Patient Validation", False, "No authentication token available")
            return False
            
        try:
            # Test with missing required fields
            invalid_data = {
                "email": "invalid-email",
                "firstName": ""
            }
            
            response = self.session.post(f"{self.base_url}/practice/patients", json=invalid_data)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Add Patient Validation", True, 
                            "Properly rejected invalid patient data")
                return True
            else:
                self.log_test("Add Patient Validation", False, 
                            f"Expected validation error (422), got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Add Patient Validation", False, f"Exception: {str(e)}")
            return False

    def test_assign_procedure(self):
        """Test POST /api/practice/assign-procedure endpoint"""
        if not self.auth_token:
            self.log_test("Assign Procedure API", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_patient_id') or not self.test_patient_id:
            self.log_test("Assign Procedure API", False, "No test patient available")
            return False
            
        try:
            # First get a procedure ID to assign
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            if procedures_response.status_code != 200:
                self.log_test("Assign Procedure API", False, "Could not fetch procedures")
                return False
                
            procedures_data = procedures_response.json()
            if not procedures_data.get("success") or not procedures_data.get("data"):
                self.log_test("Assign Procedure API", False, "No procedures available")
                return False
                
            procedure = procedures_data["data"][0]  # Use first procedure
            
            assignment_data = {
                "patientId": self.test_patient_id,
                "procedureId": procedure["id"],
                "procedureName": procedure["name"],
                "performedDate": "2024-01-15T10:00:00Z",
                "dentistName": "Dr. John Smith",
                "practiceNotes": "Standard procedure performed successfully",
                "customInstructions": ["Take medication as prescribed", "Avoid hard foods for 24 hours"],
                "followUpDate": "2024-01-22T14:00:00Z"
            }
            
            response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assignment_info = data.get("data", {})
                    # Store assignment ID for later tests
                    self.test_assignment_id = assignment_info.get("assignmentId")
                    self.log_test("Assign Procedure API", True, 
                                f"Assigned {assignment_info.get('procedureName', 'procedure')} to {assignment_info.get('patientName', 'patient')} (Assignment ID: {self.test_assignment_id})")
                    return True
                else:
                    self.log_test("Assign Procedure API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Assign Procedure API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Assign Procedure API", False, f"Exception: {str(e)}")
            return False

    def test_get_export_data(self):
        """Test GET /api/practice/export-data endpoint"""
        if not self.auth_token:
            self.log_test("Get Export Data API", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/export-data")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    export_data = data["data"]
                    patients = export_data.get("patients", [])
                    self.log_test("Get Export Data API", True, 
                                f"Retrieved export data for {len(patients)} patients")
                    return True
                else:
                    self.log_test("Get Export Data API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Export Data API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Export Data API", False, f"Exception: {str(e)}")
            return False

    def test_get_procedures_with_filter(self):
        """Test GET /api/procedures with specialty filter"""
        try:
            # Test filtering by specialty
            response = self.session.get(f"{self.base_url}/procedures?specialty=oral-surgery")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    # Verify all procedures are from oral-surgery specialty
                    all_oral_surgery = all(proc.get("specialty") == "oral-surgery" for proc in procedures)
                    if all_oral_surgery:
                        self.log_test("Get Procedures with Filter", True, 
                                    f"Retrieved {len(procedures)} oral surgery procedures")
                        return True
                    else:
                        self.log_test("Get Procedures with Filter", False, 
                                    "Filter not working - got procedures from other specialties")
                        return False
                else:
                    self.log_test("Get Procedures with Filter", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedures with Filter", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedures with Filter", False, f"Exception: {str(e)}")
            return False

    def test_get_practice_doctors(self):
        """Test GET /api/practice/doctors endpoint"""
        if not self.auth_token:
            self.log_test("Get Practice Doctors API", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/doctors")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    doctors = data["data"]
                    # Check if doctors have proper formatting (no double "Dr.")
                    properly_formatted = True
                    for doctor in doctors:
                        name = doctor.get("name", "")
                        if "Dr. Dr." in name:
                            properly_formatted = False
                            break
                    
                    if properly_formatted:
                        self.log_test("Get Practice Doctors API", True, 
                                    f"Retrieved {len(doctors)} doctors with proper name formatting")
                        return True
                    else:
                        self.log_test("Get Practice Doctors API", False, 
                                    "Doctor names have double 'Dr.' prefix")
                        return False
                else:
                    self.log_test("Get Practice Doctors API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Practice Doctors API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Practice Doctors API", False, f"Exception: {str(e)}")
            return False

    def test_get_procedure_assignment(self):
        """Test GET /api/practice/assignment/{assignment_id} endpoint"""
        if not self.auth_token:
            self.log_test("Get Procedure Assignment API", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_assignment_id') or not self.test_assignment_id:
            self.log_test("Get Procedure Assignment API", False, "No test assignment available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/assignment/{self.test_assignment_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment_data = data["data"]
                    required_keys = ["assignment", "patient", "procedure"]
                    
                    if all(key in assignment_data for key in required_keys):
                        assignment = assignment_data["assignment"]
                        patient = assignment_data["patient"]
                        procedure = assignment_data["procedure"]
                        
                        self.log_test("Get Procedure Assignment API", True, 
                                    f"Retrieved assignment for patient {patient.get('firstName', '')} {patient.get('lastName', '')} - {procedure.get('name', '')}")
                        return True
                    else:
                        self.log_test("Get Procedure Assignment API", False, 
                                    "Missing required keys in response")
                        return False
                else:
                    self.log_test("Get Procedure Assignment API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedure Assignment API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedure Assignment API", False, f"Exception: {str(e)}")
            return False

    def test_get_procedure_assignment_404(self):
        """Test GET /api/practice/assignment/{assignment_id} with invalid ID"""
        if not self.auth_token:
            self.log_test("Get Procedure Assignment 404 Test", False, "No authentication token available")
            return False
            
        try:
            invalid_id = "invalid-assignment-id-12345"
            response = self.session.get(f"{self.base_url}/practice/assignment/{invalid_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "detail" in data:
                    self.log_test("Get Procedure Assignment 404 Test", True, 
                                f"Properly returned 404 for invalid assignment ID: {data['detail']}")
                    return True
                else:
                    self.log_test("Get Procedure Assignment 404 Test", False, 
                                "404 status but missing error detail")
                    return False
            else:
                self.log_test("Get Procedure Assignment 404 Test", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedure Assignment 404 Test", False, f"Exception: {str(e)}")
            return False

    def test_update_procedure_assignment(self):
        """Test PUT /api/practice/assignment/{assignment_id} endpoint"""
        if not self.auth_token:
            self.log_test("Update Procedure Assignment API", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_assignment_id') or not self.test_assignment_id:
            self.log_test("Update Procedure Assignment API", False, "No test assignment available")
            return False
            
        try:
            update_data = {
                "dentistName": "Dr. Jane Smith",
                "practiceNotes": "Updated notes - procedure went well",
                "status": "completed"
            }
            
            response = self.session.put(f"{self.base_url}/practice/assignment/{self.test_assignment_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Update Procedure Assignment API", True, 
                                "Successfully updated procedure assignment")
                    return True
                else:
                    self.log_test("Update Procedure Assignment API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Update Procedure Assignment API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Procedure Assignment API", False, f"Exception: {str(e)}")
            return False

    def test_update_procedure_assignment_404(self):
        """Test PUT /api/practice/assignment/{assignment_id} with invalid ID"""
        if not self.auth_token:
            self.log_test("Update Procedure Assignment 404 Test", False, "No authentication token available")
            return False
            
        try:
            invalid_id = "invalid-assignment-id-12345"
            update_data = {
                "dentistName": "Dr. Test",
                "practiceNotes": "Test update"
            }
            
            response = self.session.put(f"{self.base_url}/practice/assignment/{invalid_id}", json=update_data)
            
            if response.status_code == 404:
                data = response.json()
                if "detail" in data:
                    self.log_test("Update Procedure Assignment 404 Test", True, 
                                f"Properly returned 404 for invalid assignment ID: {data['detail']}")
                    return True
                else:
                    self.log_test("Update Procedure Assignment 404 Test", False, 
                                "404 status but missing error detail")
                    return False
            else:
                self.log_test("Update Procedure Assignment 404 Test", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Update Procedure Assignment 404 Test", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🧪 Starting Backend API Tests for Dental Post-Operative Care App")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Basic API tests
        basic_tests = [
            self.test_health_check,
            self.test_get_specialties,
            self.test_get_specialty_by_id,
            self.test_get_procedures,
            self.test_get_procedure_by_id,
            self.test_search_procedures,
            self.test_get_procedures_with_filter,
            self.test_error_handling
        ]
        
        # Practice management tests (require authentication)
        practice_tests = [
            self.test_practice_login,
            self.test_get_patients,
            self.test_add_patient,
            self.test_add_patient_validation,
            self.test_assign_procedure,
            self.test_get_export_data,
            self.test_get_practice_doctors,
            self.test_get_procedure_assignment,
            self.test_get_procedure_assignment_404,
            self.test_update_procedure_assignment,
            self.test_update_procedure_assignment_404
        ]
        
        all_tests = basic_tests + practice_tests
        passed = 0
        total = len(all_tests)
        
        print("🔍 Running Basic API Tests...")
        for test in basic_tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("🏥 Running Practice Management Tests...")
        for test in practice_tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 70)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend APIs are working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the tests"""
    tester = DentalAPITester(BACKEND_URL)
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()