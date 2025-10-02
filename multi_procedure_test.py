#!/usr/bin/env python3
"""
Multi-Procedure Assignment Backend Testing
Testing the new /api/practice/assign-multiple-procedures endpoint and models
"""

import requests
import json
import sys
from datetime import datetime, timezone
import uuid

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class MultiProcedureAssignmentTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.test_patient_id = None
        self.test_procedures = []
        self.assignment_ids = []
        self.results = {
            "authentication": False,
            "new_models": False,
            "new_endpoint": False,
            "database_verification": False,
            "backward_compatibility": False,
            "error_handling": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": []
        }

    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def authenticate(self):
        """Test authentication with existing credentials"""
        self.log("🔐 Testing Authentication...")
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.auth_token = data["token"]
                    self.practice_id = data.get("user", {}).get("practiceId")
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log(f"✅ Authentication successful - Practice ID: {self.practice_id}")
                    self.results["authentication"] = True
                    return True
                else:
                    self.log(f"❌ Authentication failed - Invalid response: {data}")
                    return False
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False

    def get_test_patient(self):
        """Get or create a test patient for procedure assignment"""
        self.log("👤 Getting test patient...")
        try:
            # Get existing patients
            response = self.session.get(f"{BACKEND_URL}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    patients = data["data"]
                    if patients:
                        # Use first available patient
                        self.test_patient_id = patients[0]["id"]
                        patient_name = f"{patients[0]['firstName']} {patients[0]['lastName']}"
                        self.log(f"✅ Using existing patient: {patient_name} (ID: {self.test_patient_id})")
                        return True
            
            # Create a test patient if none exist
            self.log("Creating test patient...")
            test_patient_data = {
                "email": f"test.patient.{uuid.uuid4().hex[:8]}@example.com",
                "firstName": "Multi",
                "lastName": "ProcedureTest",
                "cellphone": "555-123-4567"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/patients",
                json=test_patient_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    self.test_patient_id = data["data"]["id"]
                    self.log(f"✅ Created test patient: {self.test_patient_id}")
                    return True
            
            self.log(f"❌ Failed to get/create test patient: {response.text}")
            return False
            
        except Exception as e:
            self.log(f"❌ Error getting test patient: {str(e)}", "ERROR")
            return False

    def get_test_procedures(self):
        """Get available procedures for testing"""
        self.log("🔍 Getting test procedures...")
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    procedures = data["data"]
                    # Get first 3 procedures for testing (minimum required)
                    self.test_procedures = procedures[:3]
                    procedure_names = [p["name"] for p in self.test_procedures]
                    self.log(f"✅ Got {len(self.test_procedures)} test procedures: {', '.join(procedure_names)}")
                    return True
            
            self.log(f"❌ Failed to get procedures: {response.text}")
            return False
            
        except Exception as e:
            self.log(f"❌ Error getting procedures: {str(e)}", "ERROR")
            return False

    def test_new_models(self):
        """Test the new MultiProcedureAssignment and ProcedureItem models"""
        self.log("📋 Testing New Models (MultiProcedureAssignment and ProcedureItem)...")
        self.results["total_tests"] += 1
        
        try:
            # Test model validation by sending invalid data
            invalid_data = {
                "patientId": "",  # Invalid empty patient ID
                "procedures": [],  # Invalid empty procedures list
                "performedDate": "invalid-date",  # Invalid date format
                "dentistName": ""  # Invalid empty dentist name
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/assign-multiple-procedures",
                json=invalid_data
            )
            
            # Should return validation error (422 or 400)
            if response.status_code in [400, 422]:
                self.log("✅ Model validation working - rejected invalid data")
                self.results["new_models"] = True
                self.results["passed_tests"] += 1
                return True
            else:
                self.log(f"❌ Model validation failed - Status: {response.status_code}, Response: {response.text}")
                self.results["failed_tests"].append("Model validation not working properly")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing models: {str(e)}", "ERROR")
            self.results["failed_tests"].append(f"Model testing error: {str(e)}")
            return False

    def test_new_endpoint(self):
        """Test the new /api/practice/assign-multiple-procedures endpoint"""
        self.log("🎯 Testing New Multi-Procedure Assignment Endpoint...")
        self.results["total_tests"] += 1
        
        if not self.test_patient_id or not self.test_procedures:
            self.log("❌ Missing test patient or procedures")
            self.results["failed_tests"].append("Missing test data for endpoint testing")
            return False
        
        try:
            # Prepare test data with multiple procedures (minimum 2-3 as requested)
            procedure_items = []
            for proc in self.test_procedures[:3]:  # Use 3 procedures minimum as requested
                procedure_items.append({
                    "procedureId": proc["id"],
                    "procedureName": proc["name"]
                })
            
            assignment_data = {
                "patientId": self.test_patient_id,
                "procedures": procedure_items,
                "performedDate": datetime.now(timezone.utc).isoformat(),
                "dentistName": "Dr. Multi Procedure Test",
                "practiceNotes": "Test multi-procedure assignment functionality",
                "customInstructions": ["Follow all post-op instructions carefully", "Take medications as prescribed"],
                "followUpDate": datetime.now(timezone.utc).isoformat()
            }
            
            self.log(f"Assigning {len(procedure_items)} procedures to patient {self.test_patient_id}")
            for i, proc in enumerate(procedure_items, 1):
                self.log(f"  {i}. {proc['procedureName']} (ID: {proc['procedureId']})")
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/assign-multiple-procedures",
                json=assignment_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assignment_ids = data.get("data", {}).get("assignmentIds", [])
                    procedure_count = data.get("data", {}).get("procedureCount", 0)
                    patient_name = data.get("data", {}).get("patientName", "Unknown")
                    
                    if len(assignment_ids) == len(procedure_items) and procedure_count == len(procedure_items):
                        self.log(f"✅ Multi-procedure assignment successful!")
                        self.log(f"   Patient: {patient_name}")
                        self.log(f"   Procedures assigned: {procedure_count}")
                        self.log(f"   Assignment IDs: {assignment_ids}")
                        
                        self.results["new_endpoint"] = True
                        self.results["passed_tests"] += 1
                        
                        # Store assignment IDs for database verification
                        self.assignment_ids = assignment_ids
                        return True
                    else:
                        self.log(f"❌ Assignment count mismatch - Expected: {len(procedure_items)}, Got: {procedure_count}")
                        self.results["failed_tests"].append("Assignment count mismatch")
                        return False
                else:
                    self.log(f"❌ Assignment failed - Response: {data}")
                    self.results["failed_tests"].append(f"Assignment failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log(f"❌ Endpoint failed - Status: {response.status_code}, Response: {response.text}")
                self.results["failed_tests"].append(f"Endpoint returned {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing endpoint: {str(e)}", "ERROR")
            self.results["failed_tests"].append(f"Endpoint testing error: {str(e)}")
            return False

    def test_database_verification(self):
        """Verify that multiple procedure assignments are created in patientprocedures collection"""
        self.log("🗄️ Testing Database Verification...")
        self.results["total_tests"] += 1
        
        if not self.assignment_ids:
            self.log("❌ No assignment IDs to verify")
            self.results["failed_tests"].append("No assignment IDs for database verification")
            return False
        
        try:
            # Get dashboard data to check recent procedures
            response = self.session.get(f"{BACKEND_URL}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    recent_procedures = data["data"].get("recentProcedures", [])
                    
                    # Check if our assignments are in the recent procedures
                    found_assignments = []
                    multi_procedure_flags = 0
                    batch_ids = set()
                    
                    for assignment_id in self.assignment_ids:
                        for proc in recent_procedures:
                            if proc.get("id") == assignment_id:
                                found_assignments.append(assignment_id)
                                
                                # Check for multi-procedure assignment flags
                                if proc.get("isMultiProcedureAssignment"):
                                    multi_procedure_flags += 1
                                    self.log(f"✅ Found isMultiProcedureAssignment=true for {assignment_id}")
                                
                                if proc.get("batchId"):
                                    batch_ids.add(proc.get("batchId"))
                                    self.log(f"✅ Found batchId for {assignment_id}: {proc.get('batchId')}")
                                break
                    
                    if len(found_assignments) == len(self.assignment_ids):
                        self.log(f"✅ Database verification successful!")
                        self.log(f"   Found all {len(found_assignments)} assignments in database")
                        self.log(f"   Multi-procedure flags: {multi_procedure_flags}/{len(self.assignment_ids)}")
                        self.log(f"   Unique batch IDs: {len(batch_ids)}")
                        
                        self.results["database_verification"] = True
                        self.results["passed_tests"] += 1
                        return True
                    else:
                        self.log(f"❌ Database verification failed - Found {len(found_assignments)}/{len(self.assignment_ids)} assignments")
                        self.results["failed_tests"].append("Not all assignments found in database")
                        return False
                else:
                    self.log(f"❌ Dashboard data unavailable: {data}")
                    self.results["failed_tests"].append("Dashboard data unavailable for verification")
                    return False
            else:
                self.log(f"❌ Dashboard request failed - Status: {response.status_code}")
                self.results["failed_tests"].append("Dashboard request failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Error verifying database: {str(e)}", "ERROR")
            self.results["failed_tests"].append(f"Database verification error: {str(e)}")
            return False

    def test_backward_compatibility(self):
        """Test that existing single procedure assignment endpoint still works"""
        self.log("🔄 Testing Backward Compatibility...")
        self.results["total_tests"] += 1
        
        if not self.test_patient_id or not self.test_procedures:
            self.log("❌ Missing test patient or procedures")
            self.results["failed_tests"].append("Missing test data for backward compatibility testing")
            return False
        
        try:
            # Test single procedure assignment (old endpoint)
            single_assignment_data = {
                "patientId": self.test_patient_id,
                "procedureId": self.test_procedures[0]["id"],
                "procedureName": self.test_procedures[0]["name"],
                "performedDate": datetime.now(timezone.utc).isoformat(),
                "dentistName": "Dr. Backward Compatibility Test",
                "practiceNotes": "Testing backward compatibility with single procedure assignment"
            }
            
            self.log(f"Testing single procedure assignment: {single_assignment_data['procedureName']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/practice/assign-procedure",
                json=single_assignment_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assignment_id = data.get("data", {}).get("assignmentId")
                    patient_name = data.get("data", {}).get("patientName", "Unknown")
                    procedure_name = data.get("data", {}).get("procedureName", "Unknown")
                    
                    self.log(f"✅ Backward compatibility successful!")
                    self.log(f"   Single assignment ID: {assignment_id}")
                    self.log(f"   Patient: {patient_name}")
                    self.log(f"   Procedure: {procedure_name}")
                    
                    self.results["backward_compatibility"] = True
                    self.results["passed_tests"] += 1
                    return True
                else:
                    self.log(f"❌ Single assignment failed: {data}")
                    self.results["failed_tests"].append("Single procedure assignment failed")
                    return False
            else:
                self.log(f"❌ Single assignment endpoint failed - Status: {response.status_code}, Response: {response.text}")
                self.results["failed_tests"].append("Single assignment endpoint not working")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing backward compatibility: {str(e)}", "ERROR")
            self.results["failed_tests"].append(f"Backward compatibility error: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling with invalid data"""
        self.log("⚠️ Testing Error Handling...")
        self.results["total_tests"] += 1
        
        try:
            test_cases = [
                {
                    "name": "Missing patient",
                    "data": {
                        "patientId": "non-existent-patient-id",
                        "procedures": [{"procedureId": "test", "procedureName": "Test"}],
                        "performedDate": datetime.now(timezone.utc).isoformat(),
                        "dentistName": "Dr. Test"
                    },
                    "expected_status": 404
                },
                {
                    "name": "Invalid procedures",
                    "data": {
                        "patientId": self.test_patient_id,
                        "procedures": [{"procedureId": "non-existent-procedure", "procedureName": "Invalid"}],
                        "performedDate": datetime.now(timezone.utc).isoformat(),
                        "dentistName": "Dr. Test"
                    },
                    "expected_status": 404
                },
                {
                    "name": "Empty procedures list",
                    "data": {
                        "patientId": self.test_patient_id,
                        "procedures": [],
                        "performedDate": datetime.now(timezone.utc).isoformat(),
                        "dentistName": "Dr. Test"
                    },
                    "expected_status": [400, 422]
                }
            ]
            
            passed_error_tests = 0
            for test_case in test_cases:
                self.log(f"Testing error case: {test_case['name']}")
                
                response = self.session.post(
                    f"{BACKEND_URL}/practice/assign-multiple-procedures",
                    json=test_case["data"]
                )
                
                expected_statuses = test_case["expected_status"] if isinstance(test_case["expected_status"], list) else [test_case["expected_status"]]
                
                if response.status_code in expected_statuses:
                    self.log(f"✅ Error handling test '{test_case['name']}' passed - Status: {response.status_code}")
                    passed_error_tests += 1
                else:
                    self.log(f"❌ Error handling test '{test_case['name']}' failed - Expected: {expected_statuses}, Got: {response.status_code}")
            
            if passed_error_tests == len(test_cases):
                self.log(f"✅ All error handling tests passed ({passed_error_tests}/{len(test_cases)})")
                self.results["error_handling"] = True
                self.results["passed_tests"] += 1
                return True
            else:
                self.log(f"❌ Error handling tests failed ({passed_error_tests}/{len(test_cases)} passed)")
                self.results["failed_tests"].append(f"Error handling tests failed ({passed_error_tests}/{len(test_cases)} passed)")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing error handling: {str(e)}", "ERROR")
            self.results["failed_tests"].append(f"Error handling testing error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting Multi-Procedure Assignment Backend Testing...")
        self.log("="*70)
        
        # Test sequence
        tests = [
            ("Authentication", self.authenticate),
            ("Get Test Patient", self.get_test_patient),
            ("Get Test Procedures", self.get_test_procedures),
            ("New Models", self.test_new_models),
            ("New Endpoint", self.test_new_endpoint),
            ("Database Verification", self.test_database_verification),
            ("Backward Compatibility", self.test_backward_compatibility),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running {test_name} Test ---")
            if not test_func():
                self.log(f"❌ {test_name} test failed - continuing with remaining tests")
        
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*70)
        self.log("🎯 MULTI-PROCEDURE ASSIGNMENT TEST SUMMARY")
        self.log("="*70)
        
        # Test results
        test_results = [
            ("Authentication Test", self.results["authentication"]),
            ("New Models Test", self.results["new_models"]),
            ("New Endpoint Test", self.results["new_endpoint"]),
            ("Database Verification", self.results["database_verification"]),
            ("Backward Compatibility", self.results["backward_compatibility"]),
            ("Error Handling", self.results["error_handling"])
        ]
        
        for test_name, passed in test_results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"{test_name}: {status}")
        
        self.log(f"\nTotal Tests: {self.results['total_tests']}")
        self.log(f"Passed: {self.results['passed_tests']}")
        self.log(f"Failed: {len(self.results['failed_tests'])}")
        
        if self.results["failed_tests"]:
            self.log("\n❌ FAILED TESTS:")
            for failure in self.results["failed_tests"]:
                self.log(f"  - {failure}")
        
        # Overall result
        all_critical_passed = all([
            self.results["authentication"],
            self.results["new_endpoint"],
            self.results["database_verification"]
        ])
        
        if all_critical_passed:
            self.log("\n🎉 CRITICAL TESTS PASSED - Multi-procedure assignment functionality is working!")
        else:
            self.log("\n❌ CRITICAL TESTS FAILED - Multi-procedure assignment needs attention!")
        
        self.log("="*70)

if __name__ == "__main__":
    tester = MultiProcedureAssignmentTester()
    tester.run_all_tests()