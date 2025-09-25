#!/usr/bin/env python3
"""
Fix specialtyName fields for procedures missing display names
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

async def fix_specialty_name_fields():
    """Fix missing specialtyName fields"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔧 FIXING MISSING SPECIALTY NAME FIELDS")
    print("=" * 80)
    
    # Specialty mapping
    specialty_mapping = {
        'oral-surgery': 'Oral Surgery',
        'prosthodontics': 'Prosthodontics', 
        'periodontics': 'Periodontics',
        'orthodontics': 'Orthodontics',
        'endodontics': 'Endodontics',
        'general-dentistry': 'General Dentistry',
        'oral-medicine': 'Oral Medicine'
    }
    
    try:
        # Find procedures with missing or empty specialtyName
        procedures = await db.procedures.find({
            "$or": [
                {"specialtyName": {"$exists": False}},
                {"specialtyName": ""},
                {"specialtyName": None}
            ]
        }).to_list(length=None)
        
        print(f"Found {len(procedures)} procedures with missing specialtyName")
        
        updated_count = 0
        
        for proc in procedures:
            name = proc.get('name', 'Unknown')
            specialty = proc.get('specialty', '')
            proc_id = proc.get('id', '')
            
            # Get the correct specialtyName
            specialty_name = specialty_mapping.get(specialty, specialty.title())
            
            # Update the procedure
            result = await db.procedures.update_one(
                {"id": proc_id},
                {"$set": {"specialtyName": specialty_name}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Fixed: {name}")
                print(f"   Added specialtyName: {specialty_name}")
                updated_count += 1
            else:
                print(f"❌ Failed to update: {name}")
        
        print(f"\n📊 RESULTS:")
        print(f"   Updated procedures: {updated_count}")
        
        # Verify all procedures now have specialtyName
        missing_count = await db.procedures.count_documents({
            "$or": [
                {"specialtyName": {"$exists": False}},
                {"specialtyName": ""},
                {"specialtyName": None}
            ]
        })
        
        if missing_count == 0:
            print(f"✅ All procedures now have specialtyName field")
        else:
            print(f"⚠️  {missing_count} procedures still missing specialtyName")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_specialty_name_fields())