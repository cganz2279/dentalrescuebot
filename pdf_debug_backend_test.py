#!/usr/bin/env python3
"""
PDF Logo Debug Testing Script
Tests PDF generation with enhanced debugging to identify logo issues
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class PDFLogoDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        
    def authenticate(self):
        """Authenticate with the test credentials"""
        print("🔐 Authenticating with test credentials...")
        
        auth_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=auth_data)
            print(f"Auth response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Auth response data: {data}")
                if data.get("success"):
                    # Handle different response structures
                    if "data" in data:
                        self.auth_token = data["data"]["token"]
                        self.practice_id = data["data"]["user"]["practiceId"]
                    else:
                        self.auth_token = data.get("token")
                        self.practice_id = data.get("user", {}).get("practiceId")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    
                    print(f"✅ Authentication successful")
                    print(f"   Practice ID: {self.practice_id}")
                    return True
                else:
                    print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Authentication failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_practice_branding(self):
        """Get current practice branding data to inspect logo"""
        print("\n🏥 Getting current practice branding data...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/dashboard")
            print(f"Dashboard response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice = data["data"]["practice"]
                    branding = practice.get("branding", {})
                    logo = branding.get("logo", "")
                    
                    print(f"✅ Practice branding retrieved")
                    print(f"   Practice Name: {practice.get('name', 'N/A')}")
                    print(f"   Primary Color: {branding.get('primaryColor', 'N/A')}")
                    print(f"   Secondary Color: {branding.get('secondaryColor', 'N/A')}")
                    
                    if logo:
                        logo_size = len(logo)
                        print(f"   Logo Data Size: {logo_size} characters")
                        
                        # Analyze logo data
                        if logo.startswith('data:image'):
                            # Extract base64 part
                            try:
                                import base64
                                logo_data = logo.split(',')[1]
                                logo_bytes = base64.b64decode(logo_data)
                                print(f"   Logo Binary Size: {len(logo_bytes)} bytes")
                                
                                if len(logo_bytes) < 100:
                                    print("   ⚠️ Logo appears to be corrupted (too small)")
                                    print(f"   Logo preview: {logo[:100]}...")
                                else:
                                    print("   ✅ Logo appears to be valid")
                                    
                            except Exception as e:
                                print(f"   ❌ Error analyzing logo data: {e}")
                        else:
                            print("   ⚠️ Logo not in data:image format")
                            print(f"   Logo preview: {logo[:100]}...")
                    else:
                        print("   ❌ No logo data found")
                    
                    return practice
                else:
                    print(f"❌ Failed to get practice data: {data.get('error', 'Unknown error')}")
                    return None
            else:
                print(f"❌ Failed to get practice data with status {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting practice branding: {e}")
            return None
    
    def test_pdf_generation(self):
        """Test PDF generation with debug output monitoring"""
        print("\n📄 Testing PDF generation with debug monitoring...")
        
        # Test with a common procedure
        test_procedures = [
            {"id": "root-canal-therapy", "name": "Root Canal Therapy"},
            {"id": "dental-implant-placement", "name": "Dental Implant Placement"},
            {"id": "tooth-extraction", "name": "Tooth Extraction"}
        ]
        
        for procedure in test_procedures:
            print(f"\n🦷 Testing PDF generation for: {procedure['name']}")
            
            pdf_request = {
                "patientEmail": "test@example.com",
                "procedureId": procedure["id"],
                "procedureName": procedure["name"]
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/practice/email-pdf", json=pdf_request)
                print(f"PDF generation response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ PDF generation successful for {procedure['name']}")
                        print(f"   Message: {data.get('message', 'N/A')}")
                        
                        # Check backend logs for debug messages
                        print("\n📋 Checking backend logs for debug messages...")
                        self.check_backend_logs()
                        
                    else:
                        print(f"❌ PDF generation failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ PDF generation failed with status {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing PDF generation: {e}")
            
            print("-" * 60)
    
    def check_backend_logs(self):
        """Check backend logs for debug messages"""
        try:
            import subprocess
            
            # Get recent backend logs
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for specific debug messages
                debug_messages = [
                    "🔍 Custom logo data size:",
                    "✅ Using custom practice logo in PDF",
                    "⚠️ Custom logo data too small, likely corrupted placeholder",
                    "⚠️ Using default logo fallback",
                    "ℹ️ No custom practice logo found",
                    "❌ Logo handling error:"
                ]
                
                found_messages = []
                for line in logs.split('\n'):
                    for msg in debug_messages:
                        if msg in line:
                            found_messages.append(line.strip())
                
                if found_messages:
                    print("🔍 Debug messages found in backend logs:")
                    for msg in found_messages[-10:]:  # Show last 10 relevant messages
                        print(f"   {msg}")
                else:
                    print("ℹ️ No specific debug messages found in recent logs")
                    
            else:
                print("⚠️ Could not read backend logs")
                
        except Exception as e:
            print(f"⚠️ Error checking backend logs: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive PDF logo debug test"""
        print("=" * 80)
        print("PDF LOGO DEBUG TESTING - ENHANCED DEBUGGING")
        print("=" * 80)
        print(f"Test started at: {datetime.now()}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {TEST_EMAIL}")
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Get current practice branding
        practice_data = self.get_practice_branding()
        if not practice_data:
            print("\n❌ CRITICAL: Could not retrieve practice branding data")
            return False
        
        # Step 3: Test PDF generation with debug monitoring
        self.test_pdf_generation()
        
        print("\n" + "=" * 80)
        print("PDF LOGO DEBUG TEST SUMMARY")
        print("=" * 80)
        
        # Key questions to answer
        print("\n🔍 KEY FINDINGS:")
        print("1. Authentication Status: ✅ SUCCESS")
        print("2. Practice Branding Data: ✅ RETRIEVED")
        
        # Analyze logo data
        branding = practice_data.get("branding", {})
        logo = branding.get("logo", "")
        
        if logo:
            try:
                import base64
                logo_data = logo.split(',')[1] if ',' in logo else logo
                logo_bytes = base64.b64decode(logo_data)
                logo_size = len(logo_bytes)
                
                print(f"3. Logo Data Size: {logo_size} bytes")
                
                if logo_size < 100:
                    print("4. Logo Status: ❌ CORRUPTED (too small - likely 1x1 pixel placeholder)")
                    print("5. Expected PDF Behavior: ⚠️ Will use default logo fallback")
                else:
                    print("4. Logo Status: ✅ APPEARS VALID")
                    print("5. Expected PDF Behavior: ✅ Should use custom practice logo")
                    
            except Exception as e:
                print(f"3. Logo Analysis Error: {e}")
                print("4. Logo Status: ❌ CORRUPTED (invalid base64 data)")
                print("5. Expected PDF Behavior: ⚠️ Will use default logo fallback")
        else:
            print("3. Logo Data: ❌ NO LOGO DATA FOUND")
            print("4. Logo Status: ❌ MISSING")
            print("5. Expected PDF Behavior: ⚠️ Will use text header")
        
        print("\n📋 BACKEND LOG ANALYSIS:")
        print("Check the debug messages above for specific logo processing details.")
        
        print(f"\nTest completed at: {datetime.now()}")
        return True

def main():
    """Main test execution"""
    tester = PDFLogoDebugTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ PDF logo debug testing completed successfully")
        sys.exit(0)
    else:
        print("\n❌ PDF logo debug testing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()