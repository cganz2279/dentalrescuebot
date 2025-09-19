#!/usr/bin/env python3
"""
Update database with EXACT overview text from original uploaded PDFs
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# EXACT text extracted from original uploaded PDF files
ORIGINAL_PDF_OVERVIEW_TEXT = {
    "amalgam-fillings": """- Avoid chewing until numbness wears off.
- Amalgam fillings take about 24 hours to fully set, so chew on the opposite side.
- Mild sensitivity to pressure or temperature may occur for a few days.
- Use OTC pain relievers if needed.
- Brush and floss normally, being gentle around the filled tooth.
- Avoid very hard or sticky foods for the first day.
- Resume normal diet after 24 hours.
- If your bite feels uneven after numbness wears off, contact the office for adjustment.
- Sensitivity should gradually decrease.
- Contact the office if pain worsens or persists beyond a week.""",

    "root-canal-therapy": """- Avoid chewing on the treated tooth until numbness wears off.
- Some tenderness or mild discomfort is normal.
- Use OTC or prescribed pain relievers as directed.
- Tooth sensitivity to pressure may last for several days.
- Brush and floss normally, avoiding excessive pressure on the treated tooth.
- Soft foods are recommended until chewing comfort improves.
- If a temporary filling is placed, avoid sticky or hard foods until the permanent restoration is done.
- A crown or permanent filling is usually required for full protection.
- Contact the office if pain worsens, swelling develops, or you notice signs of infection."""
}

async def update_with_original_text():
    """Update procedures with EXACT original PDF overview text"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔧 Updating procedures with EXACT original PDF overview text...")
        
        updated_count = 0
        
        for procedure_id, overview_text in ORIGINAL_PDF_OVERVIEW_TEXT.items():
            print(f"✅ Updating {procedure_id} with exact original PDF text")
            
            result = await db.procedures.update_one(
                {"id": procedure_id},
                {
                    "$set": {
                        "overview": overview_text,
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.matched_count > 0:
                updated_count += 1
                print(f"   ✅ Updated with {len(overview_text)} characters of original text")
            else:
                print(f"   ❌ Procedure not found in database")
        
        print(f"\n✅ Updated {updated_count} procedures with EXACT original PDF text!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(update_with_original_text())
    if success:
        print("\n🎯 DATABASE UPDATED WITH ORIGINAL PDF TEXT!")
        print("✅ Overview fields now contain exact text from uploaded PDFs")
    else:
        print("\n❌ Failed to update database")
