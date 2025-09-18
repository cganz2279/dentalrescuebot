#!/usr/bin/env python3
"""
PDF CONTENT VERIFICATION TEST
Testing current database content against original PostOp PDF requirements
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

# Test credentials from review request
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

# Expected Root Canal content from original PDF (from review request)
EXPECTED_ROOT_CANAL_CONTENT = """DENTAL RESCUE BOT
Root Canal Therapy

Purpose: Removal of infected or damaged pulp tissue from inside the tooth, followed by sealing.

First 24 Hours:
- Avoid chewing on the treated tooth until numbness wears off.
- Some tenderness or mild discomfort is normal.

Pain & Sensitivity:
- Use OTC or prescribed pain relievers as directed.
- Tooth sensitivity to pressure may last for several days.

Oral Hygiene:
- Brush and floss normally, avoiding excessive pressure on the treated tooth.

Diet:
- Soft foods are recommended until chewing comfort improves.

Special Precautions:
- If a temporary filling is placed, avoid sticky or hard foods until the permanent restoration is done.

Follow-Up:
- A crown or permanent filling is usually required for full protection.
- Contact the office if pain worsens, swelling develops, or you notice signs of infection."""

class PDFContentVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}: {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def authenticate(self) -> bool:
        """Authenticate with the backend"""
        try:
            print(f"\n🔐 Authenticating with {TEST_EMAIL}...")
            
            auth_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_result("Authentication", True, f"Successfully authenticated as {TEST_EMAIL}")
                    return True
                else:
                    self.log_result("Authentication", False, "No token received in response")
                    return False
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_procedure_content(self, procedure_id: str) -> Dict[str, Any]:
        """Get procedure content from API"""
        try:
            print(f"\n📄 Fetching procedure: {procedure_id}")
            
            response = self.session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    procedure_data = data['data']
                    self.log_result(f"Fetch {procedure_id}", True, f"Retrieved procedure data successfully")
                    return procedure_data
                else:
                    self.log_result(f"Fetch {procedure_id}", False, "Invalid response format")
                    return {}
            else:
                self.log_result(f"Fetch {procedure_id}", False, f"HTTP {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            self.log_result(f"Fetch {procedure_id}", False, f"Exception: {str(e)}")
            return {}
    
    def analyze_content_structure(self, procedure_data: Dict[str, Any], procedure_name: str):
        """Analyze the structure and content of procedure data"""
        print(f"\n🔍 ANALYZING {procedure_name.upper()} CONTENT STRUCTURE:")
        
        # Check if overview field exists and show its content
        overview = procedure_data.get('overview', '')
        if overview:
            print(f"📝 Overview field length: {len(overview)} characters")
            print(f"📝 Overview content preview: {overview[:200]}...")
            self.log_result(f"{procedure_name} Overview", True, f"Overview field contains {len(overview)} characters")
        else:
            print("❌ No overview field found")
            self.log_result(f"{procedure_name} Overview", False, "No overview field found")
        
        # Check structured fields
        structured_fields = ['immediateAftercare', 'dietRestrictions', 'warningSignsToCallDoctor', 'recoveryTimeline', 'medications']
        
        for field in structured_fields:
            field_data = procedure_data.get(field, [])
            if isinstance(field_data, list) and field_data:
                print(f"📋 {field}: {len(field_data)} items")
                for i, item in enumerate(field_data[:3]):  # Show first 3 items
                    if isinstance(item, dict):
                        print(f"   {i+1}. {item}")
                    else:
                        print(f"   {i+1}. {item}")
                self.log_result(f"{procedure_name} {field}", True, f"Contains {len(field_data)} items")
            else:
                print(f"❌ {field}: Missing or empty")
                self.log_result(f"{procedure_name} {field}", False, "Missing or empty")
    
    def compare_with_expected_content(self, procedure_data: Dict[str, Any], expected_content: str, procedure_name: str):
        """Compare actual content with expected original PDF content"""
        print(f"\n🔍 COMPARING {procedure_name.upper()} WITH EXPECTED ORIGINAL PDF CONTENT:")
        
        overview = procedure_data.get('overview', '')
        
        # Key terms that should be present in Root Canal content
        expected_terms = [
            'root canal', 'pulp', 'tooth', 'infection', 'canal',
            'temporary', 'permanent', 'crown', 'filling', 'restoration'
        ]
        
        found_terms = []
        missing_terms = []
        
        overview_lower = overview.lower()
        for term in expected_terms:
            if term.lower() in overview_lower:
                found_terms.append(term)
            else:
                missing_terms.append(term)
        
        print(f"✅ Found expected terms: {found_terms}")
        if missing_terms:
            print(f"❌ Missing expected terms: {missing_terms}")
        
        # Check if content matches the structure of original PDF
        has_purpose = 'purpose' in overview_lower or 'removal' in overview_lower
        has_aftercare = 'avoid chewing' in overview_lower or 'numbness' in overview_lower
        has_followup = 'crown' in overview_lower or 'permanent' in overview_lower
        
        structure_score = sum([has_purpose, has_aftercare, has_followup])
        
        self.log_result(f"{procedure_name} Content Match", 
                       len(found_terms) >= 6 and structure_score >= 2,
                       f"Found {len(found_terms)}/{len(expected_terms)} expected terms, structure score: {structure_score}/3")
    
    def test_root_canal_therapy(self):
        """Test Root Canal Therapy procedure content"""
        print("\n" + "="*80)
        print("🦷 TESTING ROOT CANAL THERAPY CONTENT")
        print("="*80)
        
        procedure_data = self.get_procedure_content("root-canal-therapy")
        if not procedure_data:
            return
        
        # Show complete overview content
        overview = procedure_data.get('overview', '')
        print(f"\n📄 COMPLETE OVERVIEW FIELD CONTENT ({len(overview)} characters):")
        print("-" * 60)
        print(overview)
        print("-" * 60)
        
        # Analyze structure
        self.analyze_content_structure(procedure_data, "Root Canal Therapy")
        
        # Compare with expected content
        self.compare_with_expected_content(procedure_data, EXPECTED_ROOT_CANAL_CONTENT, "Root Canal Therapy")
    
    def test_dental_bridge_placement(self):
        """Test Dental Bridge Placement procedure content"""
        print("\n" + "="*80)
        print("🌉 TESTING DENTAL BRIDGE PLACEMENT CONTENT")
        print("="*80)
        
        procedure_data = self.get_procedure_content("dental-bridge-placement")
        if not procedure_data:
            return
        
        # Show overview content
        overview = procedure_data.get('overview', '')
        print(f"\n📄 OVERVIEW FIELD CONTENT ({len(overview)} characters):")
        print("-" * 60)
        print(overview[:500] + "..." if len(overview) > 500 else overview)
        print("-" * 60)
        
        # Analyze structure
        self.analyze_content_structure(procedure_data, "Dental Bridge Placement")
        
        # Check for bridge-specific terms
        bridge_terms = ['bridge', 'crown', 'abutment', 'pontic', 'cement']
        overview_lower = overview.lower()
        found_bridge_terms = [term for term in bridge_terms if term in overview_lower]
        
        self.log_result("Dental Bridge Content", 
                       len(found_bridge_terms) >= 3,
                       f"Found bridge-specific terms: {found_bridge_terms}")
    
    def test_dental_implant_placement(self):
        """Test Dental Implant Placement procedure content"""
        print("\n" + "="*80)
        print("🦴 TESTING DENTAL IMPLANT PLACEMENT CONTENT")
        print("="*80)
        
        procedure_data = self.get_procedure_content("dental-implant-placement")
        if not procedure_data:
            return
        
        # Show overview content
        overview = procedure_data.get('overview', '')
        print(f"\n📄 OVERVIEW FIELD CONTENT ({len(overview)} characters):")
        print("-" * 60)
        print(overview[:500] + "..." if len(overview) > 500 else overview)
        print("-" * 60)
        
        # Analyze structure
        self.analyze_content_structure(procedure_data, "Dental Implant Placement")
        
        # Check for implant-specific terms
        implant_terms = ['implant', 'titanium', 'osseointegration', 'surgical', 'bone']
        overview_lower = overview.lower()
        found_implant_terms = [term for term in implant_terms if term in overview_lower]
        
        self.log_result("Dental Implant Content", 
                       len(found_implant_terms) >= 3,
                       f"Found implant-specific terms: {found_implant_terms}")
    
    def run_all_tests(self):
        """Run all PDF content verification tests"""
        print("🎯 PDF CONTENT VERIFICATION AGAINST ORIGINAL POSTOP DOCUMENTS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Test all procedures
        self.test_root_canal_therapy()
        self.test_dental_bridge_placement()
        self.test_dental_implant_placement()
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = PDFContentVerificationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)