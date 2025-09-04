#!/usr/bin/env python3
"""
PRODUCTION BACKEND VERIFICATION TEST
Testing the actual production backend at https://dentist-portal-3.emergent.host/api
Focus: Dentist management functionality for cganz2279@gmail.com user
"""

import requests
import json
import sys
from datetime import datetime

# PRODUCTION BACKEND URL - CRITICAL: Must test production, not local
PRODUCTION_BASE_URL = "https://dentist-portal-3.emergent.host/api"

# User credentials from review request
USER_EMAIL = "cganz2279@gmail.com"
USER_PASSWORD = "password123"

class ProductionBackendTester:
    def __init__(self):
        self.base_url = PRODUCTION_BASE_URL
        self.jwt_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result with timestamp"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_production_connectivity(self):
        """Test 1: Verify production backend is accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_result("Production Connectivity", True, 
                              f"Production backend accessible at {self.base_url}")
                return True
            else:
                self.log_result("Production Connectivity", False, 
                              f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Production Connectivity", False, 
                          f"Cannot connect to production backend: {str(e)}")
            return False
    
    def test_user_authentication(self):
        """Test 2: Authenticate with cganz2279@gmail.com credentials"""
        try:
            login_data = {
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.jwt_token = data['token']
                    user_info = data.get('user', {})
                    practice_info = data.get('practice', {})
                    
                    self.log_result("User Authentication", True, 
                                  f"Successfully authenticated {USER_EMAIL}",
                                  f"Role: {user_info.get('role')}, Practice: {practice_info.get('name')}")
                    return True
                else:
                    self.log_result("User Authentication", False, 
                                  "Login response missing token or success flag",
                                  f"Response: {data}")
                    return False
            else:
                self.log_result("User Authentication", False, 
                              f"Login failed with status {response.status_code}",
                              f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, 
                          f"Authentication error: {str(e)}")
            return False
    
    def test_dentist_endpoints_exist(self):
        """Test 3: Check if dentist management endpoints exist in production"""
        if not self.jwt_token:
            self.log_result("Dentist Endpoints Check", False, 
                          "No JWT token available for authentication")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test GET /api/practice/dentists endpoint
            response = requests.get(
                f"{self.base_url}/practice/dentists",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                dentists = data.get('data', [])
                self.log_result("Dentist Endpoints Check", True, 
                              f"Dentist management endpoints exist in production",
                              f"Found {len(dentists)} dentists in practice")
                return True
            elif response.status_code == 404:
                self.log_result("Dentist Endpoints Check", False, 
                              "Dentist management endpoints NOT DEPLOYED to production",
                              "GET /api/practice/dentists returns 404")
                return False
            elif response.status_code == 403:
                self.log_result("Dentist Endpoints Check", False, 
                              "Authentication issue with dentist endpoints",
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
            else:
                self.log_result("Dentist Endpoints Check", False, 
                              f"Unexpected response from dentist endpoint: {response.status_code}",
                              f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Dentist Endpoints Check", False, 
                          f"Error testing dentist endpoints: {str(e)}")
            return False
    
    def test_get_production_dentists(self):
        """Test 4: Get current dentists in production database"""
        if not self.jwt_token:
            self.log_result("Get Production Dentists", False, 
                          "No JWT token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/practice/dentists",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                dentists = data.get('data', [])
                
                # Check if Dr. John Smith exists
                john_smith_exists = any(
                    d.get('firstName') == 'John' and d.get('lastName') == 'Smith' 
                    for d in dentists
                )
                
                dentist_names = [f"Dr. {d.get('firstName')} {d.get('lastName')}" for d in dentists]
                
                self.log_result("Get Production Dentists", True, 
                              f"Retrieved {len(dentists)} dentists from production",
                              f"Dentists: {dentist_names}, John Smith exists: {john_smith_exists}")
                
                return dentists
            else:
                self.log_result("Get Production Dentists", False, 
                              f"Failed to get dentists: {response.status_code}",
                              f"Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Get Production Dentists", False, 
                          f"Error getting production dentists: {str(e)}")
            return None
    
    def test_add_john_smith_to_production(self):
        """Test 5: Add Dr. John Smith to production database"""
        if not self.jwt_token:
            self.log_result("Add John Smith", False, 
                          "No JWT token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Dr. John Smith details from review request
        dentist_data = {
            "firstName": "John",
            "lastName": "Smith",
            "email": "dr.john.smith@dentaltest.com",
            "phone": "(555) 123-4567",
            "licenseNumber": "DDS12345",
            "specialties": ["General Dentistry", "Oral Surgery"]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/practice/dentists",
                json=dentist_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                created_dentist = data.get('data', {})
                
                self.log_result("Add John Smith", True, 
                              "Successfully added Dr. John Smith to production",
                              f"Dentist ID: {created_dentist.get('id')}, Email: {created_dentist.get('email')}")
                return True
            elif response.status_code == 409:
                # Dentist already exists
                self.log_result("Add John Smith", True, 
                              "Dr. John Smith already exists in production database",
                              "Conflict error indicates dentist was previously added")
                return True
            else:
                self.log_result("Add John Smith", False, 
                              f"Failed to add Dr. John Smith: {response.status_code}",
                              f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Add John Smith", False, 
                          f"Error adding Dr. John Smith: {str(e)}")
            return False
    
    def test_verify_john_smith_in_production(self):
        """Test 6: Verify Dr. John Smith appears in production dentist list"""
        dentists = self.test_get_production_dentists()
        
        if dentists is None:
            return False
        
        # Look for Dr. John Smith
        john_smith = None
        for dentist in dentists:
            if (dentist.get('firstName') == 'John' and 
                dentist.get('lastName') == 'Smith'):
                john_smith = dentist
                break
        
        if john_smith:
            self.log_result("Verify John Smith", True, 
                          "Dr. John Smith confirmed in production dentist list",
                          f"Details: {john_smith}")
            return True
        else:
            dentist_names = [f"Dr. {d.get('firstName')} {d.get('lastName')}" for d in dentists]
            self.log_result("Verify John Smith", False, 
                          "Dr. John Smith NOT found in production dentist list",
                          f"Available dentists: {dentist_names}")
            return False
    
    def run_production_verification(self):
        """Run complete production backend verification"""
        print("=" * 80)
        print("PRODUCTION BACKEND VERIFICATION FOR DENTIST MANAGEMENT")
        print(f"Testing: {self.base_url}")
        print(f"User: {USER_EMAIL}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_production_connectivity,
            self.test_user_authentication,
            self.test_dentist_endpoints_exist,
            self.test_get_production_dentists,
            self.test_add_john_smith_to_production,
            self.test_verify_john_smith_in_production
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print("PRODUCTION VERIFICATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Production backend fully functional")
        else:
            print("⚠️  SOME TESTS FAILED - Issues found in production backend")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = ProductionBackendTester()
    success = tester.run_production_verification()
    sys.exit(0 if success else 1)