#!/usr/bin/env python3
"""
Update ALL remaining procedures with comprehensive, short-paragraph content
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def update_remaining_procedures():
    """Update all remaining procedures"""
    
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]

    # Get all procedure names first
    procedures = await db.procedures.find({}, {"name": 1}).to_list(length=None)
    print(f"Found {len(procedures)} total procedures")
    
    # Comprehensive overviews for remaining procedures
    comprehensive_overviews = {
        "Dental Bonding": """
**Dental Bonding - Post-Treatment Care**

**What Was Done:**
Tooth-colored composite resin was applied to repair chips, gaps, or discoloration. The material was shaped, hardened with special light, and polished to match your natural teeth.

**Immediate Post-Treatment:**
Local anesthetic (if used) will wear off in 1-2 hours - be careful not to bite your tongue or cheek. Your bite may feel slightly different initially - this usually self-adjusts within a day.

Some sensitivity to temperature is normal for 24-48 hours after bonding.

**First 24-48 Hours:**
The bonding material reaches full strength within 24 hours. Avoid very hard foods during this initial period.

Be gentle when chewing on the bonded tooth for the first day. Avoid temperature extremes - lukewarm beverages are best initially.

**Caring for Your Bonding:**
Brush and floss normally around the bonded area - composite bonding can be cleaned like natural teeth. Use fluoride toothpaste to strengthen surrounding tooth structure.

Regular dental cleanings help maintain the bonding and prevent staining.

**Preventing Damage:**
Avoid biting hard objects like ice, pens, or fingernails with bonded teeth. Don't use bonded teeth to open packages or tear tape.

Limit staining substances like coffee, tea, red wine, and tobacco - bonding can discolor over time.

**Longevity:**
Dental bonding typically lasts 3-7 years with proper care. The lifespan depends on location, bite forces, and oral habits.

Regular dental checkups monitor the bonding and surrounding tooth structure for any needed touch-ups.

**When to Call:**
Contact our office if bonding feels rough, sharp, or if a piece breaks off. Also call if you experience persistent sensitivity or pain when biting.

Bonding can usually be repaired or replaced easily if problems occur.
        """,

        "Dental Bridge Placement": """
**Dental Bridge Placement - Complete Care Guide**

**What Was Done:**
Your custom dental bridge has been cemented in place to replace missing teeth. The bridge is supported by crowns on adjacent teeth (abutments) and restores function and appearance.

**Immediate Post-Placement:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue or cheek. Avoid chewing on the bridge side until numbness wears off completely.

Some sensitivity around the supporting teeth is normal for several days.

**Bridge Adjustment Period:**
Your bite may feel different with the new bridge - this is normal and usually self-adjusts within a few days. Chewing and speaking may feel awkward initially but will improve quickly.

If the bridge feels "high" or uncomfortable when biting after 2-3 days, contact our office for adjustment.

**Special Cleaning Requirements:**
Bridges require special cleaning techniques since you cannot floss normally between the connected teeth. Use a floss threader or water flosser to clean under the bridge daily.

Brush twice daily, paying special attention to where the bridge meets your gums. Use fluoride toothpaste to protect the supporting teeth.

**Diet Guidelines:**
After 24 hours, gradually return to normal diet. Cut food into smaller pieces and chew more slowly initially.

Avoid very sticky foods (caramel, taffy) that could pull on the bridge. Minimize hard foods (ice, nuts) that could damage the bridge.

**Supporting Tooth Care:**
The success of your bridge depends on keeping the supporting teeth healthy. Excellent oral hygiene is critical to prevent decay or gum disease around the abutment teeth.

Regular professional cleanings every 6 months help maintain bridge and supporting structures.

**Long-Term Maintenance:**
Dental bridges typically last 10-15 years with proper care. Daily cleaning and regular dental visits are essential for longevity.

Report any changes in fit, comfort, or appearance promptly.

**Warning Signs:**
Contact our office if the bridge feels loose or moves when eating. Persistent pain or sensitivity in supporting teeth requires evaluation.

