#!/usr/bin/env python3
"""
Missing Procedures Analysis - Extract and analyze procedures from ZIP files
"""

import zipfile
import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

def extract_procedure_names_from_zip(zip_path):
    """Extract procedure names from ZIP file"""
    procedures = []
    
    if not os.path.exists(zip_path):
        print(f"❌ ZIP file not found: {zip_path}")
        return procedures
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_list = z.namelist()
            
            for file_name in file_list:
                # Skip __MACOSX files and directories
                if '__MACOSX' in file_name or file_name.endswith('/'):
                    continue
                
                # Extract procedure name from filename
                # Remove path, extension, and common prefixes
                base_name = os.path.basename(file_name)
                name_without_ext = os.path.splitext(base_name)[0]
                
                # Remove common prefixes
                prefixes_to_remove = [
                    'Post_Op_', 'Post_Care_', 'Post_Treatment_',
                    'Pre_Op_', 'Pre_Care_', 'Pre_Treatment_'
                ]
                
                procedure_name = name_without_ext
                for prefix in prefixes_to_remove:
                    if procedure_name.startswith(prefix):
                        procedure_name = procedure_name[len(prefix):]
                        break
                
                # Convert underscores to spaces and clean up
                procedure_name = procedure_name.replace('_', ' ')
                procedure_name = re.sub(r'\s+', ' ', procedure_name).strip()
                
                # Skip empty names or very short names
                if len(procedure_name) > 2:
                    procedures.append({
                        'original_filename': file_name,
                        'extracted_name': procedure_name
                    })
    
    except Exception as e:
        print(f"❌ Error reading ZIP file {zip_path}: {str(e)}")
    
    return procedures

def get_database_procedures():
    """Get all procedures from database"""
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        
        procedures = list(db.procedures.find({}, {"name": 1, "id": 1, "_id": 0}))
        client.close()
        
        return procedures
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return []

