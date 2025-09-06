#!/usr/bin/env python3
"""
Procedure Formatting Test for Dental Post-Operative Care App
Tests the procedure formatting fix to verify content includes bullet points, markdown headers, and proper line breaks
"""

import requests
import json
import sys
from pymongo import MongoClient
import os
from typing import Dict, Any, List

# MongoDB connection details
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

# Backend URL
BACKEND_URL = "https://careplan-builder.preview.emergentagent.com/api"

class ProcedureFormattingTester:
    def __init__(self, mongo_url: str, db_name: str, backend_url: str):
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.backend_url = backend_url
        self.client = None
        self.db = None
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def connect_to_mongodb(self):
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            
            # Test connection by listing collections
            collections = self.db.list_collection_names()
            self.log_test("MongoDB Connection", True, f"Connected to {self.mongo_url}/{self.db_name}, found {len(collections)} collections")
            return True
            
        except Exception as e:
            self.log_test("MongoDB Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_database_procedure_formatting(self, procedure_id: str = "alveoloplasty"):
        """Test procedure formatting directly from database"""
        if self.db is None:
            self.log_test(f"Database Procedure Formatting ({procedure_id})", False, "No database connection")
            return False
            
        try:
            # Query the procedure from database
            procedure = self.db.procedures.find_one({"id": procedure_id})
            
            if not procedure:
                self.log_test(f"Database Procedure Formatting ({procedure_id})", False, f"Procedure '{procedure_id}' not found in database")
                return False
            
            overview = procedure.get("overview", "")
            
            if not overview:
                self.log_test(f"Database Procedure Formatting ({procedure_id})", False, "No overview content found")
                return False
            
            # Check for formatting elements
            has_bullet_points = "•" in overview or "- " in overview
            has_markdown_headers = "**" in overview
            has_line_breaks = "\n" in overview
            has_short_paragraphs = len([p for p in overview.split('\n\n') if p.strip()]) > 1
            
            formatting_details = []
            if has_bullet_points:
                formatting_details.append("bullet points (• or -)")
            if has_markdown_headers:
                formatting_details.append("markdown headers (**text**)")
            if has_line_breaks:
                formatting_details.append("line breaks")
            if has_short_paragraphs:
                formatting_details.append("short paragraphs")
            
            # Show a sample of the content
            sample_content = overview[:300] + "..." if len(overview) > 300 else overview
            
            if has_bullet_points and has_line_breaks:
                self.log_test(f"Database Procedure Formatting ({procedure_id})", True, 
                            f"Content properly formatted with: {', '.join(formatting_details)}. Sample: {repr(sample_content)}")
                return True
            else:
                self.log_test(f"Database Procedure Formatting ({procedure_id})", False, 
                            f"Missing formatting elements. Found: {', '.join(formatting_details) if formatting_details else 'none'}. Sample: {repr(sample_content)}")
                return False
                
        except Exception as e:
            self.log_test(f"Database Procedure Formatting ({procedure_id})", False, f"Exception: {str(e)}")
            return False
    
    def test_api_procedure_formatting(self, procedure_id: str = "alveoloplasty"):
        """Test procedure formatting via API endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"API Procedure Formatting ({procedure_id})", False, 
                            f"API returned status {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get("success") or "data" not in data:
                self.log_test(f"API Procedure Formatting ({procedure_id})", False, 
                            "Invalid API response format")
                return False
            
            procedure = data["data"]
            overview = procedure.get("overview", "")
            
            if not overview:
                self.log_test(f"API Procedure Formatting ({procedure_id})", False, 
                            "No overview content in API response")
                return False
            
            # Check for formatting elements
            has_bullet_points = "•" in overview or "- " in overview
            has_markdown_headers = "**" in overview
            has_line_breaks = "\n" in overview
            has_short_paragraphs = len([p for p in overview.split('\n\n') if p.strip()]) > 1
            
            formatting_details = []
            if has_bullet_points:
                formatting_details.append("bullet points (• or -)")
            if has_markdown_headers:
                formatting_details.append("markdown headers (**text**)")
            if has_line_breaks:
                formatting_details.append("line breaks")
            if has_short_paragraphs:
                formatting_details.append("short paragraphs")
            
            # Show a sample of the content
            sample_content = overview[:300] + "..." if len(overview) > 300 else overview
            
            if has_bullet_points and has_line_breaks:
                self.log_test(f"API Procedure Formatting ({procedure_id})", True, 
                            f"API returns properly formatted content with: {', '.join(formatting_details)}. Sample: {repr(sample_content)}")
                return True
            else:
                self.log_test(f"API Procedure Formatting ({procedure_id})", False, 
                            f"API content missing formatting elements. Found: {', '.join(formatting_details) if formatting_details else 'none'}. Sample: {repr(sample_content)}")
                return False
                
        except Exception as e:
            self.log_test(f"API Procedure Formatting ({procedure_id})", False, f"Exception: {str(e)}")
            return False
    
    def test_multiple_procedures_formatting(self):
        """Test formatting for multiple procedures to ensure consistency"""
        test_procedures = ["alveoloplasty", "root-canal-therapy", "dental-crown-placement", "surgical-tooth-extraction"]
        
        passed_count = 0
        total_count = len(test_procedures)
        
        for procedure_id in test_procedures:
            try:
                response = self.session.get(f"{self.backend_url}/procedures/{procedure_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        procedure = data["data"]
                        overview = procedure.get("overview", "")
                        
                        has_bullet_points = "•" in overview or "- " in overview
                        has_line_breaks = "\n" in overview
                        
                        if has_bullet_points and has_line_breaks:
                            passed_count += 1
                            print(f"   ✅ {procedure_id}: Properly formatted")
                        else:
                            print(f"   ❌ {procedure_id}: Missing formatting")
                    else:
                        print(f"   ❌ {procedure_id}: Invalid API response")
                else:
                    print(f"   ❌ {procedure_id}: API error {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {procedure_id}: Exception {str(e)}")
        
        if passed_count == total_count:
            self.log_test("Multiple Procedures Formatting", True, 
                        f"All {total_count} tested procedures have proper formatting")
            return True
        else:
            self.log_test("Multiple Procedures Formatting", False, 
                        f"Only {passed_count}/{total_count} procedures have proper formatting")
            return False
    
    def test_formatting_elements_detail(self, procedure_id: str = "alveoloplasty"):
        """Test specific formatting elements in detail"""
        try:
            response = self.session.get(f"{self.backend_url}/procedures/{procedure_id}")
            
            if response.status_code != 200:
                self.log_test(f"Formatting Elements Detail ({procedure_id})", False, 
                            f"API returned status {response.status_code}")
                return False
            
            data = response.json()
            procedure = data["data"]
            overview = procedure.get("overview", "")
            
            # Count specific formatting elements
            bullet_count = overview.count("•") + overview.count("- ")
            markdown_header_count = overview.count("**") // 2  # Pairs of **
            line_break_count = overview.count("\n")
            paragraph_count = len([p for p in overview.split('\n\n') if p.strip()])
            
            details = f"Bullet points: {bullet_count}, Markdown headers: {markdown_header_count}, Line breaks: {line_break_count}, Paragraphs: {paragraph_count}"
            
            # Check if content is well-formatted
            is_well_formatted = (bullet_count > 0 and line_break_count > 0 and paragraph_count > 1)
            
            if is_well_formatted:
                self.log_test(f"Formatting Elements Detail ({procedure_id})", True, details)
                return True
            else:
                self.log_test(f"Formatting Elements Detail ({procedure_id})", False, 
                            f"Insufficient formatting. {details}")
                return False
                
        except Exception as e:
            self.log_test(f"Formatting Elements Detail ({procedure_id})", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all procedure formatting tests"""
        print(f"🧪 Starting Procedure Formatting Tests")
        print(f"🔗 Testing MongoDB: {self.mongo_url}/{self.db_name}")
        print(f"🔗 Testing API: {self.backend_url}")
        print("=" * 70)
        
        tests = [
            self.connect_to_mongodb,
            lambda: self.test_database_procedure_formatting("alveoloplasty"),
            lambda: self.test_api_procedure_formatting("alveoloplasty"),
            lambda: self.test_formatting_elements_detail("alveoloplasty"),
            self.test_multiple_procedures_formatting
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 70)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All procedure formatting tests passed! Content is properly formatted.")
            return True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            return False
    
    def cleanup(self):
        """Clean up database connection"""
        if self.client:
            self.client.close()

def main():
    """Main function to run the tests"""
    tester = ProcedureFormattingTester(MONGO_URL, DB_NAME, BACKEND_URL)
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())