Food trapping under the bridge that cannot be cleaned may indicate fit problems.
        """,

        "Dental Sealants": """
**Dental Sealants - Post-Treatment Care**

**What Was Done:**
Thin protective coatings were applied to the chewing surfaces of your back teeth. Sealants fill in deep grooves and pits to prevent cavities in these hard-to-clean areas.

**Immediate Post-Treatment:**
No anesthetic was needed, so you can eat and drink normally right away. The sealant material hardened immediately under the special curing light.

Your bite may feel slightly different for the first day as you adjust to the smooth sealant surface.

**First 24 Hours:**
Avoid very sticky or chewy foods for the first 24 hours to allow sealants to fully set. Hard foods are fine - sealants are very durable.

Continue normal brushing and flossing - sealants won't interfere with your oral hygiene routine.

**Caring for Sealants:**
Brush twice daily with fluoride toothpaste as usual. Sealants can be cleaned exactly like natural tooth enamel.

Floss daily between all teeth - sealants only protect the chewing surfaces, not between teeth.

**Diet and Activities:**
No dietary restrictions after the first 24 hours. Sealants are designed to withstand normal chewing forces.

Avoid chewing ice, hard candy, or using teeth as tools - these can damage both sealants and natural teeth.

**Sealant Longevity:**
Dental sealants typically last 5-10 years with proper care. They can last even longer with good oral hygiene and regular dental visits.

Regular checkups allow us to monitor sealant condition and reapply if needed.

**Effectiveness:**
Sealants prevent up to 80% of cavities in the back teeth when properly maintained. They're especially important for children and teenagers.

Continue fluoride use and good oral hygiene - sealants work best as part of comprehensive cavity prevention.

**Follow-Up Care:**
Regular 6-month dental checkups monitor sealant integrity and overall oral health. Sealants can be easily repaired or replaced if they chip or wear.

Early detection of any sealant problems prevents cavity formation.
        """,

        "Denture Delivery": """
**New Denture Delivery - Adjustment Guide**

**What Was Done:**
Your custom-made dentures have been fitted and adjusted for optimal comfort and function. These appliances replace missing teeth and restore your ability to eat, speak, and smile confidently.

**First Few Hours:**
It's normal for dentures to feel bulky and awkward initially. Your mouth needs time to adjust to the new appliances.

Speak slowly and practice common words - your speech will improve within a few days. Start with soft foods and small bites.

**Initial Adjustment Period:**
Expect 2-4 weeks for complete adjustment to new dentures. Mild soreness and increased salivation are normal initially.

Your facial muscles and tongue need time to learn how to work with the dentures. Be patient - this is a learning process.

**Eating Guidelines:**
Start with soft foods cut into small pieces. Chew slowly and use both sides of your mouth evenly.

Avoid sticky, hard, or very hot foods initially. Gradually introduce more challenging foods as you become comfortable.

Practice with liquids first - drink slowly to avoid choking or spillage.

**Speaking Practice:**
Read aloud daily to practice speaking with dentures. Count from one to ten and repeat difficult words.

If you notice clicking sounds, you may be chewing or speaking too quickly. Slow down and the sounds will diminish.

**Daily Denture Care:**
Remove and rinse dentures after eating to prevent food buildup. Clean daily with denture brush and mild soap or denture cleaner.

Never use regular toothpaste or bleach - these can damage denture materials. Soak overnight in denture solution or plain water.

**Oral Tissue Care:**
Remove dentures for at least 6-8 hours daily (usually overnight) to allow tissues to rest. Clean your gums, tongue, and palate with soft brush.

Massage gums gently with clean finger or soft brush to maintain circulation.

**When to Return:**
Schedule follow-up appointment in 1 week for adjustment if needed. Minor sore spots are common and easily corrected.

Multiple adjustment appointments may be needed - this is completely normal.

**Warning Signs:**
Contact our office for severe pain, excessive bleeding of gums, or dentures that become very loose suddenly.

