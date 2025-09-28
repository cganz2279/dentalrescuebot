#!/usr/bin/env python3
"""
Comprehensive Procedure Categorization and Cleanup Verification Test
Testing the comprehensive categorization and cleanup that should result in exactly 82 procedures
"""

import requests
import json
from typing import List, Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://oncallbot.preview.emergentagent.com/api"

def test_total_procedure_count():
    """Test 1: Verify total count is exactly 82 procedures (down from 88 after cleanup)"""
    print("🔍 TEST 1: Verifying total procedure count is exactly 82...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/procedures", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            procedures = data.get('data', [])
            total_count = len(procedures)
            
            print(f"   ✅ Total procedures found: {total_count}")
            
            if total_count == 82:
                print("   ✅ PASS: Total count is exactly 82 procedures as expected")
                return True, procedures
            else:
                print(f"   ❌ FAIL: Expected 82 procedures, but found {total_count}")
                return False, procedures
        else:
            print(f"   ❌ FAIL: API request failed with status {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, []

def test_orthodontics_categorization(procedures: List[Dict]):
    """Test 2: Verify procedures with 'orthodontics' or 'ortho' are properly categorized"""
    print("\n🔍 TEST 2: Testing Orthodontics categorization...")
    
    orthodontic_procedures = []
    surgical_orthodontics = []
    
    for proc in procedures:
        name = proc.get('name', '').lower()
        specialty = proc.get('specialty', '')
        specialty_name = proc.get('specialtyName', '')
        
        if 'orthodontic' in name or 'ortho' in name:
            if 'surgical orthodontics' in name:
                surgical_orthodontics.append({
                    'name': proc.get('name'),
                    'specialty': specialty,
                    'specialtyName': specialty_name
                })
            else:
                orthodontic_procedures.append({
                    'name': proc.get('name'),
                    'specialty': specialty,
                    'specialtyName': specialty_name
                })
    
    print(f"   Found {len(orthodontic_procedures)} orthodontic procedures:")
    orthodontics_pass = True
    
    for proc in orthodontic_procedures:
        expected_specialty = 'orthodontics'
        if proc['specialty'] == expected_specialty:
            print(f"   ✅ '{proc['name']}' -> {proc['specialtyName']} (correct)")
        else:
            print(f"   ❌ '{proc['name']}' -> {proc['specialtyName']} (should be Orthodontics)")
            orthodontics_pass = False
    
    print(f"   Found {len(surgical_orthodontics)} surgical orthodontics procedures:")
    for proc in surgical_orthodontics:
        print(f"   ℹ️  '{proc['name']}' -> {proc['specialtyName']} (should remain as is - surgical)")
    
    if orthodontics_pass:
        print("   ✅ PASS: Orthodontics categorization is correct")
    else:
        print("   ❌ FAIL: Some orthodontic procedures are miscategorized")
    
    return orthodontics_pass

def test_oral_surgery_categorization(procedures: List[Dict]):
    """Test 3: Verify specific procedures are under Oral Surgery"""
    print("\n🔍 TEST 3: Testing Oral Surgery categorization...")
    
    target_keywords = [
        'orthognathic',
        'osseous surgery',
        'sinus perforation repair',
        'tmj',
        'vestibuloplasty'
    ]
    
    oral_surgery_procedures = []
    vestibuloplasty_count = 0
    
    for proc in procedures:
        name = proc.get('name', '').lower()
        specialty = proc.get('specialty', '')
        specialty_name = proc.get('specialtyName', '')
        
        for keyword in target_keywords:
            if keyword in name:
                oral_surgery_procedures.append({
                    'name': proc.get('name'),
                    'specialty': specialty,
                    'specialtyName': specialty_name,
                    'keyword': keyword
                })
                
                if keyword == 'vestibuloplasty':
                    vestibuloplasty_count += 1
                break
    
    print(f"   Found {len(oral_surgery_procedures)} target oral surgery procedures:")
    oral_surgery_pass = True
    
    for proc in oral_surgery_procedures:
        expected_specialty = 'oral-surgery'
        if proc['specialty'] == expected_specialty:
            print(f"   ✅ '{proc['name']}' -> {proc['specialtyName']} (correct)")
        else:
            print(f"   ❌ '{proc['name']}' -> {proc['specialtyName']} (should be Oral Surgery)")
            oral_surgery_pass = False
    
    # Check Vestibuloplasty duplicates
    print(f"   Vestibuloplasty count: {vestibuloplasty_count}")
    if vestibuloplasty_count == 1:
        print("   ✅ PASS: Only ONE Vestibuloplasty procedure exists (duplicates removed)")
    else:
        print(f"   ❌ FAIL: Found {vestibuloplasty_count} Vestibuloplasty procedures (should be 1)")
        oral_surgery_pass = False
    
    if oral_surgery_pass:
        print("   ✅ PASS: Oral Surgery categorization is correct")
    else:
        print("   ❌ FAIL: Some oral surgery procedures are miscategorized")
    
    return oral_surgery_pass

def test_periodontics_categorization(procedures: List[Dict]):
    """Test 4: Verify Ridge and Socket Preservation procedures are under Periodontics"""
    print("\n🔍 TEST 4: Testing Periodontics categorization...")
    
    target_keywords = ['ridge', 'socket preservation']
    periodontics_procedures = []
    
    for proc in procedures:
        name = proc.get('name', '').lower()
        specialty = proc.get('specialty', '')
        specialty_name = proc.get('specialtyName', '')
        
        for keyword in target_keywords:
            if keyword in name:
                periodontics_procedures.append({
                    'name': proc.get('name'),
                    'specialty': specialty,
                    'specialtyName': specialty_name,
                    'keyword': keyword
                })
                break
    
    print(f"   Found {len(periodontics_procedures)} target periodontics procedures:")
    periodontics_pass = True
    
    for proc in periodontics_procedures:
        expected_specialty = 'periodontics'
        if proc['specialty'] == expected_specialty:
            print(f"   ✅ '{proc['name']}' -> {proc['specialtyName']} (correct)")
        else:
            print(f"   ❌ '{proc['name']}' -> {proc['specialtyName']} (should be Periodontics)")
            periodontics_pass = False
    
    if periodontics_pass:
        print("   ✅ PASS: Periodontics categorization is correct")
    else:
        print("   ❌ FAIL: Some periodontics procedures are miscategorized")
    
    return periodontics_pass

def test_cleanup_verification(procedures: List[Dict]):
    """Test 5: Verify cleanup - no duplicates, no blank procedures, no test procedures"""
    print("\n🔍 TEST 5: Testing cleanup verification...")
    
    # Check for blank procedures
    blank_procedures = []
    test_procedures = []
    duplicate_names = {}
    
    for proc in procedures:
        name = proc.get('name', '').strip()
        
        # Check for blank names
        if not name:
            blank_procedures.append(proc)
        
        # Check for test procedures
        if 'test' in name.lower():
            test_procedures.append(proc)
        
        # Check for duplicates
        if name in duplicate_names:
            duplicate_names[name] += 1
        else:
            duplicate_names[name] = 1
    
    # Find actual duplicates
    duplicates = {name: count for name, count in duplicate_names.items() if count > 1}
    
    cleanup_pass = True
    
    print(f"   Blank procedures found: {len(blank_procedures)}")
    if len(blank_procedures) == 0:
        print("   ✅ PASS: No blank procedures found")
    else:
        print("   ❌ FAIL: Found blank procedures")
        cleanup_pass = False
        for proc in blank_procedures:
            print(f"      - Blank procedure: {proc}")
    
    print(f"   Test procedures found: {len(test_procedures)}")
    if len(test_procedures) == 0:
        print("   ✅ PASS: No test procedures found")
    else:
        print("   ❌ FAIL: Found test procedures")
        cleanup_pass = False
        for proc in test_procedures:
            print(f"      - Test procedure: {proc['name']}")
    
    print(f"   Duplicate procedures found: {len(duplicates)}")
    if len(duplicates) == 0:
        print("   ✅ PASS: No duplicate procedures found")
    else:
        print("   ❌ FAIL: Found duplicate procedures")
        cleanup_pass = False
        for name, count in duplicates.items():
            print(f"      - '{name}' appears {count} times")
    
    if cleanup_pass:
        print("   ✅ PASS: Cleanup verification successful")
    else:
        print("   ❌ FAIL: Cleanup issues found")
    
    return cleanup_pass

def test_specialty_counts(procedures: List[Dict]):
    """Test 6: Verify specialty distribution makes sense"""
    print("\n🔍 TEST 6: Testing specialty counts...")
    
    specialty_counts = {}
    
    for proc in procedures:
        specialty_name = proc.get('specialtyName', 'Unknown')
        if specialty_name in specialty_counts:
            specialty_counts[specialty_name] += 1
        else:
            specialty_counts[specialty_name] = 1
    
    print("   Specialty distribution:")
    total_counted = 0
    oral_surgery_count = 0
    
    for specialty, count in sorted(specialty_counts.items()):
        print(f"   - {specialty}: {count} procedures")
        total_counted += count
        if specialty == 'Oral Surgery':
            oral_surgery_count = count
    
    print(f"   Total counted: {total_counted}")
    
    counts_pass = True
    
    # Check if Oral Surgery has around 33 procedures
    if oral_surgery_count >= 30 and oral_surgery_count <= 35:
        print(f"   ✅ PASS: Oral Surgery has {oral_surgery_count} procedures (expected around 33)")
    else:
        print(f"   ❌ FAIL: Oral Surgery has {oral_surgery_count} procedures (expected around 33)")
        counts_pass = False
    
    # Check total is exactly 82
    if total_counted == 82:
        print("   ✅ PASS: Total specialty count matches 82 procedures")
    else:
        print(f"   ❌ FAIL: Total specialty count is {total_counted} (expected 82)")
        counts_pass = False
    
    if counts_pass:
        print("   ✅ PASS: Specialty counts are reasonable")
    else:
        print("   ❌ FAIL: Specialty count issues found")
    
    return counts_pass

def run_comprehensive_categorization_test():
    """Run all comprehensive categorization and cleanup tests"""
    print("🚀 COMPREHENSIVE PROCEDURE CATEGORIZATION AND CLEANUP VERIFICATION")
    print("=" * 80)
    
    # Test 1: Total count
    count_pass, procedures = test_total_procedure_count()
    
    if not procedures:
        print("\n❌ CRITICAL FAILURE: Could not retrieve procedures. Stopping tests.")
        return False
    
    # Test 2: Orthodontics categorization
    orthodontics_pass = test_orthodontics_categorization(procedures)
    
    # Test 3: Oral Surgery categorization
    oral_surgery_pass = test_oral_surgery_categorization(procedures)
    
    # Test 4: Periodontics categorization
    periodontics_pass = test_periodontics_categorization(procedures)
    
    # Test 5: Cleanup verification
    cleanup_pass = test_cleanup_verification(procedures)
    
    # Test 6: Specialty counts
    counts_pass = test_specialty_counts(procedures)
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 80)
    
    all_tests = [
        ("Total Count (82 procedures)", count_pass),
        ("Orthodontics Categorization", orthodontics_pass),
        ("Oral Surgery Categorization", oral_surgery_pass),
        ("Periodontics Categorization", periodontics_pass),
        ("Cleanup Verification", cleanup_pass),
        ("Specialty Counts", counts_pass)
    ]
    
    passed_tests = 0
    for test_name, passed in all_tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if passed:
            passed_tests += 1
    
    print(f"\n📈 OVERALL RESULT: {passed_tests}/{len(all_tests)} tests passed")
    
    if passed_tests == len(all_tests):
        print("🎉 ALL TESTS PASSED: Comprehensive categorization and cleanup successful!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED: Issues found in categorization or cleanup")
        return False

if __name__ == "__main__":
    success = run_comprehensive_categorization_test()
    exit(0 if success else 1)