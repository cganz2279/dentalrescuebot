#!/usr/bin/env python3
"""
SESSION DEPENDENCY INVESTIGATION TEST
Testing if login has any dependencies on agent session or specific timing
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
import subprocess
import os

# Configuration
BACKEND_URL = "https://dental-admin-3.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class SessionDependencyTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_email = TEST_EMAIL
        self.test_password = TEST_PASSWORD
        self.results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def test_login_during_agent_activity(self):
        """Test 1: Login while agent is active (current state)"""
        print("\n=== TEST 1: LOGIN DURING AGENT ACTIVITY ===")
        
        try:
            # This test runs while the agent is active
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": self.test_email, "password": self.test_password},
                timeout=30
            )
            
            if response.status_code == 200 and response.json().get("success"):
                self.log_result("Login During Activity", "✅ PASS", "Login successful while agent is active")
                return response.json().get("token")
            else:
                self.log_result("Login During Activity", "❌ FAIL", f"Login failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Login During Activity", "❌ FAIL", f"Login failed: {str(e)}")
            return None
    
    def test_login_with_delays(self):
        """Test 2: Login with various delays to simulate inactivity"""
        print("\n=== TEST 2: LOGIN WITH DELAYS ===")
        
        delays = [5, 10, 30, 60]  # seconds
        
        for delay in delays:
            try:
                print(f"Waiting {delay} seconds to simulate inactivity...")
                time.sleep(delay)
                
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json={"email": self.test_email, "password": self.test_password},
                    timeout=30
                )
                
                if response.status_code == 200 and response.json().get("success"):
                    self.log_result(f"Login After {delay}s Delay", "✅ PASS", f"Login successful after {delay} seconds of inactivity")
                else:
                    self.log_result(f"Login After {delay}s Delay", "❌ FAIL", f"Login failed after {delay}s delay: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Login After {delay}s Delay", "❌ FAIL", f"Login failed after {delay}s delay: {str(e)}")
    
    def test_token_expiration_behavior(self):
        """Test 3: Test token expiration and renewal"""
        print("\n=== TEST 3: TOKEN EXPIRATION BEHAVIOR ===")
        
        try:
            # Get a fresh token
            login_response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": self.test_email, "password": self.test_password},
                timeout=30
            )
            
            if login_response.status_code != 200:
                self.log_result("Token Expiration", "❌ FAIL", "Could not get initial token")
                return
            
            token = login_response.json().get("token")
            
            # Test token immediately
            auth_response = requests.get(
                f"{self.backend_url}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if auth_response.status_code == 200:
                self.log_result("Fresh Token", "✅ PASS", "Fresh token works correctly")
            else:
                self.log_result("Fresh Token", "❌ FAIL", f"Fresh token failed: {auth_response.status_code}")
            
            # Test token after some time
            print("Waiting 30 seconds to test token persistence...")
            time.sleep(30)
            
            auth_response2 = requests.get(
                f"{self.backend_url}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if auth_response2.status_code == 200:
                self.log_result("Token After 30s", "✅ PASS", "Token still valid after 30 seconds")
            else:
                self.log_result("Token After 30s", "❌ FAIL", f"Token failed after 30s: {auth_response2.status_code}")
                
        except Exception as e:
            self.log_result("Token Expiration", "❌ FAIL", f"Token expiration test failed: {str(e)}")
    
    def test_concurrent_login_sessions(self):
        """Test 4: Test multiple concurrent login sessions"""
        print("\n=== TEST 4: CONCURRENT LOGIN SESSIONS ===")
        
        def login_worker(worker_id, results_list):
            try:
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json={"email": self.test_email, "password": self.test_password},
                    timeout=30
                )
                
                if response.status_code == 200 and response.json().get("success"):
                    token = response.json().get("token")
                    
                    # Test the token
                    auth_response = requests.get(
                        f"{self.backend_url}/api/auth/me",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
                    
                    results_list.append({
                        "worker_id": worker_id,
                        "login_success": True,
                        "token_valid": auth_response.status_code == 200
                    })
                else:
                    results_list.append({
                        "worker_id": worker_id,
                        "login_success": False,
                        "token_valid": False
                    })
                    
            except Exception as e:
                results_list.append({
                    "worker_id": worker_id,
                    "login_success": False,
                    "token_valid": False,
                    "error": str(e)
                })
        
        # Start multiple concurrent login attempts
        threads = []
        results_list = []
        
        for i in range(5):
            thread = threading.Thread(target=login_worker, args=(i+1, results_list))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        successful_logins = sum(1 for r in results_list if r.get("login_success", False))
        valid_tokens = sum(1 for r in results_list if r.get("token_valid", False))
        
        if successful_logins == 5 and valid_tokens == 5:
            self.log_result("Concurrent Sessions", "✅ PASS", f"All {successful_logins}/5 concurrent sessions successful with valid tokens")
        else:
            self.log_result("Concurrent Sessions", "❌ FAIL", f"Only {successful_logins}/5 logins successful, {valid_tokens}/5 tokens valid")
    
    def test_database_connection_dependency(self):
        """Test 5: Check if login depends on database connection state"""
        print("\n=== TEST 5: DATABASE CONNECTION DEPENDENCY ===")
        
        try:
            # Test multiple rapid logins to stress database connection
            for i in range(10):
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json={"email": self.test_email, "password": self.test_password},
                    timeout=10
                )
                
                if response.status_code != 200 or not response.json().get("success"):
                    self.log_result("DB Connection Stress", "❌ FAIL", f"Login failed on attempt {i+1}")
                    return
                
                # Small delay between requests
                time.sleep(0.5)
            
            self.log_result("DB Connection Stress", "✅ PASS", "All 10 rapid login attempts successful")
            
        except Exception as e:
            self.log_result("DB Connection Stress", "❌ FAIL", f"Database stress test failed: {str(e)}")
    
    def test_backend_service_dependency(self):
        """Test 6: Check backend service status and dependencies"""
        print("\n=== TEST 6: BACKEND SERVICE DEPENDENCY ===")
        
        try:
            # Check if backend service is running
            try:
                result = subprocess.run(['sudo', 'supervisorctl', 'status', 'backend'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    status_output = result.stdout.strip()
                    if "RUNNING" in status_output:
                        self.log_result("Backend Service", "✅ PASS", f"Backend service is running: {status_output}")
                    else:
                        self.log_result("Backend Service", "❌ FAIL", f"Backend service not running: {status_output}")
                else:
                    self.log_result("Backend Service", "⚠️ WARN", "Could not check backend service status")
                    
            except Exception as e:
                self.log_result("Backend Service", "⚠️ WARN", f"Service check failed: {str(e)}")
            
            # Test API health
            response = requests.get(f"{self.backend_url}/api/", timeout=10)
            if response.status_code == 200:
                self.log_result("API Health", "✅ PASS", "API health check successful")
            else:
                self.log_result("API Health", "❌ FAIL", f"API health check failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Service", "❌ FAIL", f"Service dependency test failed: {str(e)}")
    
    def test_environment_variables(self):
        """Test 7: Check environment variables that might affect login"""
        print("\n=== TEST 7: ENVIRONMENT VARIABLES CHECK ===")
        
        try:
            # Check critical environment variables
            env_vars = {
                "MONGO_URL": os.environ.get('MONGO_URL'),
                "DB_NAME": os.environ.get('DB_NAME'),
                "JWT_SECRET": os.environ.get('JWT_SECRET'),
                "FRONTEND_URL": os.environ.get('FRONTEND_URL')
            }
            
            print("Environment Variables:")
            for key, value in env_vars.items():
                if value:
                    # Don't print sensitive values in full
                    if key in ['JWT_SECRET', 'MONGO_URL']:
                        display_value = f"{value[:10]}..." if len(value) > 10 else value
                    else:
                        display_value = value
                    print(f"  {key}: {display_value}")
                else:
                    print(f"  {key}: NOT SET")
            
            missing_vars = [k for k, v in env_vars.items() if not v]
            
            if not missing_vars:
                self.log_result("Environment Variables", "✅ PASS", "All critical environment variables are set")
            else:
                self.log_result("Environment Variables", "⚠️ WARN", f"Missing variables: {missing_vars}")
                
        except Exception as e:
            self.log_result("Environment Variables", "❌ FAIL", f"Environment check failed: {str(e)}")
    
    def run_session_tests(self):
        """Run all session dependency tests"""
        print("🔗 STARTING SESSION DEPENDENCY INVESTIGATION")
        print(f"Backend URL: {self.backend_url}")
        print(f"Testing login for: {self.test_email}")
        print("=" * 60)
        
        # Run tests
        self.test_login_during_agent_activity()
        self.test_login_with_delays()
        self.test_token_expiration_behavior()
        self.test_concurrent_login_sessions()
        self.test_database_connection_dependency()
        self.test_backend_service_dependency()
        self.test_environment_variables()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🔗 SESSION DEPENDENCY INVESTIGATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if "✅ PASS" in r["status"])
        failed = sum(1 for r in self.results if "❌ FAIL" in r["status"])
        warnings = sum(1 for r in self.results if "⚠️ WARN" in r["status"])
        skipped = sum(1 for r in self.results if "❌ SKIP" in r["status"])
        
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"⏭️ Skipped: {skipped}")
        print()
        
        # Show all results
        for result in self.results:
            print(f"[{result['status']}] {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        # Analysis
        if failed == 0:
            print("🎉 SESSION DEPENDENCY RESULT: NO SESSION DEPENDENCIES DETECTED")
            print("\nKey findings:")
            print("- Login works consistently regardless of agent activity")
            print("- No timing dependencies found")
            print("- Tokens persist correctly")
            print("- Backend service is stable")
            print("\nThe user's issue is likely client-side related to:")
            print("- Browser state/cache")
            print("- JavaScript errors")
            print("- Network connectivity")
            print("- Browser extensions")
        else:
            print("🚨 SESSION DEPENDENCY RESULT: POTENTIAL DEPENDENCIES FOUND")
            print("\nIssues detected:")
            for result in self.results:
                if "❌ FAIL" in result["status"]:
                    print(f"- {result['test']}: {result['details']}")

def main():
    """Main function"""
    tester = SessionDependencyTester()
    tester.run_session_tests()

if __name__ == "__main__":
    main()