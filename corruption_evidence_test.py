#!/usr/bin/env python3
"""
COMPREHENSIVE CORRUPTION EVIDENCE COLLECTION
Detailed testing to provide complete evidence of specialty corruption issue
"""

import requests
import json
from datetime import datetime

# The corrupted environment (what user sees)
CORRUPTED_URL = "https://dentist-dashboard-2.preview.emergentagent.com/api"
# The clean environment 
CLEAN_URL = "https://dentist-portal-3.emergent.host/api"

TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def get_detailed_specialty_breakdown(backend_url, env_name):
    """Get detailed breakdown of all specialties and their procedures"""
    print(f"\n📊 DETAILED SPECIALTY BREAKDOWN - {env_name}")
    print(f"URL: {backend_url}")
    print("=" * 80)
    
    try:
        # Get specialties
        response = requests.get(f"{backend_url}/specialties")
        if response.status_code != 200:
            print(f"❌ Failed to get specialties: {response.status_code}")
            return None
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ API error: {data}")
            return None
            
        specialties = data.get('data', [])
        print(f"Found {len(specialties)} specialties:")
        
        total_procedures = 0
        specialty_details = {}
        
        for specialty in specialties:
            name = specialty.get('name', 'Unknown')
            count = specialty.get('procedureCount', 0)
            specialty_id = specialty.get('id', 'Unknown')
            
            print(f"  • {name}: {count} procedures (ID: {specialty_id})")
            total_procedures += count
            
            specialty_details[name] = {
                'count': count,
                'id': specialty_id
            }
        
        print(f"\nTOTAL PROCEDURES: {total_procedures}")
        
        # Check for corruption pattern
        general_count = specialty_details.get('General Dentistry', {}).get('count', 0)
        if general_count >= 81:
            print("🚨 CORRUPTION PATTERN: All procedures in General Dentistry")
        elif general_count <= 10:
            print("✅ HEALTHY PATTERN: Procedures distributed across specialties")
        else:
            print("⚠️  UNUSUAL PATTERN: High General Dentistry count")
            
        return specialty_details
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_sample_procedures(backend_url, env_name):
    """Test a sample of procedures to show corruption evidence"""
    print(f"\n🔍 SAMPLE PROCEDURE TESTING - {env_name}")
    print("=" * 80)
    
    # Test procedures that should be in different specialties
    test_procedures = [
        {"id": "root-canal-therapy", "name": "Root Canal Therapy", "expected": "Endodontics"},
        {"id": "dental-implant-placement", "name": "Dental Implant Placement", "expected": "Oral Surgery"},
        {"id": "dental-crown-placement", "name": "Dental Crown Placement", "expected": "Prosthodontics"},
        {"id": "amalgam-fillings", "name": "Amalgam Fillings", "expected": "General Dentistry"},
        {"id": "periodontal-scaling", "name": "Periodontal Scaling", "expected": "Periodontics"}
    ]
    
    results = []
    
    for proc in test_procedures:
        try:
            response = requests.get(f"{backend_url}/procedures/{proc['id']}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    procedure = data.get('data', {})
                    actual_specialty = procedure.get('specialtyName', 'Unknown')
                    
                    is_correct = actual_specialty == proc['expected']
                    status = "✅" if is_correct else "❌"
                    
                    print(f"  {status} {proc['name']}")
                    print(f"      Expected: {proc['expected']}")
                    print(f"      Actual:   {actual_specialty}")
                    
                    if not is_correct:
                        print(f"      🚨 CORRUPTION: Should be {proc['expected']}, shows as {actual_specialty}")
                    
                    results.append({
                        'name': proc['name'],
                        'expected': proc['expected'],
                        'actual': actual_specialty,
                        'correct': is_correct
                    })
                else:
                    print(f"  ❌ {proc['name']}: API error")
            else:
                print(f"  ❌ {proc['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {proc['name']}: Error - {str(e)}")
    
    # Summary for this environment
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    
    print(f"\nSUMMARY: {correct_count}/{total_count} procedures have correct specialties")
    
    if correct_count == total_count:
        print("✅ All tested procedures have correct specialties")
    elif correct_count == 0:
        print("🚨 ALL tested procedures have WRONG specialties")
    else:
        print("⚠️  PARTIAL corruption detected")
    
    return results

def main():
    """Main evidence collection"""
    print("🚨 COMPREHENSIVE SPECIALTY CORRUPTION EVIDENCE COLLECTION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Test Credentials: {TEST_EMAIL}")
    print("=" * 80)
    
    # Test both environments
    print("\n🌐 TESTING CORRUPTED ENVIRONMENT (What user sees)")
    corrupted_specialties = get_detailed_specialty_breakdown(CORRUPTED_URL, "CORRUPTED")
    corrupted_procedures = test_sample_procedures(CORRUPTED_URL, "CORRUPTED")
    
    print("\n🌐 TESTING CLEAN ENVIRONMENT (Correct data)")
    clean_specialties = get_detailed_specialty_breakdown(CLEAN_URL, "CLEAN")
    clean_procedures = test_sample_procedures(CLEAN_URL, "CLEAN")
    
    # Generate evidence report
    print("\n" + "=" * 80)
    print("🎯 CORRUPTION EVIDENCE REPORT")
    print("=" * 80)
    
    if corrupted_specialties and clean_specialties:
        corrupted_general = corrupted_specialties.get('General Dentistry', {}).get('count', 0)
        clean_general = clean_specialties.get('General Dentistry', {}).get('count', 0)
        
        print(f"\nGENERAL DENTISTRY PROCEDURE COUNT:")
        print(f"  Corrupted Environment: {corrupted_general} procedures")
        print(f"  Clean Environment:     {clean_general} procedures")
        
        if corrupted_general >= 81 and clean_general <= 10:
            print(f"\n🚨 CORRUPTION CONFIRMED:")
            print(f"  • User sees ALL {corrupted_general} procedures in General Dentistry")
            print(f"  • Clean database has only {clean_general} procedures in General Dentistry")
            print(f"  • This is a {corrupted_general - clean_general} procedure corruption!")
        
        print(f"\nFRONTEND CONFIGURATION ISSUE:")
        print(f"  • Frontend .env points to: {CORRUPTED_URL}")
        print(f"  • This backend has corrupted specialty assignments")
        print(f"  • Clean data exists at: {CLEAN_URL}")
        print(f"  • User cannot access clean data due to frontend configuration")
    
    # Procedure-level evidence
    if corrupted_procedures and clean_procedures:
        print(f"\nPROCEDURE-LEVEL CORRUPTION EVIDENCE:")
        
        for i, proc in enumerate(corrupted_procedures):
            if i < len(clean_procedures):
                clean_proc = clean_procedures[i]
                if proc['name'] == clean_proc['name']:
                    if not proc['correct'] and clean_proc['correct']:
                        print(f"  🚨 {proc['name']}:")
                        print(f"      User sees: {proc['actual']} (WRONG)")
                        print(f"      Should be: {proc['expected']} (available in clean DB)")
    
    # Final recommendation
    print(f"\n" + "=" * 80)
    print("🎯 IMMEDIATE ACTION REQUIRED")
    print("=" * 80)
    print("1. 🔧 QUICK FIX: Update frontend/.env REACT_APP_BACKEND_URL")
    print(f"   FROM: {CORRUPTED_URL}")
    print(f"   TO:   {CLEAN_URL}")
    print("")
    print("2. 🔄 LONG-TERM: Synchronize databases to prevent future discrepancies")
    print("")
    print("3. ✅ VERIFICATION: User will immediately see correct specialties after frontend update")
    print("=" * 80)

if __name__ == "__main__":
    main()