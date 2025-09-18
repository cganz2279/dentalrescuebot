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
    
    def test_specific_procedures(self) -> None:
        """Test the specific procedures requested in the review"""
        requested_procedures = [
            ("root-canal-therapy", "Root Canal Therapy"),
            ("dental-bridge-placement", "Dental Bridge Placement"),
            ("dental-implant-placement", "Dental Implant Placement")
        ]
        
        print(f"\n🎯 TESTING SPECIFIC PROCEDURES AS REQUESTED IN REVIEW")
        print("=" * 80)
        
        results = {}
        
        for procedure_id, procedure_name in requested_procedures:
            print(f"\n{'='*20} {procedure_name.upper()} {'='*20}")
            
            procedure_data = self.get_procedure_details(procedure_id)
            if procedure_data:
                self.analyze_procedure_content(procedure_data)
                self.compare_with_expected_content(procedure_data, procedure_name)
                results[procedure_name] = {
                    "found": True,
                    "has_overview": bool(procedure_data.get('overview')),
                    "has_structured_content": bool(
                        procedure_data.get('immediateAftercare') or
                        procedure_data.get('dietRestrictions') or
                        procedure_data.get('warningSignsToCallDoctor') or
                        procedure_data.get('recoveryTimeline') or
                        procedure_data.get('medications')
                    ),
                    "overview_length": len(procedure_data.get('overview', '')),
                    "structured_fields": {
                        'immediateAftercare': len(procedure_data.get('immediateAftercare', [])),
                        'dietRestrictions': len(procedure_data.get('dietRestrictions', [])),
                        'warningSignsToCallDoctor': len(procedure_data.get('warningSignsToCallDoctor', [])),
                        'recoveryTimeline': len(procedure_data.get('recoveryTimeline', [])),
                        'medications': len(procedure_data.get('medications', []))
                    }
                }
            else:
                results[procedure_name] = {"found": False}
        
        # Summary
        print(f"\n📊 SUMMARY OF REQUESTED PROCEDURES")
        print("=" * 80)
        
        for procedure_name, result in results.items():
            if result.get("found"):
                print(f"✅ {procedure_name}:")
                print(f"   Overview: {result['overview_length']} characters")
                print(f"   Structured Content: {result['has_structured_content']}")
                for field, count in result['structured_fields'].items():
                    print(f"   - {field}: {count} items")
            else:
                print(f"❌ {procedure_name}: NOT FOUND")

def main():
    """Main testing function"""
    print("🦷 DENTAL PRACTICE BACKEND TESTING - PROCEDURE DATABASE INVESTIGATION")
    print("=" * 80)
    print("Focus: Examining procedure database content as requested in review")
    print(f"Backend URL: {BACKEND_URL}")
    
    tester = DentalBackendTester()
    
    # Authenticate with specified credentials
    if not tester.authenticate("cganz2279@gmail.com", "password123"):
        print("❌ Authentication failed. Cannot proceed with testing.")
        sys.exit(1)
    
    # Test the specific procedures requested
    tester.test_specific_procedures()
    
    print(f"\n🎯 TESTING COMPLETE")
    print("=" * 80)
    print("Review the detailed analysis above to understand the current database content")
    print("and how it compares to the expected original PDF content.")

if __name__ == "__main__":
    main()