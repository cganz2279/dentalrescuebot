#!/usr/bin/env python3
"""
URGENT SPECIALTY CORRUPTION CHECK
Testing for reported issue where all 81 procedures show in General Dentistry instead of proper specialties
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate and get JWT token"""
    print("🔐 Authenticating...")
    
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
            print(f"✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_specialties_corruption():
    """Test GET /api/specialties to check procedure counts"""
    print("\n🔍 TESTING SPECIALTIES CORRUPTION...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/specialties")
        print(f"GET /api/specialties - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                specialties = data.get('data', [])
                print(f"Found {len(specialties)} specialties:")
                
                total_procedures = 0
                general_dentistry_count = 0
                
                for specialty in specialties:
                    name = specialty.get('name', 'Unknown')
                    count = specialty.get('procedureCount', 0)
                    specialty_id = specialty.get('id', 'Unknown')
                    
                    print(f"  • {name}: {count} procedures (ID: {specialty_id})")
                    total_procedures += count
                    
                    if name == "General Dentistry":
                        general_dentistry_count = count
                
                print(f"\nTOTAL PROCEDURES ACROSS ALL SPECIALTIES: {total_procedures}")
                print(f"GENERAL DENTISTRY COUNT: {general_dentistry_count}")
                
                # Check for corruption
                if general_dentistry_count >= 81:
                    print("🚨 CRITICAL CORRUPTION DETECTED: General Dentistry has 81+ procedures!")
                    print("🚨 This confirms the user's report of specialty corruption!")
                elif total_procedures == 81 and general_dentistry_count < 81:
                    print("✅ Specialties appear properly distributed")
                else:
                    print(f"⚠️  Unexpected total: {total_procedures} procedures (expected 81)")
                
                return specialties
            else:
                print(f"❌ API returned success=false: {data}")
                return None
        else:
            print(f"❌ Failed to get specialties: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing specialties: {str(e)}")
        return None

def test_specific_procedure_specialty(procedure_id, expected_specialty):
    """Test specific procedure to check its specialty assignment"""
    print(f"\n🔍 TESTING {procedure_id.upper()} SPECIALTY...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/procedures/{procedure_id}")
        print(f"GET /api/procedures/{procedure_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                procedure = data.get('data', {})
                name = procedure.get('name', 'Unknown')
                specialty = procedure.get('specialty', 'Unknown')
                specialty_name = procedure.get('specialtyName', 'Unknown')
                
                print(f"Procedure: {name}")
                print(f"Specialty ID: {specialty}")
                print(f"Specialty Name: {specialty_name}")
                
                if specialty_name == "General Dentistry" and expected_specialty != "General Dentistry":
                    print(f"🚨 CORRUPTION CONFIRMED: {name} shows as 'General Dentistry' instead of '{expected_specialty}'!")
                    return False
                elif specialty_name == expected_specialty:
                    print(f"✅ Correct specialty: {specialty_name}")
                    return True
                else:
                    print(f"⚠️  Unexpected specialty: {specialty_name} (expected: {expected_specialty})")
                    return False
            else:
                print(f"❌ API returned success=false: {data}")
                return False
        else:
            print(f"❌ Failed to get procedure: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing procedure {procedure_id}: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚨 URGENT SPECIALTY CORRUPTION CHECK")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Credentials: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Check specialties and procedure counts
    specialties = test_specialties_corruption()
    
    # Test 2: Check Root Canal Therapy (should be Endodontics)
    root_canal_correct = test_specific_procedure_specialty("root-canal-therapy", "Endodontics")
    
    # Test 3: Check Dental Implant Placement (should be Oral Surgery)
    implant_correct = test_specific_procedure_specialty("dental-implant-placement", "Oral Surgery")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 CORRUPTION CHECK SUMMARY")
    print("=" * 60)
    
    if specialties:
        general_dentistry_count = 0
        for specialty in specialties:
            if specialty.get('name') == "General Dentistry":
                general_dentistry_count = specialty.get('procedureCount', 0)
                break
        
        if general_dentistry_count >= 81:
            print("🚨 CRITICAL ISSUE: All procedures corrupted to General Dentistry")
            print("🚨 IMMEDIATE ACTION REQUIRED: Restore specialty assignments")
        elif not root_canal_correct or not implant_correct:
            print("🚨 PARTIAL CORRUPTION: Some procedures have wrong specialties")
            print("🚨 ACTION REQUIRED: Fix specialty assignments")
        else:
            print("✅ No corruption detected - specialties appear correct")
    else:
        print("❌ Could not complete corruption check due to API errors")
    
    print("=" * 60)

if __name__ == "__main__":
    main()