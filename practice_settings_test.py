#!/usr/bin/env python3
"""
Practice Settings Backend Testing for Dental Post-Operative Care App
Tests Practice Settings functionality including officeHours and emergencyContact fields
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://careplan-builder.preview.emergentagent.com/api"

class PracticeSettingsTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.practice_id = None
        
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
    
    def test_practice_login(self):
        """Test practice admin login to get authentication token"""
        try:
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    user_info = data.get("user", {})
                    self.practice_id = user_info.get("practiceId")
                    self.log_test("Practice Admin Login", True, 
                                f"Logged in as {user_info.get('firstName', '')} {user_info.get('lastName', '')} (Practice ID: {self.practice_id})")
                    return True
                else:
                    self.log_test("Practice Admin Login", False, "Invalid response format")
                    return False
            else:
                self.log_test("Practice Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Practice Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_get_current_practice_info(self):
        """Test getting current practice information to see existing officeHours and emergencyContact"""
        if not self.auth_token:
            self.log_test("Get Current Practice Info", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    practice_data = data["data"].get("practice", {})
                    current_office_hours = practice_data.get("officeHours", "Not set")
                    current_emergency_contact = practice_data.get("emergencyContact", "Not set")
                    
                    self.log_test("Get Current Practice Info", True, 
                                f"Current Office Hours: '{current_office_hours}', Emergency Contact: '{current_emergency_contact}'")
                    return True
                else:
                    self.log_test("Get Current Practice Info", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Current Practice Info", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Current Practice Info", False, f"Exception: {str(e)}")
            return False

    def test_update_practice_office_hours_and_emergency_contact(self):
        """Test PUT /api/practice/update endpoint with officeHours and emergencyContact fields"""
        if not self.auth_token:
            self.log_test("Update Practice Settings", False, "No authentication token available")
            return False
            
        try:
            # Test data with realistic office hours and emergency contact
            update_data = {
                "officeHours": "Monday-Friday: 8:00 AM - 5:00 PM, Saturday: 9:00 AM - 2:00 PM",
                "emergencyContact": "(555) 123-4567"
            }
            
            response = self.session.put(f"{self.base_url}/practice/update", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Update Practice Settings", True, 
                                f"Successfully updated officeHours and emergencyContact")
                    return True
                else:
                    self.log_test("Update Practice Settings", False, "Invalid response format")
                    return False
            else:
                self.log_test("Update Practice Settings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Practice Settings", False, f"Exception: {str(e)}")
            return False

    def test_verify_practice_settings_stored(self):
        """Test that practice settings were properly stored in database"""
        if not self.auth_token:
            self.log_test("Verify Practice Settings Stored", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    practice_data = data["data"].get("practice", {})
                    stored_office_hours = practice_data.get("officeHours")
                    stored_emergency_contact = practice_data.get("emergencyContact")
                    
                    expected_office_hours = "Monday-Friday: 8:00 AM - 5:00 PM, Saturday: 9:00 AM - 2:00 PM"
                    expected_emergency_contact = "(555) 123-4567"
                    
                    if stored_office_hours == expected_office_hours and stored_emergency_contact == expected_emergency_contact:
                        self.log_test("Verify Practice Settings Stored", True, 
                                    f"Verified stored values - Office Hours: '{stored_office_hours}', Emergency Contact: '{stored_emergency_contact}'")
                        return True
                    else:
                        self.log_test("Verify Practice Settings Stored", False, 
                                    f"Mismatch - Expected Office Hours: '{expected_office_hours}', Got: '{stored_office_hours}'; Expected Emergency Contact: '{expected_emergency_contact}', Got: '{stored_emergency_contact}'")
                        return False
                else:
                    self.log_test("Verify Practice Settings Stored", False, "Invalid response format")
                    return False
            else:
                self.log_test("Verify Practice Settings Stored", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Practice Settings Stored", False, f"Exception: {str(e)}")
            return False

    def test_procedure_pdf_includes_practice_info(self):
        """Test GET /api/procedures/{id} endpoint to confirm it returns practice info including officeHours and emergencyContact for PDF generation"""
        if not self.auth_token:
            self.log_test("Procedure PDF Practice Info", False, "No authentication token available")
            return False
            
        try:
            # Test with root-canal-therapy procedure
            response = self.session.get(f"{self.base_url}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    
                    # Check if practice information is included
                    practice_name = procedure.get("practiceName")
                    practice_phone = procedure.get("practicePhone")
                    practice_office_hours = procedure.get("practiceOfficeHours")
                    practice_emergency_contact = procedure.get("practiceEmergencyContact")
                    
                    if practice_office_hours and practice_emergency_contact:
                        self.log_test("Procedure PDF Practice Info", True, 
                                    f"Practice info included - Name: '{practice_name}', Phone: '{practice_phone}', Office Hours: '{practice_office_hours}', Emergency Contact: '{practice_emergency_contact}'")
                        return True
                    else:
                        self.log_test("Procedure PDF Practice Info", False, 
                                    f"Missing practice info - Office Hours: '{practice_office_hours}', Emergency Contact: '{practice_emergency_contact}'")
                        return False
                else:
                    self.log_test("Procedure PDF Practice Info", False, "Invalid response format")
                    return False
            else:
                self.log_test("Procedure PDF Practice Info", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Procedure PDF Practice Info", False, f"Exception: {str(e)}")
            return False

    def test_update_with_various_office_hours_formats(self):
        """Test various office hours formats for data validation"""
        if not self.auth_token:
            self.log_test("Various Office Hours Formats", False, "No authentication token available")
            return False
            
        test_formats = [
            {
                "name": "24/7 Format",
                "officeHours": "24/7 Emergency Services Available",
                "emergencyContact": "(555) 999-8888"
            },
            {
                "name": "Compact Format", 
                "officeHours": "Mon-Fri 9-5, Sat 10-2",
                "emergencyContact": "555.123.4567"
            },
            {
                "name": "Extended Format",
                "officeHours": "Monday through Friday: 7:30 AM to 6:00 PM, Saturday: 8:00 AM to 1:00 PM, Sunday: Closed",
                "emergencyContact": "+1 (555) 123-4567 ext. 911"
            }
        ]
        
        all_passed = True
        
        for test_format in test_formats:
            try:
                update_data = {
                    "officeHours": test_format["officeHours"],
                    "emergencyContact": test_format["emergencyContact"]
                }
                
                response = self.session.put(f"{self.base_url}/practice/update", json=update_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        # Verify the data was stored
                        verify_response = self.session.get(f"{self.base_url}/practice/dashboard")
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            practice_data = verify_data["data"].get("practice", {})
                            stored_hours = practice_data.get("officeHours")
                            stored_contact = practice_data.get("emergencyContact")
                            
                            if stored_hours == test_format["officeHours"] and stored_contact == test_format["emergencyContact"]:
                                self.log_test(f"Office Hours Format - {test_format['name']}", True, 
                                            f"Successfully stored: '{stored_hours}' and '{stored_contact}'")
                            else:
                                self.log_test(f"Office Hours Format - {test_format['name']}", False, 
                                            f"Storage mismatch - Expected: '{test_format['officeHours']}', Got: '{stored_hours}'")
                                all_passed = False
                        else:
                            self.log_test(f"Office Hours Format - {test_format['name']}", False, "Could not verify storage")
                            all_passed = False
                    else:
                        self.log_test(f"Office Hours Format - {test_format['name']}", False, "Update failed")
                        all_passed = False
                else:
                    self.log_test(f"Office Hours Format - {test_format['name']}", False, f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Office Hours Format - {test_format['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_update_with_various_emergency_contact_formats(self):
        """Test various emergency contact formats for data validation"""
        if not self.auth_token:
            self.log_test("Various Emergency Contact Formats", False, "No authentication token available")
            return False
            
        test_formats = [
            {
                "name": "Standard Format",
                "emergencyContact": "(555) 123-4567"
            },
            {
                "name": "International Format",
                "emergencyContact": "+1-555-123-4567"
            },
            {
                "name": "Extension Format",
                "emergencyContact": "(555) 123-4567 ext. 911"
            },
            {
                "name": "Multiple Numbers",
                "emergencyContact": "Office: (555) 123-4567, After Hours: (555) 987-6543"
            },
            {
                "name": "Text Instructions",
                "emergencyContact": "Call (555) 123-4567 for emergencies. If no answer, go to City Hospital ER."
            }
        ]
        
        all_passed = True
        
        for test_format in test_formats:
            try:
                update_data = {
                    "officeHours": "Monday-Friday: 8:00 AM - 5:00 PM",  # Keep consistent
                    "emergencyContact": test_format["emergencyContact"]
                }
                
                response = self.session.put(f"{self.base_url}/practice/update", json=update_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        # Verify the data was stored
                        verify_response = self.session.get(f"{self.base_url}/practice/dashboard")
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            practice_data = verify_data["data"].get("practice", {})
                            stored_contact = practice_data.get("emergencyContact")
                            
                            if stored_contact == test_format["emergencyContact"]:
                                self.log_test(f"Emergency Contact Format - {test_format['name']}", True, 
                                            f"Successfully stored: '{stored_contact}'")
                            else:
                                self.log_test(f"Emergency Contact Format - {test_format['name']}", False, 
                                            f"Storage mismatch - Expected: '{test_format['emergencyContact']}', Got: '{stored_contact}'")
                                all_passed = False
                        else:
                            self.log_test(f"Emergency Contact Format - {test_format['name']}", False, "Could not verify storage")
                            all_passed = False
                    else:
                        self.log_test(f"Emergency Contact Format - {test_format['name']}", False, "Update failed")
                        all_passed = False
                else:
                    self.log_test(f"Emergency Contact Format - {test_format['name']}", False, f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Emergency Contact Format - {test_format['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_edge_cases_and_validation(self):
        """Test edge cases and validation for practice settings"""
        if not self.auth_token:
            self.log_test("Edge Cases and Validation", False, "No authentication token available")
            return False
            
        edge_cases = [
            {
                "name": "Empty Strings",
                "data": {"officeHours": "", "emergencyContact": ""},
                "should_succeed": True
            },
            {
                "name": "Null Values",
                "data": {"officeHours": None, "emergencyContact": None},
                "should_succeed": True
            },
            {
                "name": "Very Long Office Hours",
                "data": {
                    "officeHours": "Monday: 8:00 AM - 5:00 PM, Tuesday: 8:00 AM - 5:00 PM, Wednesday: 8:00 AM - 5:00 PM, Thursday: 8:00 AM - 5:00 PM, Friday: 8:00 AM - 5:00 PM, Saturday: 9:00 AM - 2:00 PM, Sunday: Closed. Special holiday hours may apply. Please call ahead during holiday seasons.",
                    "emergencyContact": "(555) 123-4567"
                },
                "should_succeed": True
            },
            {
                "name": "Very Long Emergency Contact",
                "data": {
                    "officeHours": "Monday-Friday: 8:00 AM - 5:00 PM",
                    "emergencyContact": "Primary Emergency: (555) 123-4567, Secondary Emergency: (555) 987-6543, After Hours Answering Service: (555) 111-2222, Weekend Emergency: (555) 333-4444. For life-threatening emergencies, call 911 immediately."
                },
                "should_succeed": True
            },
            {
                "name": "Special Characters",
                "data": {
                    "officeHours": "Mon-Fri: 8:00 AM - 5:00 PM (EST/EDT) • Sat: 9:00 AM - 2:00 PM",
                    "emergencyContact": "📞 (555) 123-4567 • 🚨 Emergency Line"
                },
                "should_succeed": True
            }
        ]
        
        all_passed = True
        
        for case in edge_cases:
            try:
                response = self.session.put(f"{self.base_url}/practice/update", json=case["data"])
                
                if case["should_succeed"]:
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            self.log_test(f"Edge Case - {case['name']}", True, "Successfully handled edge case")
                        else:
                            self.log_test(f"Edge Case - {case['name']}", False, "Update failed despite expected success")
                            all_passed = False
                    else:
                        self.log_test(f"Edge Case - {case['name']}", False, f"Unexpected status: {response.status_code}")
                        all_passed = False
                else:
                    if response.status_code != 200:
                        self.log_test(f"Edge Case - {case['name']}", True, f"Properly rejected with status: {response.status_code}")
                    else:
                        self.log_test(f"Edge Case - {case['name']}", False, "Should have been rejected but was accepted")
                        all_passed = False
                        
            except Exception as e:
                self.log_test(f"Edge Case - {case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_unauthorized_access(self):
        """Test that practice settings endpoints require proper authentication"""
        try:
            # Test without token
            session_no_auth = requests.Session()
            
            update_data = {
                "officeHours": "Test Hours",
                "emergencyContact": "Test Contact"
            }
            
            response = session_no_auth.put(f"{self.base_url}/practice/update", json=update_data)
            
            if response.status_code in [401, 403]:  # Unauthorized or Forbidden
                self.log_test("Unauthorized Access Protection", True, 
                            f"Properly blocked unauthorized access with status: {response.status_code}")
                return True
            else:
                self.log_test("Unauthorized Access Protection", False, 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Access Protection", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all practice settings tests"""
        print("🏥 PRACTICE SETTINGS BACKEND TESTING")
        print("=" * 50)
        
        # Authentication test
        if not self.test_practice_login():
            print("❌ Authentication failed - cannot proceed with other tests")
            return False
        
        # Core functionality tests
        tests = [
            self.test_get_current_practice_info,
            self.test_update_practice_office_hours_and_emergency_contact,
            self.test_verify_practice_settings_stored,
            self.test_procedure_pdf_includes_practice_info,
            self.test_update_with_various_office_hours_formats,
            self.test_update_with_various_emergency_contact_formats,
            self.test_edge_cases_and_validation,
            self.test_unauthorized_access
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 PRACTICE SETTINGS TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL PRACTICE SETTINGS TESTS PASSED!")
            return True
        else:
            print(f"❌ {total - passed} tests failed")
            return False

def main():
    """Main function to run practice settings tests"""
    tester = PracticeSettingsTester(BACKEND_URL)
    
    print(f"🔗 Testing backend at: {BACKEND_URL}")
    print(f"🎯 Focus: Practice Settings (officeHours & emergencyContact)")
    print()
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Practice Settings backend functionality is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 Practice Settings backend has issues that need attention!")
        sys.exit(1)

if __name__ == "__main__":
    main()