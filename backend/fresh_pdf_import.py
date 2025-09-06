#!/usr/bin/env python3
"""
FRESH START: Import EXACT original content from PostOpProcedures.zip
This script will extract the user's original PDF content and import it exactly as provided.
"""

import zipfile
import PyPDF2
import io
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from PDF bytes - simple and direct"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def clean_procedure_name(filename):
    """Convert PDF filename to clean procedure name"""
    # Remove 'Post_Op_' prefix and '.pdf' suffix
    name = filename.replace('Post_Op_', '').replace('.pdf', '')
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    # Clean up any extra formatting
    name = name.replace('Post-Operative Instructions ', '')
    return name.strip()

def create_procedure_id(name):
    """Create URL-friendly ID from procedure name"""
    return name.lower().replace(' ', '-').replace('--', '-').replace('(', '').replace(')', '').replace('.', '')

async def fresh_import_original_content():
    """
    FRESH START: Import user's EXACT original content from ZIP file
    """
    print("🔄 FRESH IMPORT: Starting with user's original PostOpProcedures.zip")
    print("=" * 70)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'dentist_management')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"📊 Database: {db_name}")
    print(f"🔗 MongoDB: {mongo_url}")
    
    # COMPLETELY CLEAR existing data to start fresh
    print("\n🧹 Clearing existing procedures...")
    result = await db.procedures.delete_many({})
    print(f"   Deleted {result.deleted_count} existing procedures")
    
    # Process ZIP file
    zip_path = '/app/PostOpProcedures.zip'
    procedures_imported = 0
    
    print(f"\n📁 Processing ZIP file: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        # Get all PDF files (exclude __MACOSX files)
        pdf_files = [f for f in zip_file.namelist() 
                    if f.endswith('.pdf') and not f.startswith('__MACOSX')]
        
        print(f"📄 Found {len(pdf_files)} PDF files")
        print("\n🔄 Extracting original content:")
        
        for i, pdf_filename in enumerate(pdf_files, 1):
            try:
                print(f"\n   {i:2d}/{len(pdf_files)} Processing: {pdf_filename}")
                
                # Extract PDF content
                pdf_bytes = zip_file.read(pdf_filename)
                original_text = extract_text_from_pdf_bytes(pdf_bytes)
                
                if not original_text:
                    print(f"      ❌ No text extracted from {pdf_filename}")
                    continue
                
                # Create procedure info
                procedure_name = clean_procedure_name(pdf_filename)
                procedure_id = create_procedure_id(procedure_name)
                
                print(f"      📝 Name: {procedure_name}")
                print(f"      🆔 ID: {procedure_id}")
                print(f"      📏 Content: {len(original_text)} characters")
                print(f"      📄 Preview: {original_text[:100]}...")
                
                # Create procedure document with EXACT original content
                procedure_doc = {
                    'id': procedure_id,
                    'name': procedure_name,
                    'overview': original_text,  # USER'S EXACT ORIGINAL CONTENT
                    'specialty': 'general-dentistry',  # Default for now
                    'specialtyName': 'General Dentistry',
                    'duration': 'Variable',
                    'createdAt': '2024-01-01T00:00:00Z',
                    'updatedAt': '2024-01-01T00:00:00Z'
                }
                
                # Insert into database
                await db.procedures.insert_one(procedure_doc)
                procedures_imported += 1
                
                print(f"      ✅ Imported successfully")
                
            except Exception as e:
                print(f"      ❌ Error processing {pdf_filename}: {e}")
                continue
    
    print("\n" + "=" * 70)
    print(f"🎉 FRESH IMPORT COMPLETE!")
    print(f"📊 Total procedures imported: {procedures_imported}")
    print(f"📄 All content is EXACTLY from your original PDF files")
    print(f"✅ Database now contains your authentic professional content")
    
    # Verify a sample
    if procedures_imported > 0:
        print(f"\n🔍 Verification - Sample procedure:")
        sample = await db.procedures.find_one()
        if sample:
            print(f"   Name: {sample.get('name')}")
            print(f"   Content: {sample.get('overview', '')[:200]}...")

if __name__ == "__main__":
    asyncio.run(fresh_import_original_content())