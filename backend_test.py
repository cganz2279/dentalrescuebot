#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Correspondence Export Functionality
Testing the new POST /api/practice/export-correspondence endpoint
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import io
import csv
import openpyxl

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class CorrespondenceExportTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.practice_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate(self):
        """Authenticate with the test account"""
        print("🔐 Authenticating with test account...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.practice_id = data.get("practiceId")
                
                self.log_test(
                    "Authentication", 
                    True, 
                    f"Token obtained, Practice ID: {self.practice_id}"
                )
                return True
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_export_all_data(self):
        """Test export with no date filters (export all data)"""
        print("\n📊 Testing export with no date filters...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                # Check if it's a CSV response
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                if 'text/csv' in content_type and 'attachment' in content_disposition:
                    # Try to parse CSV content
                    csv_content = response.text
                    csv_reader = csv.reader(io.StringIO(csv_content))
                    rows = list(csv_reader)
                    
                    self.log_test(
                        "Export All Data (CSV)", 
                        True, 
                        f"CSV file generated with {len(rows)} rows (including header)"
                    )
                    
                    # Verify CSV headers
                    if rows:
                        headers = rows[0]
                        expected_headers = [
                            "patient_name", "patient_email", "date_sent", "procedure_name", 
                            "doctor_name", "communication_type", "status", "notes"
                        ]
                        
                        headers_match = all(header in headers for header in expected_headers)
                        self.log_test(
                            "CSV Headers Validation", 
                            headers_match, 
                            f"Headers: {headers}"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Export All Data (CSV)", 
                        False, 
                        f"Unexpected content type: {content_type}"
                    )
                    return False
            else:
                self.log_test(
                    "Export All Data (CSV)", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Export All Data (CSV)", False, f"Exception: {str(e)}")
            return False
    
    def test_export_with_start_date(self):
        """Test export with start_date filter only"""
        print("\n📅 Testing export with start_date filter...")
        
        try:
            # Use a date from 30 days ago
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "start_date": start_date,
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'text/csv' in content_type:
                    self.log_test(
                        "Export with Start Date", 
                        True, 
                        f"CSV export successful with start_date: {start_date}"
                    )
                    return True
                else:
                    self.log_test(
                        "Export with Start Date", 
                        False, 
                        f"Unexpected content type: {content_type}"
                    )
                    return False
            else:
                self.log_test(
                    "Export with Start Date", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Export with Start Date", False, f"Exception: {str(e)}")
            return False
    
    def test_export_with_date_range(self):
        """Test export with both start_date and end_date filters"""
        print("\n📅 Testing export with date range filters...")
        
        try:
            # Use a date range from 30 days ago to 7 days ago
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "start_date": start_date,
                    "end_date": end_date,
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'text/csv' in content_type:
                    self.log_test(
                        "Export with Date Range", 
                        True, 
                        f"CSV export successful with date range: {start_date} to {end_date}"
                    )
                    return True
                else:
                    self.log_test(
                        "Export with Date Range", 
                        False, 
                        f"Unexpected content type: {content_type}"
                    )
                    return False
            else:
                self.log_test(
                    "Export with Date Range", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Export with Date Range", False, f"Exception: {str(e)}")
            return False
    
    def test_csv_format(self):
        """Test CSV format export"""
        print("\n📄 Testing CSV format export...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                # Verify CSV content type
                csv_content_valid = 'text/csv' in content_type
                
                # Verify filename in Content-Disposition header
                filename_valid = 'correspondence_export_' in content_disposition and '.csv' in content_disposition
                
                # Try to parse CSV content
                csv_parseable = False
                try:
                    csv_content = response.text
                    csv_reader = csv.reader(io.StringIO(csv_content))
                    rows = list(csv_reader)
                    csv_parseable = len(rows) >= 1  # At least header row
                except:
                    pass
                
                success = csv_content_valid and filename_valid and csv_parseable
                
                self.log_test(
                    "CSV Format Export", 
                    success, 
                    f"Content-Type: {content_type}, Filename valid: {filename_valid}, Parseable: {csv_parseable}"
                )
                return success
            else:
                self.log_test(
                    "CSV Format Export", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("CSV Format Export", False, f"Exception: {str(e)}")
            return False
    
    def test_excel_format(self):
        """Test Excel format export"""
        print("\n📊 Testing Excel format export...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "excel"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                # Verify Excel content type
                excel_content_valid = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type
                
                # Verify filename in Content-Disposition header
                filename_valid = 'correspondence_export_' in content_disposition and '.xlsx' in content_disposition
                
                # Try to parse Excel content
                excel_parseable = False
                try:
                    excel_content = response.content
                    workbook = openpyxl.load_workbook(io.BytesIO(excel_content))
                    worksheet = workbook.active
                    excel_parseable = worksheet.max_row >= 1  # At least header row
                except:
                    pass
                
                success = excel_content_valid and filename_valid and excel_parseable
                
                self.log_test(
                    "Excel Format Export", 
                    success, 
                    f"Content-Type valid: {excel_content_valid}, Filename valid: {filename_valid}, Parseable: {excel_parseable}"
                )
                return success
            else:
                self.log_test(
                    "Excel Format Export", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Excel Format Export", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_required(self):
        """Test that JWT token authentication is required"""
        print("\n🔒 Testing authentication requirement...")
        
        try:
            # Test without authentication token
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "csv"
                },
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 401 or 403
            auth_required = response.status_code in [401, 403]
            
            self.log_test(
                "Authentication Required", 
                auth_required, 
                f"Status without token: {response.status_code}"
            )
            return auth_required
            
        except Exception as e:
            self.log_test("Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_token(self):
        """Test with invalid JWT token"""
        print("\n🔒 Testing invalid token handling...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "csv"
                },
                headers={
                    "Authorization": "Bearer invalid_token_here",
                    "Content-Type": "application/json"
                }
            )
            
            # Should return 401
            invalid_token_handled = response.status_code == 401
            
            self.log_test(
                "Invalid Token Handling", 
                invalid_token_handled, 
                f"Status with invalid token: {response.status_code}"
            )
            return invalid_token_handled
            
        except Exception as e:
            self.log_test("Invalid Token Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_practice_admin_role(self):
        """Test that practice_admin role has access"""
        print("\n👤 Testing practice_admin role access...")
        
        # This test uses the authenticated user (cganz2279@gmail.com) which should have practice_admin role
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            # Should return 200 (success) for practice_admin
            admin_access = response.status_code == 200
            
            self.log_test(
                "Practice Admin Role Access", 
                admin_access, 
                f"Status for practice_admin: {response.status_code}"
            )
            return admin_access
            
        except Exception as e:
            self.log_test("Practice Admin Role Access", False, f"Exception: {str(e)}")
            return False
    
    def test_data_fields_validation(self):
        """Test that exported data includes all requested fields"""
        print("\n📋 Testing data fields validation...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                csv_content = response.text
                csv_reader = csv.reader(io.StringIO(csv_content))
                rows = list(csv_reader)
                
                if rows:
                    headers = rows[0]
                    
                    # Check for all required fields
                    required_fields = [
                        "patient_name",
                        "patient_email", 
                        "date_sent",
                        "procedure_name",
                        "doctor_name",
                        "communication_type",
                        "status",
                        "notes"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in headers]
                    
                    fields_complete = len(missing_fields) == 0
                    
                    self.log_test(
                        "Data Fields Validation", 
                        fields_complete, 
                        f"Missing fields: {missing_fields}" if missing_fields else "All required fields present"
                    )
                    return fields_complete
                else:
                    self.log_test("Data Fields Validation", False, "No data rows found")
                    return False
            else:
                self.log_test(
                    "Data Fields Validation", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Data Fields Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_realistic_practice_data(self):
        """Test with realistic practice data using existing test account"""
        print("\n🏥 Testing with realistic practice data...")
        
        try:
            # First, get dashboard data to verify we have practice data
            dashboard_response = self.session.get(
                f"{BACKEND_URL}/api/practice/dashboard",
                headers=self.get_auth_headers()
            )
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                practice_name = dashboard_data.get("data", {}).get("practice", {}).get("name", "Unknown")
                
                # Now test the export
                response = self.session.post(
                    f"{BACKEND_URL}/api/practice/export-correspondence",
                    json={
                        "format": "csv"
                    },
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    self.log_test(
                        "Realistic Practice Data Test", 
                        True, 
                        f"Export successful for practice: {practice_name}"
                    )
                    return True
                else:
                    self.log_test(
                        "Realistic Practice Data Test", 
                        False, 
                        f"Export failed with status: {response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Realistic Practice Data Test", 
                    False, 
                    f"Dashboard access failed: {dashboard_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Realistic Practice Data Test", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_date_format(self):
        """Test error handling for invalid date formats"""
        print("\n❌ Testing invalid date format handling...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/practice/export-correspondence",
                json={
                    "start_date": "invalid-date-format",
                    "format": "csv"
                },
                headers=self.get_auth_headers()
            )
            
            # Should return 400 for invalid date format
            error_handled = response.status_code == 400
            
            self.log_test(
                "Invalid Date Format Handling", 
                error_handled, 
                f"Status for invalid date: {response.status_code}"
            )
            return error_handled
            
        except Exception as e:
            self.log_test("Invalid Date Format Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all correspondence export tests"""
        print("🚀 Starting Correspondence Export Functionality Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        tests = [
            self.test_export_all_data,
            self.test_export_with_start_date,
            self.test_export_with_date_range,
            self.test_csv_format,
            self.test_excel_format,
            self.test_authentication_required,
            self.test_invalid_token,
            self.test_practice_admin_role,
            self.test_data_fields_validation,
            self.test_realistic_practice_data,
            self.test_invalid_date_format
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CORRESPONDENCE EXPORT TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Correspondence export functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
            return False

def main():
    """Main test execution"""
    tester = CorrespondenceExportTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()