import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Sample data extracted from PDFs (condensed for testing)
pdf_procedures = [
    {
        "id": "alveoloplasty",
        "name": "Alveoloplasty",
        "specialty": "oral-surgery", 
        "specialtyName": "Oral Surgery",
        "duration": "7-14 days recovery",
        "overview": "Alveoloplasty is a surgical procedure to smooth and reshape the jawbone after tooth extraction.",
        "immediateAftercare": [
            "Apply ice pack to reduce swelling",
            "Take prescribed pain medication as directed",
            "Avoid disturbing the surgical site",
            "Follow soft diet instructions"
        ],
        "dietRestrictions": [
            "Soft foods only for first 48 hours",
            "No hot liquids for 24 hours", 
            "Avoid hard or crunchy foods",
            "No smoking or alcohol"
        ],
        "warningSignsToCallDoctor": [
            "Severe bleeding that won't stop",
            "Excessive swelling after 48 hours",
            "Signs of infection (fever, pus)",
            "Severe pain not controlled by medication"
        ],
        "recoveryTimeline": [
            {"day": "1-3", "activity": "Initial healing and swelling reduction"},
            {"day": "7-10", "activity": "Suture removal if placed"},
            {"day": "2-4 weeks", "activity": "Soft tissue healing"},
            {"day": "6-8 weeks", "activity": "Complete healing expected"}
        ],
        "medications": [
            "Prescription pain medication as directed",
            "Anti-inflammatory medication for swelling",
            "Antibiotics if prescribed"
        ]
    },
    {
        "id": "bone-grafting",
        "name": "Bone Grafting", 
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "3-6 months healing",
        "overview": "Bone grafting is a procedure to rebuild bone in areas where it has been lost.",
        "immediateAftercare": [
            "Apply ice packs for first 48 hours",
            "Take prescribed medications as directed", 
            "Avoid disturbing the graft site",
            "Use prescribed mouth rinse"
        ],
        "dietRestrictions": [
            "Soft foods only for first 2 weeks",
            "No hot foods/drinks for 48 hours",
            "Avoid hard or crunchy foods for 6 weeks", 
            "No smoking during healing period"
        ],
        "warningSignsToCallDoctor": [
            "Severe pain not controlled by medication",
            "Signs of infection (fever, excessive swelling)",
            "Graft material displacement",
            "Persistent bleeding beyond 24 hours"
        ],
        "recoveryTimeline": [
            {"day": "1-7", "activity": "Initial healing phase"},
            {"day": "2-6 weeks", "activity": "Soft tissue integration"},
            {"day": "3-6 months", "activity": "Bone integration process"},
            {"day": "6+ months", "activity": "Ready for implant placement"}
        ],
        "medications": [
            "Prescription pain medication",
            "Anti-inflammatory medication", 
            "Antibiotics as prescribed"
        ]
    },
    {
        "id": "dental-implant-placement",
        "name": "Dental Implant Placement",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery", 
        "duration": "3-6 months healing",
        "overview": "Dental implant placement involves surgically inserting a titanium post into the jawbone.",
        "immediateAftercare": [
            "Apply ice packs for first 48 hours",
            "Take prescribed medications as directed",
            "Avoid disturbing the implant site", 
            "Use antiseptic mouth rinse"
        ],
        "dietRestrictions": [
            "Soft foods only for first 2 weeks",
            "No hot foods/drinks for 48 hours",
            "Avoid hard or crunchy foods for 6 weeks",
            "No smoking or alcohol during healing"
        ],
        "warningSignsToCallDoctor": [
            "Severe pain not controlled by medication",
            "Signs of infection (fever, excessive swelling)",
            "Implant feels loose or mobile",
            "Persistent bleeding beyond 24 hours"
        ],
        "recoveryTimeline": [
            {"day": "1-7", "activity": "Initial healing and swelling reduction"},
            {"day": "7-14", "activity": "Soft tissue healing"},
            {"day": "14-90", "activity": "Osseointegration process begins"},
            {"day": "90-180", "activity": "Complete integration and crown placement"}
        ],
        "medications": [
            "Prescription pain medication",
            "Anti-inflammatory medication",
            "Antibiotics as prescribed"
        ]
    }
]

