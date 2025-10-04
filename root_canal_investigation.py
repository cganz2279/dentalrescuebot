#!/usr/bin/env python3
"""
Root Canal Procedure Content Investigation
Review Request: Investigate Root Canal procedure showing generic test content instead of proper medical instructions
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com/api"

class RootCanalInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   {details}")
        print()
        
    def authenticate(self):
        """Authenticate with provided credentials"""
        print("🔐 Authenticating with cganz2279@gmail.com/password123...")
        
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
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.jwt_token}"
                    })
                    user_info = data.get('user', {})
                    self.log_result(
                        "Authentication",
                        True,
                        f"Successfully authenticated as {user_info.get('email')} with role {user_info.get('role')} for practice {user_info.get('practiceName', 'N/A')}"
                    )
                    return True
                else:
                    self.log_result("Authentication", False, "No token in response")
                    return False
            else:
                self.log_result("Authentication", False, f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Request failed: {str(e)}")
            return False
    
    def check_root_canal_content(self):
        """Check Root Canal procedure content for generic vs medical content"""
        print("🦷 Checking Root Canal Therapy content...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                procedure = data.get("data", {}) if data.get("success") else data
                
                # Check required fields
                required_fields = [
                    "immediateAftercare",
                    "dietRestrictions", 
                    "warningSignsToCallDoctor",
                    "recoveryTimeline",
                    "medications"
                ]
                
                missing_fields = []
                generic_content_found = []
                medical_content_found = []
                
                for field in required_fields:
                    field_data = procedure.get(field)
                    if not field_data:
                        missing_fields.append(field)
                    else:
                        # Convert to string for analysis
                        content_str = str(field_data).lower()
                        
                        # Check for generic test content
                        generic_indicators = [
                            "test assignment from automated testing",
                            "please follow all post-operative instructions carefully",
                            "generic", "placeholder", "test content", "dummy"
                        ]
                        
                        # Check for root canal specific medical content
                        medical_indicators = [
                            "root canal", "pulp", "endodontic", "canal", "tooth",
                            "nerve", "infection", "antibiotics", "pain medication",
                            "temporary filling", "crown", "bite"
                        ]
                        
                        # Count indicators
                        generic_found = [indicator for indicator in generic_indicators if indicator in content_str]
                        medical_found = [indicator for indicator in medical_indicators if indicator in content_str]
                        
                        if generic_found:
                            generic_content_found.append(f"{field}: {generic_found}")
                        if medical_found:
                            medical_content_found.append(f"{field}: {medical_found}")
                
                # Analyze results
                has_all_fields = len(missing_fields) == 0
                has_generic_content = len(generic_content_found) > 0
                has_medical_content = len(medical_content_found) > 0
                
                # Check for specific corruption mentioned in test_result.md
                diet_restrictions = procedure.get("dietRestrictions", [])
                diet_corrupted = False
                if diet_restrictions:
                    diet_str = str(diet_restrictions)
                    if "spitting, rinsing, or using straws" in diet_str or "Apply an ice pack" in diet_str:
                        diet_corrupted = True
                        generic_content_found.append("dietRestrictions: Contains aftercare content (corrupted)")
                
                success = has_all_fields and has_medical_content and not has_generic_content and not diet_corrupted
                
                details = f"""
