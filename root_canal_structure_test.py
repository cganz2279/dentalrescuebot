#!/usr/bin/env python3
"""
Root Canal Procedure Structure Verification Test
Review Request: Verify Root Canal procedure has proper structured medical content for PDF generation
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com/api"

class RootCanalStructureTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, expected_result=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected_result,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if expected_result:
            print(f"   Expected: {expected_result}")
        print()
        
    def test_authentication(self):
        """Test 1: Login with cganz2279@gmail.com/password123"""
        print("🔐 Testing Authentication...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": "cganz2279@gmail.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.jwt_token = data["token"]
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.jwt_token}"
                    })
                    
                    user_info = data.get("user", {})
                    self.log_test(
                        "Authentication with cganz2279@gmail.com/password123",
                        True,
                        f"Successfully authenticated. Email: {user_info.get('email')}, Role: {user_info.get('role')}, Practice: {user_info.get('practiceName', 'N/A')}",
                        "Should authenticate successfully and return JWT token"
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication with cganz2279@gmail.com/password123",
                        False,
                        f"Login successful but no token in response: {data}",
                        "Should return JWT token"
                    )
                    return False
            else:
                self.log_test(
                    "Authentication with cganz2279@gmail.com/password123",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}",
                    "Should return 200 with JWT token"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication with cganz2279@gmail.com/password123",
                False,
                f"Authentication request failed: {str(e)}",
                "Should successfully connect and authenticate"
            )
            return False
    
    def test_root_canal_structure(self):
        """Test 2: Verify Root Canal procedure has structured medical content fields"""
        print("🦷 Testing Root Canal Procedure Structure...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                procedure_data = data.get("data", {}) if data.get("success") else data
                
                # Required structured fields for PDF generation
                required_fields = [
                    "immediateAftercare",
                    "dietRestrictions", 
                    "warningSignsToCallDoctor",
                    "recoveryTimeline",
                    "medications"
                ]
                
                missing_fields = []
                field_details = {}
                
                for field in required_fields:
                    if field in procedure_data:
                        field_value = procedure_data[field]
                        if isinstance(field_value, list):
                            field_details[field] = f"Array with {len(field_value)} items"
                        else:
                            field_details[field] = f"Type: {type(field_value).__name__}, Length: {len(str(field_value)) if field_value else 0}"
                    else:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_test(
                        "Root Canal Structured Fields Verification",
                        True,
                        f"All required structured fields present: {field_details}",
                        "Should contain immediateAftercare, dietRestrictions, warningSignsToCallDoctor, recoveryTimeline, medications as arrays"
                    )
                    return True, procedure_data
                else:
                    self.log_test(
                        "Root Canal Structured Fields Verification",
                        False,
                        f"Missing required fields: {missing_fields}. Present fields: {field_details}. Available fields: {list(procedure_data.keys())}",
                        "Should contain all required structured fields as arrays"
                    )
                    return False, procedure_data
            else:
                self.log_test(
                    "Root Canal Structured Fields Verification",
                    False,
                    f"Failed to get Root Canal procedure - Status: {response.status_code}, Response: {response.text}",
                    "Should return 200 with procedure data"
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                "Root Canal Structured Fields Verification",
                False,
                f"Root Canal API request failed: {str(e)}",
                "Should successfully retrieve Root Canal procedure data"
            )
            return False, None
    
    def test_content_quality(self, procedure_data):
        """Test 3: Verify content is specific to root canal procedures (not generic)"""
        print("📋 Testing Content Quality...")
        
        if not procedure_data:
            self.log_test(
                "Root Canal Content Quality Check",
                False,
                "Cannot test content quality - no procedure data available",
                "Requires valid procedure data"
            )
            return False
        
        # Root canal specific terms that should appear in the content
        root_canal_terms = [
            "root canal", "canal", "pulp", "endodontic", "tooth", "restoration", 
            "temporary", "permanent", "crown", "filling"
        ]
        
        # Generic test content that should NOT appear
        generic_terms = [
            "test assignment", "automated testing", "placeholder", "dummy", 
            "sample", "example", "lorem ipsum"
        ]
        
        # Check all text content in the procedure
        all_content = ""
        content_fields = ["overview", "immediateAftercare", "dietRestrictions", 
                         "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
        
        for field in content_fields:
            if field in procedure_data:
                field_value = procedure_data[field]
                if isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, dict):
                            all_content += " " + str(item.get("activity", "")) + " " + str(item.get("day", ""))
                        else:
                            all_content += " " + str(item)
                else:
                    all_content += " " + str(field_value)
        
        all_content = all_content.lower()
        
        # Check for root canal specific terms
        found_root_canal_terms = [term for term in root_canal_terms if term in all_content]
        
        # Check for generic test content
        found_generic_terms = [term for term in generic_terms if term in all_content]
        
        if found_root_canal_terms and not found_generic_terms:
            self.log_test(
                "Root Canal Content Quality Check",
                True,
                f"Content is procedure-specific. Found root canal terms: {found_root_canal_terms}. No generic test content detected.",
                "Content should be specific to root canal procedures, not generic test content"
            )
            return True
        elif found_generic_terms:
            self.log_test(
                "Root Canal Content Quality Check",
                False,
                f"Generic test content detected: {found_generic_terms}. This matches user's report of 'Test assignment from automated testing' content.",
                "Content should be medical and procedure-specific, not generic test content"
            )
            return False
        else:
            self.log_test(
                "Root Canal Content Quality Check",
                False,
                f"Content lacks root canal specific terminology. Found terms: {found_root_canal_terms}. Content may be too generic.",
                "Content should contain root canal specific medical terminology"
            )
            return False
    
    def test_field_content_integrity(self, procedure_data):
        """Test 4: Verify each field contains appropriate content (not corrupted)"""
        print("🔍 Testing Field Content Integrity...")
        
        if not procedure_data:
            self.log_test(
                "Field Content Integrity Check",
                False,
                "Cannot test field integrity - no procedure data available",
                "Requires valid procedure data"
            )
            return False
        
        integrity_issues = []
        
        # Check dietRestrictions specifically (this was reported as corrupted)
        diet_restrictions = procedure_data.get("dietRestrictions", [])
        if isinstance(diet_restrictions, list) and diet_restrictions:
            # Check if diet restrictions contain aftercare content (corruption indicator)
            diet_content = " ".join([str(item) for item in diet_restrictions]).lower()
            aftercare_indicators = ["ice pack", "spitting", "rinsing", "straws", "clot", "stitches"]
            
            found_aftercare_in_diet = [term for term in aftercare_indicators if term in diet_content]
            if found_aftercare_in_diet:
                integrity_issues.append(f"dietRestrictions contains aftercare content: {found_aftercare_in_diet}")
        
        # Check if each field has appropriate content type
        field_expectations = {
            "immediateAftercare": ["care", "avoid", "do not", "apply", "keep"],
            "dietRestrictions": ["eat", "drink", "avoid", "soft", "liquid", "food"],
            "warningSignsToCallDoctor": ["call", "contact", "emergency", "pain", "bleeding", "swelling"],
            "recoveryTimeline": ["day", "week", "hours", "time"],
            "medications": ["medication", "pain", "antibiotic", "take", "dose"]
        }
        
        for field, expected_terms in field_expectations.items():
            if field in procedure_data:
                field_value = procedure_data[field]
                if isinstance(field_value, list) and field_value:
                    field_content = " ".join([str(item) for item in field_value]).lower()
                    found_expected = [term for term in expected_terms if term in field_content]
                    
                    if not found_expected:
                        integrity_issues.append(f"{field} may not contain appropriate content (no expected terms found)")
        
        if not integrity_issues:
            self.log_test(
                "Field Content Integrity Check",
                True,
                "All fields appear to contain appropriate content types. No corruption detected.",
                "Each field should contain content appropriate to its purpose"
            )
            return True
        else:
            self.log_test(
                "Field Content Integrity Check",
                False,
                f"Content integrity issues detected: {integrity_issues}",
                "Each field should contain content appropriate to its purpose, not corrupted content from other fields"
            )
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Root Canal Procedure Structure Verification")
        print(f"Backend URL: {BACKEND_URL}")
        print("Review Request: Verify Root Canal has structured medical content for PDF generation")
        print("=" * 80)
        
        # Test 1: Authentication
        auth_success = self.test_authentication()
        
        # Test 2: Root Canal Structure
        structure_success = False
        procedure_data = None
        if auth_success:
            structure_success, procedure_data = self.test_root_canal_structure()
        
        # Test 3: Content Quality
        quality_success = False
        if procedure_data:
            quality_success = self.test_content_quality(procedure_data)
        
        # Test 4: Field Integrity
        integrity_success = False
        if procedure_data:
            integrity_success = self.test_field_content_integrity(procedure_data)
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            print(f"    {result['details']}")
            print()
        
        print("🎯 REVIEW REQUEST VERIFICATION:")
        print(f"✅ Login (cganz2279@gmail.com/password123): {'PASSED' if auth_success else 'FAILED'}")
        print(f"✅ Root Canal Structured Fields: {'PASSED' if structure_success else 'FAILED'}")  
        print(f"✅ Content Quality (procedure-specific): {'PASSED' if quality_success else 'FAILED'}")
        print(f"✅ Field Content Integrity: {'PASSED' if integrity_success else 'FAILED'}")
        
        if auth_success and structure_success and quality_success and integrity_success:
            print("\n🎉 ALL TESTS PASSED - Root Canal procedure has proper structured medical content!")
            print("✅ Database structure issue has been resolved")
            print("✅ Ready for proper PDF generation with detailed medical instructions")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - Root Canal procedure structure needs attention")
            if not structure_success:
                print("❌ Missing required structured fields for PDF generation")
            if not quality_success:
                print("❌ Content quality issues - may still contain generic test content")
            if not integrity_success:
                print("❌ Field content corruption detected - database needs restructuring")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = RootCanalStructureTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)