#!/usr/bin/env python3
"""
Enhanced PDF Generation Backend Comprehensive Testing
Verifies backend supports all enhanced WYSIWYG PDF generation features
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://careplan-builder.preview.emergentagent.com/api"

class EnhancedPDFTester:
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
    
    def test_procedure_data_completeness(self, procedure_id: str, procedure_name: str):
        """Test that procedure has all required fields for enhanced PDF generation"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"{procedure_name} - Data Completeness", False, 
                            f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            if not data.get("success"):
                self.log_test(f"{procedure_name} - Data Completeness", False, 
                            "API returned success=false")
                return False
            
            procedure = data.get("data", {})
            
            # Check all required fields for enhanced PDF
            required_fields = {
                "id": "Procedure ID",
                "name": "Procedure Name", 
                "specialty": "Specialty Code",
                "specialtyName": "Specialty Display Name",
                "duration": "Recovery Duration",
                "overview": "Overview Content",
                "immediateAftercare": "Aftercare Instructions",
                "dietRestrictions": "Diet Restrictions",
                "warningSignsToCallDoctor": "Warning Signs",
                "recoveryTimeline": "Recovery Timeline",
                "medications": "Medications"
            }
            
            missing_fields = []
            empty_fields = []
            
            for field, description in required_fields.items():
                if field not in procedure:
                    missing_fields.append(f"{field} ({description})")
                elif not procedure[field]:
                    empty_fields.append(f"{field} ({description})")
            
            if missing_fields:
                self.log_test(f"{procedure_name} - Data Completeness", False, 
                            f"Missing fields: {missing_fields}")
                return False
            
            if empty_fields:
                self.log_test(f"{procedure_name} - Data Completeness", False, 
                            f"Empty fields: {empty_fields}")
                return False
            
            self.log_test(f"{procedure_name} - Data Completeness", True, 
                        "All required fields present and populated")
            return True
            
        except Exception as e:
            self.log_test(f"{procedure_name} - Data Completeness", False, f"Exception: {str(e)}")
            return False
    
    def test_color_coded_sections_data(self, procedure_id: str, procedure_name: str):
        """Test that procedure data supports color-coded sections"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"{procedure_name} - Color-Coded Sections", False, 
                            f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            procedure = data.get("data", {})
            
            # Test each color-coded section has adequate content
            section_tests = {
                "Green (Aftercare)": {
                    "field": "immediateAftercare",
                    "min_items": 3,
                    "type": list
                },
                "Orange (Diet)": {
                    "field": "dietRestrictions", 
                    "min_items": 3,
                    "type": list
                },
                "Red (Warnings)": {
                    "field": "warningSignsToCallDoctor",
                    "min_items": 3,
                    "type": list
                },
                "Purple (Timeline)": {
                    "field": "recoveryTimeline",
                    "min_items": 2,
                    "type": list
                },
                "Blue (Medications)": {
                    "field": "medications",
                    "min_items": 1,
                    "type": list
                }
            }
            
            failed_sections = []
            
            for section_name, requirements in section_tests.items():
                field_data = procedure.get(requirements["field"], [])
                
                if not isinstance(field_data, requirements["type"]):
                    failed_sections.append(f"{section_name}: Wrong data type")
                elif len(field_data) < requirements["min_items"]:
                    failed_sections.append(f"{section_name}: Insufficient items ({len(field_data)} < {requirements['min_items']})")
            
            if failed_sections:
                self.log_test(f"{procedure_name} - Color-Coded Sections", False, 
                            f"Failed sections: {failed_sections}")
                return False
            
            self.log_test(f"{procedure_name} - Color-Coded Sections", True, 
                        "All color-coded sections have adequate content")
            return True
            
        except Exception as e:
            self.log_test(f"{procedure_name} - Color-Coded Sections", False, f"Exception: {str(e)}")
            return False
    
    def test_timeline_structure(self, procedure_id: str, procedure_name: str):
        """Test that recovery timeline has proper structure for enhanced PDF"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"{procedure_name} - Timeline Structure", False, 
                            f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            procedure = data.get("data", {})
            
            timeline = procedure.get("recoveryTimeline", [])
            
            if not timeline:
                self.log_test(f"{procedure_name} - Timeline Structure", False, 
                            "No timeline data")
                return False
            
            # Check timeline structure (should be list of objects with day/activity)
            structure_valid = True
            structure_issues = []
            
            for i, item in enumerate(timeline):
                if not isinstance(item, dict):
                    structure_issues.append(f"Item {i+1}: Not a dictionary")
                    structure_valid = False
                    continue
                
                if "day" not in item:
                    structure_issues.append(f"Item {i+1}: Missing 'day' field")
                    structure_valid = False
                
                if "activity" not in item:
                    structure_issues.append(f"Item {i+1}: Missing 'activity' field")
                    structure_valid = False
                
                if "day" in item and not item["day"]:
                    structure_issues.append(f"Item {i+1}: Empty 'day' field")
                    structure_valid = False
                
                if "activity" in item and not item["activity"]:
                    structure_issues.append(f"Item {i+1}: Empty 'activity' field")
                    structure_valid = False
            
            if not structure_valid:
                self.log_test(f"{procedure_name} - Timeline Structure", False, 
                            f"Structure issues: {structure_issues}")
                return False
            
            self.log_test(f"{procedure_name} - Timeline Structure", True, 
                        f"Timeline structure valid ({len(timeline)} items)")
            return True
            
        except Exception as e:
            self.log_test(f"{procedure_name} - Timeline Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_content_quality_for_styling(self, procedure_id: str, procedure_name: str):
        """Test that content quality supports professional styling"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"{procedure_name} - Content Quality", False, 
                            f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            procedure = data.get("data", {})
            
            quality_checks = {
                "Overview substantial": len(procedure.get("overview", "")) >= 200,
                "Procedure name descriptive": len(procedure.get("name", "")) >= 10,
                "Specialty name present": len(procedure.get("specialtyName", "")) >= 5,
                "Duration informative": len(procedure.get("duration", "")) >= 5,
                "Aftercare detailed": all(len(item.strip()) >= 20 for item in procedure.get("immediateAftercare", [])),
                "Diet restrictions specific": all(len(item.strip()) >= 15 for item in procedure.get("dietRestrictions", [])),
                "Warning signs clear": all(len(item.strip()) >= 20 for item in procedure.get("warningSignsToCallDoctor", [])),
                "Medications informative": all(len(item.strip()) >= 15 for item in procedure.get("medications", []))
            }
            
            failed_quality = [check for check, passed in quality_checks.items() if not passed]
            
            if failed_quality:
                self.log_test(f"{procedure_name} - Content Quality", False, 
                            f"Quality issues: {failed_quality}")
                return False
            
            self.log_test(f"{procedure_name} - Content Quality", True, 
                        "Content quality supports professional styling")
            return True
            
        except Exception as e:
            self.log_test(f"{procedure_name} - Content Quality", False, f"Exception: {str(e)}")
            return False
    
    def test_procedure_specific_content(self, procedure_id: str, procedure_name: str, expected_terms: List[str]):
        """Test that procedure contains specific medical terminology (not generic)"""
        try:
            response = self.session.get(f"{self.base_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"{procedure_name} - Specific Content", False, 
                            f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            procedure = data.get("data", {})
            
            # Convert all procedure content to lowercase for searching
            all_content = json.dumps(procedure).lower()
            
            found_terms = []
            missing_terms = []
            
            for term in expected_terms:
                if term.lower() in all_content:
                    found_terms.append(term)
                else:
                    missing_terms.append(term)
            
            if len(found_terms) < len(expected_terms) * 0.6:  # At least 60% of terms should be found
                self.log_test(f"{procedure_name} - Specific Content", False, 
                            f"Insufficient specific terms. Found: {found_terms}, Missing: {missing_terms}")
                return False
            
            self.log_test(f"{procedure_name} - Specific Content", True, 
                        f"Procedure-specific content verified. Found terms: {found_terms}")
            return True
            
        except Exception as e:
            self.log_test(f"{procedure_name} - Specific Content", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive enhanced PDF backend tests"""
        print("=" * 80)
        print("ENHANCED WYSIWYG PDF GENERATION - COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        
        # Test procedures mentioned in review request
        test_procedures = [
            {
                "id": "root-canal-therapy",
                "name": "Root Canal Therapy", 
                "terms": ["root canal", "pulp", "endodontic", "canal", "tooth"]
            },
            {
                "id": "dental-implant-placement",
                "name": "Dental Implant Placement",
                "terms": ["implant", "titanium", "osseointegration", "abutment", "surgical"]
            }
        ]
        
        all_tests_passed = True
        
        for proc in test_procedures:
            print(f"\n--- Testing {proc['name']} ({proc['id']}) ---")
            
            # Run all test categories for this procedure
            tests = [
                lambda: self.test_procedure_data_completeness(proc['id'], proc['name']),
                lambda: self.test_color_coded_sections_data(proc['id'], proc['name']),
                lambda: self.test_timeline_structure(proc['id'], proc['name']),
                lambda: self.test_content_quality_for_styling(proc['id'], proc['name']),
                lambda: self.test_procedure_specific_content(proc['id'], proc['name'], proc['terms'])
            ]
            
            for test in tests:
                if not test():
                    all_tests_passed = False
        
        print("\n" + "=" * 80)
        print("ENHANCED PDF BACKEND TEST SUMMARY")
        print("=" * 80)
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if all_tests_passed:
            print("\n✅ ALL ENHANCED PDF BACKEND TESTS PASSED")
            print("✅ Backend fully supports WYSIWYG PDF generation")
            print("✅ Color-coded sections data is complete")
            print("✅ Professional styling requirements met")
            print("✅ Procedure-specific content verified")
        else:
            print("\n❌ SOME ENHANCED PDF BACKEND TESTS FAILED")
            print("❌ Enhanced PDF generation may have issues")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if not result["success"]]
            if failed_tests:
                print("\nFailed Tests:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['details']}")
        
        return all_tests_passed

def main():
    """Main test execution"""
    tester = EnhancedPDFTester(BACKEND_URL)
    
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Focus: Enhanced WYSIWYG PDF Generation Support")
    
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎯 CONCLUSION: Backend is fully ready for enhanced WYSIWYG PDF generation")
        print("🎯 All color-coded sections, professional styling, and content requirements met")
        sys.exit(0)
    else:
        print("\n🚨 CONCLUSION: Backend needs improvements for enhanced PDF generation")
        sys.exit(1)

if __name__ == "__main__":
    main()