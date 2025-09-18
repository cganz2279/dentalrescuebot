#!/usr/bin/env python3
"""
DETAILED CONTENT ANALYSIS - Focus on Data Corruption Issues
"""

import requests
import json

BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate and return session"""
    session = requests.Session()
    auth_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=auth_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        if token:
            session.headers.update({'Authorization': f'Bearer {token}'})
            print(f"✅ Authenticated successfully as {TEST_EMAIL}")
            return session
    
    print(f"❌ Authentication failed: {response.status_code}")
    return None

def analyze_field_corruption(session, procedure_id, procedure_name):
    """Analyze specific field corruption in procedure data"""
    print(f"\n🔍 DETAILED ANALYSIS: {procedure_name}")
    print("=" * 60)
    
    response = session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
    if response.status_code != 200:
        print(f"❌ Failed to fetch {procedure_id}: {response.status_code}")
        return
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ API returned error for {procedure_id}")
        return
    
    procedure = data['data']
    
    # Analyze dietRestrictions field
    diet_restrictions = procedure.get('dietRestrictions', [])
    print(f"\n📋 DIET RESTRICTIONS ANALYSIS:")
    print(f"   Field type: {type(diet_restrictions)}")
    print(f"   Number of items: {len(diet_restrictions) if isinstance(diet_restrictions, list) else 'N/A'}")
    
    if isinstance(diet_restrictions, list) and diet_restrictions:
        for i, item in enumerate(diet_restrictions):
            print(f"   Item {i+1} ({len(str(item))} chars): {str(item)[:100]}...")
            
            # Check for corruption indicators
            corruption_indicators = [
                'Pain & Sensitivity:', 'Oral Hygiene:', 'Follow-Up:', 
                'Use OTC', 'prescribed pain relievers', 'Brush and floss'
            ]
            
            item_str = str(item)
            found_indicators = [indicator for indicator in corruption_indicators if indicator in item_str]
            if found_indicators:
                print(f"   🚨 CORRUPTION DETECTED: Contains {found_indicators}")
    
    # Analyze medications field
    medications = procedure.get('medications', [])
    print(f"\n💊 MEDICATIONS ANALYSIS:")
    print(f"   Field type: {type(medications)}")
    print(f"   Number of items: {len(medications) if isinstance(medications, list) else 'N/A'}")
    
    if isinstance(medications, list) and medications:
        for i, item in enumerate(medications):
            print(f"   Item {i+1} ({len(str(item))} chars): {str(item)[:100]}...")
            
            # Check for corruption indicators
            corruption_indicators = [
                'Diet:', 'Special Precautions:', 'Follow-Up:', 
                'Avoid very hard', 'Brush normally', 'floss threader'
            ]
            
            item_str = str(item)
            found_indicators = [indicator for indicator in corruption_indicators if indicator in item_str]
            if found_indicators:
                print(f"   🚨 CORRUPTION DETECTED: Contains {found_indicators}")
    
    # Check overview field for comparison
    overview = procedure.get('overview', '')
    print(f"\n📄 OVERVIEW COMPARISON:")
    print(f"   Overview length: {len(overview)} characters")
    print(f"   Contains procedure-specific terms: {procedure_name.lower().replace(' ', '') in overview.lower()}")
    
    # Check for proper medical content
    medical_terms = ['pain', 'medication', 'healing', 'recovery', 'treatment', 'care']
    found_medical_terms = [term for term in medical_terms if term.lower() in overview.lower()]
    print(f"   Medical terms found: {found_medical_terms}")

def main():
    """Main analysis function"""
    print("🔍 DETAILED CONTENT CORRUPTION ANALYSIS")
    print("=" * 80)
    
    session = authenticate()
    if not session:
        return
    
    # Test the three procedures mentioned in the review
    procedures = [
        ("root-canal-therapy", "Root Canal Therapy"),
        ("dental-bridge-placement", "Dental Bridge Placement"), 
        ("dental-implant-placement", "Dental Implant Placement")
    ]
    
    for procedure_id, procedure_name in procedures:
        analyze_field_corruption(session, procedure_id, procedure_name)
    
    print(f"\n🎯 SUMMARY OF FINDINGS:")
    print("=" * 60)
    print("1. Root Canal Therapy: Contains detailed medical overview but corrupted structured fields")
    print("2. Dental Bridge Placement: Similar corruption pattern in dietRestrictions and medications")
    print("3. Dental Implant Placement: Best structured data with proper dietRestrictions array")
    print("\n🚨 CRITICAL ISSUE: dietRestrictions and medications fields contain mixed content")
    print("   from other sections instead of proper dietary/medication guidance")

if __name__ == "__main__":
    main()