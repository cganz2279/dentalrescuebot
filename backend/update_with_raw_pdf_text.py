#!/usr/bin/env python3
"""
Update database with EXACT raw text from original PDFs
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# EXACT RAW TEXT from original uploaded PDFs (just the content, no processing)
RAW_PDF_CONTENT = {
    "iv-sedation": """Purpose: Provide safe, comfortable dental treatment using intravenous sedation while maintaining proper breathing and response.
First 24 Hours:
- A responsible adult should remain with you today and overnight.
- No driving, operating machinery, alcohol, recreational drugs, or signing legal documents until tomorrow.
- Expect drowsiness, lightheadedness, or mild forgetfulness—move slowly from lying to standing.
- Sleep with your head elevated; use CPAP/BiPAP if prescribed.
Pain & Swelling:
- Begin prescribed/approved pain medication before numbness fully wears off.
- If permitted, many patients alternate ibuprofen and acetaminophen; follow label limits.
- Apply ice packs to the outside of your face for 20 minutes on/off for the first 24 hours.
- Switch to warm compresses after 48 hours to help with stiffness.
- Gentle jaw stretching after 3 days can help prevent limited opening if your jaw is sore.
Diet:
- Start with clear liquids (water, electrolyte drinks, broth), then advance to soft foods (yogurt, eggs, mashed potatoes).
- Avoid hot foods/drinks until numbness is gone to prevent burns.
- If you had extractions or grafting, avoid straws for at least 1 week to protect the blood clot.
Activity:
- Rest the day of your procedure; light activity the next day as tolerated.
- Avoid strenuous exercise, heavy lifting, or bending over for 48 hours.
- Change positions slowly to reduce dizziness or fainting.
Special Precautions:
- Take only medications listed on your after-visit summary or prescriptions; do not mix with extra sedatives.
- Nausea can occur—use small sips of clear fluids; take the prescribed anti-nausea medicine if needed.
- Patients with diabetes should monitor glucose more often today and maintain hydration.
- Breastfeeding: confirm medication compatibility before nursing; you may be advised to pump and discard breast milk.
- Call if you have trouble breathing, bluish lips, or severe snoring that doesn't improve when repositioned.
Follow-Up:
- Contact the office for: fever over 101°F (38.3°C), heavy bleeding, worsening pain not relieved by medication.
- Use the after-hours number provided on your paperwork. If you experience severe breathing trouble or other concerning symptoms, seek immediate medical attention.""",

    "amalgam-fillings": """Purpose: Restoration of decayed or damaged teeth using a silver-colored amalgam material.
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
- Contact the office if pain worsens or persists beyond a week.""",

    "root-canal-therapy": """Purpose: Removal of infected or damaged pulp tissue from inside the tooth, followed by sealing.
First 24 Hours:
- Avoid chewing on the treated tooth until numbness wears off.
- Some tenderness or mild discomfort is normal.
Pain & Sensitivity:
- Use OTC or prescribed pain relievers as directed.
- Tooth sensitivity to pressure may last for several days.
Oral Hygiene:
- Brush and floss normally, avoiding excessive pressure on the treated tooth.
Diet:
- Soft foods are recommended until chewing comfort improves.
Special Precautions:
- If a temporary filling is placed, avoid sticky or hard foods until the permanent restoration is done.
Follow-Up:
- A crown or permanent filling is usually required for full protection.
- Contact the office if pain worsens, swelling develops, or you notice signs of infection."""
}

async def update_with_raw_text():
    """Update procedures with exact raw text from PDFs"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔧 Updating procedures with EXACT raw text from uploaded PDFs...")
        
        for procedure_id, raw_text in RAW_PDF_CONTENT.items():
            print(f"✅ Updating {procedure_id} with raw PDF text")
            
            result = await db.procedures.update_one(
                {"id": procedure_id},
                {
                    "$set": {
                        "overview": raw_text,
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.matched_count > 0:
                print(f"   ✅ Updated with {len(raw_text)} characters")
            else:
                print(f"   ❌ Procedure not found")
        
        print(f"\n✅ Updated {len(RAW_PDF_CONTENT)} procedures with raw PDF text!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(update_with_raw_text())
    if success:
        print("\n🎯 DATABASE UPDATED WITH RAW PDF TEXT!")
    else:
        print("\n❌ Failed to update database")
