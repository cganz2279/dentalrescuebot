#!/usr/bin/env python3
"""
Update ALL procedure overviews with comprehensive, well-formatted content in short paragraphs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def update_all_procedures():
    """Update all 80+ procedures with comprehensive content"""
    
    # Connect to MongoDB directly
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]

    # Comprehensive overviews for ALL procedures - short 2-3 sentence paragraphs
    comprehensive_overviews = {
        "Alveoloplasty": """
**Alveoloplasty (Jawbone Recontouring) - Recovery Guide**

**What Was Done:**
Alveoloplasty reshapes and smooths the jawbone after tooth extractions. This creates an optimal foundation for dentures or eliminates sharp bone edges.

**Immediate Care:**
Keep gauze in place for 45-60 minutes with firm pressure. Replace only if completely soaked through with blood.

Bite down firmly but avoid excessive chewing motions. Avoid talking unnecessarily to prevent disrupting blood clot formation.

**Critical First 24 Hours:**
NO rinsing, spitting, or using straws - these can dislodge blood clots. Keep your head elevated when resting to minimize swelling.

Apply ice packs for 20 minutes on, 20 minutes off during the first 6-8 hours. Stick to soft, cool foods like yogurt and pudding.

Take prescribed antibiotics exactly as directed to prevent infection.

**Managing Bleeding:**
Light oozing for 24-48 hours is normal and expected. If active bleeding occurs, bite on clean gauze for 45 minutes with steady pressure.

Emergency protocol: bite on a moistened tea bag for 30 minutes. Avoid hot liquids, alcohol, and smoking which promote bleeding.

**Controlling Swelling:**
Maximum swelling occurs 48-72 hours post-surgery - this is completely normal. Use ice therapy for first 48 hours only, then switch to warm compresses.

Use warm salt water rinses after 24 hours: ½ tsp salt in 8oz warm water, 3-4 times daily. Sleep elevated for first 3 nights.

**Pain Management:**
Take prescribed pain medication as directed - stay ahead of pain. Ibuprofen 600-800mg every 6 hours is excellent for surgical swelling.

You can combine with acetaminophen for breakthrough pain. Avoid aspirin as it increases bleeding risk.

**Healing Timeline:**
Days 1-3: Peak discomfort and swelling, restricted diet. Days 4-7: Significant improvement, gradual diet expansion.

Weeks 2-3: Soft tissue healing complete, comfortable chewing. Weeks 4-8: Complete bone remodeling.

**Call Immediately For:**
Severe pain not controlled by medication. Excessive bleeding not controlled by pressure. Signs of infection: fever, increasing pain after day 3, foul taste.
        """,

        "Amalgam Fillings": """
**Silver Amalgam Fillings - Post-Treatment Care**

**What Was Done:**
Decayed tooth structure was removed and replaced with silver amalgam filling material. Amalgam is a durable metal alloy safely used in dentistry for over 150 years.

**Immediate Post-Treatment:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue or cheek. Avoid chewing on the filled tooth until numbness wears off completely.

Your bite may feel "high" or different initially - this is normal. Some sensitivity to temperature and pressure is expected for several days.

**First 24 Hours:**
NEW AMALGAM FILLINGS TAKE 24 HOURS TO FULLY HARDEN. Avoid hard chewing during this critical period.

Stick to soft foods: pasta, cooked vegetables, soft bread, dairy products. Avoid very hot or cold foods as sensitivity is common initially.

Gentle brushing and flossing is fine, but be careful around the new filling.

**Managing Sensitivity:**
Temperature sensitivity (hot/cold) is normal for 1-4 weeks after placement. Bite sensitivity when chewing may occur for several days to weeks.

Use toothpaste for sensitive teeth if sensitivity persists. Avoid temperature extremes - lukewarm beverages are best initially.

**Bite Adjustment:**
New fillings may feel "high" when you bite down - this is very common. Most bite issues self-adjust within 1-2 weeks as you naturally wear the filling surface.

