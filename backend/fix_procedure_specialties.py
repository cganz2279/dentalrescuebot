#!/usr/bin/env python3
"""
Fix procedure specialties - categorize procedures into correct specialties
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Specialty mapping based on procedure names
SPECIALTY_MAPPING = {
    # Oral Surgery procedures
    'oral-surgery': [
        'wisdom-tooth-removal', 'surgical-tooth-extraction', 'dental-implant-placement',
        'bone-grafting', 'bone-grafting-implant-site', 'bone-grafting-ridge-preservation',
        'sinus-lift-surgery', 'sinus-augmentation', 'sinus-lift-augmentation',
        'surgical-extraction-cysts-benign-lesions', 'maxillofacial-trauma-surgery',
        'surgical-orthodontics', 'cleft-lip-palate-repair', 'tori-removal',
        'surgical-removal-supernumerary-teeth', 'surgical-exposure-impacted-teeth',
        'apicoectomy', 'hemisection', 'hemisection-root-resection',
        'iv-sedation', 'alveoloplasty'
    ],
    
    # Periodontics procedures  
    'periodontics': [
        'scaling-and-root-planing', 'periodontal-maintenance', 'gingivectomy',
        'gingivectomy-gingivoplasty', 'gum-contouring-gingivoplasty',
        'crown-lengthening', 'crown-lengthening-with-bone-removal',
        'soft-tissue-graft', 'soft-tissue-grafting', 'free-gingival-graft',
        'connective-tissue-graft', 'guided-tissue-regeneration'
    ],
    
    # Endodontics procedures
    'endodontics': [
        'root-canal-therapy', 'vital-pulp-therapy', 'pulpotomy', 'pulpectomy'
    ],
    
    # Prosthodontics procedures
    'prosthodontics': [
        'dental-crown-placement', 'dental-bridge-placement', 'denture-delivery',
        'denture-reline', 'immediate-dentures', 'inlays-and-onlays',
        'full-mouth-rehabilitation'
    ],
    
    # Orthodontics procedures
    'orthodontics': [
        'tad-placement', 'surgical-orthodontics'
    ],
    
    # General Dentistry (keep some in general)
    'general-dentistry': [
        'amalgam-fillings', 'tooth-colored-fillings', 'dental-bonding',
        'dental-sealants', 'tooth-whitening', 'biopsy-of-oral-tissue',
        'biopsy-oral-soft-tissue', 'frenectomy', 'sleep-apnea-appliance',
        'tmj-therapy', 'tmj-surgery', 'tmj-arthrocentesis-arthroscopy',
        'socket-preservation', 'vestibuloplasty', 'vestibuloplasty-1',
        'vestibuloplasty-2', 'soft-denture-treatment-liner-care'
    ]
}

async def fix_specialties():
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'dentist_management')
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print("🔄 Starting specialty fixes...")
        
        # Create reverse mapping
        procedure_to_specialty = {}
        for specialty, procedures in SPECIALTY_MAPPING.items():
            for procedure_id in procedures:
                procedure_to_specialty[procedure_id] = specialty
        
        # Update each procedure
        updated_count = 0
        for procedure_id, new_specialty in procedure_to_specialty.items():
            result = await db.procedures.update_one(
                {"id": procedure_id},
                {"$set": {
                    "specialty": new_specialty,
                    "specialtyName": new_specialty.replace('-', ' ').title()
                }}
            )
            if result.matched_count > 0:
                print(f"✅ Updated {procedure_id} -> {new_specialty}")
                updated_count += 1
            else:
                print(f"⚠️ Not found: {procedure_id}")
        
        print(f"\n🎉 Updated {updated_count} procedures with correct specialties")
        
        # Show final distribution
        print("\n📊 Final specialty distribution:")
        specialties = {}
        async for proc in db.procedures.find():
            specialty = proc.get('specialty', 'unknown')
            specialties[specialty] = specialties.get(specialty, 0) + 1
        
        for specialty, count in sorted(specialties.items()):
            print(f"  {specialty}: {count} procedures")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_specialties())