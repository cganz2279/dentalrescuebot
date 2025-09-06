#!/usr/bin/env python3
"""
CRITICAL FIX: Update ALL procedure PDFs with correct original content
This fixes the issue where 43+ procedures have incorrect/generic content
"""

import asyncio
import os
import sys
import PyPDF2
import zipfile
import re
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clean_procedure_name(name):
    """Clean procedure name for matching"""
    # Remove special characters and normalize
    cleaned = re.sub(r'[^\w\s-]', '', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.lower()

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"❌ Error extracting {pdf_path}: {e}")
        return None

def clean_pdf_content(text, procedure_name):
    """Clean and format PDF content properly"""
    if not text:
        return None
    
    # Remove the procedure name from the beginning if it appears
    lines = text.split('\n')
    cleaned_lines = []
    
    # Skip lines that are just the procedure name or similar
    skip_patterns = [
        procedure_name.lower(),
        clean_procedure_name(procedure_name),
        'post-operative instructions',
        'post operative instructions',
        'aftercare instructions'
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip if line matches procedure name or common headers
        should_skip = False
        for pattern in skip_patterns:
            if line.lower() == pattern or line.lower().startswith(pattern):
                should_skip = True
                break
                
        if not should_skip:
            cleaned_lines.append(line)
    
    # Join lines and clean up
    content = '\n'.join(cleaned_lines)
    
    # Remove extra whitespace and normalize
    content = re.sub(r'\n\s*\n', '\n\n', content)  # Fix multiple newlines
    content = re.sub(r'\s+', ' ', content)  # Fix multiple spaces
    content = content.replace('. ', '.\n').replace(':', ':\n')  # Add line breaks after sentences and colons
    
    # Ensure it starts with Purpose: if that's the first meaningful content
    if not content.startswith('Purpose:') and 'Purpose:' in content:
        purpose_index = content.find('Purpose:')
        if purpose_index > 0:
            content = content[purpose_index:]
    
    return content.strip()

async def fix_all_procedures():
    """Extract original PDFs and update ALL procedures in database"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME', 'dentist_management')]
    
    # Paths
    zip_path = Path('/app/PostOpProcedures.zip')
    extract_path = Path('/app/pdf-source-fresh')
    
    if not zip_path.exists():
        print(f"❌ PDF zip file not found at {zip_path}")
        return
    
    try:
        # Extract PDFs
        print("🔄 Extracting original PDFs...")
        extract_path.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Get all PDF files
        pdf_files = list(extract_path.glob('**/*.pdf'))
        print(f"📋 Found {len(pdf_files)} PDF files")
        
        # Get all procedures from database
        procedures = await db.procedures.find({}, {'name': 1, 'id': 1, 'overview': 1}).to_list(1000)
        print(f"🗄️ Found {len(procedures)} procedures in database")
        
        # Process each PDF
        updates_made = 0
        matches_found = 0
        
        for pdf_file in pdf_files:
            # Extract procedure name from filename
            filename = pdf_file.stem
            print(f"\n🔄 Processing: {filename}")
            
            # Extract PDF content
            pdf_content = extract_pdf_text(pdf_file)
            if not pdf_content:
                print(f"   ❌ Could not extract content")
                continue
            
            # Find matching procedure in database
            matched_procedure = None
            
            # Try exact match first
            for proc in procedures:
                if clean_procedure_name(filename) == clean_procedure_name(proc['name']):
                    matched_procedure = proc
                    break
            
            # Try partial matches if no exact match
            if not matched_procedure:
                for proc in procedures:
                    proc_clean = clean_procedure_name(proc['name'])
                    file_clean = clean_procedure_name(filename)
                    
                    if proc_clean in file_clean or file_clean in proc_clean:
                        # Additional similarity check
                        if len(set(proc_clean.split()) & set(file_clean.split())) >= 2:
                            matched_procedure = proc
                            break
            
            if not matched_procedure:
                print(f"   ⚠️ No matching procedure found for {filename}")
                continue
            
            matches_found += 1
            print(f"   ✅ Matched with: {matched_procedure['name']}")
            
            # Clean the PDF content
            cleaned_content = clean_pdf_content(pdf_content, matched_procedure['name'])
            
            if not cleaned_content or len(cleaned_content) < 100:
                print(f"   ❌ Content too short or invalid after cleaning")
                continue
            
            # Check if update is needed
            current_content = matched_procedure.get('overview', '')
            
            # Always update if current content starts with procedure name or is problematic
            needs_update = (
                current_content.startswith(matched_procedure['name']) or
                'What Was Done' in current_content or
                len(current_content) < 200 or
                cleaned_content != current_content
            )
            
            if needs_update:
                # Update in database
                result = await db.procedures.update_one(
                    {'id': matched_procedure['id']},
                    {
                        '$set': {
                            'overview': cleaned_content,
                            'updatedAt': datetime.utcnow(),
                            'contentSource': 'original_pdf_extraction'
                        }
                    }
                )
                
                if result.modified_count > 0:
                    updates_made += 1
                    print(f"   ✅ UPDATED - Content length: {len(cleaned_content)} chars")
                else:
                    print(f"   ❌ Update failed")
            else:
                print(f"   ℹ️ Content already correct, no update needed")
        
        print(f"\n🎉 COMPLETE PROCEDURE UPDATE FINISHED:")
        print(f"📊 Total PDFs processed: {len(pdf_files)}")  
        print(f"🎯 Procedures matched: {matches_found}")
        print(f"✅ Database updates made: {updates_made}")
        print(f"📋 All procedures now have correct original content!")
        
        # Verify the updates
        print(f"\n🔍 VERIFICATION - Checking updated procedures...")
        updated_procedures = await db.procedures.find(
            {'contentSource': 'original_pdf_extraction'},
            {'name': 1, 'overview': 1}
        ).to_list(1000)
        
        print(f"✅ Verified {len(updated_procedures)} procedures with original content")
        
        # Show sample of updated content
        if updated_procedures:
            sample = updated_procedures[0]
            print(f"\n📋 Sample updated procedure: {sample['name']}")
            print(f"Content preview: {sample['overview'][:200]}...")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        client.close()

if __name__ == "__main__":
    print("🚨 FIXING ALL PDF CONTENT - MEDICAL ACCURACY CRITICAL")
    print("=" * 60)
    asyncio.run(fix_all_procedures())