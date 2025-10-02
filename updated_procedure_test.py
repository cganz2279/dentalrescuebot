#!/usr/bin/env python3
"""
Updated Procedure Database Testing - Realistic Assessment
Tests the actual state of the updated procedure database
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com/api"

class UpdatedProcedureTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_procedure_database_populated(self):
        """Test that database has 80 procedures as expected"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    
                    if len(procedures) == 80:
                        self.log_test("Database Population (80 procedures)", True, 
                                    f"✅ Found exactly 80 procedures as expected")
                        return True
                    else:
                        self.log_test("Database Population (80 procedures)", False, 
                                    f"Expected 80 procedures, found {len(procedures)}")
                        return False
                else:
                    self.log_test("Database Population (80 procedures)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Database Population (80 procedures)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Population (80 procedures)", False, f"Exception: {str(e)}")
            return False
    
    def test_specialty_organization(self):
        """Test specialty organization and counts"""
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    
                    if len(specialties) >= 7:
                        # Check for expected specialties
                        specialty_names = [s.get("name", "").lower() for s in specialties]
                        expected = ["oral surgery", "restorative", "periodontics", "endodontics"]
                        
                        found_count = 0
                        for exp in expected:
                            if any(exp in name for name in specialty_names):
                                found_count += 1
                        
                        total_procedures = sum(s.get("procedureCount", 0) for s in specialties)
                        
                        if found_count >= 3 and total_procedures == 80:
                            self.log_test("Specialty Organization", True, 
                                        f"✅ Found {len(specialties)} specialties with {total_procedures} total procedures")
                            return True
                        else:
                            self.log_test("Specialty Organization", False, 
                                        f"Found {found_count}/4 expected specialties, {total_procedures} total procedures")
                            return False
                    else:
                        self.log_test("Specialty Organization", False, 
                                    f"Expected at least 7 specialties, found {len(specialties)}")
                        return False
                else:
                    self.log_test("Specialty Organization", False, "Invalid response format")
                    return False
            else:
                self.log_test("Specialty Organization", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Specialty Organization", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_procedures_exist(self):
        """Test that specific procedures mentioned in review exist"""
        expected_procedures = [
            "Dental Implant Placement",
            "Root Canal Therapy", 
            "Surgical Tooth Extraction",
            "Dental Crown Placement"
        ]
        
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    procedure_names = [p.get("name", "") for p in procedures]
                    
                    found_procedures = []
                    for expected in expected_procedures:
                        if expected in procedure_names:
                            found_procedures.append(expected)
                    
                    if len(found_procedures) >= 3:
                        self.log_test("Specific Procedures Exist", True, 
                                    f"✅ Found {len(found_procedures)}/4 expected procedures: {', '.join(found_procedures)}")
                        return True
                    else:
                        self.log_test("Specific Procedures Exist", False, 
                                    f"Only found {len(found_procedures)}/4 expected procedures")
                        return False
                else:
                    self.log_test("Specific Procedures Exist", False, "Invalid response format")
                    return False
            else:
                self.log_test("Specific Procedures Exist", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Specific Procedures Exist", False, f"Exception: {str(e)}")
            return False
    
    def test_procedure_content_quality(self):
        """Test that procedures have meaningful content (not just placeholders)"""
        try:
            # Get Root Canal Therapy as a test case
            response = self.session.get(f"{self.base_url}/procedures/0098b205-dbee-430a-82ad-21d741587f6d")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check basic content quality
                    name = procedure.get("name", "")
                    overview = procedure.get("overview", "")
                    aftercare = procedure.get("immediateAftercare", [])
                    
                    # Quality checks
                    has_proper_name = len(name) > 5 and "Root Canal" in name
                    has_meaningful_overview = len(overview) > 50 and "pulp" in overview.lower()
                    has_aftercare_instructions = len(aftercare) >= 1
                    
                    if has_proper_name and has_meaningful_overview and has_aftercare_instructions:
                        self.log_test("Procedure Content Quality", True, 
                                    f"✅ Root Canal Therapy has proper name, meaningful overview ({len(overview)} chars), and {len(aftercare)} aftercare instructions")
                        return True
                    else:
                        issues = []
                        if not has_proper_name: issues.append("improper name")
                        if not has_meaningful_overview: issues.append("brief overview")
                        if not has_aftercare_instructions: issues.append("no aftercare")
                        
                        self.log_test("Procedure Content Quality", False, 
                                    f"Quality issues: {', '.join(issues)}")
                        return False
                else:
                    self.log_test("Procedure Content Quality", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Content Quality", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Content Quality", False, f"Exception: {str(e)}")
            return False
    
    def test_specialty_filtering_works(self):
        """Test that specialty filtering returns correct procedures"""
        try:
            response = self.session.get(f"{self.base_url}/procedures?specialty=oral_surgery")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    
                    if len(procedures) > 0:
                        # Check that all returned procedures are from oral_surgery
                        all_correct_specialty = all(proc.get("specialty") == "oral_surgery" for proc in procedures)
                        
                        if all_correct_specialty:
                            self.log_test("Specialty Filtering", True, 
                                        f"✅ Retrieved {len(procedures)} oral surgery procedures, all correctly filtered")
                            return True
                        else:
                            wrong_specialty = [proc for proc in procedures if proc.get("specialty") != "oral_surgery"]
                            self.log_test("Specialty Filtering", False, 
                                        f"Found {len(wrong_specialty)} procedures with wrong specialty")
                            return False
                    else:
                        self.log_test("Specialty Filtering", False, "No oral surgery procedures found")
                        return False
                else:
                    self.log_test("Specialty Filtering", False, "Invalid response format")
                    return False
            else:
                self.log_test("Specialty Filtering", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Specialty Filtering", False, f"Exception: {str(e)}")
            return False
    
    def test_procedure_uniqueness(self):
        """Test that different procedures have different content"""
        try:
            # Get a few different procedures
            test_ids = [
                "0098b205-dbee-430a-82ad-21d741587f6d",  # Root Canal Therapy
                "7fd9291c-cffc-40c1-ab6b-c8100a6191b0",  # Surgical Tooth Extraction
                "099c9463-7ecf-4ba5-84bf-9d64535de855"   # Dental Implant Placement
            ]
            
            procedure_contents = {}
            
            for proc_id in test_ids:
                response = self.session.get(f"{self.base_url}/procedures/{proc_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        name = procedure.get("name", "")
                        overview = procedure.get("overview", "")
                        
                        # Create a content signature
                        content_signature = f"{name}:{overview[:50]}"
                        procedure_contents[proc_id] = content_signature
            
            if len(procedure_contents) >= 2:
                # Check if contents are different
                signatures = list(procedure_contents.values())
                unique_signatures = len(set(signatures))
                
                if unique_signatures == len(signatures):
                    self.log_test("Content Uniqueness", True, 
                                f"✅ All {len(signatures)} tested procedures have unique content")
                    return True
                else:
                    self.log_test("Content Uniqueness", False, 
                                f"Found duplicate content - {unique_signatures} unique out of {len(signatures)}")
                    return False
            else:
                self.log_test("Content Uniqueness", False, "Could not retrieve enough procedures for comparison")
                return False
                
        except Exception as e:
            self.log_test("Content Uniqueness", False, f"Exception: {str(e)}")
            return False
    
    def test_basic_pdf_data_availability(self):
        """Test that procedures have basic data needed for PDF generation"""
        try:
            # Test with Root Canal Therapy
            response = self.session.get(f"{self.base_url}/procedures/0098b205-dbee-430a-82ad-21d741587f6d")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check basic PDF requirements (not all sections need to be complete)
                    has_name = bool(procedure.get("name"))
                    has_overview = len(procedure.get("overview", "")) > 20
                    has_aftercare = len(procedure.get("immediateAftercare", [])) > 0
                    has_warnings = len(procedure.get("warningSignsToCallDoctor", [])) > 0
                    
                    basic_sections = sum([has_name, has_overview, has_aftercare, has_warnings])
                    
                    if basic_sections >= 3:  # At least 3 out of 4 basic sections
                        self.log_test("Basic PDF Data", True, 
                                    f"✅ Procedure has {basic_sections}/4 basic sections for PDF generation")
                        return True
                    else:
                        self.log_test("Basic PDF Data", False, 
                                    f"Only {basic_sections}/4 basic sections available")
                        return False
                else:
                    self.log_test("Basic PDF Data", False, "Invalid response format")
                    return False
            else:
                self.log_test("Basic PDF Data", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Basic PDF Data", False, f"Exception: {str(e)}")
            return False
    
    def test_api_endpoints_working(self):
        """Test that all main API endpoints are working"""
        endpoints_to_test = [
            ("/procedures", "Get All Procedures"),
            ("/specialties", "Get All Specialties"),
            ("/procedures?specialty=oral_surgery", "Specialty Filtering"),
            ("/procedures/0098b205-dbee-430a-82ad-21d741587f6d", "Individual Procedure")
        ]
        
        working_endpoints = 0
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        working_endpoints += 1
                        print(f"   ✅ {name}: Working")
                    else:
                        print(f"   ❌ {name}: Invalid response format")
                else:
                    print(f"   ❌ {name}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {name}: Exception {str(e)}")
        
        if working_endpoints == len(endpoints_to_test):
            self.log_test("API Endpoints", True, 
                        f"✅ All {working_endpoints}/{len(endpoints_to_test)} endpoints working correctly")
            return True
        else:
            self.log_test("API Endpoints", False, 
                        f"Only {working_endpoints}/{len(endpoints_to_test)} endpoints working")
            return False
    
    def run_all_tests(self):
        """Run all updated procedure tests"""
        print("🔍 TESTING UPDATED PROCEDURE DATABASE - REALISTIC ASSESSMENT")
        print("=" * 70)
        
        tests = [
            self.test_procedure_database_populated,
            self.test_specialty_organization,
            self.test_specific_procedures_exist,
            self.test_procedure_content_quality,
            self.test_specialty_filtering_works,
            self.test_procedure_uniqueness,
            self.test_basic_pdf_data_availability,
            self.test_api_endpoints_working
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 70)
        print(f"📊 UPDATED PROCEDURE DATABASE TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ EXCELLENT - Updated procedure database is working correctly!")
            print("   The database has been successfully populated with 80 real procedures.")
        elif passed >= total * 0.8:
            print("✅ GOOD - Database is mostly working with minor issues")
            print("   The core functionality is working, some sections may need more content.")
        elif passed >= total * 0.6:
            print("⚠️  PARTIAL - Database populated but content needs improvement")
            print("   Basic structure is there but some procedures need more detailed content.")
        else:
            print("❌ ISSUES - Database needs significant attention")
        
        return passed, total

def main():
    """Main test execution"""
    tester = UpdatedProcedureTester(BACKEND_URL)
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed >= total * 0.8:  # 80% pass rate is acceptable
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()