Persistent sore spots that don't improve after 3-4 days require professional adjustment.
        """,

        "Free Gingival Graft": """
**Free Gingival Graft Surgery - Recovery Guide**

**What Was Done:**
Gum tissue was taken from your palate (roof of mouth) and placed over areas of gum recession. This procedure protects exposed roots and prevents further recession.

**Two Surgical Sites:**
You have two areas healing: the donor site (palate) and the recipient site (where graft was placed). Both require special care during healing.

The palate typically heals faster than the graft site. A protective dressing may have been placed over the donor area.

**Immediate Post-Surgery:**
Bite gently on gauze for 45 minutes to control bleeding from both sites. Light bleeding for 24 hours is normal.

Take prescribed pain medication before anesthetic wears off. Apply ice packs to face: 20 minutes on, 20 minutes off for first 6 hours.

**Critical First Week:**
DO NOT disturb the graft site - avoid brushing, flossing, or touching the area. The graft needs time to attach and develop blood supply.

NO vigorous rinsing, spitting, or using straws for first 48 hours. Keep head elevated when resting.

Soft, cool diet only for first week. Avoid hot, spicy, or acidic foods that could irritate healing tissues.

**Managing Discomfort:**
The palate (donor site) is typically more uncomfortable than the graft site. This is normal and will improve within 3-5 days.

Take prescribed pain medication as directed. Over-the-counter ibuprofen is particularly effective for gum surgery.

**Oral Hygiene:**
Continue brushing and flossing other areas of your mouth normally. Avoid the surgical sites completely for first week.

After 24 hours: Very gentle salt water rinses (½ tsp salt in 8oz warm water) can be used.

After 1 week: Begin very gentle cleaning of surgical areas with soft toothbrush.

**Diet Restrictions:**
Soft foods for 2-3 weeks: pasta, cooked vegetables, soft proteins, dairy products. Avoid crunchy, spicy, or acidic foods that could disturb healing.

Chew on the opposite side of your mouth when possible.

**Healing Timeline:**
Week 1: Initial graft attachment, donor site healing begins. Weeks 2-3: Graft becomes more stable, comfort improves significantly.

Weeks 4-6: Continued tissue maturation and color changes. Month 2-3: Final healing and tissue remodeling.

**Graft Success:**
The graft will appear white or yellowish initially - this is normal. Color will gradually become more pink as healing progresses.

Some graft shrinkage is expected - final results are evaluated at 3 months.

**When to Call:**
Contact our office for severe pain not controlled by medication. Complete loss of graft material or excessive bleeding requires immediate attention.

Signs of infection: fever, increasing pain after day 3, pus formation.
        """,

        "Multiple Extractions": """
**Multiple Tooth Extractions - Recovery Protocol**

**What Was Done:**
Several teeth were removed during your appointment. Multiple extraction sites require more extensive care and longer healing time than single extractions.

**Immediate Post-Surgery:**
Bite firmly on gauze packs for 45-60 minutes to control bleeding from all sites. Replace gauze only if completely soaked through.

Take prescribed pain medication before anesthetic wears off. Begin ice therapy immediately: 20 minutes on, 20 minutes off.

**Critical First 24 Hours:**
ABSOLUTELY NO smoking, drinking through straws, or spitting - can cause dry socket in any of the extraction sites. NO vigorous rinsing or swishing.

Keep head elevated when lying down to minimize bleeding and swelling. Apply ice packs continuously for first 6-8 hours while awake.

Soft, cool diet only: pudding, yogurt, smoothies, lukewarm soup.

**Managing Bleeding:**
Some bleeding from multiple sites is expected for 12-24 hours. If persistent bleeding occurs from any site: place clean gauze over area, bite firmly for 45 minutes.

Emergency bleeding control: bite on moistened tea bags for 30 minutes. Avoid hot liquids and physical exertion.

**Controlling Swelling:**
Expect significant swelling with multiple extractions. Maximum swelling occurs at 48-72 hours - this is normal healing response.

