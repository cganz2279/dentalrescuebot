#!/usr/bin/env python3
"""
URGENT COMPREHENSIVE BACKEND TESTING
User reports entire application is broken and unreliable.
Testing ALL backend functionality to verify current working state.
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dental-portal-fix-1.preview.emergentagent.com/api"

class UrgentDentalAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_tokens = {}
        self.test_data = {}
        
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
    
    def test_database_connectivity(self):
        """Test MongoDB connection and verify data exists"""
        try:
            # Test health check first
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Database Connectivity - Health Check", True, f"Response: {data}")
                    
                    # Test specialties to verify database has data
                    specialties_response = self.session.get(f"{self.base_url}/specialties")
                    if specialties_response.status_code == 200:
                        specialties_data = specialties_response.json()
                        if specialties_data.get("success") and specialties_data.get("data"):
                            specialty_count = len(specialties_data["data"])
                            self.log_test("Database Connectivity - Data Verification", True, 
                                        f"Found {specialty_count} specialties in database")
                            return True
                        else:
                            self.log_test("Database Connectivity - Data Verification", False, "No specialties found in database")
                            return False
                    else:
                        self.log_test("Database Connectivity - Data Verification", False, 
                                    f"Specialties API failed: {specialties_response.status_code}")
                        return False
                else:
                    self.log_test("Database Connectivity - Health Check", False, "Missing 'message' in response")
                    return False
            else:
                self.log_test("Database Connectivity - Health Check", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Connectivity", False, f"Exception: {str(e)}")
            return False

    def test_core_authentication_apis(self):
        """Test all core authentication APIs with correct credentials"""
        print("\n🔐 TESTING CORE AUTHENTICATION APIs")
        
        # Test 1: Practice Admin Login with cganz2279@gmail.com
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_tokens["practice_admin"] = data["token"]
                    user_info = data.get("user", {})
                    practice_info = data.get("practice", {})
                    self.log_test("Practice Admin Login (cganz2279@gmail.com)", True, 
                                f"Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} from {practice_info.get('name', '')} (role: {user_info.get('role', '')})")
                else:
                    self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, "Invalid response format")
            else:
                self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, f"Exception: {str(e)}")

        # Test 2: Patient Login with ganzseth@gmail.com
        try:
            login_data = {
                "email": "ganzseth@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_tokens["patient"] = data["token"]
                    user_info = data.get("user", {})
                    self.log_test("Patient Login (ganzseth@gmail.com)", True, 
                                f"Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} (role: {user_info.get('role', '')})")
                else:
                    self.log_test("Patient Login (ganzseth@gmail.com)", False, "Invalid response format")
            else:
                self.log_test("Patient Login (ganzseth@gmail.com)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Patient Login (ganzseth@gmail.com)", False, f"Exception: {str(e)}")

        # Test 3: Super Admin Login with cganz@admin.com
        try:
            login_data = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_tokens["super_admin"] = data["token"]
                    user_info = data.get("user", {})
                    self.log_test("Super Admin Login (cganz@admin.com)", True, 
                                f"Logged in as super admin (role: {user_info.get('role', '')})")
                else:
                    self.log_test("Super Admin Login (cganz@admin.com)", False, "Invalid response format")
            else:
                self.log_test("Super Admin Login (cganz@admin.com)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Super Admin Login (cganz@admin.com)", False, f"Exception: {str(e)}")

    def test_practice_management_apis(self):
        """Test practice management APIs with practice admin JWT"""
        print("\n🏥 TESTING PRACTICE MANAGEMENT APIs")
        
        if "practice_admin" not in self.auth_tokens:
            self.log_test("Practice Management APIs", False, "No practice admin token available")
            return
            
        # Set up session with practice admin token
        practice_session = requests.Session()
        practice_session.headers.update({"Authorization": f"Bearer {self.auth_tokens['practice_admin']}"})
        
        # Test 1: GET /api/practice/dashboard
        try:
            response = practice_session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    practice_info = dashboard_data.get("practice", {})
                    stats = dashboard_data.get("stats", {})
                    self.log_test("Practice Dashboard API", True, 
                                f"Dashboard loaded for {practice_info.get('name', '')} - Stats: {stats}")
                else:
                    self.log_test("Practice Dashboard API", False, "Invalid response format")
            else:
                self.log_test("Practice Dashboard API", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Practice Dashboard API", False, f"Exception: {str(e)}")

        # Test 2: GET /api/practice/patients
        try:
            response = practice_session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    self.log_test("Get Patients API", True, f"Retrieved {len(patients)} patients")
                    # Store first patient for later tests
                    if patients:
                        self.test_data["existing_patient_id"] = patients[0].get("id")
                else:
                    self.log_test("Get Patients API", False, "Invalid response format")
            else:
                self.log_test("Get Patients API", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Get Patients API", False, f"Exception: {str(e)}")

        # Test 3: POST /api/practice/patients (add new patient)
        try:
            import time
            timestamp = str(int(time.time()))
            patient_data = {
                "email": f"urgent.test.{timestamp}@example.com",
                "firstName": "Urgent",
                "lastName": "TestPatient",
                "phone": "555-9999"
            }
            
            response = practice_session.post(f"{self.base_url}/practice/patients", json=patient_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patient = data["data"]
                    self.test_data["new_patient_id"] = patient.get("id")
                    self.log_test("Add New Patient API", True, 
                                f"Created patient: {patient.get('firstName')} {patient.get('lastName')} (ID: {patient.get('id')})")
                else:
                    self.log_test("Add New Patient API", False, "Invalid response format")
            else:
                self.log_test("Add New Patient API", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Add New Patient API", False, f"Exception: {str(e)}")

        # Test 4: GET /api/practice/doctors
        try:
            response = practice_session.get(f"{self.base_url}/practice/doctors")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    doctors = data["data"]
                    self.log_test("Get Practice Doctors API", True, 
                                f"Retrieved {len(doctors)} doctors: {[d.get('name', '') for d in doctors]}")
                else:
                    self.log_test("Get Practice Doctors API", False, "Invalid response format")
            else:
                self.log_test("Get Practice Doctors API", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Get Practice Doctors API", False, f"Exception: {str(e)}")

        # Test 5: POST /api/practice/assign-procedure
        try:
            # First get a procedure to assign
            procedures_response = practice_session.get(f"{self.base_url}/procedures")
            if procedures_response.status_code == 200:
                procedures_data = procedures_response.json()
                if procedures_data.get("success") and procedures_data.get("data"):
                    procedure = procedures_data["data"][0]  # Use first procedure
                    
                    # Use the new patient we just created
                    patient_id = self.test_data.get("new_patient_id") or self.test_data.get("existing_patient_id")
                    if patient_id:
                        assignment_data = {
                            "patientId": patient_id,
                            "procedureId": procedure["id"],
                            "procedureName": procedure["name"],
                            "performedDate": "2024-01-15T10:00:00Z",
                            "dentistName": "Dr. Cary Ganz",
                            "practiceNotes": "Urgent test procedure assignment",
                            "customInstructions": ["Follow all post-operative instructions", "Contact office if any concerns"],
                            "followUpDate": "2024-01-22T14:00:00Z"
                        }
                        
                        response = practice_session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("success"):
                                assignment_info = data.get("data", {})
                                self.test_data["assignment_id"] = assignment_info.get("assignmentId")
                                self.log_test("Assign Procedure API", True, 
                                            f"Assigned {assignment_info.get('procedureName', 'procedure')} to patient (Assignment ID: {self.test_data['assignment_id']})")
                            else:
                                self.log_test("Assign Procedure API", False, "Invalid response format")
                        else:
                            self.log_test("Assign Procedure API", False, f"Status: {response.status_code}, Response: {response.text}")
                    else:
                        self.log_test("Assign Procedure API", False, "No patient ID available")
                else:
                    self.log_test("Assign Procedure API", False, "No procedures available")
            else:
                self.log_test("Assign Procedure API", False, "Could not fetch procedures")
                
        except Exception as e:
            self.log_test("Assign Procedure API", False, f"Exception: {str(e)}")

    def test_core_library_apis(self):
        """Test core library APIs"""
        print("\n📚 TESTING CORE LIBRARY APIs")
        
        # Test 1: GET /api/specialties
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    self.log_test("Get All Specialties API", True, 
                                f"Retrieved {len(specialties)} specialties with procedure counts")
                else:
                    self.log_test("Get All Specialties API", False, "Invalid response format")
            else:
                self.log_test("Get All Specialties API", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get All Specialties API", False, f"Exception: {str(e)}")

        # Test 2: GET /api/procedures
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    self.log_test("Get All Procedures API", True, f"Retrieved {len(procedures)} procedures")
                else:
                    self.log_test("Get All Procedures API", False, "Invalid response format")
            else:
                self.log_test("Get All Procedures API", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get All Procedures API", False, f"Exception: {str(e)}")

        # Test 3: GET /api/procedures/root-canal-therapy
        try:
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    required_fields = ["id", "name", "specialty", "specialtyName", "duration", 
                                     "overview", "immediateAftercare", "dietRestrictions", 
                                     "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                    
                    if all(field in procedure for field in required_fields):
                        self.log_test("Get Root Canal Therapy Procedure API", True, 
                                    f"Retrieved detailed procedure information with all required fields")
                    else:
                        missing_fields = [f for f in required_fields if f not in procedure]
                        self.log_test("Get Root Canal Therapy Procedure API", False, 
                                    f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Get Root Canal Therapy Procedure API", False, "Invalid response format")
            else:
                self.log_test("Get Root Canal Therapy Procedure API", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Root Canal Therapy Procedure API", False, f"Exception: {str(e)}")

    def test_patient_portal_apis(self):
        """Test patient portal APIs with patient JWT"""
        print("\n👤 TESTING PATIENT PORTAL APIs")
        
        if "patient" not in self.auth_tokens:
            self.log_test("Patient Portal APIs", False, "No patient token available")
            return
            
        # Set up session with patient token
        patient_session = requests.Session()
        patient_session.headers.update({"Authorization": f"Bearer {self.auth_tokens['patient']}"})
        
        # Test 1: GET /api/patients/dashboard
        try:
            response = patient_session.get(f"{self.base_url}/patients/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    patient_info = dashboard_data.get("patient", {})
                    assigned_procedures = dashboard_data.get("assignedProcedures", [])
                    stats = dashboard_data.get("stats", {})
                    
                    self.log_test("Patient Dashboard API", True, 
                                f"Dashboard loaded for {patient_info.get('firstName', '')} {patient_info.get('lastName', '')} with {len(assigned_procedures)} procedures, Stats: {stats}")
                    
                    # Store assignment ID for next test
                    if assigned_procedures:
                        self.test_data["patient_assignment_id"] = assigned_procedures[0].get("id")
                else:
                    self.log_test("Patient Dashboard API", False, "Invalid response format")
            else:
                self.log_test("Patient Dashboard API", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Patient Dashboard API", False, f"Exception: {str(e)}")

        # Test 2: GET /api/patients/procedures/{assignment_id}
        assignment_id = self.test_data.get("patient_assignment_id") or self.test_data.get("assignment_id")
        if assignment_id:
            try:
                response = patient_session.get(f"{self.base_url}/patients/procedures/{assignment_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure_data = data["data"]
                        assignment = procedure_data.get("assignment", {})
                        procedure = procedure_data.get("procedure", {})
                        practice = procedure_data.get("practice", {})
                        
                        self.log_test("Patient Procedure View API", True, 
                                    f"Retrieved procedure details: {procedure.get('name', '')} for practice {practice.get('name', '')}")
                    else:
                        self.log_test("Patient Procedure View API", False, "Invalid response format")
                else:
                    self.log_test("Patient Procedure View API", False, f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test("Patient Procedure View API", False, f"Exception: {str(e)}")
        else:
            self.log_test("Patient Procedure View API", False, "No assignment ID available for testing")

    def test_user_accounts_exist(self):
        """Verify user accounts exist in database by testing login"""
        print("\n👥 VERIFYING USER ACCOUNTS EXIST")
        
        # Test accounts mentioned in review request
        test_accounts = [
            {"email": "cganz2279@gmail.com", "password": "password123", "expected_role": "practice_admin"},
            {"email": "ganzseth@gmail.com", "password": "password123", "expected_role": "patient"},
        ]
        
        for account in test_accounts:
            try:
                login_data = {
                    "email": account["email"],
                    "password": account["password"]
                }
                
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "token" in data:
                        user_info = data.get("user", {})
                        actual_role = user_info.get("role", "")
                        if actual_role == account["expected_role"]:
                            self.log_test(f"User Account Exists ({account['email']})", True, 
                                        f"Account verified - Role: {actual_role}")
                        else:
                            self.log_test(f"User Account Exists ({account['email']})", False, 
                                        f"Role mismatch - Expected: {account['expected_role']}, Got: {actual_role}")
                    else:
                        self.log_test(f"User Account Exists ({account['email']})", False, "Invalid response format")
                else:
                    self.log_test(f"User Account Exists ({account['email']})", False, 
                                f"Login failed - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"User Account Exists ({account['email']})", False, f"Exception: {str(e)}")

    def test_practice_data_exists(self):
        """Verify practice data exists in database"""
        print("\n🏢 VERIFYING PRACTICE DATA EXISTS")
        
        if "practice_admin" not in self.auth_tokens:
            self.log_test("Practice Data Verification", False, "No practice admin token available")
            return
            
        # Set up session with practice admin token
        practice_session = requests.Session()
        practice_session.headers.update({"Authorization": f"Bearer {self.auth_tokens['practice_admin']}"})
        
        try:
            response = practice_session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    practice_info = dashboard_data.get("practice", {})
                    stats = dashboard_data.get("stats", {})
                    recent_patients = dashboard_data.get("recentPatients", [])
                    recent_procedures = dashboard_data.get("recentProcedures", [])
                    
                    self.log_test("Practice Data Verification", True, 
                                f"Practice: {practice_info.get('name', '')} | Stats: {stats} | Recent Patients: {len(recent_patients)} | Recent Procedures: {len(recent_procedures)}")
                else:
                    self.log_test("Practice Data Verification", False, "Invalid response format")
            else:
                self.log_test("Practice Data Verification", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Practice Data Verification", False, f"Exception: {str(e)}")

    def run_urgent_comprehensive_test(self):
        """Run all urgent comprehensive tests"""
        print("🚨 URGENT COMPREHENSIVE BACKEND TESTING")
        print("User reports entire application is broken and unreliable")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test in priority order as requested
        test_categories = [
            ("Database Connectivity", self.test_database_connectivity),
            ("Core Authentication APIs", self.test_core_authentication_apis),
            ("Practice Management APIs", self.test_practice_management_apis),
            ("Core Library APIs", self.test_core_library_apis),
            ("Patient Portal APIs", self.test_patient_portal_apis),
            ("User Accounts Verification", self.test_user_accounts_exist),
            ("Practice Data Verification", self.test_practice_data_exists),
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n{'='*20} {category_name} {'='*20}")
            test_function()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🔍 URGENT COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n🚨 CRITICAL FAILURES ({failed_tests} tests):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print(f"\n✅ SUCCESSFUL TESTS ({passed_tests} tests):")
        for result in self.test_results:
            if result["success"]:
                print(f"   ✅ {result['test']}")
        
        # Authentication status
        print(f"\n🔐 AUTHENTICATION STATUS:")
        for token_type, token in self.auth_tokens.items():
            status = "✅ WORKING" if token else "❌ FAILED"
            print(f"   {status} {token_type.replace('_', ' ').title()}")
        
        # Critical issues check
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"].lower() for keyword in ["login", "authentication", "database", "connectivity"]):
                critical_issues.append(result["test"])
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            for issue in critical_issues:
                print(f"   🔥 {issue}")
        else:
            print(f"\n✅ NO CRITICAL AUTHENTICATION OR DATABASE ISSUES DETECTED")
        
        print("\n" + "="*80)
        return passed_tests, failed_tests, total_tests

if __name__ == "__main__":
    print("🚨 URGENT: Starting comprehensive backend testing...")
    print("User reports entire application is broken and unreliable")
    
    tester = UrgentDentalAPITester(BACKEND_URL)
    tester.run_urgent_comprehensive_test()
    
    passed, failed, total = tester.generate_summary()
    
    if failed > 0:
        print(f"\n🚨 URGENT ACTION REQUIRED: {failed} tests failed out of {total}")
        sys.exit(1)
    else:
        print(f"\n✅ ALL SYSTEMS OPERATIONAL: {passed}/{total} tests passed")
        sys.exit(0)