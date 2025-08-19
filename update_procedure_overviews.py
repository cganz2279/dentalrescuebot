#!/usr/bin/env python3
"""
Update procedure overviews with comprehensive, thorough content
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def update_procedure_overviews():
    """Update all procedure overviews with comprehensive content"""
    
    # Connect to MongoDB directly
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]
    
    comprehensive_overviews = {
        "Root Canal Therapy": """
**Root Canal Therapy - Complete Post-Operative Guide**

**What Was Done:** Root canal therapy involves removing infected or inflamed pulp tissue from inside your tooth's root canals. The canals are then cleaned, disinfected, shaped, and sealed with a biocompatible material called gutta-percha. This procedure saves your natural tooth and eliminates infection.

**Immediate Post-Treatment (First 4 Hours):**
• Keep the temporary filling intact - avoid chewing on the treated tooth until permanent restoration
• Numbness from local anesthetic will wear off in 2-4 hours - be careful not to bite tongue/cheek
• Some pressure sensation is normal as the anesthetic wears off
• Take prescribed pain medication BEFORE numbness wears off for better pain control

**First 24-48 Hours - Critical Period:**
• Mild to moderate discomfort is completely normal and expected
• The tooth may feel "different" or slightly elevated - this is temporary tissue inflammation
• Avoid hard, crunchy, or sticky foods on the treated side
• Continue normal oral hygiene but be gentle around the treated area
• Sleep with head slightly elevated to reduce any swelling

**Pain Management Protocol:**
• Take prescribed pain medication as directed - don't wait for pain to become severe
• Over-the-counter options: Ibuprofen (Advil) 600-800mg every 6 hours is highly effective for dental pain
• Can alternate ibuprofen with acetaminophen (Tylenol) every 3 hours for severe pain
• Apply cold compress for 20 minutes on/off during first 24 hours
• After 48 hours, warm compresses may be more beneficial

**What to Expect - Timeline:**
• Days 1-3: Mild to moderate discomfort, sensitivity to biting pressure
• Days 4-7: Gradual improvement, occasional tenderness when chewing
• Week 2: Most discomfort should be resolved
• Week 3-4: Complete healing, ready for permanent restoration

**Critical Follow-Up Care:**
• MUST return for permanent crown/filling within 2-4 weeks to prevent reinfection
• Temporary filling is NOT permanent - tooth will fail without proper restoration
• Schedule follow-up appointment immediately if not already done

**Normal vs. Concerning Symptoms:**
*NORMAL:* Mild pain, sensitivity to pressure, slight swelling, temporary taste changes
*CALL IMMEDIATELY:* Severe uncontrolled pain, significant facial swelling, fever over 101°F, allergic reaction to medications, temporary filling falls out completely
        """,

        "Alveoloplasty": """
**Alveoloplasty (Jawbone Recontouring) - Complete Recovery Guide**

**What Was Done:** Alveoloplasty is a surgical procedure to reshape and smooth the jawbone, typically performed after tooth extractions to create an optimal foundation for dentures or to eliminate sharp bone edges that could cause discomfort.

**Immediate Post-Surgery (First 2 Hours):**
• Keep gauze pad in place with firm, consistent pressure for 45-60 minutes
• Replace gauze if soaked through - bleeding should gradually decrease
• Bite down firmly but avoid excessive chewing motions
• Avoid talking unnecessarily to prevent disrupting blood clot formation

**Critical First 24 Hours:**
• NO rinsing, spitting, or using straws - these actions can dislodge blood clots
• Keep head elevated when resting (use 2-3 pillows) to minimize swelling
• Apply ice packs: 20 minutes on, 20 minutes off for first 6-8 hours
• Stick to soft, cool foods: yogurt, pudding, smoothies, lukewarm soup
• Take prescribed antibiotics as directed to prevent infection

**Bleeding Management:**
• Light oozing for 24-48 hours is normal and expected
• If active bleeding occurs: bite on clean gauze for 45 minutes with steady pressure
• Emergency bleeding protocol: bite on a moistened tea bag for 30 minutes (tannins help clotting)
• Avoid hot liquids, alcohol, and smoking which promote bleeding

**Swelling Control Protocol:**
• Maximum swelling occurs 48-72 hours post-surgery - this is normal
• Ice therapy: First 48 hours only, then switch to warm compresses
• Warm salt water rinses after 24 hours: ½ tsp salt in 8oz warm water, 3-4 times daily
• Sleep elevated for first 3 nights to minimize facial swelling