Ice therapy is crucial: First 24 hours continuously while awake. After 48 hours: Switch to warm, moist compresses.

Sleep with head elevated for first 3 nights.

**Pain Management:**
Multiple extractions typically cause more discomfort than single extractions. Take prescribed pain medication as directed - stay ahead of pain.

Ibuprofen 800mg every 6 hours is excellent for surgical inflammation. Alternate with prescribed narcotic for breakthrough pain.

Most pain peaks at 12-24 hours, then gradually improves.

**Diet Progression:**
Day 1: Liquids and very soft foods only (protein shakes, pudding, lukewarm broth). Days 2-4: Soft foods requiring minimal chewing (mashed potatoes, pasta).

Days 5-10: Gradual return to normal diet, avoiding all extraction sites when chewing. Avoid hard, crunchy, or sticky foods for 2 weeks.

**Oral Hygiene:**
Do NOT brush extraction sites for first 48 hours. After 24 hours: Very gentle salt water rinses (½ tsp salt in 8oz warm water) 3-4 times daily.

Resume brushing other teeth normally, carefully avoiding all extraction areas. After 1 week: Very gentle cleaning near extraction sites.

**Healing Timeline:**
Days 1-5: Peak discomfort and swelling, restricted diet, careful oral hygiene. Days 6-14: Significant improvement in pain and swelling.

Weeks 2-4: Soft tissue healing complete in most areas. Weeks 6-12: Complete bone healing in all extraction sites.

**Future Planning:**
Discuss tooth replacement options during healing period. Consider dental implants, bridges, or partial dentures to restore function.

Maintain excellent oral hygiene to protect remaining teeth.

**Warning Signs:**
Call immediately for severe pain starting 2-4 days after extraction (possible dry socket). Heavy bleeding from any site not controlled by pressure.

Signs of infection: fever, increasing pain after day 3, foul taste, pus formation. Excessive swelling or difficulty swallowing.
        """,

        "Composite Fillings": """
**Composite (White) Fillings - Post-Treatment Care**

**What Was Done:**
Decayed tooth structure was removed and replaced with tooth-colored composite resin material. The filling was shaped, hardened with special light, and polished to match your natural teeth.

**Immediate Post-Treatment:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue or cheek. Avoid chewing on the filled tooth until numbness wears off completely.

Your bite may feel slightly different initially - this usually self-adjusts within a day or two.

**First 24 Hours:**
Composite fillings reach full strength immediately after light curing, so you can eat normally once numbness wears off. Some temperature sensitivity is normal for 24-48 hours.

Avoid extremely hot or cold foods initially if you experience sensitivity.

**Managing Sensitivity:**
Mild sensitivity to hot, cold, or pressure is common for 1-2 weeks after composite placement. This typically decreases gradually.

Use toothpaste for sensitive teeth if sensitivity persists. If sensitivity worsens or lasts longer than 2 weeks, contact our office.

**Caring for Composite Fillings:**
Brush and floss normally around composite fillings - they can be cleaned exactly like natural teeth. Use fluoride toothpaste to strengthen surrounding tooth structure.

Regular dental cleanings help maintain the filling and prevent new decay.

**Preventing Staining:**
Composite fillings can stain over time, especially from coffee, tea, red wine, and tobacco. Rinse with water after consuming staining substances.

Professional cleanings help remove surface stains and keep fillings looking natural.

**Bite Adjustment:**
If your bite feels "high" or uncomfortable when chewing after the anesthetic wears off, contact our office. Minor adjustments can be made easily.

Most bite issues resolve naturally within 24-48 hours as you adjust to the new filling.

**Longevity:**
Composite fillings typically last 5-10 years with proper care. The lifespan depends on size, location, and oral habits.

Avoid chewing ice, hard candy, or using teeth as tools to maximize filling lifespan.

**When to Call:**
Contact our office for severe pain not relieved by over-the-counter medication. Persistent sensitivity worsening after 2 weeks requires evaluation.

