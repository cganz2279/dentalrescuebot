#!/usr/bin/env python3
"""
Fix procedure categorizations based on user feedback
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def fix_procedure_categorizations():
    """Fix procedures that are in wrong specialty categories"""
    print("🔧 FIXING PROCEDURE CATEGORIZATIONS")
    print("=" * 45)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Define corrections needed
    corrections = [
        # Move to Oral Surgery
        {
            'name': 'Frenectomy',
            'correct_specialty': 'oral-surgery',
            'correct_specialty_name': 'Oral Surgery'
        },
        {
            'name': 'Oral Lesion Removal', 
            'correct_specialty': 'oral-surgery',
            'correct_specialty_name': 'Oral Surgery'
        },
        
        # Move to Periodontics
        {
            'name': 'Periodontal Flap Surgery',
            'correct_specialty': 'periodontics',
            'correct_specialty_name': 'Periodontics'
        },
        {
            'name': 'Periodontal Regenerative Surgery',
            'correct_specialty': 'periodontics', 
            'correct_specialty_name': 'Periodontics'
        },
        {
            'name': 'Osseous Surgery',
            'correct_specialty': 'periodontics',
            'correct_specialty_name': 'Periodontics'
        }
    ]
    
    fixes_applied = 0
    
    for correction in corrections:
        proc_name = correction['name']
        new_specialty = correction['correct_specialty']
        new_specialty_name = correction['correct_specialty_name']
        
        # Find the procedure
        procedure = await db.procedures.find_one({'name': proc_name})
        
        if procedure:
            current_specialty = procedure.get('specialtyName', 'Unknown')
            
            if current_specialty != new_specialty_name:
                # Update the procedure
                await db.procedures.update_one(
                    {'name': proc_name},
                    {
                        '$set': {
                            'specialty': new_specialty,
                            'specialtyName': new_specialty_name,
                            'updatedAt': datetime.utcnow().isoformat() + 'Z'
                        }
                    }
                )
                
                print(f"✅ Fixed: '{proc_name}'")
                print(f"   {current_specialty} → {new_specialty_name}")
                fixes_applied += 1
            else:
                print(f"ℹ️  '{proc_name}' already in correct category: {new_specialty_name}")
        else:
            print(f"❌ Procedure not found: '{proc_name}'")
    
    # Also fix any other periodontal procedures that might be miscategorized
    print(f"\n🔍 Checking for other periodontal procedures...")
    
    # Find procedures with periodontal keywords that aren't in Periodontics
    periodontal_keywords = [
        'periodontal', 'gingival', 'gingiv', 'scaling', 'root planing',
        'tissue graft', 'connective tissue', 'guided tissue', 'crown lengthening',
        'osseous', 'flap surgery'
    ]
    
    all_procedures = await db.procedures.find({}).to_list(length=None)
    
    additional_fixes = 0
    for proc in all_procedures:
        name_lower = proc['name'].lower()
        current_specialty = proc.get('specialtyName', '')
        
        # Check if it contains periodontal keywords but isn't in Periodontics
        should_be_periodontics = any(keyword in name_lower for keyword in periodontal_keywords)
        
        if should_be_periodontics and current_specialty != 'Periodontics':
            # Skip procedures that should definitely be in Oral Surgery
            if not any(keyword in name_lower for keyword in ['extraction', 'implant', 'surgery', 'biopsy', 'cancer', 'orthognathic']):
                await db.procedures.update_one(
                    {'name': proc['name']},
                    {
                        '$set': {
                            'specialty': 'periodontics',
                            'specialtyName': 'Periodontics',
                            'updatedAt': datetime.utcnow().isoformat() + 'Z'
                        }
                    }
                )
                print(f"✅ Auto-fixed: '{proc['name']}'")
                print(f"   {current_specialty} → Periodontics")
                additional_fixes += 1
    
    # Final verification
    print(f"\n📊 FINAL VERIFICATION:")
    
    # Check specialty distribution
    specialties = {}
    final_procedures = await db.procedures.find({}, {'specialtyName': 1, '_id': 0}).to_list(length=None)
    
    for proc in final_procedures:
        specialty = proc.get('specialtyName', 'Unknown')
        specialties[specialty] = specialties.get(specialty, 0) + 1
    
    for specialty, count in sorted(specialties.items()):
        print(f'   - {specialty}: {count} procedures')
    
    print(f"\n🎉 CATEGORIZATION FIXES COMPLETED!")
    print(f"   Manual fixes applied: {fixes_applied}")
    print(f"   Additional periodontal fixes: {additional_fixes}")
    print(f"   Total procedures: {len(final_procedures)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_procedure_categorizations())