#!/usr/bin/env python3
"""
PDF Generation Backend Testing for Enhanced WYSIWYG Functionality
Tests procedure endpoints to verify data structure supports enhanced PDF generation
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dental-portal-debug.preview.emergentagent.com/api"

class PDFGenerationTester:
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
    
    def test_root_canal_therapy_procedure(self):
        """Test GET /api/procedures/root-canal-therapy for PDF generation data"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("success"):
                    self.log_test("Root Canal Therapy API Response", False, "API returned success=false")
                    return False
                
                procedure = data.get("data", {})
                
                # Check required fields for PDF generation
                required_fields = [
                    "id", "name", "specialty", "specialtyName", "duration",
                    "overview", "immediateAftercare", "dietRestrictions", 
                    "warningSignsToCallDoctor", "recoveryTimeline", "medications"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in procedure:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test("Root Canal Therapy Data Structure", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify content is procedure-specific (not generic)
                content_checks = {
                    "root canal specific terms": any(term in str(procedure).lower() for term in 
                                                   ["root canal", "pulp", "endodontic", "canal"]),
                    "has aftercare instructions": len(procedure.get("immediateAftercare", [])) > 0,
                    "has diet restrictions": len(procedure.get("dietRestrictions", [])) > 0,
                    "has warning signs": len(procedure.get("warningSignsToCallDoctor", [])) > 0,
                    "has recovery timeline": len(procedure.get("recoveryTimeline", [])) > 0,
                    "has medications": len(procedure.get("medications", [])) > 0
                }
                
                failed_checks = [check for check, passed in content_checks.items() if not passed]
                
                if failed_checks:
                    self.log_test("Root Canal Therapy Content Quality", False, 
                                f"Failed checks: {failed_checks}")
                    return False
                
                self.log_test("Root Canal Therapy API", True, 
                            f"All required fields present, procedure-specific content verified")
                return True
                
            else:
                self.log_test("Root Canal Therapy API", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Root Canal Therapy API", False, f"Exception: {str(e)}")
            return False
    
    def test_dental_implant_placement_procedure(self):
        """Test GET /api/procedures/dental-implant-placement for PDF generation data"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/dental-implant-placement")
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("success"):
                    self.log_test("Dental Implant Placement API Response", False, "API returned success=false")
                    return False
                
                procedure = data.get("data", {})
                
                # Check required fields for PDF generation
                required_fields = [
                    "id", "name", "specialty", "specialtyName", "duration",
                    "overview", "immediateAftercare", "dietRestrictions", 
                    "warningSignsToCallDoctor", "recoveryTimeline", "medications"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in procedure:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test("Dental Implant Placement Data Structure", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify content is procedure-specific (not generic)
                content_checks = {
                    "implant specific terms": any(term in str(procedure).lower() for term in 
                                                ["implant", "titanium", "osseointegration", "abutment"]),
                    "has aftercare instructions": len(procedure.get("immediateAftercare", [])) > 0,
                    "has diet restrictions": len(procedure.get("dietRestrictions", [])) > 0,
                    "has warning signs": len(procedure.get("warningSignsToCallDoctor", [])) > 0,
                    "has recovery timeline": len(procedure.get("recoveryTimeline", [])) > 0,
                    "has medications": len(procedure.get("medications", [])) > 0
                }
                
                failed_checks = [check for check, passed in content_checks.items() if not passed]
                
                if failed_checks:
                    self.log_test("Dental Implant Placement Content Quality", False, 
                                f"Failed checks: {failed_checks}")
                    return False
                
                self.log_test("Dental Implant Placement API", True, 
                            f"All required fields present, procedure-specific content verified")
                return True
                
            else:
                self.log_test("Dental Implant Placement API", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dental Implant Placement API", False, f"Exception: {str(e)}")
            return False
    
    def test_procedure_data_for_enhanced_pdf(self):
        """Test that procedure data supports enhanced PDF generation features"""
        try:
            # Test multiple procedures to verify consistent data structure
            test_procedures = ["root-canal-therapy", "dental-implant-placement"]
            
            all_procedures_valid = True
            
            for procedure_id in test_procedures:
                response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
                
                if response.status_code != 200:
                    self.log_test(f"Enhanced PDF Data Structure ({procedure_id})", False, 
                                f"HTTP {response.status_code}")
                    all_procedures_valid = False
                    continue
                
                data = response.json()
                procedure = data.get("data", {})
                
                # Check for enhanced PDF generation requirements
                enhanced_pdf_checks = {
                    "overview_has_content": bool(procedure.get("overview", "").strip()),
                    "aftercare_is_list": isinstance(procedure.get("immediateAftercare"), list),
                    "diet_is_list": isinstance(procedure.get("dietRestrictions"), list),
                    "warnings_is_list": isinstance(procedure.get("warningSignsToCallDoctor"), list),
                    "timeline_is_list": isinstance(procedure.get("recoveryTimeline"), list),
                    "medications_is_list": isinstance(procedure.get("medications"), list),
                    "has_procedure_name": bool(procedure.get("name", "").strip()),
                    "has_specialty_info": bool(procedure.get("specialtyName", "").strip())
                }
                
                failed_enhanced_checks = [check for check, passed in enhanced_pdf_checks.items() if not passed]
                
                if failed_enhanced_checks:
                    self.log_test(f"Enhanced PDF Data Structure ({procedure_id})", False, 
                                f"Failed checks: {failed_enhanced_checks}")
                    all_procedures_valid = False
                else:
                    self.log_test(f"Enhanced PDF Data Structure ({procedure_id})", True, 
                                "All enhanced PDF requirements met")
            
            return all_procedures_valid
            
        except Exception as e:
            self.log_test("Enhanced PDF Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_procedure_content_formatting(self):
        """Test that procedure content supports color-coded sections and styling"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code != 200:
                self.log_test("Procedure Content Formatting", False, 
                            f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            procedure = data.get("data", {})
            
            # Check content formatting for enhanced PDF styling
            formatting_checks = {
                "aftercare_has_multiple_items": len(procedure.get("immediateAftercare", [])) >= 3,
                "diet_has_multiple_items": len(procedure.get("dietRestrictions", [])) >= 3,
                "warnings_has_multiple_items": len(procedure.get("warningSignsToCallDoctor", [])) >= 3,
                "timeline_has_entries": len(procedure.get("recoveryTimeline", [])) >= 1,
                "medications_has_entries": len(procedure.get("medications", [])) >= 1,
                "overview_substantial": len(procedure.get("overview", "")) >= 100
            }
            
            failed_formatting = [check for check, passed in formatting_checks.items() if not passed]
            
            if failed_formatting:
                self.log_test("Procedure Content Formatting", False, 
                            f"Insufficient content for styling: {failed_formatting}")
                return False
            
            # Check for timeline structure (should have day/activity structure)
            timeline = procedure.get("recoveryTimeline", [])
            if timeline and isinstance(timeline[0], dict):
                timeline_structure_valid = all(
                    isinstance(item, dict) and "day" in item and "activity" in item 
                    for item in timeline[:3]  # Check first 3 items
                )
                
                if not timeline_structure_valid:
                    self.log_test("Procedure Content Formatting", False, 
                                "Timeline structure invalid for enhanced PDF")
                    return False
            
            self.log_test("Procedure Content Formatting", True, 
                        "Content structure supports enhanced PDF styling")
            return True
            
        except Exception as e:
            self.log_test("Procedure Content Formatting", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all PDF generation tests"""
        print("=" * 60)
        print("ENHANCED PDF GENERATION BACKEND TESTING")
        print("=" * 60)
        
        tests = [
            self.test_root_canal_therapy_procedure,
            self.test_dental_implant_placement_procedure,
            self.test_procedure_data_for_enhanced_pdf,
            self.test_procedure_content_formatting
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"PDF GENERATION TEST RESULTS: {passed}/{total} PASSED")
        print("=" * 60)
        
        if passed == total:
            print("✅ ALL PDF GENERATION TESTS PASSED")
            print("✅ Backend supports enhanced WYSIWYG PDF generation")
            print("✅ Procedure data structure is complete for styling")
            return True
        else:
            print("❌ SOME PDF GENERATION TESTS FAILED")
            print("❌ Enhanced PDF generation may not work properly")
            return False

def main():
    """Main test execution"""
    tester = PDFGenerationTester(BACKEND_URL)
    
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Focus: Enhanced PDF Generation Functionality")
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: Backend is ready for enhanced PDF generation")
        sys.exit(0)
    else:
        print("\n🚨 CONCLUSION: Backend needs fixes for enhanced PDF generation")
        sys.exit(1)

if __name__ == "__main__":
    main()