# Add many more procedures from different specialties
additional_procedures = [
    # More Oral Surgery procedures
    {
        "id": "wisdom-tooth-removal",
        "name": "Wisdom Tooth Removal",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "7-10 days recovery",
        "overview": "Wisdom teeth removal is the surgical extraction of third molars.",
        "immediateAftercare": ["Bite on gauze for 45-60 minutes", "Apply ice packs for first 24 hours", "Keep head elevated", "Take medications as prescribed"],
        "dietRestrictions": ["Liquids only for first 24 hours", "No hot liquids for 48 hours", "Soft foods only for first week", "No straws for 1 week"],
        "warningSignsToCallDoctor": ["Excessive bleeding", "Severe pain increasing after day 3", "Dry socket symptoms", "Fever above 101°F"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Peak swelling and discomfort"}, {"day": "4-7", "activity": "Gradual improvement"}, {"day": "7-10", "activity": "Most swelling resolved"}, {"day": "14-21", "activity": "Complete healing"}],
        "medications": ["Prescription pain medication", "Anti-inflammatory medication", "Antibiotics if prescribed"]
    },
    {
        "id": "tooth-extraction",
        "name": "Tooth Extraction", 
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "3-7 days recovery",
        "overview": "Tooth extraction is the removal of a tooth from its socket.",
        "immediateAftercare": ["Bite on gauze for 30-45 minutes", "Apply ice pack to reduce swelling", "Take pain medication before numbness wears off", "Rest with head elevated"],
        "dietRestrictions": ["No solid foods for first 24 hours", "Avoid hot liquids for 24 hours", "No straws for 1 week", "No alcohol or smoking for 72 hours"],
        "warningSignsToCallDoctor": ["Heavy bleeding that won't stop", "Severe pain worsening after day 3", "Dry socket symptoms", "Signs of infection"],
        "recoveryTimeline": [{"day": "1", "activity": "Blood clot forms"}, {"day": "2-3", "activity": "Swelling peaks then decreases"}, {"day": "7", "activity": "Stitches removed if placed"}, {"day": "14-21", "activity": "Complete healing"}],
        "medications": ["Ibuprofen for pain and swelling", "Prescription pain medication if provided", "Antibiotics only if prescribed"]
    },
    {
        "id": "sinus-lift-surgery",
        "name": "Sinus Lift Surgery",
        "specialty": "oral-surgery", 
        "specialtyName": "Oral Surgery",
        "duration": "7-14 days recovery",
        "overview": "Sinus lift surgery adds bone to the upper jaw in the area of molars and premolars.",
        "immediateAftercare": ["Apply ice packs for first 48 hours", "Take prescribed medications", "Avoid blowing nose for 2 weeks", "Use nasal spray as directed"],
        "dietRestrictions": ["Soft foods only for first week", "No hot liquids for 48 hours", "Avoid spicy foods", "No smoking during healing"],
        "warningSignsToCallDoctor": ["Severe sinus pressure or pain", "Heavy nasal bleeding", "Signs of sinus infection", "Graft material in nasal cavity"],
        "recoveryTimeline": [{"day": "1-7", "activity": "Initial healing phase"}, {"day": "7-14", "activity": "Sinus membrane healing"}, {"day": "14-30", "activity": "Soft tissue integration"}, {"day": "3-6 months", "activity": "Bone maturation for implants"}],
        "medications": ["Prescription pain medication", "Antibiotics", "Nasal decongestant spray", "Anti-inflammatory medication"]
    },
    {
        "id": "frenectomy",
        "name": "Frenectomy",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery", 
        "duration": "7-10 days recovery",
        "overview": "Frenectomy is the surgical removal of a frenulum that may be causing problems.",
        "immediateAftercare": ["Apply ice to reduce swelling", "Take prescribed medications", "Gentle oral hygiene", "Use prescribed mouth rinse"],
        "dietRestrictions": ["Soft foods for first few days", "Avoid spicy or acidic foods", "No hot liquids initially", "Avoid hard or crunchy foods"],
        "warningSignsToCallDoctor": ["Excessive bleeding", "Signs of infection", "Severe pain not controlled by medication", "Unusual swelling"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Initial healing and discomfort"}, {"day": "3-7", "activity": "Tissue regeneration begins"}, {"day": "7-10", "activity": "Most healing complete"}, {"day": "14+", "activity": "Complete tissue remodeling"}],
        "medications": ["Over-the-counter pain relievers", "Antibiotics if prescribed", "Antiseptic mouth rinse"]
    },
    {
        "id": "tori-removal", 
        "name": "Tori Removal",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "7-14 days recovery", 
        "overview": "Tori removal is the surgical removal of bony growths in the mouth.",
        "immediateAftercare": ["Apply ice packs to reduce swelling", "Take prescribed pain medication", "Avoid touching surgical sites", "Use prescribed mouth rinse"],
        "dietRestrictions": ["Soft diet for first week", "No hot foods or drinks for 24 hours", "Avoid sharp or crunchy foods", "No alcohol during healing"],
        "warningSignsToCallDoctor": ["Excessive bleeding", "Signs of infection (fever, pus)", "Severe pain not controlled by medication", "Numbness persisting beyond expected time"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Peak swelling and discomfort"}, {"day": "3-7", "activity": "Gradual improvement"}, {"day": "7-14", "activity": "Continued healing"}, {"day": "14+", "activity": "Complete healing expected"}],
        "medications": ["Prescription pain medication", "Anti-inflammatory medication", "Antibiotics if prescribed"]
    },
    
    # Endodontics procedures
    {
        "id": "apicoectomy",
        "name": "Apicoectomy", 
        "specialty": "endodontics",
        "specialtyName": "Endodontics",
        "duration": "10-14 days recovery",
        "overview": "Apicoectomy is a surgical procedure to remove the tip of a tooth's root.",
        "immediateAftercare": ["Apply ice pack for first 24 hours", "Take prescribed medications", "Avoid disturbing surgical site", "Use prescribed mouth rinse"],
        "dietRestrictions": ["Soft foods only for first 48 hours", "No hot liquids for 24 hours", "Avoid spicy or acidic foods", "No straws or smoking"],
        "warningSignsToCallDoctor": ["Severe bleeding that won't stop", "Intense pain not relieved by medication", "Signs of infection", "Numbness lasting more than 24 hours"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Peak swelling and discomfort"}, {"day": "4-7", "activity": "Gradual improvement"}, {"day": "7-10", "activity": "Sutures removed"}, {"day": "14+", "activity": "Complete healing"}],
        "medications": ["Prescription pain medication", "Anti-inflammatory medication", "Antibiotics if prescribed"]
    },
    {
        "id": "pulpotomy",
        "name": "Pulpotomy",
        "specialty": "endodontics",
        "specialtyName": "Endodontics",
        "duration": "2-3 days sensitivity",
        "overview": "Pulpotomy is the removal of diseased pulp tissue from the crown of the tooth.",
        "immediateAftercare": ["Avoid chewing on treated tooth", "Take prescribed medications", "Maintain gentle oral hygiene", "Use fluoride rinse if recommended"],
        "dietRestrictions": ["Avoid hard foods for 24 hours", "No extremely hot or cold foods", "Chew on opposite side", "Avoid sticky foods"],
        "warningSignsToCallDoctor": ["Severe pain that worsens", "Swelling of face or gums", "Fever", "Temporary filling falls out"],
        "recoveryTimeline": [{"day": "1-2", "activity": "Mild sensitivity normal"}, {"day": "2-3", "activity": "Sensitivity should decrease"}, {"day": "7-14", "activity": "Follow-up appointment"}, {"day": "14+", "activity": "Permanent restoration placement"}],
        "medications": ["Over-the-counter pain relievers", "Antibiotics if prescribed"]
    },
    
    # Prosthodontics procedures
    {
        "id": "dental-bridge-placement",
        "name": "Dental Bridge Placement",
        "specialty": "prosthodontics", 
        "specialtyName": "Prosthodontics",
        "duration": "3-5 days adjustment",
        "overview": "A dental bridge replaces missing teeth by connecting crowns to adjacent teeth.",
        "immediateAftercare": ["Avoid chewing until numbness subsides", "Clean around bridge carefully", "Use special floss or floss threaders", "Rinse with warm salt water"],
        "dietRestrictions": ["Avoid hard or sticky foods", "Cut food into small pieces", "Avoid extremely hot or cold foods initially", "No gum or hard candies"],
        "warningSignsToCallDoctor": ["Bridge feels loose or unstable", "Persistent pain or sensitivity", "Gum irritation or swelling", "Food consistently getting trapped"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Initial adjustment and sensitivity"}, {"day": "3-7", "activity": "Adaptation to bridge"}, {"day": "7-14", "activity": "Normal function restoration"}, {"day": "14+", "activity": "Full comfort and adaptation"}],
        "medications": ["Over-the-counter pain relievers", "Anti-inflammatory medication if recommended"]
    },
    {
        "id": "denture-delivery",
        "name": "Denture Delivery", 
        "specialty": "prosthodontics",
        "specialtyName": "Prosthodontics", 
        "duration": "2-4 weeks adjustment",
        "overview": "Denture delivery involves fitting and adjusting new dentures for optimal comfort.",
        "immediateAftercare": ["Wear dentures as directed", "Remove and clean daily", "Soak overnight in cleaning solution", "Massage gums gently"],
        "dietRestrictions": ["Start with soft foods", "Cut food into small pieces", "Avoid very hot foods initially", "Avoid hard, sticky, or chewy foods initially"],
        "warningSignsToCallDoctor": ["Severe sore spots", "Dentures become very loose", "Persistent pain or irritation", "Difficulty eating after adjustment period"],
        "recoveryTimeline": [{"day": "1-7", "activity": "Initial adjustment period"}, {"day": "7-14", "activity": "Gradual comfort improvement"}, {"day": "14-28", "activity": "Adaptation to normal function"}, {"day": "28+", "activity": "Regular follow-up appointments"}],
        "medications": ["Over-the-counter pain relievers", "Denture adhesive if recommended"]
    },
    
    # Periodontics procedures
    {
        "id": "scaling-root-planing",
        "name": "Scaling & Root Planing",
        "specialty": "periodontics",
        "specialtyName": "Periodontics", 
        "duration": "1-3 days sensitivity",
        "overview": "Scaling and root planing is a deep cleaning procedure to treat gum disease.",
        "immediateAftercare": ["Use prescribed mouth rinse", "Gentle brushing and flossing", "Apply ice if recommended", "Take prescribed medications"],
        "dietRestrictions": ["Avoid hard or crunchy foods for 24 hours", "No extremely hot or cold foods", "Soft diet recommended initially", "No smoking during healing"],
        "warningSignsToCallDoctor": ["Excessive bleeding after 24 hours", "Severe pain not controlled by medication", "Signs of infection", "Unusual swelling"],
        "recoveryTimeline": [{"day": "1", "activity": "Some sensitivity and minor bleeding normal"}, {"day": "2-3", "activity": "Sensitivity should decrease"}, {"day": "7-14", "activity": "Gum healing progresses"}, {"day": "30+", "activity": "Improved gum health"}],
        "medications": ["Over-the-counter pain relievers", "Antibiotics if prescribed", "Prescription mouth rinse"]
    },
    {
        "id": "gum-graft-surgery",
        "name": "Gum Graft Surgery",
        "specialty": "periodontics",
        "specialtyName": "Periodontics",
        "duration": "7-14 days recovery", 
        "overview": "Gum graft surgery covers exposed tooth roots with tissue grafts.",
        "immediateAftercare": ["Apply ice packs for first 24 hours", "Take prescribed medications", "Use prescribed mouth rinse", "Avoid touching graft area"],
        "dietRestrictions": ["Soft foods only for first week", "No hot foods or drinks for 48 hours", "Avoid spicy or acidic foods", "No alcohol during healing"],
        "warningSignsToCallDoctor": ["Excessive bleeding", "Graft appears to be separating", "Signs of infection", "Severe pain not controlled by medication"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Initial healing phase"}, {"day": "3-7", "activity": "Graft integration begins"}, {"day": "7-14", "activity": "Suture removal"}, {"day": "30+", "activity": "Complete graft maturation"}],
        "medications": ["Prescription pain medication", "Antibiotics", "Prescription mouth rinse", "Anti-inflammatory medication"]
    },
    
    # General Dentistry procedures
    {
        "id": "amalgam-fillings",
        "name": "Amalgam Fillings",
        "specialty": "general-dentistry",
        "specialtyName": "General Dentistry",
        "duration": "24-48 hours sensitivity",
        "overview": "Amalgam fillings are silver-colored restorations used to repair cavities.",
        "immediateAftercare": ["Avoid chewing for 2 hours", "Take pain medication if needed", "Maintain good oral hygiene", "Use fluoride rinse if recommended"],
        "dietRestrictions": ["Avoid hard foods for 24 hours", "No extremely hot or cold foods initially", "Chew on opposite side if possible", "Avoid sticky candies"],
        "warningSignsToCallDoctor": ["Severe pain that worsens", "Filling feels too high when biting", "Persistent sensitivity after a week", "Filling falls out"],
        "recoveryTimeline": [{"day": "1", "activity": "Some sensitivity normal"}, {"day": "2-3", "activity": "Sensitivity should decrease"}, {"day": "7", "activity": "Normal function expected"}, {"day": "14+", "activity": "Complete adaptation"}],
        "medications": ["Over-the-counter pain relievers as needed"]
    },
    {
        "id": "tooth-colored-fillings", 
        "name": "Tooth Colored Fillings",
        "specialty": "general-dentistry",
        "specialtyName": "General Dentistry",
        "duration": "24-48 hours sensitivity",
        "overview": "Tooth-colored composite fillings restore teeth with natural-looking materials.",
        "immediateAftercare": ["Avoid chewing for 1 hour", "Take pain medication if needed", "Maintain gentle oral hygiene", "Avoid staining foods initially"],
        "dietRestrictions": ["Avoid hard foods for 24 hours", "No coffee, wine, or dark beverages for 48 hours", "Avoid extremely hot or cold foods", "No smoking for 48 hours"],
        "warningSignsToCallDoctor": ["Severe pain that increases", "Filling feels rough or high", "Persistent sensitivity beyond a week", "Filling chips or falls out"],
        "recoveryTimeline": [{"day": "1", "activity": "Mild sensitivity possible"}, {"day": "2-3", "activity": "Sensitivity should resolve"}, {"day": "7", "activity": "Normal chewing function"}, {"day": "14+", "activity": "Complete healing"}],
        "medications": ["Over-the-counter pain relievers if needed"]
    },
    
    # Orthodontics procedures
    {
        "id": "orthodontic-appliance-delivery",
        "name": "Orthodontic Appliance Delivery", 
        "specialty": "orthodontics",
        "specialtyName": "Orthodontics",
        "duration": "3-7 days adjustment",
        "overview": "Orthodontic appliance delivery involves placement and initial adjustment of braces or other appliances.",
        "immediateAftercare": ["Use orthodontic wax for comfort", "Take pain medication as needed", "Maintain careful oral hygiene", "Follow dietary restrictions"],
        "dietRestrictions": ["Soft foods for first few days", "Avoid hard, sticky, or chewy foods", "Cut foods into small pieces", "No gum or hard candies"],
        "warningSignsToCallDoctor": ["Severe pain not controlled by medication", "Broken brackets or wires", "Persistent sores or cuts", "Appliance becomes loose"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Initial discomfort and adjustment"}, {"day": "3-7", "activity": "Adaptation to appliance"}, {"day": "7-14", "activity": "Comfortable function"}, {"day": "14+", "activity": "Regular adjustment appointments"}],
        "medications": ["Over-the-counter pain relievers", "Topical oral pain gel if recommended"]
    },
    
    # Oral Medicine procedures
    {
        "id": "oral-biopsy",
        "name": "Oral Biopsy",
        "specialty": "oral-medicine", 
        "specialtyName": "Oral Medicine",
        "duration": "7-10 days recovery",
        "overview": "Oral biopsy involves removing a small sample of tissue for laboratory examination.",
        "immediateAftercare": ["Apply ice to reduce swelling", "Take prescribed medications", "Gentle oral hygiene", "Follow wound care instructions"],
        "dietRestrictions": ["Soft foods for first few days", "Avoid spicy or acidic foods", "No alcohol during healing", "Avoid very hot foods"],
        "warningSignsToCallDoctor": ["Excessive bleeding", "Signs of infection", "Severe pain not controlled by medication", "Unusual swelling"],
        "recoveryTimeline": [{"day": "1-3", "activity": "Initial healing phase"}, {"day": "3-7", "activity": "Tissue repair continues"}, {"day": "7-10", "activity": "Suture removal if placed"}, {"day": "14+", "activity": "Biopsy results available"}],
        "medications": ["Prescription pain medication", "Antibiotics if prescribed", "Antiseptic mouth rinse"]
    }
]

# Combine all procedures
all_procedures = pdf_procedures + additional_procedures

# Specialty definitions
specialties = [
    {
        "id": "oral-surgery",
        "name": "Oral Surgery",
        "description": "Tooth extractions, implants, and surgical procedures", 
        "icon": "Scissors",
        "color": "bg-red-50 border-red-200"
    },
    {
        "id": "endodontics", 
        "name": "Endodontics",
        "description": "Root canal treatments and related procedures",
        "icon": "Activity", 
        "color": "bg-blue-50 border-blue-200"
    },
    {
        "id": "prosthodontics",
        "name": "Prosthodontics", 
        "description": "Crowns, bridges, and denture procedures",
        "icon": "Crown",
        "color": "bg-purple-50 border-purple-200"
    },
    {
        "id": "periodontics",
        "name": "Periodontics",
        "description": "Gum treatments and periodontal surgery",
        "icon": "Heart",
        "color": "bg-green-50 border-green-200"
    },
    {
        "id": "general-dentistry", 
        "name": "General Dentistry",
        "description": "Fillings, cleanings, and routine procedures",
        "icon": "Shield",
        "color": "bg-orange-50 border-orange-200"
    },
    {
        "id": "orthodontics",
        "name": "Orthodontics", 
        "description": "Braces, aligners, and teeth straightening",
        "icon": "Zap",
        "color": "bg-teal-50 border-teal-200"
    },
    {
        "id": "oral-medicine",
        "name": "Oral Medicine",
        "description": "TMJ therapy, biopsies, and oral medicine",
        "icon": "Stethoscope", 
        "color": "bg-indigo-50 border-indigo-200"
    }
]

async def seed_database():
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Seeding database: {db_name}")
    
    # Clear existing data
    await db.procedures.delete_many({})
    await db.specialties.delete_many({})
    
    # Insert specialties
    await db.specialties.insert_many(specialties)
    print(f"Inserted {len(specialties)} specialties")
    
    # Insert procedures  
    await db.procedures.insert_many(all_procedures)
    print(f"Inserted {len(all_procedures)} procedures")
    
    # Verify counts
    specialty_count = await db.specialties.count_documents({})
    procedure_count = await db.procedures.count_documents({})
    oral_surgery_count = await db.procedures.count_documents({"specialty": "oral-surgery"})
    
    print(f"\n📊 Database seeded successfully!")
    print(f"Specialties: {specialty_count}")
    print(f"Total procedures: {procedure_count}")
    print(f"Oral Surgery procedures: {oral_surgery_count}")

if __name__ == "__main__":
    asyncio.run(seed_database())