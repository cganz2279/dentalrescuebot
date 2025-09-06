#!/usr/bin/env python3
"""
Focused test for Practice Dashboard API endpoint
Tests the specific issue with dashboard data loading and search feature
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://careplan-debug.preview.emergentagent.com/api"

class DashboardTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_practice_login(self):
        """Test practice admin login with correct credentials"""
        try:
            # Use the correct credentials from test_result.md
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
                    practice_info = data.get("practice", {})
                    self.log_test("Practice Admin Login", True, 
                                f"Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} from {practice_info.get('name', '')} (role: {user_info.get('role', '')})")
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

    def test_practice_dashboard_api(self):
        """Test GET /api/practice/dashboard endpoint - main focus of the review"""
        if not self.auth_token:
            self.log_test("Practice Dashboard API", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    dashboard_data = data["data"]
                    
                    # Check the structure of returned data
                    print("\n📊 DASHBOARD DATA STRUCTURE ANALYSIS:")
                    print("=" * 50)
                    
                    # Check for required fields
                    required_fields = ["practice", "stats", "recentPatients", "recentProcedures"]
                    missing_fields = []
                    
                    for field in required_fields:
                        if field in dashboard_data:
                            print(f"✅ {field}: Present")
                            if field == "recentPatients":
                                recent_patients = dashboard_data[field]
                                print(f"   - Type: {type(recent_patients)}")
                                print(f"   - Count: {len(recent_patients) if isinstance(recent_patients, list) else 'Not a list'}")
                                if isinstance(recent_patients, list) and len(recent_patients) > 0:
                                    sample_patient = recent_patients[0]
                                    print(f"   - Sample patient fields: {list(sample_patient.keys()) if isinstance(sample_patient, dict) else 'Not a dict'}")
                                    # Check if patients have searchable fields
                                    searchable_fields = ["firstName", "lastName", "email", "phone"]
                                    for search_field in searchable_fields:
                                        if isinstance(sample_patient, dict) and search_field in sample_patient:
                                            print(f"   - ✅ Searchable field '{search_field}': {sample_patient[search_field]}")
                                        else:
                                            print(f"   - ❌ Missing searchable field '{search_field}'")
                                else:
                                    print(f"   - ⚠️  No recent patients data for search functionality")
                            elif field == "stats":
                                stats = dashboard_data[field]
                                print(f"   - Stats: {stats}")
                            elif field == "practice":
                                practice = dashboard_data[field]
                                print(f"   - Practice: {practice.get('name', 'Unknown') if isinstance(practice, dict) else practice}")
                            elif field == "recentProcedures":
                                recent_procedures = dashboard_data[field]
                                print(f"   - Recent procedures count: {len(recent_procedures) if isinstance(recent_procedures, list) else 'Not a list'}")
                        else:
                            missing_fields.append(field)
                            print(f"❌ {field}: Missing")
                    
                    print("\n🔍 SEARCH FEATURE ANALYSIS:")
                    print("=" * 50)
                    
                    # Analyze if data supports search functionality
                    recent_patients = dashboard_data.get("recentPatients", [])
                    if isinstance(recent_patients, list) and len(recent_patients) > 0:
                        print(f"✅ Patient data available for search: {len(recent_patients)} patients")
                        
                        # Check if patients have required fields for search
                        search_ready_patients = 0
                        for patient in recent_patients:
                            if isinstance(patient, dict):
                                has_name = patient.get("firstName") and patient.get("lastName")
                                has_email = patient.get("email")
                                if has_name or has_email:
                                    search_ready_patients += 1
                        
                        print(f"✅ Search-ready patients: {search_ready_patients}/{len(recent_patients)}")
                        
                        if search_ready_patients == 0:
                            print("❌ ISSUE FOUND: No patients have searchable data (firstName, lastName, email)")
                            self.log_test("Practice Dashboard API", False, 
                                        f"Dashboard loaded but patients lack searchable fields. Found {len(recent_patients)} patients but none have firstName/lastName/email for search functionality")
                            return False
                        else:
                            print("✅ Search functionality should work with available patient data")
                    else:
                        print("❌ ISSUE FOUND: No recent patients data available for search")
                        self.log_test("Practice Dashboard API", False, 
                                    "Dashboard loaded but recentPatients is empty or not a list - search feature cannot work without patient data")
                        return False
                    
                    # Check API response structure changes
                    print(f"\n📋 API RESPONSE STRUCTURE:")
                    print("=" * 50)
                    print(f"Response keys: {list(dashboard_data.keys())}")
                    
                    if missing_fields:
                        self.log_test("Practice Dashboard API", False, 
                                    f"Dashboard API missing required fields: {missing_fields}")
                        return False
                    else:
                        self.log_test("Practice Dashboard API", True, 
                                    f"Dashboard API working correctly with {len(recent_patients)} patients available for search")
                        return True
                else:
                    self.log_test("Practice Dashboard API", False, "Invalid response format - missing 'success' or 'data' fields")
                    return False
            else:
                self.log_test("Practice Dashboard API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Dashboard API", False, f"Exception: {str(e)}")
            return False

    def test_backend_service_status(self):
        """Test if backend service is running correctly"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Backend Service Status", True, f"Backend service running: {data}")
                    return True
                else:
                    self.log_test("Backend Service Status", False, "Backend responding but invalid format")
                    return False
            else:
                self.log_test("Backend Service Status", False, f"Backend not responding properly: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Backend Service Status", False, f"Backend service unreachable: {str(e)}")
            return False

    def test_get_patients_for_search(self):
        """Test GET /api/practice/patients to verify patient data for search"""
        if not self.auth_token:
            self.log_test("Get Patients for Search", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    patients = data["data"]
                    
                    print(f"\n👥 PATIENTS DATA FOR SEARCH ANALYSIS:")
                    print("=" * 50)
                    print(f"Total patients: {len(patients)}")
                    
                    if len(patients) > 0:
                        sample_patient = patients[0]
                        print(f"Sample patient structure: {list(sample_patient.keys()) if isinstance(sample_patient, dict) else 'Not a dict'}")
                        
                        # Check searchable fields
                        searchable_count = 0
                        for patient in patients:
                            if isinstance(patient, dict):
                                has_searchable_data = (
                                    patient.get("firstName") or 
                                    patient.get("lastName") or 
                                    patient.get("email") or 
                                    patient.get("phone")
                                )
                                if has_searchable_data:
                                    searchable_count += 1
                        
                        print(f"Patients with searchable data: {searchable_count}/{len(patients)}")
                        
                        if searchable_count > 0:
                            self.log_test("Get Patients for Search", True, 
                                        f"Found {len(patients)} patients, {searchable_count} have searchable data")
                            return True
                        else:
                            self.log_test("Get Patients for Search", False, 
                                        f"Found {len(patients)} patients but none have searchable fields")
                            return False
                    else:
                        self.log_test("Get Patients for Search", False, "No patients found - search feature will be empty")
                        return False
                else:
                    self.log_test("Get Patients for Search", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Patients for Search", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Patients for Search", False, f"Exception: {str(e)}")
            return False

    def run_dashboard_tests(self):
        """Run focused dashboard tests"""
        print(f"🔍 FOCUSED DASHBOARD API TESTING")
        print(f"🎯 Focus: Dashboard search feature issue investigation")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 70)
        
        tests = [
            ("Backend Service Check", self.test_backend_service_status),
            ("Practice Login", self.test_practice_login),
            ("Dashboard API Structure", self.test_practice_dashboard_api),
            ("Patients Data for Search", self.test_get_patients_for_search),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed - this may be causing the search issue")
        
        print("\n" + "=" * 70)
        print(f"📊 DASHBOARD TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All dashboard tests passed - search feature should be working")
            print("💡 If search is still missing, check frontend implementation")
        else:
            print("❌ Dashboard API issues found - this explains the missing search feature")
            print("🔧 Fix the failing tests to restore search functionality")
        
        return passed == total

if __name__ == "__main__":
    tester = DashboardTester(BACKEND_URL)
    success = tester.run_dashboard_tests()
    sys.exit(0 if success else 1)