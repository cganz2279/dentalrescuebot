#!/usr/bin/env python3
"""
Branding Logo Data Analysis Test
Focus: Examine practice branding.logo field to understand logo data issues
"""

import requests
import json
import base64
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate and get JWT token"""
    print("🔐 Authenticating with practice credentials...")
    
    auth_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=auth_data)
        print(f"Auth Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Auth response data: {json.dumps(data, indent=2)}")
            token = data.get("access_token") or data.get("token")
            practice_id = data.get("practice_id") or data.get("practiceId") or data.get("id")
            print(f"✅ Authentication successful")
            print(f"   Practice ID: {practice_id}")
            print(f"   Token length: {len(token) if token else 'None'}")
            return token, practice_id
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def get_practice_dashboard(token):
    """Get practice dashboard data and analyze branding.logo"""
    print("\n📊 Fetching practice dashboard data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/practice/dashboard", headers=headers)
        print(f"Dashboard Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data retrieved successfully")
            
            # Extract practice info from the response structure
            practice_name = data.get("name", "Unknown")
            practice_id = data.get("id", "Unknown")
            
            # Check if practice data is nested
            if not practice_name or practice_name == "Unknown":
                practice_data = data.get("practice", {})
                if practice_data:
                    practice_name = practice_data.get("name", "Unknown")
                    practice_id = practice_data.get("id", "Unknown")
            
            print(f"   Practice Name: {practice_name}")
            print(f"   Practice ID: {practice_id}")
            
            # Analyze branding data - check both locations
            branding = data.get("branding", {})
            if not branding:
                practice_data = data.get("practice", {})
                branding = practice_data.get("branding", {})
            if branding:
                print(f"\n🎨 BRANDING DATA ANALYSIS:")
                print(f"   Primary Color: {branding.get('primaryColor', 'Not set')}")
                print(f"   Secondary Color: {branding.get('secondaryColor', 'Not set')}")
                
                # Focus on logo data
                logo = branding.get("logo", "")
                if logo:
                    print(f"\n🖼️  LOGO DATA DETAILED ANALYSIS:")
                    print(f"   Logo data length: {len(logo)} characters")
                    
                    # Check if it's a data URL
                    if logo.startswith("data:"):
                        print(f"   ✅ Logo is in data URL format")
                        
                        # Extract MIME type
                        if ";" in logo:
                            mime_part = logo.split(";")[0].replace("data:", "")
                            print(f"   MIME type: {mime_part}")
                        
                        # Extract base64 data
                        if "base64," in logo:
                            base64_data = logo.split("base64,")[1]
                            print(f"   Base64 data length: {len(base64_data)} characters")
                            
                            # Try to decode and analyze
                            try:
                                decoded_data = base64.b64decode(base64_data)
                                print(f"   Decoded binary size: {len(decoded_data)} bytes")
                                
                                # Check if it's a valid image by examining headers
                                if decoded_data.startswith(b'\x89PNG'):
                                    print(f"   ✅ Valid PNG image detected")
                                elif decoded_data.startswith(b'\xff\xd8\xff'):
                                    print(f"   ✅ Valid JPEG image detected")
                                elif decoded_data.startswith(b'GIF'):
                                    print(f"   ✅ Valid GIF image detected")
                                else:
                                    print(f"   ⚠️  Unknown image format or corrupted data")
                                    print(f"   First 20 bytes: {decoded_data[:20]}")
                                
                                # Check for 1x1 pixel placeholder
                                if len(decoded_data) < 100:
                                    print(f"   ⚠️  SUSPICIOUS: Very small image size suggests 1x1 pixel placeholder")
                                elif len(decoded_data) > 10000:
                                    print(f"   ✅ Good size: Large enough to be a real logo image")
                                else:
                                    print(f"   ⚠️  Medium size: Could be real image or small placeholder")
                                    
                            except Exception as e:
                                print(f"   ❌ Failed to decode base64 data: {str(e)}")
                    else:
                        print(f"   ❌ Logo is not in data URL format")
                    
                    # Show first 100 characters as requested
                    print(f"\n📝 FIRST 100 CHARACTERS OF LOGO DATA:")
                    print(f"   '{logo[:100]}{'...' if len(logo) > 100 else ''}'")
                    
                    # Check for known 1x1 pixel placeholder
                    placeholder_1x1 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
                    if logo == placeholder_1x1:
                        print(f"   🚨 CONFIRMED: This is the 1x1 pixel transparent PNG placeholder!")
                    else:
                        print(f"   ✅ This is NOT the known 1x1 pixel placeholder")
                        
                else:
                    print(f"   ❌ No logo data found in branding")
            else:
                print(f"   ❌ No branding data found")
            
            return data
            
        else:
            print(f"❌ Dashboard request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard request error: {str(e)}")
        return None

def main():
    """Main test function"""
    print("=" * 80)
    print("🔍 BRANDING LOGO DATA ANALYSIS TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Step 1: Authenticate
    token, practice_id = authenticate()
    if not token:
        print("\n❌ CRITICAL: Authentication failed - cannot proceed with logo analysis")
        return
    
    # Step 2: Get practice dashboard and analyze logo
    dashboard_data = get_practice_dashboard(token)
    if not dashboard_data:
        print("\n❌ CRITICAL: Failed to retrieve dashboard data")
        return
    
    print("\n" + "=" * 80)
    print("🎯 LOGO ANALYSIS SUMMARY")
    print("=" * 80)
    
    branding = dashboard_data.get("branding", {})
    logo = branding.get("logo", "")
    
    if logo:
        logo_size = len(logo)
        if logo.startswith("data:") and "base64," in logo:
            base64_data = logo.split("base64,")[1]
            try:
                decoded_size = len(base64.b64decode(base64_data))
                print(f"✅ Logo data found: {logo_size} characters, {decoded_size} bytes decoded")
                
                if decoded_size < 100:
                    print(f"🚨 ISSUE: Logo appears to be a 1x1 pixel placeholder ({decoded_size} bytes)")
                    print(f"   This explains why PDFs show wrong/missing logos")
                elif decoded_size > 50000:
                    print(f"✅ GOOD: Logo is substantial size ({decoded_size} bytes) - should be valid image")
                else:
                    print(f"⚠️  UNCERTAIN: Logo is medium size ({decoded_size} bytes) - needs verification")
                    
            except:
                print(f"❌ ISSUE: Logo data cannot be decoded - corrupted base64")
        else:
            print(f"❌ ISSUE: Logo data is not in proper data URL format")
    else:
        print(f"❌ CRITICAL: No logo data found in practice branding")
    
    print("\n💡 RECOMMENDATIONS:")
    if not logo:
        print("   - Practice needs to upload a logo through practice settings")
    elif logo and len(logo) < 200:
        print("   - Current logo appears to be placeholder - upload new logo")
        print("   - This explains PDF logo issues - placeholder cannot render properly")
    else:
        print("   - Logo data appears valid - issue may be in PDF generation process")
        print("   - Check PDF generator code for logo processing errors")

if __name__ == "__main__":
    main()