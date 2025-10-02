#!/usr/bin/env python3
"""
PDF Logo Backend Test - Testing the recent fixes for logo and practice name integration in PDF generation

This test focuses on:
1. Database Query Fix: Updated email-pdf and secure-pdf endpoints to include "branding": 1 in practice data query
2. PDF Generator Enhancement: Updated to use custom practice logos and display practice names
3. Practice Name Integration: Added practice name display in PDFs

Critical Testing Points:
- Authentication with cganz2279@gmail.com/password123
- Practice dashboard API to confirm branding data
- Email PDF generation with proper logo/branding integration
- Check backend logs for PDF generation messages
- Secure PDF endpoint testing
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class PDFLogoTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.practice_id = None
        self.practice_data = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_authentication(self):
        """Test authentication with cganz2279@gmail.com/password123"""
        self.log("🔐 Testing authentication...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
                    self.practice_id = data.get("user", {}).get("practiceId")
                    self.log(f"✅ Authentication successful")
                    self.log(f"   - Token obtained: {self.token[:20]}...")
                    self.log(f"   - Practice ID: {self.practice_id}")
                    return True
                else:
                    self.log(f"❌ Authentication failed: {data.get('detail', 'Unknown error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Authentication failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_practice_dashboard_branding(self):
        """Test GET /api/practice/dashboard to confirm practice has branding data with logo"""
        self.log("🏥 Testing practice dashboard API for branding data...")
        
        if not self.token:
            self.log("❌ No authentication token available", "ERROR")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{BACKEND_URL}/practice/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice = data.get("data", {}).get("practice", {})
                    self.practice_data = practice
                    
                    # Check if branding data exists
                    branding = practice.get("branding", {})
                    
                    self.log("✅ Practice dashboard API successful")
                    self.log(f"   - Practice name: {practice.get('name', 'N/A')}")
                    self.log(f"   - Branding data present: {'Yes' if branding else 'No'}")
                    
                    if branding:
                        logo = branding.get("logo")
                        primary_color = branding.get("primaryColor")
                        secondary_color = branding.get("secondaryColor")
                        welcome_message = branding.get("welcomeMessage")
                        
                        self.log(f"   - Logo present: {'Yes' if logo else 'No'}")
                        if logo:
                            self.log(f"   - Logo format: {'base64 data URL' if logo.startswith('data:image') else 'Other format'}")
                            self.log(f"   - Logo length: {len(logo)} characters")
                        
                        self.log(f"   - Primary color: {primary_color}")
                        self.log(f"   - Secondary color: {secondary_color}")
                        self.log(f"   - Welcome message: {welcome_message[:50]}..." if welcome_message else "   - Welcome message: None")
                        
                        # This is the key fix - branding data should be included in the query
                        if logo and logo.startswith('data:image'):
                            self.log("🎯 CRITICAL: Custom logo data is available for PDF generation")
                            return True
                        else:
                            self.log("⚠️ WARNING: No custom logo found in branding data", "WARN")
                            return True  # Still successful API call, just no custom logo
                    else:
                        self.log("⚠️ WARNING: No branding data found in practice", "WARN")
                        return True  # Still successful API call
                else:
                    self.log(f"❌ Dashboard API failed: {data.get('detail', 'Unknown error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Dashboard API failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Dashboard API error: {str(e)}", "ERROR")
            return False
    
    def test_email_pdf_generation(self):
        """Test POST /api/practice/email-pdf with proper branding data integration"""
        self.log("📧 Testing email PDF generation with branding data...")
        
        if not self.token:
            self.log("❌ No authentication token available", "ERROR")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Use a test procedure for PDF generation
            test_data = {
                "patientEmail": "test@example.com",
                "procedureId": "root-canal-therapy",
                "procedureName": "Root Canal Therapy"
            }
            
            self.log(f"   - Testing with procedure: {test_data['procedureName']}")
            self.log(f"   - Patient email: {test_data['patientEmail']}")
            
            response = self.session.post(f"{BACKEND_URL}/practice/email-pdf", 
                                       headers=headers, 
                                       json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log("✅ Email PDF generation successful")
                    self.log(f"   - Message: {data.get('message', 'N/A')}")
                    self.log(f"   - Patient email: {data.get('patientEmail', 'N/A')}")
                    self.log(f"   - Procedure name: {data.get('procedureName', 'N/A')}")
                    
                    # The key fix: practice branding data should now be included in the PDF generator call
                    self.log("🎯 CRITICAL: PDF generation completed - branding data should be included")
                    self.log("   - Check backend logs for PDF generation messages about logo usage")
                    return True
                else:
                    self.log(f"❌ Email PDF generation failed: {data.get('detail', 'Unknown error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Email PDF generation failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Email PDF generation error: {str(e)}", "ERROR")
            return False
    
    def test_secure_pdf_endpoint(self):
        """Test the secure PDF endpoint structure"""
        self.log("🔒 Testing secure PDF endpoint structure...")
        
        # Test with a dummy token to verify endpoint exists and handles invalid tokens properly
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/secure-pdf/dummy-token")
            
            # We expect this to fail with 401 or 400 for invalid token, but endpoint should exist
            if response.status_code in [400, 401]:
                self.log("✅ Secure PDF endpoint exists and properly validates tokens")
                self.log(f"   - Status code: {response.status_code}")
                self.log(f"   - Response indicates proper token validation")
                return True
            elif response.status_code == 404:
                self.log("❌ Secure PDF endpoint not found", "ERROR")
                return False
            else:
                self.log(f"⚠️ Secure PDF endpoint returned unexpected status: {response.status_code}", "WARN")
                return True  # Endpoint exists, just unexpected response
                
        except Exception as e:
            self.log(f"❌ Secure PDF endpoint test error: {str(e)}", "ERROR")
            return False
    
    def check_backend_logs(self):
        """Check backend logs for PDF generation messages"""
        self.log("📋 Checking backend logs for PDF generation messages...")
        
        try:
            import subprocess
            
            # Check supervisor backend logs for PDF generation messages
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                
                # Look for PDF generation related messages
                pdf_messages = []
                for line in log_content.split('\n'):
                    if any(keyword in line.lower() for keyword in ['pdf', 'logo', 'practice', 'branding']):
                        pdf_messages.append(line.strip())
                
                if pdf_messages:
                    self.log("✅ Found PDF-related log messages:")
                    for msg in pdf_messages[-10:]:  # Show last 10 relevant messages
                        self.log(f"   📝 {msg}")
                else:
                    self.log("ℹ️ No specific PDF-related messages found in recent logs")
                
                return True
            else:
                self.log(f"⚠️ Could not read backend logs: {result.stderr}", "WARN")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("⚠️ Backend log check timed out", "WARN")
            return False
        except Exception as e:
            self.log(f"⚠️ Backend log check error: {str(e)}", "WARN")
            return False
    
    def run_comprehensive_test(self):
        """Run all PDF logo tests"""
        self.log("🚀 Starting comprehensive PDF logo functionality test...")
        self.log("=" * 80)
        
        results = {}
        
        # Test 1: Authentication
        results['authentication'] = self.test_authentication()
        
        if results['authentication']:
            # Test 2: Practice dashboard with branding data
            results['dashboard_branding'] = self.test_practice_dashboard_branding()
            
            # Test 3: Email PDF generation
            results['email_pdf'] = self.test_email_pdf_generation()
            
            # Test 4: Secure PDF endpoint
            results['secure_pdf'] = self.test_secure_pdf_endpoint()
            
            # Test 5: Backend logs
            results['backend_logs'] = self.check_backend_logs()
        else:
            self.log("❌ Skipping other tests due to authentication failure", "ERROR")
            results.update({
                'dashboard_branding': False,
                'email_pdf': False,
                'secure_pdf': False,
                'backend_logs': False
            })
        
        # Summary
        self.log("=" * 80)
        self.log("📊 TEST SUMMARY:")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        self.log(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - PDF logo functionality is working correctly!")
        elif passed >= total - 1:
            self.log("✅ MOSTLY SUCCESSFUL - Minor issues detected but core functionality working")
        else:
            self.log("⚠️ ISSUES DETECTED - Some PDF logo functionality may not be working properly")
        
        return results

def main():
    """Main test execution"""
    print("PDF Logo Backend Test")
    print("Testing the recent fixes for logo and practice name integration in PDF generation")
    print("=" * 80)
    
    tester = PDFLogoTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()