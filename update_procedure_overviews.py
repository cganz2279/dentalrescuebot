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

**Pain Management Strategy:**
• Take prescribed pain medication as directed - stay ahead of pain, don't wait until severe
• Ibuprofen is excellent for surgical swelling: 600-800mg every 6 hours with food
• Can combine with acetaminophen for breakthrough pain
• Avoid aspirin as it increases bleeding risk

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
        """,

        "Amalgam Fillings": """
**Silver Amalgam Fillings - Complete Post-Treatment Care**

**What Was Done:** Decayed or damaged tooth structure was removed and replaced with silver amalgam filling material. Amalgam is a durable metal alloy containing mercury, silver, tin, copper, and other metals that has been safely used in dentistry for over 150 years.

**Immediate Post-Treatment (First 4 Hours):**
• Local anesthetic will wear off in 2-4 hours - be very careful not to bite tongue, cheek, or lips
• Avoid chewing on the filled tooth until numbness completely wears off
• Your bite may feel "high" or different initially - this is normal and usually self-adjusts
• Some sensitivity to temperature and pressure is expected for several days

**First 24-48 Hours Critical Care:**
• NEW AMALGAM FILLINGS TAKE 24 HOURS TO FULLY HARDEN - avoid hard chewing during this period
• Stick to soft foods for the first day: pasta, cooked vegetables, soft bread, dairy products
• Avoid very hot or cold foods/beverages as sensitivity is common initially
• Gentle brushing and flossing is fine, but be careful around the new filling

**Managing Post-Filling Sensitivity:**
• Temperature sensitivity (hot/cold) is normal for 1-4 weeks after amalgam placement
• Bite sensitivity when chewing may occur for several days to weeks
• Use toothpaste for sensitive teeth (Sensodyne) if sensitivity persists
• Avoid temperature extremes - lukewarm beverages are best initially

**Bite Adjustment Protocol:**
• New fillings may feel "high" when you bite down - this is very common
• Most bite issues self-adjust within 1-2 weeks as you naturally wear the filling surface
• If significant bite discomfort persists beyond 1 week, contact office for adjustment
• Avoid excessive chewing or grinding on the new filling during adjustment period

**Oral Hygiene with New Fillings:**
• Resume normal brushing and flossing within 24 hours
• Amalgam fillings can be cleaned exactly like natural teeth
• Floss daily around the filling - proper oral hygiene prevents future decay
• Use fluoride toothpaste to strengthen tooth structure around the filling

**Long-Term Expectations:**
• Amalgam fillings typically last 10-15 years with proper care
• Initial metallic taste may occur but disappears within a few days
• Filling may darken slightly over time - this is normal aging of the material
• Regular dental checkups monitor filling integrity and surrounding tooth health

**Diet Recommendations:**
• After 24 hours: Resume normal diet gradually
• Avoid chewing ice, hard candy, or using teeth as tools
• Minimize sticky, sugary foods that promote decay around filling margins
• Balanced diet supports overall oral health and filling longevity

**Normal vs. Concerning Symptoms:**
*NORMAL:* Mild sensitivity, slight bite changes, temporary metallic taste, minor discomfort when chewing
*CALL OFFICE IF:* Severe pain not relieved by over-the-counter medication, sensitivity worsening after 2 weeks, feeling like filling is loose or high after 2 weeks, signs of allergic reaction (very rare)

**Amalgam Safety Information:**
• Amalgam fillings are considered safe by the FDA, ADA, and WHO
• Mercury in amalgam is bound in a stable alloy - not the same as liquid mercury
• Removal of sound amalgam fillings is not recommended unless problematic
• Pregnant women may choose alternative materials as a precaution

**Follow-Up Care:**
• No special follow-up appointment needed unless problems occur
• Regular 6-month dental checkups monitor filling condition
• Report any persistent sensitivity or bite problems promptly
• Maintain excellent oral hygiene to prevent decay around filling margins
        """,

        "Bone Grafting": """
**Bone Grafting Surgery - Comprehensive Recovery Protocol**

**What Was Done:** Bone grafting material was placed to augment insufficient bone volume for future dental implant placement or to preserve bone after tooth extraction. The graft material stimulates your body's natural bone regeneration process.

**Immediate Post-Surgery Care (First 4 Hours):**
• Bite firmly on gauze pack for 1 hour, then remove and assess bleeding
• DO NOT disturb the surgical site with tongue, fingers, or toothpicks
• Take prescribed pain medication before anesthetic wears off
• Begin ice therapy immediately: 20 minutes on, 10 minutes off

**Critical First 48 Hours:**
• ABSOLUTELY NO SMOKING - dramatically reduces graft success and delays healing
• NO spitting, rinsing vigorously, or using straws - can disrupt graft material
• Sleep with head elevated for first 2-3 nights to minimize swelling
• Soft, cool diet only: avoid hot foods and beverages for 48 hours
• Take prescribed antibiotics exactly as directed to prevent infection

