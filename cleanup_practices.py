#!/usr/bin/env python3
"""
Clean up test practices, keeping only the real practice
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend/.env')

async def cleanup_practices():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    # Keep only this practice
    keep_email = "cganz2279@gmail.com"
    
    try:
        # Find all practices except the one to keep
        practices_to_delete = await db.practices.find(
            {"email": {"$ne": keep_email}},
            {"_id": 0, "id": 1, "name": 1, "email": 1}
        ).to_list(length=None)
        
        print(f"Found {len(practices_to_delete)} practices to delete:")
        for practice in practices_to_delete:
            print(f"  - {practice['name']} ({practice['email']})")
        
        if practices_to_delete:
            confirm = input(f"\nDelete {len(practices_to_delete)} test practices? (y/N): ")
            if confirm.lower() == 'y':
                # Get practice IDs to delete
                practice_ids = [p['id'] for p in practices_to_delete]
                
                # Delete practices
                result = await db.practices.delete_many({"id": {"$in": practice_ids}})
                print(f"✅ Deleted {result.deleted_count} practices")
                
                # Delete associated users
                users_result = await db.users.delete_many({"practiceId": {"$in": practice_ids}})
                print(f"✅ Deleted {users_result.deleted_count} users")
                
                # Delete associated patients
                patients_result = await db.patients.delete_many({"practiceId": {"$in": practice_ids}})
                print(f"✅ Deleted {patients_result.deleted_count} patients")
                
                # Delete associated patient procedures
                procedures_result = await db.patient_procedures.delete_many({"practiceId": {"$in": practice_ids}})
                print(f"✅ Deleted {procedures_result.deleted_count} patient procedures")
                
                # Delete associated payment transactions
                payments_result = await db.payment_transactions.delete_many({"practice_id": {"$in": practice_ids}})
                print(f"✅ Deleted {payments_result.deleted_count} payment transactions")
                
                print(f"\n🎉 Cleanup complete! Only {keep_email} practice remains.")
            else:
                print("❌ Cleanup cancelled")
        else:
            print(f"✅ Already clean - only {keep_email} practice exists")
        
        # Show remaining practice
        remaining = await db.practices.find_one({"email": keep_email})
        if remaining:
            print(f"\n📋 Remaining practice: {remaining['name']} ({remaining['email']})")
        else:
            print(f"\n⚠️  Warning: {keep_email} practice not found!")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_practices())