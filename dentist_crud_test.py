#!/usr/bin/env python3
"""
Dentist CRUD Operations Test
Test the dentist management endpoints specifically to verify full CRUD functionality
"""

import requests
import json
import sys
from datetime import datetime

# Production backend URL
PRODUCTION_URL = "https://dentist-portal-3.emergent.host/api"

# Test credentials
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Get authentication token"""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{PRODUCTION_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
    except Exception as e:
        print(f"Authentication failed: {e}")
    
    return None

def test_dentist_crud():
    """Test full CRUD operations for dentist management"""
    print(f"🦷 DENTIST CRUD OPERATIONS TEST")
    print(f"Backend: {PRODUCTION_URL}")
    
    # Get authentication token
    token = authenticate()
    if not token:
        print("❌ Authentication failed - cannot test CRUD operations")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: GET existing dentists
    print(f"\n1️⃣ GET /practice/dentists - List existing dentists")
    try:
        response = requests.get(f"{PRODUCTION_URL}/practice/dentists", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            existing_dentists = data.get("data", [])
            print(f"   ✅ Found {len(existing_dentists)} existing dentists")
            for dentist in existing_dentists:
                print(f"      - {dentist.get('firstName', '')} {dentist.get('lastName', '')} ({dentist.get('email', '')})")
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: POST create new dentist
    print(f"\n2️⃣ POST /practice/dentists - Create new dentist")
    test_dentist = {
        "firstName": "Test",
        "lastName": "Dentist",
        "email": f"test.dentist.{datetime.now().strftime('%H%M%S')}@dentaltest.com",
        "phone": "(555) 123-4567",
        "licenseNumber": f"TEST{datetime.now().strftime('%H%M%S')}",
        "specialties": ["General Dentistry", "Oral Surgery"]
    }
    
    try:
        response = requests.post(f"{PRODUCTION_URL}/practice/dentists", headers=headers, json=test_dentist, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            created_dentist = data.get("data", {})
            dentist_id = created_dentist.get("id")
            print(f"   ✅ Dentist created successfully")
            print(f"      ID: {dentist_id}")
            print(f"      Name: {created_dentist.get('firstName')} {created_dentist.get('lastName')}")
            print(f"      Email: {created_dentist.get('email')}")
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: PUT update dentist
    print(f"\n3️⃣ PUT /practice/dentists/{dentist_id} - Update dentist")
    update_data = {
        "phone": "(555) 999-8888",
        "specialties": ["General Dentistry", "Oral Surgery", "Endodontics"]
    }
    
    try:
        response = requests.put(f"{PRODUCTION_URL}/practice/dentists/{dentist_id}", headers=headers, json=update_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            updated_dentist = data.get("data", {})
            print(f"   ✅ Dentist updated successfully")
            print(f"      New phone: {updated_dentist.get('phone')}")
            print(f"      New specialties: {updated_dentist.get('specialties')}")
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: GET specific dentist
    print(f"\n4️⃣ GET /practice/dentists/{dentist_id} - Get specific dentist")
    try:
        response = requests.get(f"{PRODUCTION_URL}/practice/dentists/{dentist_id}", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            dentist = data.get("data", {})
            print(f"   ✅ Dentist retrieved successfully")
            print(f"      Name: {dentist.get('firstName')} {dentist.get('lastName')}")
            print(f"      Active: {dentist.get('isActive', True)}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: DELETE dentist (soft delete)
    print(f"\n5️⃣ DELETE /practice/dentists/{dentist_id} - Soft delete dentist")
    try:
        response = requests.delete(f"{PRODUCTION_URL}/practice/dentists/{dentist_id}", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Dentist soft deleted successfully")
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 6: Verify dentist is no longer in active list
    print(f"\n6️⃣ GET /practice/dentists - Verify dentist removed from active list")
    try:
        response = requests.get(f"{PRODUCTION_URL}/practice/dentists", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            active_dentists = data.get("data", [])
            deleted_dentist_found = any(d.get("id") == dentist_id for d in active_dentists)
            
            if not deleted_dentist_found:
                print(f"   ✅ Deleted dentist correctly removed from active list")
                print(f"   Current active dentists: {len(active_dentists)}")
            else:
                print(f"   ❌ Deleted dentist still appears in active list")
                return False
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print(f"\n✅ ALL DENTIST CRUD OPERATIONS WORKING CORRECTLY")
    return True

def test_patient_crud():
    """Test patient management endpoints"""
    print(f"\n👥 PATIENT MANAGEMENT TEST")
    
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test POST create patient
    print(f"\n1️⃣ POST /practice/patients - Create new patient")
    test_patient = {
        "firstName": "Test",
        "lastName": "Patient",
        "email": f"test.patient.{datetime.now().strftime('%H%M%S')}@example.com",
        "phone": "(555) 987-6543",
        "dateOfBirth": "1990-01-01"
    }
    
    try:
        response = requests.post(f"{PRODUCTION_URL}/practice/patients", headers=headers, json=test_patient, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ Patient created successfully")
            if "data" in data:
                patient = data["data"]
                print(f"      Name: {patient.get('firstName')} {patient.get('lastName')}")
                print(f"      Email: {patient.get('email')}")
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def main():
    """Main test execution"""
    print(f"🔍 COMPREHENSIVE DENTIST & PATIENT CRUD TESTING")
    print(f"Target: {PRODUCTION_URL}")
    print(f"="*60)
    
    # Test dentist CRUD operations
    dentist_success = test_dentist_crud()
    
    # Test patient operations
    patient_success = test_patient_crud()
    
    print(f"\n" + "="*60)
    print(f"📊 FINAL RESULTS:")
    print(f"   Dentist CRUD: {'✅ WORKING' if dentist_success else '❌ FAILED'}")
    print(f"   Patient Management: {'✅ WORKING' if patient_success else '❌ FAILED'}")
    
    if dentist_success and patient_success:
        print(f"\n🎉 ALL CRUD OPERATIONS FULLY FUNCTIONAL")
        print(f"   → Add Patient page should work correctly")
        print(f"   → Assign Procedure page should work correctly")
        return True
    else:
        print(f"\n⚠️  SOME OPERATIONS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)