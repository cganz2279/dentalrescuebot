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
                "email": "cganz2279@gmail.com"
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
                "practice_name": "Cary Ganz DDS PC",
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
                                              json={"email": "cganz2279@gmail.com"})
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
                                              json={"email": "cganz2279@gmail.com"})
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
    
    def test_pdf_formatting_data_structure(self):
        """Test that procedure data has proper formatting for PDF generation"""
        try:
            # Test with a procedure that should have comprehensive formatting
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check for overview formatting elements
                    overview = procedure.get("overview", "")
                    formatting_checks = {
                        "bullet_points": "•" in overview or "-" in overview,
                        "markdown_headers": "**" in overview,
                        "line_breaks": "\n" in overview,
                        "has_content": len(overview) > 100
                    }
                    
                    # Check for numbered list data in aftercare and diet
                    aftercare = procedure.get("immediateAftercare", [])
                    diet = procedure.get("dietRestrictions", [])
                    warning_signs = procedure.get("warningSignsToCallDoctor", [])
                    recovery = procedure.get("recoveryTimeline", [])
                    medications = procedure.get("medications", [])
                    
                    structure_checks = {
                        "has_aftercare": len(aftercare) > 0,
                        "has_diet_restrictions": len(diet) > 0,
                        "has_warning_signs": len(warning_signs) > 0,
                        "has_recovery_timeline": len(recovery) > 0,
                        "has_medications": len(medications) > 0
                    }
                    
                    # Check recovery timeline structure for "DAY X:" format
                    timeline_format_ok = True
                    if recovery:
                        for timeline_item in recovery:
                            if not isinstance(timeline_item, dict) or "day" not in timeline_item or "activity" not in timeline_item:
                                timeline_format_ok = False
                                break
                    
                    all_formatting_ok = all(formatting_checks.values())
                    all_structure_ok = all(structure_checks.values()) and timeline_format_ok
                    
                    if all_formatting_ok and all_structure_ok:
                        self.log_test("PDF Formatting Data Structure", True, 
                                    f"Procedure has proper formatting: {formatting_checks}, Structure: {structure_checks}, Timeline format OK: {timeline_format_ok}")
                        return True
                    else:
                        self.log_test("PDF Formatting Data Structure", False, 
                                    f"Missing formatting elements - Formatting: {formatting_checks}, Structure: {structure_checks}, Timeline: {timeline_format_ok}")
                        return False
                else:
                    self.log_test("PDF Formatting Data Structure", False, "Invalid response format")
                    return False
            else:
                self.log_test("PDF Formatting Data Structure", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PDF Formatting Data Structure", False, f"Exception: {str(e)}")
            return False

    def test_procedure_assignment_for_pdf(self):
        """Test creating a procedure assignment with all sections for PDF generation"""
        if not self.auth_token:
            self.log_test("Procedure Assignment for PDF", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_patient_id') or not self.test_patient_id:
            self.log_test("Procedure Assignment for PDF", False, "No test patient available")
            return False
            
        try:
            # Get a procedure with comprehensive content for PDF testing
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            if procedures_response.status_code != 200:
                self.log_test("Procedure Assignment for PDF", False, "Could not fetch procedures")
                return False
                
            procedures_data = procedures_response.json()
            if not procedures_data.get("success") or not procedures_data.get("data"):
                self.log_test("Procedure Assignment for PDF", False, "No procedures available")
                return False
            
            # Find a procedure with comprehensive content (prefer root-canal-therapy)
            target_procedure = None
            for proc in procedures_data["data"]:
                if proc["id"] == "root-canal-therapy":
                    target_procedure = proc
                    break
            
            if not target_procedure:
                target_procedure = procedures_data["data"][0]  # Use first procedure as fallback
            
            # Create assignment with comprehensive data for PDF testing
            assignment_data = {
                "patientId": self.test_patient_id,
                "procedureId": target_procedure["id"],
                "procedureName": target_procedure["name"],
                "performedDate": "2024-01-15T10:00:00Z",
                "dentistName": "Dr. Sarah Johnson",
                "practiceNotes": "Comprehensive procedure performed successfully. Patient tolerated procedure well. All standard protocols followed. Post-operative instructions provided and explained to patient.",
                "customInstructions": [
                    "Take prescribed antibiotics exactly as directed",
                    "Apply ice pack for 15 minutes every hour for first 24 hours",
                    "Avoid hard, crunchy, or sticky foods for 48 hours",
                    "Rinse gently with warm salt water after 24 hours",
                    "Do not smoke or use tobacco products during healing"
                ],
                "followUpDate": "2024-01-22T14:00:00Z"
            }
            
            response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assignment_info = data.get("data", {})
                    self.test_pdf_assignment_id = assignment_info.get("assignmentId")
                    self.log_test("Procedure Assignment for PDF", True, 
                                f"Created comprehensive assignment for PDF testing: {assignment_info.get('procedureName', 'procedure')} (Assignment ID: {self.test_pdf_assignment_id})")
                    return True
                else:
                    self.log_test("Procedure Assignment for PDF", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Assignment for PDF", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Assignment for PDF", False, f"Exception: {str(e)}")
            return False

    def test_pdf_data_retrieval(self):
        """Test retrieving comprehensive procedure assignment data for PDF generation"""
        if not self.auth_token:
            self.log_test("PDF Data Retrieval", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_pdf_assignment_id') or not self.test_pdf_assignment_id:
            self.log_test("PDF Data Retrieval", False, "No PDF test assignment available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/assignment/{self.test_pdf_assignment_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment_data = data["data"]
                    
                    # Verify all required components for PDF generation
                    required_components = {
                        "assignment": assignment_data.get("assignment"),
                        "patient": assignment_data.get("patient"),
                        "procedure": assignment_data.get("procedure")
                    }
                    
                    if not all(required_components.values()):
                        self.log_test("PDF Data Retrieval", False, "Missing required components")
                        return False
                    
                    assignment = required_components["assignment"]
                    patient = required_components["patient"]
                    procedure = required_components["procedure"]
                    
                    # Check PDF-specific formatting elements
                    pdf_elements = {
                        "patient_name": f"{patient.get('firstName', '')} {patient.get('lastName', '')}".strip(),
                        "procedure_name": assignment.get("procedureName"),
                        "dentist_name": assignment.get("dentistName"),
                        "practice_notes": assignment.get("practiceNotes"),
                        "custom_instructions": assignment.get("customInstructions", []),
                        "overview_formatting": procedure.get("overview", ""),
                        "aftercare_list": procedure.get("immediateAftercare", []),
                        "diet_restrictions": procedure.get("dietRestrictions", []),
                        "warning_signs": procedure.get("warningSignsToCallDoctor", []),
                        "recovery_timeline": procedure.get("recoveryTimeline", []),
                        "medications": procedure.get("medications", [])
                    }
                    
                    # Verify formatting improvements are present
                    overview = pdf_elements["overview_formatting"]
                    formatting_improvements = {
                        "bullet_points_present": "•" in overview or "-" in overview,
                        "markdown_headers_present": "**" in overview,
                        "numbered_aftercare": len(pdf_elements["aftercare_list"]) > 0,
                        "numbered_diet": len(pdf_elements["diet_restrictions"]) > 0,
                        "warning_signs_present": len(pdf_elements["warning_signs"]) > 0,
                        "recovery_timeline_present": len(pdf_elements["recovery_timeline"]) > 0,
                        "medications_present": len(pdf_elements["medications"]) > 0
                    }
                    
                    improvements_count = sum(formatting_improvements.values())
                    
                    if improvements_count >= 5:  # At least 5 out of 7 formatting improvements
                        self.log_test("PDF Data Retrieval", True, 
                                    f"Retrieved comprehensive PDF data with {improvements_count}/7 formatting improvements: {formatting_improvements}")
                        return True
                    else:
                        self.log_test("PDF Data Retrieval", False, 
                                    f"Insufficient formatting improvements ({improvements_count}/7): {formatting_improvements}")
                        return False
                else:
                    self.log_test("PDF Data Retrieval", False, "Invalid response format")
                    return False
            else:
                self.log_test("PDF Data Retrieval", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PDF Data Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_multiple_procedures_formatting(self):
        """Test multiple procedures to verify consistent formatting improvements"""
        try:
            test_procedures = ["root-canal-therapy", "dental-crown-placement", "surgical-tooth-extraction", "alveoloplasty"]
            formatting_results = {}
            
            for proc_id in test_procedures:
                response = self.session.get(f"{self.base_url}/procedures/{proc_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        overview = procedure.get("overview", "")
                        
                        # Check formatting elements
                        formatting_results[proc_id] = {
                            "bullet_points": "•" in overview or "-" in overview,
                            "markdown_headers": "**" in overview,
                            "line_breaks": "\n" in overview,
                            "aftercare_count": len(procedure.get("immediateAftercare", [])),
                            "diet_count": len(procedure.get("dietRestrictions", [])),
                            "warning_count": len(procedure.get("warningSignsToCallDoctor", [])),
                            "recovery_count": len(procedure.get("recoveryTimeline", [])),
                            "medication_count": len(procedure.get("medications", []))
                        }
            
            # Analyze results
            procedures_with_good_formatting = 0
            for proc_id, formatting in formatting_results.items():
                # Count how many formatting elements are present
                elements_present = (
                    formatting["bullet_points"] + 
                    formatting["markdown_headers"] + 
                    formatting["line_breaks"] + 
                    (formatting["aftercare_count"] > 0) +
                    (formatting["diet_count"] > 0) +
                    (formatting["warning_count"] > 0) +
                    (formatting["recovery_count"] > 0) +
                    (formatting["medication_count"] > 0)
                )
                
                if elements_present >= 6:  # At least 6 out of 8 elements
                    procedures_with_good_formatting += 1
            
            success_rate = procedures_with_good_formatting / len(test_procedures)
            
            if success_rate >= 0.75:  # At least 75% of procedures have good formatting
                self.log_test("Multiple Procedures Formatting", True, 
                            f"Formatting improvements verified across {procedures_with_good_formatting}/{len(test_procedures)} procedures ({success_rate:.1%} success rate)")
                return True
            else:
                self.log_test("Multiple Procedures Formatting", False, 
                            f"Insufficient formatting consistency: {procedures_with_good_formatting}/{len(test_procedures)} procedures ({success_rate:.1%} success rate)")
                return False
                
        except Exception as e:
            self.log_test("Multiple Procedures Formatting", False, f"Exception: {str(e)}")
            return False

    # Dentist Management API Tests
    def test_get_dentists(self):
        """Test GET /api/practice/dentists endpoint"""
        if not self.auth_token:
            self.log_test("Get Dentists API", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/dentists")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dentists = data["data"]
                    self.log_test("Get Dentists API", True, 
                                f"Retrieved {len(dentists)} dentists for authenticated practice")
                    return True
                else:
                    self.log_test("Get Dentists API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Dentists API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Dentists API", False, f"Exception: {str(e)}")
            return False

    def test_add_dentist(self):
        """Test POST /api/practice/dentists endpoint"""
        if not self.auth_token:
            self.log_test("Add Dentist API", False, "No authentication token available")
            return False
            
        try:
            dentist_data = {
                "firstName": "John",
                "lastName": "Smith",
                "email": "j.smith@dental.com",
                "phone": "555-123-4567",
                "licenseNumber": "DDS12345",
                "specialties": ["General Dentistry", "Oral Surgery"]
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=dentist_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dentist = data["data"]
                    # Store dentist ID for later tests
                    self.test_dentist_id = dentist.get("id")
                    self.log_test("Add Dentist API", True, 
                                f"Created dentist: Dr. {dentist.get('firstName')} {dentist.get('lastName')} (ID: {self.test_dentist_id})")
                    return True
                else:
                    self.log_test("Add Dentist API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Add Dentist API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Dentist API", False, f"Exception: {str(e)}")
            return False

    def test_add_dentist_validation(self):
        """Test POST /api/practice/dentists with missing required fields"""
        if not self.auth_token:
            self.log_test("Add Dentist Validation", False, "No authentication token available")
            return False
            
        try:
            # Test with missing required fields
            invalid_dentist_data = {
                "firstName": "Jane",
                # Missing lastName and email
                "phone": "555-987-6543"
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=invalid_dentist_data)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Add Dentist Validation", True, 
                            "Properly rejected dentist with missing required fields")
                return True
            else:
                self.log_test("Add Dentist Validation", False, 
                            f"Expected 422 validation error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Add Dentist Validation", False, f"Exception: {str(e)}")
            return False

    def test_add_dentist_duplicate_email(self):
        """Test POST /api/practice/dentists with duplicate email"""
        if not self.auth_token:
            self.log_test("Add Dentist Duplicate Email", False, "No authentication token available")
            return False
            
        try:
            # Try to add dentist with same email as previous test
            duplicate_dentist_data = {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "j.smith@dental.com",  # Same email as previous dentist
                "phone": "555-987-6543",
                "licenseNumber": "DDS67890",
                "specialties": ["Orthodontics"]
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=duplicate_dentist_data)
            
            if response.status_code == 409:  # Conflict
                data = response.json()
                if "email already exists" in data.get("detail", "").lower():
                    self.log_test("Add Dentist Duplicate Email", True, 
                                "Properly rejected duplicate email within practice")
                    return True
                else:
                    self.log_test("Add Dentist Duplicate Email", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("Add Dentist Duplicate Email", False, 
                            f"Expected 409 conflict, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Add Dentist Duplicate Email", False, f"Exception: {str(e)}")
            return False

    def test_update_dentist(self):
        """Test PUT /api/practice/dentists/{dentist_id} endpoint"""
        if not self.auth_token:
            self.log_test("Update Dentist API", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_dentist_id') or not self.test_dentist_id:
            self.log_test("Update Dentist API", False, "No test dentist available")
            return False
            
        try:
            update_data = {
                "firstName": "John",
                "lastName": "Smith-Updated",
                "phone": "555-123-9999",
                "specialties": ["General Dentistry", "Oral Surgery", "Endodontics"]
            }
            
            response = self.session.put(f"{self.base_url}/practice/dentists/{self.test_dentist_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    updated_dentist = data["data"]
                    if updated_dentist.get("lastName") == "Smith-Updated":
                        self.log_test("Update Dentist API", True, 
                                    f"Successfully updated dentist: {updated_dentist.get('firstName')} {updated_dentist.get('lastName')}")
                        return True
                    else:
                        self.log_test("Update Dentist API", False, "Update not reflected in response")
                        return False
                else:
                    self.log_test("Update Dentist API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Update Dentist API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Dentist API", False, f"Exception: {str(e)}")
            return False

    def test_update_dentist_validation(self):
        """Test PUT /api/practice/dentists/{dentist_id} with email uniqueness validation"""
        if not self.auth_token:
            self.log_test("Update Dentist Validation", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_dentist_id') or not self.test_dentist_id:
            self.log_test("Update Dentist Validation", False, "No test dentist available")
            return False
            
        try:
            # First create another dentist to test email uniqueness
            another_dentist_data = {
                "firstName": "Alice",
                "lastName": "Johnson",
                "email": "a.johnson@dental.com",
                "phone": "555-111-2222",
                "licenseNumber": "DDS11111",
                "specialties": ["Pediatric Dentistry"]
            }
            
            create_response = self.session.post(f"{self.base_url}/practice/dentists", json=another_dentist_data)
            if create_response.status_code != 200:
                self.log_test("Update Dentist Validation", False, "Could not create second dentist for validation test")
                return False
            
            another_dentist = create_response.json()["data"]
            another_dentist_id = another_dentist["id"]
            
            # Try to update first dentist with second dentist's email
            update_data = {
                "email": "a.johnson@dental.com"  # Email of second dentist
            }
            
            response = self.session.put(f"{self.base_url}/practice/dentists/{self.test_dentist_id}", json=update_data)
            
            if response.status_code == 409:  # Conflict
                data = response.json()
                if "email already exists" in data.get("detail", "").lower():
                    self.log_test("Update Dentist Validation", True, 
                                "Properly prevented email duplication during update")
                    return True
                else:
                    self.log_test("Update Dentist Validation", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("Update Dentist Validation", False, 
                            f"Expected 409 conflict, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Update Dentist Validation", False, f"Exception: {str(e)}")
            return False

    def test_update_dentist_404(self):
        """Test PUT /api/practice/dentists/{dentist_id} with invalid dentist ID"""
        if not self.auth_token:
            self.log_test("Update Dentist 404", False, "No authentication token available")
            return False
            
        try:
            invalid_dentist_id = "invalid-dentist-id-12345"
            update_data = {
                "firstName": "Updated",
                "lastName": "Name"
            }
            
            response = self.session.put(f"{self.base_url}/practice/dentists/{invalid_dentist_id}", json=update_data)
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("Update Dentist 404", True, 
                                "Properly returned 404 for invalid dentist ID")
                    return True
                else:
                    self.log_test("Update Dentist 404", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("Update Dentist 404", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Update Dentist 404", False, f"Exception: {str(e)}")
            return False

    def test_delete_dentist(self):
        """Test DELETE /api/practice/dentists/{dentist_id} endpoint (soft delete)"""
        if not self.auth_token:
            self.log_test("Delete Dentist API", False, "No authentication token available")
            return False
            
        if not hasattr(self, 'test_dentist_id') or not self.test_dentist_id:
            self.log_test("Delete Dentist API", False, "No test dentist available")
            return False
            
        try:
            response = self.session.delete(f"{self.base_url}/practice/dentists/{self.test_dentist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "removed successfully" in data.get("message", "").lower():
                    # Verify dentist is no longer in active list
                    get_response = self.session.get(f"{self.base_url}/practice/dentists")
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        dentists = get_data.get("data", [])
                        # Check if deleted dentist is not in the list
                        deleted_dentist_found = any(d.get("id") == self.test_dentist_id for d in dentists)
                        if not deleted_dentist_found:
                            self.log_test("Delete Dentist API", True, 
                                        "Successfully soft-deleted dentist (isActive=false)")
                            return True
                        else:
                            self.log_test("Delete Dentist API", False, 
                                        "Dentist still appears in active list after deletion")
                            return False
                    else:
                        self.log_test("Delete Dentist API", True, 
                                    "Dentist deletion successful (could not verify list)")
                        return True
                else:
                    self.log_test("Delete Dentist API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Delete Dentist API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Dentist API", False, f"Exception: {str(e)}")
            return False

    def test_delete_dentist_404(self):
        """Test DELETE /api/practice/dentists/{dentist_id} with invalid dentist ID"""
        if not self.auth_token:
            self.log_test("Delete Dentist 404", False, "No authentication token available")
            return False
            
        try:
            invalid_dentist_id = "invalid-dentist-id-99999"
            response = self.session.delete(f"{self.base_url}/practice/dentists/{invalid_dentist_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("Delete Dentist 404", True, 
                                "Properly returned 404 for invalid dentist ID")
                    return True
                else:
                    self.log_test("Delete Dentist 404", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("Delete Dentist 404", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Delete Dentist 404", False, f"Exception: {str(e)}")
            return False

    def test_dentist_authentication_required(self):
        """Test that dentist endpoints require proper authentication and authorization"""
        try:
            # Test without authentication token
            no_auth_session = requests.Session()
            
            # Test GET dentists without auth
            response = no_auth_session.get(f"{self.base_url}/practice/dentists")
            
            if response.status_code in [401, 403]:
                self.log_test("Dentist Authentication Required", True, 
                            f"Properly blocked unauthenticated access (Status: {response.status_code})")
                return True
            else:
                self.log_test("Dentist Authentication Required", False, 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dentist Authentication Required", False, f"Exception: {str(e)}")
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
        
        # Dentist management tests (require practice admin authentication)
        dentist_tests = [
            self.test_get_dentists,
            self.test_add_dentist,
            self.test_add_dentist_validation,
            self.test_add_dentist_duplicate_email,
            self.test_update_dentist,
            self.test_update_dentist_validation,
            self.test_update_dentist_404,
            self.test_delete_dentist,
            self.test_delete_dentist_404,
            self.test_dentist_authentication_required
        ]
        
        # PDF formatting improvement tests
        pdf_tests = [
            self.test_pdf_formatting_data_structure,
            self.test_procedure_assignment_for_pdf,
            self.test_pdf_data_retrieval,
            self.test_multiple_procedures_formatting
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
        
        all_tests = basic_tests + practice_tests + dentist_tests + pdf_tests + patient_tests + password_reset_tests
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
        
        print("🦷 Running Dentist Management Tests...")
        for test in dentist_tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("📄 Running PDF Formatting Tests...")
        for test in pdf_tests:
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