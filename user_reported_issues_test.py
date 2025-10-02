#!/usr/bin/env python3

import requests
import json
import sys
import uuid
import time

# Configuration - Using the exact preview URL reported by user
BASE_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"
FRONTEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com"
PRACTICE_EMAIL = "cganz2279@gmail.com"
PRACTICE_PASSWORD = "password123"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class UserReportedIssuesTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_session = requests.Session()
        self.auth_token = None
        self.admin_token = None
        self.issues_found = []
        
    def log_issue(self, issue_type, description, severity="HIGH"):
        """Log an issue found during testing"""
        self.issues_found.append({
            "type": issue_type,
            "description": description,
            "severity": severity
        })
        
    def test_frontend_accessibility(self):
        """Test if frontend is accessible and loading"""
        print("🌐 Testing Frontend Accessibility...")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for React app indicators
                if "react" in content.lower() or "root" in content:
                    print("   ✅ Frontend is accessible and appears to be React app")
                    
                    # Check for specific elements that should be present
                    if "dental" in content.lower() or "practice" in content.lower():
                        print("   ✅ Frontend contains dental/practice related content")
                    else:
                        print("   ⚠️  Frontend may not be the correct dental app")
                        self.log_issue("FRONTEND", "Frontend doesn't contain expected dental content", "MEDIUM")
                        
                    return True
                else:
                    print("   ❌ Frontend doesn't appear to be a React app")
                    self.log_issue("FRONTEND", "Frontend is not loading React application", "HIGH")
                    return False
            else:
                print(f"   ❌ Frontend not accessible - Status: {response.status_code}")
                self.log_issue("FRONTEND", f"Frontend returns status {response.status_code}", "HIGH")
                return False
                
        except Exception as e:
            print(f"   ❌ Frontend accessibility error: {str(e)}")
            self.log_issue("FRONTEND", f"Frontend connection error: {str(e)}", "HIGH")
            return False
    
    def test_admin_route_accessibility(self):
        """Test if admin route is accessible"""
        print("\n👑 Testing Admin Route Accessibility...")
        
        try:
            # Test admin route
            admin_url = f"{FRONTEND_URL}/admin"
            response = requests.get(admin_url, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ Admin route is accessible")
                
                # Check if it's showing admin login or redirecting to practice login
                content = response.text
                if "admin" in content.lower():
                    print("   ✅ Admin route shows admin-related content")
                    return True
                else:
                    print("   ⚠️  Admin route may be showing practice login instead")
                    self.log_issue("ADMIN_ROUTE", "Admin route not showing admin login interface", "HIGH")
                    return False
            else:
                print(f"   ❌ Admin route not accessible - Status: {response.status_code}")
                self.log_issue("ADMIN_ROUTE", f"Admin route returns status {response.status_code}", "HIGH")
                return False
                
        except Exception as e:
            print(f"   ❌ Admin route error: {str(e)}")
            self.log_issue("ADMIN_ROUTE", f"Admin route connection error: {str(e)}", "HIGH")
            return False
    
    def test_practice_login_flow(self):
        """Test complete practice login flow"""
        print("\n🔐 Testing Practice Login Flow...")
        
        # Step 1: Test login endpoint
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
                    practice_id = data.get("user", {}).get("practiceId")
                    
                    print(f"   ✅ Practice login successful")
                    print(f"      Practice ID: {practice_id}")
                    
                    # Set auth header
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    # Step 2: Test dashboard access
                    dashboard_response = self.session.get(f"{BASE_URL}/practice/dashboard", timeout=10)
                    
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        if dashboard_data.get("success"):
                            practice_name = dashboard_data.get("data", {}).get("name", "Unknown")
                            print(f"   ✅ Dashboard accessible - Practice: {practice_name}")
                            return True
                        else:
                            print(f"   ❌ Dashboard API failed: {dashboard_data.get('error')}")
                            self.log_issue("PRACTICE_DASHBOARD", f"Dashboard API error: {dashboard_data.get('error')}", "HIGH")
                            return False
                    else:
                        print(f"   ❌ Dashboard not accessible - Status: {dashboard_response.status_code}")
                        self.log_issue("PRACTICE_DASHBOARD", f"Dashboard returns status {dashboard_response.status_code}", "HIGH")
                        return False
                else:
                    print(f"   ❌ Practice login failed: {data.get('error')}")
                    self.log_issue("PRACTICE_LOGIN", f"Login failed: {data.get('error')}", "HIGH")
                    return False
            else:
                print(f"   ❌ Practice login failed - Status: {response.status_code}")
                self.log_issue("PRACTICE_LOGIN", f"Login endpoint returns status {response.status_code}", "HIGH")
                return False
                
        except Exception as e:
            print(f"   ❌ Practice login error: {str(e)}")
            self.log_issue("PRACTICE_LOGIN", f"Login connection error: {str(e)}", "HIGH")
            return False
    
    def test_admin_login_flow(self):
        """Test complete admin login flow"""
        print("\n👑 Testing Admin Login Flow...")
        
        # Step 1: Test admin login endpoint
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
                    
                    print(f"   ✅ Admin login successful")
                    
                    # Set auth header
                    self.admin_session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    
                    # Step 2: Test admin dashboard access
                    dashboard_response = self.admin_session.get(f"{BASE_URL}/admin/dashboard", timeout=10)
                    
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        if dashboard_data.get("success"):
                            stats = dashboard_data.get("stats", {})
                            total_practices = stats.get("total_practices", 0)
                            print(f"   ✅ Admin dashboard accessible - {total_practices} practices")
                            
                            # Step 3: Test practices list
                            practices_response = self.admin_session.get(f"{BASE_URL}/admin/practices", timeout=10)
                            
                            if practices_response.status_code == 200:
                                practices_data = practices_response.json()
                                if practices_data.get("success"):
                                    practices = practices_data.get("practices", [])
                                    print(f"   ✅ Admin practices list accessible - {len(practices)} practices")
                                    return True
                                else:
                                    print(f"   ❌ Admin practices list failed: {practices_data.get('error')}")
                                    self.log_issue("ADMIN_PRACTICES", f"Practices list error: {practices_data.get('error')}", "HIGH")
                                    return False
                            else:
                                print(f"   ❌ Admin practices list not accessible - Status: {practices_response.status_code}")
                                self.log_issue("ADMIN_PRACTICES", f"Practices list returns status {practices_response.status_code}", "HIGH")
                                return False
                        else:
                            print(f"   ❌ Admin dashboard failed: {dashboard_data.get('error')}")
                            self.log_issue("ADMIN_DASHBOARD", f"Dashboard error: {dashboard_data.get('error')}", "HIGH")
                            return False
                    else:
                        print(f"   ❌ Admin dashboard not accessible - Status: {dashboard_response.status_code}")
                        self.log_issue("ADMIN_DASHBOARD", f"Dashboard returns status {dashboard_response.status_code}", "HIGH")
                        return False
                else:
                    print(f"   ❌ Admin login failed: {data.get('error')}")
                    self.log_issue("ADMIN_LOGIN", f"Admin login failed: {data.get('error')}", "HIGH")
                    return False
            else:
                print(f"   ❌ Admin login failed - Status: {response.status_code}")
                self.log_issue("ADMIN_LOGIN", f"Admin login endpoint returns status {response.status_code}", "HIGH")
                return False
                
        except Exception as e:
            print(f"   ❌ Admin login error: {str(e)}")
            self.log_issue("ADMIN_LOGIN", f"Admin login connection error: {str(e)}", "HIGH")
            return False
    
    def test_create_practice_functionality(self):
        """Test practice creation functionality"""
        print("\n➕ Testing Create Practice Functionality...")
        
        if not self.admin_token:
            print("   ❌ No admin token available")
            self.log_issue("CREATE_PRACTICE", "Cannot test practice creation without admin token", "HIGH")
            return False
        
        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        practice_data = {
            "practiceName": f"Test Practice {test_id}",
            "adminEmail": f"test.admin.{test_id}@example.com",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "phone": "555-123-4567",
            "tempPassword": "TempPass123!",
            "address": "123 Test Street, Test City, TS 12345",
            "subscriptionType": "trial",
            "trialDays": 30
        }
        
        try:
            response = self.admin_session.post(f"{BASE_URL}/admin/create-practice", json=practice_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice_id = data.get("practice", {}).get("id")
                    practice_name = data.get("practice", {}).get("name")
                    print(f"   ✅ Practice created successfully")
                    print(f"      Practice ID: {practice_id}")
                    print(f"      Practice Name: {practice_name}")
                    
                    # Test welcome email functionality
                    return self.test_welcome_email_with_practice(practice_data)
                else:
                    print(f"   ❌ Practice creation failed: {data.get('error')}")
                    self.log_issue("CREATE_PRACTICE", f"Practice creation failed: {data.get('error')}", "HIGH")
                    return False
            else:
                print(f"   ❌ Practice creation failed - Status: {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_issue("CREATE_PRACTICE", f"Practice creation returns status {response.status_code}", "HIGH")
                return False
                
        except Exception as e:
            print(f"   ❌ Practice creation error: {str(e)}")
            self.log_issue("CREATE_PRACTICE", f"Practice creation connection error: {str(e)}", "HIGH")
            return False
    
    def test_welcome_email_with_practice(self, practice_data):
        """Test welcome email functionality with proper data structure"""
        print("\n📧 Testing Welcome Email with Practice Data...")
        
        # Use the correct data structure expected by the endpoint
        email_data = {
            "practiceData": {
                "practiceName": practice_data["practiceName"]
            },
            "adminCredentials": {
                "adminEmail": practice_data["adminEmail"],
                "adminFirstName": practice_data["adminFirstName"],
                "adminLastName": practice_data["adminLastName"],
                "tempPassword": practice_data["tempPassword"]
            },
            "appUrl": FRONTEND_URL
        }
        
        try:
            response = self.admin_session.post(f"{BASE_URL}/admin/send-welcome-email", json=email_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Welcome email sent successfully")
                    print(f"      Message: {data.get('message')}")
                    return True
                else:
                    print(f"   ❌ Welcome email failed: {data.get('error')}")
                    self.log_issue("WELCOME_EMAIL", f"Welcome email failed: {data.get('error')}", "MEDIUM")
                    return False
            else:
                print(f"   ❌ Welcome email failed - Status: {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_issue("WELCOME_EMAIL", f"Welcome email returns status {response.status_code}", "MEDIUM")
                return False
                
        except Exception as e:
            print(f"   ❌ Welcome email error: {str(e)}")
            self.log_issue("WELCOME_EMAIL", f"Welcome email connection error: {str(e)}", "MEDIUM")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔗 Testing CORS Configuration...")
        
        # Test preflight request
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        try:
            response = requests.options(f"{BASE_URL}/auth/login", headers=headers, timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            print(f"   📋 CORS Headers: {cors_headers}")
            
            # Check if CORS is properly configured
            allow_origin = cors_headers.get('Access-Control-Allow-Origin')
            if allow_origin == '*' or FRONTEND_URL in str(allow_origin):
                print("   ✅ CORS appears to be configured correctly")
                return True
            else:
                print("   ⚠️  CORS may not be configured for frontend URL")
                self.log_issue("CORS", f"CORS may not allow frontend URL: {FRONTEND_URL}", "MEDIUM")
                return False
                
        except Exception as e:
            print(f"   ❌ CORS test error: {str(e)}")
            self.log_issue("CORS", f"CORS test connection error: {str(e)}", "MEDIUM")
            return False
    
    def run_user_reported_tests(self):
        """Run all tests for user-reported issues"""
        print("🚨 USER REPORTED ISSUES INVESTIGATION")
        print("=" * 60)
        print("User Report: 'Nothing is working. No preview. Admin does not work.'")
        print("=" * 60)
        
        # Define tests in order of importance
        tests = [
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("Admin Route Accessibility", self.test_admin_route_accessibility),
            ("Practice Login Flow", self.test_practice_login_flow),
            ("Admin Login Flow", self.test_admin_login_flow),
            ("Create Practice Functionality", self.test_create_practice_functionality),
            ("CORS Configuration", self.test_cors_configuration)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            try:
                result = test_func()
                results.append((test_name, result))
                
            except Exception as e:
                print(f"❌ {test_name}: CRITICAL ERROR - {str(e)}")
                results.append((test_name, False))
                self.log_issue(test_name.upper().replace(" ", "_"), f"Critical error: {str(e)}", "HIGH")
        
        # Generate comprehensive analysis
        self.generate_user_issue_analysis(results)
    
    def generate_user_issue_analysis(self, results):
        """Generate analysis of user-reported issues"""
        print("\n" + "="*80)
        print("🚨 USER REPORTED ISSUES ANALYSIS")
        print("="*80)
        
        # Categorize results
        critical_failures = []
        working_systems = []
        
        for test_name, result in results:
            if result:
                working_systems.append(test_name)
            else:
                critical_failures.append(test_name)
        
        # Report critical failures
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES CONFIRMING USER REPORTS:")
            print("-" * 60)
            for failure in critical_failures:
                print(f"❌ {failure}")
        
        # Report working systems
        if working_systems:
            print("\n✅ WORKING SYSTEMS:")
            print("-" * 60)
            for system in working_systems:
                print(f"✅ {system}")
        
        # Detailed issue analysis
        if self.issues_found:
            print("\n🔍 DETAILED ISSUE ANALYSIS:")
            print("-" * 60)
            
            high_issues = [i for i in self.issues_found if i["severity"] == "HIGH"]
            medium_issues = [i for i in self.issues_found if i["severity"] == "MEDIUM"]
            
            if high_issues:
                print("\n🚨 HIGH SEVERITY ISSUES:")
                for issue in high_issues:
                    print(f"   ❌ {issue['type']}: {issue['description']}")
            
            if medium_issues:
                print("\n⚠️  MEDIUM SEVERITY ISSUES:")
                for issue in medium_issues:
                    print(f"   ⚠️  {issue['type']}: {issue['description']}")
        
        # Overall assessment
        total_tests = len(results)
        critical_count = len(critical_failures)
        working_count = len(working_systems)
        
        print(f"\n📊 OVERALL USER ISSUE ASSESSMENT:")
        print(f"   Total Systems Tested: {total_tests}")
        print(f"   Critical Failures: {critical_count}")
        print(f"   Working Systems: {working_count}")
        print(f"   High Severity Issues: {len([i for i in self.issues_found if i['severity'] == 'HIGH'])}")
        print(f"   Medium Severity Issues: {len([i for i in self.issues_found if i['severity'] == 'MEDIUM'])}")
        
        if critical_count > 0:
            print(f"\n🚨 CONCLUSION: USER REPORTS ARE ACCURATE")
            print(f"   {critical_count} critical system(s) are failing")
            print(f"   User experience is severely impacted")
            return False
        else:
            print(f"\n✅ CONCLUSION: SYSTEMS APPEAR TO BE WORKING")
            print(f"   User issues may be browser/cache related")
            return True

def main():
    """Main function to run user-reported issue tests"""
    tester = UserReportedIssuesTester()
    tester.run_user_reported_tests()

if __name__ == "__main__":
    main()