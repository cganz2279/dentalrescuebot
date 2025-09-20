#!/usr/bin/env python3
"""
Add sample patients and procedures to make dashboard look populated
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timedelta
import random

async def add_sample_data():
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'dentist_management')
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        practice_id = "0b08d321-ae1a-43d5-b69a-4850cfa3a9fc"  # Cary Ganz practice ID
        
        print("🔄 Adding sample patients and procedures...")
        
        # Sample patients with Gmail addresses (so they show up in dashboard)
        sample_patients = [
            {
                "id": str(uuid.uuid4()),
                "firstName": "John",
                "lastName": "Smith", 
                "email": "john.smith.demo@gmail.com",
                "phone": "555-0101",
                "practiceId": practice_id,
                "role": "patient",
                "isActive": True,
                "createdAt": datetime.utcnow() - timedelta(days=30),
                "lastLoginAt": datetime.utcnow() - timedelta(days=5)
            },
            {
                "id": str(uuid.uuid4()),
                "firstName": "Sarah",
                "lastName": "Johnson",
                "email": "sarah.johnson.demo@gmail.com", 
                "phone": "555-0102",
                "practiceId": practice_id,
                "role": "patient",
                "isActive": True,
                "createdAt": datetime.utcnow() - timedelta(days=25),
                "lastLoginAt": datetime.utcnow() - timedelta(days=2)
            },
            {
                "id": str(uuid.uuid4()),
                "firstName": "Michael",
                "lastName": "Brown",
                "email": "michael.brown.demo@gmail.com",
                "phone": "555-0103", 
                "practiceId": practice_id,
                "role": "patient",
                "isActive": True,
                "createdAt": datetime.utcnow() - timedelta(days=20),
                "lastLoginAt": datetime.utcnow() - timedelta(days=1)
            },
            {
                "id": str(uuid.uuid4()),
                "firstName": "Emily", 
                "lastName": "Davis",
                "email": "emily.davis.demo@gmail.com",
                "phone": "555-0104",
                "practiceId": practice_id,
                "role": "patient", 
                "isActive": True,
                "createdAt": datetime.utcnow() - timedelta(days=15),
                "lastLoginAt": datetime.utcnow() - timedelta(hours=12)
            }
        ]
        
        # Insert patients
        for patient in sample_patients:
            await db.users.insert_one(patient)
            print(f"✅ Added patient: {patient['firstName']} {patient['lastName']}")
        
        # Sample recent procedures
        procedure_names = [
            "Root Canal Therapy", "Wisdom Tooth Removal", "Dental Crown Placement",
            "Scaling and Root Planing", "Dental Implant Placement", "Tooth Extraction"
        ]
        
        sample_procedures = []
        for i, patient in enumerate(sample_patients):
            # Add 1-2 procedures per patient
            for j in range(random.randint(1, 2)):
                procedure = {
                    "id": str(uuid.uuid4()),
                    "patientId": patient["id"],
                    "practiceId": practice_id,
                    "procedureName": random.choice(procedure_names),
                    "status": "completed",
                    "performedDate": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    "notes": "Procedure completed successfully",
                    "createdAt": datetime.utcnow() - timedelta(days=random.randint(1, 30))
                }
                sample_procedures.append(procedure)
        
        # Insert procedures
        for procedure in sample_procedures:
            await db.patientprocedures.insert_one(procedure)
            print(f"✅ Added procedure: {procedure['procedureName']}")
        
        print(f"\n🎉 Added {len(sample_patients)} patients and {len(sample_procedures)} procedures")
        print("📊 Dashboard should now show populated data!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_sample_data())