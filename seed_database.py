#!/usr/bin/env python3
"""
Database seeding script for Dental Post-Operative Care App
Populates MongoDB with specialties and procedures data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path('backend')
load_dotenv(ROOT_DIR / '.env')

specialties_data = [
    {
        "id": "endodontics",
        "name": "Endodontics",
        "description": "Root canal treatments and related procedures",
        "icon": "Activity",
        "color": "bg-blue-50 border-blue-200"
    },
    {
        "id": "oral-surgery",
        "name": "Oral Surgery",
        "description": "Tooth extractions, implants, and surgical procedures",
        "icon": "Scissors",
        "color": "bg-red-50 border-red-200"
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
        "id": "pedodontics",
        "name": "Pediatric Dentistry",
        "description": "Dental procedures for children",
        "icon": "Baby",
        "color": "bg-pink-50 border-pink-200"
    }
]

procedures_data = [
    {
        "id": "root-canal",
        "name": "Root Canal Treatment",
        "specialty": "endodontics",
        "specialtyName": "Endodontics",
        "duration": "7-14 days recovery",
        "overview": "Root canal treatment removes infected or damaged tissue from inside your tooth to save it from extraction.",
        "immediateAftercare": [
            "Apply ice pack to reduce swelling (15 minutes on, 15 minutes off)",
            "Take prescribed pain medication as directed",
            "Avoid chewing on the treated tooth until permanent restoration",
            "Maintain gentle oral hygiene around the area"
        ],
        "dietRestrictions": [
            "Avoid hard, crunchy foods for 24-48 hours",
            "No extremely hot or cold foods/drinks",
            "Chew on the opposite side of your mouth",
            "Avoid sticky candies and gum"
        ],
        "warningSignsToCallDoctor": [
            "Severe pain that worsens after 2-3 days",
            "Swelling that increases after 48 hours",
            "Fever above 101°F (38.3°C)",
            "Temporary filling falls out",
            "Allergic reaction to medication"
        ],
        "recoveryTimeline": [
            {"day": "1-2", "activity": "Mild discomfort and sensitivity normal"},
            {"day": "3-5", "activity": "Pain should significantly decrease"},
            {"day": "7-10", "activity": "Most discomfort should resolve"},
            {"day": "14+", "activity": "Return for permanent restoration placement"}
        ],
        "medications": [
            "Ibuprofen 600mg every 6 hours for inflammation",
            "Acetaminophen as needed for additional pain relief",
            "Antibiotics if prescribed - complete full course"
        ]
    },
    {
        "id": "apicoectomy",
        "name": "Apicoectomy",
        "specialty": "endodontics",
        "specialtyName": "Endodontics",
        "duration": "10-14 days recovery",
        "overview": "An apicoectomy is a minor surgical procedure to remove the tip of a tooth's root and surrounding infected tissue.",
        "immediateAftercare": [
            "Apply ice pack for first 24 hours to reduce swelling",
            "Take prescribed medications as directed",
            "Avoid disturbing the surgical site",
            "Use prescribed mouth rinse as directed"
        ],
        "dietRestrictions": [
            "Soft foods only for first 48 hours",
            "No hot liquids for 24 hours",
            "Avoid spicy or acidic foods for one week",
            "No straws or smoking for 72 hours"
        ],
        "warningSignsToCallDoctor": [
            "Severe bleeding that won't stop",
            "Intense pain not relieved by medication",
            "Signs of infection (fever, pus)",
            "Numbness lasting more than 24 hours"
        ],
        "recoveryTimeline": [
            {"day": "1-3", "activity": "Peak swelling and discomfort"},
            {"day": "4-7", "activity": "Gradual improvement in symptoms"},
            {"day": "7-10", "activity": "Sutures removed if placed"},
            {"day": "14+", "activity": "Complete healing expected"}
        ],
        "medications": [
            "Prescription pain medication as directed",
            "Anti-inflammatory medication for swelling",
            "Antibiotics if prescribed"
        ]
    },
    {
        "id": "tooth-extraction",
        "name": "Tooth Extraction",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "3-7 days recovery",
        "overview": "Tooth extraction is the removal of a tooth from its socket in the jawbone.",
        "immediateAftercare": [
            "Bite on gauze pad for 30-45 minutes to control bleeding",
            "Apply ice pack to reduce swelling (20 minutes on, 20 minutes off)",
            "Take prescribed pain medication before numbness wears off",
            "Rest with head elevated on pillows"
        ],
        "dietRestrictions": [
            "No solid foods for first 24 hours - liquids and soft foods only",
            "Avoid hot liquids for 24 hours",
            "No drinking through straws for 1 week",
            "No alcohol or smoking for at least 72 hours",
            "Gradually return to normal diet as comfort allows"
        ],
        "warningSignsToCallDoctor": [
            "Heavy bleeding that won't stop after 2 hours",
            "Severe pain that worsens after day 3",
            "Dry socket symptoms (severe throbbing pain)",
            "Signs of infection (fever, pus, bad taste)",
            "Numbness lasting more than 24 hours"
        ],
        "recoveryTimeline": [
            {"day": "1", "activity": "Blood clot forms - avoid disturbing"},
            {"day": "2-3", "activity": "Swelling peaks then begins to decrease"},
            {"day": "7", "activity": "Stitches removed if placed"},
            {"day": "14-21", "activity": "Complete soft tissue healing"}
        ],
        "medications": [
            "Ibuprofen for pain and swelling reduction",
            "Prescription pain medication if provided",
            "Antibiotics only if prescribed"
        ]
    },
    {
        "id": "wisdom-teeth",
        "name": "Wisdom Teeth Removal",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "7-10 days recovery",
        "overview": "Wisdom teeth removal is the surgical extraction of one or more third molars (wisdom teeth).",
        "immediateAftercare": [
            "Bite on gauze for 45-60 minutes after surgery",
            "Apply ice packs for first 24 hours (20 min on, 20 min off)",
            "Keep head elevated when lying down",
            "Take medications as prescribed",
            "Get plenty of rest"
        ],
        "dietRestrictions": [
            "Liquids only for first 24 hours",
            "No hot liquids or foods for 48 hours",
            "Soft foods only for first week",
            "No straws, spitting, or smoking for 1 week",
            "Avoid small seeds and nuts for 2 weeks"
        ],
        "warningSignsToCallDoctor": [
            "Excessive bleeding that won't stop",
            "Severe pain increasing after day 3",
            "Dry socket (intense throbbing pain)",
            "Fever above 101°F for more than 24 hours",
            "Numbness or tingling lasting beyond first day"
        ],
        "recoveryTimeline": [
            {"day": "1-3", "activity": "Peak swelling and discomfort"},
            {"day": "4-7", "activity": "Gradual improvement in symptoms"},
            {"day": "7-10", "activity": "Most swelling resolved"},
            {"day": "14-21", "activity": "Complete soft tissue healing"}
        ],
        "medications": [
            "Prescription pain medication as directed",
            "Anti-inflammatory medication for swelling",
            "Antibiotics if prescribed - complete full course"
        ]
    },
    {
        "id": "dental-implant",
        "name": "Dental Implant Placement",
        "specialty": "oral-surgery",
        "specialtyName": "Oral Surgery",
        "duration": "3-6 months healing",
        "overview": "Dental implant placement involves surgically inserting a titanium post into the jawbone to replace a missing tooth root.",
        "immediateAftercare": [
            "Apply ice packs for first 48 hours",
            "Take prescribed medications as directed",
            "Avoid disturbing the implant site",
            "Use antiseptic mouth rinse as prescribed"
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
    },
    {
        "id": "dental-crown",
        "name": "Dental Crown",
        "specialty": "prosthodontics",
        "specialtyName": "Prosthodontics",
        "duration": "2-3 days sensitivity",
        "overview": "A dental crown is a tooth-shaped cap placed over a damaged tooth to restore its shape, size, and strength.",
        "immediateAftercare": [
            "Avoid chewing on the crown side until numbness wears off",
            "Temporary crown may feel loose - this is normal",
            "Brush and floss gently around the temporary crown",
            "Use warm salt water rinses to keep area clean"
        ],
        "dietRestrictions": [
            "Avoid sticky foods that could pull off temporary crown",
            "No hard or crunchy foods on the crown side",
            "Cut foods into smaller pieces",
            "Avoid chewing gum and hard candies"
        ],
        "warningSignsToCallDoctor": [
            "Temporary crown falls off completely",
            "Severe sensitivity to hot/cold that persists",
            "Crown feels too high when biting",
            "Gum swelling or bleeding around crown",
            "Persistent bad taste or odor"
        ],
        "recoveryTimeline": [
            {"day": "1-2", "activity": "Mild sensitivity and adjustment period"},
            {"day": "3-7", "activity": "Comfort with temporary crown"},
            {"day": "14-21", "activity": "Permanent crown placement appointment"},
            {"day": "21+", "activity": "Full function and comfort restored"}
        ],
        "medications": [
            "Over-the-counter pain relievers as needed",
            "Desensitizing toothpaste if recommended"
        ]
    },
    {
        "id": "dental-bridge",
        "name": "Dental Bridge",
        "specialty": "prosthodontics",
        "specialtyName": "Prosthodontics",
        "duration": "3-5 days adjustment",
        "overview": "A dental bridge is a fixed dental restoration used to replace one or more missing teeth by connecting crowns to adjacent teeth.",
        "immediateAftercare": [
            "Avoid chewing until numbness subsides",
            "Clean around temporary bridge carefully",
            "Use special floss or floss threaders for cleaning",
            "Rinse with warm salt water after meals"
        ],
        "dietRestrictions": [
            "Avoid hard or sticky foods",
            "Cut food into small pieces",
            "Avoid extremely hot or cold foods initially",
            "No gum or hard candies"
        ],
        "warningSignsToCallDoctor": [
            "Bridge feels loose or unstable",
            "Persistent pain or sensitivity",
            "Gum irritation or swelling",
            "Food consistently getting trapped"
        ],
        "recoveryTimeline": [
            {"day": "1-3", "activity": "Initial adjustment and sensitivity"},
            {"day": "3-7", "activity": "Adaptation to bridge placement"},
            {"day": "7-14", "activity": "Normal function restoration"},
            {"day": "14+", "activity": "Full comfort and adaptation"}
        ],
        "medications": [
            "Over-the-counter pain relievers as needed",
            "Anti-inflammatory medication if recommended"
        ]
    },
    {
        "id": "dentures",
        "name": "Complete/Partial Dentures",
        "specialty": "prosthodontics",
        "specialtyName": "Prosthodontics",
        "duration": "2-4 weeks adjustment",
        "overview": "Dentures are removable dental appliances that replace missing teeth and surrounding tissues.",
        "immediateAftercare": [
            "Wear dentures as directed by dentist",
            "Remove and clean dentures daily",
            "Soak dentures overnight in cleaning solution",
            "Massage gums gently with soft brush"
        ],
        "dietRestrictions": [
            "Start with soft foods and gradually progress",
            "Cut food into small pieces",
            "Avoid very hot foods initially",
            "Avoid hard, sticky, or chewy foods initially"
        ],
        "warningSignsToCallDoctor": [
            "Severe sore spots that don't improve",
            "Dentures become very loose",
            "Persistent pain or irritation",
            "Difficulty eating or speaking after adjustment period"
        ],
        "recoveryTimeline": [
            {"day": "1-7", "activity": "Initial adjustment and learning period"},
            {"day": "7-14", "activity": "Gradual comfort improvement"},
            {"day": "14-28", "activity": "Adaptation to normal function"},
            {"day": "28+", "activity": "Regular follow-up appointments"}
        ],
        "medications": [
            "Over-the-counter pain relievers as needed",
            "Denture adhesive if recommended"
        ]
    }
]

async def seed_database():
    """Seed the database with specialties and procedures data"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        print("Connected to MongoDB")
        
        # Clear existing data
        await db.specialties.delete_many({})
        await db.procedures.delete_many({})
        print("Cleared existing data")
        
        # Insert specialties
        await db.specialties.insert_many(specialties_data)
        print(f"Seeded {len(specialties_data)} specialties")
        
        # Insert procedures
        await db.procedures.insert_many(procedures_data)
        print(f"Seeded {len(procedures_data)} procedures")
        
        print("Database seeding complete!")
        
        # Verify the data
        specialties_count = await db.specialties.count_documents({})
        procedures_count = await db.procedures.count_documents({})
        print(f"Verification: {specialties_count} specialties, {procedures_count} procedures")
        
        client.close()
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database())