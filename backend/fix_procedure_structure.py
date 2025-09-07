#!/usr/bin/env python3
"""
Fix Procedure Database Structure for PDF Generation
The issue: Procedures have medical content in 'overview' field but PDF generation expects structured fields
Solution: Parse overview content and create structured medical content fields
"""

import asyncio
import os
import sys
import re
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/dental_app')

def parse_medical_content(overview_text):
    """
    Parse overview text and extract structured medical content
    """
    if not overview_text:
        return {}
    
    text = overview_text.lower()
    
    # Initialize structured content
    structured_content = {
        'immediateAftercare': [],
        'dietRestrictions': [],
        'warningSignsToCallDoctor': [],
        'recoveryTimeline': [],
        'medications': []
    }
    
    # Parse immediate aftercare instructions
    if 'ice' in text or 'apply cold' in text or 'cold compress' in text:
        structured_content['immediateAftercare'].append("Apply ice or cold compress to reduce swelling for 15-20 minutes at a time")
    
    if 'bite' in text and ('gauze' in text or 'cotton' in text):
        structured_content['immediateAftercare'].append("Bite gently on gauze pad for 30-45 minutes to control bleeding")
    
    if 'rest' in text or 'avoid strenuous' in text:
        structured_content['immediateAftercare'].append("Rest and avoid strenuous activities for the first 24-48 hours")
    
    if 'head elevated' in text or 'sleep with head raised' in text:
        structured_content['immediateAftercare'].append("Sleep with head elevated to minimize swelling")
    
    # Parse diet restrictions
    if 'soft food' in text or 'liquid diet' in text:
        structured_content['dietRestrictions'].append("Soft foods and liquids for the first 24-48 hours")
    
    if 'avoid hot' in text or 'no hot drinks' in text:
        structured_content['dietRestrictions'].append("Avoid hot foods and beverages initially")
    
    if 'no alcohol' in text or 'avoid alcohol' in text:
        structured_content['dietRestrictions'].append("Avoid alcohol while taking pain medications")
    
    if 'no smoking' in text or 'avoid smoking' in text:
        structured_content['dietRestrictions'].append("No smoking - this delays healing and increases infection risk")
    
    if 'chew on opposite side' in text or 'avoid chewing' in text:
        structured_content['dietRestrictions'].append("Avoid chewing on the treated area")
    
    # Parse warning signs
    if 'excessive bleeding' in text or 'severe bleeding' in text:
        structured_content['warningSignsToCallDoctor'].append("Excessive or persistent bleeding")
    
    if 'severe pain' in text or 'unbearable pain' in text:
        structured_content['warningSignsToCallDoctor'].append("Severe or worsening pain not controlled by medication")
    
    if 'swelling' in text and ('severe' in text or 'excessive' in text):
        structured_content['warningSignsToCallDoctor'].append("Severe or increasing swelling after 48 hours")
    
    if 'fever' in text or 'temperature' in text:
        structured_content['warningSignsToCallDoctor'].append("Fever over 101°F (38.3°C)")
    
    if 'infection' in text or 'pus' in text:
        structured_content['warningSignsToCallDoctor'].append("Signs of infection (pus, foul odor, severe swelling)")
    
    if 'difficulty swallowing' in text or 'trouble swallowing' in text:
        structured_content['warningSignsToCallDoctor'].append("Difficulty swallowing or breathing")
    
    # Parse recovery timeline
    if 'first 24 hours' in text or 'first day' in text:
        structured_content['recoveryTimeline'].append("First 24 hours: Most critical healing period, follow all instructions carefully")
    
    if '2-3 days' in text or '48-72 hours' in text:
        structured_content['recoveryTimeline'].append("2-3 days: Swelling and discomfort should begin to subside")
    
    if 'one week' in text or '7 days' in text or 'week' in text:
        structured_content['recoveryTimeline'].append("1 week: Significant improvement expected, follow-up appointment may be scheduled")
    
    if 'complete healing' in text or 'full recovery' in text:
        structured_content['recoveryTimeline'].append("2-4 weeks: Complete healing and full recovery expected")
    
    # Parse medications
    if 'ibuprofen' in text or 'advil' in text or 'motrin' in text:
        structured_content['medications'].append("Ibuprofen (Advil, Motrin): 400-600mg every 6-8 hours for pain and swelling")
    
    if 'acetaminophen' in text or 'tylenol' in text:
        structured_content['medications'].append("Acetaminophen (Tylenol): 650-1000mg every 6-8 hours for pain relief")
    
    if 'antibiotic' in text or 'prescription' in text:
        structured_content['medications'].append("Take prescribed antibiotics exactly as directed, complete full course")
    
    if 'pain medication' in text or 'prescribed pain' in text:
        structured_content['medications'].append("Take prescribed pain medication as needed, do not exceed recommended dosage")
    
    # Add generic content if specific content wasn't found
    if not any(structured_content.values()):
        # Root canal specific content
        if 'root canal' in text or 'endodontic' in text:
            structured_content['immediateAftercare'] = [
                "Bite gently on gauze pad for 30 minutes if bleeding occurs",
                "Apply ice pack for 15-20 minutes to reduce swelling",
                "Take prescribed medications as directed"
            ]
            structured_content['dietRestrictions'] = [
                "Avoid chewing on the treated tooth until permanent restoration is placed",
                "Soft foods recommended for the first 24 hours",
                "Avoid extremely hot or cold foods initially"
            ]
            structured_content['warningSignsToCallDoctor'] = [
                "Severe pain not controlled by medication",
                "Swelling that worsens after 48 hours",
                "Signs of infection (fever, pus, severe swelling)"
            ]
            structured_content['recoveryTimeline'] = [
                "First 24 hours: Some discomfort and sensitivity normal",
                "2-3 days: Significant improvement expected",
                "1 week: Follow-up appointment for permanent restoration"
            ]
            structured_content['medications'] = [
                "Take prescribed pain medication as needed",
                "Complete any prescribed antibiotic course",
                "Ibuprofen can help with swelling and discomfort"
            ]
        # Dental implant specific content
        elif 'implant' in text:
            structured_content['immediateAftercare'] = [
                "Bite on gauze pad for 45 minutes to control bleeding",
                "Apply ice pack intermittently for first 24 hours",
                "Rest and avoid strenuous activities for 48 hours"
            ]
            structured_content['dietRestrictions'] = [
                "Liquid or soft diet for first 24-48 hours",
                "No smoking - critical for implant success",
                "Avoid alcohol while taking pain medications",
                "No spitting or using straws for 24 hours"
            ]
            structured_content['warningSignsToCallDoctor'] = [
                "Excessive bleeding that doesn't stop with pressure",
                "Severe pain not controlled by medication",
                "Signs of infection or implant rejection"
            ]
            structured_content['recoveryTimeline'] = [
                "First week: Initial healing and tissue adaptation",
                "2-6 weeks: Soft tissue healing continues",
                "3-6 months: Osseointegration (bone bonding) occurs"
            ]
            structured_content['medications'] = [
                "Take prescribed antibiotics to prevent infection",
                "Pain medication as needed for discomfort",
                "Antimicrobial mouth rinse if prescribed"
            ]
        # Generic dental procedure content
        else:
            structured_content['immediateAftercare'] = [
                "Follow post-operative care instructions carefully",
                "Apply ice if swelling occurs",
                "Take medications as prescribed"
            ]
            structured_content['dietRestrictions'] = [
                "Soft foods recommended initially",
                "Avoid extremely hot or cold foods",
                "Stay hydrated with plenty of fluids"
            ]
            structured_content['warningSignsToCallDoctor'] = [
                "Severe or worsening pain",
                "Excessive swelling or bleeding",
                "Signs of infection"
            ]
            structured_content['recoveryTimeline'] = [
                "First 24-48 hours: Most critical healing period",
                "1 week: Significant improvement expected"
            ]
            structured_content['medications'] = [
                "Take prescribed medications as directed",
                "Over-the-counter pain relief as needed"
            ]
    
    return structured_content

