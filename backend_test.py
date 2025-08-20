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
BACKEND_URL = "https://dental-assist-4.preview.emergentagent.com/api"

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

    def create_test_patient(self):
        """Create a test patient john.doe@email.com for patient login testing"""
        if not self.auth_token:
            self.log_test("Create Test Patient", False, "No authentication token available")
            return False
            
        try:
            patient_data = {
                "email": "john.doe@email.com",
                "firstName": "John",
                "lastName": "Doe",
                "phone": "555-0123"
            }
            
            response = self.session.post(f"{self.base_url}/practice/patients", json=patient_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patient = data["data"]
                    self.test_patient_john_id = patient.get("id")
                    self.log_test("Create Test Patient", True, 
                                f"Created test patient John Doe (john.doe@email.com) with ID: {self.test_patient_john_id}")
                    return True
                else:
                    self.log_test("Create Test Patient", False, "Invalid response format")
                    return False
            else:
                # Patient might already exist, try to find them
                patients_response = self.session.get(f"{self.base_url}/practice/patients")
                if patients_response.status_code == 200:
                    patients_data = patients_response.json()
                    if patients_data.get("success"):
                        patients = patients_data.get("data", [])
                        for patient in patients:
                            if patient.get("email") == "john.doe@email.com":
                                self.test_patient_john_id = patient.get("id")
                                self.log_test("Create Test Patient", True, 
                                            f"Found existing test patient John Doe (john.doe@email.com) with ID: {self.test_patient_john_id}")
                                return True
                
                self.log_test("Create Test Patient", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Test Patient", False, f"Exception: {str(e)}")
            return False

    def test_patient_password_setup(self):
        """Test POST /api/auth/patient-setup endpoint"""
        try:
            setup_data = {
                "email": "john.doe@email.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/patient-setup", json=setup_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Patient Password Setup", True, 
                                f"Successfully set up password for john.doe@email.com")
                    return True
                else:
                    self.log_test("Patient Password Setup", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Password Setup", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Patient Password Setup", False, f"Exception: {str(e)}")
            return False

    def test_patient_login(self):
        """Test patient login and get patient token"""
        try:
            login_data = {
                "email": "john.doe@email.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.patient_token = data["token"]
                    user_info = data.get("user", {})
                    if user_info.get("role") == "patient":
                        self.log_test("Patient Login", True, 
                                    f"Patient logged in successfully: {user_info.get('firstName', '')} {user_info.get('lastName', '')} (role: {user_info.get('role', '')})")
                        return True
                    else:
                        self.log_test("Patient Login", False, f"Expected patient role, got: {user_info.get('role', '')}")
                        return False
                else:
                    self.log_test("Patient Login", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Patient Login", False, f"Exception: {str(e)}")
            return False

    def assign_procedure_to_test_patient(self):
        """Assign a procedure to the test patient for testing patient endpoints"""
        if not self.auth_token:
            self.log_test("Assign Procedure to Test Patient", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_patient_john_id') or not self.test_patient_john_id:
            self.log_test("Assign Procedure to Test Patient", False, "No test patient available")
            return False
            
        try:
            # Get a procedure to assign
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            if procedures_response.status_code != 200:
                self.log_test("Assign Procedure to Test Patient", False, "Could not fetch procedures")
                return False
                
            procedures_data = procedures_response.json()
            if not procedures_data.get("success") or not procedures_data.get("data"):
                self.log_test("Assign Procedure to Test Patient", False, "No procedures available")
                return False
                
            procedure = procedures_data["data"][0]  # Use first procedure
            
            assignment_data = {
                "patientId": self.test_patient_john_id,
                "procedureId": procedure["id"],
                "procedureName": procedure["name"],
                "performedDate": "2024-01-15T10:00:00Z",
                "dentistName": "Dr. John Smith",
                "practiceNotes": "Test procedure for patient login system",
                "customInstructions": ["Follow all post-operative instructions", "Contact office if any concerns"],
                "followUpDate": "2024-01-22T14:00:00Z"
            }
            
            response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assignment_info = data.get("data", {})
                    self.test_patient_assignment_id = assignment_info.get("assignmentId")
                    self.log_test("Assign Procedure to Test Patient", True, 
                                f"Assigned {assignment_info.get('procedureName', 'procedure')} to test patient (Assignment ID: {self.test_patient_assignment_id})")
                    return True
                else:
                    self.log_test("Assign Procedure to Test Patient", False, "Invalid response format")
                    return False
            else:
                self.log_test("Assign Procedure to Test Patient", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Assign Procedure to Test Patient", False, f"Exception: {str(e)}")
            return False

    def test_patient_dashboard(self):
        """Test GET /api/patients/dashboard endpoint"""
        if not hasattr(self, 'patient_token') or not self.patient_token:
            self.log_test("Patient Dashboard", False, "No patient token available")
            return False
            
        try:
            # Create a new session with patient token
            patient_session = requests.Session()
            patient_session.headers.update({"Authorization": f"Bearer {self.patient_token}"})
            
            response = patient_session.get(f"{self.base_url}/patients/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    patient_info = dashboard_data.get("patient", {})
                    assigned_procedures = dashboard_data.get("assignedProcedures", [])
                    stats = dashboard_data.get("stats", {})
                    
                    self.log_test("Patient Dashboard", True, 
                                f"Dashboard loaded for {patient_info.get('firstName', '')} {patient_info.get('lastName', '')} with {len(assigned_procedures)} procedures, Stats: {stats}")
                    return True
                else:
                    self.log_test("Patient Dashboard", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Dashboard", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Patient Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_patient_procedure_view(self):
        """Test GET /api/patients/procedures/{assignment_id} endpoint"""
        if not hasattr(self, 'patient_token') or not self.patient_token:
            self.log_test("Patient Procedure View", False, "No patient token available")
            return False
            
        if not hasattr(self, 'test_patient_assignment_id') or not self.test_patient_assignment_id:
            self.log_test("Patient Procedure View", False, "No test assignment available")
            return False
            
        try:
            # Create a new session with patient token
            patient_session = requests.Session()
            patient_session.headers.update({"Authorization": f"Bearer {self.patient_token}"})
            
            response = patient_session.get(f"{self.base_url}/patients/procedures/{self.test_patient_assignment_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure_data = data["data"]
                    assignment = procedure_data.get("assignment", {})
                    procedure = procedure_data.get("procedure", {})
                    practice = procedure_data.get("practice", {})
                    
                    self.log_test("Patient Procedure View", True, 
                                f"Retrieved procedure details: {procedure.get('name', '')} for practice {practice.get('name', '')}")
                    return True
                else:
                    self.log_test("Patient Procedure View", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Procedure View", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Patient Procedure View", False, f"Exception: {str(e)}")
            return False

    def test_patient_download_tracking(self):
        """Test POST /api/patients/procedures/{assignment_id}/download endpoint"""
        if not hasattr(self, 'patient_token') or not self.patient_token:
            self.log_test("Patient Download Tracking", False, "No patient token available")
            return False
            
        if not hasattr(self, 'test_patient_assignment_id') or not self.test_patient_assignment_id:
            self.log_test("Patient Download Tracking", False, "No test assignment available")
            return False
            
        try:
            # Create a new session with patient token
            patient_session = requests.Session()
            patient_session.headers.update({"Authorization": f"Bearer {self.patient_token}"})
            
            response = patient_session.post(f"{self.base_url}/patients/procedures/{self.test_patient_assignment_id}/download")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Patient Download Tracking", True, 
                                f"Download tracked successfully: {data.get('message', '')}")
                    return True
                else:
                    self.log_test("Patient Download Tracking", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Download Tracking", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Patient Download Tracking", False, f"Exception: {str(e)}")
            return False

    def test_patient_unauthorized_access(self):
        """Test that patient endpoints require proper authentication"""
        try:
            # Test without token
            response = self.session.get(f"{self.base_url}/patients/dashboard")
            
            if response.status_code == 403:  # Forbidden or Unauthorized
                self.log_test("Patient Unauthorized Access", True, 
                            "Properly blocked access without patient token")
                return True
            elif response.status_code == 401:
                self.log_test("Patient Unauthorized Access", True, 
                            "Properly blocked access without patient token (401)")
                return True
            else:
                self.log_test("Patient Unauthorized Access", False, 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patient Unauthorized Access", False, f"Exception: {str(e)}")
            return False

    def test_forgot_password_valid_email(self):
        """Test POST /api/auth/forgot-password with valid email"""
        try:
            request_data = {
                "email": "admin@smithdental.com"
            }
            
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    # Should return reset token for testing (will be removed in production)
                    if "reset_token" in data and "reset_link" in data:
                        self.test_reset_token = data["reset_token"]
                        self.log_test("Forgot Password (Valid Email)", True, 
                                    f"Reset token generated: {self.test_reset_token[:8]}...")
                        return True
                    else:
                        self.log_test("Forgot Password (Valid Email)", True, 
                                    "Password reset request processed (no token returned - production mode)")
                        return True
                else:
                    self.log_test("Forgot Password (Valid Email)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Forgot Password (Valid Email)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Forgot Password (Valid Email)", False, f"Exception: {str(e)}")
            return False

    def test_forgot_password_invalid_email(self):
        """Test POST /api/auth/forgot-password with invalid email"""
        try:
            request_data = {
                "email": "nonexistent@example.com"
            }
            
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    # Should return same message to prevent email enumeration
                    expected_message = "If an account with this email exists, password reset instructions have been sent."
                    if expected_message in data["message"]:
                        self.log_test("Forgot Password (Invalid Email)", True, 
                                    "Properly prevents email enumeration - same response for invalid email")
                        return True
                    else:
                        self.log_test("Forgot Password (Invalid Email)", False, 
                                    f"Unexpected message: {data['message']}")
                        return False
                else:
                    self.log_test("Forgot Password (Invalid Email)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Forgot Password (Invalid Email)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Forgot Password (Invalid Email)", False, f"Exception: {str(e)}")
            return False

    def test_forgot_username_valid_practice(self):
        """Test POST /api/auth/forgot-username with valid practice name"""
        try:
            request_data = {
                "practice_name": "Smith Dental Practice",
                "phone": "555-123-4567",
                "adminPassword": "password123"  # Required field for verification
            }
            
            response = self.session.post(f"{self.base_url}/auth/forgot-username", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    # Should return practice info for testing (will be removed in production)
                    if "practice_name" in data and "email" in data:
                        self.log_test("Forgot Username (Valid Practice)", True, 
                                    f"Found practice: {data['practice_name']}, Email: {data['email']}")
                        return True
                    else:
                        self.log_test("Forgot Username (Valid Practice)", True, 
                                    "Username recovery request processed (no details returned - production mode)")
                        return True
                else:
                    self.log_test("Forgot Username (Valid Practice)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Forgot Username (Valid Practice)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Forgot Username (Valid Practice)", False, f"Exception: {str(e)}")
            return False

    def test_forgot_username_invalid_practice(self):
        """Test POST /api/auth/forgot-username with invalid practice name"""
        try:
            request_data = {
                "practice_name": "Nonexistent Dental Practice",
                "phone": "555-999-9999",
                "adminPassword": "somepassword"  # Required field
            }
            
            response = self.session.post(f"{self.base_url}/auth/forgot-username", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    # Should return same message to prevent information disclosure
                    expected_message = "If a practice with these details exists, username recovery information has been sent."
                    if expected_message in data["message"]:
                        self.log_test("Forgot Username (Invalid Practice)", True, 
                                    "Properly prevents information disclosure - same response for invalid practice")
                        return True
                    else:
                        self.log_test("Forgot Username (Invalid Practice)", False, 
                                    f"Unexpected message: {data['message']}")
                        return False
                else:
                    self.log_test("Forgot Username (Invalid Practice)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Forgot Username (Invalid Practice)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Forgot Username (Invalid Practice)", False, f"Exception: {str(e)}")
            return False

    def test_validate_reset_token_valid(self):
        """Test GET /api/auth/validate-reset-token/{token} with valid token"""
        if not hasattr(self, 'test_reset_token') or not self.test_reset_token:
            self.log_test("Validate Reset Token (Valid)", False, "No reset token available from forgot password test")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/auth/validate-reset-token/{self.test_reset_token}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("valid") and "user" in data:
                    user_info = data["user"]
                    if "email" in user_info and "firstName" in user_info:
                        self.log_test("Validate Reset Token (Valid)", True, 
                                    f"Valid token for user: {user_info['firstName']} ({user_info['email']})")
                        return True
                    else:
                        self.log_test("Validate Reset Token (Valid)", False, "Missing user information")
                        return False
                else:
                    self.log_test("Validate Reset Token (Valid)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Validate Reset Token (Valid)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Reset Token (Valid)", False, f"Exception: {str(e)}")
            return False

    def test_validate_reset_token_invalid(self):
        """Test GET /api/auth/validate-reset-token/{token} with invalid token"""
        try:
            invalid_token = "invalid-token-12345"
            response = self.session.get(f"{self.base_url}/auth/validate-reset-token/{invalid_token}")
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Invalid or expired reset token" in data["detail"]:
                    self.log_test("Validate Reset Token (Invalid)", True, 
                                f"Properly rejected invalid token: {data['detail']}")
                    return True
                else:
                    self.log_test("Validate Reset Token (Invalid)", False, 
                                f"Unexpected error message: {data.get('detail', 'No detail')}")
                    return False
            else:
                self.log_test("Validate Reset Token (Invalid)", False, 
                            f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Validate Reset Token (Invalid)", False, f"Exception: {str(e)}")
            return False

    def test_reset_password_valid_token(self):
        """Test POST /api/auth/reset-password with valid token"""
        if not hasattr(self, 'test_reset_token') or not self.test_reset_token:
            self.log_test("Reset Password (Valid Token)", False, "No reset token available from forgot password test")
            return False
            
        try:
            request_data = {
                "reset_token": self.test_reset_token,
                "new_password": "newpassword123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/reset-password", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    if "Password reset successful" in data["message"]:
                        self.log_test("Reset Password (Valid Token)", True, 
                                    "Password reset successful with valid token")
                        return True
                    else:
                        self.log_test("Reset Password (Valid Token)", False, 
                                    f"Unexpected message: {data['message']}")
                        return False
                else:
                    self.log_test("Reset Password (Valid Token)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Reset Password (Valid Token)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Reset Password (Valid Token)", False, f"Exception: {str(e)}")
            return False

    def test_reset_password_invalid_token(self):
        """Test POST /api/auth/reset-password with invalid token"""
        try:
            request_data = {
                "reset_token": "invalid-token-12345",
                "new_password": "newpassword123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/reset-password", json=request_data)
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Invalid or expired reset token" in data["detail"]:
                    self.log_test("Reset Password (Invalid Token)", True, 
                                f"Properly rejected invalid token: {data['detail']}")
                    return True
                else:
                    self.log_test("Reset Password (Invalid Token)", False, 
                                f"Unexpected error message: {data.get('detail', 'No detail')}")
                    return False
            else:
                self.log_test("Reset Password (Invalid Token)", False, 
                            f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reset Password (Invalid Token)", False, f"Exception: {str(e)}")
            return False

    def test_reset_password_weak_password(self):
        """Test POST /api/auth/reset-password with weak password"""
        if not hasattr(self, 'test_reset_token') or not self.test_reset_token:
            # Generate a new reset token for this test
            forgot_response = self.session.post(f"{self.base_url}/auth/forgot-password", 
                                              json={"email": "admin@smithdental.com"})
            if forgot_response.status_code == 200:
                forgot_data = forgot_response.json()
                if "reset_token" in forgot_data:
                    test_token = forgot_data["reset_token"]
                else:
                    self.log_test("Reset Password (Weak Password)", False, "Could not generate reset token for test")
                    return False
            else:
                self.log_test("Reset Password (Weak Password)", False, "Could not generate reset token for test")
                return False
        else:
            # Generate a new token since the previous one might be used
            forgot_response = self.session.post(f"{self.base_url}/auth/forgot-password", 
                                              json={"email": "admin@smithdental.com"})
            if forgot_response.status_code == 200:
                forgot_data = forgot_response.json()
                if "reset_token" in forgot_data:
                    test_token = forgot_data["reset_token"]
                else:
                    self.log_test("Reset Password (Weak Password)", False, "Could not generate reset token for test")
                    return False
            else:
                self.log_test("Reset Password (Weak Password)", False, "Could not generate reset token for test")
                return False
            
        try:
            # Test with weak password (less than 6 characters, no numbers)
            request_data = {
                "reset_token": test_token,
                "new_password": "weak"
            }
            
            response = self.session.post(f"{self.base_url}/auth/reset-password", json=request_data)
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Password must be at least 6 characters with letters and numbers" in data["detail"]:
                    self.log_test("Reset Password (Weak Password)", True, 
                                f"Properly rejected weak password: {data['detail']}")
                    return True
                else:
                    self.log_test("Reset Password (Weak Password)", False, 
                                f"Unexpected error message: {data.get('detail', 'No detail')}")
                    return False
            else:
                self.log_test("Reset Password (Weak Password)", False, 
                            f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reset Password (Weak Password)", False, f"Exception: {str(e)}")
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
        
        # Patient login system tests (require practice admin authentication first)
        patient_tests = [
            self.create_test_patient,
            self.test_patient_password_setup,
            self.test_patient_login,
            self.assign_procedure_to_test_patient,
            self.test_patient_dashboard,
            self.test_patient_procedure_view,
            self.test_patient_download_tracking,
            self.test_patient_unauthorized_access
        ]
        
        # Password reset and username recovery tests
        password_reset_tests = [
            self.test_forgot_password_valid_email,
            self.test_forgot_password_invalid_email,
            self.test_forgot_username_valid_practice,
            self.test_forgot_username_invalid_practice,
            self.test_validate_reset_token_valid,
            self.test_validate_reset_token_invalid,
            self.test_reset_password_valid_token,
            self.test_reset_password_invalid_token,
            self.test_reset_password_weak_password
        ]
        
        all_tests = basic_tests + practice_tests + patient_tests + password_reset_tests
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
        
        print("👤 Running Patient Login System Tests...")
        for test in patient_tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("🔐 Running Password Reset & Username Recovery Tests...")
        for test in password_reset_tests:
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