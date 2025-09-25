#!/usr/bin/env python3
"""
Fix procedure categorization and restore missing procedures
"""

import os
import sys
import PyPDF2
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

async def fix_procedure_issues():
    """Fix categorization and restore missing procedures"""
    print("🔧 FIXING PROCEDURE ISSUES")
    print("=" * 50)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    fixes_applied = 0
    
    # 1. Fix "All On X" categorization
    print("1. Fixing 'All On X' categorization...")
    all_on_x = await db.procedures.find_one({'name': 'All On X Post Op Instructions'})
    if all_on_x and all_on_x.get('specialtyName') != 'Oral Surgery':
        await db.procedures.update_one(
            {'name': 'All On X Post Op Instructions'},
            {
                '$set': {
                    'specialty': 'oral-surgery',
                    'specialtyName': 'Oral Surgery',
                    'updatedAt': datetime.utcnow().isoformat() + 'Z'
                }
            }
        )
        print("   ✅ Moved 'All On X Post Op Instructions' to Oral Surgery")
        fixes_applied += 1
    else:
        print("   ℹ️  'All On X' already correctly categorized or not found")
    
    # 2. Check for missing Vestibuloplasty and restore if needed
    print("\n2. Checking for Vestibuloplasty...")
    vestibulo = await db.procedures.find_one({'name': {'$regex': 'vestibulo', '$options': 'i'}})
    
    if not vestibulo:
        print("   ⚠️  Vestibuloplasty missing, checking if we can restore from PDFs...")
        
        # Check if PDF exists in the extracted files
        vestibulo_files = []
        pdf_directory = '/app/extracted_pdfs_new'
        
        if os.path.exists(pdf_directory):
            for filename in os.listdir(pdf_directory):
                if 'vestibulo' in filename.lower() and filename.endswith('.pdf'):
                    vestibulo_files.append(filename)
        
        print(f"   Found {len(vestibulo_files)} Vestibuloplasty PDF files:")
        for file in vestibulo_files:
            print(f"     - {file}")
        
        # Restore the main Vestibuloplasty (not numbered duplicates)
        main_vestibulo = None
        for file in vestibulo_files:
            if '(1)' not in file and '(2)' not in file:
                main_vestibulo = file
                break
        
        if main_vestibulo:
            pdf_path = os.path.join(pdf_directory, main_vestibulo)
            pdf_content = extract_text_from_pdf(pdf_path)
            
            if pdf_content:
                procedure_doc = {
                    'id': 'vestibuloplasty',
                    'name': 'Vestibuloplasty',
                    'overview': pdf_content,
                    'specialty': 'oral-surgery',
                    'specialtyName': 'Oral Surgery',
                    'duration': 'Variable',
                    'createdAt': datetime.utcnow().isoformat() + 'Z',
                    'updatedAt': datetime.utcnow().isoformat() + 'Z',
                    'originalFilename': main_vestibulo
                }
                
                await db.procedures.insert_one(procedure_doc)
                print(f"   ✅ Restored 'Vestibuloplasty' from {main_vestibulo}")
                fixes_applied += 1
            else:
                print(f"   ❌ Could not extract content from {main_vestibulo}")
        else:
            print("   ❌ No main Vestibuloplasty file found")
    else:
        print(f"   ✅ Vestibuloplasty found: {vestibulo['name']}")
    
    # 3. Fix any other miscategorized procedures
    print("\n3. Checking for other miscategorized procedures...")
    
    # Common procedures that should be in Oral Surgery
    oral_surgery_procedures = [
        ('Final Zirconia Implant Prosthesis Post Op Instructions', 'oral-surgery', 'Oral Surgery'),
        ('Iv Sedation Post Op', 'oral-surgery', 'Oral Surgery')
    ]
    
    for proc_name, correct_specialty, correct_specialty_name in oral_surgery_procedures:
        proc = await db.procedures.find_one({'name': proc_name})
        if proc and proc.get('specialtyName') != correct_specialty_name:
            await db.procedures.update_one(
                {'name': proc_name},
                {
                    '$set': {
                        'specialty': correct_specialty,
                        'specialtyName': correct_specialty_name,
                        'updatedAt': datetime.utcnow().isoformat() + 'Z'
                    }
                }
            )
            print(f"   ✅ Fixed categorization: '{proc_name}' → {correct_specialty_name}")
            fixes_applied += 1
    
    # 4. Final verification
    print("\n4. Final verification...")
    
    # Check All On X
    all_on_x_final = await db.procedures.find_one({'name': 'All On X Post Op Instructions'})
    if all_on_x_final:
        print(f"   ✅ All On X: {all_on_x_final['name']} ({all_on_x_final['specialtyName']})")
    else:
        print("   ❌ All On X: Not found")
    
    # Check Vestibuloplasty
    vestibulo_final = await db.procedures.find_one({'name': {'$regex': 'vestibulo', '$options': 'i'}})
    if vestibulo_final:
        print(f"   ✅ Vestibuloplasty: {vestibulo_final['name']} ({vestibulo_final['specialtyName']})")
    else:
        print("   ❌ Vestibuloplasty: Still missing")
    
    # Show final specialty distribution
    print(f"\n📊 Final Specialty Distribution:")
    specialties = {}
    all_procedures = await db.procedures.find({}, {'specialtyName': 1, '_id': 0}).to_list(length=None)
    
    for proc in all_procedures:
        specialty = proc.get('specialtyName', 'Unknown')
        specialties[specialty] = specialties.get(specialty, 0) + 1
    
    for specialty, count in sorted(specialties.items()):
        print(f'   - {specialty}: {count} procedures')
    
    print(f"\n🎉 FIXES COMPLETED!")
    print(f"   Total fixes applied: {fixes_applied}")
    print(f"   Total procedures: {len(all_procedures)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_procedure_issues())