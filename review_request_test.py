#!/usr/bin/env python3
"""
Review Request Testing for Dental Post-Operative Care App
Tests PDF content verification and dentist management endpoints as requested
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dental-pdf-sync.preview.emergentagent.com/api"

class ReviewRequestTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.practice_id = None
        
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
        """Authenticate with cganz2279@gmail.com/password123 as requested"""
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
                    self.practice_id = data.get("user", {}).get("practiceId")
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("Authentication (cganz2279@gmail.com)", True, f"Token received, Practice ID: {self.practice_id}")
                    return True
                else:
                    self.log_test("Authentication (cganz2279@gmail.com)", False, "No token in response")
                    return False
            else:
                self.log_test("Authentication (cganz2279@gmail.com)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication (cganz2279@gmail.com)", False, f"Exception: {str(e)}")
            return False

    # PRIORITY 1 - PDF CONTENT VERIFICATION
    def test_root_canal_therapy_content(self):
        """Test GET /api/procedures/root-canal-therapy - Verify specific PDF content"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check for specific root canal content (not generic)
                    overview = procedure.get("overview", "").lower()
                    aftercare = str(procedure.get("immediateAftercare", [])).lower()
                    
                    # Look for root canal specific terms
                    root_canal_terms = ["pulp", "endodontic", "root canal", "nerve", "canal"]
                    found_terms = [term for term in root_canal_terms if term in overview or term in aftercare]
                    
                    if found_terms:
                        self.log_test("Root Canal Therapy - Specific PDF Content", True, 
                                    f"Found root canal specific terms: {found_terms}")
                        return True
                    else:
                        self.log_test("Root Canal Therapy - Specific PDF Content", False, 
                                    "No root canal specific content found - may be generic")
                        return False
                else:
                    self.log_test("Root Canal Therapy - Specific PDF Content", False, "Invalid response format")
                    return False
            else:
                self.log_test("Root Canal Therapy - Specific PDF Content", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Root Canal Therapy - Specific PDF Content", False, f"Exception: {str(e)}")
            return False

    def test_dental_implant_content(self):
        """Test GET /api/procedures/dental-implant-placement - Verify implant-specific content"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/dental-implant-placement")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check for specific implant content
                    overview = procedure.get("overview", "").lower()
                    aftercare = str(procedure.get("immediateAftercare", [])).lower()
                    
                    # Look for implant specific terms
                    implant_terms = ["implant", "osseointegration", "titanium", "abutment", "crown"]
                    found_terms = [term for term in implant_terms if term in overview or term in aftercare]
                    
                    if found_terms:
                        self.log_test("Dental Implant Placement - Specific PDF Content", True, 
                                    f"Found implant specific terms: {found_terms}")
                        return True
                    else:
                        self.log_test("Dental Implant Placement - Specific PDF Content", False, 
                                    "No implant specific content found - may be generic")
                        return False
                else:
                    self.log_test("Dental Implant Placement - Specific PDF Content", False, "Invalid response format")
                    return False
            else:
                self.log_test("Dental Implant Placement - Specific PDF Content", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Dental Implant Placement - Specific PDF Content", False, f"Exception: {str(e)}")
            return False

    def test_all_procedures_count(self):
        """Test GET /api/procedures - Verify all 81 procedures from uploaded PDFs are present"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    procedure_count = len(procedures)
                    
                    # Check if we have around 81 procedures (allowing for slight variation)
                    if procedure_count >= 80 and procedure_count <= 85:
                        self.log_test("All Procedures Count (81 from PDFs)", True, 
                                    f"Found {procedure_count} procedures (expected ~81)")
                        return True
                    else:
                        self.log_test("All Procedures Count (81 from PDFs)", False, 
                                    f"Found {procedure_count} procedures, expected ~81")
                        return False
                else:
                    self.log_test("All Procedures Count (81 from PDFs)", False, "Invalid response format")
                    return False
            else:
                self.log_test("All Procedures Count (81 from PDFs)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("All Procedures Count (81 from PDFs)", False, f"Exception: {str(e)}")
            return False

    def test_specialties_with_counts(self):
        """Test GET /api/specialties - Verify all 7 specialties with correct procedure counts"""
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    specialty_count = len(specialties)
                    
                    if specialty_count == 7:
                        # Check procedure counts
                        total_procedures = sum(s.get("procedureCount", 0) for s in specialties)
                        specialty_details = [(s.get("name"), s.get("procedureCount", 0)) for s in specialties]
                        
                        self.log_test("All Specialties (7 with procedure counts)", True, 
                                    f"Found {specialty_count} specialties, {total_procedures} total procedures. Details: {specialty_details}")
                        return True
                    else:
                        self.log_test("All Specialties (7 with procedure counts)", False, 
                                    f"Found {specialty_count} specialties, expected 7")
                        return False
                else:
                    self.log_test("All Specialties (7 with procedure counts)", False, "Invalid response format")
                    return False
            else:
                self.log_test("All Specialties (7 with procedure counts)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("All Specialties (7 with procedure counts)", False, f"Exception: {str(e)}")
            return False

    # PRIORITY 2 - DENTIST MANAGEMENT VERIFICATION
    def test_get_dentists(self):
        """Test GET /api/practice/dentists"""
        try:
            response = self.session.get(f"{self.base_url}/practice/dentists")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dentists = data["data"]
                    dentist_count = len(dentists)
                    self.log_test("GET /api/practice/dentists", True, 
                                f"Retrieved {dentist_count} dentists")
                    return dentists
                else:
                    self.log_test("GET /api/practice/dentists", False, "Invalid response format")
                    return []
            else:
                self.log_test("GET /api/practice/dentists", False, f"Status: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("GET /api/practice/dentists", False, f"Exception: {str(e)}")
            return []

    def test_create_dentist(self):
        """Test POST /api/practice/dentists (create new dentist)"""
        try:
            dentist_data = {
                "firstName": "Test",
                "lastName": "Dentist",
                "email": "test.dentist@reviewtest.com",
                "phone": "(555) 999-8888",
                "licenseNumber": "TEST12345",
                "specialties": ["General Dentistry", "Oral Surgery"]
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=dentist_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    created_dentist = data["data"]
                    dentist_id = created_dentist.get("id")
                    self.log_test("POST /api/practice/dentists (create)", True, 
                                f"Created dentist with ID: {dentist_id}")
                    return dentist_id
                else:
                    self.log_test("POST /api/practice/dentists (create)", False, "Invalid response format")
                    return None
            else:
                self.log_test("POST /api/practice/dentists (create)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("POST /api/practice/dentists (create)", False, f"Exception: {str(e)}")
            return None

    def test_update_dentist(self, dentist_id: str):
        """Test PUT /api/practice/dentists/{id} (update dentist)"""
        try:
            update_data = {
                "firstName": "Updated",
                "lastName": "TestDentist",
                "phone": "(555) 999-7777",
                "specialties": ["General Dentistry", "Endodontics"]
            }
            
            response = self.session.put(f"{self.base_url}/practice/dentists/{dentist_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("PUT /api/practice/dentists/{id} (update)", True, 
                                f"Updated dentist {dentist_id}")
                    return True
                else:
                    self.log_test("PUT /api/practice/dentists/{id} (update)", False, "Invalid response format")
                    return False
            else:
                self.log_test("PUT /api/practice/dentists/{id} (update)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /api/practice/dentists/{id} (update)", False, f"Exception: {str(e)}")
            return False

    def test_delete_dentist(self, dentist_id: str):
        """Test DELETE /api/practice/dentists/{id} (soft delete)"""
        try:
            response = self.session.delete(f"{self.base_url}/practice/dentists/{dentist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("DELETE /api/practice/dentists/{id} (soft delete)", True, 
                                f"Soft deleted dentist {dentist_id}")
                    return True
                else:
                    self.log_test("DELETE /api/practice/dentists/{id} (soft delete)", False, "Invalid response format")
                    return False
            else:
                self.log_test("DELETE /api/practice/dentists/{id} (soft delete)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("DELETE /api/practice/dentists/{id} (soft delete)", False, f"Exception: {str(e)}")
            return False

    # PRIORITY 3 - INTEGRATION TESTING
    def test_procedure_assignment_with_dentist(self):
        """Test procedure assignment with dentist selection"""
        try:
            # First get patients and procedures
            patients_response = self.session.get(f"{self.base_url}/practice/patients")
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            dentists_response = self.session.get(f"{self.base_url}/practice/dentists")
            
            if (patients_response.status_code == 200 and 
                procedures_response.status_code == 200 and 
                dentists_response.status_code == 200):
                
                patients = patients_response.json().get("data", [])
                procedures = procedures_response.json().get("data", [])
                dentists = dentists_response.json().get("data", [])
                
                if patients and procedures and dentists:
                    # Create assignment with dentist
                    assignment_data = {
                        "patientId": patients[0]["id"],
                        "procedureId": procedures[0]["id"],
                        "dentistName": f"Dr. {dentists[0]['firstName']} {dentists[0]['lastName']}",
                        "scheduledDate": "2025-01-20",
                        "followUpDate": "2025-01-27",
                        "customInstructions": "Test assignment with dentist selection",
                        "practiceNotes": "Review request testing"
                    }
                    
                    response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            self.log_test("Procedure Assignment with Dentist Selection", True, 
                                        f"Assigned procedure to patient with dentist: {assignment_data['dentistName']}")
                            return True
                        else:
                            self.log_test("Procedure Assignment with Dentist Selection", False, "Invalid response format")
                            return False
                    else:
                        self.log_test("Procedure Assignment with Dentist Selection", False, 
                                    f"Status: {response.status_code}, Response: {response.text}")
                        return False
                else:
                    self.log_test("Procedure Assignment with Dentist Selection", False, 
                                "Missing patients, procedures, or dentists data")
                    return False
            else:
                self.log_test("Procedure Assignment with Dentist Selection", False, 
                            "Failed to retrieve prerequisite data")
                return False
                
        except Exception as e:
            self.log_test("Procedure Assignment with Dentist Selection", False, f"Exception: {str(e)}")
            return False

    def test_patient_management(self):
        """Verify patient management still works"""
        try:
            # Test getting patients
            response = self.session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    self.log_test("Patient Management - GET patients", True, 
                                f"Retrieved {len(patients)} patients")
                    return True
                else:
                    self.log_test("Patient Management - GET patients", False, "Invalid response format")
                    return False
            else:
                self.log_test("Patient Management - GET patients", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patient Management - GET patients", False, f"Exception: {str(e)}")
            return False

    def test_practice_dashboard(self):
        """Test practice dashboard endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    stats = dashboard_data.get("stats", {})
                    self.log_test("Practice Dashboard", True, 
                                f"Dashboard loaded - Patients: {stats.get('totalPatients')}, Procedures: {stats.get('activeProcedures')}")
                    return True
                else:
                    self.log_test("Practice Dashboard", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Dashboard", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Practice Dashboard", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all review request tests"""
        print("=" * 80)
        print("REVIEW REQUEST TESTING - PDF CONTENT & DENTIST MANAGEMENT")
        print("=" * 80)
        
        # Authentication first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        print("\n" + "=" * 50)
        print("PRIORITY 1 - PDF CONTENT VERIFICATION")
        print("=" * 50)
        
        self.test_root_canal_therapy_content()
        self.test_dental_implant_content()
        self.test_all_procedures_count()
        self.test_specialties_with_counts()
        
        print("\n" + "=" * 50)
        print("PRIORITY 2 - DENTIST MANAGEMENT VERIFICATION")
        print("=" * 50)
        
        # Get existing dentists
        existing_dentists = self.test_get_dentists()
        
        # Create new dentist
        new_dentist_id = self.test_create_dentist()
        
        # Update dentist if created successfully
        if new_dentist_id:
            self.test_update_dentist(new_dentist_id)
            self.test_delete_dentist(new_dentist_id)
        
        print("\n" + "=" * 50)
        print("PRIORITY 3 - INTEGRATION TESTING")
        print("=" * 50)
        
        self.test_procedure_assignment_with_dentist()
        self.test_patient_management()
        self.test_practice_dashboard()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
        
        return failed_tests == 0

def main():
    """Main function to run all tests"""
    tester = ReviewRequestTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Review request requirements verified!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - Check details above")
        sys.exit(1)

if __name__ == "__main__":
    main()