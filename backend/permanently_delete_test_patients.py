#!/usr/bin/env python3
"""
Permanently delete all test patients and keep only real patients
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def permanently_delete_test_patients():
    """Permanently delete test patients from the database"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dentist_management
    
    # Practice ID we're working with
    practice_id = "0b08d321-ae1a-43d5-b69a-4850cfa3a9fc"
    
    print("Permanently deleting test patients...")
    
    try:
        # Get all patients for this practice
        all_patients = await db.users.find({
            "practiceId": practice_id,
            "role": "patient"
        }).to_list(length=None)
        
        print(f"Found {len(all_patients)} total patients")
        
        # Identify real patients that should be kept
        real_patient_ids = []
        test_patient_ids = []
        
        real_patient_criteria = [
            "barbganz@gmail.com",
            "ganzseth@gmail.com", 
            "jackie@gmail.com",
            "smith@gmail.com"
        ]
        
        for patient in all_patients:
            email = patient.get("email", "").lower()
            first_name = patient.get("firstName", "").lower()
            last_name = patient.get("lastName", "").lower()
            
            # Check if this is a real patient we want to keep
            is_real_patient = email in real_patient_criteria
            
            if is_real_patient:
                real_patient_ids.append(patient["id"])
                print(f"KEEPING: {patient['firstName']} {patient['lastName']} ({patient['email']})")
            else:
                test_patient_ids.append(patient["id"])
                print(f"DELETING: {patient['firstName']} {patient['lastName']} ({patient['email']})")
        
        print(f"\nReal patients to keep: {len(real_patient_ids)}")
        print(f"Test patients to delete: {len(test_patient_ids)}")
        
        if test_patient_ids:
            # Delete all procedure assignments for test patients first
            procedure_delete_result = await db.patientprocedures.delete_many({
                "practiceId": practice_id,
                "patientId": {"$in": test_patient_ids}
            })
            print(f"Deleted {procedure_delete_result.deleted_count} procedure assignments for test patients")
            
            # Now delete the test patients themselves
            patient_delete_result = await db.users.delete_many({
                "practiceId": practice_id,
                "role": "patient",
                "id": {"$in": test_patient_ids}
            })
            print(f"Deleted {patient_delete_result.deleted_count} test patients")
        
        # Ensure real patients are active
        if real_patient_ids:
            update_result = await db.users.update_many(
                {
                    "practiceId": practice_id,
                    "role": "patient",
                    "id": {"$in": real_patient_ids}
                },
                {
                    "$set": {
                        "isActive": True,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            print(f"Ensured {update_result.modified_count} real patients are active")
        
        # Final count
        final_count = await db.users.count_documents({
            "practiceId": practice_id,
            "role": "patient"
        })
        print(f"\nFinal patient count: {final_count}")
        
        # Show remaining patients
        remaining_patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient"
            },
            {"firstName": 1, "lastName": 1, "email": 1, "isActive": 1, "_id": 0}
        ).to_list(length=None)
        
        print("\nRemaining patients:")
        for patient in remaining_patients:
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']}) - Active: {patient.get('isActive', True)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(permanently_delete_test_patients())