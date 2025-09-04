#!/usr/bin/env python3
"""
Backend API Testing for New Document Library and Patient Editing Features
Tests the specific APIs mentioned in the review request
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

class NewFeaturesTester:
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
    
    def test_practice_login(self):
        """Test practice admin login to get authentication token"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
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

    def test_update_patient_api(self):
        """Test PUT /api/practice/patients/{patientId} endpoint - NEW FEATURE"""
        if not self.auth_token:
            self.log_test("Update Patient API", False, "No authentication token available")
            return False
            
        try:
            # First, get existing patients to find one to update
            patients_response = self.session.get(f"{self.base_url}/practice/patients")
            if patients_response.status_code != 200:
                self.log_test("Update Patient API", False, "Could not fetch existing patients")
                return False
                
            patients_data = patients_response.json()
            if not patients_data.get("success") or not patients_data.get("data"):
                self.log_test("Update Patient API", False, "No patients available for testing")
                return False
                
            # Use the first patient for testing
            test_patient = patients_data["data"][0]
            patient_id = test_patient["id"]
            
            # Prepare update data with new patient editing fields
            update_data = {
                "firstName": "UpdatedFirstName",
                "lastName": "UpdatedLastName", 
                "email": test_patient["email"],  # Keep same email
                "phone": "555-999-8888",
                "dateOfBirth": "1990-01-15",
                "address": {
                    "street": "123 Updated Street",
                    "city": "Updated City",
                    "state": "CA",
                    "zipCode": "90210"
                },
                "emergencyContact": {
                    "name": "Emergency Contact Name",
                    "phone": "555-111-2222",
                    "relationship": "Spouse"
                }
            }
            
            # Test the updatePatient API endpoint
            response = self.session.put(f"{self.base_url}/practice/patients/{patient_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Update Patient API", True, 
                                f"Successfully updated patient {patient_id} with new fields (address, emergency contact, DOB)")
                    return True
                else:
                    self.log_test("Update Patient API", False, "Invalid response format")
                    return False
            elif response.status_code == 404:
                self.log_test("Update Patient API", False, 
                            "API endpoint not implemented - PUT /api/practice/patients/{patientId} returns 404")
                return False
            else:
                self.log_test("Update Patient API", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Patient API", False, f"Exception: {str(e)}")
            return False

    def test_get_procedures_for_library(self):
        """Test GET /api/procedures endpoint for Procedure Library feature"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    if len(procedures) > 0:
                        # Check if procedures have required fields for library
                        required_fields = ["id", "name", "specialty", "specialtyName", "duration"]
                        sample_procedure = procedures[0]
                        
                        if all(field in sample_procedure for field in required_fields):
                            self.log_test("Get Procedures for Library", True, 
                                        f"Found {len(procedures)} procedures with required fields for document library")
                            return True
                        else:
                            self.log_test("Get Procedures for Library", False, "Missing required fields in procedures")
                            return False
                    else:
                        self.log_test("Get Procedures for Library", False, "No procedures found")
                        return False
                else:
                    self.log_test("Get Procedures for Library", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedures for Library", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedures for Library", False, f"Exception: {str(e)}")
            return False

    def test_get_specialties_for_library(self):
        """Test GET /api/specialties endpoint for Procedure Library feature"""
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    if len(specialties) == 7:  # Should have 7 dental specialties
                        # Check if each specialty has required fields for library browsing
                        required_fields = ["id", "name", "description", "procedureCount"]
                        all_valid = True
                        for specialty in specialties:
                            for field in required_fields:
                                if field not in specialty:
                                    all_valid = False
                                    break
                        
                        if all_valid:
                            self.log_test("Get Specialties for Library", True, 
                                        f"Found {len(specialties)} specialties with procedure counts for library browsing")
                            return True
                        else:
                            self.log_test("Get Specialties for Library", False, "Missing required fields in specialties")
                            return False
                    else:
                        self.log_test("Get Specialties for Library", False, f"Expected 7 specialties, got {len(specialties)}")
                        return False
                else:
                    self.log_test("Get Specialties for Library", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Specialties for Library", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Specialties for Library", False, f"Exception: {str(e)}")
            return False

    def test_get_patients_still_works(self):
        """Test GET /api/practice/patients still works for patient management"""
        if not self.auth_token:
            self.log_test("Get Patients Still Works", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    # Check if patients have procedure counts for management page
                    if len(patients) > 0:
                        sample_patient = patients[0]
                        if "procedureCount" in sample_patient:
                            self.log_test("Get Patients Still Works", True, 
                                        f"Retrieved {len(patients)} patients with procedure counts for management")
                            return True
                        else:
                            self.log_test("Get Patients Still Works", False, "Missing procedureCount in patient data")
                            return False
                    else:
                        self.log_test("Get Patients Still Works", True, "No patients found but API working correctly")
                        return True
                else:
                    self.log_test("Get Patients Still Works", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Patients Still Works", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Patients Still Works", False, f"Exception: {str(e)}")
            return False

    def test_get_procedure_assignment_for_view_buttons(self):
        """Test GET /api/practice/assignment/{assignmentId} for View buttons functionality"""
        if not self.auth_token:
            self.log_test("Get Procedure Assignment for View Buttons", False, "No authentication token available")
            return False
            
        try:
            # First, create a test assignment to view
            # Get patients and procedures
            patients_response = self.session.get(f"{self.base_url}/practice/patients")
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            
            if patients_response.status_code != 200 or procedures_response.status_code != 200:
                self.log_test("Get Procedure Assignment for View Buttons", False, "Could not fetch patients or procedures")
                return False
                
            patients_data = patients_response.json()
            procedures_data = procedures_response.json()
            
            if not (patients_data.get("success") and procedures_data.get("success")):
                self.log_test("Get Procedure Assignment for View Buttons", False, "Invalid patient or procedure data")
                return False
                
            patients = patients_data.get("data", [])
            procedures = procedures_data.get("data", [])
            
            if len(patients) == 0 or len(procedures) == 0:
                self.log_test("Get Procedure Assignment for View Buttons", False, "No patients or procedures available for testing")
                return False
                
            # Create a test assignment
            patient = patients[0]
            procedure = procedures[0]
            
            assignment_data = {
                "patientId": patient["id"],
                "procedureId": procedure["id"],
                "procedureName": procedure["name"],
                "performedDate": "2024-01-15T10:00:00Z",
                "dentistName": "Dr. Test Doctor",
                "practiceNotes": "Test assignment for View button functionality",
                "customInstructions": ["Test instruction 1", "Test instruction 2"],
                "followUpDate": "2024-01-22T14:00:00Z"
            }
            
            assign_response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data)
            
            if assign_response.status_code != 200:
                self.log_test("Get Procedure Assignment for View Buttons", False, "Could not create test assignment")
                return False
                
            assign_data = assign_response.json()
            if not assign_data.get("success"):
                self.log_test("Get Procedure Assignment for View Buttons", False, "Failed to create test assignment")
                return False
                
            assignment_id = assign_data.get("data", {}).get("assignmentId")
            if not assignment_id:
                self.log_test("Get Procedure Assignment for View Buttons", False, "No assignment ID returned")
                return False
            
            # Now test the View button functionality - GET assignment
            response = self.session.get(f"{self.base_url}/practice/assignment/{assignment_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment_data = data["data"]
                    required_keys = ["assignment", "patient", "procedure"]
                    
                    if all(key in assignment_data for key in required_keys):
                        assignment = assignment_data["assignment"]
                        patient_info = assignment_data["patient"]
                        procedure_info = assignment_data["procedure"]
                        
                        # Check if procedure has full details for View page
                        procedure_fields = ["overview", "immediateAftercare", "dietRestrictions", 
                                          "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                        
                        if all(field in procedure_info for field in procedure_fields):
                            self.log_test("Get Procedure Assignment for View Buttons", True, 
                                        f"View button API working - retrieved full assignment with patient {patient_info.get('firstName', '')} {patient_info.get('lastName', '')} and complete procedure details")
                            return True
                        else:
                            self.log_test("Get Procedure Assignment for View Buttons", False, 
                                        "Missing procedure details required for View page")
                            return False
                    else:
                        self.log_test("Get Procedure Assignment for View Buttons", False, 
                                    "Missing required keys in assignment response")
                        return False
                else:
                    self.log_test("Get Procedure Assignment for View Buttons", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedure Assignment for View Buttons", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedure Assignment for View Buttons", False, f"Exception: {str(e)}")
            return False

    def test_procedure_search_for_library(self):
        """Test procedure search functionality for document library"""
        try:
            # Test search functionality that would be used in procedure library
            response = self.session.get(f"{self.base_url}/procedures/search?q=root")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    if len(procedures) > 0:
                        self.log_test("Procedure Search for Library", True, 
                                    f"Search functionality working - found {len(procedures)} procedures matching 'root'")
                        return True
                    else:
                        self.log_test("Procedure Search for Library", False, "No search results found")
                        return False
                else:
                    self.log_test("Procedure Search for Library", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Search for Library", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Search for Library", False, f"Exception: {str(e)}")
            return False

    def test_procedure_detail_for_library(self):
        """Test individual procedure detail endpoint for library document viewing"""
        try:
            # Test getting detailed procedure information for library document viewing
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    # Check for all fields needed for document library PDF generation
                    required_fields = ["id", "name", "specialty", "specialtyName", "duration", 
                                     "overview", "immediateAftercare", "dietRestrictions", 
                                     "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                    
                    if all(field in procedure for field in required_fields):
                        self.log_test("Procedure Detail for Library", True, 
                                    f"Procedure detail API working - retrieved complete information for {procedure.get('name', '')} with all required fields for PDF generation")
                        return True
                    else:
                        missing_fields = [f for f in required_fields if f not in procedure]
                        self.log_test("Procedure Detail for Library", False, 
                                    f"Missing fields required for library: {missing_fields}")
                        return False
                else:
                    self.log_test("Procedure Detail for Library", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Detail for Library", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Detail for Library", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all new feature tests"""
        print("🧪 TESTING NEW DOCUMENT LIBRARY AND PATIENT EDITING FEATURES")
        print("=" * 70)
        
        # Test authentication first
        if not self.test_practice_login():
            print("\n❌ Cannot proceed without authentication")
            return False
        
        print("\n📋 TESTING PATIENT EDITING FUNCTIONALITY:")
        print("-" * 50)
        self.test_update_patient_api()
        self.test_get_patients_still_works()
        
        print("\n📚 TESTING PROCEDURE LIBRARY FUNCTIONALITY:")
        print("-" * 50)
        self.test_get_procedures_for_library()
        self.test_get_specialties_for_library()
        self.test_procedure_search_for_library()
        self.test_procedure_detail_for_library()
        
        print("\n👁️ TESTING VIEW BUTTON FUNCTIONALITY:")
        print("-" * 50)
        self.test_get_procedure_assignment_for_view_buttons()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY:")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        return failed_tests == 0

def main():
    """Main function to run the tests"""
    print("🚀 Starting New Features Backend API Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print()
    
    tester = NewFeaturesTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All tests passed! New features are working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()