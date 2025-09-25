#!/usr/bin/env python3
"""
Import Missing Procedures - Add the missing 'All On X' and 'Zirconia' procedures from newer ZIP files
"""

import os
import sys
import PyPDF2
import asyncio
import zipfile
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from PDF bytes"""
    try:
        import io
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF from bytes: {e}")
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
    
    # Remove duplicate suffixes like " (2)"
    name = re.sub(r'\s*\(\d+\)$', '', name)
    
    # Clean up duplicate numbers and parentheses
    name = re.sub(r'\s+', ' ', name)  # Multiple spaces to single space
    
    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name.strip()

def determine_specialty(procedure_name):
    """Determine specialty based on procedure name"""
    name_lower = procedure_name.lower()
    
    # Specific mappings for key procedures
    if 'all on x' in name_lower or 'all-on-x' in name_lower:
        return 'Prosthodontics'
    if 'zirconia' in name_lower:
        return 'Prosthodontics'
    if 'implant crown' in name_lower or 'implant prosthesis' in name_lower:
        return 'Prosthodontics'
    
    # General mappings
    if any(word in name_lower for word in ['crown', 'bridge', 'denture', 'prosthesis', 'restoration']):
        return 'Prosthodontics'
    if any(word in name_lower for word in ['extraction', 'surgery', 'biopsy', 'implant placement']):
        return 'Oral Surgery'
    if any(word in name_lower for word in ['root canal', 'endodontic']):
        return 'Endodontics'
    if any(word in name_lower for word in ['cleaning', 'scaling', 'periodontal', 'gum']):
        return 'Periodontics'
    if any(word in name_lower for word in ['braces', 'aligners', 'orthodontic']):
        return 'Orthodontics'
    if any(word in name_lower for word in ['oral medicine', 'diagnosis']):
        return 'Oral Medicine'
    
    return 'General Dentistry'

async def check_procedure_exists(db, procedure_name):
    """Check if a procedure with similar name already exists"""
    existing = await db.procedures.find_one({
        "name": {"$regex": f"^{re.escape(procedure_name)}$", "$options": "i"}
    })
    return existing is not None

async def import_procedures_from_zip(zip_path, target_procedures=None):
    """Import specific procedures from ZIP file"""
    
    if not os.path.exists(zip_path):
        print(f"❌ ZIP file not found: {zip_path}")
        return
    
    print(f"📦 Processing ZIP file: {zip_path}")
    
    # Connect to database
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    imported_count = 0
    skipped_count = 0
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            for filename in z.namelist():
                # Skip __MACOSX files and directories
                if '__MACOSX' in filename or filename.endswith('/'):
                    continue
                
                # Only process PDF files
                if not filename.lower().endswith('.pdf'):
                    continue
                
                procedure_name = clean_procedure_name(os.path.basename(filename))
                
                # If target procedures specified, only process those
                if target_procedures:
                    name_matches = False
                    for target in target_procedures:
                        if target.lower() in procedure_name.lower():
                            name_matches = True
                            break
                    if not name_matches:
                        continue
                
                print(f"\n🔍 Processing: {filename}")
                print(f"   Cleaned name: {procedure_name}")
                
                # Check if procedure already exists
                if await check_procedure_exists(db, procedure_name):
                    print(f"   ⏭️  Skipping - already exists in database")
                    skipped_count += 1
                    continue
                
                # Extract PDF content
                try:
                    pdf_bytes = z.read(filename)
                    pdf_text = extract_text_from_pdf_bytes(pdf_bytes)
                    
                    if not pdf_text or len(pdf_text) < 10:
                        print(f"   ❌ Skipping - no readable content")
                        continue
                    
                    # Determine specialty
                    specialty = determine_specialty(procedure_name)
                    
                    # Create procedure document
                    procedure_doc = {
                        "id": str(uuid.uuid4()),
                        "name": procedure_name,
                        "specialty": specialty,
                        "overview": pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text,
                        "duration": "Variable",
                        "instructions": pdf_text,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "source_file": filename
                    }
                    
                    # Insert into database
                    await db.procedures.insert_one(procedure_doc)
                    
                    print(f"   ✅ Added to database")
                    print(f"      Specialty: {specialty}")
                    print(f"      Content length: {len(pdf_text)} characters")
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error processing {filename}: {str(e)}")
                    continue
    
    except Exception as e:
        print(f"❌ Error reading ZIP file: {str(e)}")
    
    finally:
        client.close()
    
    print(f"\n📊 IMPORT SUMMARY:")
    print(f"   ✅ Imported: {imported_count} procedures")
    print(f"   ⏭️  Skipped: {skipped_count} procedures (already exist)")
    
    return imported_count

async def verify_target_procedures():
    """Verify that target procedures now exist in database"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    target_names = [
        "All On X Post Op Instructions",
        "Final Zirconia Implant Prosthesis Post Op Instructions"
    ]
    
    print(f"\n🎯 VERIFYING TARGET PROCEDURES:")
    
    for target in target_names:
        # Search for similar names
        cursor = db.procedures.find({
            "name": {"$regex": target.replace(" ", ".*"), "$options": "i"}
        })
        
        procedures = await cursor.to_list(length=None)
        
        if procedures:
            print(f"   ✅ Found: {procedures[0]['name']} (ID: {procedures[0]['id']})")
        else:
            print(f"   ❌ Not found: {target}")
    
    # Get total count
    total_count = await db.procedures.count_documents({})
    print(f"\n📊 Total procedures in database: {total_count}")
    
    client.close()

async def main():
    """Main function to import missing procedures"""
    print("🚀 IMPORTING MISSING PROCEDURES")
    print("=" * 80)
    
    # Define target procedures to look for
    target_keywords = ["all on x", "zirconia"]
    
    # Process newer ZIP files
    zip_files = [
        "/app/post_op_instructions.zip",
        "/app/post_treatment_notes_3.zip"
    ]
    
    total_imported = 0
    
    for zip_path in zip_files:
        if os.path.exists(zip_path):
            imported = await import_procedures_from_zip(zip_path, target_keywords)
            total_imported += imported
        else:
            print(f"❌ ZIP file not found: {zip_path}")
    
    print(f"\n🎉 TOTAL IMPORTED: {total_imported} procedures")
    
    # Verify target procedures
    await verify_target_procedures()
    
    print(f"\n✅ Import process completed!")

if __name__ == "__main__":
    asyncio.run(main())