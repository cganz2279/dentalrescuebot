#!/usr/bin/env python3
"""
DENTIST MANAGEMENT API TESTING
Testing the dentist management endpoints to ensure they work correctly with the updated DentistManagementPage.jsx frontend
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
import sys

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from previous testing
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class DentistManagementTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        self.auth_token = None
        self.practice_id = None
        self.created_dentist_ids = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {details}")
    
    def authenticate(self):
        """Authenticate with practice credentials"""
        print("\n🔐 Authenticating with practice credentials...")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.auth_token = data["token"]
                    self.practice_id = data.get("user", {}).get("practiceId")
                    self.log_test(
                        "Practice Authentication",
                        True,
                        f"Successfully authenticated with practice ID: {self.practice_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Practice Authentication",
                        False,
                        f"Login succeeded but missing token or success flag: {data}"
                    )
            else:
                self.log_test(
                    "Practice Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Practice Authentication",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_get_dentists(self):
        """Test GET /api/practice/dentists - Retrieve list of dentists"""
        print("\n📋 Testing GET /api/practice/dentists...")
        
        if not self.auth_token:
            self.log_test("GET Dentists List", False, "No authentication token available")
            return False
        
        try:
            response = requests.get(
                f"{API_BASE}/practice/dentists",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dentists = data["data"]
                    self.log_test(
                        "GET Dentists List",
                        True,
                        f"Successfully retrieved {len(dentists)} dentists"
                    )
                    return data
                else:
                    self.log_test(
                        "GET Dentists List",
                        False,
                        f"Response missing success flag or data: {data}"
                    )
            else:
                self.log_test(
                    "GET Dentists List",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "GET Dentists List",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_add_dentist_valid(self):
        """Test POST /api/practice/dentists with valid data"""
        print("\n➕ Testing POST /api/practice/dentists with valid data...")
        
        if not self.auth_token:
            self.log_test("Add Dentist (Valid)", False, "No authentication token available")
            return False
        
        # Create test dentist with valid email
        test_dentist = {
            "firstName": "Dr. Sarah",
            "lastName": "Johnson",
            "email": f"sarah.johnson.{int(time.time())}@dentalpractice.com",
            "phone": "(555) 123-4567",
            "licenseNumber": "DDS12345",
            "specialties": ["General Dentistry", "Cosmetic Dentistry"]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/dentists",
                json=test_dentist,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    dentist_data = data["data"]
                    dentist_id = dentist_data.get("id")
                    if dentist_id:
                        self.created_dentist_ids.append(dentist_id)
                    
                    self.log_test(
                        "Add Dentist (Valid)",
                        True,
                        f"Successfully added dentist: {dentist_data.get('firstName')} {dentist_data.get('lastName')} (ID: {dentist_id})"
                    )
                    return dentist_data
                else:
                    self.log_test(
                        "Add Dentist (Valid)",
                        False,
                        f"Response missing success flag or data: {data}"
                    )
            else:
                self.log_test(
                    "Add Dentist (Valid)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Add Dentist (Valid)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_add_dentist_invalid_email(self):
        """Test POST /api/practice/dentists with invalid email format"""
        print("\n❌ Testing POST /api/practice/dentists with invalid email...")
        
        if not self.auth_token:
            self.log_test("Add Dentist (Invalid Email)", False, "No authentication token available")
            return False
        
        # Create test dentist with invalid email
        test_dentist = {
            "firstName": "Dr. John",
            "lastName": "Smith",
            "email": "invalid-email-format",  # Invalid email format
            "phone": "(555) 987-6543",
            "licenseNumber": "DDS67890",
            "specialties": ["Orthodontics"]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/dentists",
                json=test_dentist,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            # Should return 422 for validation error
            if response.status_code == 422:
                data = response.json()
                # Check if it's a Pydantic validation error
                if "detail" in data and isinstance(data["detail"], list):
                    validation_errors = data["detail"]
                    email_error = any(
                        ("email" in error.get("loc", []) and "email" in error.get("msg", "").lower())
                        for error in validation_errors
                    )
                    if email_error:
                        self.log_test(
                            "Add Dentist (Invalid Email)",
                            True,
                            f"Correctly rejected invalid email with Pydantic validation error: {validation_errors}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Add Dentist (Invalid Email)",
                            False,
                            f"Validation error but not for email field: {validation_errors}"
                        )
                else:
                    self.log_test(
                        "Add Dentist (Invalid Email)",
                        False,
                        f"422 status but unexpected error format: {data}"
                    )
            else:
                self.log_test(
                    "Add Dentist (Invalid Email)",
                    False,
                    f"Expected 422 validation error, got HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Add Dentist (Invalid Email)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_add_dentist_missing_required_fields(self):
        """Test POST /api/practice/dentists with missing required fields"""
        print("\n❌ Testing POST /api/practice/dentists with missing required fields...")
        
        if not self.auth_token:
            self.log_test("Add Dentist (Missing Fields)", False, "No authentication token available")
            return False
        
        # Create test dentist with missing required fields
        test_dentist = {
            "firstName": "Dr. Jane",
            # Missing lastName and email (required fields)
            "phone": "(555) 111-2222",
            "licenseNumber": "DDS11111"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/dentists",
                json=test_dentist,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            # Should return 422 for validation error
            if response.status_code == 422:
                data = response.json()
                if "detail" in data and isinstance(data["detail"], list):
                    validation_errors = data["detail"]
                    # Check for missing required fields
                    missing_fields = [error.get("loc", [])[-1] for error in validation_errors if error.get("type") == "missing"]
                    if "lastName" in missing_fields and "email" in missing_fields:
                        self.log_test(
                            "Add Dentist (Missing Fields)",
                            True,
                            f"Correctly rejected missing required fields: {missing_fields}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Add Dentist (Missing Fields)",
                            False,
                            f"Validation error but not for expected missing fields: {validation_errors}"
                        )
                else:
                    self.log_test(
                        "Add Dentist (Missing Fields)",
                        False,
                        f"422 status but unexpected error format: {data}"
                    )
            else:
                self.log_test(
                    "Add Dentist (Missing Fields)",
                    False,
                    f"Expected 422 validation error, got HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Add Dentist (Missing Fields)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_update_dentist(self):
        """Test PUT /api/practice/dentists/{dentist_id} - Update existing dentist"""
        print("\n✏️ Testing PUT /api/practice/dentists/{dentist_id}...")
        
        if not self.auth_token:
            self.log_test("Update Dentist", False, "No authentication token available")
            return False
        
        if not self.created_dentist_ids:
            self.log_test("Update Dentist", False, "No dentist available to update")
            return False
        
        dentist_id = self.created_dentist_ids[0]
        
        # Update dentist data
        update_data = {
            "firstName": "Dr. Sarah Updated",
            "phone": "(555) 999-8888",
            "specialties": ["General Dentistry", "Cosmetic Dentistry", "Endodontics"]
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/practice/dentists/{dentist_id}",
                json=update_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    updated_dentist = data["data"]
                    self.log_test(
                        "Update Dentist",
                        True,
                        f"Successfully updated dentist: {updated_dentist.get('firstName')} {updated_dentist.get('lastName')}"
                    )
                    return updated_dentist
                else:
                    self.log_test(
                        "Update Dentist",
                        False,
                        f"Response missing success flag or data: {data}"
                    )
            else:
                self.log_test(
                    "Update Dentist",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Update Dentist",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_update_dentist_invalid_email(self):
        """Test PUT /api/practice/dentists/{dentist_id} with invalid email"""
        print("\n❌ Testing PUT /api/practice/dentists/{dentist_id} with invalid email...")
        
        if not self.auth_token:
            self.log_test("Update Dentist (Invalid Email)", False, "No authentication token available")
            return False
        
        if not self.created_dentist_ids:
            self.log_test("Update Dentist (Invalid Email)", False, "No dentist available to update")
            return False
        
        dentist_id = self.created_dentist_ids[0]
        
        # Update with invalid email
        update_data = {
            "email": "invalid-email-format-update"  # Invalid email format
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/practice/dentists/{dentist_id}",
                json=update_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            # Should return 422 for validation error
            if response.status_code == 422:
                data = response.json()
                if "detail" in data and isinstance(data["detail"], list):
                    validation_errors = data["detail"]
                    email_error = any(
                        ("email" in error.get("loc", []) and "email" in error.get("msg", "").lower())
                        for error in validation_errors
                    )
                    if email_error:
                        self.log_test(
                            "Update Dentist (Invalid Email)",
                            True,
                            f"Correctly rejected invalid email update with Pydantic validation error"
                        )
                        return True
                    else:
                        self.log_test(
                            "Update Dentist (Invalid Email)",
                            False,
                            f"Validation error but not for email field: {validation_errors}"
                        )
                else:
                    self.log_test(
                        "Update Dentist (Invalid Email)",
                        False,
                        f"422 status but unexpected error format: {data}"
                    )
            else:
                self.log_test(
                    "Update Dentist (Invalid Email)",
                    False,
                    f"Expected 422 validation error, got HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Update Dentist (Invalid Email)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_delete_dentist(self):
        """Test DELETE /api/practice/dentists/{dentist_id} - Remove dentist"""
        print("\n🗑️ Testing DELETE /api/practice/dentists/{dentist_id}...")
        
        if not self.auth_token:
            self.log_test("Delete Dentist", False, "No authentication token available")
            return False
        
        if not self.created_dentist_ids:
            self.log_test("Delete Dentist", False, "No dentist available to delete")
            return False
        
        dentist_id = self.created_dentist_ids[0]
        
        try:
            response = requests.delete(
                f"{API_BASE}/practice/dentists/{dentist_id}",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "Delete Dentist",
                        True,
                        f"Successfully removed dentist with ID: {dentist_id}"
                    )
                    # Remove from our tracking list
                    self.created_dentist_ids.remove(dentist_id)
                    return True
                else:
                    self.log_test(
                        "Delete Dentist",
                        False,
                        f"Response missing success flag: {data}"
                    )
            else:
                self.log_test(
                    "Delete Dentist",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Delete Dentist",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_delete_nonexistent_dentist(self):
        """Test DELETE /api/practice/dentists/{dentist_id} with non-existent ID"""
        print("\n❌ Testing DELETE /api/practice/dentists/{dentist_id} with non-existent ID...")
        
        if not self.auth_token:
            self.log_test("Delete Non-existent Dentist", False, "No authentication token available")
            return False
        
        # Use a non-existent dentist ID
        fake_dentist_id = str(uuid.uuid4())
        
        try:
            response = requests.delete(
                f"{API_BASE}/practice/dentists/{fake_dentist_id}",
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            # Should return 404 for not found
            if response.status_code == 404:
                data = response.json()
                if "detail" in data and "not found" in data["detail"].lower():
                    self.log_test(
                        "Delete Non-existent Dentist",
                        True,
                        f"Correctly returned 404 for non-existent dentist ID"
                    )
                    return True
                else:
                    self.log_test(
                        "Delete Non-existent Dentist",
                        False,
                        f"404 status but unexpected error message: {data}"
                    )
            else:
                self.log_test(
                    "Delete Non-existent Dentist",
                    False,
                    f"Expected 404 not found, got HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Delete Non-existent Dentist",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_unauthorized_access(self):
        """Test dentist endpoints without authentication"""
        print("\n🔒 Testing dentist endpoints without authentication...")
        
        endpoints_to_test = [
            ("GET", f"{API_BASE}/practice/dentists"),
            ("POST", f"{API_BASE}/practice/dentists"),
            ("PUT", f"{API_BASE}/practice/dentists/test-id"),
            ("DELETE", f"{API_BASE}/practice/dentists/test-id")
        ]
        
        success_count = 0
        
        for method, url in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(url, timeout=30)
                elif method == "POST":
                    response = requests.post(url, json={}, timeout=30)
                elif method == "PUT":
                    response = requests.put(url, json={}, timeout=30)
                elif method == "DELETE":
                    response = requests.delete(url, timeout=30)
                
                # Should return 401 or 403 for unauthorized access
                if response.status_code in [401, 403]:
                    success_count += 1
                    print(f"  ✅ {method} endpoint correctly rejected unauthorized access (HTTP {response.status_code})")
                else:
                    print(f"  ❌ {method} endpoint should reject unauthorized access, got HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {method} endpoint test failed: {str(e)}")
        
        if success_count == len(endpoints_to_test):
            self.log_test(
                "Unauthorized Access Protection",
                True,
                f"All {len(endpoints_to_test)} endpoints correctly reject unauthorized access"
            )
            return True
        else:
            self.log_test(
                "Unauthorized Access Protection",
                False,
                f"Only {success_count}/{len(endpoints_to_test)} endpoints properly reject unauthorized access"
            )
            return False
    
    def cleanup_created_dentists(self):
        """Clean up any remaining created dentists"""
        print("\n🧹 Cleaning up created dentists...")
        
        if not self.auth_token or not self.created_dentist_ids:
            return
        
        for dentist_id in self.created_dentist_ids[:]:  # Copy list to avoid modification during iteration
            try:
                response = requests.delete(
                    f"{API_BASE}/practice/dentists/{dentist_id}",
                    headers={
                        "Authorization": f"Bearer {self.auth_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"  ✅ Cleaned up dentist ID: {dentist_id}")
                    self.created_dentist_ids.remove(dentist_id)
                else:
                    print(f"  ⚠️ Failed to clean up dentist ID: {dentist_id} (HTTP {response.status_code})")
                    
            except Exception as e:
                print(f"  ❌ Error cleaning up dentist ID {dentist_id}: {str(e)}")
    
    def run_all_tests(self):
        """Run all dentist management API tests"""
        print("🚀 Starting Dentist Management API Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        self.test_get_dentists()
        self.test_add_dentist_valid()
        self.test_add_dentist_invalid_email()
        self.test_add_dentist_missing_required_fields()
        self.test_update_dentist()
        self.test_update_dentist_invalid_email()
        self.test_delete_dentist()
        self.test_delete_nonexistent_dentist()
        self.test_unauthorized_access()
        
        # Clean up
        self.cleanup_created_dentists()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 DENTIST MANAGEMENT API TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"  - {test}")
        
        # Critical assessment
        critical_tests = [
            "Practice Authentication",
            "GET Dentists List",
            "Add Dentist (Valid)",
            "Add Dentist (Invalid Email)",
            "Update Dentist",
            "Delete Dentist"
        ]
        
        critical_failures = [test for test in self.failed_tests if test in critical_tests]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED:")
            for test in critical_failures:
                print(f"  - {test}")
            print("\n❌ DENTIST MANAGEMENT API NOT READY")
        else:
            print(f"\n🎉 ALL CRITICAL TESTS PASSED")
            print("✅ DENTIST MANAGEMENT API READY FOR FRONTEND INTEGRATION")
        
        return success_rate >= 75 and len(critical_failures) == 0

if __name__ == "__main__":
    tester = DentistManagementTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)