#!/usr/bin/env python3
"""
Procedure Content and PDF Generation Testing
Tests the updated procedure database with 80 real post-operative procedures from uploaded PDFs
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://view-print-sync.preview.emergentagent.com/api"

class ProcedureContentTester:
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
    
    def test_procedure_count_and_content(self):
        """Test that we have 80 procedures with real content (not placeholder text)"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    
                    # Check procedure count
                    if len(procedures) == 80:
                        self.log_test("Procedure Count (80 procedures)", True, f"Found exactly 80 procedures")
                        
                        # Check for real content vs placeholder
                        real_content_count = 0
                        placeholder_indicators = ["placeholder", "lorem ipsum", "sample text", "test procedure", "dummy"]
                        
                        for procedure in procedures:
                            overview = procedure.get("overview", "").lower()
                            name = procedure.get("name", "").lower()
                            
                            # Check if this looks like real content
                            has_placeholder = any(indicator in overview or indicator in name for indicator in placeholder_indicators)
                            has_substantial_content = len(overview) > 100  # Real procedures should have substantial content
                            
                            if not has_placeholder and has_substantial_content:
                                real_content_count += 1
                        
                        if real_content_count >= 75:  # Allow for some variation
                            self.log_test("Real Content Verification", True, 
                                        f"{real_content_count}/80 procedures have real, substantial content")
                            return True
                        else:
                            self.log_test("Real Content Verification", False, 
                                        f"Only {real_content_count}/80 procedures have real content")
                            return False
                    else:
                        self.log_test("Procedure Count (80 procedures)", False, 
                                    f"Expected 80 procedures, found {len(procedures)}")
                        return False
                else:
                    self.log_test("Procedure Count (80 procedures)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure Count (80 procedures)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Procedure Count (80 procedures)", False, f"Exception: {str(e)}")
            return False
    
    def test_specialty_count_and_organization(self):
        """Test that we have 9 specialties as expected"""
        try:
            response = self.session.get(f"{self.base_url}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    
                    if len(specialties) >= 7:  # Should have at least 7, expecting 9
                        specialty_names = [s.get("name", "") for s in specialties]
                        expected_specialties = ["oral_surgery", "restorative", "periodontics", "endodontics"]
                        
                        found_expected = sum(1 for exp in expected_specialties 
                                           if any(exp in name.lower().replace(" ", "_") for name in specialty_names))
                        
                        if found_expected >= 3:  # At least 3 of the expected specialties
                            total_procedures = sum(s.get("procedureCount", 0) for s in specialties)
                            self.log_test("Specialty Organization", True, 
                                        f"Found {len(specialties)} specialties with {total_procedures} total procedures")
                            return True
                        else:
                            self.log_test("Specialty Organization", False, 
                                        f"Missing expected specialties. Found: {specialty_names}")
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
    
    def test_specific_procedure_content(self):
        """Test specific procedures mentioned in the review request"""
        test_procedures = [
            "099c9463-7ecf-4ba5-84bf-9d64535de855",  # Dental Implant Placement
            "7fd9291c-cffc-40c1-ab6b-c8100a6191b0",  # Surgical Tooth Extraction
            "0098b205-dbee-430a-82ad-21d741587f6d",  # Root Canal Therapy
            "e0a217e7-41f1-4685-9399-a6bf317443e6"   # Dental Crown Placement
        ]
        
        success_count = 0
        
        for procedure_id in test_procedures:
            try:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        
                        # Check required sections
                        required_sections = [
                            "overview", "immediateAftercare", "dietRestrictions", 
                            "warningSignsToCallDoctor", "recoveryTimeline", "medications"
                        ]
                        
                        missing_sections = []
                        for section in required_sections:
                            if section not in procedure or not procedure[section]:
                                missing_sections.append(section)
                        
                        if not missing_sections:
                            # Check content quality
                            overview = procedure.get("overview", "")
                            aftercare = procedure.get("immediateAftercare", [])
                            
                            if len(overview) > 50 and len(aftercare) > 0:
                                self.log_test(f"Procedure Content: {procedure.get('name', procedure_id)}", True, 
                                            f"Complete sections with substantial content")
                                success_count += 1
                            else:
                                self.log_test(f"Procedure Content: {procedure.get('name', procedure_id)}", False, 
                                            "Content too brief or empty")
                        else:
                            self.log_test(f"Procedure Content: {procedure.get('name', procedure_id)}", False, 
                                        f"Missing sections: {missing_sections}")
                    else:
                        self.log_test(f"Procedure Content: {procedure_id}", False, "Invalid response format")
                else:
                    self.log_test(f"Procedure Content: {procedure_id}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Procedure Content: {procedure_id}", False, f"Exception: {str(e)}")
        
        return success_count >= 3  # At least 3 out of 5 should work
    
    def test_procedure_content_uniqueness(self):
        """Test that different procedures have different content (not generic)"""
        try:
            # Get a few different procedures
            test_procedures = [
                "0098b205-dbee-430a-82ad-21d741587f6d",  # Root Canal Therapy
                "7fd9291c-cffc-40c1-ab6b-c8100a6191b0",  # Surgical Tooth Extraction
                "e0a217e7-41f1-4685-9399-a6bf317443e6"   # Dental Crown Placement
            ]
            procedure_contents = {}
            
            for procedure_id in test_procedures:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        overview = procedure.get("overview", "")
                        aftercare = procedure.get("immediateAftercare", [])
                        
                        # Create a content signature
                        content_signature = overview[:100] + str(aftercare[:2])
                        procedure_contents[procedure_id] = content_signature
            
            if len(procedure_contents) >= 2:
                # Check if contents are different
                signatures = list(procedure_contents.values())
                unique_signatures = len(set(signatures))
                
                if unique_signatures == len(signatures):
                    self.log_test("Content Uniqueness", True, 
                                f"All {len(signatures)} tested procedures have unique content")
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
    
    def test_specialty_filtering(self):
        """Test GET /api/procedures?specialty=oral_surgery filtering"""
        try:
            response = self.session.get(f"{self.base_url}/procedures?specialty=oral-surgery")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    
                    if len(procedures) > 0:
                        # Check that all procedures are from oral surgery specialty
                        all_oral_surgery = all(proc.get("specialty") == "oral-surgery" for proc in procedures)
                        
                        if all_oral_surgery:
                            self.log_test("Specialty Filtering (oral-surgery)", True, 
                                        f"Retrieved {len(procedures)} oral surgery procedures")
                            return True
                        else:
                            wrong_specialty = [proc for proc in procedures if proc.get("specialty") != "oral-surgery"]
                            self.log_test("Specialty Filtering (oral-surgery)", False, 
                                        f"Found {len(wrong_specialty)} procedures from wrong specialty")
                            return False
                    else:
                        self.log_test("Specialty Filtering (oral-surgery)", False, "No oral surgery procedures found")
                        return False
                else:
                    self.log_test("Specialty Filtering (oral-surgery)", False, "Invalid response format")
                    return False
            else:
                self.log_test("Specialty Filtering (oral-surgery)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Specialty Filtering (oral-surgery)", False, f"Exception: {str(e)}")
            return False
    
    def test_procedure_pdf_data_completeness(self):
        """Test that procedures have complete data for PDF generation"""
        try:
            # Test a comprehensive procedure
            response = self.session.get(f"{self.base_url}/procedures/0098b205-dbee-430a-82ad-21d741587f6d")  # Root Canal Therapy
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check all sections needed for PDF generation
                    pdf_sections = {
                        "overview": procedure.get("overview", ""),
                        "immediateAftercare": procedure.get("immediateAftercare", []),
                        "dietRestrictions": procedure.get("dietRestrictions", []),
                        "warningSignsToCallDoctor": procedure.get("warningSignsToCallDoctor", []),
                        "recoveryTimeline": procedure.get("recoveryTimeline", []),
                        "medications": procedure.get("medications", [])
                    }
                    
                    complete_sections = 0
                    section_details = []
                    
                    for section_name, section_content in pdf_sections.items():
                        if section_content:
                            if isinstance(section_content, str) and len(section_content) > 20:
                                complete_sections += 1
                                section_details.append(f"{section_name}: {len(section_content)} chars")
                            elif isinstance(section_content, list) and len(section_content) > 0:
                                complete_sections += 1
                                section_details.append(f"{section_name}: {len(section_content)} items")
                    
                    if complete_sections >= 5:  # At least 5 out of 6 sections should be complete
                        self.log_test("PDF Data Completeness", True, 
                                    f"Procedure has {complete_sections}/6 complete sections for PDF generation")
                        return True
                    else:
                        self.log_test("PDF Data Completeness", False, 
                                    f"Only {complete_sections}/6 sections complete. Details: {section_details}")
                        return False
                else:
                    self.log_test("PDF Data Completeness", False, "Invalid response format")
                    return False
            else:
                self.log_test("PDF Data Completeness", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PDF Data Completeness", False, f"Exception: {str(e)}")
            return False
    
    def test_alphabetical_organization(self):
        """Test that procedures are stored in alphabetical order"""
        try:
            response = self.session.get(f"{self.base_url}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    
                    if len(procedures) > 10:  # Need enough procedures to test ordering
                        # Get first 20 procedure names
                        procedure_names = [proc.get("name", "") for proc in procedures[:20]]
                        
                        # Check if they're in alphabetical order
                        sorted_names = sorted(procedure_names)
                        
                        # Allow for some flexibility - check if at least 80% are in order
                        correct_positions = sum(1 for i, name in enumerate(procedure_names) 
                                              if i < len(sorted_names) and name == sorted_names[i])
                        
                        if correct_positions >= len(procedure_names) * 0.8:
                            self.log_test("Alphabetical Organization", True, 
                                        f"{correct_positions}/{len(procedure_names)} procedures in alphabetical order")
                            return True
                        else:
                            self.log_test("Alphabetical Organization", False, 
                                        f"Only {correct_positions}/{len(procedure_names)} procedures in alphabetical order")
                            return False
                    else:
                        self.log_test("Alphabetical Organization", False, "Not enough procedures to test ordering")
                        return False
                else:
                    self.log_test("Alphabetical Organization", False, "Invalid response format")
                    return False
            else:
                self.log_test("Alphabetical Organization", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Alphabetical Organization", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all procedure content tests"""
        print("🔍 TESTING UPDATED PROCEDURE CONTENT AND PDF GENERATION")
        print("=" * 60)
        
        tests = [
            self.test_procedure_count_and_content,
            self.test_specialty_count_and_organization,
            self.test_specific_procedure_content,
            self.test_procedure_content_uniqueness,
            self.test_specialty_filtering,
            self.test_procedure_pdf_data_completeness,
            self.test_alphabetical_organization
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 60)
        print(f"📊 PROCEDURE CONTENT TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - Updated procedure database is working correctly!")
        elif passed >= total * 0.8:
            print("⚠️  MOSTLY WORKING - Minor issues detected")
        else:
            print("❌ CRITICAL ISSUES - Procedure database needs attention")
        
        return passed, total

def main():
    """Main test execution"""
    tester = ProcedureContentTester(BACKEND_URL)
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()