#!/usr/bin/env python3
import requests
import json

# Test authentication and logo data
url = "https://aftercareportal.preview.emergentagent.com"
auth_data = {"email": "cganz2279@gmail.com", "password": "password123"}

print("Testing authentication...")
try:
    response = requests.post(f"{url}/api/auth/login", json=auth_data, timeout=10)
    print(f"Auth status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        practice = data.get("practice", {})
        
        print(f"Practice: {practice.get('name', 'Unknown')}")
        
        # Get dashboard data
        headers = {"Authorization": f"Bearer {token}"}
        dash_response = requests.get(f"{url}/api/practice/dashboard", headers=headers, timeout=10)
        print(f"Dashboard status: {dash_response.status_code}")
        
        if dash_response.status_code == 200:
            dash_data = dash_response.json()
            print(f"Dashboard keys: {list(dash_data.keys())}")
            
            # Check nested data structure
            data_section = dash_data.get("data", {})
            print(f"Data section keys: {list(data_section.keys())}")
            
            branding = data_section.get("branding", {})
            logo = branding.get("logo", "")
            
            print(f"Branding data: {branding}")
            print(f"Logo data length: {len(logo)} characters")
            if logo:
                print(f"First 100 chars: {logo[:100]}")
                
                # Check if it's the 1x1 placeholder
                placeholder = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
                if logo == placeholder:
                    print("🚨 CONFIRMED: 1x1 pixel placeholder detected!")
                else:
                    print("✅ Logo appears to be valid (not 1x1 placeholder)")
            else:
                print("❌ No logo data found")
        
except Exception as e:
    print(f"Error: {e}")