If significant bite discomfort persists beyond 1 week, contact our office. Avoid excessive chewing or grinding on the new filling during adjustment period.

**Long-Term Care:**
Amalgam fillings typically last 10-15 years with proper care. Initial metallic taste may occur but disappears within a few days.

The filling may darken slightly over time - this is normal aging. Regular dental checkups monitor filling integrity and surrounding tooth health.

**Daily Hygiene:**
Resume normal brushing and flossing within 24 hours. Amalgam fillings can be cleaned exactly like natural teeth.

Floss daily around the filling to prevent future decay. Use fluoride toothpaste to strengthen surrounding tooth structure.

**When to Call:**
Contact our office for severe pain not relieved by over-the-counter medication. Also call if sensitivity worsens after 2 weeks or the filling feels loose.
        """,

        "Apicoectomy": """
**Apicoectomy (Root Tip Surgery) - Recovery Guide**

**What Was Done:**
The infected tip of your tooth root was surgically removed through the gum. The root canal was sealed from the tip to prevent future infection.

**Immediate Post-Surgery:**
Bite firmly on gauze pack for 1 hour, then remove and assess bleeding. Do NOT disturb the surgical site with your tongue or fingers.

Take prescribed pain medication before anesthetic wears off. Begin ice therapy immediately: 20 minutes on, 10 minutes off.

**Critical First 48 Hours:**
ABSOLUTELY NO SMOKING - dramatically increases failure risk and delays healing. NO spitting, rinsing vigorously, or using straws.

Sleep with head elevated for first 2-3 nights. Soft, cool diet only for 48 hours - avoid hot foods and beverages.

Take prescribed antibiotics exactly as directed to prevent infection.

**Managing Pain and Swelling:**
Ice therapy: First 48 hours continuously while awake (20 min on/10 min off). Maximum swelling occurs at 48-72 hours - this is normal healing.

After 48 hours: Switch to warm, moist heat to promote healing. Take prescribed pain medication as directed - don't wait for severe pain.

Most patients experience moderate pain for 3-5 days, then rapid improvement.

**Oral Care:**
Do NOT brush surgical site for first week. Rinse gently with prescribed antimicrobial rinse or salt water after 24 hours.

Continue normal brushing and flossing of other teeth. After 1 week: Very gentle cleaning around surgical site with soft toothbrush.

**Diet Guidelines:**
Days 1-7: Soft foods only (yogurt, pudding, mashed potatoes, protein shakes). Weeks 2-3: Introduce slightly firmer foods, avoid chewing near surgical site.

Stay well-hydrated and maintain good nutrition to support healing.

**Healing Timeline:**
Week 1: Initial soft tissue healing, suture removal if needed. Weeks 2-4: Continued soft tissue healing and comfort improvement.

Months 1-3: Complete bone healing around root tip. Most apicoectomies are successful long-term.

**Warning Signs:**
Contact our office immediately for severe pain not controlled by medication. Signs of infection: fever, increasing pain after day 3, pus, bad taste.

Also call for excessive bleeding not controlled by pressure.
        """,

        "Biopsy Oral Soft Tissue": """
**Oral Soft Tissue Biopsy - Post-Procedure Care**

**What Was Done:**
A small sample of oral tissue was removed for laboratory examination. The site was closed with sutures to promote proper healing.

**Immediate Post-Biopsy:**
Bite gently on gauze for 30-45 minutes to control any bleeding. Light bleeding or oozing for several hours is normal.

Avoid disturbing the biopsy site with your tongue or fingers. Take prescribed pain medication as needed for discomfort.

**First 24-48 Hours:**
Keep the biopsy site clean and undisturbed. Avoid hot, spicy, or acidic foods that could irritate the area.

Stick to soft, lukewarm foods for the first day. Gentle oral hygiene is important but avoid the biopsy site directly.

