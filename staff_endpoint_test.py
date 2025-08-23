#!/usr/bin/env python3
"""
Focused test for Practice Staff API endpoint
Tests the GET /api/practice/staff endpoint specifically for Add Patient dentist assignment functionality
"""

import requests
import json

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentalstaff.preview.emergentagent.com/api"

def test_staff_endpoint():
    """Test the practice staff endpoint specifically"""
    session = requests.Session()
    
    print("🧪 Testing Practice Staff API Endpoint")
    print(f"🔗 Testing against: {BACKEND_URL}")
    print("=" * 50)
    
    # Step 1: Login as practice admin
    print("1. Logging in as practice admin...")
    login_data = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "token" in data:
                admin_token = data["token"]
                user = data["user"]
                print(f"✅ Login successful: {user['firstName']} {user['lastName']} ({user['role']})")
            else:
                print("❌ Login failed: Invalid response format")
                return False
        else:
            print(f"❌ Login failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False
    
    # Step 2: Test staff endpoint
    print("\n2. Testing GET /api/practice/staff endpoint...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = session.get(f"{BACKEND_URL}/practice/staff", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Staff endpoint responded with status 200")
            
            if data.get("success") and "data" in data:
                staff_members = data["data"]
                print(f"✅ Response format is correct")
                print(f"📊 Found {len(staff_members)} staff members")
                
                # Analyze staff members
                for i, staff in enumerate(staff_members, 1):
                    print(f"\n   Staff Member {i}:")
                    print(f"   - ID: {staff.get('id', 'N/A')}")
                    print(f"   - Name: {staff.get('firstName', 'N/A')} {staff.get('lastName', 'N/A')}")
                    print(f"   - Email: {staff.get('email', 'N/A')}")
                    print(f"   - Role: {staff.get('role', 'N/A')}")
                    
                    # Check if this is the expected admin user
                    if staff.get('email') == 'cganz2279@gmail.com':
                        print(f"   ✅ Admin user found in staff list")
                
                # Verify format matches frontend expectations
                required_fields = ["id", "firstName", "lastName", "email", "role"]
                format_valid = True
                
                for staff in staff_members:
                    for field in required_fields:
                        if field not in staff:
                            print(f"❌ Missing required field '{field}' in staff member")
                            format_valid = False
                    
                    if staff.get("role") not in ["practice_admin", "practice_staff"]:
                        print(f"❌ Invalid role '{staff.get('role')}' for staff member")
                        format_valid = False
                
                if format_valid:
                    print(f"\n✅ All staff members have required fields for AddPatientPage")
                    print(f"✅ Response format matches frontend expectations")
                    
                    # Check if admin user is present
                    admin_found = any(s.get('email') == 'cganz2279@gmail.com' and s.get('role') == 'practice_admin' for s in staff_members)
                    if admin_found:
                        print(f"✅ Admin user (cganz2279@gmail.com) found in staff list")
                        print(f"\n🎉 Practice Staff Endpoint Test: PASSED")
                        print(f"   The endpoint is working correctly for Add Patient dentist assignment functionality")
                        return True
                    else:
                        print(f"❌ Admin user (cganz2279@gmail.com) not found in staff list")
                        return False
                else:
                    print(f"\n❌ Practice Staff Endpoint Test: FAILED")
                    print(f"   Response format does not match frontend expectations")
                    return False
            else:
                print(f"❌ Invalid response format: {data}")
                return False
        else:
            print(f"❌ Staff endpoint failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Staff endpoint test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_staff_endpoint()
    if success:
        print(f"\n🎯 CONCLUSION: The Practice Staff API endpoint is working correctly.")
        print(f"   The Add Patient page should be able to retrieve staff members for dentist assignment.")
    else:
        print(f"\n⚠️ CONCLUSION: There are issues with the Practice Staff API endpoint.")
        print(f"   This may be causing the Add Patient dentist assignment functionality to fail.")