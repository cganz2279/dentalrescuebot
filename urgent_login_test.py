#!/usr/bin/env python3
"""
URGENT LOGIN FUNCTIONALITY TEST
Testing authentication endpoints to debug critical login issue
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URLs to test
BACKEND_URLS = [
    "https://dental-portal-debug.preview.emergentagent.com/api",  # Preview URL
    "http://localhost:8001/api"  # Local URL
]

# Confirmed working credentials from test_result.md
TEST_CREDENTIALS = [
    {
        "email": "cganz2279@gmail.com",
        "password": "password123",
        "role": "practice_admin",
        "description": "Practice Admin - Cary Ganz DDS PC"
    },
    {
        "email": "ganzseth@gmail.com", 
        "password": "password123",
        "role": "patient",
        "description": "Patient - Seth Ganz"
    },
    {
        "email": "cganz@admin.com",
        "password": "Dentist1#",
        "role": "super_admin", 
        "description": "Super Admin"
    }
]

class UrgentLoginTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_backend_connectivity(self, base_url: str):
        """Test if backend is reachable"""
        try:
            response = self.session.get(f"{base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test(f"Backend Connectivity ({base_url})", True, f"Response: {data}")
                    return True
                else:
                    self.log_test(f"Backend Connectivity ({base_url})", False, "Missing 'message' in response")
                    return False
            else:
                self.log_test(f"Backend Connectivity ({base_url})", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test(f"Backend Connectivity ({base_url})", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test(f"Backend Connectivity ({base_url})", False, f"Exception: {str(e)}")
            return False
    
    def test_login_endpoint(self, base_url: str, credentials: Dict[str, str]):
        """Test login with specific credentials"""
        try:
            login_data = {
                "email": credentials["email"],
                "password": credentials["password"]
            }
            
            # Determine endpoint based on role
            if credentials["role"] == "super_admin":
                endpoint = f"{base_url}/admin/login"
            else:
                endpoint = f"{base_url}/auth/login"
            
            response = self.session.post(endpoint, json=login_data, timeout=10)
            
            test_name = f"Login Test - {credentials['description']} ({base_url})"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and "token" in data:
                        user_info = data.get("user", {})
                        token_preview = data["token"][:20] + "..." if len(data["token"]) > 20 else data["token"]
                        
                        self.log_test(test_name, True, 
                                    f"Login successful! Token: {token_preview}, User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} (Role: {user_info.get('role', 'N/A')})")
                        return True, data["token"]
                    else:
                        self.log_test(test_name, False, f"Invalid response format: {data}")
                        return False, None
                except json.JSONDecodeError:
                    self.log_test(test_name, False, f"Invalid JSON response: {response.text}")
                    return False, None
            else:
                try:
                    error_data = response.json()
                    self.log_test(test_name, False, f"Status: {response.status_code}, Error: {error_data}")
                except:
                    self.log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            self.log_test(test_name, False, f"Connection error: {str(e)}")
            return False, None
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False, None
    
    def test_jwt_token_validation(self, base_url: str, token: str, credentials: Dict[str, str]):
        """Test if JWT token works for authenticated endpoints"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test different endpoints based on role
            if credentials["role"] == "practice_admin":
                test_endpoint = f"{base_url}/practice/dashboard"
                test_name = f"JWT Token Validation - Practice Dashboard ({base_url})"
            elif credentials["role"] == "patient":
                test_endpoint = f"{base_url}/patients/dashboard"
                test_name = f"JWT Token Validation - Patient Dashboard ({base_url})"
            elif credentials["role"] == "super_admin":
                test_endpoint = f"{base_url}/admin/dashboard"
                test_name = f"JWT Token Validation - Admin Dashboard ({base_url})"
            else:
                self.log_test(f"JWT Token Validation ({base_url})", False, f"Unknown role: {credentials['role']}")
                return False
            
            response = self.session.get(test_endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        self.log_test(test_name, True, f"Token validation successful, dashboard data retrieved")
                        return True
                    else:
                        self.log_test(test_name, False, f"Invalid response format: {data}")
                        return False
                except json.JSONDecodeError:
                    self.log_test(test_name, False, f"Invalid JSON response: {response.text}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test(test_name, False, f"Status: {response.status_code}, Error: {error_data}")
                except:
                    self.log_test(test_name, False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test(test_name, False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_credentials(self, base_url: str):
        """Test login with invalid credentials to ensure proper error handling"""
        try:
            login_data = {
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{base_url}/auth/login", json=login_data, timeout=10)
            
            test_name = f"Invalid Credentials Test ({base_url})"
            
            if response.status_code == 401 or response.status_code == 400:
                try:
                    data = response.json()
                    self.log_test(test_name, True, f"Properly rejected invalid credentials: {data}")
                    return True
                except json.JSONDecodeError:
                    self.log_test(test_name, True, f"Properly rejected invalid credentials (Status: {response.status_code})")
                    return True
            else:
                self.log_test(test_name, False, f"Unexpected status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test(test_name, False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False
    
    def run_urgent_login_tests(self):
        """Run all urgent login tests"""
        print("🚨 URGENT LOGIN FUNCTIONALITY TEST")
        print("Testing authentication endpoints to debug critical login issue")
        print("=" * 70)
        
        total_tests = 0
        passed_tests = 0
        
        for base_url in BACKEND_URLS:
            print(f"\n🔗 Testing Backend: {base_url}")
            print("-" * 50)
            
            # Test backend connectivity first
            if not self.test_backend_connectivity(base_url):
                print(f"❌ Backend {base_url} is not reachable, skipping further tests")
                continue
            
            # Test invalid credentials first
            if self.test_invalid_credentials(base_url):
                passed_tests += 1
            total_tests += 1
            
            # Test each set of credentials
            for credentials in TEST_CREDENTIALS:
                print(f"\n🔐 Testing: {credentials['description']}")
                
                # Test login
                login_success, token = self.test_login_endpoint(base_url, credentials)
                total_tests += 1
                if login_success:
                    passed_tests += 1
                    
                    # If login successful, test JWT token validation
                    if token:
                        jwt_success = self.test_jwt_token_validation(base_url, token, credentials)
                        total_tests += 1
                        if jwt_success:
                            passed_tests += 1
        
        # Print summary
        print("\n" + "=" * 70)
        print("🏁 URGENT LOGIN TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate < 100:
            print("\n❌ CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        else:
            print("\n✅ ALL LOGIN TESTS PASSED - Authentication system is working correctly")
        
        return success_rate >= 80  # Consider 80%+ as acceptable

def main():
    tester = UrgentLoginTester()
    success = tester.run_urgent_login_tests()
    
    if not success:
        print("\n🚨 URGENT ACTION REQUIRED: Login functionality has critical issues")
        sys.exit(1)
    else:
        print("\n✅ Login functionality appears to be working correctly")
        sys.exit(0)

if __name__ == "__main__":
    main()