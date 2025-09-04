#!/usr/bin/env python3
"""
Fix ALL procedures with maximum 2-3 sentence paragraphs and bullet lists
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_all_procedures_final():
    """Fix all procedures with proper short paragraphs and bullet lists"""
    
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]

    # Get all procedure names
    all_procedures = await db.procedures.find({}, {"name": 1}).to_list(length=None)
    procedure_names = [p["name"] for p in all_procedures]
    print(f"Found {len(procedure_names)} procedures to update")

    # Create comprehensive updates with proper short paragraph formatting
    updates = {}

    # Process each procedure with proper formatting
    for proc_name in procedure_names:
        if proc_name == "Amalgam Fillings":
            updates[proc_name] = """
**Silver Amalgam Fillings - Care Guide**

**What Was Done:**
Decayed tooth structure was removed. It was replaced with silver amalgam filling material.

**Immediate Post-Treatment (First 4 Hours):**
Local anesthetic will wear off in 2-4 hours. Be careful not to bite your tongue or cheek.

Your bite may feel "high" initially - this is normal.
• Some sensitivity to temperature is expected
• Avoid chewing on filled tooth until numbness wears off

**First 24 Hours - Critical Period:**
NEW AMALGAM FILLINGS TAKE 24 HOURS TO FULLY HARDEN.

Recommended foods:
• Pasta, cooked vegetables  
• Soft bread, dairy products
• Avoid very hot or cold foods
• Gentle brushing is fine around new filling

**Managing Sensitivity:**
Temperature sensitivity is normal for 1-4 weeks. Use toothpaste for sensitive teeth if needed.

Tips for comfort:
• Avoid temperature extremes
• Lukewarm beverages are best
• Most sensitivity decreases over time

**Bite Adjustment:**
New fillings may feel "high" when biting - this is common. Most bite issues self-adjust within 1-2 weeks.

If significant discomfort persists beyond 1 week:
• Contact our office for adjustment
• Avoid excessive grinding on new filling

**Long-Term Care:**
Amalgam fillings typically last 10-15 years. Initial metallic taste disappears within days.

Daily care routine:
• Resume normal brushing within 24 hours
• Floss daily around the filling
• Use fluoride toothpaste
• Regular dental checkups monitor filling

**When to Call:**
• Severe pain not relieved by medication
• Sensitivity worsening after 2 weeks  
• Filling feels loose or high after 2 weeks
            """

        elif proc_name == "Root Canal Therapy":
            updates[proc_name] = """
**Root Canal Therapy - Recovery Guide**

**What Was Done:**
Infected pulp tissue was removed from your tooth. The canals were cleaned and sealed to save your natural tooth.

**Immediate Post-Treatment (First 4 Hours):**
Keep temporary filling intact. Take prescribed pain medication BEFORE numbness wears off.

Numbness will wear off in 2-4 hours:
• Be careful not to bite tongue or cheek
• Some pressure sensation is normal
• Avoid chewing on treated tooth

**First 24-48 Hours:**
Mild to moderate discomfort is completely normal. The tooth may feel "different" initially.

Care instructions:
• Avoid hard, crunchy foods on treated side
• Continue normal oral hygiene gently
• Sleep with head slightly elevated
• Cold compress for 20 minutes if needed

**Pain Management:**
Don't wait for pain to become severe. Ibuprofen 600-800mg every 6 hours works well.

Options for pain control:
• Can alternate ibuprofen with acetaminophen
• Apply cold compress first 24 hours
• Warm compresses after 48 hours may help

**What to Expect:**
Days 1-3: Mild discomfort, sensitivity to biting. Days 4-7: Gradual improvement.

Week 2: Most discomfort resolved. Week 3-4: Complete healing, ready for crown.

**CRITICAL Follow-Up:**
You MUST return for permanent crown within 2-4 weeks. Temporary filling is NOT permanent.

Why permanent restoration is essential:
• Prevents reinfection
• Root canal teeth are more brittle  
• Crown protects against fracture
• Schedule immediately if not done

**Warning Signs - Call Immediately:**
• Severe uncontrolled pain
• Significant facial swelling
• Fever over 101°F
• Temporary filling falls out completely
            """

        elif proc_name == "Dental Crown Placement":
            updates[proc_name] = """
