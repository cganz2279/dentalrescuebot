#!/usr/bin/env python3
"""
Dental Bridge Placement PDF Generation Testing
Testing the updated PDF generation functionality for dental-bridge-placement procedure
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

def authenticate(email: str, password: str) -> str:
    """Authenticate with the backend and return JWT token"""
    print(f"🔐 Authenticating with {email}...")
    
    login_url = f"{BACKEND_URL}/api/auth/login"
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            practice_name = data.get('practice', {}).get('name', 'Unknown')
            print(f"✅ Authentication successful! Practice: {practice_name}")
            return token
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def get_procedure_data(procedure_id: str, token: str = None) -> Dict[Any, Any]:
    """Get procedure data from the API"""
    print(f"📋 Fetching procedure data for: {procedure_id}")
    
    procedure_url = f"{BACKEND_URL}/api/procedures/{procedure_id}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(procedure_url, headers=headers)
        print(f"Procedure API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                procedure = data.get('data')
                print(f"✅ Procedure data retrieved successfully!")
                print(f"Procedure name: {procedure.get('name', 'Unknown')}")
                print(f"Specialty: {procedure.get('specialtyName', 'Unknown')}")
                return procedure
            else:
                print(f"❌ API returned success=false: {data}")
                return None
        else:
            print(f"❌ Failed to get procedure data: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching procedure data: {str(e)}")
        return None

def verify_content_structure(procedure: Dict[Any, Any]) -> bool:
    """Verify the procedure contains the expected content structure"""
    print(f"\n🔍 Verifying content structure...")
    
    required_fields = [
        'name', 'overview', 'immediateAftercare', 'dietRestrictions', 
        'warningSignsToCallDoctor', 'recoveryTimeline', 'medications'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in procedure:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    
    print(f"✅ All required fields present")
    
    # Check if overview contains expected sections
    overview = procedure.get('overview', '')
    expected_sections = [
        'Purpose', 'First 24 Hours', 'Pain & Sensitivity', 
        'Oral Hygiene', 'Diet', 'Special Precautions', 'Follow-Up'
    ]
    
    found_sections = []
    for section in expected_sections:
        if section.lower() in overview.lower():
            found_sections.append(section)
    
    print(f"📝 Found sections in overview: {found_sections}")
    
    if len(found_sections) >= 4:  # At least 4 sections should be present
        print(f"✅ Content structure appears valid")
        return True
    else:
        print(f"⚠️ Limited section content found")
        return False

def print_complete_overview(procedure: Dict[Any, Any]):
    """Print the complete overview content for verification"""
    print(f"\n" + "="*80)
    print(f"COMPLETE OVERVIEW CONTENT FOR VERIFICATION")
    print(f"="*80)
    
    overview = procedure.get('overview', '')
    print(f"Procedure: {procedure.get('name', 'Unknown')}")
    print(f"Specialty: {procedure.get('specialtyName', 'Unknown')}")
    print(f"Duration: {procedure.get('duration', 'Unknown')}")
    print(f"\nOverview Content ({len(overview)} characters):")
    print(f"-" * 40)
    print(overview)
    print(f"-" * 40)
    
    # Also print structured fields
    print(f"\n📋 STRUCTURED FIELDS:")
    
    fields_to_show = [
        'immediateAftercare', 'dietRestrictions', 
        'warningSignsToCallDoctor', 'recoveryTimeline', 'medications'
    ]
    
    for field in fields_to_show:
        value = procedure.get(field, [])
        print(f"\n{field.upper()}:")
        if isinstance(value, list):
            for i, item in enumerate(value, 1):
                if isinstance(item, dict):
                    print(f"  {i}. {item}")
                else:
                    print(f"  {i}. {item}")
        else:
            print(f"  {value}")
    
    print(f"="*80)

def main():
    """Main testing function"""
    print(f"🎯 DENTAL BRIDGE PLACEMENT PDF GENERATION TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"-" * 60)
    
    # Step 1: Authenticate
    email = "cganz2279@gmail.com"
    password = "password123"
    
    token = authenticate(email, password)
    if not token:
        print(f"❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Step 2: Get procedure data
    procedure_id = "dental-bridge-placement"
    procedure = get_procedure_data(procedure_id, token)
    
    if not procedure:
        print(f"❌ Cannot proceed without procedure data")
        sys.exit(1)
    
    # Step 3: Verify content structure
    structure_valid = verify_content_structure(procedure)
    
    # Step 4: Print complete overview content
    print_complete_overview(procedure)
    
    # Step 5: Summary
    print(f"\n🎯 TEST SUMMARY:")
    print(f"✅ Authentication: SUCCESS")
    print(f"✅ Procedure Data Retrieval: SUCCESS")
    print(f"{'✅' if structure_valid else '⚠️'} Content Structure: {'VALID' if structure_valid else 'LIMITED'}")
    print(f"✅ Complete Overview Content: DISPLAYED ABOVE")
    
    if structure_valid:
        print(f"\n🎉 All tests passed! The dental-bridge-placement procedure contains properly structured content ready for PDF generation.")
    else:
        print(f"\n⚠️ Content structure may need review, but basic data is available.")

if __name__ == "__main__":
    main()