**Managing Discomfort:**
Mild to moderate discomfort is normal for 2-3 days. Over-the-counter pain medication is usually sufficient for most patients.

Avoid aspirin as it can increase bleeding risk. Use acetaminophen or ibuprofen as directed.

**Oral Hygiene:**
Continue brushing and flossing other areas of your mouth normally. Avoid the biopsy site for the first week.

After 24 hours: Gentle salt water rinses (½ tsp salt in 8oz warm water) can help keep the area clean.

**Diet Recommendations:**
Soft foods for 3-5 days: pasta, cooked vegetables, soft proteins, dairy products. Avoid hard, crunchy, or spicy foods that could irritate the site.

Stay well-hydrated and maintain good nutrition to support healing.

**Follow-Up Care:**
Suture removal appointment typically in 7-10 days if needed. Results from the laboratory usually available in 7-14 days.

We will contact you with biopsy results and discuss any necessary follow-up treatment.

**When to Call:**
Contact our office for excessive bleeding that doesn't stop with pressure. Signs of infection: increasing pain after day 3, fever, pus formation.

Also call if sutures come loose before your scheduled removal appointment.
        """,

        "Bone Grafting": """
**Bone Grafting Surgery - Recovery Protocol**

**What Was Done:**
Bone grafting material was placed to augment bone volume for future implant placement. The graft stimulates your body's natural bone regeneration process.

**Immediate Post-Surgery:**
Bite firmly on gauze pack for 1 hour, then assess bleeding. DO NOT disturb the surgical site with tongue or fingers.

Take prescribed pain medication before anesthetic wears off. Begin ice therapy immediately: 20 minutes on, 10 minutes off.

**Critical First 48 Hours:**
ABSOLUTELY NO SMOKING - dramatically reduces graft success. NO spitting, rinsing vigorously, or using straws - can disrupt graft material.

Sleep with head elevated for first 2-3 nights. Soft, cool diet only: avoid hot foods and beverages for 48 hours.

Take prescribed antibiotics exactly as directed to prevent infection.

**Protecting the Graft:**
The bone graft material must remain undisturbed for successful integration. Avoid vigorous rinsing or spitting for at least 1 week.

Do not probe the area with tongue or instruments. Small graft particles may be visible - this is normal.

Some graft material loss during initial healing is expected and normal.

**Managing Bleeding:**
Light bleeding/oozing for 24-48 hours is completely normal. If persistent bleeding occurs, bite on clean gauze for 45 minutes with continuous pressure.

Avoid hot liquids, alcohol, and physical exertion which increase bleeding.

**Controlling Swelling:**
Ice therapy: First 48 hours continuously (20 min on/10 min off while awake). Maximum swelling occurs at 48-72 hours - this is normal.

After 48 hours: Switch to warm, moist heat to promote healing. Gentle facial massage after day 3 can help reduce swelling.

**Pain Management:**
Take prescribed pain medication as directed - don't wait for severe pain. Ibuprofen 600-800mg every 6 hours is excellent for bone graft inflammation.

Most patients experience moderate pain for 3-5 days, then rapid improvement.

**Healing Timeline:**
Weeks 1-2: Initial soft tissue healing over graft site. Weeks 3-6: Early bone formation begins within graft material.

Months 2-4: Active bone regeneration and graft integration. Months 4-6: Mature bone formation ready for implant placement.

**Warning Signs:**
Contact our office immediately for severe pain not controlled by medication. Signs of infection: fever, increasing pain after day 3, pus.

Also call for complete loss of graft material from site.
        """,

        "Crown Lengthening": """
**Crown Lengthening Surgery - Recovery Guide**

**What Was Done:**
Gum tissue and possibly bone were reshaped to expose more of your tooth structure. This creates adequate space for a proper crown or filling.

**Immediate Post-Surgery:**
Bite gently on gauze for 45 minutes to control bleeding. Light bleeding mixed with saliva for 24 hours is normal.

Take prescribed pain medication before anesthetic wears off. Apply ice packs: 20 minutes on, 20 minutes off for first 6 hours.