**Nutrition and Diet Progression:**
• Days 1-3: Liquids and very soft foods only (protein shakes, smoothies, mashed potatoes)
• Days 4-7: Soft foods that require minimal chewing (pasta, soft fish, scrambled eggs)
• Week 2: Gradual return to normal diet, avoiding hard/crunchy foods near surgical site
• Stay well-hydrated - dehydration slows healing

**Pain Management Strategy:**
• Take prescribed pain medication as directed - stay ahead of pain, don't wait until severe
• Ibuprofen is excellent for surgical swelling: 600-800mg every 6 hours with food
• Can combine with acetaminophen for breakthrough pain
• Avoid aspirin as it increases bleeding risk

**Oral Hygiene Protocol:**
• No brushing surgical area for first 48 hours
• Gentle salt water rinses after 24 hours
• Resume normal brushing of other areas, avoiding surgical site
• After 1 week: gentle cleaning of surgical area with soft toothbrush

**Healing Timeline and Expectations:**
• Days 1-3: Peak discomfort and swelling, restricted diet
• Days 4-7: Significant improvement, gradual diet expansion
• Weeks 2-3: Soft tissue healing complete, comfortable chewing
• Weeks 4-8: Complete bone remodeling and final healing

**Warning Signs - Call Immediately:**
• Severe pain not controlled by prescribed medication
• Excessive bleeding not controlled by pressure
• Signs of infection: fever, increasing pain after day 3, foul taste/odor
• Numbness persisting beyond expected timeframe
• Unusual swelling or difficulty swallowing
        """,

        "Dental Implant Placement": """
**Dental Implant Surgery - Comprehensive Recovery Protocol**

**Procedure Overview:** A titanium implant was surgically placed into your jawbone to replace the root of a missing tooth. This implant will integrate with your bone over 3-6 months (osseointegration) before receiving the final crown restoration.

**Immediate Post-Surgery Care (First 4 Hours):**
• Bite firmly on gauze pack for 1 hour, then remove and assess bleeding
• Avoid disturbing the surgical site with tongue, fingers, or toothpicks
• Take prescribed pain medication before anesthetic wears off
• Begin ice therapy immediately: 20 minutes on, 10 minutes off

**Critical 48-Hour Period:**
• ABSOLUTELY NO SMOKING - dramatically increases failure risk and delays healing
• NO spitting, rinsing vigorously, or using straws - can disrupt blood clots
• Sleep with head elevated for first 2-3 nights
• Soft, cool diet only: avoid hot foods and beverages for 48 hours
• Take prescribed antibiotics exactly as directed to prevent infection

**Bleeding Management:**
• Light bleeding/oozing for 24-48 hours is completely normal
• If persistent bleeding: bite on clean gauze for 45 minutes with continuous pressure
• Avoid hot liquids, alcohol, and physical exertion which increase bleeding
• Call if bleeding is heavy or doesn't respond to pressure

**Swelling Control - Critical for Comfort:**
• Ice therapy: First 48 hours continuously (20 min on/10 min off while awake)
• Maximum swelling occurs at 48-72 hours - this is normal healing
• After 48 hours: Switch to warm, moist heat to promote healing
• Gentle facial massage after day 3 can help reduce lingering swelling

**Pain Management Protocol:**
• Take prescribed pain medication as directed - don't wait for severe pain
• Ibuprofen 600-800mg every 6 hours is excellent for implant surgery inflammation
• Can alternate with prescribed narcotic for breakthrough pain
• Most patients experience moderate pain for 3-5 days, then rapid improvement

**Nutrition During Healing:**
• Days 1-7: Soft foods only (yogurt, pudding, mashed potatoes, protein shakes)
• Weeks 2-3: Introduce slightly firmer foods, avoid chewing near implant site
• Weeks 4-8: Normal diet, but avoid very hard foods until final crown placed
• Stay well-hydrated and maintain good nutrition to support healing

**Oral Hygiene Protocol:**
• Do NOT brush implant site for first week
• Rinse gently with prescribed antimicrobial rinse or salt water (after 24 hours)
• Continue normal brushing and flossing of other teeth
• After 1 week: Very gentle cleaning around implant with soft toothbrush

**Osseointegration Phase (Healing Period):**
• 3-4 months for lower jaw, 4-6 months for upper jaw
• Implant must remain undisturbed during this critical period
• Temporary tooth replacement options will be discussed
• No pressure or chewing forces on implant during healing

