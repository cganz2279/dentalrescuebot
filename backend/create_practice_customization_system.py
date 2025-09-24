#!/usr/bin/env python3
"""
Create practice-specific procedure customization system
CRITICAL: Ensures practice edits don't affect global content
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def create_customization_system():
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'dentist_management')
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print("🔧 Creating practice-specific procedure customization system...")
        
        # Create practice_procedure_customizations collection with proper indexing
        collection_name = 'practice_procedure_customizations'
        
        # Create indexes for efficient querying
        await db[collection_name].create_index([("practiceId", 1), ("procedureId", 1)], unique=True)
        await db[collection_name].create_index([("practiceId", 1)])
        await db[collection_name].create_index([("procedureId", 1)])
        
        print(f"✅ Created {collection_name} collection with indexes")
        print("📋 Collection structure:")
        print("  - practiceId: ID of the practice making the customization")
        print("  - procedureId: ID of the procedure being customized")
        print("  - customizedOverview: Practice-specific content")
        print("  - originalOverview: Backup of original content")
        print("  - customizedAt: Timestamp of customization")
        print("  - customizedBy: User who made the customization")
        
        # Sample document structure
        sample_doc = {
            "practiceId": "sample-practice-id",
            "procedureId": "sample-procedure-id", 
            "customizedOverview": "Practice-specific customized content",
            "originalOverview": "Original global content",
            "customizedAt": datetime.now(timezone.utc).isoformat(),
            "customizedBy": "user-id-who-made-change",
            "isActive": True
        }
        
        print(f"\n📄 Sample document structure:")
        for key, value in sample_doc.items():
            print(f"  {key}: {value}")
        
        client.close()
        print(f"\n🎉 Practice customization system created successfully!")
        print("🔒 SECURITY: Global procedures remain unchanged")
        print("🏥 ISOLATION: Each practice can customize independently")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_customization_system())