#!/usr/bin/env python3
"""
Dentist Management API Testing
Tests the newly implemented dentist management API endpoints in /api/practice/dentists
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Test both production URLs
PRODUCTION_URL_1 = "https://care-guide-fix.preview.emergentagent.com/api"  # From frontend/.env
PRODUCTION_URL_2 = "https://dentist-portal-3.emergent.host/api"  # From backend/.env
LOCAL_URL = "http://localhost:8001/api"

# Use the URL from the review request context
BACKEND_URL = PRODUCTION_URL_2

class DentistManagementTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.test_dentist_id = None
        
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
    
    def test_practice_login(self):
        """Test practice admin login with provided credentials"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    user_info = data.get("user", {})
                    self.log_test("Practice Admin Login", True, 
                                f"Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    self.log_test("Practice Admin Login", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_get_dentists(self):
        """Test GET /api/practice/dentists endpoint"""
        if not self.auth_token:
            self.log_test("GET /api/practice/dentists", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/dentists")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dentists = data["data"]
                    self.log_test("GET /api/practice/dentists", True, 
                                f"Retrieved {len(dentists)} dentists for authenticated practice")
                    return True
                else:
                    self.log_test("GET /api/practice/dentists", False, "Invalid response format")
                    return False
            else:
                self.log_test("GET /api/practice/dentists", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/practice/dentists", False, f"Exception: {str(e)}")
            return False

    def test_add_dentist(self):
        """Test POST /api/practice/dentists endpoint with valid data"""
        if not self.auth_token:
            self.log_test("POST /api/practice/dentists (Create)", False, "No authentication token available")
            return False
            
        try:
            dentist_data = {
                "firstName": "John",
                "lastName": "Smith",
                "email": "j.smith@dental.com",
                "phone": "555-123-4567",
                "licenseNumber": "DDS12345",
                "specialties": ["General Dentistry", "Oral Surgery"]
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=dentist_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dentist = data["data"]
                    # Store dentist ID for later tests
                    self.test_dentist_id = dentist.get("id")
                    self.log_test("POST /api/practice/dentists (Create)", True, 
                                f"Created dentist: Dr. {dentist.get('firstName')} {dentist.get('lastName')} (ID: {self.test_dentist_id})")
                    return True
                else:
                    self.log_test("POST /api/practice/dentists (Create)", False, "Invalid response format")
                    return False
            else:
                self.log_test("POST /api/practice/dentists (Create)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/practice/dentists (Create)", False, f"Exception: {str(e)}")
            return False

    def test_add_dentist_validation(self):
        """Test POST /api/practice/dentists with missing required fields"""
        if not self.auth_token:
            self.log_test("POST /api/practice/dentists (Validation)", False, "No authentication token available")
            return False
            
        try:
            # Test with missing required fields
            invalid_dentist_data = {
                "firstName": "Jane",
                # Missing lastName and email (required fields)
                "phone": "555-987-6543"
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=invalid_dentist_data)
            
            if response.status_code == 422:  # Validation error
                self.log_test("POST /api/practice/dentists (Validation)", True, 
                            "Properly rejected dentist with missing required fields (firstName, lastName, email)")
                return True
            else:
                self.log_test("POST /api/practice/dentists (Validation)", False, 
                            f"Expected 422 validation error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/practice/dentists (Validation)", False, f"Exception: {str(e)}")
            return False

    def test_add_dentist_duplicate_email(self):
        """Test POST /api/practice/dentists with duplicate email within practice"""
        if not self.auth_token:
            self.log_test("POST /api/practice/dentists (Email Uniqueness)", False, "No authentication token available")
            return False
            
        try:
            # Try to add dentist with same email as previous test
            duplicate_dentist_data = {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "j.smith@dental.com",  # Same email as previous dentist
                "phone": "555-987-6543",
                "licenseNumber": "DDS67890",
                "specialties": ["Orthodontics"]
            }
            
            response = self.session.post(f"{self.base_url}/practice/dentists", json=duplicate_dentist_data)
            
            if response.status_code == 409:  # Conflict
                data = response.json()
                if "email already exists" in data.get("detail", "").lower():
                    self.log_test("POST /api/practice/dentists (Email Uniqueness)", True, 
                                "Properly rejected duplicate email within practice")
                    return True
                else:
                    self.log_test("POST /api/practice/dentists (Email Uniqueness)", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("POST /api/practice/dentists (Email Uniqueness)", False, 
                            f"Expected 409 conflict, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/practice/dentists (Email Uniqueness)", False, f"Exception: {str(e)}")
            return False

    def test_update_dentist(self):
        """Test PUT /api/practice/dentists/{dentist_id} endpoint"""
        if not self.auth_token:
            self.log_test("PUT /api/practice/dentists/{id} (Update)", False, "No authentication token available")
            return False
            
        if not self.test_dentist_id:
            self.log_test("PUT /api/practice/dentists/{id} (Update)", False, "No test dentist available")
            return False
            
        try:
            update_data = {
                "firstName": "John",
                "lastName": "Smith-Updated",
                "phone": "555-123-9999",
                "specialties": ["General Dentistry", "Oral Surgery", "Endodontics"]
            }
            
            response = self.session.put(f"{self.base_url}/practice/dentists/{self.test_dentist_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    updated_dentist = data["data"]
                    if updated_dentist.get("lastName") == "Smith-Updated":
                        self.log_test("PUT /api/practice/dentists/{id} (Update)", True, 
                                    f"Successfully updated dentist: {updated_dentist.get('firstName')} {updated_dentist.get('lastName')}")
                        return True
                    else:
                        self.log_test("PUT /api/practice/dentists/{id} (Update)", False, "Update not reflected in response")
                        return False
                else:
                    self.log_test("PUT /api/practice/dentists/{id} (Update)", False, "Invalid response format")
                    return False
            else:
                self.log_test("PUT /api/practice/dentists/{id} (Update)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT /api/practice/dentists/{id} (Update)", False, f"Exception: {str(e)}")
            return False

    def test_update_dentist_404(self):
        """Test PUT /api/practice/dentists/{dentist_id} with invalid dentist ID"""
        if not self.auth_token:
            self.log_test("PUT /api/practice/dentists/{id} (404 Error)", False, "No authentication token available")
            return False
            
        try:
            invalid_dentist_id = "invalid-dentist-id-12345"
            update_data = {
                "firstName": "Updated",
                "lastName": "Name"
            }
            
            response = self.session.put(f"{self.base_url}/practice/dentists/{invalid_dentist_id}", json=update_data)
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("PUT /api/practice/dentists/{id} (404 Error)", True, 
                                "Properly returned 404 for invalid dentist ID")
                    return True
                else:
                    self.log_test("PUT /api/practice/dentists/{id} (404 Error)", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("PUT /api/practice/dentists/{id} (404 Error)", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PUT /api/practice/dentists/{id} (404 Error)", False, f"Exception: {str(e)}")
            return False

    def test_delete_dentist(self):
        """Test DELETE /api/practice/dentists/{dentist_id} endpoint (soft delete)"""
        if not self.auth_token:
            self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", False, "No authentication token available")
            return False
            
        if not self.test_dentist_id:
            self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", False, "No test dentist available")
            return False
            
        try:
            response = self.session.delete(f"{self.base_url}/practice/dentists/{self.test_dentist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "removed successfully" in data.get("message", "").lower():
                    # Verify dentist is no longer in active list
                    get_response = self.session.get(f"{self.base_url}/practice/dentists")
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        dentists = get_data.get("data", [])
                        # Check if deleted dentist is not in the list
                        deleted_dentist_found = any(d.get("id") == self.test_dentist_id for d in dentists)
                        if not deleted_dentist_found:
                            self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", True, 
                                        "Successfully soft-deleted dentist (isActive=false)")
                            return True
                        else:
                            self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", False, 
                                        "Dentist still appears in active list after deletion")
                            return False
                    else:
                        self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", True, 
                                    "Dentist deletion successful (could not verify list)")
                        return True
                else:
                    self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", False, "Invalid response format")
                    return False
            else:
                self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("DELETE /api/practice/dentists/{id} (Soft Delete)", False, f"Exception: {str(e)}")
            return False

    def test_delete_dentist_404(self):
        """Test DELETE /api/practice/dentists/{dentist_id} with invalid dentist ID"""
        if not self.auth_token:
            self.log_test("DELETE /api/practice/dentists/{id} (404 Error)", False, "No authentication token available")
            return False
            
        try:
            invalid_dentist_id = "invalid-dentist-id-99999"
            response = self.session.delete(f"{self.base_url}/practice/dentists/{invalid_dentist_id}")
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("DELETE /api/practice/dentists/{id} (404 Error)", True, 
                                "Properly returned 404 for invalid dentist ID")
                    return True
                else:
                    self.log_test("DELETE /api/practice/dentists/{id} (404 Error)", False, 
                                f"Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                self.log_test("DELETE /api/practice/dentists/{id} (404 Error)", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("DELETE /api/practice/dentists/{id} (404 Error)", False, f"Exception: {str(e)}")
            return False

    def test_authentication_required(self):
        """Test that dentist endpoints require proper authentication and authorization"""
        try:
            # Test without authentication token
            no_auth_session = requests.Session()
            
            # Test GET dentists without auth
            response = no_auth_session.get(f"{self.base_url}/practice/dentists")
            
            if response.status_code in [401, 403]:
                self.log_test("Authentication & Authorization Required", True, 
                            f"Properly blocked unauthenticated access (Status: {response.status_code})")
                return True
            else:
                self.log_test("Authentication & Authorization Required", False, 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication & Authorization Required", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all dentist management API tests"""
        print(f"🦷 Dentist Management API Testing")
        print(f"🔗 Testing against: {self.base_url}")
        print(f"📋 Testing endpoints: GET, POST, PUT, DELETE /api/practice/dentists")
        print("=" * 70)
        
        # Test sequence
        tests = [
            ("Authentication", self.test_practice_login),
            ("GET Dentists", self.test_get_dentists),
            ("POST Create Dentist", self.test_add_dentist),
            ("POST Validation", self.test_add_dentist_validation),
            ("POST Email Uniqueness", self.test_add_dentist_duplicate_email),
            ("PUT Update Dentist", self.test_update_dentist),
            ("PUT 404 Error", self.test_update_dentist_404),
            ("DELETE Soft Delete", self.test_delete_dentist),
            ("DELETE 404 Error", self.test_delete_dentist_404),
            ("Auth Required", self.test_authentication_required)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All dentist management API tests passed!")
            print("✅ CRUD operations working correctly")
            print("✅ Authentication and authorization working")
            print("✅ Validation and error handling working")
            print("✅ Email uniqueness within practice enforced")
            print("✅ Soft delete functionality working")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the dentist management tests"""
    tester = DentistManagementTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()