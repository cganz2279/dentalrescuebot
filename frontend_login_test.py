#!/usr/bin/env python3
"""
FRONTEND LOGIN INVESTIGATION TEST
Testing frontend login functionality to identify potential frontend issues
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
FRONTEND_URL = "https://dental-admin-3.preview.emergentagent.com"
BACKEND_URL = "https://dental-admin-3.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class FrontendLoginTester:
    def __init__(self):
        self.frontend_url = FRONTEND_URL
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
    
    def test_frontend_accessibility(self):
        """Test 1: Check if frontend is accessible"""
        print("\n=== TEST 1: FRONTEND ACCESSIBILITY ===")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                self.log_result("Frontend Access", "✅ PASS", f"Frontend is accessible at {self.frontend_url}")
                
                # Check if it's the React app
                if "react" in response.text.lower() or "root" in response.text:
                    self.log_result("React App Check", "✅ PASS", "React application detected")
                else:
                    self.log_result("React App Check", "⚠️ WARN", "May not be React app or static content")
                    
            else:
                self.log_result("Frontend Access", "❌ FAIL", f"Frontend not accessible: {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend Access", "❌ FAIL", f"Frontend access failed: {str(e)}")
    
    def test_backend_cors_configuration(self):
        """Test 2: Check CORS configuration for frontend requests"""
        print("\n=== TEST 2: CORS CONFIGURATION TEST ===")
        
        try:
            # Simulate a preflight request
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = requests.options(f"{self.backend_url}/api/auth/login", headers=headers, timeout=10)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
            if cors_headers["Access-Control-Allow-Origin"] in ["*", self.frontend_url]:
                self.log_result("CORS Configuration", "✅ PASS", "CORS is properly configured for frontend")
            else:
                self.log_result("CORS Configuration", "⚠️ WARN", f"CORS may not be configured for frontend origin: {self.frontend_url}")
                
        except Exception as e:
            self.log_result("CORS Configuration", "❌ FAIL", f"CORS test failed: {str(e)}")
    
    def test_login_with_frontend_headers(self):
        """Test 3: Test login with headers that frontend would send"""
        print("\n=== TEST 3: LOGIN WITH FRONTEND HEADERS ===")
        
        try:
            url = f"{self.backend_url}/api/auth/login"
            payload = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            # Headers that a browser/frontend would typically send
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Origin": self.frontend_url,
                "Referer": f"{self.frontend_url}/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    self.log_result("Frontend Headers Login", "✅ PASS", "Login successful with frontend-style headers")
                    self.auth_token = response_data.get("token")
                else:
                    self.log_result("Frontend Headers Login", "❌ FAIL", f"Login failed: {response_data}")
            else:
                self.log_result("Frontend Headers Login", "❌ FAIL", f"Login failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Frontend Headers Login", "❌ FAIL", f"Frontend headers login failed: {str(e)}")
    
    def test_session_storage_simulation(self):
        """Test 4: Simulate session storage behavior"""
        print("\n=== TEST 4: SESSION STORAGE SIMULATION ===")
        
        if not hasattr(self, 'auth_token'):
            self.log_result("Session Storage", "❌ SKIP", "No auth token available")
            return
        
        try:
            # Simulate storing token and making authenticated requests
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {self.auth_token}",
                "Origin": self.frontend_url,
                "Referer": f"{self.frontend_url}/"
            })
            
            # Test authenticated endpoint
            response = session.get(f"{self.backend_url}/api/auth/me", timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.log_result("Session Storage", "✅ PASS", f"Authenticated request successful: {user_data.get('user', {}).get('email')}")
            else:
                self.log_result("Session Storage", "❌ FAIL", f"Authenticated request failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Session Storage", "❌ FAIL", f"Session storage test failed: {str(e)}")
    
    def test_multiple_tab_simulation(self):
        """Test 5: Simulate multiple browser tabs"""
        print("\n=== TEST 5: MULTIPLE TAB SIMULATION ===")
        
        try:
            # Simulate multiple sessions (tabs)
            sessions = []
            
            for i in range(3):
                session = requests.Session()
                
                # Login in each "tab"
                login_response = session.post(
                    f"{self.backend_url}/api/auth/login",
                    json={"email": self.test_email, "password": self.test_password},
                    headers={
                        "Content-Type": "application/json",
                        "Origin": self.frontend_url
                    },
                    timeout=30
                )
                
                if login_response.status_code == 200:
                    token = login_response.json().get("token")
                    session.headers.update({"Authorization": f"Bearer {token}"})
                    sessions.append(session)
                else:
                    self.log_result("Multiple Tabs", "❌ FAIL", f"Login failed in tab {i+1}")
                    return
            
            # Test all sessions work simultaneously
            all_working = True
            for i, session in enumerate(sessions):
                response = session.get(f"{self.backend_url}/api/auth/me", timeout=10)
                if response.status_code != 200:
                    all_working = False
                    break
            
            if all_working:
                self.log_result("Multiple Tabs", "✅ PASS", f"All {len(sessions)} simulated tabs working correctly")
            else:
                self.log_result("Multiple Tabs", "❌ FAIL", "Some tabs failed authentication")
                
        except Exception as e:
            self.log_result("Multiple Tabs", "❌ FAIL", f"Multiple tabs test failed: {str(e)}")
    
    def test_network_timeout_scenarios(self):
        """Test 6: Test various network timeout scenarios"""
        print("\n=== TEST 6: NETWORK TIMEOUT SCENARIOS ===")
        
        try:
            # Test with very short timeout
            try:
                response = requests.post(
                    f"{self.backend_url}/api/auth/login",
                    json={"email": self.test_email, "password": self.test_password},
                    timeout=0.1  # Very short timeout
                )
                self.log_result("Short Timeout", "⚠️ WARN", "Login succeeded with very short timeout - may indicate caching")
            except requests.exceptions.Timeout:
                self.log_result("Short Timeout", "✅ PASS", "Short timeout behaved as expected")
            
            # Test with reasonable timeout
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": self.test_email, "password": self.test_password},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result("Normal Timeout", "✅ PASS", "Login successful with normal timeout")
            else:
                self.log_result("Normal Timeout", "❌ FAIL", f"Login failed with normal timeout: {response.status_code}")
                
        except Exception as e:
            self.log_result("Network Timeout", "❌ FAIL", f"Timeout test failed: {str(e)}")
    
    def test_browser_cache_simulation(self):
        """Test 7: Simulate browser cache behavior"""
        print("\n=== TEST 7: BROWSER CACHE SIMULATION ===")
        
        try:
            # Test with cache-control headers
            headers = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": self.test_email, "password": self.test_password},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("No Cache Login", "✅ PASS", "Login successful with no-cache headers")
            else:
                self.log_result("No Cache Login", "❌ FAIL", f"Login failed with no-cache headers: {response.status_code}")
            
            # Test with If-None-Match header (simulating cached request)
            headers_with_etag = {
                "Content-Type": "application/json",
                "If-None-Match": "some-etag-value"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": self.test_email, "password": self.test_password},
                headers=headers_with_etag,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("ETag Login", "✅ PASS", "Login successful with ETag headers")
            else:
                self.log_result("ETag Login", "❌ FAIL", f"Login failed with ETag headers: {response.status_code}")
                
        except Exception as e:
            self.log_result("Browser Cache", "❌ FAIL", f"Cache simulation failed: {str(e)}")
    
    def run_frontend_tests(self):
        """Run all frontend tests"""
        print("🌐 STARTING FRONTEND LOGIN INVESTIGATION")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Testing login for: {self.test_email}")
        print("=" * 60)
        
        # Run tests
        self.test_frontend_accessibility()
        self.test_backend_cors_configuration()
        self.test_login_with_frontend_headers()
        self.test_session_storage_simulation()
        self.test_multiple_tab_simulation()
        self.test_network_timeout_scenarios()
        self.test_browser_cache_simulation()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🌐 FRONTEND LOGIN INVESTIGATION SUMMARY")
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
        
        # Provide recommendations
        if failed == 0:
            print("🎉 FRONTEND INVESTIGATION RESULT: NO CRITICAL ISSUES DETECTED")
            print("\nRecommendations for user:")
            print("1. Clear browser cache and cookies")
            print("2. Try incognito/private browsing mode")
            print("3. Disable browser extensions temporarily")
            print("4. Check browser console for JavaScript errors")
            print("5. Try a different browser")
        else:
            print("🚨 FRONTEND INVESTIGATION RESULT: ISSUES DETECTED")
            print("\nCritical issues found:")
            for result in self.results:
                if "❌ FAIL" in result["status"]:
                    print(f"- {result['test']}: {result['details']}")

def main():
    """Main function"""
    tester = FrontendLoginTester()
    tester.run_frontend_tests()

if __name__ == "__main__":
    main()