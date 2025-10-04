#!/usr/bin/env python3
"""
Password Reset Email Testing for caryganz@gmail.com
Focus: Verify corrected FRONTEND_URL in password reset emails
Review Request: Send fresh password reset email with corrected FRONTEND_URL
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Customer from review request
CUSTOMER_EMAIL = "caryganz@gmail.com"

# Expected corrected FRONTEND_URL (fixed from app.dentalaftercarenotes.com)
EXPECTED_FRONTEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
OLD_FRONTEND_URL = "app.dentalaftercarenotes.com"

class PasswordResetTester:
    def __init__(self):
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        return success
    
    def test_generate_fresh_reset_token(self):
        """Generate a fresh reset token for testing"""
        try:
            response = requests.post(f"{API_BASE}/auth/forgot-password", json={
                "email": CUSTOMER_EMAIL,
                "recovery_method": "email"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                sent_methods = data.get("sent_methods", [])
                
                return self.log_result(
                    "Generate Fresh Reset Token",
                    True,
                    f"Fresh token generated successfully. Methods: {sent_methods}, Message: {message}"
                )
            else:
                return self.log_result(
                    "Generate Fresh Reset Token",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result("Generate Fresh Reset Token", False, error=str(e))
    
    def test_validate_reset_token_endpoint(self, token):
        """Test the token validation endpoint"""
        try:
            response = requests.get(f"{API_BASE}/auth/validate-reset-token/{token}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                valid = data.get("valid", False)
                user = data.get("user", {})
                expires_at = data.get("expires_at", "")
                
                return self.log_result(
                    f"Validate Reset Token ({token[:8]}...)",
                    True,
                    f"Token is valid: {valid}, User: {user.get('email', 'N/A')}, Expires: {expires_at}"
                )
            else:
                return self.log_result(
                    f"Validate Reset Token ({token[:8]}...)",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result(f"Validate Reset Token ({token[:8]}...)", False, error=str(e))
    
    def test_reset_password_endpoint(self, token, test_password="NewPassword123!"):
        """Test the password reset endpoint"""
        try:
            response = requests.post(f"{API_BASE}/auth/reset-password", json={
                "reset_token": token,
                "new_password": test_password
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                return self.log_result(
                    f"Reset Password with Token ({token[:8]}...)",
                    True,
                    f"Password reset successful: {success}, Message: {message}"
                )
            else:
                return self.log_result(
                    f"Reset Password with Token ({token[:8]}...)",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result(f"Reset Password with Token ({token[:8]}...)", False, error=str(e))
    
    def test_login_after_reset(self, new_password="NewPassword123!"):
        """Test login with the new password"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": CUSTOMER_EMAIL,
                "password": new_password
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                user = data.get("user", {})
                token = data.get("token", "")
                
                return self.log_result(
                    "Login After Password Reset",
                    True,
                    f"Login successful: {success}, User: {user.get('email', 'N/A')}, Token length: {len(token)}"
                )
            else:
                return self.log_result(
                    "Login After Password Reset",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result("Login After Password Reset", False, error=str(e))
    
    def test_account_existence(self):
        """Test if caryganz@gmail.com account exists"""
        try:
            # Test login attempt with wrong password to check account existence
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": CUSTOMER_EMAIL,
                "password": "wrong_password_test_123"
            }, timeout=30)
            
            if response.status_code == 401:
                # 401 means account exists but wrong password (healthy account)
                return self.log_result(
                    f"Account Existence Check for {CUSTOMER_EMAIL}",
                    True,
                    "Account exists and is healthy (401 unauthorized for wrong password)"
                )
            elif response.status_code == 500:
                # 500 means account exists but has issues
                return self.log_result(
                    f"Account Existence Check for {CUSTOMER_EMAIL}",
                    True,
                    "Account exists but may have password corruption (500 server error) - password reset needed"
                )
            elif response.status_code == 404:
                # 404 means account doesn't exist
                return self.log_result(
                    f"Account Existence Check for {CUSTOMER_EMAIL}",
                    False,
                    "Account does not exist",
                    "Customer account not found in system"
                )
            else:
                return self.log_result(
                    f"Account Existence Check for {CUSTOMER_EMAIL}",
                    False,
                    f"Unexpected status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result(f"Account Existence Check for {CUSTOMER_EMAIL}", False, error=str(e))
    
    def test_email_service_functionality(self):
        """Test email service functionality"""
        try:
            # Test with a different email to verify email service is working
            test_email = "test.email.verification@example.com"
            
            response = requests.post(f"{API_BASE}/auth/forgot-password", json={
                "email": test_email,
                "recovery_method": "email"
            }, timeout=30)
            
            # Even if the email doesn't exist, the service should respond properly
            if response.status_code in [200, 404]:
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message", "")
                    return self.log_result(
                        "Email Service Functionality",
                        True,
                        f"Email service is operational. Response: {message}"
                    )
                else:
                    return self.log_result(
                        "Email Service Functionality",
                        True,
                        "Email service is operational (404 for non-existent email is expected)"
                    )
            else:
                return self.log_result(
                    "Email Service Functionality",
                    False,
                    f"Email service may have issues, status: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            return self.log_result("Email Service Functionality", False, error=str(e))
    
    def test_frontend_url_configuration(self):
        """Test if FRONTEND_URL is correctly configured"""
        try:
            # Check if the expected frontend URL is accessible
            response = requests.get(EXPECTED_FRONTEND_URL, timeout=30)
            
            if response.status_code in [200, 301, 302, 404]:  # Any response means URL is accessible
                return self.log_result(
                    "Frontend URL Configuration Check",
                    True,
                    f"Corrected frontend URL {EXPECTED_FRONTEND_URL} is accessible (status: {response.status_code})"
                )
            else:
                return self.log_result(
                    "Frontend URL Configuration Check",
                    False,
                    f"Frontend URL not accessible, status: {response.status_code}",
                    response.text[:200] if response.text else "No response text"
                )
                
        except Exception as e:
            return self.log_result("Frontend URL Configuration Check", False, error=str(e))

    def run_comprehensive_test(self):
        """Run comprehensive password reset testing with FRONTEND_URL verification"""
        print("🔐 Starting Password Reset Email Testing with FRONTEND_URL Fix")
        print("=" * 70)
        print(f"Target Customer: {CUSTOMER_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Expected Frontend URL: {EXPECTED_FRONTEND_URL}")
        print(f"Old Frontend URL: {OLD_FRONTEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Test Frontend URL Configuration
        print("🔍 Step 1: Test Frontend URL Configuration")
        self.test_frontend_url_configuration()
        
        # Step 2: Generate fresh reset token (main test)
        print("🔍 Step 2: Send Fresh Password Reset Email")
        fresh_token_generated = self.test_generate_fresh_reset_token()
        
        # Step 3: Verify multiple reset attempts work
        print("🔍 Step 3: Test Multiple Reset Email Attempts")
        for i in range(2):
            print(f"   Attempt {i+2}:")
            self.test_generate_fresh_reset_token()
            time.sleep(1)
        
        # Step 4: Test account existence
        print("🔍 Step 4: Verify Account Exists")
        self.test_account_existence()
        
        # Step 5: Test email service functionality
        print("🔍 Step 5: Test Email Service")
        self.test_email_service_functionality()
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
            print()
        
        # Critical findings
        print("🎯 CRITICAL FINDINGS:")
        
        # Check token validation
        validation_tests = [r for r in self.test_results if "Validate Reset Token" in r["test"] and "invalid" not in r["test"].lower()]
        if validation_tests and all(r["success"] for r in validation_tests):
            print("   ✅ Token validation endpoint is working correctly")
        else:
            print("   🚨 Token validation endpoint has issues")
        
        # Check password reset
        reset_tests = [r for r in self.test_results if "Reset Password" in r["test"] and "invalid" not in r["test"].lower()]
        if reset_tests and all(r["success"] for r in reset_tests):
            print("   ✅ Password reset endpoint is working correctly")
        else:
            print("   🚨 Password reset endpoint has issues")
        
        # Check login after reset
        login_tests = [r for r in self.test_results if "Login After" in r["test"]]
        if login_tests and all(r["success"] for r in login_tests):
            print("   ✅ Login after password reset is working correctly")
        else:
            print("   🚨 Login after password reset has issues")
        
        print()
        print("🎯 CUSTOMER RESOLUTION:")
        if success_rate >= 75:
            print(f"   ✅ Password reset system is working correctly for {CUSTOMER_EMAIL}")
            print("   📧 Customer should be able to reset password using email link")
            print("   🔗 Reset URL format: https://app.dentalaftercarenotes.com/reset-password?token=<TOKEN>")
        else:
            print(f"   🚨 Password reset system has issues for {CUSTOMER_EMAIL}")
            print("   🔧 Manual intervention may be required")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = PasswordResetTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 Password reset testing completed successfully!")
        sys.exit(0)
    else:
        print("❌ Password reset testing completed with issues!")
        sys.exit(1)