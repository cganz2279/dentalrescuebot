#!/usr/bin/env python3
"""
Add Screw-Retained and Cement-Retained Implant Crown procedures to database
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def add_implant_crown_procedures():
    """Add the two new implant crown procedures to the database"""
    print("🔄 ADDING IMPLANT CROWN PROCEDURES")
    print("=" * 45)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Define the two procedures
    procedures = [
        {
            'id': 'screw-retained-implant-crown',
            'name': 'Screw Retained Implant Crown',
            'overview': '''Post-Operative Instructions
Screw-Retained Implant Crown

Initial Adjustment
- Some mild tenderness or gum irritation around the implant site is normal for a few days.
- Your bite may feel slightly different at first but will adapt over time.
- You may notice a small access hole on the biting surface of the crown. This is sealed with filling material after placement.

Eating & Diet
- Avoid very hard, crunchy, or sticky foods for the first 24-48 hours.
- After this period, you may return to a normal diet — but avoid habits such as chewing ice or hard candy.
- Cut tougher foods into small pieces to reduce excess force on the crown.

Oral Hygiene
- Brush carefully twice daily, paying extra attention to the gumline around the implant.
- Floss daily using implant-safe floss or threaders to clean under the crown edges.
- Use a water flosser to remove trapped food particles if recommended by your dentist.
- Rinse daily with an antimicrobial mouthwash (alcohol-free preferred).

Special Considerations
- Screw-retained crowns can be removed by your dentist for maintenance without damaging the implant.
- The small filling material covering the screw access may wear over time and require replacement — this is normal.
- Avoid biting very hard objects that may loosen or chip the crown.

Follow-Up
- Schedule and attend regular dental visits for maintenance and professional cleaning.
- Contact our office if you feel any loosening, hear clicking when chewing, or experience pain, swelling, or bleeding near the implant.''',
            'specialty': 'oral-surgery',
            'specialtyName': 'Oral Surgery',
            'duration': 'Variable',
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'originalFilename': 'Screw_Retained_Implant_Crown_Instructions.pdf'
        },
        {
            'id': 'cement-retained-implant-crown',
            'name': 'Cement Retained Implant Crown',
            'overview': '''Post-Operative Instructions
Cement-Retained Implant Crown

Initial Adjustment
- Mild soreness or pressure around the implant area is normal for the first few days.
- Your bite may feel slightly different at first. This usually improves as your mouth adjusts.
- Increased saliva flow is normal after new crown placement.

Eating & Diet
- Avoid chewing on hard or sticky foods for the first 24-48 hours.
- After adjustment, you may return to a normal diet — but avoid chewing ice, hard candy, or very tough foods that could damage the crown.
- Chew evenly on both sides of your mouth to reduce stress on the implant.

Oral Hygiene
- Brush twice daily with a soft-bristled toothbrush.
- Floss carefully around the implant crown, using implant-safe floss or floss threaders.
- A water flosser may be used gently to keep the area clean.
- Antimicrobial rinses (if prescribed) can reduce bacteria around the crown and implant.

Special Considerations
- Cement-retained crowns are designed to look and feel natural. However, excess cement can sometimes irritate the gum tissue. If you notice persistent soreness, swelling, or bleeding, contact the office.
- Avoid using your teeth as tools (opening packages, biting nails, etc.).

Follow-Up
- Regular dental cleanings and check-ups are essential to monitor the health of the crown and implant.
- Call our office immediately if you notice loosening, pain, swelling, or unusual sensations around the crown.''',
            'specialty': 'oral-surgery',
            'specialtyName': 'Oral Surgery',
            'duration': 'Variable',
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'originalFilename': 'Cement_Retained_Implant_Crown_Instructions.pdf'
        }
    ]
    
    added_count = 0
    
    for procedure in procedures:
        # Check if procedure already exists
        existing = await db.procedures.find_one({'id': procedure['id']})
        
        if existing:
            print(f"⚠️  Procedure '{procedure['name']}' already exists, updating...")
            await db.procedures.replace_one({'id': procedure['id']}, procedure)
            print(f"✅ Updated: {procedure['name']}")
        else:
            await db.procedures.insert_one(procedure)
            print(f"✅ Added: {procedure['name']}")
            
        added_count += 1
    
    # Final verification
    print(f"\n📊 SUMMARY:")
    total_procedures = await db.procedures.count_documents({})
    oral_surgery_count = await db.procedures.count_documents({'specialtyName': 'Oral Surgery'})
    
    print(f"   Procedures processed: {added_count}")
    print(f"   Total procedures in database: {total_procedures}")
    print(f"   Oral Surgery procedures: {oral_surgery_count}")
    
    # Verify the procedures were added correctly
    print(f"\n🔍 VERIFICATION:")
    for proc_info in procedures:
        proc = await db.procedures.find_one({'id': proc_info['id']})
        if proc:
            print(f"   ✅ {proc['name']} → {proc['specialtyName']}")
        else:
            print(f"   ❌ {proc_info['name']} → NOT FOUND")
    
    print(f"\n🎉 IMPLANT CROWN PROCEDURES ADDED SUCCESSFULLY!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_implant_crown_procedures())