#!/usr/bin/env python3
"""
Focused Password Reset and Username Recovery Testing
Tests the new authentication endpoints for password reset functionality
"""

import requests
import json
import sys

BACKEND_URL = "https://dental-pdf-sync.preview.emergentagent.com/api"

class PasswordResetTester:
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
        return success
    
    def test_forgot_password_valid_email(self):
        """Test POST /api/auth/forgot-password with valid email"""
        try:
            request_data = {"email": "admin@smithdental.com"}
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    if "reset_token" in data:
                        self.test_reset_token = data["reset_token"]
                        return self.log_test("Forgot Password (Valid Email)", True, 
                                           f"Reset token generated: {self.test_reset_token[:8]}...")
                    else:
                        return self.log_test("Forgot Password (Valid Email)", True, 
                                           "Password reset request processed")
                else:
                    return self.log_test("Forgot Password (Valid Email)", False, "Invalid response format")
            else:
                return self.log_test("Forgot Password (Valid Email)", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Forgot Password (Valid Email)", False, f"Exception: {str(e)}")
    
    def test_forgot_password_invalid_email(self):
        """Test POST /api/auth/forgot-password with invalid email"""
        try:
            request_data = {"email": "nonexistent@example.com"}
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    expected_message = "If an account with this email exists, password reset instructions have been sent."
                    if expected_message in data["message"]:
                        return self.log_test("Forgot Password (Invalid Email)", True, 
                                           "Properly prevents email enumeration")
                    else:
                        return self.log_test("Forgot Password (Invalid Email)", False, 
                                           f"Unexpected message: {data['message']}")
                else:
                    return self.log_test("Forgot Password (Invalid Email)", False, "Invalid response format")
            else:
                return self.log_test("Forgot Password (Invalid Email)", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Forgot Password (Invalid Email)", False, f"Exception: {str(e)}")
    
    def test_forgot_username_valid_practice(self):
        """Test POST /api/auth/forgot-username with valid practice"""
        try:
            request_data = {
                "practice_name": "Smith Dental Practice",
                "phone": "555-123-4567",
                "adminPassword": "password123"
            }
            response = self.session.post(f"{self.base_url}/auth/forgot-username", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    if "practice_name" in data and "email" in data:
                        return self.log_test("Forgot Username (Valid Practice)", True, 
                                           f"Found practice: {data['practice_name']}, Email: {data['email']}")
                    else:
                        return self.log_test("Forgot Username (Valid Practice)", True, 
                                           "Username recovery request processed")
                else:
                    return self.log_test("Forgot Username (Valid Practice)", False, "Invalid response format")
            else:
                return self.log_test("Forgot Username (Valid Practice)", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Forgot Username (Valid Practice)", False, f"Exception: {str(e)}")
    
    def test_forgot_username_invalid_practice(self):
        """Test POST /api/auth/forgot-username with invalid practice"""
        try:
            request_data = {
                "practice_name": "Nonexistent Dental Practice",
                "phone": "555-999-9999",
                "adminPassword": "somepassword"
            }
            response = self.session.post(f"{self.base_url}/auth/forgot-username", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    expected_message = "If a practice with these details exists, username recovery information has been sent."
                    if expected_message in data["message"]:
                        return self.log_test("Forgot Username (Invalid Practice)", True, 
                                           "Properly prevents information disclosure")
                    else:
                        return self.log_test("Forgot Username (Invalid Practice)", False, 
                                           f"Unexpected message: {data['message']}")
                else:
                    return self.log_test("Forgot Username (Invalid Practice)", False, "Invalid response format")
            else:
                return self.log_test("Forgot Username (Invalid Practice)", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Forgot Username (Invalid Practice)", False, f"Exception: {str(e)}")
    
    def test_validate_reset_token_valid(self):
        """Test GET /api/auth/validate-reset-token/{token} with valid token"""
        if not hasattr(self, 'test_reset_token') or not self.test_reset_token:
            return self.log_test("Validate Reset Token (Valid)", False, "No reset token available")
            
        try:
            response = self.session.get(f"{self.base_url}/auth/validate-reset-token/{self.test_reset_token}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("valid") and "user" in data:
                    user_info = data["user"]
                    if "email" in user_info and "firstName" in user_info:
                        return self.log_test("Validate Reset Token (Valid)", True, 
                                           f"Valid token for user: {user_info['firstName']} ({user_info['email']})")
                    else:
                        return self.log_test("Validate Reset Token (Valid)", False, "Missing user information")
                else:
                    return self.log_test("Validate Reset Token (Valid)", False, "Invalid response format")
            else:
                return self.log_test("Validate Reset Token (Valid)", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Validate Reset Token (Valid)", False, f"Exception: {str(e)}")
    
    def test_validate_reset_token_invalid(self):
        """Test GET /api/auth/validate-reset-token/{token} with invalid token"""
        try:
            invalid_token = "invalid-token-12345"
            response = self.session.get(f"{self.base_url}/auth/validate-reset-token/{invalid_token}")
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Invalid or expired reset token" in data["detail"]:
                    return self.log_test("Validate Reset Token (Invalid)", True, 
                                       f"Properly rejected invalid token: {data['detail']}")
                else:
                    return self.log_test("Validate Reset Token (Invalid)", False, 
                                       f"Unexpected error message: {data.get('detail', 'No detail')}")
            else:
                return self.log_test("Validate Reset Token (Invalid)", False, 
                                   f"Expected 400, got {response.status_code}")
        except Exception as e:
            return self.log_test("Validate Reset Token (Invalid)", False, f"Exception: {str(e)}")
    
    def test_reset_password_valid_token(self):
        """Test POST /api/auth/reset-password with valid token"""
        if not hasattr(self, 'test_reset_token') or not self.test_reset_token:
            return self.log_test("Reset Password (Valid Token)", False, "No reset token available")
            
        try:
            request_data = {
                "reset_token": self.test_reset_token,
                "new_password": "newpassword123"
            }
            response = self.session.post(f"{self.base_url}/auth/reset-password", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "message" in data:
                    if "Password reset successful" in data["message"]:
                        return self.log_test("Reset Password (Valid Token)", True, 
                                           "Password reset successful with valid token")
                    else:
                        return self.log_test("Reset Password (Valid Token)", False, 
                                           f"Unexpected message: {data['message']}")
                else:
                    return self.log_test("Reset Password (Valid Token)", False, "Invalid response format")
            else:
                return self.log_test("Reset Password (Valid Token)", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Reset Password (Valid Token)", False, f"Exception: {str(e)}")
    
    def test_reset_password_invalid_token(self):
        """Test POST /api/auth/reset-password with invalid token"""
        try:
            request_data = {
                "reset_token": "invalid-token-12345",
                "new_password": "newpassword123"
            }
            response = self.session.post(f"{self.base_url}/auth/reset-password", json=request_data)
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Invalid or expired reset token" in data["detail"]:
                    return self.log_test("Reset Password (Invalid Token)", True, 
                                       f"Properly rejected invalid token: {data['detail']}")
                else:
                    return self.log_test("Reset Password (Invalid Token)", False, 
                                       f"Unexpected error message: {data.get('detail', 'No detail')}")
            else:
                return self.log_test("Reset Password (Invalid Token)", False, 
                                   f"Expected 400, got {response.status_code}")
        except Exception as e:
            return self.log_test("Reset Password (Invalid Token)", False, f"Exception: {str(e)}")
    
    def test_reset_password_weak_password(self):
        """Test POST /api/auth/reset-password with weak password"""
        # Generate a new reset token for this test
        forgot_response = self.session.post(f"{self.base_url}/auth/forgot-password", 
                                          json={"email": "admin@smithdental.com"})
        if forgot_response.status_code == 200:
            forgot_data = forgot_response.json()
            if "reset_token" in forgot_data:
                test_token = forgot_data["reset_token"]
            else:
                return self.log_test("Reset Password (Weak Password)", False, "Could not generate reset token")
        else:
            return self.log_test("Reset Password (Weak Password)", False, "Could not generate reset token")
            
        try:
            request_data = {
                "reset_token": test_token,
                "new_password": "weak"  # Less than 6 characters, no numbers
            }
            response = self.session.post(f"{self.base_url}/auth/reset-password", json=request_data)
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Password must be at least 6 characters with letters and numbers" in data["detail"]:
                    return self.log_test("Reset Password (Weak Password)", True, 
                                       f"Properly rejected weak password: {data['detail']}")
                else:
                    return self.log_test("Reset Password (Weak Password)", False, 
                                       f"Unexpected error message: {data.get('detail', 'No detail')}")
            else:
                return self.log_test("Reset Password (Weak Password)", False, 
                                   f"Expected 400, got {response.status_code}")
        except Exception as e:
            return self.log_test("Reset Password (Weak Password)", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all password reset and username recovery tests"""
        print(f"🔐 Password Reset & Username Recovery Testing")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        tests = [
            self.test_forgot_password_valid_email,
            self.test_forgot_password_invalid_email,
            self.test_forgot_username_valid_practice,
            self.test_forgot_username_invalid_practice,
            self.test_validate_reset_token_valid,
            self.test_validate_reset_token_invalid,
            self.test_reset_password_valid_token,
            self.test_reset_password_invalid_token,
            self.test_reset_password_weak_password
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All password reset tests passed! Authentication system is secure.")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False

def main():
    """Main function to run the tests"""
    tester = PasswordResetTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()