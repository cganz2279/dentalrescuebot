#!/usr/bin/env python3
"""
Detailed Procedure Content Check
Get the actual content of Root Canal procedure to see what's there
"""

import requests
import json
import sys

# Backend URL from frontend configuration
BACKEND_URL = "https://postop-care.preview.emergentagent.com/api"

def authenticate():
    """Authenticate and get token"""
    session = requests.Session()
    
    try:
        response = session.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": "cganz2279@gmail.com",
                "password": "password123"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                token = data["token"]
                session.headers.update({
                    "Authorization": f"Bearer {token}"
                })
                print(f"✅ Authenticated as {data.get('user', {}).get('email')}")
                return session
        
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def check_procedure_detailed(session, procedure_id):
    """Get detailed procedure information"""
    print(f"\n🔍 Checking procedure: {procedure_id}")
    print("=" * 60)
    
    try:
        response = session.get(f"{BACKEND_URL}/procedures/{procedure_id}")
        
        if response.status_code == 200:
            data = response.json()
            procedure = data.get("data", {}) if data.get("success") else data
            
            print(f"✅ Successfully retrieved {procedure_id}")
            print(f"Response structure: {data.get('success', 'No success field')}")
            print()
            
            # Print all available fields
            print("📋 Available fields:")
            for key, value in procedure.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
                else:
                    print(f"  {key}: {type(value).__name__} (length: {len(str(value)) if value else 0})")
            print()
            
            # Check specific fields mentioned in review
            required_fields = [
                "immediateAftercare",
                "dietRestrictions", 
                "warningSignsToCallDoctor",
                "recoveryTimeline",
                "medications"
            ]
            
            print("🎯 Required medical content fields:")
            for field in required_fields:
                value = procedure.get(field)
                if value:
                    print(f"  ✅ {field}: {type(value).__name__} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
                    if isinstance(value, list) and len(value) > 0:
                        print(f"      First item: {str(value[0])[:100]}...")
                    elif isinstance(value, str):
                        print(f"      Content: {value[:100]}...")
                else:
                    print(f"  ❌ {field}: Missing or empty")
            print()
            
            # Check for generic content indicators
            content_str = json.dumps(procedure).lower()
            generic_indicators = [
                "test assignment from automated testing",
                "please follow all post-operative instructions carefully",
                "generic", "placeholder", "test content", "dummy"
            ]
            
            print("🚨 Generic content check:")
            found_generic = []
            for indicator in generic_indicators:
                if indicator in content_str:
                    found_generic.append(indicator)
                    print(f"  ⚠️  Found: '{indicator}'")
            
            if not found_generic:
                print("  ✅ No generic content indicators found")
            print()
            
            # Check for medical content indicators
            medical_indicators = [
                "root canal", "pulp", "endodontic", "canal", "tooth",
                "nerve", "infection", "antibiotics", "pain medication"
            ]
            
            print("🏥 Medical content check:")
            found_medical = []
            for indicator in medical_indicators:
                if indicator in content_str:
                    found_medical.append(indicator)
                    print(f"  ✅ Found: '{indicator}'")
            
            if not found_medical:
                print("  ❌ No medical content indicators found")
            print()
            
            # Show overview content
            overview = procedure.get("overview", "")
            if overview:
                print(f"📖 Overview content ({len(overview)} chars):")
                print(f"  {overview[:300]}...")
                print()
            
            return procedure
            
        else:
            print(f"❌ Failed to retrieve procedure: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking procedure: {str(e)}")
        return None

def main():
    print("🚀 DETAILED PROCEDURE CONTENT CHECK")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Authenticate
    session = authenticate()
    if not session:
        return False
    
    # Check procedures mentioned in review request
    procedures = [
        "root-canal-therapy",
        "dental-implant-placement", 
        "dental-crown-placement"
    ]
    
    results = {}
    for procedure_id in procedures:
        procedure_data = check_procedure_detailed(session, procedure_id)
        results[procedure_id] = procedure_data
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    for procedure_id, data in results.items():
        if data:
            required_fields = ["immediateAftercare", "dietRestrictions", "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
            present_fields = sum(1 for field in required_fields if data.get(field))
            print(f"📋 {procedure_id}: {present_fields}/5 required fields present")
        else:
            print(f"❌ {procedure_id}: Failed to retrieve")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)