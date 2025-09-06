#!/usr/bin/env python3
"""
Registration Endpoints Testing for New Customer Signup Issues
Testing POST /api/auth/register-practice and POST /api/auth/register-practice-samcart endpoints
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentist-portal-3.emergent.host')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 REGISTRATION ENDPOINTS TESTING")
print(f"Backend URL: {BACKEND_URL}")
print(f"API Base: {API_BASE}")
print("=" * 80)

class RegistrationTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def test_register_practice_valid_data(self):
        """Test POST /api/auth/register-practice with valid data"""
        test_name = "Valid Registration Data (www.domain.com format)"
        
        # Use unique email for each test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"test_{timestamp}@dentalpractice.com"
        
        registration_data = {
            "practiceName": "Test Dental Practice",
            "email": test_email,
            "phone": "(555) 123-4567",
            "website": "www.testdental.com",  # No https:// prefix
            "adminFirstName": "John",
            "adminLastName": "Smith",
            "adminPassword": "TestPass123",  # Valid password with letters + numbers + 6+ chars
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zipCode": "12345"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register-practice",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("requiresPaymentSetup"):
                    self.log_test(test_name, True, f"Registration successful, requires payment setup as expected")
                    return True
                else:
                    self.log_test(test_name, False, f"Unexpected response structure: {data}")
                    return False
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_register_practice_samcart_valid(self):
        """Test POST /api/auth/register-practice-samcart with valid data"""
        test_name = "SamCart Registration (paymentVerified=true)"
        
        # Use unique email for each test run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"samcart_{timestamp}@dentalpractice.com"
        
        registration_data = {
            "practiceName": "SamCart Dental Practice",
            "email": test_email,
            "phone": "(555) 987-6543",
            "website": "www.samcartdental.com",
            "adminFirstName": "Jane",
            "adminLastName": "Doe",
            "adminPassword": "SamCart123",
            "street": "456 Oak Ave",
            "city": "Springfield",
            "state": "NY",
            "zipCode": "54321"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register-practice-samcart",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("practice", {}).get("status") == "active":
                    self.log_test(test_name, True, f"SamCart registration successful, practice activated immediately")
                    return True
                else:
                    self.log_test(test_name, False, f"Unexpected response structure: {data}")
                    return False
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_password_validation(self):
        """Test password validation requirements"""
        test_cases = [
            {
                "name": "Password with only letters",
                "password": "TestPassword",
                "should_fail": True,
                "expected_error": "Password must be at least 6 characters with letters and numbers"
            },
            {
                "name": "Password with only numbers", 
                "password": "123456789",
                "should_fail": True,
                "expected_error": "Password must be at least 6 characters with letters and numbers"
            },
            {
                "name": "Password under 6 characters",
                "password": "Test1",
                "should_fail": True,
                "expected_error": "Password must be at least 6 characters with letters and numbers"
            },
            {
                "name": "Valid password (letters + numbers + 6+ chars)",
                "password": "ValidPass123",
                "should_fail": False,
                "expected_error": None
            }
        ]
        
        for test_case in test_cases:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            test_email = f"pwd_test_{timestamp}@test.com"
            
            registration_data = {
                "practiceName": "Password Test Practice",
                "email": test_email,
                "phone": "(555) 000-0000",
                "website": "www.passwordtest.com",
                "adminFirstName": "Test",
                "adminLastName": "User",
                "adminPassword": test_case["password"],
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zipCode": "00000"
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/auth/register-practice",
                    json=registration_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if test_case["should_fail"]:
                    if response.status_code == 400:
                        data = response.json()
                        if test_case["expected_error"] in data.get("detail", ""):
                            self.log_test(f"Password Validation: {test_case['name']}", True, f"Correctly rejected with: {data.get('detail')}")
                        else:
                            self.log_test(f"Password Validation: {test_case['name']}", False, f"Wrong error message: {data.get('detail')}")
                    else:
                        self.log_test(f"Password Validation: {test_case['name']}", False, f"Expected 400 error, got {response.status_code}")
                else:
                    if response.status_code == 200:
                        self.log_test(f"Password Validation: {test_case['name']}", True, "Valid password accepted")
                    else:
                        self.log_test(f"Password Validation: {test_case['name']}", False, f"Valid password rejected: {response.text}")
                        
            except Exception as e:
                self.log_test(f"Password Validation: {test_case['name']}", False, f"Request failed: {str(e)}")
    
    def test_duplicate_email_handling(self):
        """Test duplicate email handling"""
        test_name = "Duplicate Email Handling"
        
        # First, register a practice
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"duplicate_{timestamp}@test.com"
        
        registration_data = {
            "practiceName": "First Practice",
            "email": test_email,
            "phone": "(555) 111-1111",
            "website": "www.first.com",
            "adminFirstName": "First",
            "adminLastName": "User",
            "adminPassword": "FirstPass123",
            "street": "123 First St",
            "city": "First City",
            "state": "FC",
            "zipCode": "11111"
        }
        
        try:
            # First registration
            response1 = requests.post(
                f"{API_BASE}/auth/register-practice",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response1.status_code != 200:
                self.log_test(test_name, False, f"First registration failed: {response1.text}")
                return
            
            # Try to register with same email
            registration_data["practiceName"] = "Second Practice"
            response2 = requests.post(
                f"{API_BASE}/auth/register-practice",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response2.status_code == 400:
                data = response2.json()
                if "Email already registered" in data.get("detail", ""):
                    self.log_test(test_name, True, f"Duplicate email correctly rejected: {data.get('detail')}")
                else:
                    self.log_test(test_name, False, f"Wrong error message for duplicate email: {data.get('detail')}")
            else:
                self.log_test(test_name, False, f"Duplicate email not rejected, got status {response2.status_code}")
                
        except Exception as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
    
    def test_missing_required_fields(self):
        """Test missing required fields validation"""
        required_fields = ["practiceName", "email", "adminFirstName", "adminLastName", "adminPassword"]
        
        for field in required_fields:
            test_name = f"Missing Required Field: {field}"
            
            # Create complete data then remove one field
            registration_data = {
                "practiceName": "Test Practice",
                "email": f"missing_{field}@test.com",
                "phone": "(555) 222-2222",
                "website": "www.missing.com",
                "adminFirstName": "Test",
                "adminLastName": "User",
                "adminPassword": "TestPass123",
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zipCode": "22222"
            }
            
            # Remove the field being tested
            del registration_data[field]
            
            try:
                response = requests.post(
                    f"{API_BASE}/auth/register-practice",
                    json=registration_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 422:  # Validation error
                    self.log_test(test_name, True, f"Missing field correctly rejected with 422 validation error")
                elif response.status_code == 400:
                    self.log_test(test_name, True, f"Missing field correctly rejected with 400 error")
                else:
                    self.log_test(test_name, False, f"Missing field not rejected, got status {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_name, False, f"Request failed: {str(e)}")
    
    def test_website_formats(self):
        """Test various website formats"""
        website_formats = [
            {
                "format": "www.example.com",
                "should_pass": True,
                "description": "Standard www format (no https)"
            },
            {
                "format": "example.com", 
                "should_pass": True,
                "description": "Domain only format"
            },
            {
                "format": "https://example.com",
                "should_pass": True,
                "description": "Full HTTPS URL format"
            },
            {
                "format": "http://www.example.com",
                "should_pass": True,
                "description": "Full HTTP URL format"
            }
        ]
        
        for i, test_case in enumerate(website_formats):
            test_name = f"Website Format: {test_case['description']}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            registration_data = {
                "practiceName": f"Website Test Practice {i}",
                "email": f"website_{i}_{timestamp}@test.com",
                "phone": f"(555) {i:03d}-{i:04d}",
                "website": test_case["format"],
                "adminFirstName": "Website",
                "adminLastName": "Test",
                "adminPassword": "WebTest123",
                "street": f"{i} Website St",
                "city": "Website City",
                "state": "WS",
                "zipCode": f"{i:05d}"
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/auth/register-practice",
                    json=registration_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if test_case["should_pass"]:
                    if response.status_code == 200:
                        self.log_test(test_name, True, f"Website format '{test_case['format']}' accepted")
                    else:
                        self.log_test(test_name, False, f"Website format '{test_case['format']}' rejected: {response.text}")
                else:
                    if response.status_code != 200:
                        self.log_test(test_name, True, f"Website format '{test_case['format']}' correctly rejected")
                    else:
                        self.log_test(test_name, False, f"Website format '{test_case['format']}' should have been rejected")
                        
            except Exception as e:
                self.log_test(test_name, False, f"Request failed: {str(e)}")
    
    def test_error_response_format(self):
        """Test that error responses have proper format and helpful messages"""
        test_name = "Error Response Format and Messages"
        
        # Test with invalid data to trigger various errors
        invalid_data = {
            "practiceName": "",  # Empty required field
            "email": "invalid-email",  # Invalid email format
            "adminPassword": "123",  # Invalid password
            "adminFirstName": "",  # Empty required field
            "adminLastName": ""  # Empty required field
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register-practice",
                json=invalid_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should get validation error
            if response.status_code in [400, 422]:
                try:
                    data = response.json()
                    if "detail" in data and isinstance(data["detail"], str) and len(data["detail"]) > 0:
                        self.log_test(test_name, True, f"Error response has proper format with helpful message: {data['detail']}")
                    else:
                        self.log_test(test_name, False, f"Error response missing or empty detail field: {data}")
                except json.JSONDecodeError:
                    self.log_test(test_name, False, f"Error response is not valid JSON: {response.text}")
            else:
                self.log_test(test_name, False, f"Expected validation error (400/422), got {response.status_code}")
                
        except Exception as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all registration tests"""
        print("🚀 Starting Registration Endpoint Tests...")
        print()
        
        # Test basic functionality
        self.test_register_practice_valid_data()
        self.test_register_practice_samcart_valid()
        
        # Test validation
        self.test_password_validation()
        self.test_duplicate_email_handling()
        self.test_missing_required_fields()
        self.test_website_formats()
        self.test_error_response_format()
        
        # Print summary
        print()
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print()
            print("🚨 FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = RegistrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL REGISTRATION TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n💥 {len(tester.failed_tests)} TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()