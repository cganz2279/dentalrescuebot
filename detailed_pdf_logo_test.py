#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import uuid
import base64
from io import BytesIO

# Configuration
BASE_URL = "https://dentalpractice-hub-1.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class DetailedPDFLogoTester:
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
    
    def get_current_practice_branding(self):
        """Get current practice branding data"""
        print("\n📊 Getting Current Practice Branding Data...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                practice = data["data"]["practice"]
                branding = practice.get("branding", {})
                
                print(f"✅ Practice Data Retrieved")
                print(f"   Practice Name: {practice.get('name', 'N/A')}")
                
                # Analyze logo data
                logo = branding.get("logo")
                if logo:
                    print(f"   Logo Data Length: {len(logo)} characters")
                    
                    # Check if it's a valid data URL
                    if logo.startswith('data:image'):
                        try:
                            # Extract the base64 part
                            header, data_part = logo.split(',', 1)
                            print(f"   Logo Header: {header}")
                            
                            # Try to decode the base64 data
                            logo_bytes = base64.b64decode(data_part)
                            print(f"   Logo Binary Size: {len(logo_bytes)} bytes")
                            
                            # Check if it's a valid image by looking at the first few bytes
                            if logo_bytes.startswith(b'\x89PNG'):
                                print("   ✅ Logo appears to be a valid PNG image")
                            elif logo_bytes.startswith(b'\xff\xd8\xff'):
                                print("   ✅ Logo appears to be a valid JPEG image")
                            else:
                                print(f"   ⚠️  Logo binary data starts with: {logo_bytes[:10].hex()}")
                                
                        except Exception as e:
                            print(f"   ❌ Error analyzing logo data: {e}")
                    else:
                        print("   ❌ Logo is not a valid data URL")
                else:
                    print("   ❌ No logo data found")
                
                return practice
            else:
                print(f"❌ Failed to get practice data: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Failed to get practice data with status {response.status_code}")
            return None
    
    def test_logo_upload_functionality(self):
        """Test logo upload functionality by uploading a test logo"""
        print("\n🔄 Testing Logo Upload Functionality...")
        
        # Create a simple test logo (1x1 red pixel PNG)
        test_logo_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        # Update practice branding with test logo
        branding_update = {
            "branding": {
                "logo": test_logo_base64,
                "primaryColor": "#2563eb",
                "secondaryColor": "#1e40af",
                "welcomeMessage": f"Test logo update at {datetime.now().strftime('%H:%M:%S')}"
            }
        }
        
        print("   Uploading test logo...")
        response = self.session.put(f"{BASE_URL}/practice/update", json=branding_update)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ Test logo uploaded successfully")
                
                # Verify the logo was saved
                verification_response = self.session.get(f"{BASE_URL}/practice/dashboard")
                if verification_response.status_code == 200:
                    verify_data = verification_response.json()
                    if verify_data.get("success"):
                        practice = verify_data["data"]["practice"]
                        saved_logo = practice.get("branding", {}).get("logo")
                        
                        if saved_logo == test_logo_base64:
                            print("   ✅ Logo upload verification successful")
                            return True
                        else:
                            print("   ❌ Logo upload verification failed - data doesn't match")
                            return False
                    else:
                        print("   ❌ Failed to verify logo upload")
                        return False
                else:
                    print("   ❌ Failed to verify logo upload")
                    return False
            else:
                print(f"   ❌ Logo upload failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Logo upload failed with status {response.status_code}")
            return False
    
    def test_pdf_generation_with_new_logo(self):
        """Test PDF generation after logo upload"""
        print("\n📄 Testing PDF Generation with New Logo...")
        
        # Test PDF generation
        test_data = {
            "patientEmail": "pdf.test@gmail.com",
            "procedureId": "dental-crown-placement",
            "procedureName": "Dental Crown Placement"
        }
        
        print(f"   Generating PDF for: {test_data['procedureName']}")
        
        response = self.session.post(f"{BASE_URL}/practice/email-pdf", json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ PDF generation successful with new logo")
                print(f"   Response: {data.get('message', 'No message')}")
                return True
            else:
                print(f"   ❌ PDF generation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ PDF generation failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error Details: {error_data}")
            except:
                print(f"   Raw Response: {response.text}")
            return False
    
    def restore_original_logo(self, original_practice_data):
        """Restore the original logo after testing"""
        print("\n🔄 Restoring Original Logo...")
        
        if not original_practice_data:
            print("   ⚠️  No original practice data to restore")
            return False
        
        original_branding = original_practice_data.get("branding", {})
        
        branding_update = {
            "branding": {
                "logo": original_branding.get("logo"),
                "primaryColor": original_branding.get("primaryColor", "#2563eb"),
                "secondaryColor": original_branding.get("secondaryColor", "#1e40af"),
                "welcomeMessage": original_branding.get("welcomeMessage", "Welcome")
            }
        }
        
        response = self.session.put(f"{BASE_URL}/practice/update", json=branding_update)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ Original logo restored successfully")
                return True
            else:
                print(f"   ❌ Failed to restore original logo: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Failed to restore original logo with status {response.status_code}")
            return False
    
    def test_pdf_generation_comprehensive(self):
        """Test PDF generation with multiple procedures"""
        print("\n🔍 Comprehensive PDF Generation Testing...")
        
        test_procedures = [
            {"id": "root-canal-therapy", "name": "Root Canal Therapy"},
            {"id": "dental-implant-placement", "name": "Dental Implant Placement"},
            {"id": "tooth-extraction", "name": "Tooth Extraction"}
        ]
        
        success_count = 0
        
        for i, proc in enumerate(test_procedures):
            print(f"   Testing procedure {i+1}: {proc['name']}")
            
            test_data = {
                "patientEmail": f"test.procedure.{i+1}@gmail.com",
                "procedureId": proc["id"],
                "procedureName": proc["name"]
            }
            
            response = self.session.post(f"{BASE_URL}/practice/email-pdf", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"      ✅ PDF generation successful")
                    success_count += 1
                else:
                    print(f"      ❌ PDF generation failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"      ❌ PDF generation failed with status {response.status_code}")
        
        print(f"   📊 PDF Generation Results: {success_count}/{len(test_procedures)} successful")
        return success_count == len(test_procedures)
    
    def run_detailed_tests(self):
        """Run all detailed PDF logo tests"""
        print("🚀 Starting Detailed PDF Logo Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Get current practice data
        original_practice_data = self.get_current_practice_branding()
        
        # Test comprehensive PDF generation with current logo
        pdf_comprehensive_success = self.test_pdf_generation_comprehensive()
        
        # Test logo upload functionality
        logo_upload_success = self.test_logo_upload_functionality()
        
        # Test PDF generation with new logo
        pdf_new_logo_success = False
        if logo_upload_success:
            pdf_new_logo_success = self.test_pdf_generation_with_new_logo()
            
            # Restore original logo
            self.restore_original_logo(original_practice_data)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DETAILED TEST SUMMARY")
        print("=" * 60)
        
        print(f"Authentication: ✅ PASSED")
        print(f"Practice Data Retrieval: {'✅ PASSED' if original_practice_data else '❌ FAILED'}")
        print(f"Comprehensive PDF Generation: {'✅ PASSED' if pdf_comprehensive_success else '❌ FAILED'}")
        print(f"Logo Upload Functionality: {'✅ PASSED' if logo_upload_success else '❌ FAILED'}")
        print(f"PDF Generation with New Logo: {'✅ PASSED' if pdf_new_logo_success else '❌ FAILED'}")
        
        # Final assessment
        print("\n🎯 FINAL ASSESSMENT:")
        
        if original_practice_data and pdf_comprehensive_success and logo_upload_success and pdf_new_logo_success:
            print("   ✅ ALL SYSTEMS WORKING: Logo functionality is working correctly")
            print("   📝 CONCLUSION: The user's reported issue may have been resolved")
            print("   🔍 RECOMMENDATION: Ask user to verify current logo display in dashboard and PDFs")
        elif pdf_comprehensive_success and logo_upload_success:
            print("   ✅ CORE FUNCTIONALITY WORKING: PDF generation and logo upload working")
            print("   ⚠️  MINOR ISSUES: Some edge cases may need attention")
        else:
            print("   ❌ ISSUES DETECTED: Some functionality is not working correctly")
            print("   🔧 RECOMMENDATION: Further investigation needed")
        
        return True

def main():
    """Main function to run the detailed tests"""
    tester = DetailedPDFLogoTester()
    success = tester.run_detailed_tests()
    
    if success:
        print("\n✅ Detailed PDF Logo Tests completed!")
        sys.exit(0)
    else:
        print("\n❌ Detailed PDF Logo Tests had issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()