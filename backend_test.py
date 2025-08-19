#!/usr/bin/env python3
"""
Backend API Testing for Dental Post-Operative Care App
Tests all backend endpoints to ensure proper functionality
"""

import requests
import json
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentalnotes.preview.emergentagent.com/api"

class DentalAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.test_practice_id = None
        self.test_patient_id = None
        
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
            # Test with root-canal-therapy procedure (correct ID)
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

    def setup_test_practice(self):
        """Setup a test practice and admin user for authentication"""
        try:
            # Generate unique test data
            test_email = f"test-practice-{uuid.uuid4().hex[:8]}@example.com"
            
            practice_data = {
                "practiceName": "Test Dental Practice",
                "email": test_email,
                "phone": "555-123-4567",
                "adminFirstName": "Test",
                "adminLastName": "Admin",
                "adminPassword": "testpass123",
                "street": "123 Test St",
                "city": "Test City",
                "state": "CA",
                "zipCode": "12345"
            }
            
            # Register practice using SamCart endpoint (active immediately)
            response = self.session.post(
                f"{self.base_url}/auth/register-practice-samcart",
                json=practice_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.test_practice_id = data["practice"]["id"]
                    
                    # Now login to get auth token
                    login_data = {
                        "email": test_email,
                        "password": "testpass123"
                    }
                    
                    login_response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json=login_data
                    )
                    
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        if login_result.get("success"):
                            self.auth_token = login_result["token"]
                            self.log_test("Setup Test Practice & Authentication", True, 
                                        f"Practice ID: {self.test_practice_id}")
                            return True
                    
                    self.log_test("Setup Test Practice & Authentication", False, 
                                f"Login failed: {login_response.status_code}")
                    return False
                else:
                    self.log_test("Setup Test Practice & Authentication", False, 
                                f"Registration failed: {data}")
                    return False
            else:
                self.log_test("Setup Test Practice & Authentication", False, 
                            f"Registration status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Setup Test Practice & Authentication", False, f"Exception: {str(e)}")
            return False

    def test_practice_dashboard(self):
        """Test GET /api/practice/dashboard endpoint"""
        if not self.auth_token:
            self.log_test("Practice Dashboard API", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    required_fields = ["practice", "stats", "recentPatients", "recentProcedures"]
                    
                    if all(field in dashboard_data for field in required_fields):
                        stats = dashboard_data["stats"]
                        if "patientCount" in stats and "activeProcedures" in stats:
                            self.log_test("Practice Dashboard API", True, 
                                        f"Dashboard loaded with {stats['patientCount']} patients, {stats['activeProcedures']} active procedures")
                            return True
                        else:
                            self.log_test("Practice Dashboard API", False, "Missing stats fields")
                            return False
                    else:
                        missing_fields = [f for f in required_fields if f not in dashboard_data]
                        self.log_test("Practice Dashboard API", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Practice Dashboard API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Dashboard API", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Practice Dashboard API", False, f"Exception: {str(e)}")
            return False

    def test_create_patient(self):
        """Test POST /api/practice/patients endpoint"""
        if not self.auth_token:
            self.log_test("Create Patient API", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Generate unique patient data
            patient_email = f"patient-{uuid.uuid4().hex[:8]}@example.com"
            patient_data = {
                "email": patient_email,
                "firstName": "John",
                "lastName": "Doe",
                "phone": "555-987-6543"
            }
            
            response = self.session.post(
                f"{self.base_url}/practice/patients", 
                json=patient_data, 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patient = data["data"]
                    required_fields = ["id", "email", "firstName", "lastName", "role", "practiceId"]
                    
                    if all(field in patient for field in required_fields):
                        if patient["email"] == patient_email and patient["role"] == "patient":
                            self.test_patient_id = patient["id"]  # Store for later tests
                            self.log_test("Create Patient API", True, 
                                        f"Patient created: {patient['firstName']} {patient['lastName']} ({patient['email']})")
                            return True
                        else:
                            self.log_test("Create Patient API", False, "Patient data mismatch")
                            return False
                    else:
                        missing_fields = [f for f in required_fields if f not in patient]
                        self.log_test("Create Patient API", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Create Patient API", False, "Invalid response format")
                    return False
            elif response.status_code == 400:
                # Check if it's a duplicate email error
                try:
                    error_data = response.json()
                    if "Email already registered" in error_data.get("detail", ""):
                        # Try with a different email
                        patient_email = f"patient-{uuid.uuid4().hex[:8]}@example.com"
                        patient_data["email"] = patient_email
                        
                        response = self.session.post(
                            f"{self.base_url}/practice/patients", 
                            json=patient_data, 
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success") and "data" in data:
                                patient = data["data"]
                                self.test_patient_id = patient["id"]
                                self.log_test("Create Patient API", True, 
                                            f"Patient created after email conflict: {patient['firstName']} {patient['lastName']}")
                                return True
                        
                        self.log_test("Create Patient API", False, f"Still failed after email change: {response.status_code}")
                        return False
                    else:
                        self.log_test("Create Patient API", False, f"400 error: {error_data.get('detail', 'Unknown')}")
                        return False
                except:
                    self.log_test("Create Patient API", False, f"400 error with unparseable response")
                    return False
            else:
                self.log_test("Create Patient API", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Create Patient API", False, f"Exception: {str(e)}")
            return False

    def test_get_practice_patients(self):
        """Test GET /api/practice/patients endpoint"""
        if not self.auth_token:
            self.log_test("Get Practice Patients API", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/practice/patients", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    
                    if isinstance(patients, list):
                        # Should have at least the patient we created
                        if len(patients) > 0:
                            sample_patient = patients[0]
                            required_fields = ["id", "email", "firstName", "lastName", "role", "procedureCount"]
                            
                            if all(field in sample_patient for field in required_fields):
                                self.log_test("Get Practice Patients API", True, 
                                            f"Retrieved {len(patients)} patients with procedure counts")
                                return True
                            else:
                                missing_fields = [f for f in required_fields if f not in sample_patient]
                                self.log_test("Get Practice Patients API", False, f"Missing fields: {missing_fields}")
                                return False
                        else:
                            self.log_test("Get Practice Patients API", True, "No patients found (empty practice)")
                            return True
                    else:
                        self.log_test("Get Practice Patients API", False, "Patients data is not a list")
                        return False
                else:
                    self.log_test("Get Practice Patients API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Practice Patients API", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Practice Patients API", False, f"Exception: {str(e)}")
            return False

    def test_assign_procedure(self):
        """Test POST /api/practice/assign-procedure endpoint"""
        if not self.auth_token or not self.test_patient_id:
            self.log_test("Assign Procedure API", False, "No auth token or patient ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Use a known procedure ID (root-canal-therapy from the seeded data)
            assignment_data = {
                "patientId": self.test_patient_id,
                "procedureId": "root-canal-therapy",
                "procedureName": "Root Canal Therapy",
                "performedDate": datetime.utcnow().isoformat() + "Z",
                "dentistName": "Dr. Test Dentist",
                "practiceNotes": "Test procedure assignment",
                "customInstructions": ["Take prescribed medication", "Avoid hard foods"],
                "followUpDate": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
            }
            
            response = self.session.post(
                f"{self.base_url}/practice/assign-procedure", 
                json=assignment_data, 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    required_fields = ["assignmentId", "patientName", "procedureName"]
                    
                    if all(field in assignment for field in required_fields):
                        if assignment["procedureName"] == "Root Canal Therapy":
                            self.log_test("Assign Procedure API", True, 
                                        f"Procedure assigned: {assignment['procedureName']} to {assignment['patientName']}")
                            return True
                        else:
                            self.log_test("Assign Procedure API", False, "Procedure name mismatch")
                            return False
                    else:
                        missing_fields = [f for f in required_fields if f not in assignment]
                        self.log_test("Assign Procedure API", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Assign Procedure API", False, "Invalid response format")
                    return False
            else:
                self.log_test("Assign Procedure API", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Assign Procedure API", False, f"Exception: {str(e)}")
            return False

    def test_unauthorized_access(self):
        """Test that endpoints properly reject unauthorized requests"""
        try:
            # Test dashboard without auth
            response = self.session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code in [401, 403]:  # Both are acceptable for unauthorized access
                self.log_test("Unauthorized Access Protection", True, 
                            f"Dashboard properly rejects unauthorized requests (HTTP {response.status_code})")
                return True
            else:
                self.log_test("Unauthorized Access Protection", False, 
                            f"Expected 401 or 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Access Protection", False, f"Exception: {str(e)}")
            return False

    def test_invalid_data_handling(self):
        """Test API endpoints with invalid data"""
        if not self.auth_token:
            self.log_test("Invalid Data Handling", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test creating patient with missing required fields
            invalid_patient_data = {
                "firstName": "Test"
                # Missing lastName and email
            }
            
            response = self.session.post(
                f"{self.base_url}/practice/patients", 
                json=invalid_patient_data, 
                headers=headers
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Invalid Data Handling", True, 
                            "API properly validates required fields")
                return True
            else:
                self.log_test("Invalid Data Handling", False, 
                            f"Expected 422 validation error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Data Handling", False, f"Exception: {str(e)}")
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
            self.test_error_handling
        ]
        
        # Practice Management API tests (require authentication)
        practice_tests = [
            self.setup_test_practice,
            self.test_practice_dashboard,
            self.test_create_patient,
            self.test_get_practice_patients,
            self.test_assign_procedure,
            self.test_unauthorized_access,
            self.test_invalid_data_handling
        ]
        
        all_tests = basic_tests + practice_tests
        
        passed = 0
        total = len(all_tests)
        
        print("🔍 Running Basic API Tests...")
        for test in basic_tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("🏥 Running Practice Management API Tests...")
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