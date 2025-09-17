#!/usr/bin/env python3
"""
Clean up test patients for the specific practice
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def clean_test_patients_by_practice():
    """Mark test patients as inactive for the specific practice"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dentist_management
    
    print("Finding practice and cleaning up test patients...")
    
    try:
        # First, find the practice with email cganz2279@gmail.com
        admin_user = await db.users.find_one({
            "email": "cganz2279@gmail.com",
            "role": "practice_admin"
        })
        
        if not admin_user:
            print("Could not find practice admin user")
            return
            
        practice_id = admin_user.get("practiceId")
        print(f"Found practice ID: {practice_id}")
        
        # Get all patients for this practice
        all_patients = await db.users.find({
            "practiceId": practice_id,
            "role": "patient"
        }).to_list(length=None)
        
        print(f"Found {len(all_patients)} total patients for this practice")
        
        # Identify real patients (those with gmail.com emails or Ganz family names)
        real_patients = []
        test_patients = []
        
        for patient in all_patients:
            email = patient.get("email", "").lower()
            first_name = patient.get("firstName", "").lower()
            last_name = patient.get("lastName", "").lower()
            
            # Check if this is a real patient
            is_real = (
                "@gmail.com" in email or
                "ganz" in last_name or
                "smith" in last_name or
                (first_name == "barbara" and last_name == "ganz") or
                (first_name == "seth" and last_name == "ganz") or
                (first_name == "jackie" and last_name == "ganz") or
                (first_name == "john" and last_name == "smith")
            )
            
            # Check if this is obviously a test patient
            is_test = (
                "test" in email or
                "delete" in email or
                "temp" in email or
                "example.com" in email or
                "cleaned" in email or
                "test" in first_name or
                "test" in last_name or
                "[cleaned]" in first_name or
                first_name in ["freshtest", "testdelete", "deletetest"] or
                "405test" in last_name
            )
            
            if is_real and not is_test:
                real_patients.append(patient)
            elif is_test:
                test_patients.append(patient)
            else:
                # Ambiguous - let's check more carefully
                if "john" in first_name and "doe" in last_name:
                    test_patients.append(patient)  # John Doe is likely test data
                else:
                    real_patients.append(patient)  # Default to real
        
        print(f"Identified {len(real_patients)} real patients and {len(test_patients)} test patients")
        
        print("\nReal patients:")
        for patient in real_patients:
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']})")
        
        print("\nTest patients to deactivate:")
        for patient in test_patients[:10]:  # Show first 10
            print(f"  - {patient['firstName']} {patient['lastName']} ({patient['email']})")
        if len(test_patients) > 10:
            print(f"  ... and {len(test_patients) - 10} more")
        
        # Mark test patients as inactive
        test_patient_ids = [p["id"] for p in test_patients]
        if test_patient_ids:
            result = await db.users.update_many(
                {
                    "practiceId": practice_id,
                    "role": "patient",
                    "id": {"$in": test_patient_ids}
                },
                {
                    "$set": {
                        "isActive": False,
                        "deactivatedAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            print(f"\nMarked {result.modified_count} test patients as inactive")
        
        # Ensure real patients are active
        real_patient_ids = [p["id"] for p in real_patients]
        if real_patient_ids:
            result = await db.users.update_many(
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
            print(f"Ensured {result.modified_count} real patients are active")
        
    except Exception as e:
        print(f"Error cleaning patients: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(clean_test_patients_by_practice())