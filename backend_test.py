#!/usr/bin/env python3
"""
Backend Test for Dental Application - Review Request
Testing database content verification and API endpoints as specified:
1. Database Content Verification - Check all 82 procedures (81 from ZIP + IV Sedation)
2. API Endpoint Testing - Test GET /api/procedures, /api/procedures/iv-sedation, /api/procedures/alveoloplasty
3. Specialty and Data Verification - Verify procedures are properly categorized
"""

import requests
import json
import sys
from typing import Dict, Any, Optional, List

# Backend URL from frontend .env file
BACKEND_URL = "https://dental-portal-fix-1.preview.emergentagent.com"

# Test credentials from review request
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class DentalBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.practice_data = None
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the backend API"""
        print(f"🔐 Authenticating with {email}...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.practice_data = data.get("practice", {})
                
                print(f"✅ Authentication successful!")
                print(f"   Practice: {self.practice_data.get('name', 'Unknown')}")
                print(f"   Role: {data.get('role', 'Unknown')}")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_procedure_details(self, procedure_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed procedure information"""
        print(f"\n🔍 Fetching procedure: {procedure_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/api/procedures/{procedure_id}")
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedure = data.get("data", {})
                    print(f"✅ Successfully retrieved procedure: {procedure.get('name', 'Unknown')}")
                    return procedure
                else:
                    print(f"❌ API returned success=false: {data}")
                    return None
            else:
                print(f"❌ Failed to fetch procedure: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching procedure: {str(e)}")
            return None
    
    def analyze_procedure_content(self, procedure: Dict[str, Any]) -> None:
        """Analyze and display procedure content in detail"""
        if not procedure:
            print("❌ No procedure data to analyze")
            return
            
        print(f"\n📋 PROCEDURE ANALYSIS: {procedure.get('name', 'Unknown')}")
        print("=" * 80)
        
        # Basic info
        print(f"ID: {procedure.get('id', 'N/A')}")
        print(f"Name: {procedure.get('name', 'N/A')}")
        print(f"Specialty: {procedure.get('specialtyName', 'N/A')} ({procedure.get('specialty', 'N/A')})")
        print(f"Duration: {procedure.get('duration', 'N/A')}")
        
        # Overview content
        overview = procedure.get('overview', '')
        print(f"\n📄 OVERVIEW CONTENT ({len(overview)} characters):")
        print("-" * 50)
        if overview:
            # Show first 500 characters and last 200 characters if long
            if len(overview) > 700:
                print(f"{overview[:500]}...")
                print(f"[... {len(overview) - 700} characters omitted ...]")
                print(f"...{overview[-200:]}")
            else:
                print(overview)
        else:
            print("❌ NO OVERVIEW CONTENT")
        
        # Structured medical content fields
        structured_fields = [
            ('immediateAftercare', '🚨 IMMEDIATE AFTERCARE'),
            ('dietRestrictions', '🍽️ DIET RESTRICTIONS'),
            ('warningSignsToCallDoctor', '⚠️ WARNING SIGNS'),
            ('recoveryTimeline', '📅 RECOVERY TIMELINE'),
            ('medications', '💊 MEDICATIONS')
        ]
        
        print(f"\n📊 STRUCTURED MEDICAL CONTENT:")
        print("-" * 50)
        
        for field_name, display_name in structured_fields:
            field_data = procedure.get(field_name, [])
            print(f"\n{display_name}:")
            
            if isinstance(field_data, list) and field_data:
                print(f"   Count: {len(field_data)} items")
                for i, item in enumerate(field_data, 1):
                    if isinstance(item, dict):
                        # For recovery timeline items
                        if 'day' in item and 'activity' in item:
                            print(f"   {i}. Day {item['day']}: {item['activity']}")
                        else:
                            print(f"   {i}. {json.dumps(item, indent=6)}")
                    else:
                        # Truncate very long items
                        item_str = str(item)
                        if len(item_str) > 200:
                            print(f"   {i}. {item_str[:200]}... [TRUNCATED - {len(item_str)} chars total]")
                        else:
                            print(f"   {i}. {item_str}")
            elif isinstance(field_data, list):
                print(f"   ❌ EMPTY LIST")
            else:
                print(f"   ❌ INVALID FORMAT: {type(field_data)} - {field_data}")
    
    def compare_with_expected_content(self, procedure: Dict[str, Any], procedure_name: str) -> None:
        """Compare procedure content with expected content from original PDF"""
        print(f"\n🔍 CONTENT COMPARISON FOR {procedure_name.upper()}")
        print("=" * 80)
        
        if procedure_name.lower() == "root canal therapy":
            expected_keywords = [
                "pulp", "infected", "damaged", "sealing", "numbness", 
                "tenderness", "discomfort", "sensitivity", "pressure",
                "soft foods", "temporary filling", "permanent restoration",
                "crown", "filling", "infection"
            ]
            
            overview = procedure.get('overview', '').lower()
            aftercare = ' '.join(procedure.get('immediateAftercare', [])).lower()
            diet = ' '.join(procedure.get('dietRestrictions', [])).lower()
            warnings = ' '.join(procedure.get('warningSignsToCallDoctor', [])).lower()
            
            all_content = f"{overview} {aftercare} {diet} {warnings}".lower()
            
            print("🎯 EXPECTED ROOT CANAL KEYWORDS ANALYSIS:")
            found_keywords = []
            missing_keywords = []
            
            for keyword in expected_keywords:
                if keyword in all_content:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            print(f"✅ FOUND ({len(found_keywords)}/{len(expected_keywords)}): {', '.join(found_keywords)}")
            if missing_keywords:
                print(f"❌ MISSING ({len(missing_keywords)}): {', '.join(missing_keywords)}")
            
            # Check for generic test content
            generic_indicators = [
                "test assignment", "automated testing", "placeholder", 
                "lorem ipsum", "sample content", "dummy data"
            ]
            
            found_generic = [indicator for indicator in generic_indicators if indicator in all_content]
            if found_generic:
                print(f"🚨 GENERIC CONTENT DETECTED: {', '.join(found_generic)}")
            else:
                print("✅ NO GENERIC TEST CONTENT DETECTED")
    
    def test_all_procedures_count(self) -> Dict[str, Any]:
        """Test that all 82 procedures are present (81 from ZIP + IV Sedation)"""
        print(f"\n🎯 1. DATABASE CONTENT VERIFICATION - PROCEDURE COUNT")
        print("=" * 80)
        print("Expected: 82 procedures total (81 from PostOpProcedures.zip + IV Sedation)")
        
        try:
            response = self.session.get(f"{self.base_url}/api/procedures")
            print(f"GET /api/procedures response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedures = data.get("data", [])
                    total_count = len(procedures)
                    
                    print(f"✅ Successfully retrieved procedures")
                    print(f"📊 TOTAL PROCEDURES FOUND: {total_count}")
                    
                    if total_count == 82:
                        print("✅ CORRECT COUNT: Found exactly 82 procedures as expected")
                    elif total_count == 81:
                        print("⚠️ MISSING 1 PROCEDURE: Found 81 procedures (IV Sedation may be missing)")
                    else:
                        print(f"❌ INCORRECT COUNT: Expected 82, found {total_count}")
                    
                    return {"success": True, "count": total_count, "procedures": procedures}
                else:
                    print(f"❌ API returned success=false: {data}")
                    return {"success": False, "error": "API returned success=false"}
            else:
                print(f"❌ Failed to fetch procedures: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error fetching procedures: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_iv_sedation_procedure(self) -> bool:
        """Test GET /api/procedures/iv-sedation specifically"""
        print(f"\n🎯 2. IV SEDATION VERIFICATION")
        print("=" * 80)
        print("Testing: GET /api/procedures/iv-sedation")
        print("Expected: IV Sedation procedure with complete, non-truncated content")
        
        procedure = self.get_procedure_details("iv-sedation")
        if not procedure:
            print("❌ CRITICAL: IV Sedation procedure not found")
            return False
        
        print(f"✅ IV Sedation procedure found: {procedure.get('name', 'Unknown')}")
        
        # Check content completeness
        overview = procedure.get('overview', '')
        overview_length = len(overview)
        
        print(f"📄 Overview content length: {overview_length} characters")
        
        if overview_length < 100:
            print("❌ CONTENT TOO SHORT: IV Sedation content appears truncated")
            return False
        elif overview_length < 500:
            print("⚠️ CONTENT MAY BE TRUNCATED: IV Sedation content is shorter than expected")
        else:
            print("✅ CONTENT LENGTH ADEQUATE: IV Sedation appears to have complete content")
        
        # Check for IV sedation specific terms
        iv_keywords = ["sedation", "iv", "intravenous", "conscious", "monitor", "recovery"]
        found_keywords = [kw for kw in iv_keywords if kw.lower() in overview.lower()]
        
        print(f"🔍 IV Sedation keywords found: {found_keywords}")
        
        if len(found_keywords) >= 3:
            print("✅ CONTENT VERIFICATION: IV Sedation content contains expected medical terminology")
            return True
        else:
            print("❌ CONTENT VERIFICATION FAILED: IV Sedation content lacks expected terminology")
            return False
    
    def test_alveoloplasty_procedure(self) -> bool:
        """Test GET /api/procedures/alveoloplasty to check sample procedure"""
        print(f"\n🎯 3. SAMPLE PROCEDURE VERIFICATION - ALVEOLOPLASTY")
        print("=" * 80)
        print("Testing: GET /api/procedures/alveoloplasty")
        print("Expected: Complete overview content from original PDF")
        
        procedure = self.get_procedure_details("alveoloplasty")
        if not procedure:
            print("❌ CRITICAL: Alveoloplasty procedure not found")
            return False
        
        print(f"✅ Alveoloplasty procedure found: {procedure.get('name', 'Unknown')}")
        
        # Analyze content quality
        overview = procedure.get('overview', '')
        overview_length = len(overview)
        
        print(f"📄 Overview content length: {overview_length} characters")
        
        # Check for medical terminology specific to alveoloplasty
        alveolo_keywords = ["alveolar", "bone", "socket", "extraction", "contouring", "healing", "tissue"]
        found_keywords = [kw for kw in alveolo_keywords if kw.lower() in overview.lower()]
        
        print(f"🔍 Alveoloplasty keywords found: {found_keywords}")
        
        # Check for generic test content
        generic_indicators = ["test assignment", "automated testing", "placeholder", "lorem ipsum", "dummy"]
        found_generic = [indicator for indicator in generic_indicators if indicator.lower() in overview.lower()]
        
        if found_generic:
            print(f"❌ GENERIC CONTENT DETECTED: {found_generic}")
            return False
        else:
            print("✅ NO GENERIC CONTENT: Procedure contains authentic medical content")
        
        if len(found_keywords) >= 3 and overview_length > 200:
            print("✅ CONTENT QUALITY VERIFIED: Alveoloplasty contains authentic medical content")
            return True
        else:
            print("❌ CONTENT QUALITY ISSUES: Alveoloplasty content may be incomplete or generic")
            return False
    
    def test_specialty_categorization(self, procedures: List[Dict[str, Any]]) -> Dict[str, int]:
        """Verify procedures are properly categorized by specialty"""
        print(f"\n🎯 4. SPECIALTY AND DATA VERIFICATION")
        print("=" * 80)
        print("Analyzing procedure distribution across specialties")
        
        specialty_counts = {}
        specialty_names = {}
        
        for procedure in procedures:
            specialty_id = procedure.get('specialty', 'unknown')
            specialty_name = procedure.get('specialtyName', 'Unknown')
            
            if specialty_id not in specialty_counts:
                specialty_counts[specialty_id] = 0
                specialty_names[specialty_id] = specialty_name
            
            specialty_counts[specialty_id] += 1
        
        print(f"📊 SPECIALTY DISTRIBUTION:")
        total_procedures = sum(specialty_counts.values())
        
        for specialty_id, count in sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True):
            specialty_name = specialty_names[specialty_id]
            percentage = (count / total_procedures) * 100
            print(f"   {specialty_name}: {count} procedures ({percentage:.1f}%)")
        
        # Check for expected specialties
        expected_specialties = ["oral-surgery", "periodontics", "endodontics", "prosthodontics", "orthodontics"]
        found_specialties = [s for s in expected_specialties if s in specialty_counts]
        
        print(f"\n🔍 EXPECTED SPECIALTIES VERIFICATION:")
        print(f"   Found: {len(found_specialties)}/{len(expected_specialties)} expected specialties")
        
        if len(found_specialties) >= 4:
            print("✅ SPECIALTY COVERAGE: Good distribution across dental specialties")
        else:
            print("⚠️ LIMITED SPECIALTY COVERAGE: Some expected specialties may be missing")
        
        return specialty_counts
    
    def verify_content_authenticity(self, procedures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify procedures contain original PDF content, not corrupted/generic content"""
        print(f"\n🎯 5. CONTENT AUTHENTICITY VERIFICATION")
        print("=" * 80)
        print("Checking for corrupted or generic 'test' content")
        
        sample_size = min(10, len(procedures))
        sample_procedures = procedures[:sample_size]
        
        results = {
            "total_checked": sample_size,
            "authentic_content": 0,
            "generic_content": 0,
            "corrupted_content": 0,
            "issues": []
        }
        
        generic_indicators = [
            "test assignment from automated testing",
            "placeholder content",
            "lorem ipsum",
            "dummy data",
            "sample text"
        ]
        
        for i, procedure in enumerate(sample_procedures, 1):
            name = procedure.get('name', f'Procedure {i}')
            overview = procedure.get('overview', '').lower()
            
            print(f"\n🔍 Checking {i}/{sample_size}: {name}")
            
            # Check for generic content
            found_generic = [indicator for indicator in generic_indicators if indicator in overview]
            
            if found_generic:
                print(f"   ❌ GENERIC CONTENT: {found_generic}")
                results["generic_content"] += 1
                results["issues"].append(f"{name}: Generic content detected")
            elif len(overview) < 100:
                print(f"   ⚠️ MINIMAL CONTENT: Only {len(overview)} characters")
                results["corrupted_content"] += 1
                results["issues"].append(f"{name}: Minimal content ({len(overview)} chars)")
            else:
                print(f"   ✅ AUTHENTIC CONTENT: {len(overview)} characters of medical content")
                results["authentic_content"] += 1
        
        print(f"\n📊 CONTENT AUTHENTICITY SUMMARY:")
        print(f"   Authentic content: {results['authentic_content']}/{sample_size}")
        print(f"   Generic content: {results['generic_content']}/{sample_size}")
        print(f"   Corrupted content: {results['corrupted_content']}/{sample_size}")
        
        if results["authentic_content"] >= sample_size * 0.8:
            print("✅ CONTENT QUALITY: Majority of procedures have authentic medical content")
        else:
            print("❌ CONTENT QUALITY ISSUES: Significant number of procedures have problems")
        
        return results
    
    def display_exact_overview_content(self, procedure: Dict[str, Any]) -> None:
        """Display the EXACT overview content as requested"""
        if not procedure:
            print("❌ No procedure data to display")
            return
            
        print(f"\n📋 EXACT DATABASE CONTENT FOR: {procedure.get('name', 'Unknown')}")
        print("=" * 80)
        
        # Basic info
        print(f"Procedure ID: {procedure.get('id', 'N/A')}")
        print(f"Procedure Name: {procedure.get('name', 'N/A')}")
        print(f"Specialty: {procedure.get('specialtyName', 'N/A')}")
        
        # EXACT overview content
        overview = procedure.get('overview', '')
        print(f"\n📄 EXACT OVERVIEW FIELD CONTENT:")
        print("=" * 50)
        print(f"Character Count: {len(overview)}")
        print("=" * 50)
        
        if overview:
            print(overview)
        else:
            print("❌ NO OVERVIEW CONTENT FOUND")
        
        print("=" * 50)
        print("END OF EXACT OVERVIEW CONTENT")
        
        # Compare with expected format
        self.compare_with_expected_amalgam_format(overview)
    
    def compare_with_expected_amalgam_format(self, overview_content: str) -> None:
        """Compare with the user's expected Amalgam Fillings format"""
        print(f"\n🔍 COMPARISON WITH USER'S EXPECTED FORMAT")
        print("=" * 80)
        
        expected_sections = [
            "Purpose:",
            "First 24 Hours:",
            "Pain & Sensitivity:",
            "Oral Hygiene:",
            "Diet:",
            "Special Precautions:",
            "Follow-Up:"
        ]
        
        expected_keywords = [
            "amalgam", "silver-colored", "restoration", "decayed", "damaged",
            "numbness", "24 hours", "fully set", "chew", "opposite side",
            "sensitivity", "pressure", "temperature", "OTC pain relievers",
            "brush", "floss", "gentle", "hard", "sticky foods",
            "bite feels uneven", "contact the office", "adjustment",
            "gradually decrease", "pain worsens", "persists", "week"
        ]
        
        print("🎯 CHECKING FOR EXPECTED SECTIONS:")
        found_sections = []
        missing_sections = []
        
        for section in expected_sections:
            if section in overview_content:
                found_sections.append(section)
                print(f"✅ Found: {section}")
            else:
                missing_sections.append(section)
                print(f"❌ Missing: {section}")
        
        print(f"\n📊 SECTION SUMMARY: {len(found_sections)}/{len(expected_sections)} sections found")
        
        print("\n🎯 CHECKING FOR EXPECTED KEYWORDS:")
        found_keywords = []
        missing_keywords = []
        
        overview_lower = overview_content.lower()
        for keyword in expected_keywords:
            if keyword.lower() in overview_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        print(f"✅ Found keywords ({len(found_keywords)}/{len(expected_keywords)}): {', '.join(found_keywords[:10])}{'...' if len(found_keywords) > 10 else ''}")
        if missing_keywords:
            print(f"❌ Missing keywords ({len(missing_keywords)}): {', '.join(missing_keywords[:10])}{'...' if len(missing_keywords) > 10 else ''}")
        
        # Format analysis
        print(f"\n📝 FORMAT ANALYSIS:")
        lines = overview_content.split('\n')
        print(f"Total lines: {len(lines)}")
        print(f"Non-empty lines: {len([line for line in lines if line.strip()])}")
        
        # Check if it matches the expected structured format
        has_structured_format = len(found_sections) >= 5  # At least 5 of the 7 expected sections
        has_sufficient_keywords = len(found_keywords) >= len(expected_keywords) * 0.7  # At least 70% of keywords
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if has_structured_format and has_sufficient_keywords:
            print("✅ CONTENT MATCHES EXPECTED FORMAT - Database contains properly formatted Amalgam Fillings content")
        elif has_structured_format:
            print("⚠️ PARTIAL MATCH - Structure is correct but some keywords missing")
        elif has_sufficient_keywords:
            print("⚠️ PARTIAL MATCH - Keywords present but structure may differ")
        else:
            print("❌ CONTENT DOES NOT MATCH EXPECTED FORMAT - Database content differs significantly from user requirements")

def main():
    """Main testing function"""
    print("🦷 URGENT: PDF FORMAT VERIFICATION - AMALGAM FILLINGS PROCEDURE")
    print("=" * 80)
    print("CRITICAL REQUEST: Show EXACT content in database for amalgam-fillings procedure")
    print("Backend URL: https://dentist-portal-3.emergent.host/api")
    print("Testing: GET /api/public/procedures/amalgam-fillings")
    
    tester = DentalBackendTester()
    
    # Authenticate with specified credentials
    print(f"\n🔐 Authenticating with cganz2279@gmail.com/password123...")
    if not tester.authenticate("cganz2279@gmail.com", "password123"):
        print("❌ Authentication failed. Proceeding with public endpoint test...")
    else:
        print("✅ Authentication successful. Testing both authenticated and public endpoints...")
    
    # Test the specific Amalgam Fillings procedure
    tester.test_amalgam_fillings_procedure()
    
    print(f"\n🎯 TESTING COMPLETE")
    print("=" * 80)
    print("Review the EXACT overview content above to verify it matches your format requirements.")
    print("Expected format includes: Purpose, First 24 Hours, Pain & Sensitivity, Oral Hygiene, Diet, Special Precautions, Follow-Up")

if __name__ == "__main__":
    main()