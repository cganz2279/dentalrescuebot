#!/usr/bin/env python3
"""
DETAILED DIETRESTRICTIONS CORRUPTION INVESTIGATION
Specific investigation of dietRestrictions field corruption as requested in review
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Use production backend URL from frontend .env
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

# Test credentials from review request
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class DietRestrictionsInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with test credentials"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                print(f"✅ Authentication successful with {TEST_EMAIL}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_procedure_details(self, procedure_id: str) -> Dict[str, Any]:
        """Get detailed procedure information"""
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                print(f"❌ Failed to get procedure {procedure_id}: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting procedure {procedure_id}: {str(e)}")
            return {}
    
    def analyze_diet_restrictions(self, procedure_name: str, diet_restrictions: List[str]) -> Dict[str, Any]:
        """Analyze dietRestrictions content for corruption patterns"""
        analysis = {
            'procedure_name': procedure_name,
            'total_items': len(diet_restrictions),
            'total_characters': sum(len(item) for item in diet_restrictions),
            'corruption_indicators': [],
            'content_preview': [],
            'likely_source_fields': []
        }
        
        # Check for corruption indicators
        for i, item in enumerate(diet_restrictions):
            # Store first 100 characters of each item for preview
            analysis['content_preview'].append({
                'item_number': i + 1,
                'first_100_chars': item[:100] + "..." if len(item) > 100 else item,
                'total_length': len(item)
            })
            
            # Check for aftercare content
            if any(keyword in item.lower() for keyword in ['rinse', 'brush', 'floss', 'mouthwash', 'oral hygiene']):
                analysis['corruption_indicators'].append(f"Item {i+1}: Contains oral hygiene/aftercare content")
                analysis['likely_source_fields'].append('immediateAftercare')
            
            # Check for pain management content
            if any(keyword in item.lower() for keyword in ['pain', 'medication', 'ibuprofen', 'acetaminophen', 'prescription']):
                analysis['corruption_indicators'].append(f"Item {i+1}: Contains pain/medication content")
                analysis['likely_source_fields'].append('medications')
            
            # Check for warning signs content
            if any(keyword in item.lower() for keyword in ['call', 'doctor', 'emergency', 'bleeding', 'swelling', 'fever']):
                analysis['corruption_indicators'].append(f"Item {i+1}: Contains warning signs content")
                analysis['likely_source_fields'].append('warningSignsToCallDoctor')
            
            # Check for timeline content
            if any(keyword in item.lower() for keyword in ['day', 'week', 'hours', 'first', 'second', 'third']):
                analysis['corruption_indicators'].append(f"Item {i+1}: Contains timeline content")
                analysis['likely_source_fields'].append('recoveryTimeline')
        
        # Remove duplicates from likely source fields
        analysis['likely_source_fields'] = list(set(analysis['likely_source_fields']))
        
        return analysis
    
    def investigate_biopsy_oral_soft_tissue(self):
        """Investigate the specific Biopsy Oral Soft Tissue procedure"""
        print("\n" + "="*80)
        print("🔍 INVESTIGATING BIOPSY ORAL SOFT TISSUE PROCEDURE")
        print("="*80)
        
        procedure = self.get_procedure_details("biopsy-oral-soft-tissue")
        
        if not procedure:
            print("❌ Could not retrieve Biopsy Oral Soft Tissue procedure")
            return
        
        diet_restrictions = procedure.get('dietRestrictions', [])
        
        print(f"📋 Procedure Name: {procedure.get('name', 'Unknown')}")
        print(f"🏥 Specialty: {procedure.get('specialtyName', 'Unknown')}")
        print(f"📊 Total dietRestrictions items: {len(diet_restrictions)}")
        print(f"📏 Total characters in dietRestrictions: {sum(len(item) for item in diet_restrictions)}")
        
        print("\n🔍 RAW DIETRESTRICTIONS CONTENT:")
        print("-" * 50)
        
        for i, item in enumerate(diet_restrictions, 1):
            print(f"\nItem {i} ({len(item)} characters):")
            print(f"First 200 chars: {item[:200]}{'...' if len(item) > 200 else ''}")
            
            if len(item) > 200:
                print(f"Last 100 chars: ...{item[-100:]}")
        
        # Analyze corruption
        analysis = self.analyze_diet_restrictions(procedure.get('name', 'Unknown'), diet_restrictions)
        
        print(f"\n🚨 CORRUPTION ANALYSIS:")
        print(f"Total corruption indicators found: {len(analysis['corruption_indicators'])}")
        
        for indicator in analysis['corruption_indicators']:
            print(f"  • {indicator}")
        
        if analysis['likely_source_fields']:
            print(f"\n🎯 Likely source fields for corrupted content:")
            for field in analysis['likely_source_fields']:
                print(f"  • {field}")
        
        return analysis
    
    def sample_procedures_investigation(self):
        """Sample 5 procedures and analyze their dietRestrictions"""
        print("\n" + "="*80)
        print("📊 SAMPLING 5 PROCEDURES FOR DIETRESTRICTIONS ANALYSIS")
        print("="*80)
        
        # Get list of procedures first
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures")
            if response.status_code != 200:
                print(f"❌ Failed to get procedures list: {response.status_code}")
                return
            
            procedures_data = response.json().get('data', [])
            
            # Sample 5 procedures (including some specific ones)
            sample_procedures = [
                "root-canal-therapy",
                "dental-implant-placement", 
                "tooth-extraction",
                "dental-crown-placement",
                "biopsy-oral-soft-tissue"
            ]
            
            results = []
            
            for proc_id in sample_procedures:
                print(f"\n🔍 Analyzing: {proc_id}")
                print("-" * 40)
                
                procedure = self.get_procedure_details(proc_id)
                if not procedure:
                    print(f"❌ Could not retrieve {proc_id}")
                    continue
                
                diet_restrictions = procedure.get('dietRestrictions', [])
                analysis = self.analyze_diet_restrictions(procedure.get('name', proc_id), diet_restrictions)
                
                print(f"📋 Name: {procedure.get('name', 'Unknown')}")
                print(f"📊 Items: {len(diet_restrictions)}")
                print(f"📏 Total chars: {sum(len(item) for item in diet_restrictions)}")
                
                if analysis['corruption_indicators']:
                    print(f"🚨 Corruption detected: {len(analysis['corruption_indicators'])} indicators")
                    for indicator in analysis['corruption_indicators'][:3]:  # Show first 3
                        print(f"  • {indicator}")
                else:
                    print("✅ No obvious corruption detected")
                
                # Show first item preview
                if diet_restrictions:
                    first_item = diet_restrictions[0]
                    print(f"📝 First item preview: {first_item[:100]}{'...' if len(first_item) > 100 else ''}")
                
                results.append(analysis)
            
            return results
            
        except Exception as e:
            print(f"❌ Error in sampling: {str(e)}")
            return []
    
    def test_specific_api_responses(self):
        """Test specific API endpoints as requested"""
        print("\n" + "="*80)
        print("🧪 TESTING SPECIFIC API RESPONSES")
        print("="*80)
        
        test_procedures = [
            "root-canal-therapy",
            "tooth-extraction", 
            "dental-implant-placement"
        ]
        
        for proc_id in test_procedures:
            print(f"\n🔍 Testing GET /api/procedures/{proc_id}")
            print("-" * 50)
            
            procedure = self.get_procedure_details(proc_id)
            
            if not procedure:
                print(f"❌ Failed to retrieve {proc_id}")
                continue
            
            diet_restrictions = procedure.get('dietRestrictions', [])
            
            print(f"✅ API Response received")
            print(f"📋 Procedure: {procedure.get('name', 'Unknown')}")
            print(f"📊 dietRestrictions items: {len(diet_restrictions)}")
            
            print(f"\n📝 EXACT DIETRESTRICTIONS CONTENT:")
            
            for i, item in enumerate(diet_restrictions, 1):
                print(f"\nItem {i}:")
                print(f"  Length: {len(item)} characters")
                print(f"  Content: {repr(item)}")  # Use repr to show exact string content
                
                if len(item) > 200:
                    print(f"  Preview: {item[:100]}...{item[-50:]}")
                else:
                    print(f"  Full text: {item}")
    
    def identify_corruption_pattern(self):
        """Identify the overall corruption pattern"""
        print("\n" + "="*80)
        print("🎯 CORRUPTION PATTERN IDENTIFICATION")
        print("="*80)
        
        # Get a broader sample of procedures
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures")
            if response.status_code != 200:
                print(f"❌ Failed to get procedures list")
                return
            
            procedures_list = response.json().get('data', [])
            
            print(f"📊 Total procedures available: {len(procedures_list)}")
            
            # Sample 10 procedures for pattern analysis
            sample_size = min(10, len(procedures_list))
            sample_procedures = procedures_list[:sample_size]
            
            corruption_stats = {
                'total_tested': 0,
                'corrupted_count': 0,
                'clean_count': 0,
                'corruption_types': {},
                'field_mixing_patterns': []
            }
            
            for proc_data in sample_procedures:
                proc_id = proc_data.get('id')
                if not proc_id:
                    continue
                
                procedure = self.get_procedure_details(proc_id)
                if not procedure:
                    continue
                
                corruption_stats['total_tested'] += 1
                
                diet_restrictions = procedure.get('dietRestrictions', [])
                analysis = self.analyze_diet_restrictions(procedure.get('name', proc_id), diet_restrictions)
                
                if analysis['corruption_indicators']:
                    corruption_stats['corrupted_count'] += 1
                    
                    # Track corruption types
                    for field in analysis['likely_source_fields']:
                        if field not in corruption_stats['corruption_types']:
                            corruption_stats['corruption_types'][field] = 0
                        corruption_stats['corruption_types'][field] += 1
                else:
                    corruption_stats['clean_count'] += 1
                    print(f"✅ CLEAN: {procedure.get('name', proc_id)}")
            
            # Report findings
            print(f"\n📈 CORRUPTION STATISTICS:")
            print(f"  Total tested: {corruption_stats['total_tested']}")
            print(f"  Corrupted: {corruption_stats['corrupted_count']}")
            print(f"  Clean: {corruption_stats['clean_count']}")
            
            if corruption_stats['total_tested'] > 0:
                corruption_rate = (corruption_stats['corrupted_count'] / corruption_stats['total_tested']) * 100
                print(f"  Corruption rate: {corruption_rate:.1f}%")
            
            print(f"\n🎯 CORRUPTION PATTERN:")
            if corruption_stats['corruption_types']:
                print("  dietRestrictions field contains content from:")
                for field, count in corruption_stats['corruption_types'].items():
                    print(f"    • {field}: {count} procedures")
            
            return corruption_stats
            
        except Exception as e:
            print(f"❌ Error in pattern identification: {str(e)}")
            return {}

def main():
    """Main investigation function"""
    print("🔍 DIETRESTRICTIONS CORRUPTION INVESTIGATION")
    print("=" * 80)
    print("Investigating exact content of corrupted dietRestrictions field")
    print("Authentication: cganz2279@gmail.com/password123")
    print("Backend URL: https://dentist-portal-3.emergent.host/api")
    
    investigator = DietRestrictionsInvestigator()
    
    # Step 1: Authenticate
    if not investigator.authenticate():
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Step 2: Investigate Biopsy Oral Soft Tissue specifically
    biopsy_analysis = investigator.investigate_biopsy_oral_soft_tissue()
    
    # Step 3: Sample 5 procedures
    sample_results = investigator.sample_procedures_investigation()
    
    # Step 4: Test specific API responses
    investigator.test_specific_api_responses()
    
    # Step 5: Identify corruption pattern
    pattern_stats = investigator.identify_corruption_pattern()
    
    # Final summary
    print("\n" + "="*80)
    print("📋 INVESTIGATION SUMMARY")
    print("="*80)
    
    if biopsy_analysis:
        print(f"🔍 Biopsy Oral Soft Tissue:")
        print(f"  • {len(biopsy_analysis.get('corruption_indicators', []))} corruption indicators")
        print(f"  • {biopsy_analysis.get('total_characters', 0)} total characters")
        print(f"  • Likely mixed from: {', '.join(biopsy_analysis.get('likely_source_fields', []))}")
    
    if pattern_stats:
        corruption_rate = 0
        if pattern_stats.get('total_tested', 0) > 0:
            corruption_rate = (pattern_stats.get('corrupted_count', 0) / pattern_stats.get('total_tested', 1)) * 100
        
        print(f"\n📊 Overall Pattern:")
        print(f"  • Corruption rate: {corruption_rate:.1f}%")
        print(f"  • Most common source: {max(pattern_stats.get('corruption_types', {}), key=pattern_stats.get('corruption_types', {}).get, default='Unknown')}")
    
    print(f"\n✅ Investigation completed successfully")

if __name__ == "__main__":
    main()