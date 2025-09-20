#!/usr/bin/env python3
"""
Create IV Sedation from backend directory using backend environment
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Add backend to path to use same environment
sys.path.append('/app/backend')

# Use backend environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

print(f"🔗 Backend environment - MONGO_URL: {MONGO_URL}")
print(f"📊 Backend environment - DB_NAME: {DB_NAME}")

async def create_iv_sedation_backend():
    """Create IV Sedation using backend environment"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔍 Checking backend database connection...")
        
        # Check collections
        collections = await db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        if 'procedures' not in collections:
            print("❌ No 'procedures' collection found!")
            return False
        
        # Check current procedure count
        total_procedures = await db.procedures.count_documents({})
        print(f"📊 Total procedures in backend database: {total_procedures}")
        
        # List first few procedures for verification
        sample_procedures = await db.procedures.find({}, {"id": 1, "name": 1}).limit(5).to_list(5)
        print("📋 Sample procedures:")
        for proc in sample_procedures:
            print(f"   - {proc.get('id')}: {proc.get('name')}")
        
        # Check if IV Sedation exists
        existing = await db.procedures.find_one({"id": "iv-sedation"})
        
        if existing:
            print("⚠️ IV Sedation already exists in backend database")
            print(f"   Name: {existing.get('name')}")
            print(f"   Specialty: {existing.get('specialty')}")
            return True
        else:
            print("➕ Creating IV Sedation in backend database...")
            
            new_procedure = {
                "id": "iv-sedation",
                "name": "I.V. Sedation",
                "overview": """Purpose: Provide safe, comfortable dental treatment using intravenous sedation while maintaining proper breathing and response.
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
            
            result = await db.procedures.insert_one(new_procedure)
            print(f"✅ Created IV Sedation with ObjectId: {result.inserted_id}")
        
        # Final verification
        verification = await db.procedures.find_one({"id": "iv-sedation"})
        if verification:
            print("\n✅ FINAL VERIFICATION SUCCESS:")
            print(f"   ID: {verification.get('id')}")
            print(f"   Name: {verification.get('name')}")
            print(f"   Specialty: {verification.get('specialty')} ({verification.get('specialtyName')})")
            print(f"   Overview length: {len(verification.get('overview', ''))}")
            
            # Check updated counts
            total_after = await db.procedures.count_documents({})
            oral_surgery_after = await db.procedures.count_documents({"specialty": "oral-surgery"})
            print(f"   Total procedures: {total_after}")
            print(f"   Oral Surgery procedures: {oral_surgery_after}")
            
            return True
        else:
            print("❌ Verification failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(create_iv_sedation_backend())
    if success:
        print("\n🎉 IV SEDATION SUCCESSFULLY CREATED IN BACKEND DATABASE!")
        print("✅ Procedure should now be accessible via API")
    else:
        print("\n❌ FAILED TO CREATE IV SEDATION")