**Dental Crown Placement - Care Guide**

**What Was Done:**
Your custom crown was cemented over your prepared tooth. It restores function and appearance for 10-20+ years.

**Immediate Post-Placement:**
Local anesthetic wears off in 2-4 hours. Be careful not to bite tongue or cheek.

Some sensitivity is normal:
• Temperature sensitivity for days to weeks
• Avoid chewing on crown side until numbness gone
• Take pain medication as needed

**Crown Adjustment Period:**
Your bite may feel different initially. Most issues self-adjust within days.

Normal adjustment signs:
• Crown may feel "high" at first
• Mild hot/cold sensitivity is common
• Should gradually decrease over time

**Managing Sensitivity:**
Temperature sensitivity is normal for 1-4 weeks. Use sensitive teeth toothpaste if needed.

Comfort tips:
• Avoid temperature extremes initially
• Lukewarm beverages are best
• Contact office if sensitivity worsens

**Daily Care Requirements:**
Resume normal brushing and flossing within 24 hours. Crown margins need extra attention.

Proper crown care:
• Brush twice daily with fluoride toothpaste
• Floss daily around crown margins
• Crowns can get cavities at edges
• Regular professional cleanings essential

**Diet Guidelines:**
Resume normal diet after 24 hours gradually. Avoid damaging habits.

Protect your crown:
• Don't chew ice or hard candy
• Avoid using teeth as tools
• Cut hard foods into smaller pieces
• Consider nightguard if you grind teeth

**Long-Term Success:**
Excellent oral hygiene is key to crown longevity. Professional maintenance is essential.

Success factors:
• Daily brushing and flossing
• 6-month dental checkups
• Avoid destructive habits
• Healthy gums around crown

**When to Call:**
• Crown feels loose or falls out
• Persistent worsening sensitivity
• Pain when biting after 1-2 weeks
• Sharp edges or rough spots
            """

        elif proc_name == "Dental Implant Placement":
            updates[proc_name] = """
**Dental Implant Surgery - Recovery Protocol**

**What Was Done:**
Titanium implant was placed in your jawbone. It will integrate over 3-6 months before receiving final crown.

**Immediate Post-Surgery:**
Bite on gauze for 1 hour firmly. Don't disturb site with tongue or fingers.

Essential first steps:
• Take pain medication before numbness wears off
• Begin ice therapy: 20 minutes on, 10 minutes off
• Avoid touching surgical site

**Critical 48-Hour Period:**
ABSOLUTELY NO SMOKING - increases failure risk dramatically. NO spitting, rinsing vigorously, or straws.

Essential precautions:
• Sleep with head elevated 2-3 nights
• Soft, cool diet only for 48 hours
• Take antibiotics exactly as prescribed
• Apply ice continuously while awake

**Managing Pain and Swelling:**
Maximum swelling occurs at 48-72 hours - this is normal. Ice therapy is crucial first 48 hours.

Pain control strategy:
• Don't wait for severe pain to take medication
• Ibuprofen 600-800mg every 6 hours excellent
• After 48 hours: switch to warm compresses
• Most pain improves significantly after 3-5 days

**Diet During Healing:**
Days 1-7: Soft foods only. Weeks 2-3: Firmer foods, avoid implant site.

Recommended foods:
• Yogurt, pudding, mashed potatoes
• Protein shakes, soup
• Stay well-hydrated
• Avoid very hard foods until crown placed

**Oral Care Protocol:**
Do NOT brush implant site first week. Continue cleaning other teeth.

Hygiene progression:
• After 24 hours: gentle salt water rinses
• After 1 week: very gentle cleaning with soft brush
• Use prescribed mouth rinse as directed

**Integration Period (Osseointegration):**
3-4 months lower jaw, 4-6 months upper jaw. Implant must remain undisturbed.

Critical healing phase:
• No pressure on implant during healing
• Temporary tooth options available
• Regular monitoring appointments essential

**Warning Signs - Call Immediately:**
• Severe pain not controlled by medication
• Fever, increasing pain after day 3
• Implant feels loose or mobile
• Excessive bleeding not controlled by pressure
            """

        elif proc_name == "Inlays and Onlays":
            updates[proc_name] = """
**Inlays and Onlays - Post-Treatment Care**

