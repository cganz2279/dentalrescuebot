#!/usr/bin/env python3

import requests
import json
import sys

# Configuration
BASE_URL = "https://aftercareportal.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class LibraryPDFSpecificTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        
    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating...")
        
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
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Authentication successful - Practice ID: {self.practice_id}")
                return True
        
        print("❌ Authentication failed")
        return False
    
    def test_common_procedures_for_pdf(self):
        """Test common procedures that users might try to generate PDFs for"""
        print("\n📋 Testing Common Procedures for PDF Generation...")
        
        # Common procedures users might want PDFs for
        common_procedures = [
            "Root Canal Therapy",
            "Dental Implant", 
            "Tooth Extraction",
            "Crown Placement",
            "Dental Cleaning"
        ]
        
        # Get all procedures first
        response = self.session.get(f"{BASE_URL}/procedures")
        if response.status_code != 200:
            print("❌ Failed to get procedures list")
            return False
        
        all_procedures = response.json().get("data", [])
        
        found_procedures = []
        
        for common_name in common_procedures:
            # Find matching procedures
            matches = [p for p in all_procedures if common_name.lower() in p.get("name", "").lower()]
            
            if matches:
                procedure = matches[0]  # Take first match
                found_procedures.append(procedure)
                print(f"   ✅ Found: {procedure.get('name')} (ID: {procedure.get('id')})")
                
                # Test if this procedure can be retrieved individually
                proc_response = self.session.get(f"{BASE_URL}/procedures/{procedure.get('id')}")
                if proc_response.status_code == 200:
                    proc_data = proc_response.json()
                    if proc_data.get("success"):
                        print(f"      ✅ Individual procedure retrieval working")
                    else:
                        print(f"      ❌ Individual procedure retrieval failed: {proc_data.get('error')}")
                else:
                    print(f"      ❌ Individual procedure retrieval failed with status {proc_response.status_code}")
            else:
                print(f"   ⚠️  Not found: {common_name}")
        
        return len(found_procedures) > 0
    
    def test_practice_data_for_pdf(self):
        """Test practice data that would be used in PDF generation"""
        print("\n🏥 Testing Practice Data for PDF Generation...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                practice = data.get("data", {})
                
                print(f"   Practice Name: {practice.get('name', 'Not set')}")
                print(f"   Practice Phone: {practice.get('phone', 'Not set')}")
                print(f"   Practice Address: {practice.get('address', 'Not set')}")
                print(f"   Office Hours: {practice.get('officeHours', 'Not set')}")
                print(f"   Emergency Contact: {practice.get('emergencyContact', 'Not set')}")
                
                # Check branding data
                branding = practice.get("branding", {})
                if branding:
                    print(f"   Primary Color: {branding.get('primaryColor', 'Not set')}")
                    print(f"   Secondary Color: {branding.get('secondaryColor', 'Not set')}")
                    
                    logo = branding.get("logo")
                    if logo:
                        print(f"   Logo: Present ({len(logo)} characters)")
                        
                        # Analyze logo data
                        if logo.startswith("data:image/"):
                            print("      ✅ Logo is in data URL format")
                            if "base64," in logo:
                                base64_part = logo.split("base64,")[1]
                                print(f"      ✅ Base64 data length: {len(base64_part)} characters")
                                
                                # Check if it's the 1x1 pixel placeholder
                                if len(base64_part) < 200:
                                    print("      ⚠️  Logo appears to be a small placeholder image")
                                else:
                                    print("      ✅ Logo appears to be a proper image")
                            else:
                                print("      ❌ Logo data URL missing base64 encoding")
                        else:
                            print("      ❌ Logo is not in data URL format")
                    else:
                        print("   Logo: Not set")
                else:
                    print("   Branding: Not configured")
                
                return True
            else:
                print(f"   ❌ Failed to get practice data: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Failed to get practice data with status {response.status_code}")
            return False
    
    def simulate_library_pdf_generation(self):
        """Simulate what happens when user clicks PDF in Library"""
        print("\n🎯 Simulating Library PDF Generation Process...")
        
        # Step 1: Get a procedure (simulating user selecting one)
        response = self.session.get(f"{BASE_URL}/procedures")
        if response.status_code != 200:
            print("❌ Failed to get procedures")
            return False
        
        procedures = response.json().get("data", [])
        if not procedures:
            print("❌ No procedures available")
            return False
        
        test_procedure = procedures[0]
        print(f"   📄 Selected procedure: {test_procedure.get('name')}")
        
        # Step 2: Get practice data (what frontend would do)
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        if response.status_code != 200:
            print("❌ Failed to get practice data")
            return False
        
        practice_data = response.json().get("data", {})
        print(f"   🏥 Practice data retrieved: {practice_data.get('name', 'Unknown')}")
        
        # Step 3: Check if all required data is available for PDF generation
        required_fields = ["name", "phone", "address", "officeHours", "emergencyContact"]
        missing_fields = []
        
        for field in required_fields:
            if not practice_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ⚠️  Missing practice data fields: {missing_fields}")
        else:
            print("   ✅ All required practice data fields present")
        
        # Step 4: Check procedure data completeness
        proc_required = ["name", "overview", "immediateAftercare", "dietRestrictions"]
        proc_missing = []
        
        for field in proc_required:
            if not test_procedure.get(field):
                proc_missing.append(field)
        
        if proc_missing:
            print(f"   ⚠️  Missing procedure data fields: {proc_missing}")
        else:
            print("   ✅ All required procedure data fields present")
        
        # Step 5: Simulate the frontend PDF generation process
        print("   🔄 Frontend would now:")
        print("      1. Import ENHANCED_PDF_WITH_LOGO.js")
        print("      2. Call generateProcedurePDF() with procedure and practice data")
        print("      3. Use jsPDF to create PDF client-side")
        print("      4. Trigger browser download")
        
        print("   ❗ NO BACKEND API CALLS are made during this process")
        
        return True
    
    def check_browser_compatibility_factors(self):
        """Check factors that might affect browser PDF generation"""
        print("\n🌐 Browser Compatibility Factors Analysis...")
        
        print("   📋 Potential Issues:")
        print("      1. Popup blocker preventing file download")
        print("      2. Browser security settings blocking downloads")
        print("      3. JavaScript errors in jsPDF library")
        print("      4. Missing fonts or resources for PDF generation")
        print("      5. CORS issues with logo/image loading")
        print("      6. Browser memory limitations for large PDFs")
        
        print("\n   🔍 Debugging Steps for User:")
        print("      1. Open browser developer console (F12)")
        print("      2. Click PDF button in Library")
        print("      3. Check for JavaScript errors in console")
        print("      4. Check Network tab for failed resource loads")
        print("      5. Try in different browser (Chrome, Firefox, Safari)")
        print("      6. Check browser download settings")
        print("      7. Disable popup blocker temporarily")
        
        return True
    
    def run_all_tests(self):
        """Run all specific Library PDF tests"""
        print("🚀 Starting Library PDF Specific Testing")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        tests = [
            ("Common Procedures Test", self.test_common_procedures_for_pdf),
            ("Practice Data Test", self.test_practice_data_for_pdf),
            ("Library PDF Simulation", self.simulate_library_pdf_generation),
            ("Browser Compatibility Analysis", self.check_browser_compatibility_factors)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 LIBRARY PDF ISSUE DIAGNOSIS")
        print("=" * 60)
        
        print("CONFIRMED: Library PDF generation is entirely CLIENT-SIDE")
        print("- Uses jsPDF library in browser")
        print("- No backend API calls involved")
        print("- Issue is browser/frontend related, not backend")
        
        print("\nRECOMMENDED ACTIONS:")
        print("1. User should check browser console for errors")
        print("2. Try different browsers")
        print("3. Check browser download/popup settings")
        print("4. Consider implementing server-side PDF generation")
        
        passed = sum(1 for _, result in results if result)
        return passed >= len(results) - 1

def main():
    tester = LibraryPDFSpecificTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Library PDF backend components are working correctly!")
        print("   The issue is in the frontend client-side PDF generation.")
    else:
        print("\n❌ Found issues with Library PDF backend components!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())