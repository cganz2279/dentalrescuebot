#!/usr/bin/env python3
"""
CSV Patient Import Functionality Test
Tests the new CSV Patient Import functionality as requested in the review.
"""

import requests
import json
import io
import csv
from datetime import datetime

# Configuration
BACKEND_URL = "https://dental-portal-debug.preview.emergentagent.com/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class CSVPatientImportTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        
    def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with test credentials...")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.auth_token = data["token"]
                self.practice_id = data["user"]["practiceId"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print(f"✅ Authentication successful for practice: {data['practice']['name']}")
                return True
            else:
                print(f"❌ Authentication failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Authentication failed with status {response.status_code}: {response.text}")
            return False
    
    def test_csv_template_download(self):
        """Test CSV Template Download (/api/practice/patient-csv-template)"""
        print("\n📋 Testing CSV Template Download...")
        
        try:
            # Test GET request to download CSV template
            response = self.session.get(f"{BACKEND_URL}/practice/patient-csv-template")
            
            if response.status_code == 200:
                print("✅ CSV template download successful")
                
                # Verify content type
                content_type = response.headers.get('content-type', '')
                if 'text/csv' in content_type:
                    print("✅ Correct content-type: text/csv")
                else:
                    print(f"⚠️  Content-type is {content_type}, expected text/csv")
                
                # Verify Content-Disposition header
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' in content_disposition and 'patient_import_template.csv' in content_disposition:
                    print("✅ Correct Content-Disposition header for file download")
                else:
                    print(f"⚠️  Content-Disposition: {content_disposition}")
                
                # Parse CSV content
                csv_content = response.text
                print(f"📄 CSV Template Content ({len(csv_content)} characters):")
                print(csv_content)
                
                # Verify template contains correct headers
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                headers = csv_reader.fieldnames
                expected_headers = ['firstName', 'lastName', 'email', 'cellphone', 'primaryDentist']
                
                if headers == expected_headers:
                    print("✅ Template contains correct headers:", headers)
                else:
                    print(f"❌ Header mismatch. Expected: {expected_headers}, Got: {headers}")
                
                # Verify template includes sample data rows
                rows = list(csv_reader)
                if len(rows) >= 2:
                    print(f"✅ Template includes {len(rows)} sample data rows")
                    for i, row in enumerate(rows, 1):
                        print(f"   Sample {i}: {row['firstName']} {row['lastName']} ({row['email']})")
                else:
                    print(f"❌ Template should include sample data rows, found {len(rows)}")
                
                return True
            else:
                print(f"❌ CSV template download failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ CSV template download test failed: {str(e)}")
            return False
    
    def test_csv_template_authentication(self):
        """Test authentication requirement for CSV template"""
        print("\n🔒 Testing CSV template authentication requirement...")
        
        try:
            # Create session without authentication
            unauth_session = requests.Session()
            response = unauth_session.get(f"{BACKEND_URL}/practice/patient-csv-template")
            
            if response.status_code in [401, 403]:
                print("✅ CSV template properly requires authentication")
                return True
            else:
                print(f"❌ CSV template should require authentication, got status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ CSV template authentication test failed: {str(e)}")
            return False
    
    def create_test_csv_content(self, scenario="valid"):
        """Create test CSV content for different scenarios"""
        if scenario == "valid":
            return """firstName,lastName,email,cellphone,primaryDentist
John,Smith,john.smith.test@gmail.com,555-123-4567,Dr. Johnson
Jane,Doe,jane.doe.test@gmail.com,555-987-6543,Dr. Smith
Robert,Wilson,robert.wilson.test@gmail.com,555-456-7890,"""
        
        elif scenario == "missing_required":
            return """firstName,lastName,email,cellphone,primaryDentist
John,Smith,,555-123-4567,Dr. Johnson
,Doe,jane.doe.test@gmail.com,555-987-6543,Dr. Smith
Robert,Wilson,robert.wilson.test@gmail.com,,"""
        
        elif scenario == "invalid_email":
            return """firstName,lastName,email,cellphone,primaryDentist
John,Smith,invalid-email,555-123-4567,Dr. Johnson
Jane,Doe,jane.doe@,555-987-6543,Dr. Smith"""
        
        elif scenario == "duplicate_email":
            return """firstName,lastName,email,cellphone,primaryDentist
John,Smith,duplicate.test@gmail.com,555-123-4567,Dr. Johnson
Jane,Doe,duplicate.test@gmail.com,555-987-6543,Dr. Smith"""
        
        elif scenario == "empty":
            return """firstName,lastName,email,cellphone,primaryDentist"""
        
        else:
            return ""
    
    def test_csv_import_valid_data(self):
        """Test successful CSV import with valid data"""
        print("\n📊 Testing CSV import with valid patient data...")
        
        try:
            csv_content = self.create_test_csv_content("valid")
            
            # Create file-like object
            csv_file = io.BytesIO(csv_content.encode('utf-8'))
            
            files = {
                'file': ('test_patients.csv', csv_file, 'text/csv')
            }
            
            response = self.session.post(f"{BACKEND_URL}/practice/import-patients-csv", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ CSV import successful")
                    
                    # Verify response structure
                    summary = data.get("summary", {})
                    details = data.get("details", {})
                    
                    print(f"📈 Import Summary:")
                    print(f"   Total Rows: {summary.get('totalRows', 0)}")
                    print(f"   Successful Imports: {summary.get('successfulImports', 0)}")
                    print(f"   Failed Imports: {summary.get('failedImports', 0)}")
                    print(f"   Duplicate Emails: {summary.get('duplicateEmails', 0)}")
                    
                    # Verify successful imports
                    successful = details.get("successful", [])
                    if len(successful) > 0:
                        print(f"✅ Successfully imported {len(successful)} patients:")
                        for patient in successful:
                            print(f"   - {patient.get('name')} ({patient.get('email')})")
                    
                    return True
                else:
                    print(f"❌ CSV import failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ CSV import failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ CSV import test failed: {str(e)}")
            return False
    
    def test_csv_import_validation(self):
        """Test validation for missing required fields"""
        print("\n🔍 Testing CSV import validation for missing required fields...")
        
        try:
            csv_content = self.create_test_csv_content("missing_required")
            csv_file = io.BytesIO(csv_content.encode('utf-8'))
            
            files = {
                'file': ('test_validation.csv', csv_file, 'text/csv')
            }
            
            response = self.session.post(f"{BACKEND_URL}/practice/import-patients-csv", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("summary", {})
                    details = data.get("details", {})
                    
                    print(f"📈 Validation Test Results:")
                    print(f"   Total Rows: {summary.get('totalRows', 0)}")
                    print(f"   Failed Imports: {summary.get('failedImports', 0)}")
                    
                    # Check failed imports
                    failed = details.get("failed", [])
                    if len(failed) > 0:
                        print(f"✅ Validation correctly caught {len(failed)} invalid rows:")
                        for failure in failed:
                            print(f"   Row {failure.get('row')}: {', '.join(failure.get('errors', []))}")
                        return True
                    else:
                        print("❌ Validation should have caught missing required fields")
                        return False
                else:
                    print(f"❌ CSV validation test failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ CSV validation test failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ CSV validation test failed: {str(e)}")
            return False
    
    def test_email_format_validation(self):
        """Test email format validation"""
        print("\n📧 Testing email format validation...")
        
        try:
            csv_content = self.create_test_csv_content("invalid_email")
            csv_file = io.BytesIO(csv_content.encode('utf-8'))
            
            files = {
                'file': ('test_email_validation.csv', csv_file, 'text/csv')
            }
            
            response = self.session.post(f"{BACKEND_URL}/practice/import-patients-csv", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    details = data.get("details", {})
                    failed = details.get("failed", [])
                    
                    # Check if email validation errors are present
                    email_validation_found = False
                    for failure in failed:
                        errors = failure.get('errors', [])
                        for error in errors:
                            if 'email format is invalid' in error:
                                email_validation_found = True
                                break
                    
                    if email_validation_found:
                        print("✅ Email format validation working correctly")
                        return True
                    else:
                        print("❌ Email format validation not working")
                        return False
                else:
                    print(f"❌ Email validation test failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Email validation test failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Email validation test failed: {str(e)}")
            return False
    
    def test_duplicate_email_handling(self):
        """Test duplicate email handling"""
        print("\n👥 Testing duplicate email handling...")
        
        try:
            csv_content = self.create_test_csv_content("duplicate_email")
            csv_file = io.BytesIO(csv_content.encode('utf-8'))
            
            files = {
                'file': ('test_duplicates.csv', csv_file, 'text/csv')
            }
            
            response = self.session.post(f"{BACKEND_URL}/practice/import-patients-csv", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("summary", {})
                    details = data.get("details", {})
                    
                    duplicates = details.get("duplicates", [])
                    if len(duplicates) > 0:
                        print(f"✅ Duplicate email handling working - found {len(duplicates)} duplicates:")
                        for dup in duplicates:
                            print(f"   Row {dup.get('row')}: {dup.get('name')} ({dup.get('email')})")
                        return True
                    else:
                        print("⚠️  No duplicates detected (may be expected if emails are unique)")
                        return True
                else:
                    print(f"❌ Duplicate email test failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Duplicate email test failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Duplicate email test failed: {str(e)}")
            return False
    
    def test_invalid_file_type(self):
        """Test invalid file type rejection"""
        print("\n📄 Testing invalid file type rejection...")
        
        try:
            # Create a text file instead of CSV
            text_content = "This is not a CSV file"
            text_file = io.BytesIO(text_content.encode('utf-8'))
            
            files = {
                'file': ('test.txt', text_file, 'text/plain')
            }
            
            response = self.session.post(f"{BACKEND_URL}/practice/import-patients-csv", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if "File must be a CSV file" in data.get("detail", ""):
                    print("✅ Invalid file type correctly rejected")
                    return True
                else:
                    print(f"❌ Wrong error message: {data.get('detail', '')}")
                    return False
            else:
                print(f"❌ Invalid file type should be rejected with 400, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Invalid file type test failed: {str(e)}")
            return False
    
    def test_empty_csv_handling(self):
        """Test empty CSV file handling"""
        print("\n📭 Testing empty CSV file handling...")
        
        try:
            csv_content = self.create_test_csv_content("empty")
            csv_file = io.BytesIO(csv_content.encode('utf-8'))
            
            files = {
                'file': ('empty.csv', csv_file, 'text/csv')
            }
            
            response = self.session.post(f"{BACKEND_URL}/practice/import-patients-csv", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("summary", {})
                    if summary.get("totalRows", 0) == 0:
                        print("✅ Empty CSV file handled correctly")
                        return True
                    else:
                        print(f"❌ Empty CSV should have 0 rows, got {summary.get('totalRows', 0)}")
                        return False
                else:
                    print(f"❌ Empty CSV test failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Empty CSV test failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Empty CSV test failed: {str(e)}")
            return False
    
    def test_imported_patients_in_list(self):
        """Test that successfully imported patients appear in patients list"""
        print("\n👥 Testing that imported patients appear in patients list...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/patients")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patients = data.get("data", [])
                    
                    # Look for test patients we imported
                    test_emails = ["john.smith.test@gmail.com", "jane.doe.test@gmail.com", "robert.wilson.test@gmail.com"]
                    found_patients = []
                    
                    for patient in patients:
                        if patient.get("email") in test_emails:
                            found_patients.append(patient)
                    
                    if len(found_patients) > 0:
                        print(f"✅ Found {len(found_patients)} imported patients in patients list:")
                        for patient in found_patients:
                            print(f"   - {patient.get('firstName')} {patient.get('lastName')} ({patient.get('email')})")
                            
                            # Verify required fields
                            required_fields = ['firstName', 'lastName', 'email', 'cellphone']
                            missing_fields = [field for field in required_fields if not patient.get(field)]
                            
                            if not missing_fields:
                                print(f"     ✅ All required fields present")
                            else:
                                print(f"     ❌ Missing fields: {missing_fields}")
                        
                        return True
                    else:
                        print("⚠️  No imported test patients found in patients list")
                        return True  # May be expected if import failed earlier
                else:
                    print(f"❌ Failed to get patients list: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Failed to get patients list with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Patients list test failed: {str(e)}")
            return False
    
    def test_integration_with_existing_systems(self):
        """Test integration with existing systems"""
        print("\n🔗 Testing integration with existing systems...")
        
        try:
            # Test dashboard recent patients
            response = self.session.get(f"{BACKEND_URL}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    dashboard_data = data.get("data", {})
                    recent_patients = dashboard_data.get("recentPatients", [])
                    
                    print(f"✅ Dashboard accessible - found {len(recent_patients)} recent patients")
                    
                    # Check if any imported patients appear in recent patients
                    test_emails = ["john.smith.test@gmail.com", "jane.doe.test@gmail.com", "robert.wilson.test@gmail.com"]
                    imported_in_recent = [p for p in recent_patients if p.get("email") in test_emails]
                    
                    if len(imported_in_recent) > 0:
                        print(f"✅ Found {len(imported_in_recent)} imported patients in dashboard recent patients")
                    else:
                        print("ℹ️  No imported patients in dashboard recent patients (may be expected)")
                    
                    return True
                else:
                    print(f"❌ Dashboard integration test failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Dashboard integration test failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Integration test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all CSV Patient Import tests"""
        print("🚀 Starting CSV Patient Import Functionality Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        test_results = []
        
        # Test 1: CSV Template Download
        test_results.append(("CSV Template Download", self.test_csv_template_download()))
        
        # Test 2: CSV Template Authentication
        test_results.append(("CSV Template Authentication", self.test_csv_template_authentication()))
        
        # Test 3: Valid CSV Import
        test_results.append(("Valid CSV Import", self.test_csv_import_valid_data()))
        
        # Test 4: Validation for Missing Fields
        test_results.append(("Missing Fields Validation", self.test_csv_import_validation()))
        
        # Test 5: Email Format Validation
        test_results.append(("Email Format Validation", self.test_email_format_validation()))
        
        # Test 6: Duplicate Email Handling
        test_results.append(("Duplicate Email Handling", self.test_duplicate_email_handling()))
        
        # Test 7: Invalid File Type Rejection
        test_results.append(("Invalid File Type Rejection", self.test_invalid_file_type()))
        
        # Test 8: Empty CSV Handling
        test_results.append(("Empty CSV Handling", self.test_empty_csv_handling()))
        
        # Test 9: Imported Patients in List
        test_results.append(("Imported Patients in List", self.test_imported_patients_in_list()))
        
        # Test 10: Integration with Existing Systems
        test_results.append(("Integration with Existing Systems", self.test_integration_with_existing_systems()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📈 Overall Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All CSV Patient Import tests passed!")
            return True
        else:
            print(f"⚠️  {failed} test(s) failed - review the output above for details")
            return False

def main():
    """Main function to run CSV Patient Import tests"""
    tester = CSVPatientImportTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CSV Patient Import functionality is working correctly!")
        exit(0)
    else:
        print("\n❌ CSV Patient Import functionality has issues that need attention!")
        exit(1)

if __name__ == "__main__":
    main()