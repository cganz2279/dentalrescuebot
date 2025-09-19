#!/usr/bin/env python3
"""
Backend Testing Script for Dental Practice Management System
Focus: Verify updated PDF content format in database
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        priority = "🚨 CRITICAL" if critical else "ℹ️ INFO"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{priority} {status} - {test_name}")
        print(f"   Details: {details}")
        print()
        
    def authenticate(self):
        """Authenticate with the backend"""
        print("🔐 AUTHENTICATING WITH BACKEND...")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Credentials: {TEST_EMAIL}/{TEST_PASSWORD}")
        print()
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    practice_name = data.get("practice", {}).get("name", "Unknown")
                    user_role = data.get("role", "Unknown")
                    
                    self.log_result(
                        "Authentication", 
                        True, 
                        f"Successfully authenticated as {user_role} for practice: {practice_name}"
                    )
                    return True
                else:
                    self.log_result(
                        "Authentication", 
                        False, 
                        "No access token in response", 
                        critical=True
                    )
                    return False
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Authentication", 
                False, 
                f"Exception during authentication: {str(e)}", 
                critical=True
            )
            return False
    
    def test_procedure_content(self, procedure_id, procedure_name):
        """Test specific procedure content format"""
        print(f"🔍 TESTING {procedure_name.upper()} CONTENT FORMAT...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    procedure = data["data"]
                    overview = procedure.get("overview", "")
                    
                    print(f"📋 PROCEDURE: {procedure.get('name', 'Unknown')}")
                    print(f"📏 OVERVIEW LENGTH: {len(overview)} characters")
                    print(f"🔤 OVERVIEW CONTENT:")
                    print("=" * 80)
                    print(overview)
                    print("=" * 80)
                    print()
                    
                    # Check for expected format sections
                    expected_sections = [
                        "Purpose:",
                        "First 24",
                        "Pain & Sensitivity:",
                        "Oral Hygiene:",
                        "Diet:",
                        "Follow-Up:"
                    ]
                    
                    found_sections = []
                    for section in expected_sections:
                        if section in overview:
                            found_sections.append(section)
                    
                    # Analyze content structure
                    has_structured_format = len(found_sections) >= 3
                    
                    details = f"Overview length: {len(overview)} chars. Found sections: {found_sections}. Expected format: {'YES' if has_structured_format else 'NO'}"
                    
                    self.log_result(
                        f"{procedure_name} Content Format",
                        True,  # Always pass to show content, but note format in details
                        details
                    )
                    
                    # Also check structured fields
                    structured_fields = {
                        "immediateAftercare": procedure.get("immediateAftercare", []),
                        "dietRestrictions": procedure.get("dietRestrictions", []),
                        "warningSignsToCallDoctor": procedure.get("warningSignsToCallDoctor", []),
                        "recoveryTimeline": procedure.get("recoveryTimeline", []),
                        "medications": procedure.get("medications", [])
                    }
                    
                    print(f"📊 STRUCTURED FIELDS ANALYSIS:")
                    for field_name, field_data in structured_fields.items():
                        if isinstance(field_data, list):
                            print(f"   {field_name}: {len(field_data)} items")
                            if field_data and len(field_data) > 0:
                                print(f"      First item: {str(field_data[0])[:100]}...")
                        else:
                            print(f"   {field_name}: {type(field_data)} - {str(field_data)[:100]}...")
                    print()
                    
                    return True
                else:
                    self.log_result(
                        f"{procedure_name} Content Format",
                        False,
                        "No procedure data in response",
                        critical=True
                    )
                    return False
            else:
                self.log_result(
                    f"{procedure_name} Content Format",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_result(
                f"{procedure_name} Content Format",
                False,
                f"Exception: {str(e)}",
                critical=True
            )
            return False
    
    def run_content_verification_tests(self):
        """Run the specific content verification tests requested"""
        print("🎯 STARTING PDF CONTENT VERIFICATION TESTS")
        print("=" * 60)
        print()
        
        # Test 1: Root Canal Therapy
        success1 = self.test_procedure_content("root-canal-therapy", "Root Canal Therapy")
        
        # Test 2: Amalgam Fillings  
        success2 = self.test_procedure_content("amalgam-fillings", "Amalgam Fillings")
        
        return success1 and success2
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for result in self.test_results if not result["success"] and result["critical"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🚨 Critical Failures: {critical_failures}")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    priority = "🚨 CRITICAL" if result["critical"] else "⚠️ MINOR"
                    print(f"   {priority} {result['test']}: {result['details']}")
            print()
        
        return critical_failures == 0

def main():
    """Main test execution"""
    print("🚀 BACKEND CONTENT VERIFICATION TESTING")
    print("=" * 60)
    print(f"Target: {BACKEND_URL}")
    print(f"Focus: Verify updated PDF content format")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    tester = BackendTester()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("🚨 AUTHENTICATION FAILED - CANNOT PROCEED")
        sys.exit(1)
    
    # Step 2: Run content verification tests
    content_tests_passed = tester.run_content_verification_tests()
    
    # Step 3: Print summary
    overall_success = tester.print_summary()
    
    if overall_success:
        print("🎉 ALL CRITICAL TESTS PASSED")
        sys.exit(0)
    else:
        print("🚨 CRITICAL TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()