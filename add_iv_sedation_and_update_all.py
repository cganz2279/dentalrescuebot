#!/usr/bin/env python3
"""
Add IV Sedation to Oral Surgery and use as template for all PDFs
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# EXACT content from uploaded IV Sedation PDF (without header)
IV_SEDATION_CONTENT = """Purpose: Provide safe, comfortable dental treatment using intravenous sedation while maintaining proper breathing and response.
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

async def add_iv_sedation_and_update_all():
    """Add IV Sedation to Oral Surgery and update all procedures with this template format"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🏥 Adding IV Sedation to Oral Surgery section...")
        
        # First, check if IV Sedation already exists
        existing = await db.procedures.find_one({"id": "iv-sedation"})
        
        if existing:
            print("✅ IV Sedation already exists - updating content")
            result = await db.procedures.update_one(
                {"id": "iv-sedation"},
                {
                    "$set": {
                        "overview": IV_SEDATION_CONTENT,
                        "specialty": "oral-surgery",
                        "specialtyName": "Oral Surgery",
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
        else:
            print("➕ Creating new IV Sedation procedure")
            result = await db.procedures.insert_one({
                "id": "iv-sedation",
                "name": "I.V. Sedation",
                "overview": IV_SEDATION_CONTENT,
                "specialty": "oral-surgery",
                "specialtyName": "Oral Surgery",
                "duration": "Variable",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "contentSource": "original_uploaded_pdf"
            })
        
        print("✅ IV Sedation added/updated in Oral Surgery")
        
        # Now update ALL other procedures to use this template format
        print("\n🔄 Updating ALL procedures to use IV Sedation template format...")
        
        # Get all procedures except IV Sedation
        all_procedures = await db.procedures.find({"id": {"$ne": "iv-sedation"}}).to_list(1000)
        print(f"📊 Found {len(all_procedures)} procedures to update")
        
        updated_count = 0
        
        for procedure in all_procedures:
            procedure_id = procedure.get('id')
            procedure_name = procedure.get('name', 'Unknown')
            
            # Create content in the same format as IV Sedation template
            template_content = f"""Purpose: Post-operative care instructions for {procedure_name}.
First 24 Hours:
- Follow all post-procedure instructions provided by your dentist.
- Some discomfort or sensitivity is normal after treatment.
- Avoid chewing on the treated area until numbness wears off.
Pain & Swelling:
- Use prescribed or over-the-counter pain relievers as directed.
- Apply ice packs to reduce swelling if recommended by your dentist.
- Contact the office if pain is severe or worsening.
Diet:
- Follow any dietary restrictions provided for this procedure.
- Avoid foods that may irritate or damage the treated area.
- Stay hydrated with plenty of fluids.
Activity:
- Rest as needed and avoid strenuous activities if recommended.
- Follow your dentist's specific activity guidelines for this procedure.
Special Precautions:
- Follow all specific precautions given for this type of procedure.
- Take medications only as prescribed or recommended.
- Maintain good oral hygiene as instructed by your dental team.
Follow-Up:
- Attend all scheduled follow-up appointments.
- Contact the office if you have concerns about your recovery.
- Use the after-hours number for urgent issues outside office hours."""
            
            # Update the procedure
            result = await db.procedures.update_one(
                {"id": procedure_id},
                {
                    "$set": {
                        "overview": template_content,
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                updated_count += 1
            
            print(f"✅ Updated {procedure_name}")
        
        print(f"\n🎉 COMPLETE! Updated {updated_count} procedures with template format")
        print("✅ IV Sedation added to Oral Surgery")
        print("✅ All procedures now use consistent template format")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(add_iv_sedation_and_update_all())
    if success:
        print("\n🎯 SUCCESS! IV Sedation added and all PDFs updated with template format!")
    else:
        print("\n❌ Failed to complete updates")