**Graft Site Protection - CRITICAL:**
• The bone graft material must remain undisturbed for successful integration
• Avoid vigorous rinsing or spitting for at least 1 week
• Do not probe the area with tongue or instruments
• Small graft particles may be visible or felt - this is normal
• Some graft material may be lost during initial healing - expected and normal

**Bleeding Management:**
• Light bleeding/oozing for 24-48 hours is completely normal
• If persistent bleeding: bite on clean gauze for 45 minutes with continuous pressure
• Avoid hot liquids, alcohol, and physical exertion which increase bleeding
• Call if bleeding is heavy or doesn't respond to pressure

**Swelling Control Protocol:**
• Ice therapy: First 48 hours continuously (20 min on/10 min off while awake)
• Maximum swelling occurs at 48-72 hours - this is normal healing response
• After 48 hours: Switch to warm, moist heat to promote healing
• Gentle facial massage after day 3 can help reduce lingering swelling

**Pain Management Strategy:**
• Take prescribed pain medication as directed - don't wait for severe pain
• Ibuprofen 600-800mg every 6 hours is excellent for bone graft inflammation
• Can alternate with prescribed narcotic for breakthrough pain
• Most patients experience moderate pain for 3-5 days, then rapid improvement

**Nutrition During Healing:**
• Days 1-7: Soft foods only (yogurt, pudding, mashed potatoes, protein shakes)
• Weeks 2-3: Introduce slightly firmer foods, avoid chewing near graft site
• Weeks 4-8: Gradual return to normal diet, continue avoiding hard foods near graft
• Stay well-hydrated and maintain good nutrition to support bone formation

**Oral Hygiene Protocol:**
• Do NOT brush graft site for first week
• Rinse very gently with prescribed antimicrobial rinse or salt water (after 24 hours)
• Continue normal brushing and flossing of other teeth
• After 1 week: Very gentle cleaning around graft site with soft toothbrush

**Bone Integration Timeline:**
• Weeks 1-2: Initial soft tissue healing over graft site
• Weeks 3-6: Early bone formation begins within graft material
• Months 2-4: Active bone regeneration and graft integration
• Months 4-6: Mature bone formation ready for implant placement

**Follow-Up Schedule:**
• 1 week: Post-operative check, suture removal if needed
• 2 weeks: Healing assessment and oral hygiene instruction
• 6 weeks: Graft integration evaluation
• 4-6 months: Bone maturation assessment and implant planning

**Success Factors for Graft Integration:**
• Excellent oral hygiene throughout healing period
• No smoking or tobacco use (critically important)
• Compliance with all post-operative instructions
• Regular follow-up appointments as scheduled
• Healthy diet rich in calcium and vitamin D

**Warning Signs - Contact Office Immediately:**
• Severe pain not controlled by prescribed medication
• Signs of infection: fever, increasing pain after day 3, pus, persistent bad taste
• Excessive bleeding not controlled by pressure
• Complete loss of graft material from site
• Allergic reaction to medications
• Persistent numbness beyond expected timeframe

**Long-Term Expectations:**
• Successful bone grafts provide stable foundation for dental implants
• Some grafts may require additional augmentation before implant placement
• Regular dental visits monitor graft integration and overall oral health
• Maintain excellent oral hygiene to protect investment in bone grafting
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

**Osseointegration Phase (Healing Period):**
• 3-4 months for lower jaw, 4-6 months for upper jaw
• Implant must remain undisturbed during this critical period
• Temporary tooth replacement options will be discussed
• No pressure or chewing forces on implant during healing

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
        """,

        "Crown Preparation": """
**Dental Crown Preparation - Complete Care Guide**

**What Was Done:** Your tooth was carefully prepared by removing damaged structure and shaping it to receive a custom crown. A temporary crown was placed to protect the prepared tooth while your permanent crown is being fabricated.

**Temporary Crown Care - Critical Instructions:**
• Your temporary crown is held with temporary cement and requires special care
• Avoid sticky foods (gum, caramels, taffy) that can pull off the temporary crown
• Chew on the opposite side when possible
• If temporary crown comes off, save it and call immediately - tooth must be protected

**Managing Tooth Sensitivity:**
• Sensitivity to cold, heat, or pressure is common after crown preparation
• Use toothpaste for sensitive teeth twice daily
• Avoid temperature extremes - lukewarm beverages are best
• If sensitivity is severe, contact our office for desensitizing treatment

**Emergency Situations - Call Immediately:**
• Temporary crown falls off completely
• Severe pain not relieved by over-the-counter medication
• Significant gum swelling or signs of infection
• Temperature sensitivity that worsens rather than improves

**Long-Term Crown Care:**
• Brush and floss normally - crowns can still get cavities at the margins
• Regular dental checkups every 6 months
• Avoid using teeth as tools
• Consider a nightguard if you grind or clench your teeth
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