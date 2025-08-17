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
    # Endodontics
    {
        "id": "root-canal-therapy",
        "name": "Root Canal Therapy", 
        "specialty": "endodontics",
        "specialtyName": "Endodontics",
        "duration": "7-14 days recovery",
        "overview": "Root canal therapy removes infected tissue from inside the tooth to save it.",
        "immediateAftercare": [
            "Apply ice pack to reduce swelling",
            "Take prescribed pain medication",
            "Avoid chewing on treated tooth",
            "Maintain gentle oral hygiene"
        ],
        "dietRestrictions": [
            "Avoid hard, crunchy foods for 24-48 hours", 
            "No extremely hot or cold foods/drinks",
            "Chew on opposite side of mouth",
            "Avoid sticky candies and gum"
        ],
        "warningSignsToCallDoctor": [
            "Severe pain that worsens after 2-3 days",
            "Swelling that increases after 48 hours",
            "Fever above 101°F (38.3°C)",
            "Temporary filling falls out"
        ],
        "recoveryTimeline": [
            {"day": "1-2", "activity": "Mild discomfort and sensitivity normal"},
            {"day": "3-5", "activity": "Pain should significantly decrease"},
            {"day": "7-10", "activity": "Most discomfort should resolve"},
            {"day": "14+", "activity": "Return for permanent restoration"}
        ],
        "medications": [
            "Ibuprofen 600mg every 6 hours for inflammation",
            "Acetaminophen as needed for pain relief", 
            "Antibiotics if prescribed"
        ]
    },
    # Prosthodontics  
    {
        "id": "dental-crown-placement",
        "name": "Dental Crown Placement",
        "specialty": "prosthodontics",
        "specialtyName": "Prosthodontics",
        "duration": "2-3 days sensitivity",
        "overview": "A dental crown is a tooth-shaped cap placed over a damaged tooth.",
        "immediateAftercare": [
            "Avoid chewing until numbness wears off",
            "Temporary crown may feel loose",
            "Brush and floss gently around crown",
            "Use warm salt water rinses"
        ],
        "dietRestrictions": [
            "Avoid sticky foods that could pull off crown",
            "No hard or crunchy foods on crown side",
            "Cut foods into smaller pieces",
            "Avoid chewing gum and hard candies"
        ],
        "warningSignsToCallDoctor": [
            "Temporary crown falls off completely",
            "Severe sensitivity that persists",
            "Crown feels too high when biting",
            "Gum swelling around crown"
        ],
        "recoveryTimeline": [
            {"day": "1-2", "activity": "Mild sensitivity and adjustment"},
            {"day": "3-7", "activity": "Comfort with temporary crown"},
            {"day": "14-21", "activity": "Permanent crown placement"},
            {"day": "21+", "activity": "Full function restored"}
        ],
        "medications": [
            "Over-the-counter pain relievers as needed",
            "Desensitizing toothpaste if recommended"
        ]
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