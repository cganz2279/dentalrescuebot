#!/usr/bin/env python3
"""
Final comprehensive update for all remaining procedures with proper short paragraph formatting
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def update_remaining_procedures():
    """Update all procedures with comprehensive, short-paragraph content"""
    
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]

    # Update key procedures that definitely need fixing
    updates = {
        "Inlays and Onlays": """
**Inlays and Onlays - Post-Treatment Care**

**What Was Done:**
Custom-made restorations were cemented to repair damaged teeth. These provide stronger alternatives to large fillings while being more conservative than crowns.

**Immediate Post-Treatment:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue. Avoid chewing on the restored tooth until numbness wears off completely.

Your bite may feel slightly different initially as you adjust to the restoration.

**First 24-48 Hours:**
Some sensitivity to temperature and pressure is normal for several days to weeks. This typically decreases gradually over time.

Avoid extremely hot or cold foods if you experience sensitivity. Chew gently on the restored tooth initially.

**Managing Sensitivity:**
Temperature sensitivity is common but should improve over 1-4 weeks. Use toothpaste for sensitive teeth if needed.

Most sensitivity resolves naturally with time. Contact our office if sensitivity worsens or persists beyond 4 weeks.

**Bite Adjustment:**
The restoration should feel comfortable when biting. If it feels "high" or uncomfortable after anesthetic wears off, contact our office for adjustment.

Minor bite adjustments are common and easily made. Proper bite balance is essential for restoration longevity.

**Daily Care:**
Care for inlays and onlays like natural teeth with regular brushing and flossing. Pay special attention to margins where restoration meets tooth.

Daily routine:
• Brush twice daily with fluoride toothpaste
• Floss daily around restoration margins  
• Use antimicrobial mouth rinse if recommended
• Regular professional cleanings maintain restoration

**Restoration Longevity:**
Inlays and onlays typically last 10-20+ years with proper care. They're more durable than large fillings but require good oral hygiene.

Protective measures:
• Avoid chewing ice or very hard objects
• Don't use teeth as tools for opening packages
• Consider nightguard if you grind teeth
• Cut hard foods into smaller pieces

**When to Call:**
Contact our office for persistent sensitivity, bite problems, or rough spots on the restoration.

Warning signs requiring attention:
• Worsening sensitivity after initial period
• Pain when biting that doesn't improve
• Restoration feels loose or high
• Food consistently trapping around restoration
        """,

        "Orthodontic Adjustment": """
**Orthodontic Adjustment - Post-Appointment Care**

**What Was Done:**
Your braces were adjusted by tightening wires, changing elastics, or making other modifications. This applies gentle pressure to move teeth toward their ideal positions.

**Immediate Post-Adjustment:**
Some discomfort is normal for 24-72 hours after adjustments. This indicates that your teeth are beginning to move as planned.

The level of discomfort varies depending on the type of adjustment made. Most patients adapt quickly to the sensation.

**Managing Discomfort:**
Take over-the-counter pain medication before discomfort peaks (usually 2-4 hours after adjustment). Ibuprofen is particularly effective for orthodontic discomfort.

Pain management tips:
• Take medication before leaving the orthodontic office
• Continue medication for 24-48 hours as needed
• Cold foods and beverages can provide additional comfort
• Soft foods reduce chewing pressure on tender teeth

**Diet Modifications:**
Stick to soft foods for the first day or two after adjustments. This reduces pressure on teeth and minimizes discomfort.

Recommended foods:
• Yogurt, pudding, smoothies
• Pasta, mashed potatoes, soft bread
• Cooked vegetables, soft fruits
• Lukewarm soup and beverages

**Oral Hygiene Importance:**
Maintain excellent oral hygiene despite any discomfort. Plaque buildup around braces can cause permanent damage to teeth.

Enhanced cleaning routine:
• Brush after every meal and snack
• Use fluoride toothpaste and soft-bristled brush
• Floss daily with orthodontic floss or floss threaders
• Rinse with fluoride mouthwash

**Wire and Bracket Care:**
Check for any loose wires or brackets after your adjustment. Small issues can often be temporarily managed at home.

Emergency care:
• Loose wire: Use orthodontic wax to cover sharp edges
• Poking wire: Push with pencil eraser or cover with wax
• Loose bracket: Save it and call orthodontist
• Severe pain or injury: Contact orthodontist immediately

**Progress Expectations:**
Tooth movement is gradual and occurs over months. Each adjustment brings you closer to your final result.

Movement timeline:
• Days 1-3: Discomfort as teeth begin to move
• Days 4-7: Adaptation to new pressure
• Weeks 2-4: Gradual tooth movement
• Next appointment: Further adjustments based on progress