Call if you feel roughness, sharp edges, or if part of the filling breaks off.
        """,

        "Wisdom Tooth Extraction": """
**Wisdom Tooth Extraction - Recovery Guide**

**What Was Done:**
One or more wisdom teeth were surgically removed. These extractions often require more extensive care due to the location and complexity of wisdom tooth removal.

**Immediate Post-Surgery:**
Bite firmly on gauze pack for 1 hour, then remove and assess bleeding. DO NOT disturb the surgical site with tongue or fingers.

Take prescribed pain medication before anesthetic wears off. Begin ice therapy immediately: 20 minutes on, 10 minutes off.

**Critical First 24 Hours:**
ABSOLUTELY NO smoking, drinking through straws, or spitting - can cause painful dry socket. NO vigorous rinsing or swishing.

Keep head elevated when lying down to minimize bleeding and swelling. Apply ice packs continuously for first 6-8 hours while awake.

Soft, cool diet only: pudding, yogurt, smoothies, lukewarm soup.

**Managing Bleeding:**
Light bleeding mixed with saliva for 24 hours is normal after wisdom tooth extraction. If persistent bleeding occurs: place clean gauze over site, bite firmly for 45 minutes.

Emergency bleeding control: bite on a moistened tea bag for 30 minutes. Avoid hot liquids and physical exertion.

**Controlling Swelling:**
Significant facial swelling is common after wisdom tooth extraction. Maximum swelling occurs at 48-72 hours - this is expected.

Ice therapy is crucial: First 24 hours continuously while awake. After 48 hours: Switch to warm, moist compresses to promote healing.

Sleep with head elevated for first 3 nights.

**Pain Management:**
Wisdom tooth extractions typically cause moderate to severe discomfort. Take prescribed pain medication as directed - stay ahead of pain.

Ibuprofen 800mg every 6 hours is excellent for wisdom tooth surgery inflammation. Alternate with prescribed narcotic for breakthrough pain.

Most pain peaks at 24-48 hours, then gradually improves over 5-7 days.

**Diet Progression:**
Day 1: Liquids and very soft foods only (protein shakes, pudding, lukewarm broth). Days 2-4: Soft foods requiring minimal chewing (mashed potatoes, pasta).

Days 5-10: Gradual return to normal diet, avoiding extraction site when chewing. Avoid hard, crunchy, or sticky foods for 2 weeks.

**Oral Hygiene:**
Do NOT brush extraction site for first 48 hours. After 24 hours: Very gentle salt water rinses (½ tsp salt in 8oz warm water) 3-4 times daily.

Resume brushing other teeth normally, carefully avoiding extraction area. After 1 week: Very gentle cleaning near extraction site.

**Activity Restrictions:**
Avoid strenuous exercise for first 3-5 days - increased heart rate can promote bleeding and swelling. Rest and limited activity promote faster healing.

Return to normal activities gradually as comfort improves.

**Dry Socket Prevention:**
Occurs in 5-10% of wisdom tooth extractions when blood clot is lost. Prevention: Follow ALL post-operative instructions carefully.

No smoking, spitting, straws, or vigorous rinsing for 72 hours minimum.

**Warning Signs:**
Call immediately for severe pain starting 2-4 days after extraction (possible dry socket). Heavy bleeding not controlled by pressure after 6 hours.

Signs of infection: fever, increasing pain after day 3, foul taste, pus. Numbness in lip, tongue, or chin persisting beyond expected timeframe.
        """
    }

    # Update each procedure
    updated_count = 0
    for procedure_name, comprehensive_overview in comprehensive_overviews.items():
        result = await db.procedures.update_one(
            {"name": procedure_name},
            {"$set": {"overview": comprehensive_overview.strip()}}
        )
        if result.modified_count > 0:
            updated_count += 1
            print(f"✅ Updated: {procedure_name}")
        else:
            print(f"⚠️ Not found: {procedure_name}")
    
    print(f"\n📊 Updated {updated_count} more procedure overviews")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(update_remaining_procedures())