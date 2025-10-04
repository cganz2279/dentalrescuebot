#!/usr/bin/env python3
"""
Detailed analysis of current procedure categorizations
"""

import requests
import json

BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def analyze_current_categorizations():
    """Analyze current procedure categorizations"""
    print("🔍 DETAILED CATEGORIZATION ANALYSIS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/procedures", timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to get procedures: {response.status_code}")
            return
            
        data = response.json()
        procedures = data.get('data', [])
        
        # Target procedures that should be in Oral Surgery
        target_procedures = [
            "Biopsy of Oral Tissue",
            "Biopsy Oral Soft Tissue", 
            "Oral Biopsy",
            "Oral Cancer Screening FollowUp",
            "Oral Cancer Surgery"
        ]
        
        print(f"Total procedures in database: {len(procedures)}")
        print()
        
        # Count by specialty
        specialty_counts = {}
        for proc in procedures:
            specialty_name = proc.get('specialtyName', 'Unknown')
            if specialty_name not in specialty_counts:
                specialty_counts[specialty_name] = 0
            specialty_counts[specialty_name] += 1
        
        print("Current procedure counts by specialty:")
        for specialty, count in sorted(specialty_counts.items()):
            print(f"   {specialty}: {count} procedures")
        print()
        
        # Find target procedures and their current categorization
        print("Target procedures and their current categorization:")
        found_targets = []
        for proc in procedures:
            name = proc.get('name', '')
            if name in target_procedures:
                found_targets.append({
                    'name': name,
                    'specialty': proc.get('specialty', ''),
                    'specialtyName': proc.get('specialtyName', ''),
                    'id': proc.get('id', '')
                })
        
        for target in found_targets:
            print(f"   ✅ {target['name']}")
            print(f"      Current specialty: {target['specialtyName']} ({target['specialty']})")
            print(f"      ID: {target['id']}")
            print()
        
        missing_targets = [name for name in target_procedures if name not in [t['name'] for t in found_targets]]
        if missing_targets:
            print("❌ Missing target procedures:")
            for missing in missing_targets:
                print(f"   - {missing}")
        
        # Show some Oral Surgery procedures for reference
        print("\nCurrent Oral Surgery procedures (first 10):")
        oral_surgery_procs = [p for p in procedures if p.get('specialtyName') == 'Oral Surgery']
        for i, proc in enumerate(oral_surgery_procs[:10]):
            print(f"   {i+1}. {proc.get('name', 'Unknown')}")
        
        if len(oral_surgery_procs) > 10:
            print(f"   ... and {len(oral_surgery_procs) - 10} more")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    analyze_current_categorizations()