**Critical First 24 Hours:**
NO vigorous rinsing, spitting, or using straws for first 24 hours. Keep your head elevated when resting to minimize swelling.

Stick to soft, cool foods. Avoid hot beverages and spicy foods that could irritate the surgical site.

**Managing Discomfort:**
Mild to moderate discomfort is normal for 3-5 days. Take prescribed pain medication as directed or use over-the-counter alternatives.

Ibuprofen is particularly effective for reducing both pain and swelling after gum surgery.

**Oral Hygiene:**
Do NOT brush the surgical area for first week. Continue normal brushing of other teeth carefully.

After 24 hours: Gentle salt water rinses (½ tsp salt in 8oz warm water) 3-4 times daily.

After 1 week: Very gentle brushing of surgical area with soft toothbrush.

**Diet Guidelines:**
Soft foods for first week: pasta, cooked vegetables, soft proteins, dairy products. Avoid hard, crunchy, or sticky foods that could disturb healing.

Stay well-hydrated and maintain good nutrition to support healing.

**Healing Timeline:**
Days 1-3: Peak discomfort and swelling, careful oral hygiene. Days 4-7: Gradual improvement in comfort.

Weeks 2-4: Soft tissue healing and reshaping continues. Weeks 6-8: Final tissue contours established.

**Follow-Up Care:**
Suture removal typically in 7-10 days. Crown or filling placement usually 6-8 weeks after surgery to allow complete healing.

Regular periodontal maintenance helps ensure long-term success.

**When to Call:**
Contact our office for severe pain not controlled by medication. Signs of infection: fever, increasing pain after day 3, pus formation.

Excessive bleeding that doesn't respond to pressure after 4-6 hours.
        """,

        "Dental Crown Placement": """
**Dental Crown Placement - Complete Care Guide**

**What Was Done:**
Your custom-fabricated permanent crown has been cemented over your prepared tooth. The crown restores function, strength, and appearance for 10-20+ years with proper care.

**Immediate Post-Placement:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue or cheek. Avoid chewing on the crown side until numbness wears off completely.

Some sensitivity to temperature and pressure is normal for several days to weeks.

**Crown Adjustment Period:**
Your bite may feel slightly different - this is normal and usually self-adjusts within a few days. The crown may feel "high" initially, but most bite issues resolve naturally.

Mild sensitivity to hot/cold is common and should gradually decrease. If significant bite discomfort persists beyond 1 week, contact our office.

**Managing Sensitivity:**
Temperature sensitivity is normal for 1-4 weeks after crown placement. Use toothpaste for sensitive teeth if sensitivity persists.

Avoid temperature extremes initially - lukewarm beverages are best. Sensitivity should gradually improve - contact us if it worsens.

**Daily Care:**
Resume normal brushing and flossing within 24 hours. Crown margins (where crown meets tooth) require extra attention to prevent decay.

Floss daily around the crown - crowns can get cavities at the margins. Use fluoride toothpaste to protect natural tooth structure under the crown.

**Diet Guidelines:**
After 24 hours, resume normal diet gradually. Avoid chewing ice, hard candy, or using teeth as tools.

Minimize sticky, hard, or overly chewy foods that could damage the crown. Consider a nightguard if you grind or clench your teeth.

**Long-Term Care:**
Crowns require the same care as natural teeth - brush twice daily and floss daily. Regular dental checkups every 6 months monitor the crown and surrounding tissues.

Professional cleanings remove plaque from crown margins where decay commonly starts.

**Crown Longevity:**
Excellent oral hygiene is the #1 factor in crown longevity. Regular dental visits for professional cleaning and monitoring are essential.

Avoid destructive habits like chewing ice or opening packages with teeth.

**When to Call:**
Contact our office if the crown feels loose, shifts, or falls out. Also call for persistent sensitivity that worsens rather than improves.

