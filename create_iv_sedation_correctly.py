#!/usr/bin/env python3
"""
Correctly create IV Sedation procedure in Oral Surgery
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

# EXACT content from uploaded IV Sedation PDF
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

async def create_iv_sedation():
    """Create IV Sedation procedure correctly"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🏥 Creating IV Sedation procedure in Oral Surgery...")
        
        # Check if it already exists
        existing = await db.procedures.find_one({"id": "iv-sedation"})
        
        if existing:
            print("⚠️ IV Sedation already exists - updating it")
            result = await db.procedures.update_one(
                {"id": "iv-sedation"},
                {
                    "$set": {
                        "name": "I.V. Sedation",
                        "overview": IV_SEDATION_CONTENT,
                        "specialty": "oral-surgery",
                        "specialtyName": "Oral Surgery",
                        "duration": "Variable",
                        "updatedAt": datetime.now(timezone.utc).isoformat(),
                        "contentSource": "original_uploaded_pdf"
                    }
                }
            )
            print(f"✅ Updated existing IV Sedation: {result.modified_count} documents modified")
        else:
            print("➕ Creating new IV Sedation procedure")
            
            # Create the procedure document
            procedure_doc = {
                "id": "iv-sedation",
                "name": "I.V. Sedation",
                "overview": IV_SEDATION_CONTENT,
                "specialty": "oral-surgery",
                "specialtyName": "Oral Surgery",
                "duration": "Variable",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
                "contentSource": "original_uploaded_pdf",
                "dietRestrictions": [],
                "immediateAftercare": [],
                "medications": [], 
                "recoveryTimeline": [],
                "warningSignsToCallDoctor": []
            }
            
            result = await db.procedures.insert_one(procedure_doc)
            print(f"✅ Created IV Sedation with ID: {result.inserted_id}")
        
        # Verify it was created correctly
        verification = await db.procedures.find_one({"id": "iv-sedation"})
        
        if verification:
            print("\n🔍 VERIFICATION:")
            print(f"   ID: {verification.get('id')}")
            print(f"   Name: {verification.get('name')}")
            print(f"   Specialty: {verification.get('specialty')}")
            print(f"   Specialty Name: {verification.get('specialtyName')}")
            print(f"   Overview length: {len(verification.get('overview', ''))}")
            print(f"   Content source: {verification.get('contentSource')}")
            
            # Check oral surgery count
            oral_surgery_count = await db.procedures.count_documents({"specialty": "oral-surgery"})
            print(f"   Total procedures in Oral Surgery: {oral_surgery_count}")
            
            return True
        else:
            print("❌ VERIFICATION FAILED - IV Sedation not found after creation")
            return False
        
    except Exception as e:
        print(f"❌ Error creating IV Sedation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(create_iv_sedation())
    if success:
        print("\n🎉 SUCCESS! IV Sedation created in Oral Surgery!")
        print("✅ Procedure should now be visible in the Oral Surgery section")
    else:
        print("\n❌ FAILED to create IV Sedation")
