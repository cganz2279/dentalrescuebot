#!/usr/bin/env python3

import requests
import json
import sys
import base64
from datetime import datetime

# Configuration - Using the correct backend URL from frontend/.env
BASE_URL = "https://aftercareportal.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class DashboardBrandingTester:
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
    
    def test_dashboard_branding_data(self):
        """Test GET /api/practice/dashboard for branding data"""
        print("\n📊 Testing Dashboard API for Branding Data...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                practice_data = data.get("data", {})
                print(f"✅ Dashboard API successful")
                print(f"   Practice Name: {practice_data.get('practice', {}).get('name', 'N/A')}")
                
                # Debug: Print the full response structure
                print(f"   Full response structure: {list(practice_data.keys())}")
                
                # Check if branding data is included in practice object
                practice_info = practice_data.get("practice", {})
                branding = practice_info.get("branding")
                
                if branding is None:
                    print("❌ CRITICAL: Branding data is missing from dashboard response")
                    print(f"   Practice data keys: {list(practice_info.keys())}")
                    return False
                
                print("✅ Branding data is included in dashboard response")
                
                # Check branding structure
                required_fields = ["logo", "primaryColor", "secondaryColor", "welcomeMessage"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in branding:
                        missing_fields.append(field)
                    else:
                        print(f"   ✅ {field}: Present")
                
                if missing_fields:
                    print(f"❌ Missing branding fields: {missing_fields}")
                    return False
                
                # Analyze logo data if present
                logo_data = branding.get("logo")
                if logo_data:
                    self.analyze_logo_data(logo_data)
                else:
                    print("   ⚠️  Logo field is present but empty")
                
                # Display other branding values
                print(f"   Primary Color: {branding.get('primaryColor', 'N/A')}")
                print(f"   Secondary Color: {branding.get('secondaryColor', 'N/A')}")
                print(f"   Welcome Message: {branding.get('welcomeMessage', 'N/A')}")
                
                return True
            else:
                print(f"❌ Dashboard API failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Dashboard API failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def analyze_logo_data(self, logo_data):
        """Analyze logo data to determine if it's valid or a placeholder"""
        print("\n🔍 Analyzing Logo Data...")
        
        if not logo_data:
            print("   ❌ Logo data is empty")
            return
        
        # Check if it's a data URL
        if logo_data.startswith("data:image/"):
            print("   ✅ Logo is in data URL format")
            
            # Extract the base64 part
            try:
                header, base64_data = logo_data.split(",", 1)
                image_type = header.split(";")[0].split("/")[1]
                print(f"   Image Type: {image_type}")
                
                # Decode base64 to get actual size
                decoded_data = base64.b64decode(base64_data)
                size_bytes = len(decoded_data)
                
                print(f"   Logo Size: {size_bytes} bytes ({size_bytes / 1024:.1f} KB)")
                
                # Check if it's a placeholder (1x1 pixel images are typically very small)
                if size_bytes < 200:  # Less than 200 bytes is likely a placeholder
                    print("   ⚠️  Logo appears to be a placeholder (very small size)")
                    
                    # Check for known placeholder pattern
                    placeholder_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
                    if placeholder_b64 in base64_data:
                        print("   ❌ CONFIRMED: Logo is 1x1 pixel transparent PNG placeholder")
                    else:
                        print("   ⚠️  Logo is very small but may be valid")
                else:
                    print("   ✅ Logo appears to be a valid image (reasonable size)")
                    
                    # Additional analysis for larger images
                    if size_bytes > 100000:  # > 100KB
                        print("   📊 Logo is quite large - good for high quality display")
                    elif size_bytes > 10000:  # > 10KB
                        print("   📊 Logo is medium size - suitable for web display")
                    else:
                        print("   📊 Logo is small but likely valid")
                
            except Exception as e:
                print(f"   ❌ Error analyzing logo data: {str(e)}")
        else:
            print("   ❌ Logo is not in expected data URL format")
            print(f"   Logo data preview: {logo_data[:100]}...")
    
    def test_branding_defaults(self):
        """Test that branding data has proper defaults when not customized"""
        print("\n🎨 Testing Branding Defaults...")
        
        response = self.session.get(f"{BASE_URL}/practice/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                branding = data.get("data", {}).get("branding", {})
                
                # Check for default values
                primary_color = branding.get("primaryColor")
                secondary_color = branding.get("secondaryColor")
                welcome_message = branding.get("welcomeMessage")
                
                print(f"   Primary Color: {primary_color}")
                print(f"   Secondary Color: {secondary_color}")
                print(f"   Welcome Message: {welcome_message}")
                
                # Verify defaults are not None/empty
                if primary_color and secondary_color:
                    print("   ✅ Color defaults are properly set")
                else:
                    print("   ❌ Color defaults are missing")
                    return False
                
                if welcome_message:
                    print("   ✅ Welcome message default is set")
                else:
                    print("   ⚠️  Welcome message is empty (may be intentional)")
                
                return True
            else:
                print(f"   ❌ Failed to get dashboard data: {data.get('error')}")
                return False
        else:
            print(f"   ❌ Dashboard request failed: {response.status_code}")
            return False
    
    def run_branding_tests(self):
        """Run all branding-related tests"""
        print("🚀 Starting Dashboard Branding Data Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run branding tests
        tests = [
            ("Dashboard Branding Data Structure", self.test_dashboard_branding_data),
            ("Branding Defaults", self.test_branding_defaults)
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
        print("📊 BRANDING TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All Dashboard Branding tests PASSED!")
            return True
        else:
            print("⚠️  Some branding tests FAILED - see details above")
            return False

def main():
    """Main function to run the branding tests"""
    tester = DashboardBrandingTester()
    success = tester.run_branding_tests()
    
    if success:
        print("\n✅ Dashboard branding data fix is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Dashboard branding data has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()