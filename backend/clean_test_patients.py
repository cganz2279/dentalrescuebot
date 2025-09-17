#!/usr/bin/env python3
"""
Clean up test patients and ensure real patients show up properly
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def clean_test_patients():
    """Mark test patients as inactive and ensure real patients are active"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dentist_management
    
    print("Cleaning up test patients...")
    
    try:
        # Define test patient criteria (emails containing test keywords or obvious test names)
        test_criteria = [
            {"email": {"$regex": "test", "$options": "i"}},
            {"email": {"$regex": "delete", "$options": "i"}},
            {"email": {"$regex": "temp", "$options": "i"}},
            {"email": {"$regex": "cleaned", "$options": "i"}},
            {"firstName": {"$regex": "test", "$options": "i"}},
            {"firstName": {"$regex": "temp", "$options": "i"}},
            {"firstName": {"$regex": "\\[CLEANED\\]", "$options": "i"}},
            {"lastName": {"$regex": "test", "$options": "i"}},
            {"email": {"$regex": "example.com", "$options": "i"}},
            {"email": {"$regex": "hidden.example.com", "$options": "i"}},
            # Specific test patient names
            {"firstName": "FreshTest"},
            {"firstName": "TestDelete"},
            {"firstName": "DeleteTest"},
            {"lastName": "405Test"}
        ]
        
        # Mark test patients as inactive
        for criteria in test_criteria:
            result = await db.users.update_many(
                {
                    "role": "patient",
                    **criteria
                },
                {
                    "$set": {
                        "isActive": False,
                        "deactivatedAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            print(f"Marked {result.modified_count} patients as inactive for criteria: {criteria}")
        
        # Ensure real patients (those with gmail.com or legitimate names) are active
        real_patient_criteria = [
            {"email": {"$regex": "gmail.com$"}},
            {"firstName": {"$in": ["barbara", "Seth", "jackie", "John", "JOhn"]}},
            {"lastName": {"$in": ["Ganz", "Smith"]}},
        ]
        
        for criteria in real_patient_criteria:
            result = await db.users.update_many(
                {
                    "role": "patient",
                    **criteria
                },
                {
                    "$set": {
                        "isActive": True,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            print(f"Ensured {result.modified_count} real patients are active for criteria: {criteria}")
        
        # Show summary
        active_count = await db.users.count_documents({
            "role": "patient",
            "isActive": True
        })
        
        inactive_count = await db.users.count_documents({
            "role": "patient", 
            "isActive": False
        })
        
        print(f"\nFinal counts: {active_count} active patients, {inactive_count} inactive patients")
        
        # Show active patients
        active_patients = await db.users.find(
            {
                "role": "patient",
                "isActive": True
            },
            {"firstName": 1, "lastName": 1, "email": 1, "_id": 0}
        ).to_list(length=None)
        
        print("\nActive patients:")
        for patient in active_patients:
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']})")
        
    except Exception as e:
        print(f"Error cleaning patients: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(clean_test_patients())