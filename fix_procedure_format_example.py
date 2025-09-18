#!/usr/bin/env python3
"""
Update procedure content to match exact user format example
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# Exact content matching user's format example
EXACT_PROCEDURE_CONTENT = """Purpose: A periodontal procedure that uses a barrier membrane to direct the growth of new bone and gum tissue where it has been lost.
First 24–48 Hours:
- Mild bleeding, swelling, and discomfort are normal.
- Apply ice packs to the outside of the face for 15–20 minutes at a time during the first day.
- Keep your head elevated when resting.
Pain & Sensitivity:
- Take prescribed pain medications and antibiotics as directed.
- Mild sensitivity to hot and cold may persist for several weeks.
Oral Hygiene:
- Do not brush or floss near the surgical site until instructed by your dentist.
- Use prescribed antimicrobial rinses to keep the area clean.
Diet:
- Eat soft foods for the first 3–5 days.
- Avoid chewing on the treated side, and avoid spicy, hard, or crunchy foods.
Special Precautions:
- Avoid smoking and alcohol during healing.
- Do not disturb the surgical site with your tongue or fingers.
Follow-Up:
- Attend follow-up visits to ensure proper healing and membrane stability.
- Contact your dentist if bleeding persists, swelling worsens after 3 days, or signs of infection develop."""

async def update_procedure_format():
    """Update a procedure with exact user format"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔧 Updating procedure content to exact user format...")
        
        # Let's update the Amalgam Fillings procedure we worked on before
        result = await db.procedures.update_one(
            {"id": "amalgam-fillings"},
            {
                "$set": {
                    "overview": EXACT_PROCEDURE_CONTENT,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            print("❌ Amalgam Fillings procedure not found!")
            return False
        
        if result.modified_count > 0:
            print("✅ Successfully updated procedure content to exact format!")
            print(f"📄 New content length: {len(EXACT_PROCEDURE_CONTENT)} characters")
            print("\n📋 Updated content preview:")
            print("-" * 50)
            print(EXACT_PROCEDURE_CONTENT[:200] + "...")
            print("-" * 50)
            return True
        else:
            print("⚠️ No changes made (content was already correct)")
            return True
            
    except Exception as e:
        print(f"❌ Error updating content: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(update_procedure_format())
    if success:
        print("\n🎯 Procedure now has EXACT user format!")
        print("✅ PDFs should now generate correctly with this content")
    else:
        print("\n❌ Failed to update procedure content")