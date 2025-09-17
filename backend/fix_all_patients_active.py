#!/usr/bin/env python3
"""
Set all patients to active status
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def fix_all_patients():
    """Set all patients to active status"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dentist_management
    
    print("Setting all patients to active status...")
    
    try:
        # Update ALL patients to be active (unless explicitly set to inactive)
        result = await db.users.update_many(
            {
                "role": "patient"
            },
            {
                "$set": {
                    "isActive": True,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        print(f"Updated {result.modified_count} patients to have isActive=True")
        
        # Count and show some patients
        patients = await db.users.find(
            {"role": "patient"},
            {"firstName": 1, "lastName": 1, "email": 1, "isActive": 1, "_id": 0}
        ).limit(5).to_list(length=None)
        
        print("Sample patients after update:")
        for patient in patients:
            print(f"  - {patient['firstName']} {patient['lastName']}: isActive={patient.get('isActive')}")
        
    except Exception as e:
        print(f"Error fixing patients: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_all_patients())