Pain when biting that doesn't resolve within 1-2 weeks requires evaluation.
        """,

        "Dental Implant Placement": """
**Dental Implant Surgery - Recovery Protocol**

**What Was Done:**
A titanium implant was surgically placed into your jawbone to replace a missing tooth root. The implant will integrate with your bone over 3-6 months before receiving the final crown.

**Immediate Post-Surgery:**
Bite firmly on gauze pack for 1 hour, then assess bleeding. Avoid disturbing the surgical site with tongue, fingers, or toothpicks.

Take prescribed pain medication before anesthetic wears off. Begin ice therapy immediately: 20 minutes on, 10 minutes off.

**Critical 48-Hour Period:**
ABSOLUTELY NO SMOKING - dramatically increases failure risk and delays healing. NO spitting, rinsing vigorously, or using straws - can disrupt blood clots.

Sleep with head elevated for first 2-3 nights. Soft, cool diet only: avoid hot foods and beverages for 48 hours.

Take prescribed antibiotics exactly as directed to prevent infection.

**Managing Pain and Swelling:**
Ice therapy: First 48 hours continuously (20 min on/10 min off while awake). Maximum swelling occurs at 48-72 hours - this is normal healing.

After 48 hours: Switch to warm, moist heat to promote healing. Take prescribed pain medication as directed - don't wait for severe pain.

Ibuprofen 600-800mg every 6 hours is excellent for implant surgery inflammation.

**Diet During Healing:**
Days 1-7: Soft foods only (yogurt, pudding, mashed potatoes, protein shakes). Weeks 2-3: Introduce slightly firmer foods, avoid chewing near implant site.

Weeks 4-8: Normal diet, but avoid very hard foods until final crown placed. Stay well-hydrated and maintain good nutrition.

**Oral Care:**
Do NOT brush implant site for first week. Rinse gently with prescribed antimicrobial rinse or salt water after 24 hours.

Continue normal brushing and flossing of other teeth. After 1 week: Very gentle cleaning around implant with soft toothbrush.

**Integration Period:**
3-4 months for lower jaw, 4-6 months for upper jaw. Implant must remain undisturbed during this critical period.

No pressure or chewing forces on implant during healing. Temporary tooth replacement options will be discussed.

**Success Factors:**
Excellent oral hygiene throughout healing is essential. No smoking or tobacco use - critically important for success.

Compliance with all post-operative instructions and regular follow-up appointments.

**Warning Signs:**
Contact our office immediately for severe pain not controlled by medication. Signs of infection: fever, increasing pain after day 3, pus, bad taste.

If the implant feels loose or mobile, call immediately.
        """,

        "Root Canal Therapy": """
**Root Canal Therapy - Complete Post-Operative Guide**

**What Was Done:**
Infected or inflamed pulp tissue was removed from inside your tooth's root canals. The canals were cleaned, disinfected, shaped, and sealed with biocompatible material to save your natural tooth.

**Immediate Post-Treatment:**
Keep the temporary filling intact and avoid chewing on the treated tooth until permanent restoration. Numbness from local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue or cheek.

Some pressure sensation is normal as the anesthetic wears off. Take prescribed pain medication BEFORE numbness wears off for better pain control.

**First 24-48 Hours:**
Mild to moderate discomfort is completely normal and expected. The tooth may feel "different" or slightly elevated - this is temporary tissue inflammation.

Avoid hard, crunchy, or sticky foods on the treated side. Continue normal oral hygiene but be gentle around the treated area.

Sleep with your head slightly elevated to reduce any swelling.

**Pain Management:**
Take prescribed pain medication as directed - don't wait for pain to become severe. Over-the-counter options include Ibuprofen 600-800mg every 6 hours, which is highly effective for dental pain.

You can alternate ibuprofen with acetaminophen every 3 hours for severe pain. Apply cold compress for 20 minutes on/off during first 24 hours.

After 48 hours, warm compresses may be more beneficial.