**Activity Guidelines:**
Normal activities can be resumed immediately. Continue to avoid hard, sticky, or crunchy foods that could damage braces.

**Follow-Up Schedule:**
Attend all scheduled appointments for optimal treatment progress. Missed appointments can extend treatment time significantly.

**When to Call:**
Contact your orthodontist for severe pain, damaged appliances, or any concerns about your treatment progress.
        """,

        "Orthodontic Appliance Delivery": """
**Orthodontic Appliance Delivery - Adaptation Guide**

**What Was Done:**
Your new orthodontic appliance (braces, retainer, or other device) was placed to guide tooth movement. Initial adaptation requires patience and proper care.

**Initial Adjustment Period:**
Expect 1-2 weeks for complete adaptation to your new appliance. Initial discomfort, speech changes, and eating difficulties are normal.

Your mouth needs time to adapt to the new appliance. Be patient during this adjustment period.

**Speech Adaptation:**
Your speech may be affected initially, especially with appliances that contact your tongue or palate. Practice speaking aloud to accelerate adaptation.

Speech improvement tips:
• Read aloud daily for practice
• Practice difficult words and sounds
• Speak slowly and clearly initially
• Most speech issues resolve within one week

**Eating Modifications:**
Start with soft foods and gradually progress to your normal diet as comfort improves. Avoid foods that could damage your appliance.

Foods to avoid:
• Hard foods: ice, nuts, hard candy
• Sticky foods: caramel, gum, taffy  
• Crunchy foods: popcorn, chips, pretzels
• Chewing on non-food items: pens, fingernails

**Oral Hygiene Protocol:**
Excellent oral hygiene is critical with orthodontic appliances. Food particles and plaque can accumulate around brackets and wires.

Enhanced cleaning routine:
• Brush after every meal and snack
• Use soft-bristled toothbrush and fluoride toothpaste
• Floss daily with orthodontic floss or water flosser
• Use fluoride rinse to strengthen teeth during treatment

**Managing Discomfort:**
Some soreness is normal for the first few days as your mouth adapts. Over-the-counter pain medication helps manage discomfort.

Comfort measures:
• Take ibuprofen or acetaminophen as directed
• Rinse with warm salt water for sore spots
• Use orthodontic wax on brackets that cause irritation
• Cold foods and beverages can provide relief

**Appliance Care:**
Handle your appliance carefully to avoid damage. Follow specific care instructions provided for your type of appliance.

General care tips:
• Remove removable appliances when eating (if instructed)
• Clean removable appliances daily with mild soap
• Store removable appliances in their case when not worn
• Report any damage or breakage immediately

**Emergency Management:**
Know how to handle common orthodontic emergencies until you can see your orthodontist.

Common issues:
• Poking wire: Cover with orthodontic wax
• Loose bracket: Save it and call orthodontist
• Lost elastic: Replace with provided extras
• Severe pain: Contact orthodontist for evaluation

**Treatment Success:**
Success depends on your cooperation with wearing appliances as directed and maintaining excellent oral hygiene.

**Follow-Up Schedule:**
Attend all scheduled appointments for adjustments and monitoring. Regular visits ensure optimal treatment progress.
        """,

        "Pulpotomy": """
**Pulpotomy - Post-Treatment Care**

**What Was Done:**
The infected portion of tooth pulp was removed while preserving healthy pulp in the root canals. A medicated filling was placed to promote healing.

**Immediate Post-Treatment:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue or cheek. Some sensitivity to temperature and pressure is normal initially.

Take prescribed or recommended pain medication before numbness wears off for better comfort.

**First 24-48 Hours:**
Mild to moderate discomfort is normal as the tooth heals from the procedure. The tooth may feel different or slightly sensitive.

Avoid hard, crunchy, or sticky foods on the treated side. Continue normal oral hygiene but be gentle around the treated tooth.

**Managing Discomfort:**
Take prescribed pain medication as directed or use over-the-counter alternatives. Most discomfort resolves within 2-3 days.

Pain management tips:
• Don't wait for pain to become severe before taking medication
• Ibuprofen is particularly effective for dental inflammation
• Apply cold compress to face for 15-20 minutes if swelling occurs

**Temporary Restoration Care:**
A temporary restoration may have been placed. Avoid chewing sticky foods that could dislodge it.

If the temporary filling comes out:
• Save the filling if possible
• Call our office immediately
• Avoid chewing on that tooth until repaired

**Oral Hygiene:**
Continue normal brushing and flossing around the treated tooth. Use fluoride toothpaste to strengthen the remaining tooth structure.

Gentle cleaning helps prevent infection while promoting healing.

