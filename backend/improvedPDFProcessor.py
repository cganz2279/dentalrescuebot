import asyncio
import os
import re
from PyPDF2 import PdfReader
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Specialty mapping (same as before)
specialty_mapping = {
    'endodontics': {
        'keywords': ['root canal', 'apicoectomy', 'pulpotomy', 'vital pulp', 'hemisection', 'root amputation', 'root resection', 'endodontic'],
        'name': 'Endodontics',
        'icon': 'Activity',
        'color': 'bg-blue-50 border-blue-200'
    },
    'oral-surgery': {
        'keywords': ['extraction', 'surgical', 'wisdom', 'impacted', 'bone graft', 'sinus lift', 'implant', 'cyst', 'lesion removal', 
                    'trauma', 'cancer surgery', 'orthognathic', 'tori removal', 'cleft', 'biopsy', 'alveoloplasty', 'frenectomy',
                    'vestibuloplasty', 'coronectomy', 'odontectomy', 'maxillofacial', 'third molar', 'socket preservation'],
        'name': 'Oral Surgery',
        'icon': 'Scissors',
        'color': 'bg-red-50 border-red-200'
    },
    'prosthodontics': {
        'keywords': ['crown', 'bridge', 'denture', 'veneer', 'inlay', 'onlay', 'full mouth rehabilitation', 'immediate dentures', 
                    'reline', 'rebasing', 'implant crown', 'abutment', 'provisional', 'temporary crown'],
        'name': 'Prosthodontics',
        'icon': 'Crown',
        'color': 'bg-purple-50 border-purple-200'
    },
    'periodontics': {
        'keywords': ['scaling', 'root planing', 'periodontal', 'gum', 'gingivectomy', 'gingivoplasty', 'flap surgery', 
                    'tissue graft', 'connective tissue', 'free gingival', 'crown lengthening', 'osseous', 'regenerative', 
                    'guided tissue', 'membrane', 'bone regeneration', 'perio'],
        'name': 'Periodontics',
        'icon': 'Heart',
        'color': 'bg-green-50 border-green-200'
    },
    'general-dentistry': {
        'keywords': ['filling', 'amalgam', 'tooth colored', 'composite', 'bonding', 'sealant', 'whitening', 'cleaning', 
                    'fluoride', 'prophylaxis'],
        'name': 'General Dentistry',
        'icon': 'Shield',  
        'color': 'bg-orange-50 border-orange-200'
    },
    'orthodontics': {
        'keywords': ['orthodontic', 'braces', 'tad placement', 'surgical orthodontics', 'adjustment', 'appliance delivery',
                    'retainer', 'aligners', 'invisalign', 'expansion', 'headgear'],
        'name': 'Orthodontics',
        'icon': 'Zap',
        'color': 'bg-teal-50 border-teal-200'
    },
    'pedodontics': {
        'keywords': ['pediatric', 'child', 'kids', 'baby tooth', 'primary tooth', 'space maintainer', 'pulpotomy pediatric'],
        'name': 'Pediatric Dentistry',
        'icon': 'Baby',
        'color': 'bg-pink-50 border-pink-200'
    },
    'oral-medicine': {
        'keywords': ['tmj', 'sleep apnea', 'nightguard', 'occlusal guard', 'oral cancer screening', 'biopsy soft tissue',
                    'lesion', 'oral pathology', 'medicine'],
        'name': 'Oral Medicine',
        'icon': 'Stethoscope',
        'color': 'bg-indigo-50 border-indigo-200'
    }
}

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def categorize_procedure(procedure_name, content):
    """Categorize procedure based on keywords"""
    text = (procedure_name + ' ' + content).lower()
    
    # Score each specialty based on keyword matches
    scores = {}
    for specialty_id, specialty in specialty_mapping.items():
        score = 0
        for keyword in specialty['keywords']:
            if keyword.lower() in text:
                # Weight longer keywords more heavily
                score += len(keyword.split())
        scores[specialty_id] = score
    
    # Get the specialty with the highest score
    if scores and max(scores.values()) > 0:
        best_specialty_id = max(scores, key=scores.get)
        specialty = specialty_mapping[best_specialty_id]
        return {
            'id': best_specialty_id,
            'name': specialty['name'],
            'icon': specialty['icon'],
            'color': specialty['color']
        }
    
    # Default to general dentistry
    return {
        'id': 'general-dentistry',
        'name': 'General Dentistry',
        'icon': 'Shield',
        'color': 'bg-orange-50 border-orange-200'
    }

