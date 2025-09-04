#!/usr/bin/env python3
"""
URGENT USER CREDENTIAL VERIFICATION TEST
Specifically tests cganz2279@gmail.com/password123 credentials against production backend
"""

import requests
import json
import sys
from typing import Dict, Any

# Production backend URL from frontend .env
PRODUCTION_BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

class CredentialVerificationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
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
    
    def test_backend_connectivity(self):
        """Test if production backend is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Production Backend Connectivity", True, 
                                f"Backend accessible: {data}")
                    return True
                else:
                    self.log_test("Production Backend Connectivity", False, 
                                "Backend accessible but unexpected response format")
                    return False
            else:
                self.log_test("Production Backend Connectivity", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Production Backend Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_user_login_cganz2279(self):
        """Test login with cganz2279@gmail.com/password123 credentials"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    practice_info = data.get("practice", {})
                    self.log_test("cganz2279@gmail.com Login Test", True, 
                                f"✅ LOGIN SUCCESSFUL - User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')}), Practice: {practice_info.get('name', 'Unknown')}")
                    return True, data
                else:
                    self.log_test("cganz2279@gmail.com Login Test", False, 
                                f"Invalid response format: {data}")
                    return False, None
            elif response.status_code == 401:
                try:
                    error_data = response.json()
                    self.log_test("cganz2279@gmail.com Login Test", False, 
                                f"❌ AUTHENTICATION FAILED - 401 Unauthorized: {error_data.get('detail', 'Invalid credentials')}")
                except:
                    self.log_test("cganz2279@gmail.com Login Test", False, 
                                f"❌ AUTHENTICATION FAILED - 401 Unauthorized: {response.text}")
                return False, None
            else:
                self.log_test("cganz2279@gmail.com Login Test", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_test("cganz2279@gmail.com Login Test", False, f"Exception: {str(e)}")
            return False, None
    
    def test_alternative_credentials(self):
        """Test known working credentials to verify authentication system"""
        try:
            # Test ganzseth@gmail.com which was reported to work on production
            login_data = {
                "email": "ganzseth@gmail.com", 
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    practice_info = data.get("practice", {})
                    self.log_test("Alternative Credentials Test (ganzseth@gmail.com)", True, 
                                f"✅ WORKING CREDENTIALS CONFIRMED - User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')}), Practice: {practice_info.get('name', 'Unknown')}")
                    return True
                else:
                    self.log_test("Alternative Credentials Test (ganzseth@gmail.com)", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Alternative Credentials Test (ganzseth@gmail.com)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Alternative Credentials Test (ganzseth@gmail.com)", False, f"Exception: {str(e)}")
            return False
    
    def test_database_user_enumeration(self):
        """Test forgot password to check if cganz2279@gmail.com exists in database"""
        try:
            request_data = {
                "email": "cganz2279@gmail.com"
            }
            
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json=request_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    # Check if reset token is returned (indicates user exists)
                    if "reset_token" in data:
                        self.log_test("Database User Existence Check", True, 
                                    f"✅ USER EXISTS - cganz2279@gmail.com found in database (reset token generated)")
                        return True
                    else:
                        self.log_test("Database User Existence Check", True, 
                                    f"✅ FORGOT PASSWORD PROCESSED - Response: {data['message']} (user existence cannot be determined due to security)")
                        return True
                else:
                    self.log_test("Database User Existence Check", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Database User Existence Check", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database User Existence Check", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_login_verification(self):
        """Test super admin login to verify system is working"""
        try:
            login_data = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    user_info = data.get("user", {})
                    self.log_test("Admin Login Verification", True, 
                                f"✅ ADMIN SYSTEM WORKING - Admin: {user_info.get('username', '')} ({user_info.get('role', '')})")
                    return True
                else:
                    self.log_test("Admin Login Verification", False, 
                                f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Admin Login Verification", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all credential verification tests"""
        print("=" * 80)
        print("🚨 URGENT USER CREDENTIAL VERIFICATION TEST")
        print("Testing cganz2279@gmail.com/password123 against production backend")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test 1: Backend connectivity
        connectivity_ok = self.test_backend_connectivity()
        
        if not connectivity_ok:
            print("\n❌ CRITICAL: Cannot connect to production backend")
            return False
        
        # Test 2: User login with reported credentials
        login_success, login_data = self.test_user_login_cganz2279()
        
        # Test 3: Alternative credentials to verify auth system
        alt_success = self.test_alternative_credentials()
        
        # Test 4: Check if user exists in database
        user_exists = self.test_database_user_enumeration()
        
        # Test 5: Verify admin system is working
        admin_working = self.test_admin_login_verification()
        
        # Summary
        print("\n" + "=" * 80)
        print("🔍 CREDENTIAL VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if login_success:
            print("\n✅ RESULT: cganz2279@gmail.com/password123 credentials ARE WORKING")
        else:
            print("\n❌ RESULT: cganz2279@gmail.com/password123 credentials ARE NOT WORKING")
            
            if alt_success:
                print("   ℹ️  Authentication system is functional (ganzseth@gmail.com works)")
                print("   🔍 Issue: User account may not exist or password is incorrect")
            else:
                print("   ⚠️  Authentication system may have issues")
        
        print("\n" + "=" * 80)
        return login_success

def main():
    """Main function to run credential verification"""
    tester = CredentialVerificationTester(PRODUCTION_BACKEND_URL)
    success = tester.run_all_tests()
    
    if success:
        print("✅ User credentials verified successfully")
        sys.exit(0)
    else:
        print("❌ User credential verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main()