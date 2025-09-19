#!/usr/bin/env python3
"""
Update specific procedures with exact content from original PDF files
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# Exact content from original PDFs (removing "DENTAL RESCUE BOT" header as user requested)
SPECIFIC_PROCEDURES = {
    "wisdom-tooth-removal": """Purpose: Removal of impacted or partially erupted third molars.
First 24 Hours:
- Same bleeding and clot care as other extractions.
- Expect facial swelling, jaw stiffness, and possible bruising.
Pain & Swelling:
- Take prescribed pain medication as directed.
- Apply ice packs to the outside of your face for 20 minutes on/off for the first 24 hours.
- Switch to warm compresses after 48 hours to help with stiffness.
- Gentle jaw stretching after 3 days can help prevent limited opening.
Diet:
- Liquid and soft foods for 3-5 days.
- Avoid straws for 1 week to prevent dislodging the clot.
Activity:
- Rest for 2-3 days after surgery.
- Avoid sports or activities that may cause trauma to the face.
Special Precautions:
- If upper wisdom teeth were removed near the sinuses, avoid blowing your nose for 1 week.
- Sneeze with your mouth open to avoid pressure in the sinus.
Follow-Up:
- Suture removal if required.
- Contact the office if you experience persistent numbness, fever, foul taste, or swelling that worsens after 3 days.""",

    "tooth-colored-fillings": """Purpose: Restoration of decayed or damaged teeth using composite resin for a natural appearance.
First 24 Hours:
- Avoid chewing until numbness wears off.
- Composite fillings harden immediately, but chewing may cause discomfort initially.
Pain & Sensitivity:
- Mild sensitivity to pressure, temperature, or sweets may occur for a few days.
- Use OTC pain relievers if needed.
Oral Hygiene:
- Brush and floss normally, taking care around the filled tooth.
Diet:
- Avoid very hard or sticky foods for the rest of the day.
- Resume normal diet as comfort allows.
Special Precautions:
- If your bite feels uneven after numbness wears off, contact the office for adjustment.
Follow-Up:
- Sensitivity should gradually decrease.
- Contact the office if pain worsens or persists beyond a week."""
}

async def update_specific_procedures():
    """Update specific procedures with exact PDF content"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔧 Updating specific procedures with exact original PDF content...")
        
        updated_count = 0
        
        for procedure_id, content in SPECIFIC_PROCEDURES.items():
            print(f"✅ Updating {procedure_id} with original PDF content")
            
            result = await db.procedures.update_one(
                {"id": procedure_id},
                {
                    "$set": {
                        "overview": content,
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.matched_count > 0:
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"   ✅ Updated successfully")
                else:
                    print(f"   ⚠️ No changes (content was same)")
            else:
                print(f"   ❌ Procedure not found in database")
        
        print(f"\n✅ Updated {updated_count} specific procedures with original PDF content!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(update_specific_procedures())
    if success:
        print("\n🎯 SPECIFIC PROCEDURES UPDATED!")
        print("✅ These procedures now have exact original PDF content")
    else:
        print("\n❌ Failed to update specific procedures")
