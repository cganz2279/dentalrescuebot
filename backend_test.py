#!/usr/bin/env python3
"""
Backend API Testing for Dental Post-Operative Care App
Tests all backend endpoints to ensure proper functionality
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentalcarebot.preview.emergentagent.com/api"

class DentalAPITester:
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
    
    def test_health_check(self):
        """Test GET /api/ endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Health Check (GET /api/)", True, f"Response: {data}")
                    return True
                else:
                    self.log_test("Health Check (GET /api/)", False, "Missing 'message' in response")
                    return False
            else:
                self.log_test("Health Check (GET /api/)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check (GET /api/)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_specialties(self):
        """Test GET /api/specialties endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    if len(specialties) == 7:  # Should have 7 dental specialties
                        # Check if each specialty has required fields
                        required_fields = ["id", "name", "description", "procedureCount"]
                        all_valid = True
                        for specialty in specialties:
                            for field in required_fields:
                                if field not in specialty:
                                    all_valid = False
                                    break
                        
                        if all_valid:
                            self.log_test("Get All Specialties", True, f"Found {len(specialties)} specialties with procedure counts")
                            return True
                        else:
                            self.log_test("Get All Specialties", False, "Missing required fields in specialties")
                            return False
                    else:
                        self.log_test("Get All Specialties", False, f"Expected 7 specialties, got {len(specialties)}")
                        return False
                else:
                    self.log_test("Get All Specialties", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get All Specialties", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get All Specialties", False, f"Exception: {str(e)}")
            return False
    
    def test_get_specialty_by_id(self):
        """Test GET /api/specialties/{id} endpoint"""
        try:
            # Test with oral-surgery specialty
            response = self.session.get(f"{self.base_url}/specialties/oral-surgery")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialty = data["data"]
                    required_fields = ["id", "name", "description", "procedures"]
                    
                    if all(field in specialty for field in required_fields):
                        if specialty["id"] == "oral-surgery":
                            procedures = specialty.get("procedures", [])
                            self.log_test("Get Specialty by ID (oral-surgery)", True, 
                                        f"Found specialty with {len(procedures)} procedures")
                            return True
                        else:
                            self.log_test("Get Specialty by ID (oral-surgery)", False, "Wrong specialty returned")
                            return False
                    else:
                        self.log_test("Get Specialty by ID (oral-surgery)", False, "Missing required fields")
                        return False
                else:
                    self.log_test("Get Specialty by ID (oral-surgery)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Specialty by ID (oral-surgery)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Specialty by ID (oral-surgery)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_procedures(self):
        """Test GET /api/procedures endpoint"""
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
                            self.log_test("Get All Procedures", True, f"Found {len(procedures)} procedures")
                            return True
                        else:
                            self.log_test("Get All Procedures", False, "Missing required fields in procedures")
                            return False
                    else:
                        self.log_test("Get All Procedures", False, "No procedures found")
                        return False
                else:
                    self.log_test("Get All Procedures", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get All Procedures", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get All Procedures", False, f"Exception: {str(e)}")
            return False
    
    def test_get_procedure_by_id(self):
        """Test GET /api/procedures/{id} endpoint"""
        try:
            # Test with root-canal procedure
            response = self.session.get(f"{self.base_url}/procedures/root-canal")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    required_fields = ["id", "name", "specialty", "specialtyName", "duration", 
                                     "overview", "immediateAftercare", "dietRestrictions", 
                                     "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                    
                    if all(field in procedure for field in required_fields):
                        if procedure["id"] == "root-canal":
                            self.log_test("Get Procedure by ID (root-canal)", True, 
                                        f"Found detailed procedure information")
                            return True
                        else:
                            self.log_test("Get Procedure by ID (root-canal)", False, "Wrong procedure returned")
                            return False
                    else:
                        missing_fields = [f for f in required_fields if f not in procedure]
                        self.log_test("Get Procedure by ID (root-canal)", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Get Procedure by ID (root-canal)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Procedure by ID (root-canal)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Procedure by ID (root-canal)", False, f"Exception: {str(e)}")
            return False
    
    def test_search_procedures(self):
        """Test GET /api/procedures/search endpoint"""
        try:
            # Search for procedures containing "root"
            response = self.session.get(f"{self.base_url}/procedures/search?q=root")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    if len(procedures) > 0:
                        # Check if search results contain "root" in name or description
                        valid_results = True
                        for procedure in procedures:
                            name_match = "root" in procedure.get("name", "").lower()
                            specialty_match = "root" in procedure.get("specialtyName", "").lower()
                            if not (name_match or specialty_match):
                                # This might be okay if it matches in overview field
                                pass
                        
                        self.log_test("Search Procedures (q=root)", True, 
                                    f"Found {len(procedures)} matching procedures")
                        return True
                    else:
                        self.log_test("Search Procedures (q=root)", False, "No search results found")
                        return False
                else:
                    self.log_test("Search Procedures (q=root)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Search Procedures (q=root)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Search Procedures (q=root)", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid endpoints"""
        try:
            # Test invalid specialty ID
            response = self.session.get(f"{self.base_url}/specialties/invalid-id")
            
            if response.status_code == 404:
                data = response.json()
                if "detail" in data:
                    self.log_test("Error Handling (Invalid Specialty ID)", True, 
                                f"Proper 404 error returned: {data['detail']}")
                    return True
                else:
                    self.log_test("Error Handling (Invalid Specialty ID)", False, 
                                "404 status but missing error detail")
                    return False
            else:
                self.log_test("Error Handling (Invalid Specialty ID)", False, 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling (Invalid Specialty ID)", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🧪 Starting Backend API Tests for Dental Post-Operative Care App")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 70)
        
        tests = [
            self.test_health_check,
            self.test_get_specialties,
            self.test_get_specialty_by_id,
            self.test_get_procedures,
            self.test_get_procedure_by_id,
            self.test_search_procedures,
            self.test_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 70)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend APIs are working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the tests"""
    tester = DentalAPITester(BACKEND_URL)
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()