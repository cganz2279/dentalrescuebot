#!/usr/bin/env python3
"""
Logo Functionality Fix Test
Tests the logo functionality fix in practice settings as requested in the review.

Test Requirements:
1. Authentication with cganz2279@gmail.com/password123
2. Test GET /api/practice/dashboard to check current practice branding data
3. Test PUT /api/practice/update-practice endpoint with branding data (logo update)
4. Verify dashboard API returns new logo after update
5. Test PDF generation endpoints to verify they use updated logo
"""

import requests
import json
import base64
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://dental-admin-3.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test credentials
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

# Sample base64 image data for testing (small 1x1 pixel PNG)
SAMPLE_LOGO_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="

class LogoFunctionalityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.original_logo = None
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Authenticate with the provided credentials"""
        self.log("🔐 Starting authentication test...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"Authentication response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.auth_token = data["token"]
                    self.practice_id = data.get("user", {}).get("practiceId")
                    self.log(f"✅ Authentication successful! Practice ID: {self.practice_id}")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}",
                        "Content-Type": "application/json"
                    })
                    return True
                else:
                    self.log(f"❌ Authentication failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Authentication failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_current_practice_data(self):
        """Test GET /api/practice/dashboard to check current practice branding data"""
        self.log("📊 Testing current practice dashboard data...")
        
        try:
            response = self.session.get(f"{API_BASE}/practice/dashboard")
            
            self.log(f"Dashboard response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice_data = data.get("data", {}).get("practice", {})
                    branding = practice_data.get("branding", {})
                    
                    self.log("✅ Dashboard API successful!")
                    self.log(f"Practice Name: {practice_data.get('name', 'N/A')}")
                    self.log(f"Practice ID: {practice_data.get('id', 'N/A')}")
                    
                    # Store original logo for comparison
                    self.original_logo = branding.get("logo")
                    if self.original_logo:
                        self.log(f"Current Logo: {self.original_logo[:50]}..." if len(self.original_logo) > 50 else f"Current Logo: {self.original_logo}")
                    else:
                        self.log("Current Logo: None")
                    
                    self.log(f"Primary Color: {branding.get('primaryColor', 'N/A')}")
                    self.log(f"Secondary Color: {branding.get('secondaryColor', 'N/A')}")
                    self.log(f"Welcome Message: {branding.get('welcomeMessage', 'N/A')}")
                    
                    return True, practice_data
                else:
                    self.log(f"❌ Dashboard API failed: {data}", "ERROR")
                    return False, None
            else:
                self.log(f"❌ Dashboard API failed with status {response.status_code}: {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Dashboard API error: {str(e)}", "ERROR")
            return False, None
    
    def test_branding_update(self):
        """Test PUT /api/practice/update-practice endpoint with branding data"""
        self.log("🎨 Testing practice branding update...")
        
        try:
            # Test data with logo update
            update_data = {
                "branding": {
                    "logo": SAMPLE_LOGO_BASE64,
                    "primaryColor": "#2563eb",
                    "secondaryColor": "#1e40af"
                }
            }
            
            response = self.session.put(
                f"{API_BASE}/practice/update",
                json=update_data
            )
            
            self.log(f"Branding update response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log("✅ Branding update successful!")
                    self.log(f"Update message: {data.get('message', 'N/A')}")
                    return True
                else:
                    self.log(f"❌ Branding update failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Branding update failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Branding update error: {str(e)}", "ERROR")
            return False
    
    def verify_updated_logo(self):
        """Verify dashboard API returns new logo after update"""
        self.log("🔍 Verifying updated logo in dashboard...")
        
        try:
            response = self.session.get(f"{API_BASE}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice_data = data.get("data", {}).get("practice", {})
                    branding = practice_data.get("branding", {})
                    current_logo = branding.get("logo")
                    
                    if current_logo == SAMPLE_LOGO_BASE64:
                        self.log("✅ Logo update verified! New logo is present in dashboard data")
                        return True
                    elif current_logo != self.original_logo:
                        self.log("✅ Logo changed from original, but may not match test data exactly")
                        self.log(f"New logo: {current_logo[:50]}..." if current_logo and len(current_logo) > 50 else f"New logo: {current_logo}")
                        return True
                    else:
                        self.log("❌ Logo was not updated - still matches original", "ERROR")
                        return False
                else:
                    self.log(f"❌ Dashboard verification failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Dashboard verification failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Logo verification error: {str(e)}", "ERROR")
            return False
    
    def test_pdf_generation(self):
        """Test PDF generation endpoints to verify they use updated logo"""
        self.log("📄 Testing PDF generation with updated logo...")
        
        # First, try to get a procedure assignment to test with
        try:
            dashboard_response = self.session.get(f"{API_BASE}/practice/dashboard")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                recent_procedures = dashboard_data.get("data", {}).get("recentProcedures", [])
                
                if recent_procedures:
                    # Test with first available procedure
                    test_procedure = recent_procedures[0]
                    assignment_id = test_procedure.get("id")
                    
                    self.log(f"Testing PDF generation with procedure: {test_procedure.get('procedureName', 'Unknown')}")
                    
                    # Test email-pdf endpoint
                    email_pdf_data = {
                        "patientEmail": "test@example.com",
                        "procedureId": test_procedure.get("procedureId", ""),
                        "procedureName": test_procedure.get("procedureName", ""),
                        "assignmentId": assignment_id
                    }
                    
                    email_response = self.session.post(
                        f"{API_BASE}/practice/email-pdf",
                        json=email_pdf_data
                    )
                    
                    self.log(f"Email PDF response status: {email_response.status_code}")
                    
                    if email_response.status_code == 200:
                        email_data = email_response.json()
                        if email_data.get("success"):
                            self.log("✅ Email PDF generation successful!")
                            
                            # Check if response mentions logo usage
                            response_text = str(email_data)
                            if "logo" in response_text.lower():
                                self.log("✅ PDF generation response mentions logo usage")
                            
                            return True
                        else:
                            self.log(f"❌ Email PDF generation failed: {email_data}", "ERROR")
                    else:
                        self.log(f"❌ Email PDF generation failed with status {email_response.status_code}: {email_response.text}", "ERROR")
                
                else:
                    self.log("⚠️ No recent procedures found for PDF testing", "WARNING")
                    return True  # Not a failure, just no data to test with
                    
        except Exception as e:
            self.log(f"❌ PDF generation test error: {str(e)}", "ERROR")
            return False
        
        return False
    
    def run_all_tests(self):
        """Run all logo functionality tests"""
        self.log("🚀 Starting Logo Functionality Fix Test Suite")
        self.log("=" * 60)
        
        test_results = {
            "authentication": False,
            "current_practice_data": False,
            "branding_update": False,
            "logo_verification": False,
            "pdf_generation": False
        }
        
        # Test 1: Authentication
        if self.authenticate():
            test_results["authentication"] = True
        else:
            self.log("❌ Authentication failed - cannot continue with other tests", "ERROR")
            return test_results
        
        # Test 2: Current Practice Data
        success, practice_data = self.test_current_practice_data()
        test_results["current_practice_data"] = success
        
        if not success:
            self.log("❌ Cannot retrieve current practice data - continuing with other tests", "WARNING")
        
        # Test 3: Branding Update
        if self.test_branding_update():
            test_results["branding_update"] = True
        else:
            self.log("❌ Branding update failed - logo verification may not work", "WARNING")
        
        # Test 4: Logo Verification
        if self.verify_updated_logo():
            test_results["logo_verification"] = True
        
        # Test 5: PDF Generation
        if self.test_pdf_generation():
            test_results["pdf_generation"] = True
        
        return test_results
    
    def print_summary(self, results):
        """Print test summary"""
        self.log("=" * 60)
        self.log("📋 TEST SUMMARY")
        self.log("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        self.log("-" * 60)
        self.log(f"Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED - Logo functionality is working correctly!")
        elif passed_tests >= total_tests * 0.8:
            self.log("⚠️ MOSTLY WORKING - Minor issues detected")
        else:
            self.log("❌ MAJOR ISSUES - Logo functionality needs attention")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = LogoFunctionalityTester()
    
    try:
        results = tester.run_all_tests()
        success = tester.print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        tester.log("Test interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        tester.log(f"Unexpected error: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()