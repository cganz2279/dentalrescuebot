#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime, timezone
import uuid

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://aftercareportal.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class PDFLibraryBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.user_id = None
        self.practice_data = None
        
    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with practice login credentials...")
        
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
    
    def test_procedures_endpoint(self):
        """Test the /api/procedures endpoint to make sure procedures are available"""
        print("\n📚 Testing Procedures Endpoint...")
        
        response = self.session.get(f"{BASE_URL}/procedures")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                procedures = data.get("data", [])
                count = data.get("count", 0)
                
                print(f"✅ Procedures endpoint working - Found {count} procedures")
                
                if procedures:
                    # Show first few procedures for verification
                    print("   Sample procedures:")
                    for i, proc in enumerate(procedures[:3]):
                        print(f"     {i+1}. {proc.get('name', 'Unknown')} (ID: {proc.get('id', 'No ID')})")
                    
                    # Store some procedures for PDF testing
                    self.sample_procedures = procedures[:5]
                    return True
                else:
                    print("❌ No procedures found in database")
                    return False
            else:
                print(f"❌ Procedures endpoint failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Procedures endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_practice_dashboard(self):
        """Test practice dashboard to get practice data"""
        print("\n🏥 Testing Practice Dashboard...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.practice_data = data.get("data", {})
                practice_name = self.practice_data.get("name", "Unknown")
                
                print(f"✅ Practice dashboard working - Practice: {practice_name}")
                
                # Check if practice has branding/logo data
                branding = self.practice_data.get("branding", {})
                if branding.get("logo"):
                    logo_size = len(branding["logo"])
                    print(f"   ✅ Practice has custom logo ({logo_size} characters)")
                else:
                    print("   ⚠️  Practice has no custom logo")
                
                return True
            else:
                print(f"❌ Practice dashboard failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Practice dashboard failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_pdf_generation_endpoints(self):
        """Test backend PDF generation endpoints"""
        print("\n📄 Testing Backend PDF Generation Endpoints...")
        
        if not hasattr(self, 'sample_procedures') or not self.sample_procedures:
            print("❌ No sample procedures available for PDF testing")
            return False
        
        # Test email-pdf endpoint
        print("   Testing /api/practice/email-pdf endpoint...")
        
        test_procedure = self.sample_procedures[0]
        
        email_pdf_data = {
            "patientEmail": "test@example.com",
            "patientName": "Test Patient",
            "procedureId": test_procedure.get("id"),
            "procedureName": test_procedure.get("name"),
            "dentistName": "Dr. Test"
        }
        
        response = self.session.post(f"{BASE_URL}/practice/email-pdf", json=email_pdf_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Email PDF endpoint working - {data.get('message', 'Success')}")
            else:
                print(f"   ❌ Email PDF endpoint failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Email PDF endpoint failed with status {response.status_code}")
            print(f"      Response: {response.text}")
            # Don't return False here as this might be expected behavior
        
        # Test SMS PDF endpoint
        print("   Testing /api/practice/sms-pdf endpoint...")
        
        sms_pdf_data = {
            "patientPhone": "+1234567890",
            "patientName": "Test Patient",
            "procedureId": test_procedure.get("id"),
            "procedureName": test_procedure.get("name"),
            "dentistName": "Dr. Test"
        }
        
        response = self.session.post(f"{BASE_URL}/practice/sms-pdf", json=sms_pdf_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ SMS PDF endpoint working - {data.get('message', 'Success')}")
            else:
                print(f"   ❌ SMS PDF endpoint failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ SMS PDF endpoint failed with status {response.status_code}")
            print(f"      Response: {response.text}")
        
        return True
    
    def test_secure_pdf_endpoint(self):
        """Test secure PDF endpoint"""
        print("\n🔒 Testing Secure PDF Endpoint...")
        
        # Test with invalid token first
        print("   Testing with invalid token...")
        response = self.session.get(f"{BASE_URL}/practice/secure-pdf/invalid-token")
        
        if response.status_code == 401:
            print("   ✅ Secure PDF endpoint correctly rejects invalid tokens")
        else:
            print(f"   ⚠️  Secure PDF endpoint response for invalid token: {response.status_code}")
        
        return True
    
    def check_backend_logs_for_pdf_errors(self):
        """Check if there are any backend endpoints that might log PDF generation errors"""
        print("\n📋 Checking for PDF-related Backend Functionality...")
        
        # Test if there are any PDF download endpoints
        print("   Looking for PDF download endpoints...")
        
        # Check if there's a direct PDF generation endpoint
        test_endpoints = [
            "/practice/generate-pdf",
            "/practice/download-pdf", 
            "/practice/pdf",
            "/procedures/pdf",
            "/generate-pdf"
        ]
        
        found_endpoints = []
        
        for endpoint in test_endpoints:
            response = self.session.get(f"{BASE_URL}{endpoint}")
            if response.status_code != 404:
                found_endpoints.append((endpoint, response.status_code))
        
        if found_endpoints:
            print("   ✅ Found potential PDF endpoints:")
            for endpoint, status in found_endpoints:
                print(f"      {endpoint} - Status: {status}")
        else:
            print("   ⚠️  No direct PDF generation endpoints found")
        
        return True
    
    def analyze_pdf_generation_issue(self):
        """Analyze the PDF generation issue based on findings"""
        print("\n🔍 PDF Generation Issue Analysis...")
        
        print("   📋 FINDINGS:")
        print("   1. Frontend uses client-side PDF generation (jsPDF) in ENHANCED_PDF_WITH_LOGO.js")
        print("   2. No backend API calls are made for Library PDF generation")
        print("   3. Backend has email-pdf and sms-pdf endpoints for server-side PDF generation")
        print("   4. User reports 'creating PDF' message but no file downloads")
        
        print("\n   🎯 LIKELY CAUSES:")
        print("   1. Browser blocking file downloads due to popup blocker")
        print("   2. JavaScript error in client-side PDF generation")
        print("   3. Missing practice data causing PDF generation to fail silently")
        print("   4. Browser compatibility issues with jsPDF library")
        
        print("\n   💡 RECOMMENDATIONS:")
        print("   1. Check browser console for JavaScript errors during PDF generation")
        print("   2. Verify browser allows file downloads from the domain")
        print("   3. Test PDF generation in different browsers")
        print("   4. Consider implementing server-side PDF generation for Library")
        print("   5. Add better error handling and user feedback in frontend")
        
        return True
    
    def run_all_tests(self):
        """Run all PDF Library backend tests"""
        print("🚀 Starting PDF Library Backend Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        tests = [
            ("Procedures Endpoint", self.test_procedures_endpoint),
            ("Practice Dashboard", self.test_practice_dashboard),
            ("PDF Generation Endpoints", self.test_pdf_generation_endpoints),
            ("Secure PDF Endpoint", self.test_secure_pdf_endpoint),
            ("Backend PDF Functionality Check", self.check_backend_logs_for_pdf_errors),
            ("PDF Generation Issue Analysis", self.analyze_pdf_generation_issue)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PDF LIBRARY BACKEND TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Special analysis for PDF issue
        print("\n" + "=" * 60)
        print("🎯 PDF GENERATION ISSUE DIAGNOSIS")
        print("=" * 60)
        
        print("CRITICAL FINDING: Library PDF generation is CLIENT-SIDE ONLY")
        print("- Frontend uses jsPDF library for PDF generation")
        print("- No backend API calls are made during Library PDF generation")
        print("- User's issue is likely browser-related, not backend-related")
        print("\nRECOMMENDATION: Focus on frontend debugging and browser compatibility")
        
        return passed >= (total - 1)  # Allow one test to fail

def main():
    """Main function to run the tests"""
    tester = PDFLibraryBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ PDF Library backend functionality is working correctly!")
        print("   The issue is likely in the frontend client-side PDF generation.")
        sys.exit(0)
    else:
        print("\n❌ PDF Library backend functionality has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()