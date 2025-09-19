#!/usr/bin/env python3
"""
URGENT SPECIALTY ASSIGNMENT CHECK
Testing specialty distribution and procedure assignments as requested in review.
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
LOGIN_EMAIL = "cganz2279@gmail.com"
LOGIN_PASSWORD = "password123"

def authenticate():
    """Authenticate and get JWT token"""
    print("🔐 Authenticating with backend...")
    
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("✅ Authentication successful")
                return token
            else:
                print("❌ No access token in response")
                print(f"Response: {data}")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_specialty_distribution(token):
    """Test 1: Check specialty distribution and procedure counts"""
    print("\n" + "="*60)
    print("TEST 1: SPECIALTY DISTRIBUTION")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/specialties", headers=headers)
        print(f"GET /api/specialties - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                specialties = data["data"]
                print(f"\n📊 SPECIALTY PROCEDURE COUNTS:")
                print("-" * 40)
                
                total_procedures = 0
                for specialty in specialties:
                    name = specialty.get("name", "Unknown")
                    count = specialty.get("procedureCount", 0)
                    specialty_id = specialty.get("id", "Unknown")
                    print(f"• {name}: {count} procedures (ID: {specialty_id})")
                    total_procedures += count
                
                print(f"\nTotal procedures across all specialties: {total_procedures}")
                
                # Check if all procedures are in General Dentistry
                general_dentistry = next((s for s in specialties if "general" in s.get("name", "").lower()), None)
                if general_dentistry:
                    general_count = general_dentistry.get("procedureCount", 0)
                    if general_count == total_procedures and total_procedures > 10:
                        print("🚨 CRITICAL ISSUE: All procedures appear to be in General Dentistry!")
                    elif general_count > total_procedures * 0.8:
                        print("⚠️  WARNING: Most procedures are in General Dentistry - possible specialty assignment issue")
                
                return specialties
            else:
                print(f"❌ Invalid response format: {data}")
                return None
        else:
            print(f"❌ Failed to get specialties: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing specialties: {str(e)}")
        return None

def test_specific_procedures(token):
    """Test 2: Check specific procedure specialty assignments"""
    print("\n" + "="*60)
    print("TEST 2: SPECIFIC PROCEDURE SPECIALTY ASSIGNMENTS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    test_procedures = [
        {
            "id": "root-canal-therapy",
            "name": "Root Canal Therapy",
            "expected_specialty": "Endodontics"
        },
        {
            "id": "dental-implant-placement", 
            "name": "Dental Implant Placement",
            "expected_specialty": "Oral Surgery"
        },
        {
            "id": "wisdom-tooth-removal",
            "name": "Wisdom Tooth Removal", 
            "expected_specialty": "Oral Surgery"
        }
    ]
    
    results = []
    
    for procedure in test_procedures:
        print(f"\n🔍 Testing: {procedure['name']}")
        print("-" * 30)
        
        try:
            response = requests.get(f"{BACKEND_URL}/procedures/{procedure['id']}", headers=headers)
            print(f"GET /api/procedures/{procedure['id']} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    proc_data = data["data"]
                    actual_specialty = proc_data.get("specialtyName", "Unknown")
                    specialty_id = proc_data.get("specialty", "Unknown")
                    
                    print(f"• Actual Specialty: {actual_specialty}")
                    print(f"• Expected Specialty: {procedure['expected_specialty']}")
                    print(f"• Specialty ID: {specialty_id}")
                    
                    if actual_specialty.lower() == procedure['expected_specialty'].lower():
                        print("✅ CORRECT specialty assignment")
                        status = "CORRECT"
                    elif "general" in actual_specialty.lower():
                        print("❌ INCORRECT: Shows as General Dentistry")
                        status = "GENERAL_DENTISTRY_ERROR"
                    else:
                        print(f"⚠️  UNEXPECTED: Shows as {actual_specialty}")
                        status = "UNEXPECTED"
                    
                    results.append({
                        "procedure": procedure['name'],
                        "expected": procedure['expected_specialty'],
                        "actual": actual_specialty,
                        "status": status
                    })
                    
                    # For root canal, also check overview content
                    if procedure['id'] == 'root-canal-therapy':
                        overview = proc_data.get("overview", "")
                        print(f"\n📄 Root Canal Overview (first 200 chars):")
                        print(f"'{overview[:200]}{'...' if len(overview) > 200 else ''}'")
                        
                else:
                    print(f"❌ Invalid response format: {data}")
                    results.append({
                        "procedure": procedure['name'],
                        "expected": procedure['expected_specialty'],
                        "actual": "ERROR - Invalid response",
                        "status": "ERROR"
                    })
            else:
                print(f"❌ Failed to get procedure: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    "procedure": procedure['name'],
                    "expected": procedure['expected_specialty'],
                    "actual": f"ERROR - {response.status_code}",
                    "status": "ERROR"
                })
                
        except Exception as e:
            print(f"❌ Error testing {procedure['name']}: {str(e)}")
            results.append({
                "procedure": procedure['name'],
                "expected": procedure['expected_specialty'],
                "actual": f"ERROR - {str(e)}",
                "status": "ERROR"
            })
    
    return results

def print_summary(specialty_data, procedure_results):
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("🎯 SPECIALTY ASSIGNMENT TEST SUMMARY")
    print("="*60)
    
    if specialty_data:
        print("\n📊 SPECIALTY DISTRIBUTION:")
        for specialty in specialty_data:
            name = specialty.get("name", "Unknown")
            count = specialty.get("procedureCount", 0)
            print(f"  • {name}: {count} procedures")
    
    print("\n🔍 PROCEDURE SPECIALTY ASSIGNMENTS:")
    correct_count = 0
    general_dentistry_errors = 0
    
    for result in procedure_results:
        status_icon = "✅" if result["status"] == "CORRECT" else "❌"
        print(f"  {status_icon} {result['procedure']}")
        print(f"     Expected: {result['expected']}")
        print(f"     Actual: {result['actual']}")
        
        if result["status"] == "CORRECT":
            correct_count += 1
        elif result["status"] == "GENERAL_DENTISTRY_ERROR":
            general_dentistry_errors += 1
    
    print(f"\n📈 RESULTS:")
    print(f"  • Correct assignments: {correct_count}/{len(procedure_results)}")
    print(f"  • General Dentistry errors: {general_dentistry_errors}/{len(procedure_results)}")
    
    if general_dentistry_errors > 0:
        print(f"\n🚨 CRITICAL ISSUE CONFIRMED:")
        print(f"   {general_dentistry_errors} procedures incorrectly assigned to General Dentistry")
        print(f"   This matches the user's report - specialty assignments are corrupted!")
    elif correct_count == len(procedure_results):
        print(f"\n✅ ALL SPECIALTY ASSIGNMENTS CORRECT")
        print(f"   No issues found - specialties are properly assigned")
    else:
        print(f"\n⚠️  MIXED RESULTS - Some assignments incorrect but not all General Dentistry")

def main():
    """Main test execution"""
    print("🚨 URGENT SPECIALTY ASSIGNMENT CHECK")
    print("Testing procedure specialty distribution as reported by user")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Login: {LOGIN_EMAIL}")
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Step 2: Test specialty distribution
    specialty_data = test_specialty_distribution(token)
    
    # Step 3: Test specific procedures
    procedure_results = test_specific_procedures(token)
    
    # Step 4: Print summary
    print_summary(specialty_data, procedure_results)
    
    print(f"\n🏁 Testing completed!")

if __name__ == "__main__":
    main()