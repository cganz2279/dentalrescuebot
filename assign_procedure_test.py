#!/usr/bin/env python3
"""
URGENT API Testing for Assign Procedure Page
Tests the specific endpoints that AssignProcedurePage.jsx is calling
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://postop-care.preview.emergentagent.com/api"

class AssignProcedureAPITester:
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
    
    def authenticate(self):
        """Authenticate with practice admin credentials"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("Authentication", True, f"Logged in as {data.get('user', {}).get('email', 'unknown')}")
                    return True
                else:
                    self.log_test("Authentication", False, "No token in response")
                    return False
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_get_patients(self):
        """Test GET /api/practice/patients - Get all patients for the practice"""
        try:
            response = self.session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "data" in data:
                    patients = data["data"]
                    if isinstance(patients, list):
                        patient_count = len(patients)
                        if patient_count > 0:
                            # Check if patients have required fields
                            sample_patient = patients[0]
                            required_fields = ['id', 'firstName', 'lastName', 'email']
                            missing_fields = [field for field in required_fields if field not in sample_patient]
                            
                            if not missing_fields:
                                self.log_test("Get Patients API", True, f"Retrieved {patient_count} patients with all required fields")
                                return True
                            else:
                                self.log_test("Get Patients API", False, f"Missing required fields: {missing_fields}")
                                return False
                        else:
                            self.log_test("Get Patients API", True, "No patients found (empty practice)")
                            return True
                    else:
                        self.log_test("Get Patients API", False, f"Expected list in data, got: {type(patients)}")
                        return False
                else:
                    self.log_test("Get Patients API", False, f"Missing success/data fields in response: {data}")
                    return False
            else:
                self.log_test("Get Patients API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Patients API", False, f"Exception: {str(e)}")
            return False
    
    def test_get_procedures(self):
        """Test GET /api/procedures - Get all available procedures"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "data" in data:
                    procedures = data["data"]
                    if isinstance(procedures, list):
                        procedure_count = len(procedures)
                        if procedure_count > 0:
                            # Check if procedures have required fields
                            sample_procedure = procedures[0]
                            required_fields = ['id', 'name', 'specialty', 'specialtyName', 'duration']
                            missing_fields = [field for field in required_fields if field not in sample_procedure]
                            
                            if not missing_fields:
                                self.log_test("Get Procedures API", True, f"Retrieved {procedure_count} procedures with all required fields")
                                return True
                            else:
                                self.log_test("Get Procedures API", False, f"Missing required fields: {missing_fields}")
                                return False
                        else:
                            self.log_test("Get Procedures API", False, "No procedures found")
                            return False
                    else:
                        self.log_test("Get Procedures API", False, f"Expected list in data, got: {type(procedures)}")
                        return False
                else:
                    self.log_test("Get Procedures API", False, f"Missing success/data fields in response: {data}")
                    return False
            else:
                self.log_test("Get Procedures API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedures API", False, f"Exception: {str(e)}")
            return False
    
    def test_get_doctors(self):
        """Test GET /api/practice/doctors - Get practice doctors/dentists"""
        try:
            response = self.session.get(f"{self.base_url}/practice/doctors")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "data" in data:
                    doctors = data["data"]
                    if isinstance(doctors, list):
                        doctor_count = len(doctors)
                        if doctor_count > 0:
                            # Check if doctors have required fields
                            sample_doctor = doctors[0]
                            if 'name' in sample_doctor:
                                self.log_test("Get Practice Doctors API", True, f"Retrieved {doctor_count} doctors: {[doc.get('name', 'Unknown') for doc in doctors]}")
                                return True
                            else:
                                self.log_test("Get Practice Doctors API", False, "Missing 'name' field in doctor data")
                                return False
                        else:
                            self.log_test("Get Practice Doctors API", False, "No doctors found")
                            return False
                    else:
                        self.log_test("Get Practice Doctors API", False, f"Expected list in data, got: {type(doctors)}")
                        return False
                else:
                    self.log_test("Get Practice Doctors API", False, f"Missing success/data fields in response: {data}")
                    return False
            else:
                self.log_test("Get Practice Doctors API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Practice Doctors API", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        # Create a session without auth token
        unauth_session = requests.Session()
        
        endpoints_to_test = [
            "/practice/patients",
            "/practice/doctors"
        ]
        
        all_protected = True
        for endpoint in endpoints_to_test:
            try:
                response = unauth_session.get(f"{self.base_url}{endpoint}")
                if response.status_code not in [401, 403]:
                    self.log_test(f"Authentication Required for {endpoint}", False, f"Expected 401/403, got {response.status_code}")
                    all_protected = False
                else:
                    print(f"   ✅ {endpoint} properly protected (Status: {response.status_code})")
            except Exception as e:
                self.log_test(f"Authentication Required for {endpoint}", False, f"Exception: {str(e)}")
                all_protected = False
        
        if all_protected:
            self.log_test("Authentication Required", True, "All practice endpoints properly protected")
            return True
        else:
            return False
    
    def run_all_tests(self):
        """Run all tests for Assign Procedure page endpoints"""
        print("=" * 80)
        print("URGENT: Testing Assign Procedure Page API Endpoints")
        print("=" * 80)
        
        # Test authentication first
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot test protected endpoints")
            return False
        
        # Test the specific endpoints that AssignProcedurePage.jsx calls
        tests = [
            self.test_get_patients,
            self.test_get_procedures, 
            self.test_get_doctors,
            self.test_authentication_required
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 80)
        print(f"ASSIGN PROCEDURE API TEST RESULTS: {passed}/{total} tests passed")
        print("=" * 80)
        
        if passed == total:
            print("✅ ALL TESTS PASSED - Assign Procedure APIs are working correctly")
            return True
        else:
            print("❌ SOME TESTS FAILED - Check the specific API endpoints above")
            return False

def main():
    """Main test execution"""
    tester = AssignProcedureAPITester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()