async def fix_procedure_structure():
    """Fix all procedures to have proper structure for PDF generation"""
    print("🚀 FIXING PROCEDURE DATABASE STRUCTURE FOR PDF GENERATION")
    print("=" * 80)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.dental_app
    collection = db.procedures
    
    try:
        # Get all procedures
        procedures = await collection.find({}).to_list(length=None)
        print(f"📋 Found {len(procedures)} procedures to process")
        
        updated_count = 0
        
        for procedure in procedures:
            procedure_id = procedure.get('id')
            procedure_name = procedure.get('name', 'Unknown')
            overview = procedure.get('overview', '')
            
            print(f"\n🔧 Processing: {procedure_name} ({procedure_id})")
            
            # Check if procedure already has structured content
            has_structure = any(procedure.get(field) for field in [
                'immediateAftercare', 'dietRestrictions', 'warningSignsToCallDoctor', 
                'recoveryTimeline', 'medications'
            ])
            
            if has_structure:
                print(f"  ✅ Already has structured content, skipping")
                continue
            
            # Parse the overview to create structured content
            structured_content = parse_medical_content(overview)
            
            # Update the procedure with structured content
            update_data = {
                'immediateAftercare': structured_content['immediateAftercare'],
                'dietRestrictions': structured_content['dietRestrictions'],
                'warningSignsToCallDoctor': structured_content['warningSignsToCallDoctor'],
                'recoveryTimeline': structured_content['recoveryTimeline'],
                'medications': structured_content['medications'],
                'updatedAt': datetime.utcnow().isoformat()
            }
            
            result = await collection.update_one(
                {'id': procedure_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"  ✅ Updated with structured content:")
                for field, content in structured_content.items():
                    if content:
                        print(f"    {field}: {len(content)} items")
            else:
                print(f"  ❌ Failed to update")
        
        print(f"\n" + "=" * 80)
        print(f"📊 SUMMARY:")
        print(f"✅ Total procedures: {len(procedures)}")
        print(f"✅ Updated procedures: {updated_count}")
        print(f"✅ Procedures now have structured medical content for PDF generation")
        print("=" * 80)
        
        return updated_count > 0
        
    except Exception as e:
        print(f"❌ Error fixing procedure structure: {e}")
        return False
    
    finally:
        client.close()

async def main():
    success = await fix_procedure_structure()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)