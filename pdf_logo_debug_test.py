#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://dental-admin-3.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class PDFLogoDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with test credentials...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.auth_token = data["token"]
                self.practice_id = data["user"]["practiceId"]
                self.user_id = data["user"]["id"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   Practice ID: {self.practice_id}")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def check_current_practice_data(self):
        """Check current practice branding data"""
        print("\n📊 Checking Current Practice Data...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                practice = data["data"]["practice"]
                branding = practice.get("branding", {})
                
                print(f"✅ Practice Dashboard Data Retrieved")
                print(f"   Practice Name: {practice.get('name', 'N/A')}")
                print(f"   Practice ID: {practice.get('id', 'N/A')}")
                
                # Check logo data
                logo = branding.get("logo")
                if logo:
                    print(f"   Logo Data Present: YES")
                    print(f"   Logo Data Length: {len(logo)} characters")
                    print(f"   Logo Data Type: {'Data URL' if logo.startswith('data:') else 'Unknown'}")
                    
                    # Check if it's the 1x1 pixel placeholder
                    placeholder_logo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
                    if logo == placeholder_logo:
                        print("   ⚠️  LOGO IS 1x1 PIXEL PLACEHOLDER - This is the corrupted data!")
                    else:
                        print("   ✅ Logo appears to be custom data (not placeholder)")
                        # Show first 100 characters for debugging
                        print(f"   Logo Preview: {logo[:100]}...")
                else:
                    print("   Logo Data Present: NO")
                
                # Check other branding data
                print(f"   Primary Color: {branding.get('primaryColor', 'N/A')}")
                print(f"   Secondary Color: {branding.get('secondaryColor', 'N/A')}")
                print(f"   Welcome Message: {branding.get('welcomeMessage', 'N/A')}")
                
                return practice
            else:
                print(f"❌ Failed to get practice data: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Failed to get practice data with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    def test_pdf_generation_debug(self):
        """Test PDF generation and debug what data is being passed"""
        print("\n🔍 Testing PDF Generation with Debug Info...")
        
        # Use a common procedure for testing
        test_data = {
            "patientEmail": "test.patient@gmail.com",
            "procedureId": "root-canal-therapy",
            "procedureName": "Root Canal Therapy"
        }
        
        print(f"   Testing with procedure: {test_data['procedureName']}")
        print(f"   Patient email: {test_data['patientEmail']}")
        
        response = self.session.post(f"{BASE_URL}/practice/email-pdf", json=test_data)
        
        print(f"   PDF Generation Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ PDF Generation Request Successful")
                print(f"   Response: {data.get('message', 'No message')}")
                return True
            else:
                print(f"   ❌ PDF Generation Failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ PDF Generation Failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error Details: {error_data}")
            except:
                print(f"   Raw Response: {response.text}")
            return False
    
    def test_secure_pdf_endpoint(self):
        """Test secure PDF endpoint with invalid token to check error handling"""
        print("\n🔒 Testing Secure PDF Endpoint...")
        
        # Test with invalid token to see if endpoint is working
        invalid_token = "invalid-test-token-12345"
        
        response = self.session.get(f"{BASE_URL}/practice/secure-pdf/{invalid_token}")
        
        print(f"   Secure PDF Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Secure PDF endpoint working (correctly rejected invalid token)")
            return True
        elif response.status_code == 500:
            print("   ⚠️  Secure PDF endpoint has internal error")
            try:
                error_data = response.json()
                print(f"   Error Details: {error_data}")
            except:
                print(f"   Raw Response: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected response from secure PDF endpoint")
            try:
                error_data = response.json()
                print(f"   Response Details: {error_data}")
            except:
                print(f"   Raw Response: {response.text}")
            return False
    
    def analyze_logo_issue(self, practice_data):
        """Analyze the logo issue based on practice data"""
        print("\n🔬 Logo Issue Analysis...")
        
        if not practice_data:
            print("   ❌ No practice data available for analysis")
            return
        
        branding = practice_data.get("branding", {})
        logo = branding.get("logo")
        
        if not logo:
            print("   ❌ ISSUE: No logo data in practice branding")
            print("   📝 RECOMMENDATION: User needs to upload a logo through practice settings")
            return
        
        # Check if it's the corrupted placeholder
        placeholder_logo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        if logo == placeholder_logo:
            print("   ❌ CRITICAL ISSUE CONFIRMED: Logo is 1x1 pixel transparent PNG placeholder")
            print("   📊 Logo Analysis:")
            print("      - Type: 1x1 pixel transparent PNG")
            print("      - Size: 118 characters (base64)")
            print("      - Status: CORRUPTED/PLACEHOLDER")
            print("   🔧 ROOT CAUSE: Practice branding contains placeholder instead of actual logo")
            print("   📝 SOLUTION: User must upload new logo through practice settings to replace corrupted data")
            print("   ⚠️  IMPACT: Both dashboard and PDFs will show corrupted logo until replaced")
        else:
            print("   ✅ Logo data appears to be valid (not the known placeholder)")
            print(f"   📊 Logo Analysis:")
            print(f"      - Length: {len(logo)} characters")
            print(f"      - Format: {'Data URL' if logo.startswith('data:') else 'Unknown'}")
            if logo.startswith('data:'):
                # Extract MIME type
                try:
                    mime_part = logo.split(',')[0]
                    print(f"      - MIME Type: {mime_part}")
                except:
                    print("      - MIME Type: Could not parse")
    
    def run_debug_tests(self):
        """Run all debug tests for PDF logo issue"""
        print("🚀 Starting PDF Logo Debug Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Check current practice data
        practice_data = self.check_current_practice_data()
        
        # Analyze logo issue
        self.analyze_logo_issue(practice_data)
        
        # Test PDF generation
        pdf_success = self.test_pdf_generation_debug()
        
        # Test secure PDF endpoint
        secure_pdf_success = self.test_secure_pdf_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DEBUG TEST SUMMARY")
        print("=" * 60)
        
        print(f"Authentication: ✅ PASSED")
        print(f"Practice Data Retrieval: {'✅ PASSED' if practice_data else '❌ FAILED'}")
        print(f"PDF Generation Test: {'✅ PASSED' if pdf_success else '❌ FAILED'}")
        print(f"Secure PDF Endpoint: {'✅ PASSED' if secure_pdf_success else '❌ FAILED'}")
        
        # Key findings
        if practice_data:
            branding = practice_data.get("branding", {})
            logo = branding.get("logo")
            placeholder_logo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            
            print("\n🔍 KEY FINDINGS:")
            if logo == placeholder_logo:
                print("   ❌ CONFIRMED: Logo is corrupted 1x1 pixel placeholder")
                print("   📝 USER ACTION REQUIRED: Upload new logo through practice settings")
                print("   🎯 ISSUE STATUS: User report is ACCURATE - logo needs to be replaced")
            elif logo:
                print("   ✅ Logo data appears valid - may be a different issue")
                print("   🔍 FURTHER INVESTIGATION: Check PDF generation logs")
            else:
                print("   ❌ No logo data found in practice branding")
                print("   📝 USER ACTION REQUIRED: Upload logo through practice settings")
        
        return True

def main():
    """Main function to run the debug tests"""
    tester = PDFLogoDebugTester()
    success = tester.run_debug_tests()
    
    if success:
        print("\n✅ PDF Logo Debug Tests completed!")
        sys.exit(0)
    else:
        print("\n❌ PDF Logo Debug Tests had issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()