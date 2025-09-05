#!/usr/bin/env python3
"""
Registration Functionality Testing - Comprehensive Test Suite
Tests the fixed registration functionality as requested in the review.
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://dentistpdf.preview.emergentagent.com/api"

class RegistrationTester:
    def __init__(self):
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

def test_valid_registration():
    """Test Case 1: Valid Registration with proper data"""
    test_name = "Valid Registration"
    
    try:
        # Use realistic test data
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Sunrise Dental Care",
            "email": f"admin.test.{timestamp}@sunrisedental.com",
            "phone": "(555) 123-4567",
            "website": "www.sunrisedental.com",
            "adminFirstName": "Dr. Sarah",
            "adminLastName": "Johnson",
            "adminPassword": "SecurePass123",
            "street": "123 Main Street",
            "city": "Springfield",
            "state": "IL",
            "zipCode": "62701"
        }
        
        print(f"🧪 Testing Valid Registration")
        print(f"   Email: {registration_data['email']}")
        print(f"   Practice: {registration_data['practiceName']}")
        print(f"   Website: {registration_data['website']}")
        print(f"   Password: {registration_data['adminPassword']}")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if (data.get('success') and 
                data.get('message') and 
                data.get('practice', {}).get('status') == 'active'):
                
                print("✅ PASS Valid Registration: Registration successful")
                print(f"   Practice ID: {data['practice']['id']}")
                print(f"   Status: {data['practice']['status']}")
                return True
            else:
                print(f"❌ FAIL Valid Registration: Invalid response structure: {data}")
                return False
        else:
            print(f"❌ FAIL Valid Registration: HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Valid Registration: Exception: {str(e)}")
        return False

def test_password_validation_letters_only():
    """Test Case 2a: Password with only letters (should fail)"""
    test_name = "Password Validation - Letters Only"
    
    try:
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Test Practice Letters",
            "email": f"test.letters.{timestamp}@testpractice.com",
            "phone": "(555) 987-6543",
            "website": "www.testpractice.com",
            "adminFirstName": "John",
            "adminLastName": "Doe",
            "adminPassword": "OnlyLetters",  # No numbers
            "street": "456 Test Ave",
            "city": "Test City",
            "state": "CA",
            "zipCode": "90210"
        }
        
        print(f"\n🧪 Testing Password Validation - Letters Only")
        print(f"   Password: {registration_data['adminPassword']} (should fail)")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 400:
            data = response.json()
            if "letters and numbers" in data.get('detail', '').lower():
                print("✅ PASS Password Validation - Letters Only: Correctly rejected")
                print(f"   Error message: {data['detail']}")
                return True
            else:
                print(f"❌ FAIL Password Validation - Letters Only: Wrong error message: {data.get('detail')}")
                return False
        else:
            print(f"❌ FAIL Password Validation - Letters Only: Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Password Validation - Letters Only: Exception: {str(e)}")
        return False

def test_password_validation_numbers_only():
    """Test Case 2b: Password with only numbers (should fail)"""
    test_name = "Password Validation - Numbers Only"
    
    try:
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Test Practice Numbers",
            "email": f"test.numbers.{timestamp}@testpractice.com",
            "phone": "(555) 987-6543",
            "website": "www.testpractice.com",
            "adminFirstName": "Jane",
            "adminLastName": "Smith",
            "adminPassword": "123456789",  # Only numbers
            "street": "789 Number St",
            "city": "Number City",
            "state": "TX",
            "zipCode": "75001"
        }
        
        print(f"\n🧪 Testing Password Validation - Numbers Only")
        print(f"   Password: {registration_data['adminPassword']} (should fail)")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 400:
            data = response.json()
            if "letters and numbers" in data.get('detail', '').lower():
                print("✅ PASS Password Validation - Numbers Only: Correctly rejected")
                print(f"   Error message: {data['detail']}")
                return True
            else:
                print(f"❌ FAIL Password Validation - Numbers Only: Wrong error message: {data.get('detail')}")
                return False
        else:
            print(f"❌ FAIL Password Validation - Numbers Only: Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Password Validation - Numbers Only: Exception: {str(e)}")
        return False

def test_password_validation_too_short():
    """Test Case 2c: Password < 6 characters (should fail)"""
    test_name = "Password Validation - Too Short"
    
    try:
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Test Practice Short",
            "email": f"test.short.{timestamp}@testpractice.com",
            "phone": "(555) 987-6543",
            "website": "www.testpractice.com",
            "adminFirstName": "Bob",
            "adminLastName": "Wilson",
            "adminPassword": "Ab1",  # Too short
            "street": "321 Short St",
            "city": "Short City",
            "state": "FL",
            "zipCode": "33101"
        }
        
        print(f"\n🧪 Testing Password Validation - Too Short")
        print(f"   Password: {registration_data['adminPassword']} (should fail - too short)")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 400:
            data = response.json()
            if "6 characters" in data.get('detail', '').lower():
                print("✅ PASS Password Validation - Too Short: Correctly rejected")
                print(f"   Error message: {data['detail']}")
                return True
            else:
                print(f"❌ FAIL Password Validation - Too Short: Wrong error message: {data.get('detail')}")
                return False
        else:
            print(f"❌ FAIL Password Validation - Too Short: Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Password Validation - Too Short: Exception: {str(e)}")
        return False

def test_password_validation_valid():
    """Test Case 2d: Valid password with letters+numbers (should succeed)"""
    test_name = "Password Validation - Valid Password"
    
    try:
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Valid Password Practice",
            "email": f"test.valid.{timestamp}@validpractice.com",
            "phone": "(555) 456-7890",
            "website": "www.validpractice.com",
            "adminFirstName": "Alice",
            "adminLastName": "Brown",
            "adminPassword": "ValidPass123",  # Valid: letters + numbers + 6+ chars
            "street": "654 Valid Ave",
            "city": "Valid City",
            "state": "NY",
            "zipCode": "10001"
        }
        
        print(f"\n🧪 Testing Password Validation - Valid Password")
        print(f"   Password: {registration_data['adminPassword']} (should succeed)")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('practice', {}).get('status') == 'active':
                print("✅ PASS Password Validation - Valid Password: Registration successful")
                print(f"   Practice: {data['practice']['name']}")
                return True
            else:
                print(f"❌ FAIL Password Validation - Valid Password: Registration failed: {data}")
                return False
        else:
            print(f"❌ FAIL Password Validation - Valid Password: Expected 200 success, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Password Validation - Valid Password: Exception: {str(e)}")
        return False

def test_duplicate_email_validation():
    """Test Case 3: Email validation - duplicate email handling"""
    test_name = "Email Validation - Duplicate Email"
    
    try:
        # First, register with a specific email
        timestamp = str(int(time.time()))
        duplicate_email = f"duplicate.test.{timestamp}@duplicate.com"
        
        first_registration = {
            "practiceName": "First Practice",
            "email": duplicate_email,
            "phone": "(555) 111-2222",
            "website": "www.firstpractice.com",
            "adminFirstName": "First",
            "adminLastName": "Admin",
            "adminPassword": "FirstPass123",
            "street": "111 First St",
            "city": "First City",
            "state": "WA",
            "zipCode": "98101"
        }
        
        print(f"\n🧪 Testing Email Validation - Duplicate Email")
        print(f"   First registration with: {duplicate_email}")
        
        # Register first practice
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=first_registration)
        
        if response.status_code != 200:
            print(f"❌ FAIL Email Validation - Duplicate Email: Failed to create first practice: {response.status_code}")
            return False
            
        print(f"   First registration successful")
        
        # Now try to register with the same email
        second_registration = {
            "practiceName": "Second Practice",
            "email": duplicate_email,  # Same email
            "phone": "(555) 333-4444",
            "website": "www.secondpractice.com",
            "adminFirstName": "Second",
            "adminLastName": "Admin",
            "adminPassword": "SecondPass123",
            "street": "222 Second St",
            "city": "Second City",
            "state": "OR",
            "zipCode": "97201"
        }
        
        print(f"   Attempting second registration with same email...")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=second_registration)
        
        if response.status_code == 400:
            data = response.json()
            if "already registered" in data.get('detail', '').lower():
                print("✅ PASS Email Validation - Duplicate Email: Correctly rejected duplicate")
                print(f"   Error message: {data['detail']}")
                return True
            else:
                print(f"❌ FAIL Email Validation - Duplicate Email: Wrong error message: {data.get('detail')}")
                return False
        else:
            print(f"❌ FAIL Email Validation - Duplicate Email: Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Email Validation - Duplicate Email: Exception: {str(e)}")
        return False

def test_website_field_validation():
    """Test Case 4: Website field accepts www.domain.com format"""
    test_name = "Website Field Validation"
    
    try:
        timestamp = str(int(time.time()))
        registration_data = {
            "practiceName": "Website Test Practice",
            "email": f"website.test.{timestamp}@websitetest.com",
            "phone": "(555) 777-8888",
            "website": "www.websitetest.com",  # Should be accepted
            "adminFirstName": "Website",
            "adminLastName": "Tester",
            "adminPassword": "WebsitePass123",
            "street": "888 Website Blvd",
            "city": "Website City",
            "state": "CO",
            "zipCode": "80201"
        }
        
        print(f"\n🧪 Testing Website Field Validation")
        print(f"   Website: {registration_data['website']} (should be accepted)")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=registration_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ PASS Website Field Validation: www.domain.com format accepted")
                return True
            else:
                print(f"❌ FAIL Website Field Validation: Registration failed: {data}")
                return False
        else:
            print(f"❌ FAIL Website Field Validation: HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Website Field Validation: Exception: {str(e)}")
        return False

def test_error_handling_missing_fields():
    """Test Case 5: Error handling for missing required fields"""
    test_name = "Error Handling - Missing Fields"
    
    try:
        # Missing required fields
        incomplete_data = {
            "practiceName": "Incomplete Practice",
            # Missing email, adminFirstName, adminLastName, adminPassword
            "phone": "(555) 999-0000",
            "website": "www.incomplete.com"
        }
        
        print(f"\n🧪 Testing Error Handling - Missing Fields")
        print(f"   Sending incomplete data (missing email, names, password)")
        
        response = requests.post(f"{BACKEND_URL}/auth/register-practice-samcart", json=incomplete_data)
        
        if response.status_code == 422:  # Validation error
            print("✅ PASS Error Handling - Missing Fields: Correctly returned validation error")
            return True
        else:
            print(f"❌ FAIL Error Handling - Missing Fields: Expected 422 validation error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL Error Handling - Missing Fields: Exception: {str(e)}")
        return False

def test_registration_endpoint():
    """Legacy test function - kept for compatibility"""
    return test_valid_registration()

def run_all_tests():
    """Run all registration tests"""
    print("🧪 STARTING REGISTRATION FUNCTIONALITY TESTING")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Valid Registration
    test_results.append(test_valid_registration())
    
    # Test 2: Password Validation
    test_results.append(test_password_validation_letters_only())
    test_results.append(test_password_validation_numbers_only())
    test_results.append(test_password_validation_too_short())
    test_results.append(test_password_validation_valid())
    
    # Test 3: Email Validation
    test_results.append(test_duplicate_email_validation())
    
    # Test 4: Website Field
    test_results.append(test_website_field_validation())
    
    # Test 5: Error Handling
    test_results.append(test_error_handling_missing_fields())
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in test_results if result)
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Registration functionality is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the issues above.")
        
    return passed == total

def main():
    """Main function"""
    print("🔐 COMPREHENSIVE REGISTRATION FUNCTIONALITY TESTING")
    print("Testing the fixed registration functionality as requested in review")
    print("=" * 70)
    
    success = run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)