def improved_extract_sections(text):
    """Improved extraction that captures the full PDF content structure"""
    
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text).strip()
    
    sections = {
        'overview': '',
        'immediateAftercare': [],
        'dietRestrictions': [],
        'warningSignsToCallDoctor': [],
        'recoveryTimeline': [],
        'medications': []
    }
    
    # Store the complete text as overview for now - this preserves ALL content
    sections['overview'] = text
    
    # Split text into lines for better parsing
    lines = text.split('\n')
    current_section = None
    current_items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Identify section headers
        line_lower = line.lower()
        
        # Extract Purpose/Overview content
        if 'purpose:' in line_lower or line.startswith('Purpose:'):
            overview_content = line.split(':', 1)[1].strip()
            if overview_content:
                sections['overview'] = overview_content + ' ' + sections['overview']
        
        # Extract First 24 Hours / Immediate care
        elif any(phrase in line_lower for phrase in ['first 24 hours:', 'immediate care:', 'first day:']):
            current_section = 'immediateAftercare'
            current_items = []
        
        # Extract Diet instructions  
        elif 'diet:' in line_lower:
            current_section = 'dietRestrictions'
            current_items = []
            
        # Extract Pain & Sensitivity (part of aftercare)
        elif any(phrase in line_lower for phrase in ['pain', 'sensitivity']):
            if current_section != 'immediateAftercare':
                current_section = 'immediateAftercare'
                
        # Extract Follow-up / Warning signs
        elif any(phrase in line_lower for phrase in ['follow-up:', 'contact', 'call', 'warning']):
            current_section = 'warningSignsToCallDoctor'
            current_items = []
            
        # Extract Special Precautions (part of aftercare)
        elif 'special precautions:' in line_lower:
            current_section = 'immediateAftercare'
            
        # Extract Oral Hygiene (part of aftercare)
        elif 'oral hygiene:' in line_lower:
            current_section = 'immediateAftercare'
            
        # If we're in a section, collect the content
        elif current_section and line.startswith('-'):
            # This is a bullet point
            item = line[1:].strip()  # Remove the dash
            if len(item) > 5:  # Only keep meaningful items
                current_items.append(item)
                sections[current_section] = list(set(sections[current_section] + current_items))
        
        # If we're in a section and it's regular content, add it
        elif current_section and line and not line.endswith(':'):
            # This is content for the current section
            if len(line) > 10:  # Only keep meaningful content
                current_items.append(line)
                sections[current_section] = list(set(sections[current_section] + current_items))
    
    # Fill in defaults if extraction failed
    if not sections['immediateAftercare']:
        sections['immediateAftercare'] = [
            'Follow your dentist\'s specific post-operative instructions',
            'Take prescribed medications as directed',
            'Apply ice pack to reduce swelling if recommended',
            'Maintain gentle oral hygiene as instructed'
        ]
    
    if not sections['dietRestrictions']:
        sections['dietRestrictions'] = [
            'Avoid hard or crunchy foods for 24-48 hours',
            'Eat soft foods and liquids initially',
            'Avoid extremely hot or cold foods/drinks', 
            'No smoking or alcohol during healing period'
        ]
    
    if not sections['warningSignsToCallDoctor']:
        sections['warningSignsToCallDoctor'] = [
            'Severe pain that worsens after 2-3 days',
            'Excessive bleeding that won\'t stop',
            'Signs of infection (fever, pus, bad taste)',
            'Unusual swelling that increases after 48 hours'
        ]
    
    if not sections['medications']:
        sections['medications'] = [
            'Take prescribed pain medication as directed',
            'Use anti-inflammatory medication to reduce swelling',
            'Complete antibiotic course if prescribed'
        ]
    
    # Generate recovery timeline based on procedure type
    sections['recoveryTimeline'] = [
        {'day': '1-2', 'activity': 'Initial healing and adjustment period'},
        {'day': '3-7', 'activity': 'Gradual improvement in comfort'},
        {'day': '1-2 weeks', 'activity': 'Most symptoms should resolve'},
        {'day': '2+ weeks', 'activity': 'Complete healing expected'}
    ]
    
    return sections

def create_procedure_data(filename, text_content):
    """Create structured procedure data from PDF content"""
    
    # Extract procedure name from filename
    procedure_name = filename.replace('Post_Op_', '').replace('.pdf', '').replace('_', ' ').strip()
    
    # Create unique ID
    procedure_id = procedure_name.lower().replace(' ', '-').replace('--', '-')
    
    # Categorize the procedure
    specialty = categorize_procedure(procedure_name, text_content)
    
    # Extract structured sections with improved method
    sections = improved_extract_sections(text_content)
    
    # Determine duration based on procedure type
    duration = '3-7 days recovery'
    if any(keyword in procedure_name.lower() for keyword in ['implant', 'graft', 'surgery']):
        duration = '2-4 weeks recovery'
    elif any(keyword in procedure_name.lower() for keyword in ['extraction', 'surgical']):
        duration = '7-14 days recovery'
    elif any(keyword in procedure_name.lower() for keyword in ['filling', 'crown', 'cleaning']):
        duration = '1-3 days sensitivity'
    
    return {
        'id': procedure_id,
        'name': procedure_name,
        'specialty': specialty['id'],
        'specialtyName': specialty['name'],
        'duration': duration,
        **sections
    }

async def update_single_procedure():
    """Update a single procedure to test the improved extraction"""
    
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"🔄 Testing improved PDF extraction on Root Canal Therapy...")
    
    pdf_path = '/app/pdf-source/Post_Op_Root_Canal_Therapy.pdf'
    
    try:
        # Extract text from PDF
        text_content = extract_text_from_pdf(pdf_path)
        
        if not text_content.strip():
            print(f"⚠️  No text extracted from Root Canal Therapy PDF")
            return
            
        print(f"📄 Extracted {len(text_content)} characters from PDF")
        
        # Create structured procedure data with improved extraction
        procedure_data = create_procedure_data('Post_Op_Root_Canal_Therapy.pdf', text_content)
        
        print(f"📊 Improved extraction results:")
        print(f"   Overview length: {len(procedure_data['overview'])} characters")
        print(f"   Immediate Aftercare: {len(procedure_data['immediateAftercare'])} items")
        print(f"   Diet Restrictions: {len(procedure_data['dietRestrictions'])} items")
        print(f"   Warning Signs: {len(procedure_data['warningSignsToCallDoctor'])} items")
        
        # Update the database
        result = await db.procedures.replace_one(
            {'id': 'root-canal-therapy'},
            procedure_data,
            upsert=True
        )
        
        print(f"✅ Updated Root Canal Therapy procedure in database")
        
    except Exception as e:
        print(f"❌ Error processing Root Canal Therapy: {e}")

if __name__ == "__main__":
    asyncio.run(update_single_procedure())