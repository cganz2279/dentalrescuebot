#!/usr/bin/env python3
"""
Final Categorization Fixes
Fix remaining categorization issues
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

async def fix_remaining_categorizations():
    """Fix the remaining categorization issues"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔧 FIXING REMAINING CATEGORIZATION ISSUES")
    print("=" * 80)
    
    fixes = [
        {
            'name': 'TMJ Therapy',
            'target_specialty': 'oral-surgery',
            'target_specialty_name': 'Oral Surgery'
        },
        {
            'name': 'Dental Bridge Placement', 
            'target_specialty': 'prosthodontics',
            'target_specialty_name': 'Prosthodontics'
        }
    ]
    
    try:
        for fix in fixes:
            # Find the procedure
            procedure = await db.procedures.find_one({"name": fix['name']})
            
            if procedure:
                current_specialty = procedure.get('specialty', 'unknown')
                
                # Update the procedure
                result = await db.procedures.update_one(
                    {"name": fix['name']},
                    {"$set": {
                        "specialty": fix['target_specialty'],
                        "specialtyName": fix['target_specialty_name']
                    }}
                )
                
                if result.modified_count > 0:
                    print(f"✅ Fixed: {fix['name']}")
                    print(f"   {current_specialty} → {fix['target_specialty_name']}")
                else:
                    print(f"❌ Failed to update: {fix['name']}")
            else:
                print(f"❌ Procedure not found: {fix['name']}")
        
        # Verify final counts
        print(f"\n📊 FINAL SPECIALTY COUNTS:")
        specialties = await db.procedures.distinct("specialty")
        
        for specialty in sorted(specialties):
            count = await db.procedures.count_documents({"specialty": specialty})
            print(f"   {specialty}: {count} procedures")
        
        total = await db.procedures.count_documents({})
        print(f"\n📋 Total procedures: {total}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_remaining_categorizations())