**Follow-Up Schedule:**
• 1 week: Post-operative check, suture removal if needed
• 2 weeks: Healing assessment
• 6 weeks: Tissue healing evaluation
• 3-6 months: Integration check and impression for crown

**Success Factors:**
• Excellent oral hygiene throughout healing
• No smoking or tobacco use
• Compliance with all post-operative instructions
• Regular follow-up appointments
• Healthy diet and lifestyle

**Warning Signs - Contact Office Immediately:**
• Severe pain not controlled by prescribed medication
• Signs of infection: fever, increasing pain after day 3, pus, bad taste
• Implant feels loose or mobile
• Excessive bleeding not controlled by pressure
• Allergic reaction to medications
• Persistent numbness beyond expected timeframe

**Long-Term Care:**
• Once healed, implants require maintenance similar to natural teeth
• Regular dental cleanings and check-ups every 6 months
• Special flossing techniques around implant crown
• Avoid chewing ice, hard candy, or other very hard objects
        """,

        "Crown Preparation": """
**Dental Crown Preparation - Complete Care Guide**

**What Was Done:** Your tooth was carefully prepared by removing damaged structure and shaping it to receive a custom crown. A temporary crown was placed to protect the prepared tooth while your permanent crown is being fabricated in the dental laboratory.

**Temporary Crown Care - Critical Instructions:**
• Your temporary crown is held with temporary cement and requires special care
• Avoid sticky foods (gum, caramels, taffy) that can pull off the temporary crown
• Chew on the opposite side when possible
• If temporary crown comes off, save it and call immediately - tooth must be protected
• Clean gently around temporary crown - no aggressive flossing that could dislodge it

**Immediate Post-Preparation Care (First 4 Hours):**
• Local anesthetic will wear off in 2-4 hours - be careful not to bite tongue or cheek
• Some sensitivity to temperature and pressure is normal with the prepared tooth
• Take over-the-counter pain medication as needed for mild discomfort
• Avoid very hot or cold foods/drinks for the first 24 hours

**Managing Tooth Sensitivity:**
• Sensitivity to cold, heat, or pressure is common after crown preparation
• Use toothpaste for sensitive teeth (Sensodyne) twice daily
• Avoid temperature extremes - lukewarm beverages and foods are best
• If sensitivity is severe, contact our office for desensitizing treatment

**Oral Hygiene with Temporary Crown:**
• Brush normally but be gentle around the temporary crown
• When flossing near temporary crown: pull floss out sideways rather than lifting up
• Use antimicrobial mouth rinse to maintain gum health around preparation
• Maintain excellent oral hygiene to ensure healthy gums for crown placement

**Diet Modifications During Temporary Phase:**
• Avoid hard foods: nuts, ice, hard candy, crusty bread
• Avoid sticky foods: caramel, gum, dried fruit, sticky candy
• Cut food into smaller pieces and chew on the opposite side
• Soft foods are ideal: pasta, cooked vegetables, soft fish, dairy products

**Gum Health Maintenance:**
• Slight gum irritation around preparation site is normal
• Rinse with warm salt water (½ tsp salt in 8oz warm water) 2-3 times daily
• If gums become red, swollen, or bleed easily, call our office
• Healthy gums are essential for proper crown fit and longevity

**What to Expect Before Permanent Crown:**
• Mild sensitivity may persist throughout temporary crown period
• Temporary crown may feel different from your natural tooth - this is normal
• You may need 1-2 days to adjust to the temporary crown's shape and bite
• Some minor roughness or irregularities with temporary crown are expected

**Emergency Situations - Call Immediately:**
• Temporary crown falls off completely (save the crown, call ASAP)
• Severe pain not relieved by over-the-counter pain medication
• Significant gum swelling or signs of infection
• Temperature sensitivity that worsens rather than improves
• Bite feels severely off or uncomfortable

**Preparing for Permanent Crown Placement:**
• Schedule permanent crown appointment as recommended (typically 2-3 weeks)
• Continue excellent oral hygiene throughout temporary period
• Report any concerns about fit, comfort, or sensitivity at crown delivery
• Avoid delaying permanent crown placement - temporary crowns are not long-term solutions

**Permanent Crown Expectations:**
• May take a few days to fully adjust to permanent crown
• Initial mild sensitivity is normal and should resolve within 1-2 weeks
• Crown should feel comfortable and function like a natural tooth
• Proper care ensures crown longevity of 10-20+ years

