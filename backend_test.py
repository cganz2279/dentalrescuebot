#!/usr/bin/env python3
"""
Backend Testing Script for Dental Practice Management System
Focus: URGENT PDF FORMAT VERIFICATION - Amalgam Fillings Procedure Content
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host"

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
    
    def test_amalgam_fillings_procedure(self) -> None:
        """Test the specific Amalgam Fillings procedure as requested in review"""
        print(f"\n🎯 URGENT: TESTING AMALGAM FILLINGS PROCEDURE CONTENT")
        print("=" * 80)
        print("Request: Show EXACT content in overview field for amalgam-fillings procedure")
        print("Expected format verification against user's requirements")
        
        # Test the public endpoint as specified in review
        procedure_id = "amalgam-fillings"
        print(f"\n🔍 Testing GET /api/public/procedures/{procedure_id}")
        
        try:
            # Test public endpoint first (no auth required)
            response = self.session.get(f"{self.base_url}/api/public/procedures/{procedure_id}")
            print(f"Public endpoint response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedure = data.get("data", {})
                    print(f"✅ Successfully retrieved from public endpoint: {procedure.get('name', 'Unknown')}")
                    self.display_exact_overview_content(procedure)
                    return
                else:
                    print(f"❌ Public API returned success=false: {data}")
            else:
                print(f"❌ Public endpoint failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error with public endpoint: {str(e)}")
        
        # Fallback to regular procedure endpoint
        print(f"\n🔄 Trying regular procedure endpoint...")
        procedure_data = self.get_procedure_details(procedure_id)
        if procedure_data:
            self.display_exact_overview_content(procedure_data)
        else:
            print("❌ CRITICAL: Could not retrieve Amalgam Fillings procedure from any endpoint")
    
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