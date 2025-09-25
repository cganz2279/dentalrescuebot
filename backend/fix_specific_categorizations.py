#!/usr/bin/env python3
"""
Fix specific procedure categorizations as requested by user
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def fix_specific_categorizations():
    """Fix the specific procedures identified by the user"""
    print("🔧 FIXING SPECIFIC PROCEDURE CATEGORIZATIONS")
    print("=" * 50)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Define the specific fixes needed
    specific_fixes = [
        # Move to Oral Surgery
        {
            'name': 'Osseous Surgery',
            'target_specialty': 'oral-surgery',
            'target_specialty_name': 'Oral Surgery'
        },
        {
            'name': 'Root Amputation', 
            'target_specialty': 'oral-surgery',
            'target_specialty_name': 'Oral Surgery'
        },
        {
            'name': 'Sinus Perforation Repair',
            'target_specialty': 'oral-surgery',
            'target_specialty_name': 'Oral Surgery'
        },
        
        # Move to Periodontics
        {
            'name': 'Bone Grafting Ridge Preservation',
            'target_specialty': 'periodontics',
            'target_specialty_name': 'Periodontics'
        },
        {
            'name': 'Ridge Preservation After Extraction',
            'target_specialty': 'periodontics', 
            'target_specialty_name': 'Periodontics'
        }
    ]
    
    fixes_applied = 0
    
    for fix in specific_fixes:
        proc_name = fix['name']
        target_specialty = fix['target_specialty']
        target_specialty_name = fix['target_specialty_name']
        
        # Find and update the procedure
        procedure = await db.procedures.find_one({'name': proc_name})
        
        if procedure:
            current_specialty = procedure.get('specialtyName', 'Unknown')
            
            if current_specialty != target_specialty_name:
                await db.procedures.update_one(
                    {'name': proc_name},
                    {
                        '$set': {
                            'specialty': target_specialty,
                            'specialtyName': target_specialty_name,
                            'updatedAt': datetime.utcnow().isoformat() + 'Z'
                        }
                    }
                )
                
                print(f"✅ Fixed: '{proc_name}'")
                print(f"   {current_specialty} → {target_specialty_name}")
                fixes_applied += 1
            else:
                print(f"ℹ️  '{proc_name}' already in correct category: {target_specialty_name}")
        else:
            print(f"❌ Procedure not found: '{proc_name}'")
    
    # Check for any "Scaling" procedures in General Dentistry that need to move
    print(f"\n🔍 Checking for Scaling procedures in wrong categories...")
    scaling_procedures = await db.procedures.find({
        'name': {'$regex': 'scaling', '$options': 'i'},
        'specialtyName': {'$ne': 'Periodontics'}
    }).to_list(length=None)
    
    for proc in scaling_procedures:
        await db.procedures.update_one(
            {'_id': proc['_id']},
            {
                '$set': {
                    'specialty': 'periodontics',
                    'specialtyName': 'Periodontics', 
                    'updatedAt': datetime.utcnow().isoformat() + 'Z'
                }
            }
        )
        print(f"✅ Fixed: '{proc['name']}' moved from {proc['specialtyName']} to Periodontics")
        fixes_applied += 1
    
    # Final verification - show updated specialty distribution
    print(f"\n📊 FINAL SPECIALTY DISTRIBUTION:")
    specialties = {}
    all_procedures = await db.procedures.find({}, {'specialtyName': 1, '_id': 0}).to_list(length=None)
    
    for proc in all_procedures:
        specialty = proc.get('specialtyName', 'Unknown')
        specialties[specialty] = specialties.get(specialty, 0) + 1
    
    for specialty, count in sorted(specialties.items()):
        print(f'   - {specialty}: {count} procedures')
    
    print(f"\n🎉 CATEGORIZATION FIXES COMPLETED!")
    print(f"   Total fixes applied: {fixes_applied}")
    print(f"   Total procedures: {len(all_procedures)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_specific_categorizations())