#!/usr/bin/env python3
"""
Fix IV Sedation with complete content from original uploaded PDF
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# COMPLETE IV Sedation content from original uploaded PDF
COMPLETE_IV_SEDATION_CONTENT = """Purpose: Provide safe, comfortable dental treatment using intravenous sedation while maintaining proper breathing and response.
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
- Use the after-hours number provided on your paperwork. If you experience severe breathing trouble or other concerning symptoms, seek immediate medical attention."""

async def fix_iv_sedation_complete_content():
    """Fix IV Sedation with complete content"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🏥 Fixing IV Sedation with COMPLETE content from original PDF...")
        
        # Update IV Sedation with complete content
        result = await db.procedures.update_one(
            {"id": "iv-sedation"},
            {
                "$set": {
                    "overview": COMPLETE_IV_SEDATION_CONTENT,
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count > 0:
            print(f"✅ Updated IV Sedation with complete content ({len(COMPLETE_IV_SEDATION_CONTENT)} characters)")
            
            # Verify the update
            verification = await db.procedures.find_one({"id": "iv-sedation"})
            if verification:
                new_overview = verification.get('overview', '')
                print(f"📊 Verification - New overview length: {len(new_overview)}")
                print(f"📋 First 200 characters: {new_overview[:200]}...")
                return True
            else:
                print("❌ Verification failed")
                return False
        else:
            print("❌ IV Sedation not found in database")
            return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(fix_iv_sedation_complete_content())
    if success:
        print("\n🎉 IV SEDATION CONTENT FIXED!")
        print("✅ Now contains complete post-operative care instructions")
    else:
        print("\n❌ FAILED to fix IV Sedation content")