**Long-Term Crown Care:**
• Brush and floss normally - crowns can still get cavities at the margins
• Regular dental checkups every 6 months to monitor crown and surrounding teeth
• Avoid using teeth as tools (opening packages, cracking nuts)
• Consider a nightguard if you grind or clench your teeth
        """,

        "Tooth Extraction (Simple)": """
**Simple Tooth Extraction - Complete Recovery Guide**

**What Was Done:** Your tooth was carefully removed using specialized instruments. The extraction site has been cleaned and may have received stitches to aid healing. A blood clot will form in the socket, which is essential for proper healing.

**Immediate Post-Extraction Care (First 2 Hours):**
• Bite firmly on gauze pad for 45-60 minutes to control bleeding
• Do NOT remove gauze frequently to "check" the site - this disrupts clot formation
• Replace gauze only if it becomes completely soaked with blood
• Avoid talking, spitting, or unnecessary mouth movements

**Critical First 24 Hours - Protecting the Blood Clot:**
• ABSOLUTELY NO smoking, drinking through straws, or spitting - can cause dry socket
• NO rinsing or swishing - gentle drinking is okay but no forceful mouth movements
• Keep head elevated when lying down to minimize bleeding and swelling
• Apply ice packs: 20 minutes on, 20 minutes off for first 6 hours
• Soft, cool foods only: pudding, yogurt, smoothies, lukewarm soup

**Bleeding Management Protocol:**
• Light oozing mixed with saliva for 24 hours is completely normal
• If active bleeding occurs: place clean gauze over site, bite firmly for 45 minutes
• Emergency bleeding control: bite on a moistened tea bag for 30 minutes
• Avoid hot liquids, alcohol, and physical exertion which promote bleeding

**Pain Control Strategy:**
• Take prescribed pain medication as directed, before anesthetic wears off
• Over-the-counter options: Ibuprofen 600-800mg every 6 hours (excellent for extraction pain)
• Can alternate ibuprofen with acetaminophen for breakthrough pain
• Most pain peaks at 6-12 hours post-extraction, then gradually improves

**Swelling Prevention and Management:**
• Ice therapy is crucial: First 24 hours, 20 minutes on/off while awake
• Maximum swelling occurs at 48-72 hours - this is normal healing response
• After 48 hours: Switch to warm, moist compresses to promote healing
• Sleep with head elevated for first 2-3 nights

**Diet Progression Guidelines:**
• Day 1: Liquids and very soft foods (protein shakes, pudding, lukewarm broth)
• Days 2-3: Soft foods that require minimal chewing (mashed potatoes, pasta, soft fish)
• Days 4-7: Gradual return to normal diet, avoiding extraction site when chewing
• Avoid hard, crunchy, or sticky foods for at least one week

**Oral Hygiene Protocol:**
• Do NOT brush extraction site for first 24 hours
• After 24 hours: Gentle salt water rinses (½ tsp salt in 8oz warm water, 3-4 times daily)
• Resume brushing other teeth normally, carefully avoiding extraction area
• After 1 week: Very gentle brushing near extraction site as comfort allows

**Normal Healing Timeline:**
• Days 1-3: Active healing, blood clot formation, peak discomfort
• Days 4-7: Significant improvement in pain and swelling
• Weeks 1-2: Soft tissue healing, gradual return to normal function
• Weeks 3-8: Complete bone healing and socket filling

**Dry Socket Prevention (Critical):**
• Occurs in 2-5% of extractions when blood clot is lost
• Prevention: Follow ALL post-operative instructions carefully
• No smoking, spitting, straws, or vigorous rinsing for 72 hours minimum
• Take prescribed antibiotics if given to prevent infection

**Warning Signs - Call Office Immediately:**
• Severe pain starting 2-4 days after extraction (possible dry socket)
• Heavy bleeding not controlled by pressure after 4-6 hours
• Signs of infection: fever, increasing pain after day 3, foul taste/smell
• Excessive swelling, difficulty swallowing, or breathing problems
• Numbness or tingling persisting beyond expected timeframe

**Follow-Up Care:**
• Suture removal appointment if stitches were placed (typically 7-10 days)
• Discuss tooth replacement options during healing period
• Consider bone grafting for future implant placement if recommended
• Regular dental checkups to monitor healing and adjacent teeth

**Long-Term Considerations:**
• Missing tooth may cause adjacent teeth to shift over time
• Consider replacement options: dental implant, bridge, or partial denture
• Maintain excellent oral hygiene to protect remaining teeth
• Regular dental visits become even more important after tooth loss
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
    asyncio.run(update_procedure_overviews())