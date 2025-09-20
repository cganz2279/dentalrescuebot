#!/usr/bin/env python3
"""
IV Sedation Content Verification Test - Review Request
Testing GET /api/procedures/iv-sedation endpoint to show COMPLETE overview field content
User reports: "IV Sedation is missing most of the PDF content"
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class IVSedationContentTester:
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
    
    def test_iv_sedation_content(self) -> None:
        """Test IV Sedation procedure content as requested in review"""
        print(f"\n🎯 CRITICAL: TESTING IV SEDATION PROCEDURE CONTENT")
        print("=" * 80)
        print("Request: Show COMPLETE overview field content for iv-sedation procedure")
        print("Expected sections: Purpose, First 24 Hours, Pain & Swelling, Diet, Activity, Special Precautions, Follow-Up")
        
        procedure_id = "iv-sedation"
        print(f"\n🔍 Testing GET /api/procedures/{procedure_id}")
        
        try:
            # Test the main procedure endpoint
            response = self.session.get(f"{self.base_url}/api/procedures/{procedure_id}")
            print(f"Procedure endpoint response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedure = data.get("data", {})
                    print(f"✅ Successfully retrieved: {procedure.get('name', 'Unknown')}")
                    self.display_complete_iv_sedation_content(procedure)
                    return
                else:
                    print(f"❌ API returned success=false: {data}")
            else:
                print(f"❌ Procedure endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error with procedure endpoint: {str(e)}")
        
        # Try alternative endpoints
        print(f"\n🔄 Trying public endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/public/procedures/{procedure_id}")
            print(f"Public endpoint response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedure = data.get("data", {})
                    print(f"✅ Successfully retrieved from public endpoint: {procedure.get('name', 'Unknown')}")
                    self.display_complete_iv_sedation_content(procedure)
                    return
                    
        except Exception as e:
            print(f"❌ Error with public endpoint: {str(e)}")
            
        print("❌ CRITICAL: Could not retrieve IV Sedation procedure from any endpoint")
    
    def display_complete_iv_sedation_content(self, procedure: Dict[str, Any]) -> None:
        """Display the COMPLETE IV Sedation content as requested"""
        if not procedure:
            print("❌ No procedure data to display")
            return
            
        print(f"\n📋 COMPLETE IV SEDATION CONTENT ANALYSIS")
        print("=" * 80)
        
        # Basic info
        print(f"Procedure ID: {procedure.get('id', 'N/A')}")
        print(f"Procedure Name: {procedure.get('name', 'N/A')}")
        print(f"Specialty: {procedure.get('specialtyName', 'N/A')} ({procedure.get('specialty', 'N/A')})")
        print(f"Duration: {procedure.get('duration', 'N/A')}")
        
        # COMPLETE overview content - this is what the user needs to see
        overview = procedure.get('overview', '')
        print(f"\n📄 COMPLETE OVERVIEW FIELD CONTENT:")
        print("=" * 60)
        print(f"Character Count: {len(overview)}")
        print("=" * 60)
        
        if overview:
            print(overview)
        else:
            print("❌ NO OVERVIEW CONTENT FOUND - THIS EXPLAINS THE MISSING PDF CONTENT")
        
        print("=" * 60)
        print("END OF COMPLETE OVERVIEW CONTENT")
        
        # Check structured fields as well
        print(f"\n📊 STRUCTURED MEDICAL CONTENT FIELDS:")
        print("-" * 50)
        
        structured_fields = [
            ('immediateAftercare', '🚨 IMMEDIATE AFTERCARE'),
            ('dietRestrictions', '🍽️ DIET RESTRICTIONS'),
            ('warningSignsToCallDoctor', '⚠️ WARNING SIGNS'),
            ('recoveryTimeline', '📅 RECOVERY TIMELINE'),
            ('medications', '💊 MEDICATIONS')
        ]
        
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
                        # Show full content for IV Sedation analysis
                        item_str = str(item)
                        print(f"   {i}. {item_str}")
            elif isinstance(field_data, list):
                print(f"   ❌ EMPTY LIST")
            else:
                print(f"   ❌ INVALID FORMAT: {type(field_data)} - {field_data}")
        
        # Compare with expected IV Sedation content
        self.verify_expected_iv_sedation_sections(overview)
    
    def verify_expected_iv_sedation_sections(self, overview_content: str) -> None:
        """Verify if the overview contains expected IV Sedation sections"""
        print(f"\n🔍 VERIFICATION AGAINST EXPECTED IV SEDATION CONTENT")
        print("=" * 80)
        
        expected_sections = [
            "Purpose:",
            "First 24 Hours:",
            "Pain & Swelling:",
            "Diet:",
            "Activity:",
            "Special Precautions:",
            "Follow-Up:"
        ]
        
        expected_keywords = [
            "intravenous sedation", "safe", "comfortable", "dental treatment",
            "responsible adult", "remain with you", "24 hours",
            "pain medication", "prescribed", "approved",
            "clear liquids", "start with", "diet",
            "rest", "day of procedure", "activity",
            "medications listed", "precautions",
            "contact the office", "fever", "101°F", "follow-up"
        ]
        
        print("🎯 CHECKING FOR EXPECTED IV SEDATION SECTIONS:")
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
        
        print("\n🎯 CHECKING FOR EXPECTED IV SEDATION KEYWORDS:")
        found_keywords = []
        missing_keywords = []
        
        overview_lower = overview_content.lower()
        for keyword in expected_keywords:
            if keyword.lower() in overview_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        print(f"✅ Found keywords ({len(found_keywords)}/{len(expected_keywords)}): {', '.join(found_keywords[:15])}{'...' if len(found_keywords) > 15 else ''}")
        if missing_keywords:
            print(f"❌ Missing keywords ({len(missing_keywords)}): {', '.join(missing_keywords[:15])}{'...' if len(missing_keywords) > 15 else ''}")
        
        # Content completeness analysis
        print(f"\n📝 CONTENT COMPLETENESS ANALYSIS:")
        print(f"Total characters: {len(overview_content)}")
        lines = overview_content.split('\n')
        print(f"Total lines: {len(lines)}")
        print(f"Non-empty lines: {len([line for line in lines if line.strip()])}")
        
        # Determine if content is complete or truncated
        has_expected_sections = len(found_sections) >= 5  # At least 5 of the 7 expected sections
        has_sufficient_keywords = len(found_keywords) >= len(expected_keywords) * 0.6  # At least 60% of keywords
        has_reasonable_length = len(overview_content) >= 1000  # IV Sedation should be comprehensive
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if has_expected_sections and has_sufficient_keywords and has_reasonable_length:
            print("✅ CONTENT APPEARS COMPLETE - Database contains comprehensive IV Sedation content")
        elif has_expected_sections and has_sufficient_keywords:
            print("⚠️ CONTENT MAY BE TRUNCATED - Structure and keywords present but content seems short")
        elif has_expected_sections:
            print("⚠️ PARTIAL CONTENT - Structure present but missing key IV Sedation information")
        elif len(overview_content) < 500:
            print("❌ CONTENT SEVERELY TRUNCATED OR MISSING - This explains incomplete PDFs")
        else:
            print("❌ CONTENT DOES NOT MATCH EXPECTED IV SEDATION FORMAT")
            
        # Show content preview for diagnosis
        if len(overview_content) > 0:
            print(f"\n📄 CONTENT PREVIEW (First 300 characters):")
            print("-" * 50)
            print(overview_content[:300] + ("..." if len(overview_content) > 300 else ""))
            
            if len(overview_content) > 300:
                print(f"\n📄 CONTENT ENDING (Last 200 characters):")
                print("-" * 50)
                print("..." + overview_content[-200:])

def main():
    """Main testing function"""
    print("🦷 CRITICAL: IV SEDATION CONTENT VERIFICATION")
    print("=" * 80)
    print("URGENT REQUEST: Check IV Sedation content - User reports missing most PDF content")
    print("Backend URL: https://dentist-portal-3.emergent.host/api")
    print("Testing: GET /api/procedures/iv-sedation")
    print("Authentication: cganz2279@gmail.com/password123")
    
    tester = IVSedationContentTester()
    
    # Authenticate with specified credentials
    print(f"\n🔐 Authenticating as requested...")
    if not tester.authenticate(TEST_EMAIL, TEST_PASSWORD):
        print("❌ Authentication failed. Continuing with unauthenticated requests...")
    else:
        print("✅ Authentication successful. Proceeding with IV Sedation content check...")
    
    # Test the IV Sedation procedure content
    tester.test_iv_sedation_content()
    
    print(f"\n🎯 IV SEDATION CONTENT CHECK COMPLETE")
    print("=" * 80)
    print("REVIEW THE COMPLETE OVERVIEW CONTENT ABOVE")
    print("Expected sections: Purpose, First 24 Hours, Pain & Swelling, Diet, Activity, Special Precautions, Follow-Up")
    print("If content is missing or truncated, this explains why PDFs are incomplete.")

if __name__ == "__main__":
    main()