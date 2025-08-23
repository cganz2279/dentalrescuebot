#!/usr/bin/env python3
"""
Procedure Assignment Endpoints Testing
Tests the specific endpoints needed for editing procedure notes functionality
"""

import requests
import json
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Get backend URL from frontend .env file
BACKEND_URL = "https://carebot-1.preview.emergentagent.com/api"

class ProcedureAssignmentTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
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
        """Test practice admin login with correct credentials"""
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

    def test_check_existing_assignments(self):
        """Check if there are existing procedure assignments in the database"""
        if not self.admin_token:
            self.log_test("Check Existing Assignments", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            # Try to get practice dashboard to see recent procedures
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
                            self.log_test("Check Existing Assignments", True, 
                                        f"Found {len(recent_procedures)} existing assignments. Using ID: {self.test_assignment_id}")
                            return True
                    
                    # If no existing assignments, create one for testing
                    self.log_test("Check Existing Assignments", True, "No existing assignments found - will create one for testing")
                    return self.create_test_assignment()
                else:
                    self.log_test("Check Existing Assignments", False, "Invalid response format")
                    return False
            else:
                self.log_test("Check Existing Assignments", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Check Existing Assignments", False, f"Exception: {str(e)}")
            return False

    def create_test_assignment(self):
        """Create a test procedure assignment if none exist"""
        try:
            # First, get or create a test patient
            test_patient_id = "2c5fcd14-5eba-4f4a-aa25-ed8054b8f86c"  # Use existing patient
            
            # Create assignment data
            assignment_data = {
                "patientId": test_patient_id,
                "procedureId": "root-canal-therapy",
                "procedureName": "Root Canal Therapy",
                "performedDate": datetime.utcnow().isoformat() + "Z",
                "dentistName": "Dr. Craig Admin",
                "practiceNotes": "Test procedure assignment for editing functionality",
                "customInstructions": ["Take prescribed medication", "Avoid hard foods"],
                "followUpDate": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/practice/assign-procedure", json=assignment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    self.test_assignment_id = assignment["assignmentId"]
                    self.log_test("Create Test Assignment", True, f"Created test assignment: {assignment['procedureName']}")
                    return True
                else:
                    self.log_test("Create Test Assignment", False, "Invalid response format")
                    return False
            else:
                self.log_test("Create Test Assignment", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Test Assignment", False, f"Exception: {str(e)}")
            return False

    def test_get_procedure_assignment(self):
        """Test GET /api/practice/procedure-assignments/{assignment_id} endpoint"""
        if not self.admin_token or not self.test_assignment_id:
            self.log_test("GET Procedure Assignment", False, "No admin token or assignment ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/practice/procedure-assignments/{self.test_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    
                    # Check required fields for procedure assignment
                    required_fields = ["id", "procedureName", "dentistName", "performedDate", "practiceNotes", "customInstructions", "followUpDate"]
                    missing_fields = [field for field in required_fields if field not in assignment]
                    
                    if not missing_fields:
                        self.log_test("GET Procedure Assignment", True, 
                                    f"Successfully retrieved assignment: {assignment.get('procedureName', 'Unknown')} by {assignment.get('dentistName', 'Unknown')}")
                        print(f"   Assignment Data: {json.dumps(assignment, indent=2, default=str)}")
                        return True
                    else:
                        self.log_test("GET Procedure Assignment", False, f"Missing required fields: {missing_fields}")
                        return False
                else:
                    self.log_test("GET Procedure Assignment", False, "Invalid response format")
                    return False
            else:
                self.log_test("GET Procedure Assignment", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET Procedure Assignment", False, f"Exception: {str(e)}")
            return False

    def test_update_procedure_assignment(self):
        """Test PUT /api/practice/procedure-assignments/{assignment_id} endpoint"""
        if not self.admin_token or not self.test_assignment_id:
            self.log_test("PUT Procedure Assignment", False, "No admin token or assignment ID available")
            return False
            
        try:
            # Prepare update data with all the fields mentioned in the requirements
            update_data = {
                "practiceNotes": "UPDATED: Patient responded excellently to treatment. No complications observed. Healing progressing as expected.",
                "customInstructions": [
                    "Take prescribed antibiotics (Amoxicillin 500mg) three times daily for 7 days",
                    "Avoid hard, crunchy foods for 48-72 hours",
                    "Use warm salt water rinse (1 tsp salt in 8oz warm water) twice daily",
                    "Apply ice pack for 15 minutes every hour for first 24 hours if swelling occurs",
                    "Return immediately if experiencing severe pain, excessive bleeding, or signs of infection"
                ],
                "followUpDate": (datetime.utcnow() + timedelta(days=14)).isoformat() + "Z",
                "performedDate": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.put(f"{self.base_url}/practice/procedure-assignments/{self.test_assignment_id}", 
                                      json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("PUT Procedure Assignment", True, 
                                f"Successfully updated assignment with new notes, instructions, follow-up date, and performed date")
                    print(f"   Update Data: {json.dumps(update_data, indent=2, default=str)}")
                    return True
                else:
                    self.log_test("PUT Procedure Assignment", False, "Invalid response format")
                    return False
            else:
                self.log_test("PUT Procedure Assignment", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT Procedure Assignment", False, f"Exception: {str(e)}")
            return False

    def test_verify_update(self):
        """Verify that the update was successful by retrieving the assignment again"""
        if not self.admin_token or not self.test_assignment_id:
            self.log_test("Verify Update", False, "No admin token or assignment ID available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/practice/procedure-assignments/{self.test_assignment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    assignment = data["data"]
                    
                    # Check if the update was applied
                    updated_notes = assignment.get("practiceNotes", "")
                    updated_instructions = assignment.get("customInstructions", [])
                    
                    if "UPDATED:" in updated_notes and len(updated_instructions) == 5:
                        self.log_test("Verify Update", True, 
                                    f"Update verified: Notes and instructions were successfully updated")
                        return True
                    else:
                        self.log_test("Verify Update", False, 
                                    f"Update not reflected: Notes contain 'UPDATED:': {'UPDATED:' in updated_notes}, Instructions count: {len(updated_instructions)}")
                        return False
                else:
                    self.log_test("Verify Update", False, "Invalid response format")
                    return False
            else:
                self.log_test("Verify Update", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Update", False, f"Exception: {str(e)}")
            return False
    
    def run_procedure_assignment_tests(self):
        """Run all procedure assignment tests"""
        print(f"🧪 Testing Procedure Assignment Endpoints for Editing Procedure Notes")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_practice_admin_login,
            self.test_check_existing_assignments,
            self.test_get_procedure_assignment,
            self.test_update_procedure_assignment,
            self.test_verify_update,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        print("=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All procedure assignment tests passed! Endpoints are working correctly.")
            print("\n📋 Summary:")
            print("✅ GET /api/practice/procedure-assignments/{assignment_id} - Successfully loads procedure assignment data")
            print("✅ PUT /api/practice/procedure-assignments/{assignment_id} - Successfully updates practiceNotes, customInstructions, followUpDate, performedDate")
            print("✅ Authentication working with practice admin credentials (cganz2279@gmail.com/admin123)")
            print("✅ Data persistence verified - updates are saved and retrievable")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the procedure assignment tests"""
    tester = ProcedureAssignmentTester(BACKEND_URL)
    success = tester.run_procedure_assignment_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()