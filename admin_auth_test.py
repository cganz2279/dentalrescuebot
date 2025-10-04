#!/usr/bin/env python3
"""
Admin Authentication System Testing Script
Tests the specific admin authentication issues reported by the user:
1. Admin login with credentials cganz@admin.com/Dentist1#
2. GET /api/admin/dashboard with token
3. GET /api/admin/tutorials with token  
4. POST /api/admin/tutorials with token

Focus: Identifying 401 Unauthorized errors and "Token expired" messages
"""

import requests
import json
import os
from datetime import datetime
import jwt

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class AdminAuthTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def decode_token_info(self, token):
        """Decode JWT token to inspect its contents (without verification)"""
        try:
            # Decode without verification to inspect contents
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            return f"Error decoding token: {str(e)}"
    
    def test_admin_login(self):
        """Test admin login and token generation"""
        try:
            print("\n🔐 Testing Admin Login...")
            print(f"Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
            
            response = requests.post(
                f"{BACKEND_URL}/api/admin/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                },
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                self.admin_token = data.get("token")
                if self.admin_token:
                    # Decode token to inspect
                    token_info = self.decode_token_info(self.admin_token)
                    print(f"Token Info: {json.dumps(token_info, indent=2, default=str)}")
                    
                    self.log_test("Admin Login", True, f"Successfully authenticated. Token length: {len(self.admin_token)} chars")
                    return True
                else:
                    self.log_test("Admin Login", False, "No token in response")
                    return False
            else:
                error_text = response.text
                self.log_test("Admin Login", False, f"Login failed: {response.status_code} - {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin token"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_admin_dashboard(self):
        """Test GET /api/admin/dashboard with token"""
        try:
            print("\n📊 Testing Admin Dashboard Access...")
            print(f"Using token: {self.admin_token[:50]}..." if self.admin_token else "No token available")
            
            response = requests.get(
                f"{BACKEND_URL}/api/admin/dashboard",
                headers=self.get_admin_headers(),
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Dashboard Data Keys: {list(data.keys())}")
                if 'stats' in data:
                    print(f"Stats: {data['stats']}")
                
                self.log_test("Admin Dashboard", True, f"Dashboard accessed successfully. Data keys: {list(data.keys())}")
                return True
            elif response.status_code == 401:
                error_text = response.text
                print(f"401 Error Details: {error_text}")
                self.log_test("Admin Dashboard", False, f"401 Unauthorized: {error_text}")
                return False
            else:
                error_text = response.text
                print(f"Error Details: {error_text}")
                self.log_test("Admin Dashboard", False, f"Failed: {response.status_code} - {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard", False, f"Dashboard error: {str(e)}")
            return False
    
    def test_admin_tutorials_get(self):
        """Test GET /api/admin/tutorials with token"""
        try:
            print("\n📚 Testing Admin Tutorials GET...")
            print(f"Using token: {self.admin_token[:50]}..." if self.admin_token else "No token available")
            
            response = requests.get(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=self.get_admin_headers(),
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Tutorials Count: {len(data) if isinstance(data, list) else 'Not a list'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"First Tutorial Keys: {list(data[0].keys()) if data[0] else 'Empty'}")
                
                self.log_test("Admin Tutorials GET", True, f"Tutorials retrieved successfully. Count: {len(data) if isinstance(data, list) else 'Unknown'}")
                return True
            elif response.status_code == 401:
                error_text = response.text
                print(f"401 Error Details: {error_text}")
                self.log_test("Admin Tutorials GET", False, f"401 Unauthorized: {error_text}")
                return False
            else:
                error_text = response.text
                print(f"Error Details: {error_text}")
                self.log_test("Admin Tutorials GET", False, f"Failed: {response.status_code} - {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Tutorials GET", False, f"Tutorials GET error: {str(e)}")
            return False
    
    def test_admin_tutorials_post(self):
        """Test POST /api/admin/tutorials with token (minimal test data)"""
        try:
            print("\n📝 Testing Admin Tutorials POST...")
            print(f"Using token: {self.admin_token[:50]}..." if self.admin_token else "No token available")
            
            # Create minimal test video content
            test_video_content = b"fake video content for auth testing"
            
            files = {
                'video': ('test_auth_video.mp4', test_video_content, 'video/mp4')
            }
            
            data = {
                'title': 'Auth Test Tutorial',
                'description': 'Testing admin authentication for tutorial creation',
                'category': 'test',
                'order': 999
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.post(
                f"{BACKEND_URL}/api/admin/tutorials",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response Data: {json.dumps(result, indent=2)}")
                tutorial_id = result.get("tutorial_id")
                
                self.log_test("Admin Tutorials POST", True, f"Tutorial created successfully. ID: {tutorial_id}")
                return True
            elif response.status_code == 401:
                error_text = response.text
                print(f"401 Error Details: {error_text}")
                self.log_test("Admin Tutorials POST", False, f"401 Unauthorized: {error_text}")
                return False
            else:
                error_text = response.text
                print(f"Error Details: {error_text}")
                self.log_test("Admin Tutorials POST", False, f"Failed: {response.status_code} - {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Tutorials POST", False, f"Tutorials POST error: {str(e)}")
            return False
    
    def test_token_validation_details(self):
        """Test token validation in detail"""
        try:
            print("\n🔍 Testing Token Validation Details...")
            
            if not self.admin_token:
                self.log_test("Token Validation", False, "No token available for validation")
                return False
            
            # Decode token to check expiration
            token_info = self.decode_token_info(self.admin_token)
            print(f"Token Payload: {json.dumps(token_info, indent=2, default=str)}")
            
            if isinstance(token_info, dict):
                exp = token_info.get('exp')
                iat = token_info.get('iat')
                role = token_info.get('role')
                admin_email = token_info.get('adminEmail')
                
                if exp:
                    exp_time = datetime.fromtimestamp(exp)
                    current_time = datetime.now()
                    time_until_exp = exp_time - current_time
                    
                    print(f"Token expires at: {exp_time}")
                    print(f"Current time: {current_time}")
                    print(f"Time until expiration: {time_until_exp}")
                    
                    if time_until_exp.total_seconds() > 0:
                        self.log_test("Token Validation", True, f"Token valid for {time_until_exp}. Role: {role}, Email: {admin_email}")
                    else:
                        self.log_test("Token Validation", False, f"Token expired {abs(time_until_exp)} ago")
                else:
                    self.log_test("Token Validation", False, "No expiration time in token")
            else:
                self.log_test("Token Validation", False, f"Could not decode token: {token_info}")
            
            return True
            
        except Exception as e:
            self.log_test("Token Validation", False, f"Token validation error: {str(e)}")
            return False
    
    def test_jwt_secret_consistency(self):
        """Test if JWT_SECRET is consistent by making multiple requests"""
        try:
            print("\n🔑 Testing JWT Secret Consistency...")
            
            # Make multiple login requests to see if tokens are consistent
            tokens = []
            for i in range(3):
                response = requests.post(
                    f"{BACKEND_URL}/api/admin/login",
                    json={
                        "email": ADMIN_EMAIL,
                        "password": ADMIN_PASSWORD
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token")
                    if token:
                        tokens.append(token)
                        token_info = self.decode_token_info(token)
                        print(f"Token {i+1} info: {json.dumps(token_info, indent=2, default=str)}")
            
            if len(tokens) >= 2:
                # Compare token structures (they should have same structure but different iat/exp)
                token1_info = self.decode_token_info(tokens[0])
                token2_info = self.decode_token_info(tokens[1])
                
                if isinstance(token1_info, dict) and isinstance(token2_info, dict):
                    # Check if role and adminEmail are consistent
                    role_consistent = token1_info.get('role') == token2_info.get('role')
                    email_consistent = token1_info.get('adminEmail') == token2_info.get('adminEmail')
                    
                    if role_consistent and email_consistent:
                        self.log_test("JWT Secret Consistency", True, "Multiple tokens have consistent structure and claims")
                    else:
                        self.log_test("JWT Secret Consistency", False, "Token claims are inconsistent between requests")
                else:
                    self.log_test("JWT Secret Consistency", False, "Could not decode tokens for comparison")
            else:
                self.log_test("JWT Secret Consistency", False, f"Could only generate {len(tokens)} tokens for comparison")
            
            return True
            
        except Exception as e:
            self.log_test("JWT Secret Consistency", False, f"JWT secret test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all admin authentication tests"""
        print("🚀 Starting Admin Authentication System Tests")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print("=" * 60)
        
        # Step 1: Admin Login
        if not self.test_admin_login():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Token validation details
        self.test_token_validation_details()
        
        # Step 3: JWT Secret consistency
        self.test_jwt_secret_consistency()
        
        # Step 4: Test admin dashboard
        self.test_admin_dashboard()
        
        # Step 5: Test admin tutorials GET
        self.test_admin_tutorials_get()
        
        # Step 6: Test admin tutorials POST
        self.test_admin_tutorials_post()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 ADMIN AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🔍 AUTHENTICATION ANALYSIS:")
        if self.admin_token:
            token_info = self.decode_token_info(self.admin_token)
            if isinstance(token_info, dict):
                print(f"  - Token Role: {token_info.get('role')}")
                print(f"  - Admin Email: {token_info.get('adminEmail')}")
                print(f"  - Token Expiry: {datetime.fromtimestamp(token_info.get('exp', 0))}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = AdminAuthTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All admin authentication tests passed!")
    else:
        print("\n⚠️ Some authentication tests failed. Check the details above.")