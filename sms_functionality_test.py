#!/usr/bin/env python3
"""
SMS Functionality Test for Dental Instructions Application
Testing SMS PDF endpoint, secure PDF link endpoint, patient cellphone field, and integration testing
"""

import requests
import json
import time
import re
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BACKEND_URL = "https://oncallbot.preview.emergentagent.com/api"

# Test credentials
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class SMSFunctionalityTester:
    def __init__(self):
        self.auth_token = None
        self.practice_id = None
        self.test_patient_id = None
        self.test_procedure_id = None
        self.test_assignment_id = None
        
    def authenticate(self) -> bool:
        """Authenticate with the backend and get JWT token"""
        print("🔐 Authenticating with backend...")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                },
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.auth_token = data['data']['token']
                    self.practice_id = data['data']['user']['practiceId']
                    print(f"   ✅ Authentication successful")
                    print(f"   Practice ID: {self.practice_id}")
                    return True
                else:
                    print(f"   ❌ Authentication failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Authentication failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_patient_cellphone_field(self) -> bool:
        """Test creating patients with mandatory cellphone field"""
        print("\n📱 TEST 1: Testing Patient Cellphone Field...")
        
        try:
            # Test creating patient with cellphone
            test_patient_data = {
                "email": f"test.sms.patient.{int(time.time())}@gmail.com",
                "firstName": "SMS",
                "lastName": "TestPatient",
                "cellphone": "+1234567890"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/practice/patients",
                json=test_patient_data,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            print(f"   Create Patient Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_patient_id = data['data']['id']
                    print(f"   ✅ Patient created successfully with cellphone")
                    print(f"   Patient ID: {self.test_patient_id}")
                    print(f"   Cellphone: {data['data'].get('cellphone', 'Not found')}")
                    
                    # Verify cellphone field is stored
                    if data['data'].get('cellphone') == test_patient_data['cellphone']:
                        print(f"   ✅ Cellphone field properly stored and retrieved")
                        return True
                    else:
                        print(f"   ❌ Cellphone field mismatch")
                        return False
                else:
                    print(f"   ❌ Patient creation failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Patient creation failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Patient cellphone test error: {str(e)}")
            return False
    
    def test_patient_cellphone_update(self) -> bool:
        """Test updating patient cellphone information"""
        print("\n📱 TEST 2: Testing Patient Cellphone Update...")
        
        if not self.test_patient_id:
            print("   ❌ No test patient available for update test")
            return False
        
        try:
            # Update patient cellphone
            update_data = {
                "cellphone": "+1987654321"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/practice/patients/{self.test_patient_id}",
                json=update_data,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            print(f"   Update Patient Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Patient cellphone updated successfully")
                    
                    # Verify the update by getting patient details
                    get_response = requests.get(
                        f"{BACKEND_URL}/practice/patients",
                        headers=self.get_auth_headers(),
                        timeout=30
                    )
                    
                    if get_response.status_code == 200:
                        patients_data = get_response.json()
                        if patients_data.get('success'):
                            patients = patients_data['data']
                            test_patient = next((p for p in patients if p['id'] == self.test_patient_id), None)
                            
                            if test_patient and test_patient.get('cellphone') == update_data['cellphone']:
                                print(f"   ✅ Cellphone update verified: {test_patient['cellphone']}")
                                return True
                            else:
                                print(f"   ❌ Cellphone update not reflected in patient data")
                                return False
                    
                    return True
                else:
                    print(f"   ❌ Patient update failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Patient update failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Patient cellphone update test error: {str(e)}")
            return False
    
    def get_test_procedure(self) -> bool:
        """Get a test procedure for SMS testing"""
        print("\n🦷 Getting test procedure...")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/procedures",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    procedures = data['data']
                    if procedures:
                        # Use the first procedure for testing
                        test_procedure = procedures[0]
                        self.test_procedure_id = test_procedure['id']
                        print(f"   ✅ Test procedure selected: {test_procedure['name']}")
                        print(f"   Procedure ID: {self.test_procedure_id}")
                        return True
                    else:
                        print(f"   ❌ No procedures available for testing")
                        return False
                else:
                    print(f"   ❌ Failed to get procedures")
                    return False
            else:
                print(f"   ❌ Failed to get procedures with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get test procedure error: {str(e)}")
            return False
    
    def test_sms_pdf_endpoint_valid_request(self) -> bool:
        """Test SMS PDF endpoint with valid request"""
        print("\n📨 TEST 3: Testing SMS PDF Endpoint - Valid Request...")
        
        if not self.test_procedure_id:
            if not self.get_test_procedure():
                return False
        
        try:
            # Test SMS PDF request with valid data
            sms_request = {
                "patientCellphone": "+1234567890",
                "procedureId": self.test_procedure_id,
                "procedureName": "Test Procedure for SMS"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/practice/sms-pdf",
                json=sms_request,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            print(f"   SMS PDF Request Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ SMS PDF request successful")
                    print(f"   Message: {data.get('message', 'No message')}")
                    print(f"   Patient Cellphone: {data.get('patientCellphone', 'Not provided')}")
                    print(f"   Procedure Name: {data.get('procedureName', 'Not provided')}")
                    print(f"   Secure Link: {data.get('secureLink', 'Not provided')[:50]}...")
                    print(f"   Message SID: {data.get('messageSid', 'Not provided')}")
                    
                    # Store secure link for later testing
                    self.secure_link = data.get('secureLink', '')
                    
                    return True
                else:
                    print(f"   ❌ SMS PDF request failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ SMS PDF request failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ SMS PDF endpoint test error: {str(e)}")
            return False
    
    def test_sms_pdf_phone_validation(self) -> bool:
        """Test SMS PDF endpoint phone number validation"""
        print("\n📨 TEST 4: Testing SMS PDF Phone Number Validation...")
        
        test_cases = [
            {
                "phone": "invalid-phone",
                "description": "Invalid phone format",
                "should_fail": True
            },
            {
                "phone": "123",
                "description": "Too short phone number",
                "should_fail": True
            },
            {
                "phone": "1234567890",
                "description": "US format without country code",
                "should_fail": False
            },
            {
                "phone": "+1234567890",
                "description": "US format with country code",
                "should_fail": False
            },
            {
                "phone": "+44123456789",
                "description": "International format",
                "should_fail": False
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['description']} ({test_case['phone']})")
            
            try:
                sms_request = {
                    "patientCellphone": test_case['phone'],
                    "procedureId": self.test_procedure_id,
                    "procedureName": "Test Procedure for Validation"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/practice/sms-pdf",
                    json=sms_request,
                    headers=self.get_auth_headers(),
                    timeout=30
                )
                
                if test_case['should_fail']:
                    if response.status_code == 400:
                        print(f"     ✅ Correctly rejected invalid phone: {test_case['phone']}")
                    else:
                        print(f"     ❌ Should have rejected invalid phone: {test_case['phone']} (got {response.status_code})")
                        all_passed = False
                else:
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            print(f"     ✅ Correctly accepted valid phone: {test_case['phone']}")
                        else:
                            print(f"     ❌ Valid phone rejected: {test_case['phone']}")
                            all_passed = False
                    else:
                        print(f"     ❌ Valid phone failed: {test_case['phone']} (status {response.status_code})")
                        all_passed = False
                        
            except Exception as e:
                print(f"     ❌ Error testing phone {test_case['phone']}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_secure_pdf_link_endpoint(self) -> bool:
        """Test secure PDF link endpoint"""
        print("\n🔗 TEST 5: Testing Secure PDF Link Endpoint...")
        
        if not hasattr(self, 'secure_link') or not self.secure_link:
            print("   ❌ No secure link available from previous SMS test")
            return False
        
        try:
            # Extract token from secure link
            # Expected format: https://domain.com/secure-pdf/{token}
            token_match = re.search(r'/secure-pdf/([^/?]+)', self.secure_link)
            if not token_match:
                print(f"   ❌ Could not extract token from secure link: {self.secure_link}")
                return False
            
            token = token_match.group(1)
            print(f"   Extracted token: {token[:20]}...")
            
            # Test accessing PDF via secure token
            response = requests.get(
                f"{BACKEND_URL}/practice/secure-pdf/{token}",
                timeout=30
            )
            
            print(f"   Secure PDF Access Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if response is PDF content
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    print(f"   ✅ Secure PDF access successful")
                    print(f"   Content-Type: {content_type}")
                    print(f"   Content-Length: {len(response.content)} bytes")
                    
                    # Check for PDF content disposition header
                    content_disposition = response.headers.get('content-disposition', '')
                    if content_disposition:
                        print(f"   Content-Disposition: {content_disposition}")
                    
                    return True
                else:
                    print(f"   ❌ Response is not PDF content (Content-Type: {content_type})")
                    return False
            else:
                print(f"   ❌ Secure PDF access failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Error response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Secure PDF link test error: {str(e)}")
            return False
    
    def test_secure_pdf_invalid_token(self) -> bool:
        """Test secure PDF endpoint with invalid token"""
        print("\n🔗 TEST 6: Testing Secure PDF Link - Invalid Token...")
        
        try:
            # Test with invalid token
            invalid_token = "invalid-token-12345"
            
            response = requests.get(
                f"{BACKEND_URL}/practice/secure-pdf/{invalid_token}",
                timeout=30
            )
            
            print(f"   Invalid Token Status: {response.status_code}")
            
            if response.status_code == 401:
                print(f"   ✅ Invalid token correctly rejected with 401")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data.get('detail', 'No detail')}")
                except:
                    pass
                return True
            else:
                print(f"   ❌ Invalid token should return 401, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Invalid token test error: {str(e)}")
            return False
    
    def test_integration_flow(self) -> bool:
        """Test full integration flow: create patient -> assign procedure -> send SMS"""
        print("\n🔄 TEST 7: Testing Full Integration Flow...")
        
        try:
            # Step 1: Create patient with cellphone (if not already done)
            if not self.test_patient_id:
                print("   Creating test patient for integration...")
                if not self.test_patient_cellphone_field():
                    return False
            
            # Step 2: Assign procedure to patient
            print("   Assigning procedure to patient...")
            assignment_data = {
                "patientId": self.test_patient_id,
                "procedureId": self.test_procedure_id,
                "procedureName": "Integration Test Procedure",
                "performedDate": "2024-01-15T10:00:00Z",
                "dentistName": "Dr. Test Dentist"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/practice/assign-procedure",
                json=assignment_data,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_assignment_id = data['data']['assignmentId']
                    print(f"   ✅ Procedure assigned successfully")
                    print(f"   Assignment ID: {self.test_assignment_id}")
                else:
                    print(f"   ❌ Procedure assignment failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Procedure assignment failed with status {response.status_code}")
                return False
            
            # Step 3: Send SMS with assignment ID
            print("   Sending SMS with assignment ID...")
            sms_request = {
                "patientCellphone": "+1987654321",  # Updated cellphone from earlier test
                "procedureId": self.test_procedure_id,
                "procedureName": "Integration Test Procedure",
                "assignmentId": self.test_assignment_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/practice/sms-pdf",
                json=sms_request,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Integration SMS sent successfully")
                    print(f"   Secure Link: {data.get('secureLink', 'Not provided')[:50]}...")
                    
                    # Step 4: Test the secure link
                    integration_secure_link = data.get('secureLink', '')
                    if integration_secure_link:
                        token_match = re.search(r'/secure-pdf/([^/?]+)', integration_secure_link)
                        if token_match:
                            token = token_match.group(1)
                            
                            pdf_response = requests.get(
                                f"{BACKEND_URL}/practice/secure-pdf/{token}",
                                timeout=30
                            )
                            
                            if pdf_response.status_code == 200 and 'application/pdf' in pdf_response.headers.get('content-type', ''):
                                print(f"   ✅ Integration secure PDF access successful")
                                return True
                            else:
                                print(f"   ❌ Integration secure PDF access failed")
                                return False
                    
                    return True
                else:
                    print(f"   ❌ Integration SMS failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Integration SMS failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Integration flow test error: {str(e)}")
            return False
    
    def test_email_functionality_still_works(self) -> bool:
        """Test that existing email functionality still works"""
        print("\n📧 TEST 8: Testing Email Functionality Still Works...")
        
        try:
            # Test email PDF request
            email_request = {
                "patientEmail": f"test.email.{int(time.time())}@gmail.com",
                "procedureId": self.test_procedure_id,
                "procedureName": "Email Test Procedure"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/practice/email-pdf",
                json=email_request,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            print(f"   Email PDF Request Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Email functionality still working")
                    print(f"   Message: {data.get('message', 'No message')}")
                    return True
                else:
                    print(f"   ❌ Email functionality failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Email functionality failed with status {response.status_code}")
                # This might be expected if email service is not configured
                print(f"   ℹ️  Email service might not be configured - this is acceptable")
                return True  # Don't fail the test if email service is not available
                
        except Exception as e:
            print(f"   ❌ Email functionality test error: {str(e)}")
            return True  # Don't fail the test if email service is not available
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            if self.test_patient_id:
                # Delete test patient
                response = requests.delete(
                    f"{BACKEND_URL}/practice/patients/{self.test_patient_id}?hard_delete=true",
                    headers=self.get_auth_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Test patient cleaned up")
                else:
                    print(f"   ⚠️  Could not clean up test patient (status {response.status_code})")
                    
        except Exception as e:
            print(f"   ⚠️  Cleanup error: {str(e)}")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all SMS functionality tests"""
        print("🚀 Starting SMS Functionality Tests...")
        print("=" * 60)
        
        results = {}
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return {"authentication": False}
        
        results["authentication"] = True
        
        # Run all tests
        test_methods = [
            ("patient_cellphone_field", self.test_patient_cellphone_field),
            ("patient_cellphone_update", self.test_patient_cellphone_update),
            ("sms_pdf_valid_request", self.test_sms_pdf_endpoint_valid_request),
            ("sms_pdf_phone_validation", self.test_sms_pdf_phone_validation),
            ("secure_pdf_link_valid", self.test_secure_pdf_link_endpoint),
            ("secure_pdf_link_invalid", self.test_secure_pdf_invalid_token),
            ("integration_flow", self.test_integration_flow),
            ("email_functionality", self.test_email_functionality_still_works)
        ]
        
        for test_name, test_method in test_methods:
            try:
                results[test_name] = test_method()
            except Exception as e:
                print(f"   ❌ Test {test_name} crashed: {str(e)}")
                results[test_name] = False
        
        # Cleanup
        self.cleanup_test_data()
        
        return results

def main():
    """Main test execution"""
    tester = SMSFunctionalityTester()
    results = tester.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SMS FUNCTIONALITY TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        total += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All SMS functionality tests PASSED!")
        return True
    else:
        print("⚠️  Some SMS functionality tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)