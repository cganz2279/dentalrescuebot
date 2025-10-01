#!/usr/bin/env python3
"""
URGENT LOGIN RESPONSE STRUCTURE TEST - Review Request
Test the login API to see exactly what practice data it's returning
Focus: Complete response structure and practice field analysis
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://dental-portal-debug.preview.emergentagent.com/api"

class LoginResponseTester:
    def __init__(self):
        self.session = requests.Session()
        
    def test_login_response_structure(self):
        """URGENT: Test login API response structure with cganz2279@gmail.com/password123"""
        print("🚨 URGENT LOGIN API RESPONSE TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing credentials: cganz2279@gmail.com/password123")
        print("=" * 60)
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": "cganz2279@gmail.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 Response Status Code: {response.status_code}")
            print(f"🔍 Response Headers: {dict(response.headers)}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                
                print("🎯 COMPLETE LOGIN RESPONSE STRUCTURE:")
                print("=" * 60)
                print(json.dumps(data, indent=2, default=str))
                print("=" * 60)
                print()
                
                # Analyze practice field specifically
                practice_data = data.get("practice")
                if practice_data:
                    print("🏥 PRACTICE FIELD ANALYSIS:")
                    print("=" * 40)
                    print(f"Practice field exists: ✅ YES")
                    print(f"Practice field type: {type(practice_data)}")
                    print()
                    
                    print("📋 PRACTICE FIELD CONTENTS:")
                    for key, value in practice_data.items():
                        print(f"  {key}: {value} (type: {type(value).__name__})")
                    print()
                    
                    # Check specifically for officeHours and emergencyContact
                    office_hours = practice_data.get("officeHours")
                    emergency_contact = practice_data.get("emergencyContact")
                    
                    print("🎯 CRITICAL FIELDS CHECK:")
                    print(f"  officeHours: {'✅ PRESENT' if office_hours is not None else '❌ MISSING'}")
                    if office_hours is not None:
                        print(f"    Value: '{office_hours}'")
                        print(f"    Type: {type(office_hours).__name__}")
                        print(f"    Length: {len(str(office_hours))}")
                    
                    print(f"  emergencyContact: {'✅ PRESENT' if emergency_contact is not None else '❌ MISSING'}")
                    if emergency_contact is not None:
                        print(f"    Value: '{emergency_contact}'")
                        print(f"    Type: {type(emergency_contact).__name__}")
                        print(f"    Length: {len(str(emergency_contact))}")
                    
                    print()
                    
                else:
                    print("🏥 PRACTICE FIELD ANALYSIS:")
                    print("=" * 40)
                    print("❌ NO PRACTICE FIELD IN RESPONSE")
                    print()
                    
                    # Check if practice data is nested elsewhere
                    user_data = data.get("user", {})
                    if "practice" in user_data:
                        print("🔍 Found practice data in user field:")
                        print(json.dumps(user_data["practice"], indent=2, default=str))
                    elif "practiceId" in user_data:
                        print(f"🔍 Found practiceId in user field: {user_data['practiceId']}")
                    else:
                        print("🔍 No practice-related data found in user field")
                
                # Summary for review request
                print("🎯 REVIEW REQUEST SUMMARY:")
                print("=" * 40)
                if practice_data and office_hours is not None and emergency_contact is not None:
                    print("✅ LOGIN API RETURNS COMPLETE PRACTICE DATA")
                    print("✅ officeHours field is present and populated")
                    print("✅ emergencyContact field is present and populated")
                    print("🎯 CONCLUSION: This is likely a FRONTEND issue (option B)")
                    print("   The backend is providing the practice data correctly.")
                elif practice_data:
                    print("⚠️  LOGIN API RETURNS PRACTICE DATA BUT MISSING CRITICAL FIELDS")
                    print(f"   officeHours: {'Present' if office_hours is not None else 'Missing'}")
                    print(f"   emergencyContact: {'Present' if emergency_contact is not None else 'Missing'}")
                    print("🎯 CONCLUSION: This is a BACKEND issue (option A)")
                    print("   The practice data is incomplete.")
                else:
                    print("❌ LOGIN API DOES NOT RETURN PRACTICE DATA")
                    print("🎯 CONCLUSION: This is a BACKEND issue (option A)")
                    print("   The login API is not returning practice information.")
                
                return True
                
            else:
                print(f"❌ LOGIN FAILED")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
                print()
                print("🎯 REVIEW REQUEST SUMMARY:")
                print("=" * 40)
                print("❌ CANNOT TEST PRACTICE DATA - LOGIN FAILED")
                print("🎯 CONCLUSION: Authentication issue needs to be resolved first")
                
                return False
                
        except Exception as e:
            print(f"❌ REQUEST FAILED: {str(e)}")
            print()
            print("🎯 REVIEW REQUEST SUMMARY:")
            print("=" * 40)
            print("❌ CANNOT TEST PRACTICE DATA - CONNECTION FAILED")
            print("🎯 CONCLUSION: Backend connectivity issue")
            return False
    
    def test_database_relationship(self):
        """Test if we can verify the practice record exists in database"""
        print("\n🔍 TESTING DATABASE RELATIONSHIP")
        print("=" * 60)
        
        # First, try to login to get authentication
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": "cganz2279@gmail.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                
                if token:
                    # Set authorization header
                    self.session.headers.update({
                        "Authorization": f"Bearer {token}"
                    })
                    
                    # Try to get practice dashboard data
                    dashboard_response = self.session.get(f"{BACKEND_URL}/practice/dashboard")
                    
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        
                        print("📊 PRACTICE DASHBOARD DATA:")
                        print("=" * 40)
                        print(json.dumps(dashboard_data, indent=2, default=str))
                        print()
                        
                        # Extract practice info from dashboard
                        practice_info = dashboard_data.get("data", {}).get("practice", {})
                        if practice_info:
                            office_hours = practice_info.get("officeHours")
                            emergency_contact = practice_info.get("emergencyContact")
                            
                            print("🎯 DASHBOARD PRACTICE FIELDS:")
                            print(f"  officeHours: {office_hours}")
                            print(f"  emergencyContact: {emergency_contact}")
                            
                            return True
                    else:
                        print(f"❌ Dashboard request failed: {dashboard_response.status_code}")
                        print(f"Response: {dashboard_response.text}")
                        return False
                else:
                    print("❌ No token in login response")
                    return False
            else:
                print(f"❌ Login failed for dashboard test: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Database relationship test failed: {str(e)}")
            return False

def main():
    """Run the urgent login API test"""
    tester = LoginResponseTester()
    
    print("🚨 URGENT LOGIN API TESTING - REVIEW REQUEST")
    print("Testing login API response to determine if issue is:")
    print("A) Login API not returning practice data (backend issue)")
    print("B) Frontend not using practice data correctly (frontend issue)")
    print()
    
    # Test 1: Login response structure
    login_success = tester.test_login_response_structure()
    
    # Test 2: Database relationship verification
    if login_success:
        tester.test_database_relationship()
    
    print("\n" + "=" * 60)
    print("🎯 URGENT TEST COMPLETED")
    print("See analysis above to determine if this is a backend or frontend issue.")
    print("=" * 60)

if __name__ == "__main__":
    main()