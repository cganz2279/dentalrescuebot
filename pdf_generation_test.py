#!/usr/bin/env python3
"""
PDF Generation Backend Testing for Dental Post-Operative Care App
Focused testing for PDF generation related endpoints
"""

import requests
import json
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Get backend URL from frontend .env file
BACKEND_URL = "https://carebot-2.preview.emergentagent.com/api"

class PDFGenerationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.test_assignment_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_practice_admin_login(self):
        """Test practice admin login with specific credentials for PDF generation"""
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
                        self.log_test("Practice Admin Login (PDF Generation)", True, 
                                    f"Admin logged in: {user['firstName']} {user['lastName']} - Ready for PDF generation")
                        return True
                    else:
                        self.log_test("Practice Admin Login (PDF Generation)", False, f"Wrong role: {user.get('role')}")
                        return False
                else:
                    self.log_test("Practice Admin Login (PDF Generation)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Admin Login (PDF Generation)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Admin Login (PDF Generation)", False, f"Exception: {str(e)}")
            return False

    def test_get_available_assignments(self):
        """Get available procedure assignments for PDF generation testing"""
        if not self.admin_token:
            self.log_test("Get Available Assignments", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    recent_procedures = dashboard_data.get("recentProcedures", [])
                    
                    if recent_procedures:
                        # Use the first procedure assignment ID for testing
                        first_assignment = recent_procedures[0]
                        if "id" in first_assignment:
                            self.test_assignment_id = first_assignment["id"]
                            procedure_name = first_assignment.get("procedureName", "Unknown")
                            patient_name = first_assignment.get("patientName", "Unknown Patient")
                            self.log_test("Get Available Assignments", True, 
                                        f"Found {len(recent_procedures)} assignments. Testing with: {procedure_name} for {patient_name} (ID: {self.test_assignment_id})")
                            return True
                    
                    self.log_test("Get Available Assignments", False, "No procedure assignments found for PDF testing")
                    return False
                else:
                    self.log_test("Get Available Assignments", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Available Assignments", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Available Assignments", False, f"Exception: {str(e)}")
            return False

    def test_pdf_data_endpoint(self):
        """Test GET /api/practice/procedure-assignments/{assignment_id} - the main endpoint for PDF generation"""
        if not self.admin_token or not self.test_assignment_id:
            self.log_test("PDF Data Endpoint", False, "No admin token or assignment ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/practice/procedure-assignments/{self.test_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    
                    # Check ALL required fields for PDF generation
                    required_fields = [
                        "id", "procedureName", "dentistName", "performedDate", 
                        "practiceNotes", "customInstructions", "followUpDate"
                    ]
                    
                    missing_fields = []
                    present_fields = []
                    
                    for field in required_fields:
                        if field in assignment and assignment[field] is not None:
                            present_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    # Additional checks for PDF generation
                    pdf_ready = True
                    pdf_issues = []
                    
                    # Check if procedureName is not empty
                    if not assignment.get("procedureName", "").strip():
                        pdf_issues.append("procedureName is empty")
                        pdf_ready = False
                    
                    # Check if dentistName is not empty
                    if not assignment.get("dentistName", "").strip():
                        pdf_issues.append("dentistName is empty")
                        pdf_ready = False
                    
                    # Check if customInstructions is a list
                    if not isinstance(assignment.get("customInstructions"), list):
                        pdf_issues.append("customInstructions is not a list")
                        pdf_ready = False
                    
                    # Check if performedDate is valid
                    performed_date = assignment.get("performedDate")
                    if performed_date:
                        try:
                            if isinstance(performed_date, str):
                                datetime.fromisoformat(performed_date.replace('Z', '+00:00'))
                        except:
                            pdf_issues.append("performedDate format is invalid")
                            pdf_ready = False
                    
                    if not missing_fields and pdf_ready:
                        self.log_test("PDF Data Endpoint", True, 
                                    f"PDF READY - All required fields present: {', '.join(present_fields)}. Procedure: {assignment.get('procedureName', 'Unknown')} by {assignment.get('dentistName', 'Unknown')}")
                        return True
                    else:
                        issues = []
                        if missing_fields:
                            issues.append(f"Missing fields: {missing_fields}")
                        if pdf_issues:
                            issues.append(f"PDF issues: {pdf_issues}")
                        
                        self.log_test("PDF Data Endpoint", False, f"PDF NOT READY - {'; '.join(issues)}")
                        return False
                else:
                    self.log_test("PDF Data Endpoint", False, "Invalid response format")
                    return False
            else:
                self.log_test("PDF Data Endpoint", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PDF Data Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_procedure_detail_endpoint(self):
        """Test if we can get detailed procedure information for PDF content"""
        try:
            # Test with a common procedure ID
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check fields needed for PDF content
                    pdf_content_fields = [
                        "name", "overview", "immediateAftercare", "dietRestrictions", 
                        "warningSignsToCallDoctor", "recoveryTimeline", "medications"
                    ]
                    
                    missing_content = []
                    present_content = []
                    
                    for field in pdf_content_fields:
                        if field in procedure and procedure[field]:
                            present_content.append(field)
                        else:
                            missing_content.append(field)
                    
                    if not missing_content:
                        self.log_test("Procedure Detail Endpoint", True, 
                                    f"PDF CONTENT READY - All content fields present: {', '.join(present_content)}")
                        return True
                    else:
                        self.log_test("Procedure Detail Endpoint", False, 
                                    f"PDF CONTENT INCOMPLETE - Missing: {missing_content}")
                        return False
                else:
                    self.log_test("Procedure Detail Endpoint", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Detail Endpoint", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Detail Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_multiple_assignments_for_pdf(self):
        """Test multiple procedure assignments to ensure PDF generation works for different procedures"""
        if not self.admin_token:
            self.log_test("Multiple Assignments PDF Test", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    recent_procedures = dashboard_data.get("recentProcedures", [])
                    
                    if len(recent_procedures) >= 2:
                        pdf_ready_count = 0
                        tested_assignments = []
                        
                        # Test up to 3 assignments
                        for i, assignment in enumerate(recent_procedures[:3]):
                            assignment_id = assignment.get("id")
                            if assignment_id:
                                # Test this assignment
                                assign_response = self.session.get(f"{self.base_url}/practice/procedure-assignments/{assignment_id}", headers=headers)
                                
                                if assign_response.status_code == 200:
                                    assign_data = assign_response.json()
                                    if assign_data.get("success") and "data" in assign_data:
                                        assign_details = assign_data["data"]
                                        
                                        # Check if this assignment is PDF ready
                                        required_fields = ["procedureName", "dentistName", "performedDate", "practiceNotes", "customInstructions"]
                                        is_pdf_ready = all(field in assign_details and assign_details[field] is not None for field in required_fields)
                                        
                                        if is_pdf_ready:
                                            pdf_ready_count += 1
                                        
                                        tested_assignments.append({
                                            "procedure": assign_details.get("procedureName", "Unknown"),
                                            "pdf_ready": is_pdf_ready
                                        })
                        
                        if pdf_ready_count > 0:
                            ready_list = [f"{a['procedure']} ({'READY' if a['pdf_ready'] else 'NOT READY'})" for a in tested_assignments]
                            self.log_test("Multiple Assignments PDF Test", True, 
                                        f"{pdf_ready_count}/{len(tested_assignments)} assignments are PDF ready. Tested: {ready_list}")
                            return True
                        else:
                            self.log_test("Multiple Assignments PDF Test", False, 
                                        f"0/{len(tested_assignments)} assignments are PDF ready")
                            return False
                    else:
                        self.log_test("Multiple Assignments PDF Test", True, 
                                    f"Only {len(recent_procedures)} assignment(s) available - limited testing but functional")
                        return True
                else:
                    self.log_test("Multiple Assignments PDF Test", False, "Invalid response format")
                    return False
            else:
                self.log_test("Multiple Assignments PDF Test", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Multiple Assignments PDF Test", False, f"Exception: {str(e)}")
            return False

    def test_pdf_endpoint_error_handling(self):
        """Test error handling for PDF generation endpoints"""
        if not self.admin_token:
            self.log_test("PDF Endpoint Error Handling", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test with invalid assignment ID
            invalid_id = "invalid-assignment-id-12345"
            response = self.session.get(f"{self.base_url}/practice/procedure-assignments/{invalid_id}", headers=headers)
            
            if response.status_code == 404:
                error_data = response.json()
                if "detail" in error_data:
                    self.log_test("PDF Endpoint Error Handling", True, 
                                f"Proper 404 error handling for invalid assignment ID: {error_data['detail']}")
                    return True
                else:
                    self.log_test("PDF Endpoint Error Handling", False, "404 status but missing error detail")
                    return False
            else:
                self.log_test("PDF Endpoint Error Handling", False, f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PDF Endpoint Error Handling", False, f"Exception: {str(e)}")
            return False

    def test_unauthorized_pdf_access(self):
        """Test unauthorized access to PDF generation endpoints"""
        try:
            # Test without token
            response = self.session.get(f"{self.base_url}/practice/procedure-assignments/test-id")
            
            if response.status_code == 401:
                self.log_test("Unauthorized PDF Access", True, 
                            "Properly blocked unauthorized access to PDF data endpoint")
                return True
            else:
                self.log_test("Unauthorized PDF Access", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized PDF Access", False, f"Exception: {str(e)}")
            return False

    def run_pdf_generation_tests(self):
        """Run all PDF generation related tests"""
        print(f"Starting PDF Generation Backend Tests")
        print(f"Testing against: {self.base_url}")
        print(f"Focus: PDF generation endpoints and data integrity")
        print("=" * 70)
        
        # Authentication test
        auth_tests = [
            self.test_practice_admin_login,
        ]
        
        # Core PDF generation tests
        pdf_tests = [
            self.test_get_available_assignments,
            self.test_pdf_data_endpoint,
            self.test_procedure_detail_endpoint,
            self.test_multiple_assignments_for_pdf,
        ]
        
        # Security and error handling tests
        security_tests = [
            self.test_pdf_endpoint_error_handling,
            self.test_unauthorized_pdf_access,
        ]
        
        all_tests = auth_tests + pdf_tests + security_tests
        
        passed = 0
        total = len(all_tests)
        
        print("Running Authentication for PDF Generation...")
        for test in auth_tests:
            if test():
                passed += 1
            print()
        
        print("Running PDF Generation Core Tests...")
        for test in pdf_tests:
            if test():
                passed += 1
            print()
        
        print("Running Security & Error Handling Tests...")
        for test in security_tests:
            if test():
                passed += 1
            print()
        
        print("=" * 70)
        print(f"PDF Generation Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("All PDF generation tests passed! Backend is ready for PDF functionality.")
            return True
        else:
            print(f"{total - passed} test(s) failed. PDF generation may have issues.")
            return False

def main():
    """Main function to run the PDF generation tests"""
    tester = PDFGenerationTester(BACKEND_URL)
    
    # Run PDF generation focused tests
    success = tester.run_pdf_generation_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()