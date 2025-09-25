#!/usr/bin/env python3
"""
Remove Duplicate PDFs - Keep only one instance of each procedure
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def remove_duplicates():
    """Remove duplicate procedures, keeping only the original version"""
    print("🔄 Starting Duplicate Removal Process")
    print("=" * 50)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Define specific duplicates to remove (keep the original, remove the numbered ones)
    duplicates_to_remove = [
        'final-zirconia-implant-prosthesis-post-op-instructions-2-2',  # Keep the original without (2)
        'pulpotomy-1-1',  # Keep the original without (1)
        'scaling-and-root-planing-1-1',  # Keep the original without (1)
        'vestibuloplasty-1-1',  # Keep the original without (1)
        'vestibuloplasty-2-2'   # Keep the original without (2)
    ]
    
    removed_count = 0
    
    print("🗑️  Removing duplicate procedures:")
    
    for procedure_id in duplicates_to_remove:
        # Find the procedure
        procedure = await db.procedures.find_one({'id': procedure_id})
        
        if procedure:
            procedure_name = procedure.get('name', 'Unknown')
            original_filename = procedure.get('originalFilename', 'Unknown')
            
            # Delete the duplicate
            result = await db.procedures.delete_one({'id': procedure_id})
            
            if result.deleted_count > 0:
                print(f"  ✅ Removed: {procedure_name} (File: {original_filename})")
                removed_count += 1
            else:
                print(f"  ❌ Failed to remove: {procedure_name}")
        else:
            print(f"  ⚠️  Not found: {procedure_id}")
    
    print(f"\n📊 Summary:")
    print(f"  - Duplicates removed: {removed_count}")
    
    # Verify final count
    final_count = await db.procedures.count_documents({})
    print(f"  - Final procedure count: {final_count}")
    
    # Verify no duplicates remain
    print(f"\n🔍 Verification - checking for remaining duplicates...")
    
    procedures = await db.procedures.find({}, {'name': 1, 'id': 1, '_id': 0}).to_list(length=None)
    
    # Group by base name to verify no duplicates
    base_names = {}
    for proc in procedures:
        name = proc['name']
        base_name = name.replace(' (1)', '').replace(' (2)', '').strip()
        
        if base_name not in base_names:
            base_names[base_name] = []
        base_names[base_name].append(proc)
    
    duplicates_remaining = []
    for base_name, procs in base_names.items():
        if len(procs) > 1:
            duplicates_remaining.append(base_name)
            print(f"  ❌ Still duplicated: {base_name}")
    
    if not duplicates_remaining:
        print("  ✅ No duplicates remaining")
    
    print("\n" + "=" * 50)
    print("🎉 DUPLICATE REMOVAL COMPLETED!")
    
    # Show final specialty breakdown
    print(f"\n📋 Final Specialty Distribution:")
    specialties = {}
    procedures = await db.procedures.find({}, {'specialtyName': 1, '_id': 0}).to_list(length=None)
    for proc in procedures:
        specialty = proc.get('specialtyName', 'Unknown')
        specialties[specialty] = specialties.get(specialty, 0) + 1
    
    for specialty, count in sorted(specialties.items()):
        print(f'   - {specialty}: {count} procedures')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(remove_duplicates())