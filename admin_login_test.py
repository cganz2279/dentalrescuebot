#!/usr/bin/env python3
"""
Admin Login API Test
Tests the specific admin login and dashboard endpoints requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://dentistpdf.preview.emergentagent.com/api"

# Admin credentials from the review request
ADMIN_CREDENTIALS = {
    "email": "cganz@admin.com",
    "password": "Dentist1#"
}

def test_admin_login():
    """Test POST /api/admin/login endpoint"""
    print("🔐 Testing Admin Login API...")
    print(f"URL: {BACKEND_URL}/admin/login")
    print(f"Credentials: {ADMIN_CREDENTIALS}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/login",
            json=ADMIN_CREDENTIALS,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # Check for expected fields
            if data.get("success") and data.get("token"):
                print("✅ Admin login successful!")
                print(f"JWT Token received: {data['token'][:50]}...")
                return data["token"]
            else:
                print("❌ Admin login failed - missing success or token in response")
                return None
        else:
            print(f"❌ Admin login failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response text: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during admin login: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during admin login: {e}")
        return None

def test_admin_dashboard(jwt_token):
    """Test GET /api/admin/dashboard endpoint with JWT token"""
    print("\n📊 Testing Admin Dashboard API...")
    print(f"URL: {BACKEND_URL}/admin/dashboard")
    print(f"Using JWT Token: {jwt_token[:50]}...")
    
    try:
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BACKEND_URL}/admin/dashboard",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # Check for expected dashboard fields
            if data.get("success") and data.get("stats"):
                print("✅ Admin dashboard loaded successfully!")
                stats = data["stats"]
                print(f"Dashboard Stats:")
                print(f"  - Total Practices: {stats.get('total_practices', 'N/A')}")
                print(f"  - Active Practices: {stats.get('active_practices', 'N/A')}")
                print(f"  - Trial Practices: {stats.get('trial_practices', 'N/A')}")
                print(f"  - Total Revenue: ${stats.get('total_revenue', 'N/A')}")
                print(f"  - Recent Practices: {len(data.get('recent_practices', []))}")
                print(f"  - Expiring Trials: {len(data.get('expiring_trials', []))}")
                return True
            else:
                print("❌ Admin dashboard failed - missing success or stats in response")
                return False
        else:
            print(f"❌ Admin dashboard failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during admin dashboard: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during admin dashboard: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 80)
    print("ADMIN LOGIN API TESTING")
    print("=" * 80)
    print(f"Testing against: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Test 1: Admin Login
    jwt_token = test_admin_login()
    
    if not jwt_token:
        print("\n❌ CRITICAL: Admin login failed - cannot proceed with dashboard test")
        print("\n🔍 DIAGNOSIS:")
        print("- The admin login API is not working correctly")
        print("- This could be a backend API issue")
        print("- Check if the admin credentials are correct")
        print("- Verify the backend service is running")
        sys.exit(1)
    
    # Test 2: Admin Dashboard (only if login succeeded)
    dashboard_success = test_admin_dashboard(jwt_token)
    
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if jwt_token and dashboard_success:
        print("✅ ADMIN LOGIN: WORKING")
        print("✅ ADMIN DASHBOARD: WORKING")
        print("\n🎉 CONCLUSION: Backend admin APIs are working correctly!")
        print("   The frontend admin login issue is likely a frontend problem, not backend.")
        print("   Both admin login and dashboard endpoints are functional.")
    elif jwt_token and not dashboard_success:
        print("✅ ADMIN LOGIN: WORKING")
        print("❌ ADMIN DASHBOARD: FAILED")
        print("\n⚠️  CONCLUSION: Admin login works but dashboard has issues.")
        print("   This is a backend API problem with the dashboard endpoint.")
    else:
        print("❌ ADMIN LOGIN: FAILED")
        print("❌ ADMIN DASHBOARD: NOT TESTED")
        print("\n🚨 CONCLUSION: Backend admin login API is not working!")
        print("   This is definitely a backend API issue.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()