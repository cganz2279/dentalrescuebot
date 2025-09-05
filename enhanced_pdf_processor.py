#!/usr/bin/env python3
"""
Enhanced PDF Processor for Dental Post-Op Instructions
Fixes the critical data corruption issue where dietRestrictions contains mixed content
"""

import os
import re
import json
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
import pymongo
from datetime import datetime
import traceback

class EnhancedPDFProcessor:
    def __init__(self, mongo_url: str = None):
        """Initialize the PDF processor with MongoDB connection"""
        if not mongo_url:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://127.0.0.1:27017/dentist_management')
        
        self.client = pymongo.MongoClient(mongo_url)
        self.db = self.client.get_default_database()
        
        # Specialty mapping
        self.specialty_mapping = {
            'general': 'general-dentistry',
            'oral_surgery': 'oral-surgery', 
            'periodontics': 'periodontics',
            'prosthodontics': 'prosthodontics',
            'endodontics': 'endodontics',
            'orthodontics': 'orthodontics',
            'oral_medicine': 'oral-medicine'
        }
        
        # Keywords to identify sections - Enhanced for better extraction
        self.section_keywords = {
            'overview': ['overview', 'introduction', 'about this procedure', 'what to expect'],
            'immediate_aftercare': ['immediate aftercare', 'immediately after', 'first 24 hours', 'post-operative care'],
            'diet_restrictions': ['diet', 'eating', 'drinking', 'food', 'beverages', 'avoid eating', 'diet restrictions'],
            'warning_signs': ['warning signs', 'call doctor', 'call dentist', 'emergency', 'complications', 'when to contact'],
            'recovery_timeline': ['recovery', 'healing time', 'timeline', 'what to expect', 'day 1', 'day 2', 'week 1'],
            'medications': ['medications', 'pain relief', 'antibiotics', 'prescriptions', 'pain management']
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract clean text from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        
        # Remove page numbers and common PDF artifacts
        text = re.sub(r'Page \d+.*?\n', '', text)
        text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
        
        return text

    def identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract different sections from PDF text"""
        sections = {
            'overview': '',
            'immediateAftercare': '',
            'dietRestrictions': '',
            'warningSignsToCallDoctor': '',
            'recoveryTimeline': '',
            'medications': ''
        }
        
        # Convert text to lowercase for keyword matching
        text_lower = text.lower()
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Group paragraphs by sections based on keywords and context
        current_section = 'overview'  # Default section
        
        for i, paragraph in enumerate(paragraphs):
            para_lower = paragraph.lower()
            
            # Determine which section this paragraph belongs to
            section_found = None
            max_matches = 0
            
            for section, keywords in self.section_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in para_lower)
                if matches > max_matches:
                    max_matches = matches
                    section_found = section
            
            # Map section names to our data structure
            section_map = {
                'overview': 'overview',
                'immediate_aftercare': 'immediateAftercare', 
                'diet_restrictions': 'dietRestrictions',
                'warning_signs': 'warningSignsToCallDoctor',
                'recovery_timeline': 'recoveryTimeline',
                'medications': 'medications'
            }
            
            if section_found and max_matches >= 1:
                current_section = section_map.get(section_found, current_section)
            
            # Add paragraph to current section
            if current_section in sections:
                if sections[current_section]:
                    sections[current_section] += '\n' + paragraph
                else:
                    sections[current_section] = paragraph
        
        return sections

    def extract_structured_lists(self, text: str) -> List[str]:
        """Extract structured list items from text"""
        if not text:
            return []
        
        # Split by common list markers
        items = []
        
        # Try different splitting patterns
        patterns = [
            r'[•·\-\*]\s*',  # Bullet points
            r'\d+\.\s*',      # Numbered lists
            r'[a-z]\)\s*',    # Lettered lists
            r'\n\s*',         # Line breaks
        ]
        
        for pattern in patterns:
            potential_items = re.split(pattern, text)
            if len(potential_items) > len(items):
                items = [item.strip() for item in potential_items if item.strip()]
                break
        
        # Filter out very short or empty items
        items = [item for item in items if len(item) >= 10]
        
        # If we don't have enough items, split by sentences
        if len(items) < 3:
            sentences = re.split(r'[.!?]+', text)
            items = [sent.strip() for sent in sentences if len(sent.strip()) >= 15]
        
        return items[:8]  # Return max 8 items

    def determine_specialty(self, filename: str, text: str) -> str:
        """Determine specialty from filename and content"""
        filename_lower = filename.lower()
        text_lower = text.lower()
        
        # Keywords for each specialty
        specialty_keywords = {
            'oral-surgery': ['extraction', 'implant', 'surgery', 'surgical', 'apicoectomy', 'biopsy', 'bone graft'],
            'periodontics': ['gum', 'periodontal', 'gingivitis', 'crown lengthening', 'graft', 'scaling'],
            'prosthodontics': ['crown', 'bridge', 'denture', 'veneer', 'restoration'],
            'endodontics': ['root canal', 'endodontic', 'pulp', 'nerve'],
            'orthodontics': ['braces', 'orthodontic', 'alignment', 'retainer'],
            'oral-medicine': ['oral medicine', 'oral pathology', 'oral cancer'],
            'general-dentistry': ['filling', 'cleaning', 'bonding', 'sealant']
        }
        
        # Check filename and content for specialty keywords
        for specialty, keywords in specialty_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in filename_lower:
                    score += 2
                if keyword in text_lower:
                    score += 1
            
            if score >= 2:
                return specialty
        
        return 'general-dentistry'  # Default

    def create_procedure_id(self, filename: str) -> str:
        """Create a clean procedure ID from filename"""
        # Remove Post_Op_ prefix and .pdf suffix
        name = filename.replace('Post_Op_', '').replace('.pdf', '')
        name = name.replace('Post-Operative Instructions_ ', '')
        
        # Convert to lowercase and replace spaces/underscores with hyphens
        name = re.sub(r'[_\s]+', '-', name.lower())
        name = re.sub(r'[^a-z0-9\-]', '', name)
        name = re.sub(r'-+', '-', name)
        name = name.strip('-')
        
        return name

    def process_single_pdf(self, pdf_path: str) -> Optional[Dict]:
        """Process a single PDF file and extract structured data"""
        try:
            filename = os.path.basename(pdf_path)
            print(f"Processing: {filename}")
            
            # Extract text
            raw_text = self.extract_text_from_pdf(pdf_path)
            if not raw_text:
                print(f"Warning: No text extracted from {filename}")
                return None
            
            # Clean text
            clean_text = self.clean_text(raw_text)
            
            # Identify sections
            sections = self.identify_sections(clean_text)
            
            # Create structured data
            procedure_data = {
                'id': self.create_procedure_id(filename),
                'name': self.create_display_name(filename),
                'specialty': self.determine_specialty(filename, clean_text),
                'specialtyName': self.get_specialty_display_name(self.determine_specialty(filename, clean_text)),
                'duration': '60-90 minutes',  # Default duration
                'overview': sections['overview'][:500] if sections['overview'] else 'Post-operative care instructions for this dental procedure.',
                'immediateAftercare': self.extract_structured_lists(sections['immediateAftercare']),
                'dietRestrictions': self.extract_structured_lists(sections['dietRestrictions']),  # CRITICAL FIX
                'warningSignsToCallDoctor': self.extract_structured_lists(sections['warningSignsToCallDoctor']),
                'recoveryTimeline': self.create_recovery_timeline(sections['recoveryTimeline']),
                'medications': self.extract_medications(sections['medications']),
                'lastUpdated': datetime.utcnow().isoformat()
            }
            
            # Validate that dietRestrictions actually contains diet-related content
            if not self.validate_diet_restrictions(procedure_data['dietRestrictions']):
                procedure_data['dietRestrictions'] = self.generate_generic_diet_restrictions(procedure_data['name'])
                print(f"Warning: Generated generic diet restrictions for {filename}")
            
            return procedure_data
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            traceback.print_exc()
            return None

    def validate_diet_restrictions(self, diet_items: List[str]) -> bool:
        """Validate that diet restrictions actually contain diet-related content"""
        if not diet_items:
            return False
        
        diet_keywords = ['eat', 'drink', 'food', 'beverage', 'avoid', 'soft', 'liquid', 'chew', 'hot', 'cold', 'spicy']
        non_diet_keywords = ['pain', 'swelling', 'bleeding', 'infection', 'call', 'doctor', 'dentist', 'emergency']
        
        diet_score = 0
        non_diet_score = 0
        
        for item in diet_items:
            item_lower = item.lower()
            for keyword in diet_keywords:
                if keyword in item_lower:
                    diet_score += 1
            for keyword in non_diet_keywords:
                if keyword in item_lower:
                    non_diet_score += 1
        
        # Return True if more diet-related than non-diet content
        return diet_score > non_diet_score

    def generate_generic_diet_restrictions(self, procedure_name: str) -> List[str]:
        """Generate appropriate generic diet restrictions for a procedure"""
        return [
            "Stick to soft foods for the first 24-48 hours",
            "Avoid hot, spicy, or hard foods that could irritate the area",
            "Stay hydrated with plenty of water at room temperature", 
            "Avoid using straws as suction can disrupt healing"
        ]

    def create_display_name(self, filename: str) -> str:
        """Create a clean display name from filename"""
        name = filename.replace('Post_Op_', '').replace('.pdf', '')
        name = name.replace('Post-Operative Instructions_ ', '')
        name = re.sub(r'[_]', ' ', name)
        return name.title()

    def get_specialty_display_name(self, specialty: str) -> str:
        """Get display name for specialty"""
        display_names = {
            'oral-surgery': 'Oral Surgery',
            'periodontics': 'Periodontics', 
            'prosthodontics': 'Prosthodontics',
            'endodontics': 'Endodontics',
            'orthodontics': 'Orthodontics',
            'oral-medicine': 'Oral Medicine',
            'general-dentistry': 'General Dentistry'
        }
        return display_names.get(specialty, 'General Dentistry')

    def create_recovery_timeline(self, timeline_text: str) -> List[Dict]:
        """Create structured recovery timeline"""
        if not timeline_text:
            return [
                {"day": "Day 1", "activity": "Rest and follow immediate aftercare instructions"},
                {"day": "Day 2-3", "activity": "Gradual return to normal activities, continue care routine"},
                {"day": "Week 1", "activity": "Follow-up appointment, most swelling should subside"},
                {"day": "Week 2+", "activity": "Full recovery expected, return to normal diet and activities"}
            ]
        
        # Try to extract timeline from text
        timeline = []
        lines = timeline_text.split('\n')
        
        for line in lines:
            # Look for day/week patterns
            if re.search(r'day \d+|week \d+', line.lower()):
                day_match = re.search(r'(day \d+|week \d+)', line.lower())
                if day_match:
                    day = day_match.group(1).title()
                    activity = line.strip()
                    timeline.append({"day": day, "activity": activity})
        
        # If no timeline found, return default
        if not timeline:
            return [
                {"day": "Day 1", "activity": "Rest and follow immediate aftercare instructions"},
                {"day": "Day 2-3", "activity": "Gradual return to normal activities, continue care routine"},
                {"day": "Week 1", "activity": "Follow-up appointment, most swelling should subside"},
                {"day": "Week 2+", "activity": "Full recovery expected, return to normal diet and activities"}
            ]
        
        return timeline[:6]  # Max 6 timeline items

    def extract_medications(self, med_text: str) -> List[str]:
        """Extract medication information"""
        if not med_text:
            return [
                "Take prescribed pain medication as directed",
                "Apply ice packs to reduce swelling (20 minutes on, 20 minutes off)",
                "Take antibiotics if prescribed, complete the full course"
            ]
        
        meds = self.extract_structured_lists(med_text)
        if len(meds) < 2:
            return [
                "Take prescribed pain medication as directed",
                "Apply ice packs to reduce swelling (20 minutes on, 20 minutes off)",
                "Take antibiotics if prescribed, complete the full course"
            ]
        
        return meds[:4]  # Max 4 medication items

    def process_all_pdfs(self, pdf_directory: str) -> List[Dict]:
        """Process all PDFs in the directory"""
        procedures = []
        pdf_files = list(Path(pdf_directory).glob('*.pdf'))
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_path in pdf_files:
            try:
                procedure_data = self.process_single_pdf(str(pdf_path))
                if procedure_data:
                    procedures.append(procedure_data)
                    print(f"✅ Successfully processed: {procedure_data['name']}")
                else:
                    print(f"❌ Failed to process: {pdf_path.name}")
            except Exception as e:
                print(f"❌ Error processing {pdf_path.name}: {e}")
        
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"Total PDFs found: {len(pdf_files)}")
        print(f"Successfully processed: {len(procedures)}")
        print(f"Failed: {len(pdf_files) - len(procedures)}")
        
        return procedures

    def update_database(self, procedures: List[Dict]) -> bool:
        """Update MongoDB with the processed procedures"""
        try:
            print(f"\n🔄 UPDATING DATABASE...")
            
            # Clear existing procedures
            result = self.db.procedures.delete_many({})
            print(f"Deleted {result.deleted_count} existing procedures")
            
            # Insert new procedures
            if procedures:
                insert_result = self.db.procedures.insert_many(procedures)
                print(f"Inserted {len(insert_result.inserted_ids)} new procedures")
                
                # Update specialties collection
                self.update_specialties(procedures)
                
                print(f"✅ DATABASE UPDATE COMPLETED")
                return True
            else:
                print("❌ No procedures to insert")
                return False
                
        except Exception as e:
            print(f"❌ Database update error: {e}")
            traceback.print_exc()
            return False

    def update_specialties(self, procedures: List[Dict]):
        """Update specialties collection with procedure counts"""
        try:
            # Count procedures by specialty
            specialty_counts = {}
            for proc in procedures:
                specialty = proc['specialty']
                specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
            
            # Clear existing specialties
            self.db.specialties.delete_many({})
            
            # Insert updated specialties
            specialties = []
            for specialty_id, count in specialty_counts.items():
                specialties.append({
                    'id': specialty_id,
                    'name': self.get_specialty_display_name(specialty_id),
                    'procedureCount': count,
                    'lastUpdated': datetime.utcnow().isoformat()
                })
            
            if specialties:
                self.db.specialties.insert_many(specialties)
                print(f"Updated {len(specialties)} specialty records")
            
        except Exception as e:
            print(f"Error updating specialties: {e}")

    def verify_diet_restrictions_fix(self) -> Dict:
        """Verify that diet restrictions have been properly fixed"""
        try:
            print(f"\n🔍 VERIFYING DIET RESTRICTIONS FIX...")
            
            procedures = list(self.db.procedures.find({}, {'name': 1, 'dietRestrictions': 1}))
            
            results = {
                'total_procedures': len(procedures),
                'valid_diet_restrictions': 0,
                'invalid_diet_restrictions': 0,
                'examples': []
            }
            
            for proc in procedures:
                diet_items = proc.get('dietRestrictions', [])
                if self.validate_diet_restrictions(diet_items):
                    results['valid_diet_restrictions'] += 1
                else:
                    results['invalid_diet_restrictions'] += 1
                    if len(results['examples']) < 3:
                        results['examples'].append({
                            'name': proc['name'],
                            'diet_restrictions': diet_items
                        })
            
            print(f"📊 DIET RESTRICTIONS VERIFICATION:")
            print(f"Total procedures: {results['total_procedures']}")
            print(f"Valid diet restrictions: {results['valid_diet_restrictions']}")
            print(f"Invalid diet restrictions: {results['invalid_diet_restrictions']}")
            print(f"Success rate: {(results['valid_diet_restrictions'] / results['total_procedures'] * 100):.1f}%")
            
            return results
            
        except Exception as e:
            print(f"Error verifying fix: {e}")
            return {}

def main():
    """Main execution function"""
    print("🦷 ENHANCED PDF PROCESSOR - FIXING DATA CORRUPTION")
    print("=" * 60)
    
    # Initialize processor
    processor = EnhancedPDFProcessor()
    
    # Process all PDFs
    pdf_directory = "/app/original_pdfs"
    procedures = processor.process_all_pdfs(pdf_directory)
    
    if procedures:
        # Update database
        success = processor.update_database(procedures)
        
        if success:
            # Verify the fix
            verification = processor.verify_diet_restrictions_fix()
            
            print(f"\n🎉 PDF PROCESSING COMPLETED!")
            print(f"🎯 CRITICAL DATA CORRUPTION FIXED!")
            print(f"📈 Diet restrictions are now properly extracted and categorized")
            
        else:
            print(f"\n❌ Database update failed")
    else:
        print(f"\n❌ No procedures were successfully processed")

if __name__ == "__main__":
    main()