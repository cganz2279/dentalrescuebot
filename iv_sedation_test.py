#!/usr/bin/env python3
"""
IV Sedation Procedure Verification Test
Testing specific review request: IV Sedation not loaded into Oral Surgery section
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate with the backend and return JWT token"""
    print("🔐 Authenticating with backend...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            practice_name = data.get('practice', {}).get('name', 'Unknown')
            print(f"✅ Authentication successful - Practice: {practice_name}")
            return token
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_iv_sedation_procedure(token):
    """Test GET /api/procedures/iv-sedation"""
    print("\n🎯 Testing IV Sedation Procedure...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(f"{BACKEND_URL}/procedures/iv-sedation", headers=headers)
        print(f"IV Sedation API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                procedure = data.get('data', {})
                print(f"✅ IV Sedation procedure found!")
                print(f"   ID: {procedure.get('id')}")
                print(f"   Name: {procedure.get('name')}")
                print(f"   Specialty: {procedure.get('specialty')}")
                print(f"   Specialty Name: {procedure.get('specialtyName')}")
                print(f"   Overview (first 200 chars): {procedure.get('overview', '')[:200]}...")
                
                # Verify expected values
                expected_checks = [
                    ("id", "iv-sedation", procedure.get('id')),
                    ("name", "I.V. Sedation", procedure.get('name')),
                    ("specialty", "oral-surgery", procedure.get('specialty')),
                    ("specialtyName", "Oral Surgery", procedure.get('specialtyName'))
                ]
                
                print("\n🔍 Verification Results:")
                all_correct = True
                for field, expected, actual in expected_checks:
                    if actual == expected:
                        print(f"   ✅ {field}: {actual} (correct)")
                    else:
                        print(f"   ❌ {field}: {actual} (expected: {expected})")
                        all_correct = False
                
                return all_correct, procedure
            else:
                print(f"❌ API returned success=false: {data}")
                return False, None
        elif response.status_code == 404:
            print("❌ IV Sedation procedure NOT FOUND (404)")
            return False, None
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error testing IV Sedation: {str(e)}")
        return False, None

def test_specialties(token):
    """Test GET /api/specialties"""
    print("\n🏥 Testing Specialties...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(f"{BACKEND_URL}/specialties", headers=headers)
        print(f"Specialties API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                specialties = data.get('data', [])
                print(f"✅ Found {len(specialties)} specialties")
                
                # Find Oral Surgery specialty
                oral_surgery = None
                for specialty in specialties:
                    if specialty.get('id') == 'oral-surgery' or specialty.get('name') == 'Oral Surgery':
                        oral_surgery = specialty
                        break
                
                if oral_surgery:
                    print(f"✅ Oral Surgery specialty found!")
                    print(f"   ID: {oral_surgery.get('id')}")
                    print(f"   Name: {oral_surgery.get('name')}")
                    print(f"   Procedure Count: {oral_surgery.get('procedureCount')}")
                    return True, oral_surgery
                else:
                    print("❌ Oral Surgery specialty NOT FOUND")
                    print("Available specialties:")
                    for specialty in specialties:
                        print(f"   - {specialty.get('name')} (id: {specialty.get('id')}, count: {specialty.get('procedureCount')})")
                    return False, None
            else:
                print(f"❌ API returned success=false: {data}")
                return False, None
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error testing specialties: {str(e)}")
        return False, None

def test_oral_surgery_procedures(token):
    """Test GET /api/procedures?specialty=oral-surgery"""
    print("\n🦷 Testing Oral Surgery Procedures...")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(f"{BACKEND_URL}/procedures?specialty=oral-surgery", headers=headers)
        print(f"Oral Surgery procedures API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                procedures = data.get('data', [])
                print(f"✅ Found {len(procedures)} procedures in Oral Surgery")
                
                # Look for IV Sedation
                iv_sedation_found = False
                print("\nOral Surgery procedures:")
                for procedure in procedures:
                    name = procedure.get('name')
                    proc_id = procedure.get('id')
                    print(f"   - {name} (id: {proc_id})")
                    
                    if proc_id == 'iv-sedation' or name == 'I.V. Sedation':
                        iv_sedation_found = True
                        print(f"     ✅ IV Sedation found in Oral Surgery!")
                
                if not iv_sedation_found:
                    print("❌ IV Sedation NOT found in Oral Surgery procedures")
                
                return True, procedures, iv_sedation_found
            else:
                print(f"❌ API returned success=false: {data}")
                return False, [], False
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False, [], False
            
    except Exception as e:
        print(f"❌ Error testing oral surgery procedures: {str(e)}")
        return False, [], False

def main():
    """Main test execution"""
    print("🚨 IV SEDATION PROCEDURE VERIFICATION TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test credentials: {TEST_EMAIL}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Test results
    results = {
        'iv_sedation_exists': False,
        'iv_sedation_correct': False,
        'oral_surgery_exists': False,
        'iv_sedation_in_oral_surgery': False,
        'procedure_count': 0
    }
    
    # Test 1: Check if IV Sedation procedure exists
    iv_correct, iv_procedure = test_iv_sedation_procedure(token)
    results['iv_sedation_exists'] = iv_procedure is not None
    results['iv_sedation_correct'] = iv_correct
    
    # Test 2: Check specialties and Oral Surgery
    specialties_ok, oral_surgery = test_specialties(token)
    results['oral_surgery_exists'] = oral_surgery is not None
    if oral_surgery:
        results['procedure_count'] = oral_surgery.get('procedureCount', 0)
    
    # Test 3: Check procedures in Oral Surgery
    procedures_ok, procedures, iv_in_oral = test_oral_surgery_procedures(token)
    results['iv_sedation_in_oral_surgery'] = iv_in_oral
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 50)
    
    print(f"1. IV Sedation procedure exists: {'✅' if results['iv_sedation_exists'] else '❌'}")
    print(f"2. IV Sedation has correct details: {'✅' if results['iv_sedation_correct'] else '❌'}")
    print(f"3. Oral Surgery specialty exists: {'✅' if results['oral_surgery_exists'] else '❌'}")
    print(f"4. Oral Surgery procedure count: {results['procedure_count']}")
    print(f"5. IV Sedation in Oral Surgery list: {'✅' if results['iv_sedation_in_oral_surgery'] else '❌'}")
    
    # Diagnosis
    print("\n🔍 DIAGNOSIS:")
    if results['iv_sedation_exists'] and results['iv_sedation_correct'] and results['iv_sedation_in_oral_surgery']:
        print("✅ IV Sedation is properly loaded into Oral Surgery section")
    elif results['iv_sedation_exists'] and not results['iv_sedation_in_oral_surgery']:
        print("❌ IV Sedation exists but is NOT in Oral Surgery specialty")
        print("   This indicates the procedure was created with wrong specialty assignment")
    elif not results['iv_sedation_exists']:
        print("❌ IV Sedation procedure does NOT exist in database")
        print("   This indicates the database update failed completely")
    else:
        print("❌ IV Sedation has incorrect details or specialty assignment")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()