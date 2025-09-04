#!/usr/bin/env python3

import os
import re
import subprocess
from pymongo import MongoClient
from datetime import datetime
import uuid

# Database connection
client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext"""
    try:
        result = subprocess.run(['pdftotext', pdf_path, '-'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def parse_procedure_name(filename):
    """Extract procedure name from filename"""
    # Remove .pdf extension and Post_Op_ prefix
    name = filename.replace('.pdf', '').replace('Post_Op_', '').replace('Post-Operative Instructions_ ', '')
    # Replace underscores with spaces and title case
    name = name.replace('_', ' ').title()
    return name

def parse_pdf_content(text):
    """Parse PDF text content into structured data"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    procedure_data = {
        'overview': '',
        'immediateAftercare': [],
        'dietRestrictions': [],
        'warningSignsToCallDoctor': [],
        'recoveryTimeline': [],
        'medications': []
    }
    
    current_section = 'overview'
    
    # First line is usually the procedure name/purpose
    if lines:
        procedure_data['name'] = lines[0]
        if len(lines) > 1 and lines[1].startswith('Purpose:'):
            procedure_data['overview'] = lines[1].replace('Purpose:', '').strip()
    
    # Parse sections
    for line in lines[1:]:
        line_lower = line.lower()
        
        # Identify sections
        if any(keyword in line_lower for keyword in ['first 24 hours', 'immediate', 'initially', 'day 1']):
            current_section = 'immediateAftercare'
            continue
        elif any(keyword in line_lower for keyword in ['diet', 'eating', 'food', 'what to eat', 'avoid eating']):
            current_section = 'dietRestrictions'
            continue
        elif any(keyword in line_lower for keyword in ['pain', 'swelling', 'bleeding', 'soreness', 'discomfort']):
            current_section = 'immediateAftercare'
            continue
        elif any(keyword in line_lower for keyword in ['oral hygiene', 'brushing', 'cleaning', 'rinse', 'floss']):
            current_section = 'immediateAftercare'
            continue
        elif any(keyword in line_lower for keyword in ['activity', 'exercise', 'rest', 'work']):
            current_section = 'immediateAftercare'
            continue
        elif any(keyword in line_lower for keyword in ['follow-up', 'follow up', 'contact', 'call', 'emergency', 'when to call']):
            current_section = 'warningSignsToCallDoctor'
            continue
        elif any(keyword in line_lower for keyword in ['medication', 'medicine', 'prescription', 'pain relief', 'antibiotic']):
            current_section = 'medications'
            continue
        
        # Add content to appropriate section
        if line.startswith('- ') or line.startswith('• '):
            # Bullet point
            content = line[2:].strip()
            if current_section == 'immediateAftercare':
                procedure_data['immediateAftercare'].append(content)
            elif current_section == 'dietRestrictions':
                procedure_data['dietRestrictions'].append(content)
            elif current_section == 'warningSignsToCallDoctor':
                procedure_data['warningSignsToCallDoctor'].append(content)
            elif current_section == 'medications':
                procedure_data['medications'].append(content)
        elif line and not line.endswith(':'):
            # Regular content line
            if current_section == 'overview' and not procedure_data['overview']:
                procedure_data['overview'] = line
            elif current_section == 'immediateAftercare':
                procedure_data['immediateAftercare'].append(line)
            elif current_section == 'dietRestrictions':
                procedure_data['dietRestrictions'].append(line)
            elif current_section == 'warningSignsToCallDoctor':
                procedure_data['warningSignsToCallDoctor'].append(line)
            elif current_section == 'medications':
                procedure_data['medications'].append(line)
    
    return procedure_data

def create_specialty_mapping():
    """Create specialty mappings for procedures"""
    specialty_map = {
        'oral_surgery': [
            'extraction', 'implant', 'bone graft', 'sinus lift', 'apicoectomy', 
            'biopsy', 'surgical', 'cyst', 'lesion', 'alveoloplasty'
        ],
        'restorative': [
            'filling', 'crown', 'bridge', 'onlay', 'inlay', 'amalgam', 'composite'
        ],
        'periodontics': [
            'gum', 'scaling', 'root planing', 'periodontal', 'gingivectomy', 
            'crown lengthening', 'flap'
        ],
        'endodontics': [
            'root canal', 'endodontic', 'pulpotomy', 'apicoectomy'
        ],
        'prosthodontics': [
            'denture', 'partial', 'full denture', 'overdenture', 'liner'
        ],
        'orthodontics': [
            'braces', 'orthodontic', 'retainer', 'spacer'
        ],
        'pedodontics': [
            'pediatric', 'child', 'children', 'pulpotomy', 'space maintainer'
        ],
        'cosmetic': [
            'whitening', 'bleaching', 'veneer', 'bonding'
        ]
    }
    
    return specialty_map

