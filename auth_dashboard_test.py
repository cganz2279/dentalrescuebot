#!/usr/bin/env python3
"""
Authentication and Dashboard API Testing for Dental Application
Tests the specific endpoints requested in the review:
1. Authentication API with cganz2279@gmail.com / password123
2. Dashboard and key management endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://dentistpdf.preview.emergentagent.com/api"

class AuthDashboardTester:
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
    
    def test_authentication_login(self):
        """Test POST /api/auth/login with cganz2279@gmail.com / password123"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    user_info = data["user"]
                    practice_name = user_info.get("practiceName", "Unknown")
                    self.log_test("Authentication Login (POST /api/auth/login)", True, 
                                f"Successfully logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} from {practice_name}")
                    return True
                else:
                    self.log_test("Authentication Login (POST /api/auth/login)", False, 
                                f"Missing token or user in response: {data}")
                    return False
            else:
                self.log_test("Authentication Login (POST /api/auth/login)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Login (POST /api/auth/login)", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me endpoint to validate JWT token"""
        if not self.auth_token:
            self.log_test("Auth Me Endpoint (GET /api/auth/me)", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data:
                    user_info = data["user"]
                    self.log_test("Auth Me Endpoint (GET /api/auth/me)", True, 
                                f"JWT token valid, user: {user_info.get('email', 'Unknown')}")
                    return True
                else:
                    self.log_test("Auth Me Endpoint (GET /api/auth/me)", False, 
                                f"Missing user in response: {data}")
                    return False
            else:
                self.log_test("Auth Me Endpoint (GET /api/auth/me)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint (GET /api/auth/me)", False, f"Exception: {str(e)}")
            return False
    
    def test_practice_dashboard(self):
        """Test GET /api/practice/dashboard"""
        if not self.auth_token:
            self.log_test("Practice Dashboard (GET /api/practice/dashboard)", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/practice/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "data" in data:
                    dashboard_data = data["data"]
                    if "practice" in dashboard_data and "stats" in dashboard_data:
                        practice = dashboard_data["practice"]
                        stats = dashboard_data["stats"]
                        self.log_test("Practice Dashboard (GET /api/practice/dashboard)", True, 
                                    f"Dashboard loaded for {practice.get('name', 'Unknown')} - "
                                    f"Patients: {stats.get('patientCount', 0)}, "
                                    f"Active Procedures: {stats.get('activeProcedures', 0)}")
                        return True
                    else:
                        self.log_test("Practice Dashboard (GET /api/practice/dashboard)", False, 
                                    f"Missing practice or stats in dashboard data: {dashboard_data}")
                        return False
                else:
                    self.log_test("Practice Dashboard (GET /api/practice/dashboard)", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Practice Dashboard (GET /api/practice/dashboard)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Dashboard (GET /api/practice/dashboard)", False, f"Exception: {str(e)}")
            return False
    
    def test_practice_patients(self):
        """Test GET /api/practice/patients"""
        if not self.auth_token:
            self.log_test("Practice Patients (GET /api/practice/patients)", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/practice/patients", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "data" in data:
                    patients = data["data"]
                    self.log_test("Practice Patients (GET /api/practice/patients)", True, 
                                f"Retrieved {len(patients)} patients")
                    return True
                else:
                    self.log_test("Practice Patients (GET /api/practice/patients)", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Practice Patients (GET /api/practice/patients)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Patients (GET /api/practice/patients)", False, f"Exception: {str(e)}")
            return False
    
    def test_procedures_endpoint(self):
        """Test GET /api/procedures"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "data" in data:
                    procedures = data["data"]
                    self.log_test("Procedures Endpoint (GET /api/procedures)", True, 
                                f"Retrieved {len(procedures)} procedures")
                    return True
                else:
                    self.log_test("Procedures Endpoint (GET /api/procedures)", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Procedures Endpoint (GET /api/procedures)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Procedures Endpoint (GET /api/procedures)", False, f"Exception: {str(e)}")
            return False
    
    def test_practice_doctors(self):
        """Test GET /api/practice/doctors"""
        if not self.auth_token:
            self.log_test("Practice Doctors (GET /api/practice/doctors)", False, "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{self.base_url}/practice/doctors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"] and "data" in data:
                    doctors = data["data"]
                    self.log_test("Practice Doctors (GET /api/practice/doctors)", True, 
                                f"Retrieved {len(doctors)} doctors")
                    return True
                else:
                    self.log_test("Practice Doctors (GET /api/practice/doctors)", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Practice Doctors (GET /api/practice/doctors)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Doctors (GET /api/practice/doctors)", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication and dashboard tests"""
        print("🧪 Starting Authentication and Dashboard API Testing")
        print("=" * 60)
        
        # Test authentication first
        auth_success = self.test_authentication_login()
        
        if auth_success:
            # Test JWT token validation
            self.test_auth_me_endpoint()
            
            # Test dashboard and key management endpoints
            self.test_practice_dashboard()
            self.test_practice_patients()
            self.test_practice_doctors()
        
        # Test public endpoints (no auth required)
        self.test_procedures_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Backend authentication and dashboard APIs are working correctly!")
            return True
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED - See details above")
            return False

def main():
    """Main test execution"""
    tester = AuthDashboardTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()