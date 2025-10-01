#!/usr/bin/env python3
"""
Enhanced PDF Generation Backend Verification Test
=================================================

This test verifies that the backend provides complete data structure 
for enhanced PDF generation with color-coded sections and professional styling.

Review Request Requirements:
1. Verify procedure data is accessible via API endpoints
2. Test that backend provides complete data structure for PDF generation  
3. Check that all required fields are present for enhanced styling

Key Endpoints:
- GET /api/procedures/root-canal-therapy
- GET /api/procedures/dental-implant-placement
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dental-admin-3.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 Enhanced PDF Generation Backend Verification")
print(f"📡 Testing Backend: {API_BASE}")
print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

def test_procedure_data_structure(procedure_id, procedure_name):
    """Test that procedure provides complete data structure for enhanced PDF generation"""
    print(f"\n🧪 Testing {procedure_name} Data Structure")
    print(f"📋 Endpoint: GET /api/procedures/{procedure_id}")
    
    try:
        response = requests.get(f"{API_BASE}/procedures/{procedure_id}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            return False
            
        data = response.json()
        
        # Verify response structure
        if not data.get('success'):
            print(f"❌ FAILED: Response success is {data.get('success')}")
            return False
            
        procedure = data.get('data')
        if not procedure:
            print("❌ FAILED: No procedure data in response")
            return False
            
        print(f"✅ SUCCESS: Valid response structure")
        
        # Check required fields for enhanced PDF generation
        required_fields = [
            'id', 'name', 'specialty', 'specialtyName', 'duration',
            'overview', 'immediateAftercare', 'dietRestrictions', 
            'warningSignsToCallDoctor', 'recoveryTimeline', 'medications'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in procedure:
                missing_fields.append(field)
                
        if missing_fields:
            print(f"❌ FAILED: Missing required fields: {missing_fields}")
            return False
            
        print(f"✅ SUCCESS: All required fields present")
        
        # Verify data structure for color-coded sections
        sections_data = {
            'Green (Aftercare)': procedure.get('immediateAftercare', []),
            'Orange (Diet)': procedure.get('dietRestrictions', []),
            'Red (Warnings)': procedure.get('warningSignsToCallDoctor', []),
            'Purple (Timeline)': procedure.get('recoveryTimeline', []),
            'Blue (Medications)': procedure.get('medications', [])
        }
        
        print(f"\n📋 Enhanced PDF Data Structure Analysis:")
        for section_name, section_data in sections_data.items():
            if isinstance(section_data, list):
                count = len(section_data)
                print(f"   {section_name}: {count} items")
                if count == 0:
                    print(f"   ⚠️  WARNING: {section_name} section is empty")
            else:
                print(f"   {section_name}: {type(section_data).__name__} (not list)")
                
        # Verify procedure-specific content (not generic)
        procedure_name_lower = procedure_name.lower()
        overview = procedure.get('overview', '').lower()
        
        # Check for procedure-specific terminology
        specific_terms = {
            'root canal': ['root canal', 'pulp', 'endodontic', 'canal'],
            'dental implant': ['implant', 'titanium', 'surgical', 'osseointegration']
        }
        
        found_terms = []
        for procedure_type, terms in specific_terms.items():
            if procedure_type in procedure_name_lower:
                for term in terms:
                    if term in overview:
                        found_terms.append(term)
                        
        if found_terms:
            print(f"✅ SUCCESS: Procedure-specific content verified (found: {', '.join(found_terms)})")
        else:
            print(f"⚠️  WARNING: No procedure-specific terminology found in overview")
            
        # Verify content is not generic placeholder
        generic_indicators = ['lorem ipsum', 'placeholder', 'sample text', 'generic']
        is_generic = any(indicator in overview for indicator in generic_indicators)
        
        if is_generic:
            print(f"❌ FAILED: Content appears to be generic placeholder")
            return False
        else:
            print(f"✅ SUCCESS: Content appears to be procedure-specific")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: Network error - {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON response - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {str(e)}")
        return False

def test_enhanced_pdf_data_completeness():
    """Test that all procedures have sufficient data for enhanced PDF generation"""
    print(f"\n🧪 Testing Enhanced PDF Data Completeness")
    print(f"📋 Endpoint: GET /api/procedures")
    
    try:
        response = requests.get(f"{API_BASE}/procedures")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            return False
            
        data = response.json()
        procedures = data.get('data', [])
        
        print(f"📋 Total Procedures: {len(procedures)}")
        
        # Sample a few procedures to verify data completeness
        sample_procedures = procedures[:5] if len(procedures) >= 5 else procedures
        
        complete_procedures = 0
        for procedure in sample_procedures:
            has_all_sections = all([
                procedure.get('immediateAftercare'),
                procedure.get('dietRestrictions'),
                procedure.get('warningSignsToCallDoctor'),
                procedure.get('recoveryTimeline'),
                procedure.get('medications')
            ])
            
            if has_all_sections:
                complete_procedures += 1
                
        completion_rate = (complete_procedures / len(sample_procedures)) * 100 if sample_procedures else 0
        print(f"📊 Data Completeness: {complete_procedures}/{len(sample_procedures)} ({completion_rate:.1f}%)")
        
        if completion_rate >= 80:
            print(f"✅ SUCCESS: High data completeness for enhanced PDF generation")
            return True
        else:
            print(f"⚠️  WARNING: Low data completeness may affect PDF quality")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error testing data completeness - {str(e)}")
        return False

def main():
    """Run all enhanced PDF backend verification tests"""
    print("🚀 Starting Enhanced PDF Generation Backend Verification Tests")
    
    test_results = []
    
    # Test specific procedures mentioned in review request
    test_cases = [
        ('root-canal-therapy', 'Root Canal Therapy'),
        ('dental-implant-placement', 'Dental Implant Placement')
    ]
    
    for procedure_id, procedure_name in test_cases:
        result = test_procedure_data_structure(procedure_id, procedure_name)
        test_results.append((f"{procedure_name} Data Structure", result))
        
    # Test overall data completeness
    result = test_enhanced_pdf_data_completeness()
    test_results.append(("Enhanced PDF Data Completeness", result))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ENHANCED PDF BACKEND VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if passed:
            passed_tests += 1
            
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n📈 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 ALL TESTS PASSED: Backend provides complete data for enhanced PDF generation")
        return True
    elif success_rate >= 80:
        print("⚠️  MOSTLY SUCCESSFUL: Minor issues detected but core functionality working")
        return True
    else:
        print("❌ CRITICAL ISSUES: Backend data structure insufficient for enhanced PDF generation")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)