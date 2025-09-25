#!/usr/bin/env python3
"""
Complete PDF Import: Import all 99 procedures from the uploaded zip file
This script will process all PDFs and import them with proper formatting and categorization.
"""

import os
import sys
import PyPDF2
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import re

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

def clean_procedure_name(filename):
    """Convert PDF filename to clean procedure name"""
    # Remove file extension
    name = filename.replace('.pdf', '')
    
    # Remove common prefixes
    name = re.sub(r'^Post_Op_', '', name)
    name = re.sub(r'^Post_Care_', '', name)
    name = re.sub(r'^Post-Operative\s*Instructions[_\s]*', '', name)
    
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    # Clean up duplicate numbers and parentheses
    name = re.sub(r'\s*\(\d+\)', '', name)  # Remove (1), (2), etc.
    name = re.sub(r'\s+', ' ', name)  # Multiple spaces to single space
    
    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name.strip()

def create_procedure_id(name):
    """Create URL-friendly ID from procedure name"""
    # Convert to lowercase and replace spaces with hyphens
    proc_id = name.lower()
    proc_id = re.sub(r'[^\w\s-]', '', proc_id)  # Remove special chars except hyphens
    proc_id = re.sub(r'\s+', '-', proc_id)  # Replace spaces with hyphens
    proc_id = re.sub(r'-+', '-', proc_id)  # Replace multiple hyphens with single
    proc_id = proc_id.strip('-')  # Remove leading/trailing hyphens
    return proc_id

def determine_specialty(procedure_name):
    """Determine specialty based on procedure name"""
    name_lower = procedure_name.lower()
    
    # Oral Surgery procedures
    oral_surgery_keywords = [
        'extraction', 'implant', 'surgery', 'surgical', 'bone grafting', 'sinus lift',
        'wisdom tooth', 'alveoloplasty', 'apicoectomy', 'hemisection', 'orthognathic',
        'trauma', 'tmd', 'tmj', 'oral cancer', 'biopsy', 'cleft', 'maxillofacial'
    ]
    
    # Periodontics procedures  
    periodontics_keywords = [
        'gingiv', 'periodontal', 'gum', 'tissue graft', 'connective tissue',
        'free gingival', 'guided tissue', 'osseous', 'flap surgery', 'scaling',
        'root planing', 'crown lengthening', 'frenectomy'
    ]
    
    # Endodontics procedures
    endodontics_keywords = [
        'root canal', 'pulpotomy', 'vital pulp', 'root amputation'
    ]
    
    # Orthodontics procedures
    orthodontics_keywords = [
        'braces', 'orthodontic', 'aligners', 'retention', 'tad placement',
        'surgical orthodontics', 'appliance'
    ]
    
    # Prosthodontics procedures
    prosthodontics_keywords = [
        'crown', 'bridge', 'denture', 'veneer', 'inlay', 'onlay',
        'prosthesis', 'rehabilitation', 'reline'
    ]
    
    # Restorative procedures
    restorative_keywords = [
        'filling', 'amalgam', 'bonding', 'tooth colored', 'sealant',
        'whitening', 'restoration'
    ]
    
    # Check specialties in order of specificity
    if any(keyword in name_lower for keyword in oral_surgery_keywords):
        return 'oral-surgery', 'Oral Surgery'
    elif any(keyword in name_lower for keyword in periodontics_keywords):
        return 'periodontics', 'Periodontics'  
    elif any(keyword in name_lower for keyword in endodontics_keywords):
        return 'endodontics', 'Endodontics'
    elif any(keyword in name_lower for keyword in orthodontics_keywords):
        return 'orthodontics', 'Orthodontics'
    elif any(keyword in name_lower for keyword in prosthodontics_keywords):
        return 'prosthodontics', 'Prosthodontics'
    elif any(keyword in name_lower for keyword in restorative_keywords):
        return 'restorative-dentistry', 'Restorative Dentistry'
    else:
        return 'general-dentistry', 'General Dentistry'

async def import_all_procedures():
    """Import all procedures from extracted PDFs directory"""
    print("🔄 Starting Complete PDF Import Process")
    print("=" * 70)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Clear existing procedures
    print("🧹 Clearing existing procedures...")
    await db.procedures.delete_many({})
    
    pdf_directory = '/app/extracted_pdfs'
    if not os.path.exists(pdf_directory):
        print(f"❌ PDF directory not found: {pdf_directory}")
        return
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf') and not f.startswith('._')]
    pdf_files.sort()
    
    print(f"📁 Found {len(pdf_files)} PDF files to import")
    print()
    
    procedures_imported = 0
    procedures_skipped = 0
    
    for i, pdf_filename in enumerate(pdf_files, 1):
        print(f"[{i:02d}/{len(pdf_files)}] Processing: {pdf_filename}")
        
        try:
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            
            # Extract PDF content
            pdf_content = extract_text_from_pdf(pdf_path)
            
            if not pdf_content or len(pdf_content) < 50:
                print(f"      ❌ No content extracted or content too short")
                procedures_skipped += 1
                continue
            
            # Create procedure info
            procedure_name = clean_procedure_name(pdf_filename)
            procedure_id = create_procedure_id(procedure_name)
            specialty_id, specialty_name = determine_specialty(procedure_name)
            
            print(f"      📝 Name: {procedure_name}")
            print(f"      🆔 ID: {procedure_id}")
            print(f"      🏥 Specialty: {specialty_name}")
            print(f"      📏 Content: {len(pdf_content)} characters")
            print(f"      📄 Preview: {pdf_content[:100].replace(chr(10), ' ')}...")
            
            # Create procedure document
            procedure_doc = {
                'id': procedure_id,
                'name': procedure_name,
                'overview': pdf_content,  # Full PDF content
                'specialty': specialty_id,
                'specialtyName': specialty_name,
                'duration': 'Variable',
                'createdAt': datetime.utcnow().isoformat() + 'Z',
                'updatedAt': datetime.utcnow().isoformat() + 'Z',
                'originalFilename': pdf_filename
            }
            
            # Check for duplicates
            existing = await db.procedures.find_one({'id': procedure_id})
            if existing:
                print(f"      ⚠️  Procedure with ID {procedure_id} already exists, updating...")
                await db.procedures.replace_one({'id': procedure_id}, procedure_doc)
            else:
                await db.procedures.insert_one(procedure_doc)
            
            procedures_imported += 1
            print(f"      ✅ Imported successfully")
            
        except Exception as e:
            print(f"      ❌ Error processing {pdf_filename}: {e}")
            procedures_skipped += 1
            continue
        
        print()  # Empty line for readability
    
    print("=" * 70)
    print("🎉 COMPLETE PDF IMPORT FINISHED!")
    print(f"📊 Total procedures imported: {procedures_imported}")
    print(f"⏭️  Procedures skipped: {procedures_skipped}")
    print(f"📚 Database now contains all your PDF procedures")
    
    # Show specialty breakdown
    print(f"\n📋 Specialty Distribution:")
    specialties = await db.procedures.distinct('specialtyName')
    for specialty in sorted(specialties):
        count = await db.procedures.count_documents({'specialtyName': specialty})
        print(f"   - {specialty}: {count} procedures")
    
    # Verification - show sample procedures
    print(f"\n🔍 Sample procedures:")
    sample_procedures = await db.procedures.find({}).limit(5).to_list(length=5)
    for proc in sample_procedures:
        print(f"   - {proc['name']} ({proc['specialtyName']})")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(import_all_procedures())