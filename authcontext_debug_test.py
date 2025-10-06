#!/usr/bin/env python3
"""
AuthContext Debug Test - Investigation of Practice Data Flow
==========================================================

This test specifically investigates the login API response structure
to determine why AuthContext isn't getting complete practice data.

CRITICAL INVESTIGATION POINTS:
1. Login API response structure with cganz2279@gmail.com/password123
2. Complete practice data in response.practice field
3. Comparison with dashboard API data
4. Identification of data inconsistency root cause
"""

import requests
import json
import sys
from datetime import datetime

# Use the backend URL from frontend .env
BACKEND_URL = "https://dentiportal.preview.emergentagent.com/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_json_pretty(data, title=""):
    """Print JSON data in a readable format"""
    if title:
        print(f"\n📊 {title}:")
    print(json.dumps(data, indent=2, default=str))

def test_login_api_response():
    """Test login API and examine complete response structure"""
    print_section("LOGIN API RESPONSE INVESTIGATION")
    
    login_url = f"{BACKEND_URL}/auth/login"
    credentials = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    print(f"🔐 Testing login with: {credentials['email']}")
    print(f"🌐 Login URL: {login_url}")
    
    try:
        response = requests.post(login_url, json=credentials)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            login_data = response.json()
            print_json_pretty(login_data, "COMPLETE LOGIN RESPONSE")
            
            # Extract practice data specifically
            if 'practice' in login_data:
                practice_data = login_data['practice']
                print_json_pretty(practice_data, "PRACTICE DATA FROM LOGIN")
                
                # Check for critical fields
                print(f"\n🏢 Practice Analysis:")
                print(f"   - Practice Name: {practice_data.get('name', 'MISSING')}")
                print(f"   - Office Hours: {practice_data.get('officeHours', 'MISSING')}")
                print(f"   - Emergency Contact: {practice_data.get('emergencyContact', 'MISSING')}")
                print(f"   - Phone: {practice_data.get('phone', 'MISSING')}")
                print(f"   - Practice ID: {practice_data.get('id', 'MISSING')}")
                
                return login_data, practice_data
            else:
                print("❌ NO PRACTICE DATA IN LOGIN RESPONSE")
                return login_data, None
                
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login request failed: {str(e)}")
        return None, None

def test_dashboard_api_response(auth_token):
    """Test dashboard API and compare practice data"""
    print_section("DASHBOARD API RESPONSE COMPARISON")
    
    dashboard_url = f"{BACKEND_URL}/practice/dashboard"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print(f"🌐 Dashboard URL: {dashboard_url}")
    print(f"🔑 Using auth token: {auth_token[:20]}...")
    
    try:
        response = requests.get(dashboard_url, headers=headers)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            dashboard_data = response.json()
            print_json_pretty(dashboard_data, "COMPLETE DASHBOARD RESPONSE")
            
            # Extract practice data from dashboard
            if 'practice' in dashboard_data:
                dashboard_practice = dashboard_data['practice']
                print_json_pretty(dashboard_practice, "PRACTICE DATA FROM DASHBOARD")
                
                print(f"\n🏢 Dashboard Practice Analysis:")
                print(f"   - Practice Name: {dashboard_practice.get('name', 'MISSING')}")
                print(f"   - Office Hours: {dashboard_practice.get('officeHours', 'MISSING')}")
                print(f"   - Emergency Contact: {dashboard_practice.get('emergencyContact', 'MISSING')}")
                print(f"   - Phone: {dashboard_practice.get('phone', 'MISSING')}")
                print(f"   - Practice ID: {dashboard_practice.get('id', 'MISSING')}")
                
                return dashboard_practice
            else:
                print("❌ NO PRACTICE DATA IN DASHBOARD RESPONSE")
                return None
                
        else:
            print(f"❌ Dashboard request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard request failed: {str(e)}")
        return None

