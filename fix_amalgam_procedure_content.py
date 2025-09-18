#!/usr/bin/env python3
"""
Fix Amalgam Fillings procedure content to match exact user format
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# Exact content matching user's specified format
EXACT_AMALGAM_CONTENT = """Purpose: Restoration of decayed or damaged teeth using a silver-colored amalgam material.
First 24 Hours:
- Avoid chewing until numbness wears off.
- Amalgam fillings take about 24 hours to fully set, so chew on the opposite side.
Pain & Sensitivity:
- Mild sensitivity to pressure or temperature may occur for a few days.
- Use OTC pain relievers if needed.
Oral Hygiene:
- Brush and floss normally, being gentle around the filled tooth.
Diet:
- Avoid very hard or sticky foods for the first day.
- Resume normal diet after 24 hours.
Special Precautions:
- If your bite feels uneven after numbness wears off, contact the office for adjustment.
Follow-Up:
- Sensitivity should gradually decrease.
- Contact the office if pain worsens or persists beyond a week."""

async def fix_amalgam_content():
    """Update Amalgam Fillings procedure with exact user format"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔧 Updating Amalgam Fillings procedure content to exact user format...")
        
        # Update the procedure with exact content
        result = await db.procedures.update_one(
            {"id": "amalgam-fillings"},
            {
                "$set": {
                    "overview": EXACT_AMALGAM_CONTENT,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            print("❌ Amalgam Fillings procedure not found!")
            return False
        
        if result.modified_count > 0:
            print("✅ Successfully updated Amalgam Fillings procedure content!")
            print(f"📄 New content length: {len(EXACT_AMALGAM_CONTENT)} characters")
            print("\n📋 Updated content:")
            print("-" * 50)
            print(EXACT_AMALGAM_CONTENT)
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
    success = asyncio.run(fix_amalgam_content())
    if success:
        print("\n🎯 Amalgam Fillings procedure now has EXACT user format!")
        print("✅ PDFs should now generate correctly with this content")
    else:
        print("\n❌ Failed to update procedure content")