#!/usr/bin/env python3
"""
Critical Backend API Testing for User-Reported Issues
Focus on PDF generation data, procedure library, admin authentication, and system stability
"""

import requests
import json
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Get backend URL from frontend .env file
BACKEND_URL = "https://carebot-2.preview.emergentagent.com/api"

class CriticalAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.super_admin_token = None
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

    def test_practice_admin_login(self):
        """Test practice admin login (cganz2279@gmail.com/admin123)"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data and "user" in data:
                    user = data["user"]
                    if user.get("role") == "practice_admin":
                        self.admin_token = data["token"]
                        self.log_test("Practice Admin Login (cganz2279@gmail.com)", True, 
                                    f"Admin logged in: {user['firstName']} {user['lastName']}")
                        return True
                    else:
                        self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, 
                                    f"Wrong role: {user.get('role')}")
                        return False
                else:
                    self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Admin Login (cganz2279@gmail.com)", False, f"Exception: {str(e)}")
            return False

    def test_super_admin_login(self):
        """Test super admin login - using correct credentials from backend code"""
        try:
            # Based on backend/routes/admin.py, the super admin credentials are hardcoded as:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.super_admin_token = data["token"]
                    self.log_test("Super Admin Login", True, "Super admin login successful")
                    return True
                else:
                    self.log_test("Super Admin Login", False, "Invalid response format")
                    return False
            else:
                self.log_test("Super Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Super Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_procedure_library_completeness(self):
        """Test GET /api/procedures endpoint - should return all 80 procedures"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    procedure_count = len(procedures)
                    
                    # Check if we have the expected 80 procedures
                    if procedure_count >= 80:
                        # Verify required fields for library functionality
                        required_fields = ["id", "name", "specialty", "specialtyName", "duration"]
                        sample_procedure = procedures[0] if procedures else {}
                        
                        if all(field in sample_procedure for field in required_fields):
                            self.log_test("Procedure Library Completeness", True, 
                                        f"Found {procedure_count} procedures with all required fields for library")
                            return True
                        else:
                            missing_fields = [f for f in required_fields if f not in sample_procedure]
                            self.log_test("Procedure Library Completeness", False, 
                                        f"Procedures missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Procedure Library Completeness", False, 
                                    f"Expected 80+ procedures, got {procedure_count}")
                        return False
                else:
                    self.log_test("Procedure Library Completeness", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Library Completeness", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Library Completeness", False, f"Exception: {str(e)}")
            return False

    def test_pdf_generation_data_completeness(self):
        """Test procedure assignment endpoints for PDF generation data completeness"""
        if not self.admin_token:
            self.log_test("PDF Generation Data Completeness", False, "No admin token available")
            return False
            
        try:
            # First get dashboard to find existing assignments
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            dashboard_response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
            
            assignment_id = None
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                if dashboard_data.get("success") and "data" in dashboard_data:
                    recent_procedures = dashboard_data["data"].get("recentProcedures", [])
                    if recent_procedures:
                        assignment_id = recent_procedures[0].get("id")
            
            if not assignment_id:
                # Create a test assignment for PDF testing
                assignment_success = self.create_test_assignment_for_pdf()
                if not assignment_success:
                    self.log_test("PDF Generation Data Completeness", False, 
                                "No existing assignments and failed to create test assignment")
                    return False
                assignment_id = self.test_assignment_id
            
            # Test GET assignment endpoint for PDF data
            response = self.session.get(f"{self.base_url}/practice/procedure-assignments/{assignment_id}", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    
                    # Check all required fields for PDF generation
                    pdf_required_fields = [
                        "procedureName", "dentistName", "performedDate", 
                        "practiceNotes", "customInstructions"
                    ]
                    
                    missing_fields = []
                    empty_fields = []
                    
                    for field in pdf_required_fields:
                        if field not in assignment:
                            missing_fields.append(field)
                        elif not assignment[field] or (isinstance(assignment[field], list) and len(assignment[field]) == 0):
                            empty_fields.append(field)
                    
                    if not missing_fields and not empty_fields:
                        self.log_test("PDF Generation Data Completeness", True, 
                                    f"All PDF required fields present and populated: {', '.join(pdf_required_fields)}")
                        return True
                    else:
                        issues = []
                        if missing_fields:
                            issues.append(f"Missing: {', '.join(missing_fields)}")
                        if empty_fields:
                            issues.append(f"Empty: {', '.join(empty_fields)}")
                        self.log_test("PDF Generation Data Completeness", False, 
                                    f"PDF data issues: {'; '.join(issues)}")
                        return False
                else:
                    self.log_test("PDF Generation Data Completeness", False, "Invalid response format")
                    return False
            else:
                self.log_test("PDF Generation Data Completeness", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PDF Generation Data Completeness", False, f"Exception: {str(e)}")
            return False

    def create_test_assignment_for_pdf(self):
        """Create a test procedure assignment for PDF testing"""
        if not self.admin_token:
            return False
            
        try:
            # First get a patient to assign to
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            patients_response = self.session.get(f"{self.base_url}/practice/patients", headers=headers)
            
            if patients_response.status_code != 200:
                return False
            
            patients_data = patients_response.json()
            if not patients_data.get("success") or not patients_data.get("data"):
                return False
            
            patients = patients_data["data"]
            if len(patients) == 0:
                return False
            
            # Use first patient for testing
            test_patient = patients[0]
            
            # Create assignment with complete PDF data
            assignment_data = {
                "patientId": test_patient["id"],
                "procedureId": "root-canal-therapy",
                "procedureName": "Root Canal Therapy",
                "performedDate": datetime.utcnow().isoformat() + "Z",
                "dentistName": "Dr. Sarah Johnson",
                "practiceNotes": "Patient responded well to local anesthesia. Procedure completed without complications. Post-operative healing progressing normally.",
                "customInstructions": [
                    "Take prescribed antibiotics as directed",
                    "Avoid chewing on treated tooth for 24 hours",
                    "Use warm salt water rinse twice daily",
                    "Return if experiencing severe pain or swelling"
                ],
                "followUpDate": (datetime.utcnow() + timedelta(days=14)).isoformat() + "Z"
            }
            
            response = self.session.post(f"{self.base_url}/practice/assign-procedure", 
                                       json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    self.test_assignment_id = assignment.get("assignmentId")
                    return True
            
            return False
                
        except Exception as e:
            return False

    def test_procedure_content_for_pdf(self):
        """Test individual procedure endpoints for complete content needed for PDF"""
        try:
            # Test key procedures that are commonly used
            test_procedures = [
                "root-canal-therapy",
                "surgical-tooth-extraction", 
                "dental-crown-placement"
            ]
            
            all_complete = True
            procedure_results = []
            
            for procedure_id in test_procedures:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        
                        # Check all content sections needed for PDF
                        required_sections = {
                            "overview": "Overview section",
                            "immediateAftercare": "Aftercare instructions", 
                            "dietRestrictions": "Diet restrictions",
                            "warningSignsToCallDoctor": "Warning signs",
                            "recoveryTimeline": "Recovery timeline",
                            "medications": "Medications"
                        }
                        
                        missing_sections = []
                        empty_sections = []
                        
                        for field, description in required_sections.items():
                            if field not in procedure:
                                missing_sections.append(description)
                            elif not procedure[field] or (isinstance(procedure[field], list) and len(procedure[field]) == 0):
                                empty_sections.append(description)
                        
                        if missing_sections or empty_sections:
                            all_complete = False
                            issues = []
                            if missing_sections:
                                issues.append(f"Missing: {', '.join(missing_sections)}")
                            if empty_sections:
                                issues.append(f"Empty: {', '.join(empty_sections)}")
                            procedure_results.append(f"❌ {procedure_id}: {'; '.join(issues)}")
                        else:
                            procedure_results.append(f"✅ {procedure_id}: Complete content for PDF")
                    else:
                        all_complete = False
                        procedure_results.append(f"❌ {procedure_id}: Invalid response format")
                else:
                    all_complete = False
                    procedure_results.append(f"❌ {procedure_id}: HTTP {response.status_code}")
            
            details = "\n   " + "\n   ".join(procedure_results)
            
            if all_complete:
                self.log_test("Procedure Content for PDF", True, 
                            f"All tested procedures have complete content for PDF generation{details}")
                return True
            else:
                self.log_test("Procedure Content for PDF", False, 
                            f"Some procedures missing content for PDF{details}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Content for PDF", False, f"Exception: {str(e)}")
            return False

    def test_admin_dashboard_functionality(self):
        """Test admin dashboard endpoint for admin panel functionality"""
        if not self.super_admin_token:
            self.log_test("Admin Dashboard Functionality", False, "No super admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.super_admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "stats" in data:
                    stats = data["stats"]
                    required_stats = ["total_practices", "active_practices", "trial_practices", "cancelled_practices"]
                    
                    if all(stat in stats for stat in required_stats):
                        self.log_test("Admin Dashboard Functionality", True, 
                                    f"Admin dashboard working: {stats.get('total_practices', 0)} total practices, {stats.get('active_practices', 0)} active")
                        return True
                    else:
                        missing_stats = [s for s in required_stats if s not in stats]
                        self.log_test("Admin Dashboard Functionality", False, 
                                    f"Missing required stats: {missing_stats}")
                        return False
                else:
                    self.log_test("Admin Dashboard Functionality", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Dashboard Functionality", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard Functionality", False, f"Exception: {str(e)}")
            return False

    def test_system_stability_endpoints(self):
        """Test critical endpoints for system stability and error handling"""
        try:
            stability_tests = []
            
            # Test health check
            health_response = self.session.get(f"{self.base_url}/health")
            if health_response.status_code == 200:
                stability_tests.append("✅ Health check endpoint stable")
            else:
                stability_tests.append(f"❌ Health check failed: {health_response.status_code}")
            
            # Test procedures endpoint
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            if procedures_response.status_code == 200:
                stability_tests.append("✅ Procedures endpoint stable")
            else:
                stability_tests.append(f"❌ Procedures endpoint failed: {procedures_response.status_code}")
            
            # Test specialties endpoint
            specialties_response = self.session.get(f"{self.base_url}/specialties")
            if specialties_response.status_code == 200:
                stability_tests.append("✅ Specialties endpoint stable")
            else:
                stability_tests.append(f"❌ Specialties endpoint failed: {specialties_response.status_code}")
            
            # Test invalid endpoint for proper error handling
            invalid_response = self.session.get(f"{self.base_url}/nonexistent-endpoint")
            if invalid_response.status_code == 404:
                stability_tests.append("✅ Proper 404 error handling")
            else:
                stability_tests.append(f"❌ Improper error handling: {invalid_response.status_code}")
            
            # Test invalid procedure ID for error handling
            invalid_proc_response = self.session.get(f"{self.base_url}/procedures/invalid-procedure-id")
            if invalid_proc_response.status_code == 404:
                stability_tests.append("✅ Proper procedure not found handling")
            else:
                stability_tests.append(f"❌ Improper procedure error handling: {invalid_proc_response.status_code}")
            
            failed_tests = [test for test in stability_tests if test.startswith("❌")]
            
            details = "\n   " + "\n   ".join(stability_tests)
            
            if len(failed_tests) == 0:
                self.log_test("System Stability Endpoints", True, f"All stability tests passed{details}")
                return True
            else:
                self.log_test("System Stability Endpoints", False, 
                            f"{len(failed_tests)} stability issues found{details}")
                return False
                
        except Exception as e:
            self.log_test("System Stability Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_data_consistency(self):
        """Test data consistency across related endpoints"""
        try:
            consistency_tests = []
            
            # Test specialty-procedure consistency
            specialties_response = self.session.get(f"{self.base_url}/specialties")
            procedures_response = self.session.get(f"{self.base_url}/procedures")
            
            if specialties_response.status_code == 200 and procedures_response.status_code == 200:
                specialties_data = specialties_response.json()
                procedures_data = procedures_response.json()
                
                if (specialties_data.get("success") and procedures_data.get("success")):
                    specialties = specialties_data["data"]
                    procedures = procedures_data["data"]
                    
                    # Check if specialty IDs in procedures match existing specialties
                    specialty_ids = {s["id"] for s in specialties}
                    procedure_specialty_ids = {p["specialty"] for p in procedures}
                    
                    orphaned_specialties = procedure_specialty_ids - specialty_ids
                    if len(orphaned_specialties) == 0:
                        consistency_tests.append("✅ Specialty-procedure ID consistency maintained")
                    else:
                        consistency_tests.append(f"❌ Orphaned specialty IDs in procedures: {orphaned_specialties}")
                    
                    # Check procedure counts in specialties
                    for specialty in specialties:
                        actual_count = len([p for p in procedures if p["specialty"] == specialty["id"]])
                        reported_count = specialty.get("procedureCount", 0)
                        if actual_count == reported_count:
                            consistency_tests.append(f"✅ {specialty['name']}: count consistent ({actual_count})")
                        else:
                            consistency_tests.append(f"❌ {specialty['name']}: count mismatch (actual: {actual_count}, reported: {reported_count})")
                else:
                    consistency_tests.append("❌ Failed to get specialty or procedure data")
            else:
                consistency_tests.append("❌ Failed to fetch specialty/procedure endpoints")
            
            failed_tests = [test for test in consistency_tests if test.startswith("❌")]
            
            details = "\n   " + "\n   ".join(consistency_tests)
            
            if len(failed_tests) == 0:
                self.log_test("Data Consistency", True, f"All consistency checks passed{details}")
                return True
            else:
                self.log_test("Data Consistency", False, 
                            f"{len(failed_tests)} consistency issues found{details}")
                return False
                
        except Exception as e:
            self.log_test("Data Consistency", False, f"Exception: {str(e)}")
            return False

    def run_critical_tests(self):
        """Run all critical tests based on user-reported issues"""
        print("=" * 70)
        print("🚨 CRITICAL BACKEND TESTING FOR USER-REPORTED ISSUES")
        print("Testing PDF generation, procedure library, admin auth, and system stability")
        print("=" * 70)
        
        tests = [
            # Admin Authentication Issues
            ("Practice Admin Login", self.test_practice_admin_login),
            ("Super Admin Login", self.test_super_admin_login),
            ("Admin Dashboard Functionality", self.test_admin_dashboard_functionality),
            
            # PDF Generation Issues
            ("PDF Generation Data Completeness", self.test_pdf_generation_data_completeness),
            ("Procedure Content for PDF", self.test_procedure_content_for_pdf),
            
            # Procedure Library Issues
            ("Procedure Library Completeness", self.test_procedure_library_completeness),
            
            # System Stability Issues
            ("System Stability Endpoints", self.test_system_stability_endpoints),
            ("Data Consistency", self.test_data_consistency),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        if passed < total:
            print(f"⚠️  {total - passed} test(s) failed.")
        else:
            print("✅ All critical tests passed!")
        print("=" * 70)
        
        return passed == total

def main():
    tester = CriticalAPITester(BACKEND_URL)
    success = tester.run_critical_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()