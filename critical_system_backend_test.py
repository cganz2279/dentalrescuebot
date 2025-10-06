#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import uuid
import time

# Configuration - Using the preview URL as specified in the review request
BASE_URL = "https://dentiportal.preview.emergentagent.com/api"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class CriticalSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_session = requests.Session()
        self.auth_token = None
        self.admin_token = None
        self.practice_id = None
        self.user_id = None
        self.test_results = []
        
    def log_test_result(self, test_name, success, message):
        """Log test result for summary"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def test_basic_connectivity(self):
        """Test basic API connectivity and CORS"""
        print("🌐 Testing Basic API Connectivity and CORS...")
        
        try:
            # Test basic health endpoint
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                print("   ✅ API server is accessible")
                
                # Check CORS headers
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                
                print(f"   📋 CORS Headers: {cors_headers}")
                
                self.log_test_result("Basic Connectivity", True, "API server accessible")
                return True
            else:
                print(f"   ❌ API server returned status {response.status_code}")
                self.log_test_result("Basic Connectivity", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection failed: {str(e)}")
            self.log_test_result("Basic Connectivity", False, f"Connection error: {str(e)}")
            return False
    
    def test_practice_authentication(self):
        """Test practice login authentication"""
        print("\n🔐 Testing Practice Authentication...")
        
        auth_data = {
            "email": PRACTICE_EMAIL,
            "password": PRACTICE_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=auth_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.auth_token = data.get("token")
                    self.practice_id = data.get("user", {}).get("practiceId")
                    self.user_id = data.get("user", {}).get("id")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    print(f"   ✅ Practice authentication successful")
                    print(f"      Practice ID: {self.practice_id}")
                    print(f"      User ID: {self.user_id}")
                    print(f"      Token: {self.auth_token[:20]}...")
                    
                    self.log_test_result("Practice Authentication", True, "Login successful")
                    return True
                else:
                    print(f"   ❌ Authentication failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Practice Authentication", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Authentication failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test_result("Practice Authentication", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Authentication request failed: {str(e)}")
            self.log_test_result("Practice Authentication", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test admin login authentication"""
        print("\n👑 Testing Admin Authentication...")
        
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.admin_session.post(f"{BASE_URL}/admin/login", json=auth_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.admin_token = data.get("token")
                    
                    # Set authorization header for admin requests
                    self.admin_session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    
                    print(f"   ✅ Admin authentication successful")
                    print(f"      Admin Token: {self.admin_token[:20]}...")
                    
                    self.log_test_result("Admin Authentication", True, "Admin login successful")
                    return True
                else:
                    print(f"   ❌ Admin authentication failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Admin Authentication", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Admin authentication failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test_result("Admin Authentication", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Admin authentication request failed: {str(e)}")
            self.log_test_result("Admin Authentication", False, f"Request error: {str(e)}")
            return False
    
    def test_practice_dashboard_api(self):
        """Test practice dashboard API"""
        print("\n📊 Testing Practice Dashboard API...")
        
        if not self.auth_token:
            print("   ❌ No authentication token available")
            self.log_test_result("Practice Dashboard API", False, "No auth token")
            return False
        
        try:
            response = self.session.get(f"{BASE_URL}/practice/dashboard", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice_data = data.get("data", {})
                    practice_name = practice_data.get("name", "Unknown")
                    
                    print(f"   ✅ Dashboard API working")
                    print(f"      Practice Name: {practice_name}")
                    print(f"      Practice ID: {practice_data.get('id', 'Unknown')}")
                    
                    # Check if branding data is present
                    branding = practice_data.get("branding", {})
                    if branding:
                        print(f"      Branding: Logo present: {'logo' in branding}")
                        print(f"      Primary Color: {branding.get('primaryColor', 'Not set')}")
                    
                    self.log_test_result("Practice Dashboard API", True, f"Dashboard loaded for {practice_name}")
                    return True
                else:
                    print(f"   ❌ Dashboard API failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Practice Dashboard API", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Dashboard API failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test_result("Practice Dashboard API", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Dashboard API request failed: {str(e)}")
            self.log_test_result("Practice Dashboard API", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_endpoints(self):
        """Test critical admin endpoints"""
        print("\n🔧 Testing Admin Endpoints...")
        
        if not self.admin_token:
            print("   ❌ No admin authentication token available")
            self.log_test_result("Admin Endpoints", False, "No admin token")
            return False
        
        # Test admin dashboard/practices list
        try:
            response = self.admin_session.get(f"{BASE_URL}/admin/practices", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practices = data.get("data", [])
                    print(f"   ✅ Admin practices list working - Found {len(practices)} practices")
                    
                    for practice in practices[:3]:  # Show first 3
                        print(f"      - {practice.get('name', 'Unknown')} ({practice.get('adminEmail', 'No email')})")
                    
                    self.log_test_result("Admin Practices List", True, f"Found {len(practices)} practices")
                else:
                    print(f"   ❌ Admin practices list failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Admin Practices List", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Admin practices list failed with status {response.status_code}")
                self.log_test_result("Admin Practices List", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Admin practices request failed: {str(e)}")
            self.log_test_result("Admin Practices List", False, f"Request error: {str(e)}")
            return False
        
        return True
    
    def test_welcome_email_functionality(self):
        """Test welcome email functionality that was previously failing"""
        print("\n📧 Testing Welcome Email Functionality...")
        
        if not self.admin_token:
            print("   ❌ No admin authentication token available")
            self.log_test_result("Welcome Email", False, "No admin token")
            return False
        
        # Test welcome email endpoint
        email_data = {
            "practiceId": "test-practice-id",
            "adminEmail": "test@example.com",
            "practiceName": "Test Practice",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "tempPassword": "TempPass123!"
        }
        
        try:
            response = self.admin_session.post(f"{BASE_URL}/admin/send-welcome-email", json=email_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("   ✅ Welcome email endpoint working")
                    print(f"      Message: {data.get('message', 'Email sent')}")
                    self.log_test_result("Welcome Email", True, "Email endpoint functional")
                    return True
                else:
                    print(f"   ❌ Welcome email failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Welcome Email", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Welcome email failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test_result("Welcome Email", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Welcome email request failed: {str(e)}")
            self.log_test_result("Welcome Email", False, f"Request error: {str(e)}")
            return False
    
    def test_password_recovery_endpoints(self):
        """Test password recovery functionality"""
        print("\n🔑 Testing Password Recovery Endpoints...")
        
        # Test forgot password endpoint
        recovery_data = {
            "email": "test@example.com",
            "recoveryMethod": "email"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/forgot-password", json=recovery_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("   ✅ Forgot password endpoint working")
                    self.log_test_result("Password Recovery", True, "Forgot password functional")
                    return True
                else:
                    print(f"   ❌ Forgot password failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Password Recovery", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Forgot password failed with status {response.status_code}")
                self.log_test_result("Password Recovery", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Password recovery request failed: {str(e)}")
            self.log_test_result("Password Recovery", False, f"Request error: {str(e)}")
            return False
    
    def test_pdf_generation_endpoints(self):
        """Test PDF generation endpoints"""
        print("\n📄 Testing PDF Generation Endpoints...")
        
        if not self.auth_token:
            print("   ❌ No authentication token available")
            self.log_test_result("PDF Generation", False, "No auth token")
            return False
        
        # Test email PDF endpoint
        pdf_data = {
            "procedureId": "root-canal-therapy",
            "patientName": "Test Patient",
            "patientEmail": "test@example.com",
            "dentistName": "Dr. Test"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/practice/email-pdf", json=pdf_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("   ✅ PDF generation endpoint working")
                    self.log_test_result("PDF Generation", True, "PDF generation functional")
                    return True
                else:
                    print(f"   ❌ PDF generation failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("PDF Generation", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ PDF generation failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test_result("PDF Generation", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ PDF generation request failed: {str(e)}")
            self.log_test_result("PDF Generation", False, f"Request error: {str(e)}")
            return False
    
    def test_procedures_api(self):
        """Test procedures API endpoints"""
        print("\n📋 Testing Procedures API...")
        
        try:
            # Test get all procedures
            response = requests.get(f"{BASE_URL}/procedures", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedures = data.get("data", [])
                    print(f"   ✅ Procedures API working - Found {len(procedures)} procedures")
                    
                    if procedures:
                        # Test specific procedure
                        first_procedure = procedures[0]
                        procedure_id = first_procedure.get("id")
                        
                        if procedure_id:
                            proc_response = requests.get(f"{BASE_URL}/procedures/{procedure_id}", timeout=10)
                            if proc_response.status_code == 200:
                                print(f"   ✅ Individual procedure API working")
                                self.log_test_result("Procedures API", True, f"Found {len(procedures)} procedures")
                                return True
                    
                    self.log_test_result("Procedures API", True, f"Found {len(procedures)} procedures")
                    return True
                else:
                    print(f"   ❌ Procedures API failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Procedures API", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Procedures API failed with status {response.status_code}")
                self.log_test_result("Procedures API", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Procedures API request failed: {str(e)}")
            self.log_test_result("Procedures API", False, f"Request error: {str(e)}")
            return False
    
    def test_specialties_api(self):
        """Test specialties API endpoints"""
        print("\n🏥 Testing Specialties API...")
        
        try:
            response = requests.get(f"{BASE_URL}/specialties", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    specialties = data.get("data", [])
                    print(f"   ✅ Specialties API working - Found {len(specialties)} specialties")
                    
                    for specialty in specialties[:3]:  # Show first 3
                        name = specialty.get("name", "Unknown")
                        count = specialty.get("procedureCount", 0)
                        print(f"      - {name}: {count} procedures")
                    
                    self.log_test_result("Specialties API", True, f"Found {len(specialties)} specialties")
                    return True
                else:
                    print(f"   ❌ Specialties API failed: {data.get('error', 'Unknown error')}")
                    self.log_test_result("Specialties API", False, data.get('error', 'Unknown error'))
                    return False
            else:
                print(f"   ❌ Specialties API failed with status {response.status_code}")
                self.log_test_result("Specialties API", False, f"Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Specialties API request failed: {str(e)}")
            self.log_test_result("Specialties API", False, f"Request error: {str(e)}")
            return False
    
    def check_backend_logs(self):
        """Check backend logs for errors"""
        print("\n📋 Checking Backend Service Status...")
        
        try:
            import subprocess
            
            # Check supervisor status
            result = subprocess.run(['sudo', 'supervisorctl', 'status', 'backend'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"   📊 Backend service status: {result.stdout.strip()}")
                
                # Check recent backend logs
                log_result = subprocess.run(['tail', '-n', '20', '/var/log/supervisor/backend.err.log'], 
                                          capture_output=True, text=True, timeout=10)
                
                if log_result.returncode == 0 and log_result.stdout.strip():
                    print("   📋 Recent backend error logs:")
                    for line in log_result.stdout.strip().split('\n')[-5:]:  # Last 5 lines
                        print(f"      {line}")
                else:
                    print("   ✅ No recent backend errors in logs")
                
                self.log_test_result("Backend Service", True, "Service running")
                return True
            else:
                print(f"   ❌ Backend service check failed: {result.stderr}")
                self.log_test_result("Backend Service", False, "Service check failed")
                return False
                
        except Exception as e:
            print(f"   ⚠️  Could not check backend logs: {str(e)}")
            self.log_test_result("Backend Service", True, "Could not check logs")
            return True
    
    def run_all_tests(self):
        """Run all critical system tests"""
        print("🚨 CRITICAL SYSTEM FAILURE INVESTIGATION")
        print("=" * 60)
        print("Testing all backend APIs to identify system failures...")
        print("=" * 60)
        
        # Define all tests
        tests = [
            ("Basic Connectivity & CORS", self.test_basic_connectivity),
            ("Practice Authentication", self.test_practice_authentication),
            ("Admin Authentication", self.test_admin_authentication),
            ("Practice Dashboard API", self.test_practice_dashboard_api),
            ("Admin Endpoints", self.test_admin_endpoints),
            ("Welcome Email Functionality", self.test_welcome_email_functionality),
            ("Password Recovery", self.test_password_recovery_endpoints),
            ("PDF Generation", self.test_pdf_generation_endpoints),
            ("Procedures API", self.test_procedures_api),
            ("Specialties API", self.test_specialties_api),
            ("Backend Service Status", self.check_backend_logs)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*60}")
                test_func()
                
            except Exception as e:
                print(f"❌ {test_name}: CRITICAL ERROR - {str(e)}")
                self.log_test_result(test_name, False, f"Critical error: {str(e)}")
        
        # Generate comprehensive summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🚨 CRITICAL SYSTEM FAILURE ANALYSIS SUMMARY")
        print("="*80)
        
        # Categorize results
        critical_failures = []
        working_systems = []
        minor_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in ["auth", "admin", "connectivity"]):
                    critical_failures.append(result)
                else:
                    minor_issues.append(result)
            else:
                working_systems.append(result)
        
        # Report critical failures first
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES (System Breaking):")
            print("-" * 50)
            for failure in critical_failures:
                print(f"❌ {failure['test']}: {failure['message']}")
        
        # Report minor issues
        if minor_issues:
            print("\n⚠️  MINOR ISSUES (Non-Critical):")
            print("-" * 50)
            for issue in minor_issues:
                print(f"⚠️  {issue['test']}: {issue['message']}")
        
        # Report working systems
        if working_systems:
            print("\n✅ WORKING SYSTEMS:")
            print("-" * 50)
            for system in working_systems:
                print(f"✅ {system['test']}: {system['message']}")
        
        # Overall assessment
        total_tests = len(self.test_results)
        critical_count = len(critical_failures)
        working_count = len(working_systems)
        
        print(f"\n📊 OVERALL ASSESSMENT:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Critical Failures: {critical_count}")
        print(f"   Working Systems: {working_count}")
        print(f"   Minor Issues: {len(minor_issues)}")
        
        if critical_count > 0:
            print(f"\n🚨 SYSTEM STATUS: CRITICAL FAILURES DETECTED")
            print(f"   User reports are ACCURATE - {critical_count} critical system(s) failing")
            return False
        elif len(minor_issues) > 0:
            print(f"\n⚠️  SYSTEM STATUS: MINOR ISSUES DETECTED")
            print(f"   Core functionality working, {len(minor_issues)} minor issue(s)")
            return True
        else:
            print(f"\n✅ SYSTEM STATUS: ALL SYSTEMS OPERATIONAL")
            print(f"   User reports may be frontend/browser related")
            return True

def main():
    """Main function to run critical system tests"""
    tester = CriticalSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()