def compare_practice_data(login_practice, dashboard_practice):
    """Compare practice data from login vs dashboard APIs"""
    print_section("PRACTICE DATA COMPARISON ANALYSIS")
    
    if not login_practice or not dashboard_practice:
        print("❌ Cannot compare - missing data from one or both APIs")
        return
    
    # Key fields to compare
    key_fields = ['name', 'officeHours', 'emergencyContact', 'phone', 'id', 'address']
    
    print("📊 Field-by-Field Comparison:")
    print(f"{'Field':<20} {'Login API':<30} {'Dashboard API':<30} {'Match':<10}")
    print("-" * 100)
    
    differences = []
    
    for field in key_fields:
        login_value = login_practice.get(field, 'MISSING')
        dashboard_value = dashboard_practice.get(field, 'MISSING')
        
        # Convert to string for comparison
        login_str = str(login_value) if login_value is not None else 'NULL'
        dashboard_str = str(dashboard_value) if dashboard_value is not None else 'NULL'
        
        match = "✅ YES" if login_str == dashboard_str else "❌ NO"
        
        if login_str != dashboard_str:
            differences.append({
                'field': field,
                'login': login_str,
                'dashboard': dashboard_str
            })
        
        # Truncate long values for display
        login_display = login_str[:25] + "..." if len(login_str) > 25 else login_str
        dashboard_display = dashboard_str[:25] + "..." if len(dashboard_str) > 25 else dashboard_str
        
        print(f"{field:<20} {login_display:<30} {dashboard_display:<30} {match:<10}")
    
    if differences:
        print(f"\n🚨 FOUND {len(differences)} DIFFERENCES:")
        for diff in differences:
            print(f"\n   Field: {diff['field']}")
            print(f"   Login API: {diff['login']}")
            print(f"   Dashboard API: {diff['dashboard']}")
    else:
        print(f"\n✅ ALL FIELDS MATCH BETWEEN LOGIN AND DASHBOARD APIs")

def test_procedure_api_practice_data():
    """Test if procedure APIs include practice data"""
    print_section("PROCEDURE API PRACTICE DATA CHECK")
    
    procedure_url = f"{BACKEND_URL}/procedures/root-canal-therapy"
    print(f"🌐 Procedure URL: {procedure_url}")
    
    try:
        response = requests.get(procedure_url)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            procedure_data = response.json()
            
            # Check if practice fields are included
            practice_fields = ['practiceName', 'practicePhone', 'practiceOfficeHours', 'practiceEmergencyContact']
            
            print("🔍 Checking for practice fields in procedure response:")
            for field in practice_fields:
                if field in procedure_data.get('data', {}):
                    value = procedure_data['data'][field]
                    print(f"   ✅ {field}: {value}")
                else:
                    print(f"   ❌ {field}: MISSING")
            
            return procedure_data
        else:
            print(f"❌ Procedure request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Procedure request failed: {str(e)}")
        return None

def test_authcontext_behavior():
    """Test how AuthContext should behave based on login response"""
    print_section("AUTHCONTEXT BEHAVIOR ANALYSIS")
    
    login_url = f"{BACKEND_URL}/auth/login"
    credentials = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code == 200:
            login_data = response.json()
            practice_data = login_data.get('practice')
            
            print("🔍 SIMULATING AUTHCONTEXT LOGIC:")
            print(f"   - Login provides practice data: {'✅ YES' if practice_data else '❌ NO'}")
            
            if practice_data:
                print(f"   - AuthContext should: ⏭️ SKIP dashboard fetch (practice provided)")
                print(f"   - Practice data available to components: ✅ YES")
                
                # Check if the provided practice data has the required fields
                has_office_hours = practice_data.get('officeHours') not in [None, '', 'null']
                has_emergency_contact = practice_data.get('emergencyContact') not in [None, '', 'null']
                
                print(f"\n📋 PRACTICE DATA COMPLETENESS:")
                print(f"   - Office Hours present: {'✅ YES' if has_office_hours else '❌ NO'}")
                print(f"   - Emergency Contact present: {'✅ YES' if has_emergency_contact else '❌ NO'}")
                
                if has_office_hours and has_emergency_contact:
                    print(f"\n✅ EXPECTED BEHAVIOR: PDFs should show actual practice information")
                    print(f"   - Office Hours: {practice_data.get('officeHours')}")
                    print(f"   - Emergency Contact: {practice_data.get('emergencyContact')}")
                else:
                    print(f"\n❌ EXPECTED BEHAVIOR: PDFs will show generic placeholders")
                    print(f"   - Missing fields cause fallback to generic text")
            else:
                print(f"   - AuthContext should: 🏥 FETCH from dashboard API")
                print(f"   - Practice data available to components: ❓ DEPENDS on dashboard API")
                
        return login_data
    except Exception as e:
        print(f"❌ Failed to test AuthContext behavior: {str(e)}")
        return None

