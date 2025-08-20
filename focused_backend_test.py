#!/usr/bin/env python3
"""
Focused Backend API Testing for Dental Application
Tests the specific APIs mentioned in the review request
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from the review request
BACKEND_URL = "https://dental-assist-4.preview.emergentagent.com/api"

class FocusedDentalAPITester:
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
    
    def test_auth_login(self):
        """Test POST /api/auth/login with admin@smithdental.com / password123"""
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
                    practice_info = data.get("practice", {})
                    practice_name = practice_info.get("name", "Unknown Practice") if practice_info else "No Practice"
                    self.log_test("Authentication API (/api/auth/login)", True, 
                                f"Successfully logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')}) from {practice_name}")
                    return True
                else:
                    self.log_test("Authentication API (/api/auth/login)", False, "Invalid response format - missing success or token")
                    return False
            else:
                self.log_test("Authentication API (/api/auth/login)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication API (/api/auth/login)", False, f"Exception: {str(e)}")
            return False

    def test_practice_dashboard(self):
        """Test GET /api/practice/dashboard"""
        if not self.auth_token:
            self.log_test("Practice Dashboard API (/api/practice/dashboard)", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    practice = dashboard_data.get("practice", {})
                    stats = dashboard_data.get("stats", {})
                    recent_patients = dashboard_data.get("recentPatients", [])
                    recent_procedures = dashboard_data.get("recentProcedures", [])
                    
                    self.log_test("Practice Dashboard API (/api/practice/dashboard)", True, 
                                f"Dashboard loaded for {practice.get('name', 'Unknown Practice')} - {stats.get('patientCount', 0)} patients, {stats.get('activeProcedures', 0)} active procedures, {len(recent_patients)} recent patients, {len(recent_procedures)} recent procedures")
                    return True
                else:
                    self.log_test("Practice Dashboard API (/api/practice/dashboard)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Dashboard API (/api/practice/dashboard)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Dashboard API (/api/practice/dashboard)", False, f"Exception: {str(e)}")
            return False

    def test_get_patients(self):
        """Test GET /api/practice/patients"""
        if not self.auth_token:
            self.log_test("Get Patients API (/api/practice/patients)", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    # Check if patients have required fields
                    if patients:
                        sample_patient = patients[0]
                        required_fields = ["id", "firstName", "lastName", "email"]
                        if all(field in sample_patient for field in required_fields):
                            self.log_test("Get Patients API (/api/practice/patients)", True, 
                                        f"Retrieved {len(patients)} patients with complete information")
                            return True
                        else:
                            self.log_test("Get Patients API (/api/practice/patients)", False, "Patients missing required fields")
                            return False
                    else:
                        self.log_test("Get Patients API (/api/practice/patients)", True, 
                                    "Retrieved 0 patients (empty practice)")
                        return True
                else:
                    self.log_test("Get Patients API (/api/practice/patients)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Patients API (/api/practice/patients)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Patients API (/api/practice/patients)", False, f"Exception: {str(e)}")
            return False

    def test_get_procedures(self):
        """Test GET /api/procedures"""
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
                            self.log_test("Get Procedures API (/api/procedures)", True, 
                                        f"Retrieved {len(procedures)} procedures with complete information")
                            return True
                        else:
                            self.log_test("Get Procedures API (/api/procedures)", False, "Procedures missing required fields")
                            return False
                    else:
                        self.log_test("Get Procedures API (/api/procedures)", False, "No procedures found")
                        return False
                else:
                    self.log_test("Get Procedures API (/api/procedures)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedures API (/api/procedures)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedures API (/api/procedures)", False, f"Exception: {str(e)}")
            return False

    def test_get_practice_doctors(self):
        """Test GET /api/practice/doctors"""
        if not self.auth_token:
            self.log_test("Get Practice Doctors API (/api/practice/doctors)", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/doctors")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    doctors = data["data"]
                    # Check if doctors have proper formatting (no double "Dr.")
                    properly_formatted = True
                    doctor_names = []
                    for doctor in doctors:
                        name = doctor.get("name", "")
                        doctor_names.append(name)
                        if "Dr. Dr." in name:
                            properly_formatted = False
                            break
                    
                    if properly_formatted:
                        self.log_test("Get Practice Doctors API (/api/practice/doctors)", True, 
                                    f"Retrieved {len(doctors)} doctors with proper name formatting: {', '.join(doctor_names)}")
                        return True
                    else:
                        self.log_test("Get Practice Doctors API (/api/practice/doctors)", False, 
                                    "Doctor names have double 'Dr.' prefix")
                        return False
                else:
                    self.log_test("Get Practice Doctors API (/api/practice/doctors)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Practice Doctors API (/api/practice/doctors)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Practice Doctors API (/api/practice/doctors)", False, f"Exception: {str(e)}")
            return False

    def test_request_procedure(self):
        """Test POST /api/practice/request-procedure"""
        if not self.auth_token:
            self.log_test("Request Procedure API (/api/practice/request-procedure)", False, "No authentication token available")
            return False
            
        try:
            # Create a test procedure request
            request_data = {
                "procedureName": "Custom Dental Implant Procedure",
                "specialty": "oral-surgery",
                "description": "A specialized implant procedure for complex cases",
                "reasonForRequest": "We need this procedure for our practice as we frequently perform complex implant cases",
                "urgencyLevel": "normal"
            }
            
            response = self.session.post(f"{self.base_url}/practice/request-procedure", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "requestId" in data:
                    request_id = data["requestId"]
                    self.log_test("Request Procedure API (/api/practice/request-procedure)", True, 
                                f"Successfully submitted procedure request: {request_data['procedureName']} (Request ID: {request_id})")
                    return True
                else:
                    self.log_test("Request Procedure API (/api/practice/request-procedure)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Request Procedure API (/api/practice/request-procedure)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Request Procedure API (/api/practice/request-procedure)", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run the focused tests for the review request"""
        print(f"🧪 Starting Focused Backend API Tests for Dental Application")
        print(f"🔗 Testing against: {self.base_url}")
        print(f"📋 Testing specific APIs mentioned in review request:")
        print("   1. Authentication API (/api/auth/login)")
        print("   2. Practice Dashboard API (/api/practice/dashboard)")
        print("   3. Get Patients API (/api/practice/patients)")
        print("   4. Get Procedures API (/api/procedures)")
        print("   5. Get Practice Doctors API (/api/practice/doctors)")
        print("   6. Request Procedure API (/api/practice/request-procedure)")
        print("=" * 70)
        
        # Define the tests in order
        tests = [
            self.test_auth_login,
            self.test_practice_dashboard,
            self.test_get_patients,
            self.test_get_procedures,
            self.test_get_practice_doctors,
            self.test_request_procedure
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 70)
        print(f"📊 Focused Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All focused tests passed! The specific APIs mentioned in the review request are working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the focused tests"""
    tester = FocusedDentalAPITester(BACKEND_URL)
    success = tester.run_focused_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()