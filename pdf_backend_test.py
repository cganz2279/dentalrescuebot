#!/usr/bin/env python3
"""
PDF Generation Backend Testing
Testing backend API endpoints that support PDF generation functionality
Focus: Procedure Data API and PDF Content Quality verification
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Backend URL from environment (using working URL from test_result.md)
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com/api"

class PDFBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()

    def authenticate(self):
        """Authenticate with test credentials"""
        try:
            # Try authentication with known working credentials
            auth_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_result("Authentication", True, "Successfully authenticated with cganz2279@gmail.com")
                    return True
                else:
                    self.log_result("Authentication", False, f"Login response missing token: {data}")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_root_canal_therapy_api(self):
        """Test GET /api/procedures/root-canal-therapy for complete procedure data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/root-canal-therapy")
            
            if response.status_code != 200:
                self.log_result("Root Canal Therapy API", False, f"API returned status {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_result("Root Canal Therapy API", False, f"API returned success=false: {data}")
                return False
                
            procedure = data.get("data", {})
            
            # Check required fields for PDF generation
            required_fields = ["name", "specialty", "duration", "overview", "immediateAftercare", 
                             "dietRestrictions", "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
            
            missing_fields = []
            for field in required_fields:
                if field not in procedure:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("Root Canal Therapy API", False, f"Missing required fields: {missing_fields}")
                return False
            
            # Verify content arrays have multiple items
            content_arrays = {
                "immediateAftercare": procedure.get("immediateAftercare", []),
                "dietRestrictions": procedure.get("dietRestrictions", []),
                "warningSignsToCallDoctor": procedure.get("warningSignsToCallDoctor", []),
                "recoveryTimeline": procedure.get("recoveryTimeline", []),
                "medications": procedure.get("medications", [])
            }
            
            array_details = {}
            for array_name, array_data in content_arrays.items():
                array_details[array_name] = {
                    "count": len(array_data),
                    "sample": array_data[:2] if array_data else []
                }
            
            # Check for procedure-specific content (root canal terminology)
            root_canal_terms = ["root canal", "pulp", "canal", "endodontic", "tooth"]
            content_text = json.dumps(procedure).lower()
            found_terms = [term for term in root_canal_terms if term in content_text]
            
            details = {
                "procedure_name": procedure.get("name"),
                "specialty": procedure.get("specialty"),
                "content_arrays": array_details,
                "root_canal_terms_found": found_terms,
                "overview_length": len(procedure.get("overview", "")),
                "total_fields": len(procedure.keys())
            }
            
            # Verify this is procedure-specific content
            if len(found_terms) < 2:
                self.log_result("Root Canal Therapy API", False, 
                              f"Content appears generic - only found {len(found_terms)} root canal terms: {found_terms}", details)
                return False
            
            self.log_result("Root Canal Therapy API", True, 
                          f"Complete procedure data with {len(found_terms)} root canal-specific terms", details)
            return True
            
        except Exception as e:
            self.log_result("Root Canal Therapy API", False, f"Test error: {str(e)}")
            return False

    def test_dental_implant_api(self):
        """Test GET /api/procedures/dental-implant-placement for comparison"""
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/dental-implant-placement")
            
            if response.status_code != 200:
                self.log_result("Dental Implant API", False, f"API returned status {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            if not data.get("success"):
                self.log_result("Dental Implant API", False, f"API returned success=false: {data}")
                return False
                
            procedure = data.get("data", {})
            
            # Check for implant-specific content
            implant_terms = ["implant", "titanium", "surgical", "osseointegration", "abutment"]
            content_text = json.dumps(procedure).lower()
            found_terms = [term for term in implant_terms if term in content_text]
            
            # Verify content arrays
            content_arrays = {
                "immediateAftercare": len(procedure.get("immediateAftercare", [])),
                "dietRestrictions": len(procedure.get("dietRestrictions", [])),
                "warningSignsToCallDoctor": len(procedure.get("warningSignsToCallDoctor", [])),
                "recoveryTimeline": len(procedure.get("recoveryTimeline", [])),
                "medications": len(procedure.get("medications", []))
            }
            
            details = {
                "procedure_name": procedure.get("name"),
                "implant_terms_found": found_terms,
                "content_array_counts": content_arrays
            }
            
            if len(found_terms) < 2:
                self.log_result("Dental Implant API", False, 
                              f"Content appears generic - only found {len(found_terms)} implant terms: {found_terms}", details)
                return False
            
            self.log_result("Dental Implant API", True, 
                          f"Procedure-specific content with {len(found_terms)} implant-specific terms", details)
            return True
            
        except Exception as e:
            self.log_result("Dental Implant API", False, f"Test error: {str(e)}")
            return False

    def test_pdf_data_structure_compatibility(self):
        """Test that procedure data structure supports enhanced PDF layout"""
        try:
            # Test multiple procedures to verify consistent structure
            test_procedures = ["root-canal-therapy", "dental-implant-placement", "surgical-tooth-extraction"]
            
            structure_results = {}
            
            for procedure_id in test_procedures:
                response = self.session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        procedure = data.get("data", {})
                        
                        # Analyze structure for PDF compatibility
                        structure_results[procedure_id] = {
                            "name": procedure.get("name", ""),
                            "aftercare_items": len(procedure.get("immediateAftercare", [])),
                            "diet_items": len(procedure.get("dietRestrictions", [])),
                            "warning_items": len(procedure.get("warningSignsToCallDoctor", [])),
                            "timeline_items": len(procedure.get("recoveryTimeline", [])),
                            "medication_items": len(procedure.get("medications", [])),
                            "has_overview": bool(procedure.get("overview", "").strip())
                        }
            
            # Verify all procedures have adequate content for enhanced PDF styling
            min_requirements = {
                "aftercare_items": 3,  # For green badges
                "diet_items": 3,       # For orange badges  
                "warning_items": 3,    # For red alert boxes
                "timeline_items": 3,   # For purple timeline badges
                "medication_items": 1  # For blue headers
            }
            
            compatibility_issues = []
            
            for proc_id, structure in structure_results.items():
                for req_field, min_count in min_requirements.items():
                    if structure.get(req_field, 0) < min_count:
                        compatibility_issues.append(f"{proc_id}: {req_field} has {structure.get(req_field, 0)} items (need {min_count})")
            
            if compatibility_issues:
                self.log_result("PDF Data Structure", False, 
                              f"Structure issues found: {compatibility_issues}", structure_results)
                return False
            
            self.log_result("PDF Data Structure", True, 
                          "All procedures have adequate content for enhanced PDF styling", structure_results)
            return True
            
        except Exception as e:
            self.log_result("PDF Data Structure", False, f"Test error: {str(e)}")
            return False

    def test_procedure_content_uniqueness(self):
        """Verify procedures have unique, procedure-specific content (not generic placeholders)"""
        try:
            # Test several procedures to verify content uniqueness
            test_procedures = [
                "root-canal-therapy",
                "dental-implant-placement", 
                "surgical-tooth-extraction",
                "dental-crown-placement"
            ]
            
            procedure_contents = {}
            
            for procedure_id in test_procedures:
                response = self.session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        procedure = data.get("data", {})
                        
                        # Extract key content for comparison
                        content_signature = {
                            "overview_words": set(procedure.get("overview", "").lower().split()[:20]),
                            "aftercare_first": procedure.get("immediateAftercare", [""])[0].lower() if procedure.get("immediateAftercare") else "",
                            "warning_first": procedure.get("warningSignsToCallDoctor", [""])[0].lower() if procedure.get("warningSignsToCallDoctor") else ""
                        }
                        
                        procedure_contents[procedure_id] = content_signature
            
            # Check for content uniqueness
            uniqueness_results = {}
            
            for proc1_id, content1 in procedure_contents.items():
                for proc2_id, content2 in procedure_contents.items():
                    if proc1_id != proc2_id:
                        # Calculate content similarity
                        overview_overlap = len(content1["overview_words"].intersection(content2["overview_words"]))
                        aftercare_similar = content1["aftercare_first"] == content2["aftercare_first"]
                        warning_similar = content1["warning_first"] == content2["warning_first"]
                        
                        similarity_key = f"{proc1_id}_vs_{proc2_id}"
                        uniqueness_results[similarity_key] = {
                            "overview_word_overlap": overview_overlap,
                            "aftercare_identical": aftercare_similar,
                            "warning_identical": warning_similar
                        }
            
            # Check for concerning similarities (indicating generic content)
            generic_content_issues = []
            
            for comparison, similarity in uniqueness_results.items():
                if similarity["overview_word_overlap"] > 15:  # Too many shared words
                    generic_content_issues.append(f"{comparison}: {similarity['overview_word_overlap']} shared overview words")
                if similarity["aftercare_identical"] and similarity["warning_identical"]:
                    generic_content_issues.append(f"{comparison}: Identical aftercare and warning content")
            
            if generic_content_issues:
                self.log_result("Content Uniqueness", False, 
                              f"Generic content detected: {generic_content_issues}", uniqueness_results)
                return False
            
            self.log_result("Content Uniqueness", True, 
                          "All procedures have unique, procedure-specific content", 
                          {"procedures_tested": len(procedure_contents), "comparisons": len(uniqueness_results)})
            return True
            
        except Exception as e:
            self.log_result("Content Uniqueness", False, f"Test error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all PDF backend tests"""
        print("🔍 STARTING PDF GENERATION BACKEND TESTING")
        print("=" * 60)
        print()
        
        # Authentication first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run priority tests
        tests = [
            ("Procedure Data API - Root Canal Therapy", self.test_root_canal_therapy_api),
            ("Procedure Data API - Dental Implant", self.test_dental_implant_api),
            ("PDF Data Structure Compatibility", self.test_pdf_data_structure_compatibility),
            ("Procedure Content Uniqueness", self.test_procedure_content_uniqueness)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"🧪 Running: {test_name}")
            if test_func():
                passed_tests += 1
            print("-" * 40)
        
        # Summary
        print()
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if passed_tests == total_tests:
            print("✅ ALL PDF BACKEND TESTS PASSED")
            return True
        else:
            print("❌ SOME PDF BACKEND TESTS FAILED")
            return False

if __name__ == "__main__":
    tester = PDFBackendTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)