#!/usr/bin/env python3
"""
Import Only Missing PDFs - Add the 6 PDFs that are missing from the database
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
    
    # Clean up duplicate numbers and parentheses (keep them for duplicates)
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
    
    # Handle duplicates by adding a suffix
    if '(1)' in name:
        proc_id += '-1'
    elif '(2)' in name:
        proc_id += '-2'
    elif '2)' in name and 'zirconia' in name.lower():
        proc_id += '-2'
    
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
        'surgical orthodontics', 'appliance', 'retainer'
    ]
    
    # Prosthodontics procedures
    prosthodontics_keywords = [
        'crown', 'bridge', 'denture', 'veneer', 'inlay', 'onlay',
        'prosthesis', 'rehabilitation', 'reline', 'zirconia'
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

async def import_missing_procedures():
    """Import only the missing procedures"""
    print("🔄 Starting Missing PDFs Import Process")
    print("=" * 60)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # List of missing PDFs to import
    missing_pdfs = [
        'Final_Zirconia_Implant_Prosthesis_Post_Op_Instructions (2).pdf',
        'Post_Op_Pulpotomy (1).pdf', 
        'Post_Op_Scaling_and_Root_Planing (1).pdf',
        'Post_Op_Vestibuloplasty (1).pdf',
        'Post_Op_Vestibuloplasty (2).pdf',
        'Retainers_Instructions.pdf'
    ]
    
    pdf_directory = '/app/extracted_pdfs_new'
    
    print(f"📁 Missing PDFs to import: {len(missing_pdfs)}")
    print()
    
    procedures_imported = 0
    procedures_skipped = 0
    
    for i, pdf_filename in enumerate(missing_pdfs, 1):
        print(f"[{i:02d}/{len(missing_pdfs)}] Processing: {pdf_filename}")
        
        try:
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            
            if not os.path.exists(pdf_path):
                print(f"      ❌ File not found: {pdf_path}")
                procedures_skipped += 1
                continue
            
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
                print(f"      ⚠️  Procedure with ID {procedure_id} already exists, skipping...")
                procedures_skipped += 1
                continue
            else:
                await db.procedures.insert_one(procedure_doc)
            
            procedures_imported += 1
            print(f"      ✅ Imported successfully")
            
        except Exception as e:
            print(f"      ❌ Error processing {pdf_filename}: {e}")
            procedures_skipped += 1
            continue
        
        print()  # Empty line for readability
    
    print("=" * 60)
    print("🎉 MISSING PDFs IMPORT FINISHED!")
    print(f"📊 New procedures imported: {procedures_imported}")
    print(f"⏭️  Procedures skipped: {procedures_skipped}")
    
    # Verify final count
    total_count = await db.procedures.count_documents({})
    print(f"📚 Total procedures in database: {total_count}")
    
    if total_count >= 99:
        print("✅ SUCCESS: Database now contains 99+ procedures as expected!")
    else:
        print(f"⚠️  Note: Expected 99+ procedures, but found {total_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(import_missing_procedures())