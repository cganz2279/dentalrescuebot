#!/usr/bin/env python3
"""
LOGIN RESPONSE INVESTIGATION
============================
Investigating exactly what practice data is being returned in the login response
to understand why AuthContext is skipping the dashboard fetch.

REVIEW REQUEST GOALS:
1. Login with cganz2279@gmail.com/password123
2. Examine complete login response structure
3. Show what practice data is included in login response
4. Check if officeHours and emergencyContact are included
5. Compare login vs dashboard data
6. Determine fix strategy for PDF generic content issue
"""

import requests
import json
import sys
from typing import Dict, Any

# Use the backend URL from frontend/.env
BACKEND_URL = "https://dentist-dashboard-2.preview.emergentagent.com"

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_json_pretty(data: Any, title: str = ""):
    """Print JSON data in a readable format"""
    if title:
        print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, default=str))

def investigate_login_response():
    """Investigate the login response structure"""
    print_section("LOGIN RESPONSE INVESTIGATION")
    
    # Test credentials from review request
    login_credentials = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    print(f"🔐 Testing login with: {login_credentials['email']}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    
    try:
        # Step 1: Login and examine response
        print_section("STEP 1: LOGIN API CALL")
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Login Status Code: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
        login_data = login_response.json()
        print_json_pretty(login_data, "Complete Login Response")
        
        # Extract practice data from login response
        practice_data_in_login = login_data.get('practice', {})
        print_json_pretty(practice_data_in_login, "Practice Data in Login Response")
        
        # Check for specific fields
        print_section("STEP 2: PRACTICE DATA ANALYSIS")
        
        office_hours = practice_data_in_login.get('officeHours')
        emergency_contact = practice_data_in_login.get('emergencyContact')
        
        print(f"🏢 Practice Name: {practice_data_in_login.get('name', 'NOT FOUND')}")
        print(f"📞 Practice Phone: {practice_data_in_login.get('phone', 'NOT FOUND')}")
        print(f"🕒 Office Hours: {office_hours if office_hours else 'NOT FOUND'}")
        print(f"🚨 Emergency Contact: {emergency_contact if emergency_contact else 'NOT FOUND'}")
        
        # Get JWT token for dashboard call
        jwt_token = login_data.get('token')
        if not jwt_token:
            print("❌ No JWT token in login response")
            return False
            
        # Step 3: Compare with dashboard API
        print_section("STEP 3: DASHBOARD API COMPARISON")
        
        dashboard_response = requests.get(
            f"{BACKEND_URL}/api/practice/dashboard",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"📊 Dashboard Status Code: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print_json_pretty(dashboard_data, "Complete Dashboard Response")
            
            dashboard_practice = dashboard_data.get('practice', {})
            print_json_pretty(dashboard_practice, "Practice Data in Dashboard Response")
            
            # Compare the two practice objects
            print_section("STEP 4: DATA COMPARISON")
            
            print("🔄 COMPARISON RESULTS:")
            print(f"Login Practice Name: {practice_data_in_login.get('name', 'MISSING')}")
            print(f"Dashboard Practice Name: {dashboard_practice.get('name', 'MISSING')}")
            
            print(f"Login Office Hours: {practice_data_in_login.get('officeHours', 'MISSING')}")
            print(f"Dashboard Office Hours: {dashboard_practice.get('officeHours', 'MISSING')}")
            
            print(f"Login Emergency Contact: {practice_data_in_login.get('emergencyContact', 'MISSING')}")
            print(f"Dashboard Emergency Contact: {dashboard_practice.get('emergencyContact', 'MISSING')}")
            
            # Determine the issue
            print_section("STEP 5: ROOT CAUSE ANALYSIS")
            
            login_has_office_hours = bool(practice_data_in_login.get('officeHours'))
            login_has_emergency_contact = bool(practice_data_in_login.get('emergencyContact'))
            
            dashboard_has_office_hours = bool(dashboard_practice.get('officeHours'))
            dashboard_has_emergency_contact = bool(dashboard_practice.get('emergencyContact'))
            
            print(f"🔍 LOGIN RESPONSE ANALYSIS:")
            print(f"   ✅ Has Office Hours: {login_has_office_hours}")
            print(f"   ✅ Has Emergency Contact: {login_has_emergency_contact}")
            
            print(f"🔍 DASHBOARD RESPONSE ANALYSIS:")
            print(f"   ✅ Has Office Hours: {dashboard_has_office_hours}")
            print(f"   ✅ Has Emergency Contact: {dashboard_has_emergency_contact}")
            
            # Determine fix strategy
            print_section("STEP 6: FIX STRATEGY DETERMINATION")
            
            if login_has_office_hours and login_has_emergency_contact:
                print("✅ LOGIN RESPONSE HAS COMPLETE PRACTICE DATA")
                print("🎯 ISSUE: AuthContext should use login practice data for PDFs")
                print("🔧 FIX STRATEGY: Ensure PDF generator receives practice data from AuthContext")
                print("📝 NO NEED to modify AuthContext to fetch dashboard data")
            elif dashboard_has_office_hours and dashboard_has_emergency_contact:
                print("❌ LOGIN RESPONSE MISSING PRACTICE DATA")
                print("✅ DASHBOARD HAS COMPLETE PRACTICE DATA")
                print("🎯 ISSUE: AuthContext needs to fetch dashboard data after login")
                print("🔧 FIX STRATEGY: Modify AuthContext to always fetch dashboard data")
            else:
                print("❌ BOTH LOGIN AND DASHBOARD MISSING PRACTICE DATA")
                print("🎯 ISSUE: Database lacks officeHours and emergencyContact")
                print("🔧 FIX STRATEGY: Populate practice data in database first")
                
        else:
            print(f"❌ Dashboard API failed: {dashboard_response.text}")
            
        # Step 7: Test procedure API to see what's passed to PDF generator
        print_section("STEP 7: PROCEDURE API ANALYSIS")
        
        procedure_response = requests.get(
            f"{BACKEND_URL}/api/procedures/root-canal-therapy",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Procedure API Status Code: {procedure_response.status_code}")
        
        if procedure_response.status_code == 200:
            procedure_data = procedure_response.json()
            procedure_info = procedure_data.get('data', {})
            
            print(f"🦷 Procedure Name: {procedure_info.get('name', 'NOT FOUND')}")
            print(f"🏥 Practice Name in Procedure: {procedure_info.get('practiceName', 'NOT FOUND')}")
            print(f"📞 Practice Phone in Procedure: {procedure_info.get('practicePhone', 'NOT FOUND')}")
            print(f"🕒 Practice Office Hours in Procedure: {procedure_info.get('practiceOfficeHours', 'NOT FOUND')}")
            print(f"🚨 Practice Emergency Contact in Procedure: {procedure_info.get('practiceEmergencyContact', 'NOT FOUND')}")
            
            if not procedure_info.get('practiceOfficeHours'):
                print("❌ CRITICAL: Procedure API does NOT include practice office hours")
                print("🎯 This explains why PDFs show generic content")
        else:
            print(f"❌ Procedure API failed: {procedure_response.text}")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main investigation function"""
    print("🚀 STARTING LOGIN RESPONSE INVESTIGATION")
    print("=" * 60)
    
    success = investigate_login_response()
    
    print_section("INVESTIGATION COMPLETE")
    
    if success:
        print("✅ Investigation completed successfully")
        print("📋 Check the analysis above for root cause and fix strategy")
    else:
        print("❌ Investigation failed")
        print("🔧 Check authentication credentials and backend connectivity")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)