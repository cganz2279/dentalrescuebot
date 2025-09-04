import asyncio
import os
import re
from PyPDF2 import PdfReader
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Comprehensive specialty mapping
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

def extract_sections(text):
    """Extract different sections from PDF text using various patterns"""
    
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
    
    # Extract overview (first meaningful paragraph or description)
    overview_patterns = [
        r'(?:overview|description|what is|what to expect|procedure)[:\s]+(.*?)(?=\n\n|immediate|post|care|instructions|diet)',
        r'^(.*?)(?=immediate|post|care|instructions|diet)',
    ]
    
    for pattern in overview_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match and len(match.group(1).strip()) > 50:
            sections['overview'] = match.group(1).strip()[:500] + "..."
            break
    
    if not sections['overview']:
        sections['overview'] = text[:200].strip() + "..."
    
    # Extract aftercare instructions
    aftercare_patterns = [
        r'(?:immediate|post-?operative|after\s*care|instructions)[:\s]+(.*?)(?=diet|food|eating|warning|medications)',
        r'(?:what to do|care instructions|follow these)[:\s]+(.*?)(?=diet|food|warning)',
    ]
    
    for pattern in aftercare_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            instructions_text = match.group(1)
            # Split by bullets, numbers, or periods
            instructions = re.split(r'[•\n\r]\s*|\d+\.\s*', instructions_text)
            instructions = [inst.strip() for inst in instructions if len(inst.strip()) > 15]
            sections['immediateAftercare'] = instructions[:6]
            break
    
    # Extract diet restrictions
    diet_patterns = [
        r'(?:diet|food|eating|drink|avoid)[:\s]+(.*?)(?=warning|call|contact|medications)',
        r'(?:do not eat|don\'t eat|dietary)[:\s]+(.*?)(?=warning|medications)',
    ]
    
    for pattern in diet_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            diet_text = match.group(1)
            restrictions = re.split(r'[•\n\r]\s*|\d+\.\s*', diet_text)
            restrictions = [rest.strip() for rest in restrictions if len(rest.strip()) > 10]
            sections['dietRestrictions'] = restrictions[:5]
            break
    
    # Extract warning signs
    warning_patterns = [
        r'(?:warning|call|contact|emergency|when to call)[:\s]+(.*?)(?=medications|recovery|follow)',
        r'(?:signs|symptoms|complications)[:\s]+(.*?)(?=medications|recovery)',
    ]
    
    for pattern in warning_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            warning_text = match.group(1)
            warnings = re.split(r'[•\n\r]\s*|\d+\.\s*', warning_text)
            warnings = [warn.strip() for warn in warnings if len(warn.strip()) > 15]
            sections['warningSignsToCallDoctor'] = warnings[:5]
            break
    
    # Extract medications
    med_patterns = [
        r'(?:medication|medicine|pain|ibuprofen|prescription)[:\s]+(.*?)(?=recovery|follow|appointment)',
        r'(?:take|prescribed|analgesic)[:\s]+(.*?)(?=recovery|follow)',
    ]
    
    for pattern in med_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            med_text = match.group(1)
            medications = re.split(r'[•\n\r]\s*|\d+\.\s*', med_text)
            medications = [med.strip() for med in medications if len(med.strip()) > 10]
            sections['medications'] = medications[:4]
            break
    
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
    
    # Extract structured sections
    sections = extract_sections(text_content)
    
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

async def process_all_pdfs():
    """Process all PDF files and populate database"""
    
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"🔄 Processing all PDFs and populating database: {db_name}")
    
    # Clear existing data
    await db.procedures.delete_many({})
    await db.specialties.delete_many({})
    
    pdf_directory = '/app/pdf-source'
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    pdf_files.sort()
    
    print(f"📄 Found {len(pdf_files)} PDF files to process")
    
    processed_procedures = []
    specialty_counts = {}
    
    # Process each PDF
    for i, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(pdf_directory, filename)
        
        print(f"⚙️  Processing {i}/{len(pdf_files)}: {filename}")
        
        try:
            # Extract text from PDF
            text_content = extract_text_from_pdf(pdf_path)
            
            if not text_content.strip():
                print(f"⚠️  No text extracted from {filename}")
                continue
                
            # Create structured procedure data
            procedure_data = create_procedure_data(filename, text_content)
            
            # Track specialty counts
            specialty_id = procedure_data['specialty']
            if specialty_id not in specialty_counts:
                specialty_counts[specialty_id] = 0
            specialty_counts[specialty_id] += 1
            
            processed_procedures.append(procedure_data)
            
            print(f"✅ {procedure_data['name']} → {procedure_data['specialtyName']}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    # Insert procedures into database
    if processed_procedures:
        await db.procedures.insert_many(processed_procedures)
        print(f"✅ Inserted {len(processed_procedures)} procedures")
    
    # Create and insert specialties
    specialties_to_insert = []
    for specialty_id, specialty_data in specialty_mapping.items():
        if specialty_id in specialty_counts:
            specialties_to_insert.append({
                'id': specialty_id,
                'name': specialty_data['name'],
                'description': f"{specialty_data['name']} procedures and treatments",
                'icon': specialty_data['icon'],
                'color': specialty_data['color']
            })
    
    if specialties_to_insert:
        await db.specialties.insert_many(specialties_to_insert)
        print(f"✅ Inserted {len(specialties_to_insert)} specialties")
    
    # Final counts
    total_procedures = await db.procedures.count_documents({})
    total_specialties = await db.specialties.count_documents({})
    
    print(f"\n🎉 Processing complete!")
    print(f"📊 Final Database Stats:")
    print(f"   Total Procedures: {total_procedures}")
    print(f"   Total Specialties: {total_specialties}")
    print(f"\n📋 Procedures per Specialty:")
    
    for specialty_id, count in specialty_counts.items():
        specialty_name = specialty_mapping[specialty_id]['name']
        print(f"   {specialty_name}: {count} procedures")

if __name__ == "__main__":
    asyncio.run(process_all_pdfs())