def analyze_missing_procedures():
    """Analyze which procedures are missing from database"""
    print("🔍 MISSING PROCEDURES ANALYSIS")
    print("=" * 80)
    
    # ZIP files to analyze
    zip_files = [
        ('PostOpProcedures.zip', 'Original ZIP (used for database)'),
        ('post_op_instructions.zip', 'Updated ZIP (contains missing procedures)'),
        ('post_treatment_notes_3.zip', 'Latest ZIP (contains missing procedures)')
    ]
    
    all_zip_procedures = {}
    
    # Extract procedures from each ZIP
    for zip_file, description in zip_files:
        print(f"\n📦 ANALYZING {zip_file} - {description}")
        print("-" * 60)
        
        procedures = extract_procedure_names_from_zip(zip_file)
        all_zip_procedures[zip_file] = procedures
        
        print(f"📊 Found {len(procedures)} procedures in {zip_file}")
        
        # Look for target procedures
        target_procedures = ['All on X', 'All On X', 'Zirconia', 'Final']
        found_targets = []
        
        for proc in procedures:
            name = proc['extracted_name']
            for target in target_procedures:
                if target.lower() in name.lower():
                    found_targets.append(proc)
                    break
        
        if found_targets:
            print(f"🎯 TARGET PROCEDURES FOUND ({len(found_targets)}):")
            for proc in found_targets:
                print(f"   ✅ {proc['extracted_name']}")
                print(f"      Original file: {proc['original_filename']}")
        else:
            print(f"❌ No target procedures found in {zip_file}")
    
    # Get database procedures
    print(f"\n🗄️ DATABASE PROCEDURES")
    print("-" * 60)
    db_procedures = get_database_procedures()
    print(f"📊 Found {len(db_procedures)} procedures in database")
    
    db_names = {proc['name'].lower().strip() for proc in db_procedures}
    
    # Compare ZIP files to find missing procedures
    print(f"\n⚖️ COMPARISON ANALYSIS")
    print("=" * 80)
    
    # Compare newer ZIPs with database
    newer_zips = ['post_op_instructions.zip', 'post_treatment_notes_3.zip']
    
    for zip_file in newer_zips:
        if zip_file in all_zip_procedures:
            print(f"\n📊 MISSING FROM DATABASE (found in {zip_file}):")
            print("-" * 60)
            
            zip_procedures = all_zip_procedures[zip_file]
            missing_count = 0
            
            for proc in zip_procedures:
                zip_name = proc['extracted_name'].lower().strip()
                
                # Check if this procedure name exists in database
                found_in_db = False
                for db_name in db_names:
                    # Fuzzy matching - check if names are similar
                    if zip_name == db_name or zip_name in db_name or db_name in zip_name:
                        found_in_db = True
                        break
                
                if not found_in_db:
                    missing_count += 1
                    print(f"   ❌ MISSING: {proc['extracted_name']}")
                    print(f"      File: {proc['original_filename']}")
                    
                    # Check if this is one of our target procedures
                    target_terms = ['all on x', 'zirconia', 'final']
                    is_target = any(term in zip_name for term in target_terms)
                    if is_target:
                        print(f"      🎯 TARGET PROCEDURE!")
            
            print(f"\n📈 SUMMARY FOR {zip_file}:")
            print(f"   Total procedures in ZIP: {len(zip_procedures)}")
            print(f"   Missing from database: {missing_count}")
            print(f"   Expected database count if imported: {len(db_procedures) + missing_count}")
    
    # Specific target procedure analysis
    print(f"\n🎯 TARGET PROCEDURE DETAILED ANALYSIS")
    print("=" * 80)
    
    target_searches = [
        'All on X Post Op Instructions',
        'Final Zirconia Implant Prosthesis Post Op Instructions'
    ]
    
    for target in target_searches:
        print(f"\n🔍 SEARCHING FOR: {target}")
        print("-" * 40)
        
        found_in_zips = []
        
        for zip_file, procedures in all_zip_procedures.items():
            for proc in procedures:
                name = proc['extracted_name']
                # Check for partial matches
                if 'all on x' in name.lower() and 'post op' in name.lower():
                    found_in_zips.append((zip_file, proc))
                elif 'zirconia' in name.lower() and 'final' in name.lower():
                    found_in_zips.append((zip_file, proc))
        
        if found_in_zips:
            print(f"✅ FOUND IN ZIP FILES:")
            for zip_file, proc in found_in_zips:
                print(f"   📦 {zip_file}: {proc['extracted_name']}")
                print(f"      File: {proc['original_filename']}")
        else:
            print(f"❌ NOT FOUND in any ZIP files")
        
        # Check database
        found_in_db = False
        for db_proc in db_procedures:
            if target.lower() in db_proc['name'].lower():
                found_in_db = True
                print(f"✅ FOUND IN DATABASE: {db_proc['name']}")
                break
        
        if not found_in_db:
            print(f"❌ NOT FOUND in database")
    
    # Final summary
    print(f"\n📋 FINAL ANALYSIS SUMMARY")
    print("=" * 80)
    
    original_zip_count = len(all_zip_procedures.get('PostOpProcedures.zip', []))
    newer_zip_count = len(all_zip_procedures.get('post_op_instructions.zip', []))
    db_count = len(db_procedures)
    
    print(f"📊 Original ZIP (PostOpProcedures.zip): {original_zip_count} procedures")
    print(f"📊 Newer ZIP (post_op_instructions.zip): {newer_zip_count} procedures")
    print(f"📊 Database: {db_count} procedures")
    print(f"📊 Additional procedures in newer ZIP: {newer_zip_count - original_zip_count}")
    
    print(f"\n🎯 ROOT CAUSE ANALYSIS:")
    print(f"1. Database was populated from original ZIP with {original_zip_count} procedures")
    print(f"2. Newer ZIP files contain {newer_zip_count} procedures (additional {newer_zip_count - original_zip_count})")
    print(f"3. Missing procedures include target 'All On X' and 'Zirconia' procedures")
    print(f"4. Database needs to be updated with procedures from newer ZIP files")
    
    print(f"\n💡 RECOMMENDED SOLUTION:")
    print(f"1. Extract missing procedures from newer ZIP files")
    print(f"2. Add missing procedures to database")
    print(f"3. Update API to return all procedures (should be ~{newer_zip_count} total)")

if __name__ == "__main__":
    analyze_missing_procedures()