def determine_specialty(procedure_name):
    """Determine specialty based on procedure name"""
    specialty_map = create_specialty_mapping()
    procedure_lower = procedure_name.lower()
    
    for specialty, keywords in specialty_map.items():
        if any(keyword in procedure_lower for keyword in keywords):
            return specialty
    
    return 'general_dentistry'  # Default

def process_all_pdfs():
    """Process all PDFs and update database"""
    pdf_files = [f for f in os.listdir('/app') if f.endswith('.pdf') and f.startswith('Post_Op')]
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Clear existing procedures
    db.procedures.delete_many({})
    print("Cleared existing procedures from database")
    
    procedures_added = 0
    
    for pdf_file in sorted(pdf_files):  # Alphabetical order
        print(f"Processing: {pdf_file}")
        
        # Extract text
        pdf_path = f"/app/{pdf_file}"
        text_content = extract_text_from_pdf(pdf_path)
        
        if not text_content:
            print(f"Failed to extract text from {pdf_file}")
            continue
        
        # Parse content
        procedure_data = parse_pdf_content(text_content)
        procedure_name = parse_procedure_name(pdf_file)
        specialty = determine_specialty(procedure_name)
        
        # Create procedure document
        procedure_doc = {
            'id': str(uuid.uuid4()),
            'name': procedure_name,
            'specialty': specialty,
            'description': procedure_data['overview'] or f"Post-operative care instructions for {procedure_name.lower()}",
            'overview': procedure_data['overview'] or text_content[:500] + "...",
            'immediateAftercare': procedure_data['immediateAftercare'],
            'dietRestrictions': procedure_data['dietRestrictions'],
            'warningSignsToCallDoctor': procedure_data['warningSignsToCallDoctor'],
            'recoveryTimeline': procedure_data['recoveryTimeline'],
            'medications': procedure_data['medications'],
            'estimatedRecoveryTime': '1-2 weeks',  # Default
            'difficulty': 'moderate',  # Default
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        # Insert into database
        try:
            db.procedures.insert_one(procedure_doc)
            procedures_added += 1
            print(f"✅ Added: {procedure_name} ({specialty})")
        except Exception as e:
            print(f"❌ Failed to add {procedure_name}: {e}")
    
    print(f"\n🎉 Successfully processed {procedures_added} procedures!")
    
    # Update specialties collection
    update_specialties()

def update_specialties():
    """Update specialties collection with categories"""
    specialties = [
        {
            'id': 'oral_surgery',
            'name': 'Oral Surgery',
            'description': 'Surgical procedures including extractions, implants, and bone grafts',
            'icon': '🦷',
            'color': 'bg-red-50 border-red-200'
        },
        {
            'id': 'restorative',
            'name': 'Restorative Dentistry',
            'description': 'Fillings, crowns, bridges, and other restorative procedures',
            'icon': '🔧',
            'color': 'bg-blue-50 border-blue-200'
        },
        {
            'id': 'periodontics',
            'name': 'Periodontics',
            'description': 'Gum disease treatment and periodontal procedures',
            'icon': '🌿',
            'color': 'bg-green-50 border-green-200'
        },
        {
            'id': 'endodontics',
            'name': 'Endodontics',
            'description': 'Root canal therapy and endodontic treatments',
            'icon': '🎯',
            'color': 'bg-purple-50 border-purple-200'
        },
        {
            'id': 'prosthodontics',
            'name': 'Prosthodontics',
            'description': 'Dentures, partials, and prosthetic replacements',
            'icon': '🦾',
            'color': 'bg-orange-50 border-orange-200'
        },
        {
            'id': 'orthodontics',
            'name': 'Orthodontics',
            'description': 'Braces, aligners, and orthodontic treatments',
            'icon': '📐',
            'color': 'bg-pink-50 border-pink-200'
        },
        {
            'id': 'pedodontics',
            'name': 'Pediatric Dentistry',
            'description': 'Dental care specifically for children',
            'icon': '👶',
            'color': 'bg-yellow-50 border-yellow-200'
        },
        {
            'id': 'cosmetic',
            'name': 'Cosmetic Dentistry',
            'description': 'Whitening, veneers, and aesthetic procedures',
            'icon': '✨',
            'color': 'bg-indigo-50 border-indigo-200'
        },
        {
            'id': 'general_dentistry',
            'name': 'General Dentistry',
            'description': 'Routine cleanings and general dental procedures',
            'icon': '🏥',
            'color': 'bg-gray-50 border-gray-200'
        }
    ]
    
    # Clear and update specialties
    db.specialties.delete_many({})
    for specialty in specialties:
        db.specialties.insert_one(specialty)
    
    print("✅ Updated specialties collection")

if __name__ == "__main__":
    process_all_pdfs()