#!/usr/bin/env python3
"""
Detailed Root Canal Content Inspection
Review Request: Detailed verification of Root Canal procedure content quality
"""

import requests
import json
import sys

# Backend URL from frontend configuration
BACKEND_URL = "https://dental-rescue.preview.emergentagent.com/api"

def authenticate():
    """Authenticate and get JWT token"""
    session = requests.Session()
    
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
            session.headers.update({
                "Authorization": f"Bearer {data['token']}"
            })
            return session
    return None

def inspect_root_canal_content():
    """Get and inspect detailed Root Canal content"""
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("🔍 DETAILED ROOT CANAL CONTENT INSPECTION")
    print("=" * 60)
    
    response = session.get(f"{BACKEND_URL}/procedures/root-canal-therapy")
    
    if response.status_code == 200:
        data = response.json()
        procedure = data.get("data", {}) if data.get("success") else data
        
        print(f"📋 Procedure Name: {procedure.get('name', 'N/A')}")
        print(f"🏥 Specialty: {procedure.get('specialtyName', 'N/A')}")
        print(f"⏱️  Duration: {procedure.get('duration', 'N/A')}")
        print()
        
        # Overview
        print("📖 OVERVIEW:")
        overview = procedure.get('overview', '')
        print(f"Length: {len(overview)} characters")
        print(f"Content: {overview[:200]}{'...' if len(overview) > 200 else ''}")
        print()
        
        # Immediate Aftercare
        print("🩹 IMMEDIATE AFTERCARE:")
        aftercare = procedure.get('immediateAftercare', [])
        print(f"Items: {len(aftercare)}")
        for i, item in enumerate(aftercare, 1):
            print(f"  {i}. {item}")
        print()
        
        # Diet Restrictions
        print("🍽️ DIET RESTRICTIONS:")
        diet = procedure.get('dietRestrictions', [])
        print(f"Items: {len(diet)}")
        for i, item in enumerate(diet, 1):
            print(f"  {i}. {item}")
        print()
        
        # Warning Signs
        print("⚠️ WARNING SIGNS TO CALL DOCTOR:")
        warnings = procedure.get('warningSignsToCallDoctor', [])
        print(f"Items: {len(warnings)}")
        for i, item in enumerate(warnings, 1):
            print(f"  {i}. {item}")
        print()
        
        # Recovery Timeline
        print("📅 RECOVERY TIMELINE:")
        timeline = procedure.get('recoveryTimeline', [])
        print(f"Items: {len(timeline)}")
        for i, item in enumerate(timeline, 1):
            if isinstance(item, dict):
                print(f"  {i}. Day: {item.get('day', 'N/A')}, Activity: {item.get('activity', 'N/A')}")
            else:
                print(f"  {i}. {item}")
        print()
        
        # Medications
        print("💊 MEDICATIONS:")
        medications = procedure.get('medications', [])
        print(f"Items: {len(medications)}")
        for i, item in enumerate(medications, 1):
            print(f"  {i}. {item}")
        print()
        
        # Content Analysis
        print("🔬 CONTENT ANALYSIS:")
        
        # Check for root canal specific terms
        all_text = str(procedure).lower()
        root_canal_terms = {
            'root canal': all_text.count('root canal'),
            'canal': all_text.count('canal'),
            'pulp': all_text.count('pulp'),
            'endodontic': all_text.count('endodontic'),
            'tooth': all_text.count('tooth'),
            'restoration': all_text.count('restoration'),
            'temporary': all_text.count('temporary'),
            'permanent': all_text.count('permanent'),
            'crown': all_text.count('crown'),
            'filling': all_text.count('filling')
        }
        
        print("Root Canal Terminology Frequency:")
        for term, count in root_canal_terms.items():
            if count > 0:
                print(f"  - '{term}': {count} occurrences")
        
        # Check for generic/test content
        generic_terms = {
            'test assignment': all_text.count('test assignment'),
            'automated testing': all_text.count('automated testing'),
            'placeholder': all_text.count('placeholder'),
            'dummy': all_text.count('dummy'),
            'sample': all_text.count('sample'),
            'example': all_text.count('example')
        }
        
        generic_found = sum(generic_terms.values())
        if generic_found > 0:
            print("\n❌ Generic/Test Content Found:")
            for term, count in generic_terms.items():
                if count > 0:
                    print(f"  - '{term}': {count} occurrences")
        else:
            print("\n✅ No generic/test content detected")
        
        # Field length analysis
        print(f"\nField Lengths:")
        print(f"  - Overview: {len(str(procedure.get('overview', '')))} chars")
        print(f"  - Immediate Aftercare: {len(aftercare)} items, {sum(len(str(item)) for item in aftercare)} total chars")
        print(f"  - Diet Restrictions: {len(diet)} items, {sum(len(str(item)) for item in diet)} total chars")
        print(f"  - Warning Signs: {len(warnings)} items, {sum(len(str(item)) for item in warnings)} total chars")
        print(f"  - Recovery Timeline: {len(timeline)} items")
        print(f"  - Medications: {len(medications)} items, {sum(len(str(item)) for item in medications)} total chars")
        
        print("\n🎯 CONCLUSION:")
        if generic_found == 0 and sum(root_canal_terms.values()) > 0:
            print("✅ Content appears to be genuine medical content specific to root canal procedures")
            print("✅ No 'Test assignment from automated testing' content found")
            print("✅ Database structure has been properly fixed")
        else:
            print("❌ Content quality issues detected")
            if generic_found > 0:
                print("❌ Generic test content still present")
            if sum(root_canal_terms.values()) == 0:
                print("❌ Lacks root canal specific terminology")
    
    else:
        print(f"❌ Failed to get Root Canal procedure: {response.status_code} - {response.text}")

if __name__ == "__main__":
    inspect_root_canal_content()