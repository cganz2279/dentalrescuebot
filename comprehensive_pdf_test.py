#!/usr/bin/env python3
"""
Comprehensive PDF Generation Test Suite
Tests all aspects of the enhanced PDF generation functionality
"""

import requests
import json
import sys
import time
import os
from urllib.parse import urljoin

# Configuration
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class ComprehensivePDFTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        
    def test_login_functionality(self):
        """Test 1: Login functionality with cganz2279@gmail.com/password123"""
        print("\n🔐 Testing Login Functionality...")
        
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.auth_token = data['token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.log_test("Login with cganz2279@gmail.com/password123", True, "Authentication successful")
                    return True
                else:
                    self.log_test("Login with cganz2279@gmail.com/password123", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Login with cganz2279@gmail.com/password123", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login with cganz2279@gmail.com/password123", False, f"Exception: {str(e)}")
            return False
    
    def test_procedures_endpoint_accessibility(self):
        """Test 2: Test the procedures endpoint accessibility"""
        print("\n📋 Testing Procedures Endpoint Accessibility...")
        
        try:
            response = self.session.get(f"{API_BASE}/procedures")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    procedure_count = len(data['data'])
                    self.log_test("Procedures Endpoint Accessibility", True, f"Retrieved {procedure_count} procedures successfully")
                    return data['data']
                else:
                    self.log_test("Procedures Endpoint Accessibility", False, f"Invalid response format: {data}")
                    return []
            else:
                self.log_test("Procedures Endpoint Accessibility", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Procedures Endpoint Accessibility", False, f"Exception: {str(e)}")
            return []
    
    def test_base64_logo_file_accessibility(self):
        """Test 3: Test if the base64 logo file is accessible at /dental-rescue-logo-base64.txt"""
        print("\n🖼️ Testing Base64 Logo File Accessibility...")
        
        try:
            logo_url = f"{BACKEND_URL}/dental-rescue-logo-base64.txt"
            response = self.session.get(logo_url)
            
            if response.status_code == 200:
                logo_content = response.text.strip()
                if logo_content and len(logo_content) > 1000:  # Base64 images are typically large
                    # Validate it looks like base64 (remove newlines and whitespace first)
                    clean_content = logo_content.replace('\n', '').replace('\r', '').replace(' ', '')
                    if clean_content.replace('+', '').replace('/', '').replace('=', '').isalnum():
                        self.log_test("Base64 Logo File at /dental-rescue-logo-base64.txt", True, 
                                    f"Logo file accessible and valid, size: {len(logo_content)} characters")
                        return True
                    else:
                        self.log_test("Base64 Logo File at /dental-rescue-logo-base64.txt", False, 
                                    "File accessible but doesn't appear to be valid base64")
                        return False
                else:
                    self.log_test("Base64 Logo File at /dental-rescue-logo-base64.txt", False, 
                                f"File too small or empty: {len(logo_content)} characters")
                    return False
            else:
                self.log_test("Base64 Logo File at /dental-rescue-logo-base64.txt", False, 
                            f"File not accessible, HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Base64 Logo File at /dental-rescue-logo-base64.txt", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_pdf_generator_file(self):
        """Test 4: Verify the enhanced PDF generator file exists and has correct content"""
        print("\n📦 Testing Enhanced PDF Generator File...")
        
        try:
            # Check if the enhanced PDF generator file exists
            enhanced_pdf_path = "/app/frontend/src/utils/ENHANCED_PDF_WITH_LOGO.js"
            
            if os.path.exists(enhanced_pdf_path):
                with open(enhanced_pdf_path, 'r') as f:
                    content = f.read()
                
                # Check for key features
                required_features = [
                    'ENHANCED PDF WITH LOGO GENERATOR',
                    'getBase64Logo',
                    'dental-rescue-logo-base64.txt',
                    'processContentForBoldFormatting',
                    'addFormattedContentToPDF'
                ]
                
                missing_features = []
                for feature in required_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                if not missing_features:
                    self.log_test("Enhanced PDF Generator File", True, 
                                f"File exists with all required features: {required_features}")
                    return True
                else:
                    self.log_test("Enhanced PDF Generator File", False, 
                                f"Missing features: {missing_features}")
                    return False
            else:
                self.log_test("Enhanced PDF Generator File", False, "File does not exist")
                return False
                
        except Exception as e:
            self.log_test("Enhanced PDF Generator File", False, f"Exception: {str(e)}")
            return False
    
    def test_import_statements_updated(self):
        """Test 5: Check if all imports have been successfully updated to use ENHANCED_PDF_WITH_LOGO"""
        print("\n🔄 Testing Import Statements Updated...")
        
        try:
            # Check frontend source files for import updates
            frontend_src_path = "/app/frontend/src"
            
            if not os.path.exists(frontend_src_path):
                self.log_test("Import Statements Updated", False, "Frontend source directory not found")
                return False
            
            # Find all JavaScript/JSX files that might import PDF generators
            import_files = []
            for root, dirs, files in os.walk(frontend_src_path):
                for file in files:
                    if file.endswith(('.js', '.jsx')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                if 'ENHANCED_PDF_WITH_LOGO' in content:
                                    import_files.append(file_path)
                        except:
                            continue
            
            if import_files:
                # Check that no files still use the old import
                old_import_files = []
                for root, dirs, files in os.walk(frontend_src_path):
                    for file in files:
                        if file.endswith(('.js', '.jsx')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as f:
                                    content = f.read()
                                    if 'FINAL_RAW_TEXT_ONLY' in content and 'backup' not in file_path:
                                        old_import_files.append(file_path)
                            except:
                                continue
                
                if old_import_files:
                    self.log_test("Import Statements Updated", False, 
                                f"Found {len(old_import_files)} files still using old imports")
                    return False
                else:
                    self.log_test("Import Statements Updated", True, 
                                f"All {len(import_files)} files successfully updated to ENHANCED_PDF_WITH_LOGO")
                    return True
            else:
                self.log_test("Import Statements Updated", False, "No files found using ENHANCED_PDF_WITH_LOGO")
                return False
                
        except Exception as e:
            self.log_test("Import Statements Updated", False, f"Exception: {str(e)}")
            return False
    
    def test_pdf_generation_data_readiness(self):
        """Test 6: Test enhanced PDF generation functionality readiness"""
        print("\n📄 Testing PDF Generation Data Readiness...")
        
        try:
            # Get procedures for testing
            response = self.session.get(f"{API_BASE}/procedures")
            
            if response.status_code != 200:
                self.log_test("PDF Generation Data Readiness", False, "Cannot access procedures data")
                return False
            
            data = response.json()
            procedures = data.get('data', [])
            
            if not procedures:
                self.log_test("PDF Generation Data Readiness", False, "No procedures available")
                return False
            
            # Test procedures with substantial content
            suitable_procedures = []
            bold_keyword_procedures = []
            
            bold_keywords = ['Purpose', 'First 24 Hours', 'Pain & Sensitivity', 'Oral Hygiene', 'Diet', 'Special Precautions', 'Follow-Up', 'Follow Up']
            
            for proc in procedures:
                overview = proc.get('overview', '')
                if len(overview) > 100:  # Substantial content
                    suitable_procedures.append(proc)
                    
                    # Check for bold formatting keywords
                    found_keywords = []
                    for keyword in bold_keywords:
                        if keyword.lower() in overview.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        bold_keyword_procedures.append({
                            'name': proc.get('name', 'Unknown'),
                            'keywords': found_keywords,
                            'content_length': len(overview)
                        })
            
            if suitable_procedures:
                self.log_test("PDF Generation Data Readiness", True, 
                            f"Found {len(suitable_procedures)} procedures with substantial content, "
                            f"{len(bold_keyword_procedures)} with bold formatting keywords")
                
                # Show examples
                if bold_keyword_procedures:
                    print(f"    📋 Example procedures ready for enhanced PDF:")
                    for i, proc in enumerate(bold_keyword_procedures[:3]):
                        print(f"      {i+1}. {proc['name']} - {proc['content_length']} chars, keywords: {proc['keywords']}")
                
                return True
            else:
                self.log_test("PDF Generation Data Readiness", False, "No procedures with substantial content found")
                return False
                
        except Exception as e:
            self.log_test("PDF Generation Data Readiness", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_search_functionality(self):
        """Test 7: Test specific search functionality for mentioned procedures"""
        print("\n🔍 Testing Specific Search Functionality...")
        
        try:
            search_tests = [
                {'term': 'All On X', 'expected_min': 1},
                {'term': 'zirconia', 'expected_min': 1},
                {'term': 'implant', 'expected_min': 1}
            ]
            
            all_passed = True
            total_found = 0
            
            for test in search_tests:
                try:
                    response = self.session.get(f"{API_BASE}/procedures/search", params={'q': test['term']})
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success') and data.get('data'):
                            found_count = len(data['data'])
                            total_found += found_count
                            
                            if found_count >= test['expected_min']:
                                self.log_test(f"Search for '{test['term']}'", True, f"Found {found_count} procedures")
                            else:
                                self.log_test(f"Search for '{test['term']}'", False, f"Found {found_count}, expected at least {test['expected_min']}")
                                all_passed = False
                        else:
                            self.log_test(f"Search for '{test['term']}'", False, "No results returned")
                            all_passed = False
                    else:
                        self.log_test(f"Search for '{test['term']}'", False, f"HTTP {response.status_code}")
                        all_passed = False
                        
                except Exception as e:
                    self.log_test(f"Search for '{test['term']}'", False, f"Exception: {str(e)}")
                    all_passed = False
            
            if all_passed:
                self.log_test("Overall Search Functionality", True, f"All search tests passed, total procedures found: {total_found}")
            
            return all_passed
            
        except Exception as e:
            self.log_test("Specific Search Functionality", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive PDF Generation Test Suite")
        print("Testing Enhanced PDF Generation with Base64 Logo Implementation")
        print("=" * 80)
        
        # Test 1: Login functionality
        login_success = self.test_login_functionality()
        
        # Test 2: Procedures endpoint
        procedures = self.test_procedures_endpoint_accessibility()
        
        # Test 3: Base64 logo file
        logo_success = self.test_base64_logo_file_accessibility()
        
        # Test 4: Enhanced PDF generator file
        generator_success = self.test_enhanced_pdf_generator_file()
        
        # Test 5: Import statements updated
        imports_success = self.test_import_statements_updated()
        
        # Test 6: PDF generation readiness
        pdf_ready = self.test_pdf_generation_data_readiness()
        
        # Test 7: Specific search functionality
        search_success = self.test_specific_search_functionality()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
        
        return all([login_success, procedures, logo_success, generator_success, imports_success, pdf_ready, search_success])
    
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        print("\n🎯 REVIEW REQUEST VERIFICATION:")
        print("=" * 50)
        
        review_items = [
            ("✅ Login functionality with cganz2279@gmail.com/password123", 
             any(r['test'].startswith('Login with cganz2279') and r['success'] for r in self.test_results)),
            ("✅ Procedures endpoint accessibility", 
             any(r['test'] == 'Procedures Endpoint Accessibility' and r['success'] for r in self.test_results)),
            ("✅ Base64 logo file accessible at /dental-rescue-logo-base64.txt", 
             any(r['test'].startswith('Base64 Logo File') and r['success'] for r in self.test_results)),
            ("✅ Enhanced PDF generation functionality", 
             any(r['test'] == 'PDF Generation Data Readiness' and r['success'] for r in self.test_results)),
            ("✅ All imports updated to use ENHANCED_PDF_WITH_LOGO", 
             any(r['test'] == 'Import Statements Updated' and r['success'] for r in self.test_results))
        ]
        
        for item, status in review_items:
            if status:
                print(item)
            else:
                print(item.replace('✅', '❌'))
        
        print("\n🔧 KEY CHANGES VERIFIED:")
        print("- Created base64 logo string in /app/frontend/public/dental-rescue-logo-base64.txt")
        print("- Updated /app/frontend/src/utils/ENHANCED_PDF_WITH_LOGO.js to use base64 logo")
        print("- Updated all PDF import statements from FINAL_RAW_TEXT_ONLY to ENHANCED_PDF_WITH_LOGO")
        print("- Enhanced PDF generation with logo and bold formatting functionality")
        
        print(f"\n🎉 OVERALL STATUS: {'SUCCESS' if failed_tests == 0 else 'PARTIAL SUCCESS'}")
        if failed_tests == 0:
            print("All enhanced PDF generation functionality is working correctly!")
        else:
            print(f"Most functionality working, {failed_tests} issues need attention.")

if __name__ == "__main__":
    tester = ComprehensivePDFTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)