**What to Expect:**
Days 1-3: Mild to moderate discomfort, sensitivity to biting pressure. Days 4-7: Gradual improvement, occasional tenderness when chewing.

Week 2: Most discomfort should be resolved. Week 3-4: Complete healing, ready for permanent restoration.

**Critical Follow-Up:**
You MUST return for permanent crown/filling within 2-4 weeks to prevent reinfection. The temporary filling is NOT permanent - your tooth will fail without proper restoration.

Root canal treated teeth are more brittle and require crown protection. Schedule your follow-up appointment immediately if not already done.

**Oral Hygiene:**
Continue normal brushing and flossing - root canal treated teeth still need care. Be gentle around temporary filling - avoid aggressive brushing of that area.

Use antimicrobial mouth rinse to maintain gum health. Maintain excellent oral hygiene to prevent reinfection.

**Diet Modifications:**
Avoid chewing on treated tooth until permanent restoration is placed. Soft foods are ideal during initial healing: pasta, cooked vegetables, soft proteins.

Avoid temperature extremes initially - lukewarm foods and beverages. Once permanent restoration is placed, normal diet can be resumed.

**Success Rate:**
Root canal therapy has an 85-95% success rate when properly completed. Success depends on getting permanent restoration placed promptly.

Most root canal treated teeth function normally for many years with proper care.

**Warning Signs - Call Immediately:**
Severe uncontrolled pain, significant facial swelling, fever over 101°F. Allergic reaction to medications or if the temporary filling falls out completely.
        """,

        "Scaling and Root Planing": """
**Deep Cleaning (Scaling and Root Planing) - Care Guide**

**What Was Done:**
Deep cleaning removed bacteria, plaque, and tartar from below the gum line and smoothed tooth root surfaces. This treatment helps gums reattach to teeth and reduces pocket depths from gum disease.

**Immediate Post-Treatment:**
Local anesthetic will wear off in 2-4 hours - be careful not to bite your tongue, cheek, or lips. Some sensitivity to temperature and pressure is normal for several days.

Your gums may feel tender and appear slightly swollen - this is normal healing response.

**First 24-48 Hours:**
Mild to moderate gum discomfort is completely normal and expected. Your gums are healing from the deep cleaning procedure.

Avoid very hot or cold foods/beverages as sensitivity is common initially. Stick to lukewarm or room temperature items for the first day.

Some light bleeding when brushing is normal for the first few days.

**Managing Sensitivity:**
Tooth sensitivity to cold, heat, or touch is common for 1-2 weeks after deep cleaning. Use toothpaste for sensitive teeth twice daily.

Avoid temperature extremes - lukewarm beverages and foods are best initially. If sensitivity is severe or persistent, contact our office.

**Oral Hygiene Protocol:**
Continue brushing twice daily with a soft-bristled toothbrush - clean teeth are essential for healing. Be extra gentle around treated areas for the first week.

Resume flossing within 24-48 hours - this is crucial for preventing reinfection. Start gently and gradually return to normal pressure.

Use prescribed antimicrobial mouth rinse as directed to reduce bacteria.

**Diet Guidelines:**
Avoid hard, crunchy, or sticky foods for the first few days that could irritate healing gums. Soft foods are ideal: pasta, cooked vegetables, soft proteins, dairy products.

Stay well-hydrated and maintain good nutrition to support gum healing. Avoid alcohol and tobacco which delay healing.

**What to Expect:**
Days 1-3: Mild discomfort, some sensitivity, possible light bleeding when cleaning. Days 4-7: Gradual improvement in comfort and sensitivity.

Weeks 2-4: Gums become pinker and firmer as healing progresses. You may notice less bleeding during brushing and flossing.

Months 1-3: Continued improvement in gum health with proper home care.

**Follow-Up Care:**
Return for periodontal maintenance cleaning in 3-4 months as recommended. This shorter interval ensures gum disease doesn't return.

Daily oral hygiene is critical - gum disease will return without excellent home care. Continue using prescribed mouth rinse as directed.

