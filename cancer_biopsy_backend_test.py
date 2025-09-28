#!/usr/bin/env python3
"""
Cancer and Biopsy Procedure Categorization Fix Verification Test
Testing specific requirements from review request to verify procedures are properly categorized under Oral Surgery
"""

import requests
import json
import sys
from typing import List, Dict, Any

# Backend URL from frontend environment
BACKEND_URL = "https://oncallbot.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_get_all_procedures():
    """Test 1: Get all procedures and verify total count is 88"""
    print("🔍 TEST 1: Verifying total procedure count...")
    
    try:
        response = requests.get(f"{API_BASE}/procedures", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ FAILED: Expected 200, got {response.status_code}")
            return False, []
            
        data = response.json()
        procedures = data.get('data', [])
        total_count = len(procedures)
        
        print(f"   Total procedures found: {total_count}")
        
        if total_count != 88:
            print(f"   ❌ FAILED: Expected 88 procedures, found {total_count}")
            return False, procedures
        
        print(f"   ✅ PASSED: Found exactly 88 procedures as expected")
        return True, procedures
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, []

def test_specific_procedure_categorization(procedures: List[Dict]):
    """Test 2: Verify specific cancer/biopsy procedures are categorized as Oral Surgery"""
    print("\n🔍 TEST 2: Verifying specific procedure categorizations...")
    
    # Target procedures that should be categorized as "Oral Surgery"
    target_procedures = [
        "Biopsy of Oral Tissue",
        "Biopsy Oral Soft Tissue", 
        "Oral Biopsy",
        "Oral Cancer Screening FollowUp",
        "Oral Cancer Surgery"
    ]
    
    found_procedures = {}
    oral_surgery_procedures = []
    
    # Find target procedures and check their categorization
    for proc in procedures:
        name = proc.get('name', '')
        specialty = proc.get('specialty', '')
        specialty_name = proc.get('specialtyName', '')
        
        # Collect all oral surgery procedures
        if specialty == 'oral-surgery' or specialty_name == 'Oral Surgery':
            oral_surgery_procedures.append(proc)
        
        # Check if this is one of our target procedures
        if name in target_procedures:
            found_procedures[name] = {
                'specialty': specialty,
                'specialtyName': specialty_name,
                'id': proc.get('id', ''),
                'found': True
            }
    
    # Check results for each target procedure
    all_passed = True
    for target_name in target_procedures:
        if target_name in found_procedures:
            proc_info = found_procedures[target_name]
            specialty = proc_info['specialty']
            specialty_name = proc_info['specialtyName']
            
            if specialty == 'oral-surgery' or specialty_name == 'Oral Surgery':
                print(f"   ✅ {target_name}: Correctly categorized as '{specialty_name}' (ID: {proc_info['id']})")
            else:
                print(f"   ❌ {target_name}: Incorrectly categorized as '{specialty_name}' (should be Oral Surgery)")
                all_passed = False
        else:
            print(f"   ❌ {target_name}: Procedure not found in database")
            all_passed = False
    
    print(f"\n   Total Oral Surgery procedures found: {len(oral_surgery_procedures)}")
    
    if all_passed:
        print(f"   ✅ PASSED: All target procedures correctly categorized as Oral Surgery")
    else:
        print(f"   ❌ FAILED: Some procedures not properly categorized")
    
    return all_passed, oral_surgery_procedures

def test_search_by_specialty():
    """Test 3: Test procedures endpoint filtered by Oral Surgery specialty"""
    print("\n🔍 TEST 3: Testing search by Oral Surgery specialty...")
    
    try:
        response = requests.get(f"{API_BASE}/procedures?specialty=oral-surgery", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ FAILED: Expected 200, got {response.status_code}")
            return False, []
            
        data = response.json()
        oral_surgery_procedures = data.get('data', [])
        count = len(oral_surgery_procedures)
        
        print(f"   Oral Surgery procedures found: {count}")
        
        # Check that our target procedures are included
        target_procedures = [
            "Biopsy of Oral Tissue",
            "Biopsy Oral Soft Tissue", 
            "Oral Biopsy",
            "Oral Cancer Screening FollowUp",
            "Oral Cancer Surgery"
        ]
        
        found_targets = []
        for proc in oral_surgery_procedures:
            name = proc.get('name', '')
            if name in target_procedures:
                found_targets.append(name)
                print(f"   ✅ Found target procedure: {name}")
        
        missing_targets = [name for name in target_procedures if name not in found_targets]
        if missing_targets:
            print(f"   ❌ Missing target procedures: {missing_targets}")
            return False, oral_surgery_procedures
        
        print(f"   ✅ PASSED: All target procedures found in Oral Surgery specialty filter")
        return True, oral_surgery_procedures
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, []

def test_search_functionality():
    """Test 4: Test search functionality for biopsy and cancer terms"""
    print("\n🔍 TEST 4: Testing search functionality...")
    
    search_terms = ["biopsy", "cancer"]
    all_passed = True
    
    for term in search_terms:
        print(f"\n   Testing search for '{term}'...")
        
        try:
            response = requests.get(f"{API_BASE}/procedures/search?q={term}", timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ FAILED: Expected 200, got {response.status_code}")
                all_passed = False
                continue
                
            data = response.json()
            search_results = data.get('data', [])
            count = len(search_results)
            
            print(f"   Search results for '{term}': {count} procedures found")
            
            # Check that results contain procedures with the search term
            relevant_results = []
            for proc in search_results:
                name = proc.get('name', '').lower()
                specialty_name = proc.get('specialtyName', '')
                
                if term.lower() in name:
                    relevant_results.append(proc)
                    print(f"   ✅ Found: {proc.get('name')} (Specialty: {specialty_name})")
            
            if not relevant_results:
                print(f"   ❌ FAILED: No relevant results found for '{term}'")
                all_passed = False
            else:
                # Check that results show correct specialty (should be Oral Surgery)
                oral_surgery_count = 0
                for proc in relevant_results:
                    if proc.get('specialtyName') == 'Oral Surgery':
                        oral_surgery_count += 1
                
                print(f"   Procedures in Oral Surgery: {oral_surgery_count}/{len(relevant_results)}")
                
                if oral_surgery_count == 0:
                    print(f"   ❌ WARNING: No {term} procedures found in Oral Surgery specialty")
                else:
                    print(f"   ✅ Found {term} procedures in Oral Surgery specialty")
                    
        except Exception as e:
            print(f"   ❌ ERROR searching for '{term}': {str(e)}")
            all_passed = False
    
    if all_passed:
        print(f"\n   ✅ PASSED: Search functionality working correctly")
    else:
        print(f"\n   ❌ FAILED: Issues found with search functionality")
    
    return all_passed

def test_count_verification(oral_surgery_procedures: List[Dict]):
    """Test 5: Verify procedure counts"""
    print("\n🔍 TEST 5: Verifying procedure counts...")
    
    oral_surgery_count = len(oral_surgery_procedures)
    print(f"   Current Oral Surgery procedure count: {oral_surgery_count}")
    
    # According to the review request, Oral Surgery should have increased by 5 procedures
    # We need to check if the count makes sense
    target_procedures = [
        "Biopsy of Oral Tissue",
        "Biopsy Oral Soft Tissue", 
        "Oral Biopsy",
        "Oral Cancer Screening FollowUp",
        "Oral Cancer Surgery"
    ]
    
    found_target_count = 0
    for proc in oral_surgery_procedures:
        if proc.get('name') in target_procedures:
            found_target_count += 1
    
    print(f"   Target procedures found in Oral Surgery: {found_target_count}/5")
    
    if found_target_count == 5:
        print(f"   ✅ PASSED: All 5 target procedures found in Oral Surgery")
        return True
    else:
        print(f"   ❌ FAILED: Expected 5 target procedures, found {found_target_count}")
        return False

def main():
    """Run all cancer/biopsy categorization tests"""
    print("🧪 CANCER AND BIOPSY PROCEDURE CATEGORIZATION FIX VERIFICATION")
    print("=" * 80)
    print(f"Testing API at: {API_BASE}")
    print()
    
    # Test 1: Get all procedures and verify count
    test1_passed, all_procedures = test_get_all_procedures()
    
    if not test1_passed:
        print("\n❌ CRITICAL: Cannot proceed with other tests - procedure retrieval failed")
        return False
    
    # Test 2: Verify specific procedure categorizations
    test2_passed, oral_surgery_procedures = test_specific_procedure_categorization(all_procedures)
    
    # Test 3: Test search by specialty
    test3_passed, specialty_procedures = test_search_by_specialty()
    
    # Test 4: Test search functionality
    test4_passed = test_search_functionality()
    
    # Test 5: Verify counts
    test5_passed = test_count_verification(oral_surgery_procedures if oral_surgery_procedures else specialty_procedures)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY:")
    print(f"   Test 1 - Total Procedure Count (88): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Test 2 - Specific Categorizations: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   Test 3 - Search by Specialty: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print(f"   Test 4 - Search Functionality: {'✅ PASSED' if test4_passed else '❌ FAILED'}")
    print(f"   Test 5 - Count Verification: {'✅ PASSED' if test5_passed else '❌ FAILED'}")
    
    all_tests_passed = all([test1_passed, test2_passed, test3_passed, test4_passed, test5_passed])
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED: Cancer and biopsy procedure categorization fix is working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED: Issues found with cancer and biopsy procedure categorization")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)