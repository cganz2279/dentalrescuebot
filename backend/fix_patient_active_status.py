#!/usr/bin/env python3
"""
Fix patient active status - ensure all patients have isActive field set properly
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def fix_patient_active_status():
    """Fix patient active status for all existing patients"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dentist_management
    
    print("Fixing patient active status...")
    
    try:
        # Update all patients without isActive field to be active
        result = await db.users.update_many(
            {
                "role": "patient",
                "isActive": None
            },
            {
                "$set": {
                    "isActive": True,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        print(f"Updated {result.modified_count} patients to have isActive=True")
        
        # Update all patients where isActive is missing to be active
        result2 = await db.users.update_many(
            {
                "role": "patient",
                "isActive": {"$exists": False}
            },
            {
                "$set": {
                    "isActive": True,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        print(f"Updated {result2.modified_count} patients without isActive field to have isActive=True")
        
        # Count total patients by status
        active_count = await db.users.count_documents({
            "role": "patient",
            "isActive": True
        })
        
        inactive_count = await db.users.count_documents({
            "role": "patient",
            "isActive": False
        })
        
        print(f"Final status: {active_count} active patients, {inactive_count} inactive patients")
        
    except Exception as e:
        print(f"Error fixing patient status: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_patient_active_status())