Fields present: {5 - len(missing_fields)}/5 (missing: {missing_fields})
Generic content indicators: {len(generic_content_found)} ({generic_content_found})
Medical content indicators: {len(medical_content_found)} ({medical_content_found})
Diet restrictions corrupted: {diet_corrupted}
Procedure overview length: {len(str(procedure.get('overview', '')))} characters
"""
                
                self.log_result(
                    "Root Canal Content Analysis",
                    success,
                    details.strip()
                )
                
                return procedure
                
            else:
                self.log_result(
                    "Root Canal Content Analysis",
                    False,
                    f"Failed to retrieve procedure - Status: {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Root Canal Content Analysis",
                False,
                f"Error: {str(e)}"
            )
            return None
    
    def check_other_procedures(self):
        """Check other procedures for comparison"""
        print("🔍 Checking other procedures for comparison...")
        
        procedures_to_check = [
            ("dental-implant-placement", "Dental Implant Placement"),
            ("dental-crown-placement", "Dental Crown Placement")
        ]
        
        results = {}
        
        for procedure_id, procedure_name in procedures_to_check:
            try:
                response = self.session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    procedure = data.get("data", {}) if data.get("success") else data
                    
                    # Quick analysis
                    has_content = all(procedure.get(field) for field in [
                        "immediateAftercare", "dietRestrictions", "warningSignsToCallDoctor",
                        "recoveryTimeline", "medications"
                    ])
                    
                    # Check for generic content
                    content_str = str(procedure).lower()
                    has_generic = any(indicator in content_str for indicator in [
                        "test assignment", "generic", "placeholder"
                    ])
                    
                    results[procedure_id] = {
                        "name": procedure_name,
                        "has_content": has_content,
                        "has_generic": has_generic,
                        "status": "working" if has_content and not has_generic else "issues"
                    }
                    
                else:
                    results[procedure_id] = {
                        "name": procedure_name,
                        "status": f"error_{response.status_code}"
                    }
                    
            except Exception as e:
                results[procedure_id] = {
                    "name": procedure_name,
                    "status": f"exception_{str(e)}"
                }
        
        # Summary
        working_procedures = sum(1 for r in results.values() if r.get("status") == "working")
        total_procedures = len(results)
        
        success = working_procedures == total_procedures
        
        details = f"""
Procedures tested: {total_procedures}
Working properly: {working_procedures}
Results: {json.dumps(results, indent=2)}
"""
        
        self.log_result(
            "Other Procedures Comparison",
            success,
            details.strip()
        )
        
        return results
    
    def verify_database_content(self):
        """Verify database content integrity"""
        print("🗄️ Verifying database content integrity...")
        
        try:
            # Check total procedure count
            response = self.session.get(f"{BACKEND_URL}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                procedures = data.get("data", []) if data.get("success") else []
                
                total_count = len(procedures)
                expected_count = 81  # Based on test_result.md
                
                # Check for procedures with real content vs generic
                real_content_count = 0
                generic_content_count = 0
                
                for proc in procedures[:10]:  # Sample first 10
                    content_str = str(proc).lower()
                    if any(indicator in content_str for indicator in ["test", "generic", "placeholder"]):
                        generic_content_count += 1
                    else:
                        real_content_count += 1
                
                success = total_count == expected_count and real_content_count > generic_content_count
                
                details = f"""
Total procedures: {total_count} (expected: {expected_count})
Sample analysis (first 10):
- Real content: {real_content_count}
- Generic content: {generic_content_count}
"""
                
                self.log_result(
                    "Database Content Verification",
                    success,
                    details.strip()
                )
                
                return total_count == expected_count
                
            else:
                self.log_result(
                    "Database Content Verification",
                    False,
                    f"Failed to retrieve procedures - Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Database Content Verification",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("🚀 ROOT CANAL PROCEDURE CONTENT INVESTIGATION")
        print(f"Backend URL: {BACKEND_URL}")
        print("Issue: Root Canal procedure showing generic test content instead of medical instructions")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Check Root Canal content specifically
        root_canal_data = self.check_root_canal_content()
        
        # Step 3: Check other procedures for comparison
        other_procedures = self.check_other_procedures()
        
        # Step 4: Verify database content integrity
        db_integrity = self.verify_database_content()
        
        # Generate summary
        print("=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print("\n💡 CONCLUSION:")
        if passed_tests == total_tests:
            print("✅ Root Canal procedure contains proper medical content from uploaded PDFs")
            print("✅ No generic test content detected")
            print("✅ Database integrity verified")
        else:
            print("❌ CRITICAL ISSUE CONFIRMED: Root Canal procedure has content issues")
            print("🔧 ACTION REQUIRED: Database needs re-processing to fix content corruption")
            print("📋 IMPACT: PDF generation will produce poor quality output")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    investigator = RootCanalInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)