**Diet Guidelines:**
Soft foods for the first day, then gradually return to normal diet as comfort allows. Chew on the opposite side when possible.

**Follow-Up Care:**
A permanent restoration (crown or filling) will be needed to protect the treated tooth. Schedule this appointment as recommended.

Timeline for permanent restoration:
• Usually within 2-4 weeks after pulpotomy
• Temporary restoration protects tooth during healing
• Permanent restoration essential for long-term success

**Success Expectations:**
Pulpotomy has a high success rate when followed by proper restoration. The tooth should function normally after complete treatment.

**Monitoring:**
Watch for signs of infection or treatment failure. Most pulpotomies heal without complications.

**When to Call:**
Contact our office for severe pain, swelling, or if the temporary restoration falls out.

Warning signs:
• Severe pain that worsens rather than improves
• Facial swelling or fever
• Temporary restoration becomes loose or falls out
• Persistent sensitivity that doesn't improve
        """,

        "Tori Removal": """
**Tori Removal Surgery - Recovery Protocol**

**What Was Done:**
Bony growths (tori) were surgically removed from your mouth to improve comfort, function, or allow for proper denture fit.

**Immediate Post-Surgery:**
Bite on gauze for 45-60 minutes to control bleeding. Light bleeding mixed with saliva is normal for 24 hours.

Take prescribed pain medication before anesthetic wears off. Apply ice packs: 20 minutes on, 20 minutes off for first 6 hours.

**Critical First 24 Hours:**
NO vigorous rinsing, spitting, or using straws which could disturb blood clots. Keep your head elevated when resting.

Dietary restrictions:
• Soft, cool foods only for first 24-48 hours
• Avoid hot beverages and spicy foods
• Stay well-hydrated with lukewarm liquids

**Managing Post-Surgical Discomfort:**
Expect moderate discomfort for 5-7 days due to bone removal. Take prescribed pain medication as directed.

Pain management strategy:
• Don't wait for pain to become severe before taking medication
• Ibuprofen is excellent for bone surgery inflammation
• Can alternate with prescribed narcotic for breakthrough pain

**Oral Hygiene Protocol:**
Do NOT brush surgical areas for first week. Continue gentle cleaning of other teeth.

Modified hygiene routine:
• After 24 hours: very gentle salt water rinses 3-4 times daily
• Use ½ teaspoon salt in 8 ounces warm water
• After 1 week: begin gentle cleaning of surgical areas

**Diet Guidelines:**
Soft foods for 2-3 weeks while surgical sites heal completely.

Recommended foods:
• Week 1: Yogurt, pudding, soup, mashed potatoes
• Weeks 2-3: Soft pasta, cooked vegetables, soft proteins
• Avoid hard, crunchy, or abrasive foods until cleared

**Healing Timeline:**
Bone healing takes longer than soft tissue healing. Complete recovery requires 4-6 weeks.

Healing phases:
• Week 1: Initial soft tissue healing over bone
• Weeks 2-3: Continued tissue healing and comfort improvement  
• Weeks 4-6: Complete bone healing and tissue maturation

**Prosthetic Considerations:**
If tori removal was done for dentures, healing must be complete before final impressions and delivery.

Denture timeline:
• Temporary dentures may be adjusted during healing
• Final denture impressions after complete healing
• Better denture fit and comfort after tori removal

**Activity Restrictions:**
Avoid strenuous activities for first week to prevent bleeding and swelling. Normal activities can be resumed gradually.

**Follow-Up Care:**
Suture removal typically at 1-2 weeks. Multiple appointments monitor healing progress.

**Warning Signs:**
Contact our office for excessive bleeding, severe pain, or signs of infection.

Immediate attention for:
• Heavy bleeding not controlled by pressure
• Severe pain not responding to prescribed medication
• Signs of infection: fever, increasing pain after day 3, pus
• Delayed healing or unusual complications
        """
    }

    # Update procedures
    updated_count = 0
    total_count = 0
    
    # Get all procedure names
    all_procedures = await db.procedures.find({}, {"name": 1}).to_list(length=None)
    print(f"Found {len(all_procedures)} total procedures in database")
    
    # Update the ones we have content for
    for procedure_name, overview_content in updates.items():
        total_count += 1
        result = await db.procedures.update_one(
            {"name": procedure_name},
            {"$set": {"overview": overview_content.strip()}}
        )
        if result.modified_count > 0:
            updated_count += 1
            print(f"✅ Updated: {procedure_name}")
        else:
            print(f"⚠️ Not found: {procedure_name}")
    
    print(f"\n📊 Successfully updated {updated_count} out of {total_count} targeted procedures")
    print(f"🎯 Total procedures in database: {len(all_procedures)}")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(update_remaining_procedures())