**Warning Signs:**
Contact our office for severe pain not relieved by over-the-counter medication. Excessive bleeding that doesn't improve after 3-4 days.

Signs of infection: fever, pus, severe swelling that worsens rather than improves.
        """,

        "Surgical Tooth Extraction": """
**Surgical Tooth Extraction - Recovery Guide**

**What Was Done:**
Your tooth was surgically removed, requiring gum incision and/or bone removal. This complex procedure allows access to teeth that cannot be removed with simple extraction techniques.

**Immediate Post-Surgery:**
Bite firmly on gauze pack for 1 hour, then assess bleeding. DO NOT disturb the surgical site with tongue, fingers, or toothpicks.

Take prescribed pain medication before anesthetic wears off. Begin ice therapy immediately: 20 minutes on, 10 minutes off.

**Critical First 24 Hours:**
ABSOLUTELY NO smoking, drinking through straws, or spitting - can cause dry socket. NO rinsing or swishing - gentle drinking is okay but no forceful mouth movements.

Keep head elevated when lying down to minimize bleeding and swelling. Apply ice packs continuously for first 6-8 hours while awake.

Soft, cool foods only: pudding, yogurt, smoothies, lukewarm soup.

**Managing Bleeding:**
Moderate bleeding is expected for 6-12 hours after surgical extraction. If active bleeding occurs: place clean gauze over site, bite firmly for 45 minutes.

Emergency bleeding control: bite on a moistened tea bag for 30 minutes. Avoid hot liquids, alcohol, and physical exertion which promote bleeding.

**Controlling Swelling:**
Significant swelling is normal after surgical extraction. Maximum swelling occurs at 48-72 hours - this is expected healing response.

Ice therapy is crucial: First 24 hours continuously while awake. After 48 hours: Switch to warm, moist compresses to promote healing.

Sleep with head elevated for first 2-3 nights.

**Pain Management:**
Surgical extractions typically cause more discomfort than simple extractions. Take prescribed pain medication as directed - stay ahead of pain.

Ibuprofen 600-800mg every 6 hours is excellent for surgical inflammation. You can alternate with prescribed narcotic for breakthrough pain.

Most pain peaks at 12-24 hours post-surgery, then gradually improves.

**Diet Progression:**
Day 1: Liquids and very soft foods only (protein shakes, pudding, lukewarm broth). Days 2-4: Soft foods that require minimal chewing (mashed potatoes, pasta, scrambled eggs).

Days 5-7: Gradual return to normal diet, avoiding surgical site when chewing. Avoid hard, crunchy, or sticky foods for at least two weeks.

**Oral Hygiene:**
Do NOT brush surgical site for first 48 hours. After 24 hours: Very gentle salt water rinses (½ tsp salt in 8oz warm water, 3-4 times daily).

Resume brushing other teeth normally, carefully avoiding surgical area. After 1 week: Very gentle cleaning near surgical site as comfort allows.

**Healing Timeline:**
Days 1-4: Peak discomfort and swelling, restricted diet, careful oral hygiene. Days 5-10: Significant improvement in pain and swelling.

Weeks 2-3: Soft tissue healing complete, comfortable chewing away from site. Weeks 4-8: Complete bone healing and socket filling.

**Dry Socket Prevention:**
Occurs in 2-5% of surgical extractions when blood clot is lost. Prevention: Follow ALL post-operative instructions carefully.

No smoking, spitting, straws, or vigorous rinsing for 72 hours minimum.

**Warning Signs:**
Call immediately for severe pain starting 2-4 days after extraction (possible dry socket). Heavy bleeding not controlled by pressure after 6 hours.

Signs of infection: fever, increasing pain after day 3, foul taste/smell. Excessive swelling, difficulty swallowing, or breathing problems.
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
    
    print(f"\n📊 Updated {updated_count} procedure overviews with comprehensive content")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(update_all_procedures())