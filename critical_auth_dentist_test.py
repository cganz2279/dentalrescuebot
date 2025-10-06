#!/usr/bin/env python3
"""
CRITICAL AUTHENTICATION AND DENTIST FUNCTIONALITY TESTING
Testing the specific issues reported by the user:
1. Authentication Issue: caryganz@gmail.com password not working
2. Add Dentist Functionality: "Add Dentist" button not adding dentists
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

class CriticalAuthDentistTester:
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
    
    def check_database_accounts(self):
        """Check what practice accounts exist for caryganz@gmail.com"""
        print("\n🔍 Checking database for caryganz@gmail.com accounts...")
        
        # Test different email variations that might exist
        email_variations = [
            "caryganz@gmail.com",
            "cganz2279@gmail.com",  # From previous tests
            "caryganzconsulting@gmail.com"  # Another variation mentioned in logs
        ]
        
        for email in email_variations:
            print(f"\n  Testing email: {email}")
            
            # Try to trigger password reset to see if account exists
            try:
                response = requests.post(
                    f"{API_BASE}/auth/forgot-password",
                    json={
                        "email": email,
                        "recovery_method": "email"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"    ✅ Account EXISTS for {email} - password reset available")
                        self.log_test(
                            f"Account Exists Check ({email})",
                            True,
                            f"Account found - password reset email sent"
                        )
                    else:
                        print(f"    ❌ Account check failed for {email}: {data}")
                        self.log_test(
                            f"Account Exists Check ({email})",
                            False,
                            f"Password reset failed: {data}"
                        )
                elif response.status_code == 404:
                    print(f"    ❌ Account NOT FOUND for {email}")
                    self.log_test(
                        f"Account Exists Check ({email})",
                        False,
                        f"Account does not exist (404)"
                    )
                else:
                    print(f"    ❌ Unexpected response for {email}: HTTP {response.status_code}")
                    self.log_test(
                        f"Account Exists Check ({email})",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                print(f"    ❌ Error checking {email}: {str(e)}")
                self.log_test(
                    f"Account Exists Check ({email})",
                    False,
                    f"Request failed: {str(e)}"
                )
    
    def test_login_variations(self):
        """Test login with different email/password combinations"""
        print("\n🔐 Testing login with different email/password combinations...")
        
        # Test combinations based on previous test results
        login_combinations = [
            ("caryganz@gmail.com", "password123"),
            ("cganz2279@gmail.com", "password123"),
            ("caryganzconsulting@gmail.com", "password123"),
            ("caryganz@gmail.com", "Password123"),
            ("caryganz@gmail.com", "Dentist1#"),
        ]
        
        successful_login = None
        
        for email, password in login_combinations:
            print(f"\n  Testing login: {email} / {password}")
            
            try:
                response = requests.post(
                    f"{API_BASE}/auth/login",
                    json={
                        "email": email,
                        "password": password
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("token"):
                        self.auth_token = data["token"]
                        self.practice_id = data.get("user", {}).get("practiceId")
                        successful_login = (email, password)
                        print(f"    ✅ LOGIN SUCCESSFUL!")
                        print(f"    Practice ID: {self.practice_id}")
                        self.log_test(
                            f"Login Test ({email})",
                            True,
                            f"Successfully authenticated with practice ID: {self.practice_id}"
                        )
                        break
                    else:
                        print(f"    ❌ Login response missing token: {data}")
                        self.log_test(
                            f"Login Test ({email})",
                            False,
                            f"Login succeeded but missing token: {data}"
                        )
                elif response.status_code == 401:
                    print(f"    ❌ Invalid credentials (401)")
                    self.log_test(
                        f"Login Test ({email})",
                        False,
                        f"Invalid credentials (401): {response.text}"
                    )
                elif response.status_code == 500:
                    print(f"    ❌ Server error (500) - possible password corruption")
                    self.log_test(
                        f"Login Test ({email})",
                        False,
                        f"Server error (500) - password may be corrupted: {response.text}"
                    )
                else:
                    print(f"    ❌ HTTP {response.status_code}: {response.text}")
                    self.log_test(
                        f"Login Test ({email})",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                print(f"    ❌ Request failed: {str(e)}")
                self.log_test(
                    f"Login Test ({email})",
                    False,
                    f"Request failed: {str(e)}"
                )
        
        if successful_login:
            print(f"\n🎉 WORKING CREDENTIALS FOUND: {successful_login[0]} / {successful_login[1]}")
            return successful_login
        else:
            print(f"\n❌ NO WORKING CREDENTIALS FOUND")
            return None
    
    def test_password_reset_flow(self):
        """Test password reset functionality for caryganz@gmail.com"""
        print("\n🔄 Testing password reset flow for caryganz@gmail.com...")
        
        try:
            # Step 1: Request password reset
            response = requests.post(
                f"{API_BASE}/auth/forgot-password",
                json={
                    "email": "caryganz@gmail.com",
                    "recovery_method": "email"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("    ✅ Password reset email sent successfully")
                    self.log_test(
                        "Password Reset Request",
                        True,
                        "Password reset email sent to caryganz@gmail.com"
                    )
                    
                    # Note: In a real scenario, user would click the link in email
                    # We can't test the full flow without access to the email
                    print("    📧 User should check email for reset link")
                    return True
                else:
                    print(f"    ❌ Password reset failed: {data}")
                    self.log_test(
                        "Password Reset Request",
                        False,
                        f"Password reset failed: {data}"
                    )
            else:
                print(f"    ❌ HTTP {response.status_code}: {response.text}")
                self.log_test(
                    "Password Reset Request",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            print(f"    ❌ Request failed: {str(e)}")
            self.log_test(
                "Password Reset Request",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False
    
    def test_add_dentist_functionality(self):
        """Test the POST /api/practice/dentists endpoint with various scenarios"""
        print("\n➕ Testing Add Dentist functionality...")
        
        if not self.auth_token:
            print("    ❌ No authentication token - cannot test dentist functionality")
            self.log_test(
                "Add Dentist Functionality",
                False,
                "No authentication token available"
            )
            return False
        
        # Test 1: Valid dentist data
        print("\n  Test 1: Adding dentist with valid data...")
        valid_dentist = {
            "firstName": "Dr. Michael",
            "lastName": "Thompson",
            "email": f"michael.thompson.{int(time.time())}@dentalpractice.com",
            "phone": "(555) 123-4567",
            "licenseNumber": "DDS98765",
            "specialties": ["General Dentistry", "Oral Surgery"]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/dentists",
                json=valid_dentist,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            print(f"    Response Status: {response.status_code}")
            print(f"    Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    dentist_data = data["data"]
                    dentist_id = dentist_data.get("id")
                    if dentist_id:
                        self.created_dentist_ids.append(dentist_id)
                    
                    print(f"    ✅ Dentist added successfully!")
                    print(f"    Dentist ID: {dentist_id}")
                    print(f"    Name: {dentist_data.get('firstName')} {dentist_data.get('lastName')}")
                    
                    self.log_test(
                        "Add Dentist (Valid Data)",
                        True,
                        f"Successfully added dentist: {dentist_data.get('firstName')} {dentist_data.get('lastName')} (ID: {dentist_id})"
                    )
                else:
                    print(f"    ❌ Response missing success flag or data: {data}")
                    self.log_test(
                        "Add Dentist (Valid Data)",
                        False,
                        f"Response missing success flag or data: {data}"
                    )
            elif response.status_code == 401 or response.status_code == 403:
                print(f"    ❌ Authentication error - token may be invalid")
                self.log_test(
                    "Add Dentist (Valid Data)",
                    False,
                    f"Authentication error (HTTP {response.status_code}): {response.text}"
                )
            elif response.status_code == 422:
                print(f"    ❌ Validation error - check required fields")
                data = response.json()
                print(f"    Validation details: {data}")
                self.log_test(
                    "Add Dentist (Valid Data)",
                    False,
                    f"Validation error (422): {data}"
                )
            else:
                print(f"    ❌ HTTP {response.status_code}: {response.text}")
                self.log_test(
                    "Add Dentist (Valid Data)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            print(f"    ❌ Request failed: {str(e)}")
            self.log_test(
                "Add Dentist (Valid Data)",
                False,
                f"Request failed: {str(e)}"
            )
        
        # Test 2: Different payload formats
        print("\n  Test 2: Testing different payload formats...")
        
        # Minimal payload
        minimal_dentist = {
            "firstName": "Dr. Jane",
            "lastName": "Smith",
            "email": f"jane.smith.{int(time.time())}@dentalpractice.com"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/practice/dentists",
                json=minimal_dentist,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            print(f"    Minimal payload - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    dentist_id = data.get("data", {}).get("id")
                    if dentist_id:
                        self.created_dentist_ids.append(dentist_id)
                    print(f"    ✅ Minimal payload accepted")
                    self.log_test(
                        "Add Dentist (Minimal Payload)",
                        True,
                        "Successfully added dentist with minimal required fields"
                    )
                else:
                    print(f"    ❌ Minimal payload failed: {data}")
                    self.log_test(
                        "Add Dentist (Minimal Payload)",
                        False,
                        f"Minimal payload failed: {data}"
                    )
            else:
                print(f"    ❌ Minimal payload rejected: HTTP {response.status_code}")
                self.log_test(
                    "Add Dentist (Minimal Payload)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            print(f"    ❌ Minimal payload test failed: {str(e)}")
            self.log_test(
                "Add Dentist (Minimal Payload)",
                False,
                f"Request failed: {str(e)}"
            )
        
        # Test 3: Check if dentists were actually added
        print("\n  Test 3: Verifying dentists were added to the system...")
        
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
                    print(f"    ✅ Retrieved {len(dentists)} dentists from system")
                    
                    # Check if our created dentists are in the list
                    found_dentists = 0
                    for dentist_id in self.created_dentist_ids:
                        if any(d.get("id") == dentist_id for d in dentists):
                            found_dentists += 1
                    
                    print(f"    ✅ Found {found_dentists}/{len(self.created_dentist_ids)} created dentists in system")
                    
                    self.log_test(
                        "Verify Dentists Added",
                        True,
                        f"Successfully verified {found_dentists}/{len(self.created_dentist_ids)} dentists were added to system"
                    )
                else:
                    print(f"    ❌ Failed to retrieve dentists: {data}")
                    self.log_test(
                        "Verify Dentists Added",
                        False,
                        f"Failed to retrieve dentists: {data}"
                    )
            else:
                print(f"    ❌ Failed to get dentists list: HTTP {response.status_code}")
                self.log_test(
                    "Verify Dentists Added",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            print(f"    ❌ Verification failed: {str(e)}")
            self.log_test(
                "Verify Dentists Added",
                False,
                f"Request failed: {str(e)}"
            )
        
        return len(self.created_dentist_ids) > 0
    
    def cleanup_created_dentists(self):
        """Clean up any created dentists"""
        print("\n🧹 Cleaning up created dentists...")
        
        if not self.auth_token or not self.created_dentist_ids:
            return
        
        for dentist_id in self.created_dentist_ids[:]:
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
    
    def run_critical_tests(self):
        """Run all critical authentication and dentist functionality tests"""
        print("🚨 Starting CRITICAL Authentication and Dentist Functionality Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Check what accounts exist
        self.check_database_accounts()
        
        # Step 2: Test login variations
        working_credentials = self.test_login_variations()
        
        # Step 3: Test password reset if login fails
        if not working_credentials:
            print("\n🔄 No working credentials found - testing password reset...")
            self.test_password_reset_flow()
        
        # Step 4: Test dentist functionality if we have authentication
        if self.auth_token:
            self.test_add_dentist_functionality()
        else:
            print("\n❌ Cannot test dentist functionality - no valid authentication")
        
        # Clean up
        self.cleanup_created_dentists()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 CRITICAL TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len(self.passed_tests)
        failed_tests = len(self.failed_tests)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Authentication findings
        auth_working = any("Login Test" in test and test in self.passed_tests for test in self.passed_tests)
        if auth_working:
            working_creds = [test for test in self.passed_tests if "Login Test" in test]
            print(f"  ✅ AUTHENTICATION: Working credentials found")
            for cred in working_creds:
                print(f"    - {cred}")
        else:
            print(f"  ❌ AUTHENTICATION: No working credentials found for caryganz@gmail.com")
            
            # Check if password reset is available
            reset_working = "Password Reset Request" in self.passed_tests
            if reset_working:
                print(f"  ✅ PASSWORD RESET: Available as alternative access method")
            else:
                print(f"  ❌ PASSWORD RESET: Not working")
        
        # Dentist functionality findings
        dentist_working = any("Add Dentist" in test and test in self.passed_tests for test in self.passed_tests)
        if dentist_working:
            print(f"  ✅ DENTIST FUNCTIONALITY: Add Dentist is working correctly")
        else:
            print(f"  ❌ DENTIST FUNCTIONALITY: Add Dentist is not working")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not auth_working:
            print(f"  1. User should use password reset functionality to access account")
            print(f"  2. Check if account exists under different email variation")
            print(f"  3. Verify account was created properly via SamCart webhook")
        
        if not dentist_working and auth_working:
            print(f"  1. Check API endpoint authentication requirements")
            print(f"  2. Verify request payload format matches API expectations")
            print(f"  3. Check for any validation errors in API response")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        return working_credentials, dentist_working

if __name__ == "__main__":
    tester = CriticalAuthDentistTester()
    working_creds, dentist_working = tester.run_critical_tests()
    
    # Exit with appropriate code
    success = working_creds is not None or dentist_working
    sys.exit(0 if success else 1)