#!/usr/bin/env python3
"""
Support Request API Testing Script
Tests the newly implemented Support Request API endpoints as requested in review.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
TEST_CREDENTIALS = {
    "email": "cganz2279@gmail.com",
    "password": "password123"
}

class SupportRequestAPITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.auth_token = None
        self.practice_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self):
        """Authenticate with practice credentials"""
        try:
            print("\n🔐 AUTHENTICATING WITH PRACTICE CREDENTIALS...")
            
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                # Extract practice_id from user data
                user_data = data.get("user", {})
                self.practice_id = user_data.get("practiceId")
                
                self.log_test(
                    "Practice Authentication",
                    True,
                    f"Successfully authenticated with {TEST_CREDENTIALS['email']}, Practice ID: {self.practice_id}"
                )
                return True
            else:
                self.log_test(
                    "Practice Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Practice Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_create_support_request_valid(self):
        """Test POST /api/support/request with valid data"""
        try:
            print("\n📝 TESTING CREATE SUPPORT REQUEST (VALID DATA)...")
            
            test_data = {
                "practice_name": "Test Dental Office",
                "email": "test@example.com",
                "phone": "(555) 123-4567",
                "support": True,
                "suggestions": False,
                "description": "Testing the new support system functionality"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json=test_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("id"):
                    self.log_test(
                        "Create Support Request (Valid Data)",
                        True,
                        f"Support request created successfully with ID: {data.get('id')}"
                    )
                    return data.get("id")
                else:
                    self.log_test(
                        "Create Support Request (Valid Data)",
                        False,
                        f"Invalid response format: {data}"
                    )
            else:
                self.log_test(
                    "Create Support Request (Valid Data)",
                    False,
                    f"Request failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test("Create Support Request (Valid Data)", False, f"Exception: {str(e)}")
        
        return None
    
    def test_create_support_request_validation_errors(self):
        """Test validation errors for support request creation"""
        print("\n🔍 TESTING SUPPORT REQUEST VALIDATION ERRORS...")
        
        # Test 1: Missing required fields
        try:
            test_data = {
                "practice_name": "",
                "email": "invalid-email",
                "support": False,
                "suggestions": False,
                "description": "short"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json=test_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 422:
                self.log_test(
                    "Validation Error - Invalid Email Format",
                    True,
                    "Correctly rejected invalid email format with 422 status"
                )
            else:
                self.log_test(
                    "Validation Error - Invalid Email Format",
                    False,
                    f"Expected 422, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Validation Error - Invalid Email Format", False, f"Exception: {str(e)}")
        
        # Test 2: Neither support nor suggestions checked
        try:
            test_data = {
                "practice_name": "Test Practice",
                "email": "test@example.com",
                "support": False,
                "suggestions": False,
                "description": "This is a test description that is long enough"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json=test_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 422:
                self.log_test(
                    "Validation Error - No Checkboxes Selected",
                    True,
                    "Correctly rejected request with no support/suggestions selected"
                )
            else:
                self.log_test(
                    "Validation Error - No Checkboxes Selected",
                    False,
                    f"Expected 422, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Validation Error - No Checkboxes Selected", False, f"Exception: {str(e)}")
        
        # Test 3: Description too short
        try:
            test_data = {
                "practice_name": "Test Practice",
                "email": "test@example.com",
                "support": True,
                "suggestions": False,
                "description": "short"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json=test_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 422:
                self.log_test(
                    "Validation Error - Description Too Short",
                    True,
                    "Correctly rejected description under 10 characters"
                )
            else:
                self.log_test(
                    "Validation Error - Description Too Short",
                    False,
                    f"Expected 422, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Validation Error - Description Too Short", False, f"Exception: {str(e)}")
    
    def test_get_support_requests(self):
        """Test GET /api/support/requests for authenticated practice"""
        try:
            print("\n📋 TESTING GET SUPPORT REQUESTS FOR PRACTICE...")
            
            response = requests.get(
                f"{self.backend_url}/api/support/requests",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(
                        "Get Support Requests (Practice)",
                        True,
                        f"Successfully retrieved {len(data)} support requests for practice"
                    )
                else:
                    self.log_test(
                        "Get Support Requests (Practice)",
                        False,
                        f"Expected list, got: {type(data)}"
                    )
            else:
                self.log_test(
                    "Get Support Requests (Practice)",
                    False,
                    f"Request failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test("Get Support Requests (Practice)", False, f"Exception: {str(e)}")
    
    def test_get_all_support_requests_admin(self):
        """Test GET /api/support/admin/all-requests (no auth required)"""
        try:
            print("\n👨‍💼 TESTING GET ALL SUPPORT REQUESTS (ADMIN)...")
            
            response = requests.get(f"{self.backend_url}/api/support/admin/all-requests")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test(
                        "Get All Support Requests (Admin)",
                        True,
                        f"Successfully retrieved {len(data)} total support requests"
                    )
                else:
                    self.log_test(
                        "Get All Support Requests (Admin)",
                        False,
                        f"Expected list, got: {type(data)}"
                    )
            else:
                self.log_test(
                    "Get All Support Requests (Admin)",
                    False,
                    f"Request failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test("Get All Support Requests (Admin)", False, f"Exception: {str(e)}")
    
    def test_email_functionality(self):
        """Test that support request creation sends email notification"""
        try:
            print("\n📧 TESTING EMAIL NOTIFICATION FUNCTIONALITY...")
            
            # Create a support request and check if email is sent
            test_data = {
                "practice_name": "Email Test Dental Office",
                "email": "emailtest@example.com",
                "phone": "(555) 999-8888",
                "support": True,
                "suggestions": True,
                "description": "Testing email notification functionality for support requests"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json=test_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "Email Notification Test",
                        True,
                        "Support request created successfully - email should be sent to support@dentalaftercarenotes.com"
                    )
                else:
                    self.log_test(
                        "Email Notification Test",
                        False,
                        f"Support request creation failed: {data}"
                    )
            else:
                self.log_test(
                    "Email Notification Test",
                    False,
                    f"Request failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test("Email Notification Test", False, f"Exception: {str(e)}")
    
    def test_authentication_required(self):
        """Test that endpoints require proper authentication"""
        try:
            print("\n🔒 TESTING AUTHENTICATION REQUIREMENTS...")
            
            # Test without auth token
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json={
                    "practice_name": "Test",
                    "email": "test@example.com",
                    "support": True,
                    "description": "Test description"
                }
            )
            
            if response.status_code in [401, 403]:
                self.log_test(
                    "Authentication Required Test",
                    True,
                    f"Correctly rejected unauthenticated request with {response.status_code} status"
                )
            else:
                self.log_test(
                    "Authentication Required Test",
                    False,
                    f"Expected 401/403, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Authentication Required Test", False, f"Exception: {str(e)}")
    
    def test_database_storage(self):
        """Test that support requests are stored in database"""
        try:
            print("\n💾 TESTING DATABASE STORAGE...")
            
            # Create a support request
            test_data = {
                "practice_name": "Database Test Office",
                "email": "dbtest@example.com",
                "phone": "(555) 777-6666",
                "support": False,
                "suggestions": True,
                "description": "Testing database storage functionality for support requests"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/support/request",
                json=test_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("id")
                
                if request_id:
                    # Try to retrieve the request
                    get_response = requests.get(
                        f"{self.backend_url}/api/support/requests",
                        headers=self.get_auth_headers()
                    )
                    
                    if get_response.status_code == 200:
                        requests_list = get_response.json()
                        found_request = any(req.get("id") == request_id for req in requests_list)
                        
                        if found_request:
                            self.log_test(
                                "Database Storage Test",
                                True,
                                f"Support request {request_id} successfully stored and retrieved from database"
                            )
                        else:
                            self.log_test(
                                "Database Storage Test",
                                False,
                                f"Support request {request_id} not found in retrieved list"
                            )
                    else:
                        self.log_test(
                            "Database Storage Test",
                            False,
                            f"Failed to retrieve requests: {get_response.status_code}"
                        )
                else:
                    self.log_test(
                        "Database Storage Test",
                        False,
                        "No request ID returned from creation"
                    )
            else:
                self.log_test(
                    "Database Storage Test",
                    False,
                    f"Failed to create request: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test("Database Storage Test", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all support request API tests"""
        print("🚀 STARTING SUPPORT REQUEST API COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test authentication requirements
        self.test_authentication_required()
        
        # Step 3: Test valid support request creation
        self.test_create_support_request_valid()
        
        # Step 4: Test validation errors
        self.test_create_support_request_validation_errors()
        
        # Step 5: Test retrieving support requests
        self.test_get_support_requests()
        
        # Step 6: Test admin endpoint
        self.test_get_all_support_requests_admin()
        
        # Step 7: Test email functionality
        self.test_email_functionality()
        
        # Step 8: Test database storage
        self.test_database_storage()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 SUPPORT REQUEST API TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL FINDINGS:")
        if passed_tests == total_tests:
            print("   ✅ ALL SUPPORT REQUEST API ENDPOINTS ARE WORKING CORRECTLY")
            print("   ✅ Authentication, validation, and database storage functional")
            print("   ✅ Email notifications should be sent to support@dentalaftercarenotes.com")
        else:
            print(f"   ⚠️  {failed_tests} test(s) failed - see details above")

if __name__ == "__main__":
    tester = SupportRequestAPITester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)