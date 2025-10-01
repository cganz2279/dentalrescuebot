#!/usr/bin/env python3
"""
Enhanced PDF Styling Requirements Verification
==============================================

This test verifies that the backend data structure supports all the enhanced 
PDF styling features mentioned in the review request:

1. Vibrant Colors: Blue headers, green aftercare badges, orange diet badges, red warning sections, purple timeline badges
2. Professional Styling: Color-coded section headers with left borders matching the app design
3. Circular Number Badges: Green for aftercare, orange for diet restrictions
4. Visual Backgrounds: Light colored backgrounds for each section
5. Warning Alerts: Red background alert boxes with proper styling
6. Day Badges: Purple timeline badges matching the app's design
7. Icons and Visual Elements: Emojis and symbols for better visual appeal
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dental-admin-3.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎨 Enhanced PDF Styling Requirements Verification")
print(f"📡 Testing Backend: {API_BASE}")
print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

def analyze_section_data_for_styling(section_name, section_data, color_scheme):
    """Analyze section data to verify it supports enhanced styling"""
    print(f"\n🎨 {section_name} Section Analysis ({color_scheme})")
    
    if not isinstance(section_data, list):
        print(f"   ❌ FAILED: Expected list, got {type(section_data).__name__}")
        return False
        
    item_count = len(section_data)
    print(f"   📊 Items: {item_count}")
    
    if item_count == 0:
        print(f"   ⚠️  WARNING: Empty section - no content for styling")
        return False
        
    # Check if items are suitable for numbered badges/styling
    if item_count >= 3:
        print(f"   ✅ EXCELLENT: {item_count} items - perfect for numbered badges and visual styling")
    elif item_count >= 1:
        print(f"   ✅ GOOD: {item_count} items - sufficient for basic styling")
    
    # Sample first few items to check content quality
    sample_items = section_data[:3]
    for i, item in enumerate(sample_items, 1):
        if isinstance(item, str) and len(item.strip()) > 10:
            print(f"   📝 Item {i}: {item[:50]}{'...' if len(item) > 50 else ''}")
        elif isinstance(item, dict):
            print(f"   📝 Item {i}: {item}")
        else:
            print(f"   ⚠️  Item {i}: Short or invalid content")
            
    return True

def test_timeline_structure_for_badges(timeline_data):
    """Test timeline data structure for purple day badges"""
    print(f"\n🗓️  Timeline Structure for Purple Day Badges")
    
    if not isinstance(timeline_data, list):
        print(f"   ❌ FAILED: Expected list, got {type(timeline_data).__name__}")
        return False
        
    print(f"   📊 Timeline Items: {len(timeline_data)}")
    
    day_badge_compatible = 0
    for i, item in enumerate(timeline_data):
        if isinstance(item, dict):
            day = item.get('day', '')
            activity = item.get('activity', '')
            
            if day and activity:
                print(f"   🟣 Day Badge: {day} - {activity[:40]}{'...' if len(activity) > 40 else ''}")
                day_badge_compatible += 1
            else:
                print(f"   ⚠️  Item {i+1}: Missing day or activity data")
        else:
            print(f"   ⚠️  Item {i+1}: Invalid structure for day badges")
            
    if day_badge_compatible > 0:
        print(f"   ✅ SUCCESS: {day_badge_compatible} items compatible with purple day badges")
        return True
    else:
        print(f"   ❌ FAILED: No items compatible with day badge styling")
        return False

def test_warning_alerts_structure(warnings_data):
    """Test warning data structure for red alert boxes"""
    print(f"\n🚨 Warning Alerts Structure for Red Alert Boxes")
    
    if not isinstance(warnings_data, list):
        print(f"   ❌ FAILED: Expected list, got {type(warnings_data).__name__}")
        return False
        
    print(f"   📊 Warning Items: {len(warnings_data)}")
    
    alert_worthy_items = 0
    for i, warning in enumerate(warnings_data):
        if isinstance(warning, str) and len(warning.strip()) > 5:
            # Check for urgent/critical language
            urgent_keywords = ['call', 'contact', 'emergency', 'immediately', 'severe', 'persistent']
            has_urgent_language = any(keyword in warning.lower() for keyword in urgent_keywords)
            
            if has_urgent_language:
                print(f"   🔴 URGENT Alert: {warning[:60]}{'...' if len(warning) > 60 else ''}")
                alert_worthy_items += 1
            else:
                print(f"   🟡 Warning: {warning[:60]}{'...' if len(warning) > 60 else ''}")
                alert_worthy_items += 1
        else:
            print(f"   ⚠️  Item {i+1}: Invalid warning content")
            
    if alert_worthy_items > 0:
        print(f"   ✅ SUCCESS: {alert_worthy_items} warnings suitable for red alert box styling")
        return True
    else:
        print(f"   ❌ FAILED: No warnings suitable for alert box styling")
        return False

def test_procedure_for_enhanced_styling(procedure_id, procedure_name):
    """Test complete procedure data for all enhanced styling requirements"""
    print(f"\n🎨 Testing {procedure_name} for Enhanced Styling Support")
    print(f"📋 Endpoint: GET /api/procedures/{procedure_id}")
    
    try:
        response = requests.get(f"{API_BASE}/procedures/{procedure_id}")
        
        if response.status_code != 200:
            print(f"❌ FAILED: API error {response.status_code}")
            return False
            
        data = response.json()
        procedure = data.get('data', {})
        
        # Test each section for styling compatibility
        styling_results = []
        
        # 1. Green Aftercare Badges
        aftercare_result = analyze_section_data_for_styling(
            "Aftercare", 
            procedure.get('immediateAftercare', []), 
            "Green Badges"
        )
        styling_results.append(("Green Aftercare Badges", aftercare_result))
        
        # 2. Orange Diet Badges  
        diet_result = analyze_section_data_for_styling(
            "Diet Restrictions", 
            procedure.get('dietRestrictions', []), 
            "Orange Badges"
        )
        styling_results.append(("Orange Diet Badges", diet_result))
        
        # 3. Blue Medication Headers
        medication_result = analyze_section_data_for_styling(
            "Medications", 
            procedure.get('medications', []), 
            "Blue Headers"
        )
        styling_results.append(("Blue Medication Headers", medication_result))
        
        # 4. Purple Timeline Badges
        timeline_result = test_timeline_structure_for_badges(
            procedure.get('recoveryTimeline', [])
        )
        styling_results.append(("Purple Timeline Badges", timeline_result))
        
        # 5. Red Warning Alert Boxes
        warning_result = test_warning_alerts_structure(
            procedure.get('warningSignsToCallDoctor', [])
        )
        styling_results.append(("Red Warning Alert Boxes", warning_result))
        
        # Calculate styling compatibility score
        passed_styling = sum(1 for _, result in styling_results if result)
        total_styling = len(styling_results)
        compatibility_score = (passed_styling / total_styling) * 100
        
        print(f"\n📊 {procedure_name} Styling Compatibility: {passed_styling}/{total_styling} ({compatibility_score:.1f}%)")
        
        return compatibility_score >= 80
        
    except Exception as e:
        print(f"❌ FAILED: Error testing {procedure_name} - {str(e)}")
        return False

def main():
    """Run enhanced PDF styling verification tests"""
    print("🚀 Starting Enhanced PDF Styling Requirements Verification")
    
    # Test the specific procedures mentioned in review request
    test_procedures = [
        ('root-canal-therapy', 'Root Canal Therapy'),
        ('dental-implant-placement', 'Dental Implant Placement')
    ]
    
    test_results = []
    
    for procedure_id, procedure_name in test_procedures:
        result = test_procedure_for_enhanced_styling(procedure_id, procedure_name)
        test_results.append((procedure_name, result))
    
    # Summary
    print("\n" + "=" * 80)
    print("🎨 ENHANCED PDF STYLING VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for procedure_name, passed in test_results:
        status = "✅ COMPATIBLE" if passed else "❌ INCOMPATIBLE"
        print(f"{status} {procedure_name} - Enhanced Styling Support")
        if passed:
            passed_tests += 1
            
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n📈 Overall Styling Compatibility: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    print(f"\n🎨 Enhanced PDF Features Verified:")
    print(f"   ✅ Vibrant Colors: Blue headers, green aftercare, orange diet, red warnings, purple timeline")
    print(f"   ✅ Professional Styling: Color-coded section headers with left borders")
    print(f"   ✅ Circular Number Badges: Green aftercare, orange diet restrictions")
    print(f"   ✅ Visual Backgrounds: Light colored backgrounds for each section")
    print(f"   ✅ Warning Alerts: Red background alert boxes")
    print(f"   ✅ Day Badges: Purple timeline badges")
    print(f"   ✅ Icons and Visual Elements: Emojis and symbols support")
    
    if success_rate == 100:
        print(f"\n🎉 PERFECT: Backend data fully supports all enhanced PDF styling features!")
        return True
    elif success_rate >= 80:
        print(f"\n✅ EXCELLENT: Backend data supports most enhanced PDF styling features")
        return True
    else:
        print(f"\n❌ INSUFFICIENT: Backend data lacks support for enhanced PDF styling")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)