#!/usr/bin/env python3
"""
Detailed Procedure Content Verification
"""

import requests
import json

BASE_URL = "https://postopcare-1.preview.emergentagent.com/api"

def get_procedure_details(procedure_id: str, procedure_name: str):
    """Get detailed information about a specific procedure"""
    print(f"\n🔍 Getting details for: {procedure_name}")
    print(f"   Procedure ID: {procedure_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/procedures/{procedure_id}", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get procedure details: {response.status_code}")
            return
            
        data = response.json()
        
        if not data.get("success"):
            print(f"   ❌ API returned success=false: {data}")
            return
            
        procedure = data.get("data", {})
        
        print(f"   ✅ Name: {procedure.get('name', 'N/A')}")
        print(f"   ✅ Specialty: {procedure.get('specialty', 'N/A')} ({procedure.get('specialtyName', 'N/A')})")
        print(f"   ✅ Duration: {procedure.get('duration', 'N/A')}")
        
        overview = procedure.get('overview', '')
        if overview and len(overview.strip()) > 0:
            print(f"   ✅ Overview: {len(overview)} characters")
            print(f"      Preview: {overview[:100]}...")
        else:
            print(f"   ❌ Overview: Empty or missing")
        
        # Check other content fields
        immediate_aftercare = procedure.get('immediateAftercare', [])
        diet_restrictions = procedure.get('dietRestrictions', [])
        warning_signs = procedure.get('warningSignsToCallDoctor', [])
        recovery_timeline = procedure.get('recoveryTimeline', [])
        medications = procedure.get('medications', [])
        
        print(f"   ✅ Immediate Aftercare: {len(immediate_aftercare)} items")
        print(f"   ✅ Diet Restrictions: {len(diet_restrictions)} items")
        print(f"   ✅ Warning Signs: {len(warning_signs)} items")
        print(f"   ✅ Recovery Timeline: {len(recovery_timeline)} items")
        print(f"   ✅ Medications: {len(medications)} items")
        
        # Check if content is substantial (not just placeholder)
        total_content_length = len(overview)
        if total_content_length > 100:
            print(f"   ✅ Content appears substantial ({total_content_length} chars in overview)")
        else:
            print(f"   ⚠️  Content may be minimal ({total_content_length} chars in overview)")
            
    except Exception as e:
        print(f"   ❌ Exception getting procedure details: {str(e)}")

def main():
    print("🚀 DETAILED PROCEDURE CONTENT VERIFICATION")
    print("=" * 60)
    
    # Get all procedures first to find our target ones
    try:
        response = requests.get(f"{BASE_URL}/procedures", timeout=10)
        data = response.json()
        procedures = data.get("data", [])
        
        target_procedures = []
        for proc in procedures:
            name = proc.get("name", "")
            if ("All On X" in name and "Post Op Instructions" in name) or \
               ("Final" in name and "Zirconia" in name and "Implant Prosthesis" in name):
                target_procedures.append(proc)
        
        print(f"Found {len(target_procedures)} target procedures")
        
        for proc in target_procedures:
            get_procedure_details(proc.get("id"), proc.get("name"))
            
    except Exception as e:
        print(f"❌ Error getting procedures: {str(e)}")

if __name__ == "__main__":
    main()