**What Was Done:**
Custom restorations were cemented to repair damaged teeth. They're stronger than fillings, more conservative than crowns.

**Immediate Post-Treatment:**
Local anesthetic wears off in 2-4 hours. Be careful not to bite tongue.

Initial care:
• Avoid chewing on restored tooth until numbness gone
• Bite may feel different initially - this is normal
• Some sensitivity expected for days to weeks

**First 24-48 Hours:**
Temperature sensitivity is common but should improve. This typically decreases gradually.

Comfort measures:
• Avoid extremely hot/cold foods if sensitive
• Chew gently on restored tooth initially
• Normal oral hygiene can resume immediately

**Managing Sensitivity:**
Most sensitivity resolves in 1-4 weeks. Use sensitive teeth toothpaste if needed.

When to contact office:
• Sensitivity worsens rather than improves
• Sensitivity persists beyond 4 weeks
• Pain when biting doesn't resolve

**Bite Adjustment:**
Restoration should feel comfortable when biting. Contact office if feels "high" after anesthetic wears off.

Important notes:
• Minor adjustments are common and easy
• Don't adjust to uncomfortable bite
• Proper balance essential for longevity

**Daily Care Requirements:**
Care like natural teeth with regular brushing and flossing. Pay attention to margins.

Daily routine:
• Brush twice daily with fluoride toothpaste
• Floss daily around restoration margins
• Antimicrobial rinse if recommended
• Regular professional cleanings essential

**Restoration Longevity:**
Typically last 10-20+ years with proper care. More durable than large fillings.

Protective measures:
• Avoid chewing ice or hard objects
• Don't use teeth as tools
• Consider nightguard if you grind teeth
• Cut hard foods into smaller pieces

**When to Call:**
• Persistent sensitivity or bite problems
• Restoration feels loose or rough
• Food consistently trapping around restoration
• Sharp edges or unusual changes
            """

        else:
            # For other procedures, create a basic but well-formatted template
            updates[proc_name] = f"""
**{proc_name} - Post-Treatment Care**

**What Was Done:**
Your {proc_name.lower()} procedure was completed successfully. This treatment helps restore your oral health and function.

**Immediate Post-Treatment:**
Some discomfort and sensitivity are normal initially. Take prescribed or recommended pain medication as directed.

Follow these guidelines:
• Be gentle with the treated area
• Avoid extremely hot or cold foods initially
• Maintain good oral hygiene carefully

**First 24-48 Hours:**
The treated area needs time to heal properly. Stick to soft foods when possible.

Care instructions:
• Follow all specific instructions given
• Take medications as prescribed
• Apply ice if swelling occurs (20 min on/off)
• Keep head elevated when resting

**Managing Discomfort:**
Mild to moderate discomfort is expected. This should improve over the next few days.

Pain management:
• Don't wait for severe pain before taking medication
• Ibuprofen is effective for dental inflammation
• Contact office if pain worsens after 48 hours

**Oral Hygiene:**
Continue brushing and flossing other areas normally. Be gentle around treated area.

Cleaning routine:
• Use soft-bristled toothbrush
• Gentle salt water rinses after 24 hours
• Avoid vigorous rinsing initially
• Return to normal hygiene as comfort allows

**Diet Guidelines:**
Soft foods for first few days help promote healing. Gradually return to normal diet.

Recommended foods:
• Yogurt, soup, pasta
• Cooked vegetables, soft proteins
• Lukewarm beverages
• Avoid hard, crunchy, or spicy foods initially

**Follow-Up Care:**
Attend all scheduled follow-up appointments. Report any concerns promptly.

Important reminders:
• Keep all scheduled appointments
• Follow all post-treatment instructions
• Contact office with questions or concerns

**When to Call:**
• Severe pain not relieved by medication
• Excessive bleeding or swelling
• Signs of infection (fever, pus)
• Any unusual symptoms or concerns
            """

    # Update all procedures
    updated_count = 0
    for proc_name, overview_content in updates.items():
        result = await db.procedures.update_one(
            {"name": proc_name},
            {"$set": {"overview": overview_content.strip()}}
        )
        if result.modified_count > 0:
            updated_count += 1
            print(f"✅ Updated: {proc_name}")

    print(f"\n📊 Successfully updated {updated_count} procedures with proper short paragraphs and bullet lists")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_all_procedures_final())