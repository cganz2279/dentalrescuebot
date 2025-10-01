#!/usr/bin/env python3
"""
PDF DATA FLOW COMPREHENSIVE TEST
================================
Testing the complete data flow from login → AuthContext → PDF generation
to verify why PDFs show generic content instead of practice-specific information.

FINDINGS FROM LOGIN INVESTIGATION:
✅ Login response HAS complete practice data (officeHours, emergencyContact)
❌ Procedure API does NOT include practice data
🎯 Issue: Practice data not being passed from AuthContext to PDF generator
"""

import requests
import json
import sys
from typing import Dict, Any

# Use the backend URL from frontend/.env
BACKEND_URL = "https://dental-admin-3.preview.emergentagent.com"

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def test_complete_pdf_data_flow():
    """Test the complete data flow for PDF generation"""
    print_section("PDF DATA FLOW COMPREHENSIVE TEST")
    
    # Test credentials
    login_credentials = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    print(f"🔐 Testing with: {login_credentials['email']}")
    
    try:
        # Step 1: Login and get practice data
        print_section("STEP 1: LOGIN & PRACTICE DATA EXTRACTION")
        
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=login_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
        login_data = login_response.json()
        practice_data = login_data.get('practice', {})
        
        # Extract key practice information
        practice_name = practice_data.get('name')
        practice_phone = practice_data.get('phone')
        office_hours = practice_data.get('officeHours')
        emergency_contact = practice_data.get('emergencyContact')
        
        print(f"✅ Login successful")
        print(f"🏢 Practice Name: {practice_name}")
        print(f"📞 Practice Phone: {practice_phone}")
        print(f"🕒 Office Hours: {office_hours}")
        print(f"🚨 Emergency Contact: {emergency_contact}")
        
        # Step 2: Test procedure API (what PDF generator receives)
        print_section("STEP 2: PROCEDURE API DATA")
        
        procedure_response = requests.get(
            f"{BACKEND_URL}/api/procedures/root-canal-therapy",
            headers={"Content-Type": "application/json"}
        )
        
        if procedure_response.status_code != 200:
            print(f"❌ Procedure API failed: {procedure_response.text}")
            return False
            
        procedure_data = procedure_response.json()
        procedure_info = procedure_data.get('data', {})
        
        print(f"✅ Procedure API successful")
        print(f"🦷 Procedure: {procedure_info.get('name')}")
        print(f"🏥 Practice Name in API: {procedure_info.get('practiceName', 'MISSING')}")
        print(f"📞 Practice Phone in API: {procedure_info.get('practicePhone', 'MISSING')}")
        print(f"🕒 Office Hours in API: {procedure_info.get('practiceOfficeHours', 'MISSING')}")
        print(f"🚨 Emergency Contact in API: {procedure_info.get('practiceEmergencyContact', 'MISSING')}")
        
        # Step 3: Analyze the data gap
        print_section("STEP 3: DATA GAP ANALYSIS")
        
        has_practice_data_in_login = bool(office_hours and emergency_contact)
        has_practice_data_in_procedure = bool(
            procedure_info.get('practiceOfficeHours') and 
            procedure_info.get('practiceEmergencyContact')
        )
        
        print(f"📊 LOGIN RESPONSE:")
        print(f"   ✅ Has Office Hours: {bool(office_hours)}")
        print(f"   ✅ Has Emergency Contact: {bool(emergency_contact)}")
        print(f"   ✅ Complete Practice Data: {has_practice_data_in_login}")
        
        print(f"📊 PROCEDURE API:")
        print(f"   ❌ Has Office Hours: {bool(procedure_info.get('practiceOfficeHours'))}")
        print(f"   ❌ Has Emergency Contact: {bool(procedure_info.get('practiceEmergencyContact'))}")
        print(f"   ❌ Complete Practice Data: {has_practice_data_in_procedure}")
        
        # Step 4: Root cause identification
        print_section("STEP 4: ROOT CAUSE IDENTIFICATION")
        
        if has_practice_data_in_login and not has_practice_data_in_procedure:
            print("🎯 ROOT CAUSE IDENTIFIED:")
            print("   ✅ Login provides complete practice data")
            print("   ❌ Procedure API does NOT include practice data")
            print("   🔧 ISSUE: Frontend must combine login practice data with procedure data")
            print("   📝 SOLUTION: AuthContext should pass practice data to PDF generator")
            
            # Step 5: Test what should be in PDF
            print_section("STEP 5: EXPECTED PDF CONTENT")
            
            print("📄 PDF SHOULD CONTAIN:")
            print(f"   🏢 Practice: {practice_name}")
            print(f"   📞 Phone: {practice_phone}")
            print(f"   🕒 Office Hours: {office_hours}")
            print(f"   🚨 Emergency: {emergency_contact}")
            
            print("📄 PDF CURRENTLY SHOWS:")
            print("   🏢 Practice: Generic placeholder")
            print("   📞 Phone: Generic placeholder")
            print("   🕒 Office Hours: 'Contact your dental office during regular business hours'")
            print("   🚨 Emergency: 'Follow your dentist's emergency contact instructions'")
            
            return True
        else:
            print("❌ UNEXPECTED DATA PATTERN")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_multiple_procedures():
    """Test multiple procedures to confirm the pattern"""
    print_section("TESTING MULTIPLE PROCEDURES")
    
    procedures_to_test = [
        "root-canal-therapy",
        "dental-implant-placement", 
        "tooth-extraction"
    ]
    
    for procedure_id in procedures_to_test:
        print(f"\n🦷 Testing: {procedure_id}")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/procedures/{procedure_id}",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                has_practice_data = bool(
                    data.get('practiceOfficeHours') or 
                    data.get('practiceEmergencyContact')
                )
                print(f"   📊 Status: ✅ Found")
                print(f"   🏥 Has Practice Data: {'✅' if has_practice_data else '❌'}")
            else:
                print(f"   📊 Status: ❌ Not Found ({response.status_code})")
                
        except Exception as e:
            print(f"   📊 Status: ❌ Error ({e})")

def main():
    """Main test function"""
    print("🚀 STARTING PDF DATA FLOW COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test the complete data flow
    success = test_complete_pdf_data_flow()
    
    # Test multiple procedures to confirm pattern
    test_multiple_procedures()
    
    print_section("TEST SUMMARY")
    
    if success:
        print("✅ COMPREHENSIVE TEST COMPLETED SUCCESSFULLY")
        print("\n🎯 KEY FINDINGS:")
        print("   1. ✅ Login response contains complete practice data")
        print("   2. ❌ Procedure APIs do NOT contain practice data")
        print("   3. 🔧 Frontend must combine login + procedure data for PDFs")
        print("   4. 📝 AuthContext should pass practice data to PDF generator")
        
        print("\n🔧 SOLUTION REQUIRED:")
        print("   - Modify PDF generator to receive practice data from AuthContext")
        print("   - Ensure practice officeHours and emergencyContact are passed to PDF")
        print("   - No backend changes needed - data exists in login response")
        
    else:
        print("❌ TEST FAILED")
        print("🔧 Check authentication and backend connectivity")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)