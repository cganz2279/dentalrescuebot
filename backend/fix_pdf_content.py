import asyncio
import os
import zipfile
import PyPDF2
import io
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Specialty mapping
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
    'oral-medicine': {
        'keywords': ['tmj', 'sleep apnea', 'nightguard', 'occlusal guard', 'oral cancer screening', 'biopsy soft tissue',
                    'lesion', 'oral pathology', 'medicine'],
        'name': 'Oral Medicine',
        'icon': 'Stethoscope',
        'color': 'bg-indigo-50 border-indigo-200'
    }
}

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

def extract_text_from_pdf_data(pdf_data):
    """Extract text from PDF binary data"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

async def fix_pdf_content():
    """Fix PDF content by properly extracting from original PDFs"""
    
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"🔄 Fixing PDF content in database: {db_name}")
    
    # Clear existing procedures and specialties
    await db.procedures.delete_many({})
    await db.specialties.delete_many({})
    
    zip_file_path = '/app/PostOpProcedures.zip'
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        pdf_files = [f for f in zip_file.namelist() if f.endswith('.pdf') and not f.startswith('__MACOSX')]
        
        print(f"📄 Found {len(pdf_files)} PDF files to process")
        
        processed_procedures = []
        specialty_counts = {}
        
        for i, filename in enumerate(pdf_files, 1):
            print(f"⚙️  Processing {i}/{len(pdf_files)}: {filename}")
            
            try:
                # Extract text from PDF
                pdf_data = zip_file.read(filename)
                text_content = extract_text_from_pdf_data(pdf_data)
                
                if not text_content.strip():
                    print(f"⚠️  No text extracted from {filename}")
                    continue
                
                # Extract procedure name from filename
                procedure_name = filename.replace('Post_Op_', '').replace('.pdf', '').replace('_', ' ').strip()
                
                # Clean up procedure name
                if procedure_name.startswith('Post-Operative Instructions'):
                    procedure_name = procedure_name.replace('Post-Operative Instructions_', '').strip()
                
                # Create unique ID
                procedure_id = procedure_name.lower().replace(' ', '-').replace('--', '-')
                
                # Categorize the procedure
                specialty = categorize_procedure(procedure_name, text_content)
                
                # Use the EXACT content from the PDF as overview
                # Clean it up slightly but keep all the original structure
                overview_content = text_content.strip()
                
                # Remove any header that repeats the procedure name
                lines = overview_content.split('\n')
                clean_lines = []
                for line in lines[1:]:  # Skip first line (usually the title)
                    clean_line = line.strip()
                    if clean_line and not clean_line.lower() == procedure_name.lower():
                        clean_lines.append(clean_line)
                
                overview_content = '\n'.join(clean_lines).strip()
                
                # Determine duration based on procedure type
                duration = '3-7 days recovery'
                if any(keyword in procedure_name.lower() for keyword in ['implant', 'graft', 'surgery']):
                    duration = '2-4 weeks recovery'
                elif any(keyword in procedure_name.lower() for keyword in ['extraction', 'surgical']):
                    duration = '7-14 days recovery'
                elif any(keyword in procedure_name.lower() for keyword in ['filling', 'crown', 'cleaning']):
                    duration = '1-3 days sensitivity'
                
                # Track specialty counts
                specialty_id = specialty['id']
                if specialty_id not in specialty_counts:
                    specialty_counts[specialty_id] = 0
                specialty_counts[specialty_id] += 1
                
                # Create procedure data with EXACT PDF content
                procedure_data = {
                    'id': procedure_id,
                    'name': procedure_name,
                    'specialty': specialty['id'],
                    'specialtyName': specialty['name'],
                    'duration': duration,
                    'overview': overview_content,  # This is the user's EXACT content
                    # Remove all other fields - we only want overview
                }
                
                processed_procedures.append(procedure_data)
                
                print(f"✅ {procedure_name} → {specialty['name']}")
                print(f"   Content length: {len(overview_content)} characters")
                
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
                continue
        
        # Insert procedures into database
        if processed_procedures:
            await db.procedures.insert_many(processed_procedures)
            print(f"✅ Inserted {len(processed_procedures)} procedures with ORIGINAL content")
        
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
        
        print(f"\n🎉 Content fix complete!")
        print(f"📊 Final Database Stats:")
        print(f"   Total Procedures: {total_procedures}")
        print(f"   Total Specialties: {total_specialties}")
        print(f"\n📋 Procedures per Specialty:")
        
        for specialty_id, count in specialty_counts.items():
            specialty_name = specialty_mapping[specialty_id]['name']
            print(f"   {specialty_name}: {count} procedures")

if __name__ == "__main__":
    asyncio.run(fix_pdf_content())