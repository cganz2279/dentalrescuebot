#!/usr/bin/env python3
"""
Fix cancer and biopsy procedure categorization - move them from General Dentistry to Oral Surgery
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# Target procedures that should be categorized as Oral Surgery
TARGET_PROCEDURES = [
    "Biopsy of Oral Tissue",
    "Biopsy Oral Soft Tissue", 
    "Oral Biopsy",
    "Oral Cancer Screening FollowUp",
    "Oral Cancer Surgery"
]

async def fix_categorization():
    """Fix categorization of cancer and biopsy procedures"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔧 Fixing cancer and biopsy procedure categorizations...")
        print(f"Moving {len(TARGET_PROCEDURES)} procedures from General Dentistry to Oral Surgery")
        print()
        
        updated_count = 0
        
        for procedure_name in TARGET_PROCEDURES:
            print(f"Processing: {procedure_name}")
            
            # First, check current categorization
            current_proc = await db.procedures.find_one({"name": procedure_name})
            if not current_proc:
                print(f"   ❌ Procedure not found in database")
                continue
            
            current_specialty = current_proc.get('specialty', 'unknown')
            current_specialty_name = current_proc.get('specialtyName', 'unknown')
            print(f"   Current: specialty='{current_specialty}', specialtyName='{current_specialty_name}'")
            
            # Update to Oral Surgery
            result = await db.procedures.update_one(
                {"name": procedure_name},
                {
                    "$set": {
                        "specialty": "oral-surgery",
                        "specialtyName": "Oral Surgery",
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.matched_count > 0:
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"   ✅ Updated to Oral Surgery")
                else:
                    print(f"   ⚠️ No changes needed (already correct)")
            else:
                print(f"   ❌ Procedure not found in database")
            print()
        
        print(f"✅ Successfully updated {updated_count} procedures to Oral Surgery!")
        
        # Verify the changes
        print("\n🔍 Verifying changes...")
        for procedure_name in TARGET_PROCEDURES:
            proc = await db.procedures.find_one({"name": procedure_name})
            if proc:
                specialty = proc.get('specialty', 'unknown')
                specialty_name = proc.get('specialtyName', 'unknown')
                if specialty == 'oral-surgery' and specialty_name == 'Oral Surgery':
                    print(f"   ✅ {procedure_name}: Correctly categorized as Oral Surgery")
                else:
                    print(f"   ❌ {procedure_name}: Still incorrectly categorized as {specialty_name}")
            else:
                print(f"   ❌ {procedure_name}: Not found")
        
        # Show updated counts by specialty
        print("\n📊 Updated procedure counts by specialty:")
        pipeline = [
            {"$group": {"_id": "$specialtyName", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        specialty_counts = await db.procedures.aggregate(pipeline).to_list(length=None)
        for item in specialty_counts:
            specialty_name = item['_id'] or 'Unknown'
            count = item['count']
            print(f"   {specialty_name}: {count} procedures")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(fix_categorization())
    if success:
        print("\n🎯 CATEGORIZATION FIX COMPLETED!")
        print("✅ Cancer and biopsy procedures are now properly categorized under Oral Surgery")
    else:
        print("\n❌ Failed to fix categorization")