def main():
    """Main test execution"""
    print("🎯 AUTHCONTEXT DEBUG TEST - PRACTICE DATA INVESTIGATION")
    print(f"⏰ Test started at: {datetime.now()}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    
    # Step 1: Test login API response
    login_response, login_practice = test_login_api_response()
    
    if not login_response:
        print("❌ Cannot continue - login failed")
        sys.exit(1)
    
    # Extract auth token
    auth_token = login_response.get('token') or login_response.get('access_token')
    if not auth_token:
        print("❌ No auth token in login response")
        sys.exit(1)
    
    # Step 2: Test dashboard API response
    dashboard_practice = test_dashboard_api_response(auth_token)
    
    # Step 3: Compare the data
    compare_practice_data(login_practice, dashboard_practice)
    
    # Step 4: Check procedure API
    test_procedure_api_practice_data()
    
    # Step 5: Analyze AuthContext behavior
    test_authcontext_behavior()
    
    # Final analysis
    print_section("FINAL ANALYSIS & CONCLUSIONS")
    
    print("🎯 ANSWERING THE CRITICAL QUESTION:")
    print("   'Is the login API actually returning the complete practice data with officeHours and emergencyContact fields?'")
    
    if login_practice:
        has_office_hours = login_practice.get('officeHours') not in [None, '', 'null']
        has_emergency_contact = login_practice.get('emergencyContact') not in [None, '', 'null']
        
        print(f"\n📊 LOGIN API ANALYSIS:")
        print(f"   - Login API provides practice data: ✅ YES")
        print(f"   - Practice has Office Hours: {'✅ YES' if has_office_hours else '❌ NO'}")
        print(f"   - Practice has Emergency Contact: {'✅ YES' if has_emergency_contact else '❌ NO'}")
        
        if has_office_hours and has_emergency_contact:
            print(f"\n✅ ANSWER: YES - Login API DOES return complete practice data")
            print(f"   - Office Hours: '{login_practice.get('officeHours')}'")
            print(f"   - Emergency Contact: '{login_practice.get('emergencyContact')}'")
            print(f"\n🔍 ROOT CAUSE: The issue is NOT in the login API response")
            print(f"   - AuthContext receives complete data but may not be using it correctly")
            print(f"   - Frontend components may not be accessing practice data properly")
            print(f"   - PDF generator may not be receiving practice data from AuthContext")
        else:
            print(f"\n❌ ANSWER: NO - Login API returns INCOMPLETE practice data")
            print(f"   - Missing Office Hours: {not has_office_hours}")
            print(f"   - Missing Emergency Contact: {not has_emergency_contact}")
            print(f"\n🔍 ROOT CAUSE: Database lacks complete practice information")
            print(f"   - Practice record needs to be updated with missing fields")
    else:
        print(f"\n❌ ANSWER: NO - Login API does NOT provide practice data at all")
        print(f"   - AuthContext should fetch from dashboard API but may not be doing so")
        print(f"\n🔍 ROOT CAUSE: Login response structure issue")
        
    print(f"\n🎯 RECOMMENDATION:")
    if login_practice and login_practice.get('officeHours') and login_practice.get('emergencyContact'):
        print(f"   - Investigate frontend data flow from AuthContext to PDF generator")
        print(f"   - Verify practice data is being passed to PDF generation components")
        print(f"   - Check if PDF generator is using practice data correctly")
    else:
        print(f"   - Fix database to include complete practice information")
        print(f"   - Ensure AuthContext fetches from dashboard API when needed")
        print(f"   - Verify dashboard API returns complete practice data")

if __name__ == "__main__":
    main()