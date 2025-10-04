#!/usr/bin/env python3
"""
Database Structure Investigation
Check what fields are actually available in the procedures and find any with proper structure
"""

import requests
import json
import sys

# Backend URL from frontend configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com/api"

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

def check_all_procedures_structure(session):
    """Check the structure of all procedures to find patterns"""
    print("\n🔍 Checking all procedures structure...")
    
    try:
        response = session.get(f"{BACKEND_URL}/procedures")
        
        if response.status_code == 200:
            data = response.json()
            procedures = data.get("data", []) if data.get("success") else []
            
            print(f"✅ Retrieved {len(procedures)} procedures")
            
            # Analyze field patterns
            all_fields = set()
            field_counts = {}
            
            for proc in procedures:
                for field in proc.keys():
                    all_fields.add(field)
                    field_counts[field] = field_counts.get(field, 0) + 1
            
            print(f"\n📊 Field analysis across {len(procedures)} procedures:")
            for field in sorted(all_fields):
                count = field_counts[field]
                percentage = (count / len(procedures)) * 100
                print(f"  {field}: {count}/{len(procedures)} ({percentage:.1f}%)")
            
            # Look for procedures with the expected structure
            required_fields = ["immediateAftercare", "dietRestrictions", "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
            
            print(f"\n🎯 Looking for procedures with required medical fields...")
            procedures_with_structure = []
            
            for proc in procedures:
                has_fields = sum(1 for field in required_fields if proc.get(field))
                if has_fields > 0:
                    procedures_with_structure.append({
                        "id": proc.get("id"),
                        "name": proc.get("name"),
                        "fields_present": has_fields,
                        "fields": [field for field in required_fields if proc.get(field)]
                    })
            
            if procedures_with_structure:
                print(f"✅ Found {len(procedures_with_structure)} procedures with some required fields:")
                for proc in procedures_with_structure[:5]:  # Show first 5
                    print(f"  - {proc['name']} ({proc['id']}): {proc['fields_present']}/5 fields - {proc['fields']}")
            else:
                print("❌ No procedures found with the required medical content fields")
            
            # Check a few sample procedures in detail
            print(f"\n📋 Sample procedure structures (first 3):")
            for i, proc in enumerate(procedures[:3]):
                print(f"\n  Procedure {i+1}: {proc.get('name', 'Unknown')}")
                for key, value in proc.items():
                    if isinstance(value, list):
                        print(f"    {key}: list[{len(value)}] - {value[:2] if value else '[]'}")
                    elif isinstance(value, dict):
                        print(f"    {key}: dict with keys: {list(value.keys())}")
                    else:
                        value_str = str(value)
                        print(f"    {key}: {type(value).__name__} - {value_str[:50]}{'...' if len(value_str) > 50 else ''}")
            
            return procedures
            
        else:
            print(f"❌ Failed to retrieve procedures: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking procedures: {str(e)}")
        return None

def check_specific_procedure_by_name(session, search_name):
    """Look for procedures by name pattern"""
    print(f"\n🔍 Searching for procedures containing '{search_name}'...")
    
    try:
        response = session.get(f"{BACKEND_URL}/procedures/search?q={search_name}")
        
        if response.status_code == 200:
            data = response.json()
            procedures = data.get("data", []) if data.get("success") else []
            
            print(f"✅ Found {len(procedures)} procedures matching '{search_name}'")
            
            for proc in procedures:
                print(f"\n📋 {proc.get('name')} ({proc.get('id')})")
                required_fields = ["immediateAftercare", "dietRestrictions", "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
                present_fields = [field for field in required_fields if proc.get(field)]
                print(f"  Required fields present: {len(present_fields)}/5 - {present_fields}")
                
                # Show overview
                overview = proc.get("overview", "")
                if overview:
                    print(f"  Overview: {overview[:100]}...")
            
            return procedures
            
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        return None

def main():
    print("🚀 DATABASE STRUCTURE INVESTIGATION")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Authenticate
    session = authenticate()
    if not session:
        return False
    
    # Check all procedures structure
    all_procedures = check_all_procedures_structure(session)
    
    # Search for specific procedures
    search_terms = ["root", "implant", "crown"]
    for term in search_terms:
        check_specific_procedure_by_name(session, term)
    
    print("\n" + "=" * 80)
    print("📊 INVESTIGATION CONCLUSION")
    print("=" * 80)
    
    if all_procedures:
        print(f"✅ Database contains {len(all_procedures)} procedures")
        
        # Check if any have the required structure
        required_fields = ["immediateAftercare", "dietRestrictions", "warningSignsToCallDoctor", "recoveryTimeline", "medications"]
        procedures_with_structure = []
        
        for proc in all_procedures:
            has_fields = sum(1 for field in required_fields if proc.get(field))
            if has_fields > 0:
                procedures_with_structure.append(proc)
        
        if procedures_with_structure:
            print(f"✅ {len(procedures_with_structure)} procedures have some required medical fields")
            print("✅ Database structure supports PDF generation")
        else:
            print("❌ CRITICAL ISSUE: No procedures have the required medical content fields")
            print("❌ Database structure does NOT support proper PDF generation")
            print("🔧 ACTION REQUIRED: Database needs to be re-processed to add structured medical content")
        
        print(f"\n💡 Current structure: Procedures have 'overview' field with medical content")
        print(f"💡 Missing structure: Procedures lack structured fields (immediateAftercare, dietRestrictions, etc.)")
        print(f"💡 Impact: PDF generation cannot create properly formatted medical instructions")
        
    else:
        print("❌ Failed to retrieve procedure data")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)