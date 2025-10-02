#!/usr/bin/env python3
"""
PDF Import Fix Verification Test
Tests the specific fix for missing procedures: All On X and Final Zirconia
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Use the production URL from frontend/.env
BASE_URL = "https://aftercareportal.preview.emergentagent.com/api"

class PDFImportFixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        
    def log_result(self, test_name: str, passed: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
    def test_procedure_count(self) -> bool:
        """Test 1: Verify procedure count is now 88"""
        print("\n🔍 TEST 1: Verifying procedure count is 88...")
        
        try:
            response = requests.get(f"{self.base_url}/procedures", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Procedure Count Test", False, f"API returned {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_result("Procedure Count Test", False, f"API returned success=false: {data}")
                return False
                
            procedures = data.get("data", [])
            count = len(procedures)
            
            if count == 88:
                self.log_result("Procedure Count Test", True, f"Found exactly 88 procedures (increased from 86)")
                return True
            else:
                self.log_result("Procedure Count Test", False, f"Found {count} procedures, expected 88")
                return False
                
        except Exception as e:
            self.log_result("Procedure Count Test", False, f"Exception: {str(e)}")
            return False
    
    def test_search_all_on_x(self) -> bool:
        """Test 2: Search for 'All On X' procedure"""
        print("\n🔍 TEST 2: Searching for 'All On X' procedure...")
        
        try:
            response = requests.get(f"{self.base_url}/procedures/search?q=All On X", timeout=10)
            
            if response.status_code != 200:
                self.log_result("All On X Search Test", False, f"API returned {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_result("All On X Search Test", False, f"API returned success=false: {data}")
                return False
                
            procedures = data.get("data", [])
            
            # Look for "All On X Post Op Instructions"
            target_found = False
            for proc in procedures:
                if "All On X" in proc.get("name", "") and "Post Op Instructions" in proc.get("name", ""):
                    target_found = True
                    self.log_result("All On X Search Test", True, f"Found 'All On X Post Op Instructions' procedure: {proc.get('name')}")
                    return True
            
            if not target_found:
                found_names = [proc.get("name", "Unknown") for proc in procedures]
                self.log_result("All On X Search Test", False, f"'All On X Post Op Instructions' not found. Found: {found_names}")
                return False
                
        except Exception as e:
            self.log_result("All On X Search Test", False, f"Exception: {str(e)}")
            return False
    
    def test_search_zirconia(self) -> bool:
        """Test 3: Search for 'zirconia' procedure"""
        print("\n🔍 TEST 3: Searching for 'zirconia' procedure...")
        
        try:
            response = requests.get(f"{self.base_url}/procedures/search?q=zirconia", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Zirconia Search Test", False, f"API returned {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_result("Zirconia Search Test", False, f"API returned success=false: {data}")
                return False
                
            procedures = data.get("data", [])
            
            # Look for "Final Zirconia Implant Prosthesis Post Op Instructions"
            target_found = False
            for proc in procedures:
                if "Zirconia" in proc.get("name", "") and "Final" in proc.get("name", "") and "Implant Prosthesis" in proc.get("name", ""):
                    target_found = True
                    self.log_result("Zirconia Search Test", True, f"Found 'Final Zirconia Implant Prosthesis Post Op Instructions' procedure: {proc.get('name')}")
                    return True
            
            if not target_found:
                found_names = [proc.get("name", "Unknown") for proc in procedures]
                self.log_result("Zirconia Search Test", False, f"'Final Zirconia Implant Prosthesis Post Op Instructions' not found. Found: {found_names}")
                return False
                
        except Exception as e:
            self.log_result("Zirconia Search Test", False, f"Exception: {str(e)}")
            return False
    
    def test_search_final_zirconia(self) -> bool:
        """Test 4: Search for 'final zirconia' procedure"""
        print("\n🔍 TEST 4: Searching for 'final zirconia' procedure...")
        
        try:
            response = requests.get(f"{self.base_url}/procedures/search?q=final zirconia", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Final Zirconia Search Test", False, f"API returned {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_result("Final Zirconia Search Test", False, f"API returned success=false: {data}")
                return False
                
            procedures = data.get("data", [])
            
            # Look for the zirconia procedure
            target_found = False
            for proc in procedures:
                if "Final" in proc.get("name", "") and "Zirconia" in proc.get("name", ""):
                    target_found = True
                    self.log_result("Final Zirconia Search Test", True, f"Found procedure with 'Final Zirconia': {proc.get('name')}")
                    return True
            
            if not target_found:
                found_names = [proc.get("name", "Unknown") for proc in procedures]
                self.log_result("Final Zirconia Search Test", False, f"No procedure with 'Final Zirconia' found. Found: {found_names}")
                return False
                
        except Exception as e:
            self.log_result("Final Zirconia Search Test", False, f"Exception: {str(e)}")
            return False
    
    def test_case_sensitivity(self) -> bool:
        """Test 5: Verify case insensitive searches work"""
        print("\n🔍 TEST 5: Testing case sensitivity...")
        
        test_cases = [
            ("all on x", "lowercase"),
            ("ZIRCONIA", "uppercase"), 
            ("All On X", "mixed case")
        ]
        
        all_passed = True
        
        for search_term, case_type in test_cases:
            try:
                response = requests.get(f"{self.base_url}/procedures/search?q={search_term}", timeout=10)
                
                if response.status_code != 200:
                    self.log_result(f"Case Sensitivity Test ({case_type})", False, f"API returned {response.status_code}")
                    all_passed = False
                    continue
                    
                data = response.json()
                
                if not data.get("success"):
                    self.log_result(f"Case Sensitivity Test ({case_type})", False, f"API returned success=false")
                    all_passed = False
                    continue
                    
                procedures = data.get("data", [])
                
                if len(procedures) > 0:
                    self.log_result(f"Case Sensitivity Test ({case_type})", True, f"Found {len(procedures)} results for '{search_term}'")
                else:
                    self.log_result(f"Case Sensitivity Test ({case_type})", False, f"No results found for '{search_term}'")
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Case Sensitivity Test ({case_type})", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def verify_procedure_details(self) -> bool:
        """Test 6: Verify procedure details for new procedures"""
        print("\n🔍 TEST 6: Verifying procedure details...")
        
        # First get all procedures to find the target ones
        try:
            response = requests.get(f"{self.base_url}/procedures", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Procedure Details Test", False, f"Failed to get procedures: {response.status_code}")
                return False
                
            data = response.json()
            procedures = data.get("data", [])
            
            target_procedures = []
            for proc in procedures:
                name = proc.get("name", "")
                if ("All On X" in name and "Post Op Instructions" in name) or \
                   ("Final" in name and "Zirconia" in name and "Implant Prosthesis" in name):
                    target_procedures.append(proc)
            
            if len(target_procedures) == 0:
                self.log_result("Procedure Details Test", False, "No target procedures found in database")
                return False
            
            all_valid = True
            
            for proc in target_procedures:
                proc_name = proc.get("name", "Unknown")
                proc_id = proc.get("id")
                
                # Check required fields
                if not proc.get("overview") or len(proc.get("overview", "").strip()) == 0:
                    self.log_result("Procedure Details Test", False, f"{proc_name}: Missing or empty overview")
                    all_valid = False
                    continue
                
                specialty = proc.get("specialty", "").lower()
                if specialty != "prosthodontics":
                    self.log_result("Procedure Details Test", False, f"{proc_name}: Expected specialty 'prosthodontics', got '{proc.get('specialty')}'")
                    all_valid = False
                    continue
                
                if not proc_id:
                    self.log_result("Procedure Details Test", False, f"{proc_name}: Missing procedure ID")
                    all_valid = False
                    continue
                
                self.log_result("Procedure Details Test", True, f"{proc_name}: Has proper content, specialty=prosthodontics, ID={proc_id}")
            
            return all_valid
            
        except Exception as e:
            self.log_result("Procedure Details Test", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all PDF import fix tests"""
        print("🚀 STARTING PDF IMPORT FIX VERIFICATION TESTS")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        tests = [
            self.test_procedure_count,
            self.test_search_all_on_x,
            self.test_search_zirconia,
            self.test_search_final_zirconia,
            self.test_case_sensitivity,
            self.verify_procedure_details
        ]
        
        passed_count = 0
        total_count = len(tests)
        
        for test in tests:
            if test():
                passed_count += 1
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("🎉 ALL TESTS PASSED - PDF import fix is working correctly!")
            return True
        else:
            print("❌ SOME TESTS FAILED - PDF import fix needs attention")
            return False

def main():
    tester = PDFImportFixTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()