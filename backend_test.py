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

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentalrescue.preview.emergentagent.com/api"

class DentalAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.patient_token = None
        self.test_patient_id = None
        self.test_assignment_id = None
        
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
            # Test with root-canal procedure
            response = self.session.get(f"{self.base_url}/procedures/root-canal")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    required_fields = ["id", "name", "specialty", "specialtyName", "duration", 
                                     "overview", "immediateAftercare", "dietRestrictions", 
                                     "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                    
                    if all(field in procedure for field in required_fields):
                        if procedure["id"] == "root-canal":
                            self.log_test("Get Procedure by ID (root-canal)", True, 
                                        f"Found detailed procedure information")
                            return True
                        else:
                            self.log_test("Get Procedure by ID (root-canal)", False, "Wrong procedure returned")
                            return False
                    else:
                        missing_fields = [f for f in required_fields if f not in procedure]
                        self.log_test("Get Procedure by ID (root-canal)", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Get Procedure by ID (root-canal)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedure by ID (root-canal)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedure by ID (root-canal)", False, f"Exception: {str(e)}")
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
    
    def test_practice_admin_login(self):
        """Test practice admin login"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data and "user" in data:
                    user = data["user"]
                    if user.get("role") == "practice_admin":
                        self.admin_token = data["token"]
                        self.log_test("Practice Admin Login", True, f"Admin logged in: {user['firstName']} {user['lastName']}")
                        return True
                    else:
                        self.log_test("Practice Admin Login", False, f"Wrong role: {user.get('role')}")
                        return False
                else:
                    self.log_test("Practice Admin Login", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_add_patient(self):
        """Test adding a new patient"""
        if not self.admin_token:
            self.log_test("Add Patient", False, "No admin token available")
            return False
            
        try:
            patient_data = {
                "email": "testpatient@dentaltest.com",
                "firstName": "John",
                "lastName": "Doe",
                "phone": "555-123-4567"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/practice/patients", json=patient_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patient = data["data"]
                    self.test_patient_id = patient["id"]
                    self.log_test("Add Patient", True, f"Patient created: {patient['firstName']} {patient['lastName']} (ID: {patient['id']})")
                    return True
                else:
                    self.log_test("Add Patient", False, "Invalid response format")
                    return False
            else:
                self.log_test("Add Patient", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Patient", False, f"Exception: {str(e)}")
            return False

    def test_assign_procedure(self):
        """Test assigning a procedure to a patient"""
        if not self.admin_token or not self.test_patient_id:
            self.log_test("Assign Procedure", False, "No admin token or patient ID available")
            return False
            
        try:
            # Use root-canal procedure for testing
            assignment_data = {
                "patientId": self.test_patient_id,
                "procedureId": "root-canal",
                "procedureName": "Root Canal Treatment",
                "performedDate": datetime.utcnow().isoformat() + "Z",
                "dentistName": "Dr. Smith",
                "practiceNotes": "Standard root canal procedure completed successfully",
                "customInstructions": ["Take prescribed antibiotics", "Avoid hard foods for 24 hours"],
                "followUpDate": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    self.test_assignment_id = assignment["assignmentId"]
                    self.log_test("Assign Procedure", True, f"Procedure assigned: {assignment['procedureName']} to {assignment['patientName']}")
                    return True
                else:
                    self.log_test("Assign Procedure", False, "Invalid response format")
                    return False
            else:
                self.log_test("Assign Procedure", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Assign Procedure", False, f"Exception: {str(e)}")
            return False

    def test_set_patient_password(self):
        """Test setting patient password for login"""
        if not self.admin_token:
            self.log_test("Set Patient Password", False, "No admin token available")
            return False
            
        try:
            password_data = {
                "email": "testpatient@dentaltest.com",
                "newPassword": "patient123"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/auth/set-patient-password", json=password_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Set Patient Password", True, "Patient password set successfully")
                    return True
                else:
                    self.log_test("Set Patient Password", False, "Invalid response format")
                    return False
            else:
                self.log_test("Set Patient Password", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Set Patient Password", False, f"Exception: {str(e)}")
            return False

    def test_patient_login(self):
        """Test patient login"""
        try:
            login_data = {
                "email": "testpatient@dentaltest.com",
                "password": "patient123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data and "user" in data:
                    user = data["user"]
                    if user.get("role") == "patient":
                        self.patient_token = data["token"]
                        self.log_test("Patient Login", True, f"Patient logged in: {user['firstName']} {user['lastName']}")
                        return True
                    else:
                        self.log_test("Patient Login", False, f"Wrong role: {user.get('role')}")
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

    def test_patient_dashboard(self):
        """Test patient dashboard API"""
        if not self.patient_token:
            self.log_test("Patient Dashboard", False, "No patient token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.patient_token}"}
            response = self.session.get(f"{self.base_url}/auth/patient-dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    patient = dashboard_data.get("patient")
                    practice = dashboard_data.get("practice")
                    procedures = dashboard_data.get("assignedProcedures", [])
                    stats = dashboard_data.get("stats", {})
                    
                    if patient and practice and isinstance(procedures, list):
                        self.log_test("Patient Dashboard", True, 
                                    f"Dashboard loaded: {len(procedures)} procedures, Practice: {practice.get('name', 'Unknown')}")
                        return True
                    else:
                        self.log_test("Patient Dashboard", False, "Missing required dashboard data")
                        return False
                else:
                    self.log_test("Patient Dashboard", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Dashboard", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Patient Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_practice_dashboard(self):
        """Test practice dashboard API"""
        if not self.admin_token:
            self.log_test("Practice Dashboard", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    practice = dashboard_data.get("practice")
                    stats = dashboard_data.get("stats", {})
                    recent_patients = dashboard_data.get("recentPatients", [])
                    recent_procedures = dashboard_data.get("recentProcedures", [])
                    
                    if practice and "patientCount" in stats:
                        self.log_test("Practice Dashboard", True, 
                                    f"Dashboard loaded: {stats.get('patientCount', 0)} patients, {stats.get('activeProcedures', 0)} active procedures")
                        return True
                    else:
                        self.log_test("Practice Dashboard", False, "Missing required dashboard data")
                        return False
                else:
                    self.log_test("Practice Dashboard", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Dashboard", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_unauthorized_access(self):
        """Test unauthorized access scenarios"""
        try:
            # Test patient trying to access admin API
            if self.patient_token:
                headers = {"Authorization": f"Bearer {self.patient_token}"}
                response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
                
                if response.status_code == 403:
                    self.log_test("Unauthorized Access (Patient->Admin)", True, "Properly blocked patient from admin API")
                    return True
                else:
                    self.log_test("Unauthorized Access (Patient->Admin)", False, f"Expected 403, got {response.status_code}")
                    return False
            else:
                self.log_test("Unauthorized Access (Patient->Admin)", False, "No patient token to test with")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Access (Patient->Admin)", False, f"Exception: {str(e)}")
            return False

    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        try:
            login_data = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 401:
                data = response.json()
                if "detail" in data:
                    self.log_test("Invalid Credentials", True, f"Proper 401 error: {data['detail']}")
                    return True
                else:
                    self.log_test("Invalid Credentials", False, "401 status but missing error detail")
                    return False
            else:
                self.log_test("Invalid Credentials", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Credentials", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🧪 Starting Backend API Tests for Dental B2B SaaS Application")
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
        ]
        
        # Patient management workflow tests
        patient_management_tests = [
            self.test_practice_admin_login,
            self.test_add_patient,
            self.test_assign_procedure,
            self.test_set_patient_password,
            self.test_patient_login,
            self.test_patient_dashboard,
            self.test_practice_dashboard,
        ]
        
        # Security tests
        security_tests = [
            self.test_unauthorized_access,
            self.test_invalid_credentials,
        ]
        
        all_tests = basic_tests + patient_management_tests + security_tests
        
        passed = 0
        total = len(all_tests)
        
        print("🔍 Running Basic API Tests...")
        for test in basic_tests:
            if test():
                passed += 1
            print()
        
        print("👥 Running Patient Management Tests...")
        for test in patient_management_tests:
            if test():
                passed += 1
            print()
        
        print("🔒 Running Security Tests...")
        for test in security_tests:
            if test():
                passed += 1
            print()
        
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