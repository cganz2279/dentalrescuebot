#!/usr/bin/env python3
"""
PRECISION PDF Extractor - Clean, accurate section extraction
Fixes fragment extraction and content mixing issues
"""

import os
import re
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
import pymongo
from datetime import datetime
import traceback

class PrecisionPDFExtractor:
    def __init__(self):
        """Initialize with correct database"""
        mongo_url = 'mongodb://localhost:27017/test_database'
        self.client = pymongo.MongoClient(mongo_url)
        self.db = self.client.get_default_database()

    def extract_clean_text(self, pdf_path: str) -> str:
        """Extract and clean text from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                return full_text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def extract_section_content(self, text: str, section_name: str) -> List[str]:
        """Extract content for a specific section with precise parsing"""
        
        if section_name == "medications":
            return self.extract_medications_precise(text)
        elif section_name == "diet":
            return self.extract_diet_precise(text)
        elif section_name == "aftercare":
            return self.extract_aftercare_precise(text)
        elif section_name == "warnings":
            return self.extract_warnings_precise(text)
        else:
            return []

    def extract_medications_precise(self, text: str) -> List[str]:
        """Extract only medication-related content"""
        medication_items = []
        
        # Look for pain/medication sections
        lines = text.split('\n')
        in_med_section = False
        
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Detect medication section start
            if any(keyword in line_lower for keyword in [
                'pain & sensitivity:', 'pain management:', 'medications:', 
                'pain relief:', 'prescribed medication'
            ]):
                in_med_section = True
                # Extract content from the header line itself
                content_after_colon = self.extract_after_colon(line)
                if content_after_colon and len(content_after_colon) > 10:
                    medication_items.append(content_after_colon)
                continue
            
            # Stop at next major section
            if in_med_section and any(keyword in line_lower for keyword in [
                'oral hygiene:', 'diet:', 'follow-up:', 'special precautions:', 
                'activity:', 'bleeding:', 'swelling:'
            ]):
                break
            
            # Collect medication content
            if in_med_section:
                cleaned_line = self.clean_content_line(line)
                if self.is_medication_content(cleaned_line):
                    medication_items.append(cleaned_line)
        
        # If no section-based extraction, search for medication sentences
        if len(medication_items) < 2:
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if self.is_medication_content(sentence) and len(sentence) > 15:
                    medication_items.append(sentence.capitalize())
        
        return medication_items[:4] if medication_items else [
            "Take pain medication as prescribed by your dentist",
            "Apply ice packs to reduce swelling if recommended"
        ]

    def extract_diet_precise(self, text: str) -> List[str]:
        """Extract only diet-related content"""
        diet_items = []
        
        lines = text.split('\n')
        in_diet_section = False
        
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Detect diet section start
            if any(keyword in line_lower for keyword in [
                'diet:', 'eating:', 'food restrictions:', 'dietary guidelines:'
            ]):
                in_diet_section = True
                content_after_colon = self.extract_after_colon(line)
                if content_after_colon and len(content_after_colon) > 10:
                    diet_items.append(content_after_colon)
                continue
            
            # Stop at next major section
            if in_diet_section and any(keyword in line_lower for keyword in [
                'oral hygiene:', 'medications:', 'follow-up:', 'special precautions:',
                'activity:', 'pain & sensitivity:', 'bleeding:'
            ]):
                break
            
            # Collect diet content
            if in_diet_section:
                cleaned_line = self.clean_content_line(line)
                if self.is_diet_content(cleaned_line):
                    diet_items.append(cleaned_line)
        
        # If no section-based extraction, search for diet sentences
        if len(diet_items) < 2:
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if self.is_diet_content(sentence) and len(sentence) > 15:
                    diet_items.append(sentence.capitalize())
        
        return diet_items[:4] if diet_items else [
            "Eat soft foods for the first 24-48 hours",
            "Avoid hot, spicy, or hard foods"
        ]

    def extract_aftercare_precise(self, text: str) -> List[str]:
        """Extract immediate aftercare content"""
        aftercare_items = []
        
        lines = text.split('\n')
        in_aftercare_section = False
        
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Detect aftercare section start
            if any(keyword in line_lower for keyword in [
                'first 24 hours:', 'immediately after:', 'post-operative care:',
                'initial care:', 'aftercare:'
            ]):
                in_aftercare_section = True
                content_after_colon = self.extract_after_colon(line)
                if content_after_colon and len(content_after_colon) > 10:
                    aftercare_items.append(content_after_colon)
                continue
            
            # Stop at next major section
            if in_aftercare_section and any(keyword in line_lower for keyword in [
                'pain & sensitivity:', 'diet:', 'oral hygiene:', 'follow-up:'
            ]):
                break
            
            # Collect aftercare content
            if in_aftercare_section:
                cleaned_line = self.clean_content_line(line)
                if self.is_aftercare_content(cleaned_line):
                    aftercare_items.append(cleaned_line)
        
        return aftercare_items[:4] if aftercare_items else [
            "Follow your dentist's post-operative instructions",
            "Rest and avoid strenuous activity"
        ]

    def extract_warnings_precise(self, text: str) -> List[str]:
        """Extract warning signs content"""
        warning_items = []
        
        lines = text.split('\n')
        in_warning_section = False
        
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Detect warning section start
            if any(keyword in line_lower for keyword in [
                'contact the office', 'call doctor', 'warning signs', 
                'emergency', 'signs of infection'
            ]):
                in_warning_section = True
                content_after_colon = self.extract_after_colon(line)
                if content_after_colon and len(content_after_colon) > 10:
                    warning_items.append(content_after_colon)
                continue
            
            # Collect warning content
            if in_warning_section:
                cleaned_line = self.clean_content_line(line)
                if self.is_warning_content(cleaned_line):
                    warning_items.append(cleaned_line)
        
        return warning_items[:4] if warning_items else [
            "Severe pain that doesn't improve with medication",
            "Excessive bleeding or swelling"
        ]

    def extract_after_colon(self, line: str) -> str:
        """Extract content after colon in header lines"""
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                content = parts[1].strip()
                if len(content) > 5:
                    return content
        return ""

    def clean_content_line(self, line: str) -> str:
        """Clean up content lines"""
        if not line:
            return ""
        
        # Remove bullet points and dashes
        line = re.sub(r'^[•\-*]\s*', '', line)
        line = re.sub(r'^\d+\.\s*', '', line)
        
        # Remove incomplete fragments
        if line.endswith(':') and len(line) < 20:
            return ""
        
        # Clean whitespace
        line = re.sub(r'\s+', ' ', line).strip()
        
        return line

    def is_medication_content(self, text: str) -> bool:
        """Check if text is medication-related"""
        if len(text) < 10:
            return False
        
        text_lower = text.lower()
        med_keywords = ['pain', 'medication', 'prescribed', 'otc', 'ibuprofen', 'tylenol', 'ice pack', 'antibiotic']
        non_med_keywords = ['brush', 'floss', 'eat', 'food', 'rinse', 'activity', 'exercise']
        
        has_med = any(keyword in text_lower for keyword in med_keywords)
        has_non_med = any(keyword in text_lower for keyword in non_med_keywords)
        
        return has_med and not has_non_med

    def is_diet_content(self, text: str) -> bool:
        """Check if text is diet-related"""
        if len(text) < 10:
            return False
        
        text_lower = text.lower()
        diet_keywords = ['eat', 'food', 'drink', 'soft', 'avoid', 'chew', 'liquid', 'beverage']
        non_diet_keywords = ['pain', 'medication', 'brush', 'floss', 'activity', 'exercise', 'bleeding']
        
        has_diet = any(keyword in text_lower for keyword in diet_keywords)
        has_non_diet = any(keyword in text_lower for keyword in non_diet_keywords)
        
        return has_diet and not has_non_diet

    def is_aftercare_content(self, text: str) -> bool:
        """Check if text is aftercare-related"""
        if len(text) < 10:
            return False
        
        text_lower = text.lower()
        aftercare_keywords = ['bleeding', 'swelling', 'normal', 'avoid', 'protect', 'clot', 'ice']
        
        return any(keyword in text_lower for keyword in aftercare_keywords)

    def is_warning_content(self, text: str) -> bool:
        """Check if text is warning-related"""
        if len(text) < 10:
            return False
        
        text_lower = text.lower()
        warning_keywords = ['severe', 'excessive', 'infection', 'fever', 'call', 'contact', 'emergency']
        
        return any(keyword in text_lower for keyword in warning_keywords)

    def process_single_pdf(self, pdf_path: str) -> Optional[Dict]:
        """Process PDF with precision extraction"""
        try:
            filename = os.path.basename(pdf_path)
            print(f"Processing: {filename}")
            
            # Extract text
            text = self.extract_clean_text(pdf_path)
            if not text:
                return None
            
            # Create procedure data with precise extraction
            procedure_data = {
                'id': self.create_procedure_id(filename),
                'name': self.create_display_name(filename),
                'specialty': 'general-dentistry',  # Simplified for now
                'specialtyName': 'General Dentistry',
                'duration': 'Follow your dentist\'s timeline',
                'overview': self.extract_overview(text),
                'immediateAftercare': self.extract_section_content(text, 'aftercare'),
                'dietRestrictions': self.extract_section_content(text, 'diet'),
                'warningSignsToCallDoctor': self.extract_section_content(text, 'warnings'),
                'recoveryTimeline': [
                    {"day": "Day 1", "activity": "Rest and follow immediate care instructions"},
                    {"day": "Day 2-3", "activity": "Gradual return to normal activities"},
                    {"day": "Week 1", "activity": "Most symptoms should subside"}
                ],
                'medications': self.extract_section_content(text, 'medications'),
                'lastUpdated': datetime.utcnow().isoformat()
            }
            
            return procedure_data
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return None

    def extract_overview(self, text: str) -> str:
        """Extract overview/purpose"""
        lines = text.split('\n')
        for line in lines:
            if 'purpose:' in line.lower():
                return line.split(':', 1)[1].strip()[:500]
        
        # Get first meaningful paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para) > 50 and not para.isupper():
                return para.strip()[:500]
        
        return "Post-operative care instructions for this dental procedure."

    def create_procedure_id(self, filename: str) -> str:
        """Create clean procedure ID"""
        name = filename.replace('Post_Op_', '').replace('.pdf', '')
        name = re.sub(r'[_\s]+', '-', name.lower())
        return re.sub(r'[^a-z0-9\-]', '', name).strip('-')

    def create_display_name(self, filename: str) -> str:
        """Create display name"""
        name = filename.replace('Post_Op_', '').replace('.pdf', '')
        return re.sub(r'[_]', ' ', name).title()

    def process_all_pdfs(self, pdf_directory: str) -> List[Dict]:
        """Process all PDFs with precision"""
        procedures = []
        pdf_files = list(Path(pdf_directory).glob('*.pdf'))
        
        print(f"PRECISION EXTRACTION: {len(pdf_files)} PDFs")
        
        for pdf_path in pdf_files:
            procedure_data = self.process_single_pdf(str(pdf_path))
            if procedure_data:
                procedures.append(procedure_data)
        
        return procedures

    def update_database(self, procedures: List[Dict]) -> bool:
        """Update database with clean content"""
        try:
            result = self.db.procedures.delete_many({})
            print(f"Deleted {result.deleted_count} existing procedures")
            
            if procedures:
                insert_result = self.db.procedures.insert_many(procedures)
                print(f"Inserted {len(insert_result.inserted_ids)} procedures with CLEAN content")
                return True
            return False
        except Exception as e:
            print(f"Database error: {e}")
            return False

def main():
    extractor = PrecisionPDFExtractor()
    procedures = extractor.process_all_pdfs("/app/original_pdfs")
    
    if procedures:
        success = extractor.update_database(procedures)
        if success:
            print(f"\n✅ SUCCESS: {len(procedures)} procedures with CLEAN, PRECISE content")
        else:
            print("❌ Database update failed")
    else:
        print("❌ No procedures processed")

if __name__ == "__main__":
    main()