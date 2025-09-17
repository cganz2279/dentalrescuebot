#!/usr/bin/env python3
"""
Debug patient data to understand the discrepancy
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def debug_patients():
    """Debug patient data"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dentist_management
    
    practice_id = "0b08d321-ae1a-43d5-b69a-4850cfa3a9fc"
    
    try:
        # Count all patients for this practice
        total_patients = await db.users.count_documents({
            "practiceId": practice_id,
            "role": "patient"
        })
        print(f"Total patients for practice: {total_patients}")
        
        # Count active patients
        active_patients = await db.users.count_documents({
            "practiceId": practice_id,
            "role": "patient",
            "isActive": True
        })
        print(f"Active patients: {active_patients}")
        
        # Count inactive patients
        inactive_patients = await db.users.count_documents({
            "practiceId": practice_id,
            "role": "patient", 
            "isActive": False
        })
        print(f"Inactive patients: {inactive_patients}")
        
        # Count patients without isActive field
        no_status_patients = await db.users.count_documents({
            "practiceId": practice_id,
            "role": "patient",
            "isActive": {"$exists": False}
        })
        print(f"Patients without isActive field: {no_status_patients}")
        
        # Get a sample of all patients with their isActive status
        all_patients_sample = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient"
            },
            {
                "firstName": 1,
                "lastName": 1, 
                "email": 1,
                "isActive": 1,
                "_id": 0
            }
        ).limit(10).to_list(length=None)
        
        print("\nSample patients:")
        for patient in all_patients_sample:
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']}) - isActive: {patient.get('isActive', 'NOT SET')}")
        
        # Check what the API query would return
        api_query_patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient",
                "isActive": True
            },
            {
                "firstName": 1,
                "lastName": 1,
                "email": 1,
                "_id": 0
            }
        ).to_list(length=None)
        
        print(f"\nPatients that would be returned by API (isActive: true): {len(api_query_patients)}")
        for patient in api_query_patients[:5]:
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(debug_patients())