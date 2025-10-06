#!/usr/bin/env python3
"""
Admin Panel Procedure Creation API Validation Test
Testing 422 validation errors and successful creation scenarios
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"

# Admin credentials
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if details:
        print(f"   Details: {details}")

def test_admin_login():
    """Test admin login and get authentication token"""
    print_test_header("ADMIN LOGIN TEST")
    
    try:
        login_url = f"{BACKEND_URL}/api/admin/login"
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        print(f"🔐 Attempting login to: {login_url}")
        print(f"📧 Email: {ADMIN_EMAIL}")
        print(f"🔑 Password: {ADMIN_PASSWORD}")
        
        response = requests.post(login_url, json=login_data, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response Data: {json.dumps(data, indent=2)}")
            
            if data.get("success") and data.get("token"):
                token = data["token"]
                print_result(True, f"Admin login successful", f"Token: {token[:20]}...")
                return token
            else:
                print_result(False, "Login response missing success or token", str(data))
                return None
        else:
            print(f"📄 Response Text: {response.text}")
            print_result(False, f"Login failed with status {response.status_code}", response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Login request failed", str(e))
        return None

def test_procedure_creation_validation_errors(token):
    """Test procedure creation with missing required fields to trigger 422 validation errors"""
    print_test_header("PROCEDURE CREATION VALIDATION ERRORS TEST")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    create_url = f"{BACKEND_URL}/api/admin/procedures"
    
    # Test scenarios for validation errors
    test_scenarios = [
        {
            "name": "Missing name field",
            "data": {
                "specialty": "general-dentistry",
                "specialtyName": "General Dentistry",
                "overview": "Test procedure overview",
                "duration": "1-2 days",
                "immediateAftercare": ["Rest for 24 hours"],
                "dietRestrictions": ["Soft foods only"],
                "warningSignsToCallDoctor": ["Excessive bleeding"],
                "recoveryTimeline": [{"day": "Day 1", "activity": "Rest"}],
                "medications": ["Ibuprofen"]
            }
        },
        {
            "name": "Missing specialty field",
            "data": {
                "name": "Test Procedure",
                "specialtyName": "General Dentistry",
                "overview": "Test procedure overview",
                "duration": "1-2 days",
                "immediateAftercare": ["Rest for 24 hours"],
                "dietRestrictions": ["Soft foods only"],
                "warningSignsToCallDoctor": ["Excessive bleeding"],
                "recoveryTimeline": [{"day": "Day 1", "activity": "Rest"}],
                "medications": ["Ibuprofen"]
            }
        },
        {
            "name": "Missing overview field",
            "data": {
                "name": "Test Procedure",
                "specialty": "general-dentistry",
                "specialtyName": "General Dentistry",
                "duration": "1-2 days",
                "immediateAftercare": ["Rest for 24 hours"],
                "dietRestrictions": ["Soft foods only"],
                "warningSignsToCallDoctor": ["Excessive bleeding"],
                "recoveryTimeline": [{"day": "Day 1", "activity": "Rest"}],
                "medications": ["Ibuprofen"]
            }
        },
        {
            "name": "Empty name field",
            "data": {
                "name": "",
                "specialty": "general-dentistry",
                "specialtyName": "General Dentistry",
                "overview": "Test procedure overview",
                "duration": "1-2 days",
                "immediateAftercare": ["Rest for 24 hours"],
                "dietRestrictions": ["Soft foods only"],
                "warningSignsToCallDoctor": ["Excessive bleeding"],
                "recoveryTimeline": [{"day": "Day 1", "activity": "Rest"}],
                "medications": ["Ibuprofen"]
            }
        },
        {
            "name": "Empty specialty field",
            "data": {
                "name": "Test Procedure",
                "specialty": "",
                "specialtyName": "General Dentistry",
                "overview": "Test procedure overview",
                "duration": "1-2 days",
                "immediateAftercare": ["Rest for 24 hours"],
                "dietRestrictions": ["Soft foods only"],
                "warningSignsToCallDoctor": ["Excessive bleeding"],
                "recoveryTimeline": [{"day": "Day 1", "activity": "Rest"}],
                "medications": ["Ibuprofen"]
            }
        },
        {
            "name": "Empty overview field",
            "data": {
                "name": "Test Procedure",
                "specialty": "general-dentistry",
                "specialtyName": "General Dentistry",
                "overview": "",
                "duration": "1-2 days",
                "immediateAftercare": ["Rest for 24 hours"],
                "dietRestrictions": ["Soft foods only"],
                "warningSignsToCallDoctor": ["Excessive bleeding"],
                "recoveryTimeline": [{"day": "Day 1", "activity": "Rest"}],
                "medications": ["Ibuprofen"]
            }
        }
    ]
    
    validation_errors_found = []
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        
        try:
            response = requests.post(create_url, json=scenario['data'], headers=headers, timeout=30)
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"📄 Response Text: {response.text}")
            
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    print(f"📋 Validation Error Response: {json.dumps(error_data, indent=2)}")
                    
                    # Check if error response is properly structured
                    if "detail" in error_data:
                        validation_errors_found.append({
                            "scenario": scenario['name'],
                            "status_code": response.status_code,
                            "error_structure": error_data,
                            "properly_structured": True
                        })
                        print_result(True, f"422 validation error correctly returned", f"Error: {error_data.get('detail', 'No detail')}")
                    else:
                        validation_errors_found.append({
                            "scenario": scenario['name'],
                            "status_code": response.status_code,
                            "error_structure": error_data,
                            "properly_structured": False
                        })
                        print_result(False, f"422 error returned but not properly structured", str(error_data))
                        
                except json.JSONDecodeError:
                    validation_errors_found.append({
                        "scenario": scenario['name'],
                        "status_code": response.status_code,
                        "error_structure": response.text,
                        "properly_structured": False
                    })
                    print_result(False, f"422 error returned but response is not valid JSON", response.text)
                    
            else:
                print_result(False, f"Expected 422 validation error but got {response.status_code}", response.text)
                validation_errors_found.append({
                    "scenario": scenario['name'],
                    "status_code": response.status_code,
                    "error_structure": response.text,
                    "properly_structured": False
                })
                
        except Exception as e:
            print_result(False, f"Request failed for scenario: {scenario['name']}", str(e))
            validation_errors_found.append({
                "scenario": scenario['name'],
                "status_code": "ERROR",
                "error_structure": str(e),
                "properly_structured": False
            })
    
    return validation_errors_found

def test_procedure_creation_success(token):
    """Test procedure creation with valid data to ensure normal creation works"""
    print_test_header("PROCEDURE CREATION SUCCESS TEST")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    create_url = f"{BACKEND_URL}/api/admin/procedures"
    
    # Valid test data
    valid_procedure_data = {
        "name": f"Test Procedure {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "specialty": "general-dentistry",
        "specialtyName": "General Dentistry",
        "overview": "This is a comprehensive test procedure overview that provides detailed information about the procedure.",
        "duration": "1-2 days",
        "immediateAftercare": [
            "Rest for 24 hours after the procedure",
            "Apply ice pack to reduce swelling",
            "Take prescribed medications as directed"
        ],
        "dietRestrictions": [
            "Soft foods only for first 24 hours",
            "Avoid hot liquids",
            "No alcohol for 48 hours"
        ],
        "warningSignsToCallDoctor": [
            "Excessive bleeding that doesn't stop",
            "Severe pain not relieved by medication",
            "Signs of infection (fever, pus)"
        ],
        "recoveryTimeline": [
            {"day": "Day 1", "activity": "Complete rest, soft foods only"},
            {"day": "Day 2-3", "activity": "Light activities, continue soft diet"},
            {"day": "Day 4-7", "activity": "Gradual return to normal activities"}
        ],
        "medications": [
            "Ibuprofen 400mg every 6 hours for pain",
            "Amoxicillin 500mg twice daily if prescribed"
        ]
    }
    
    print(f"🧪 Testing procedure creation with valid data")
    print(f"📋 Procedure Data: {json.dumps(valid_procedure_data, indent=2)}")
    
    try:
        response = requests.post(create_url, json=valid_procedure_data, headers=headers, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                success_data = response.json()
                print(f"📋 Success Response: {json.dumps(success_data, indent=2)}")
                
                if success_data.get("success") and success_data.get("procedure_id"):
                    print_result(True, "Procedure created successfully", f"ID: {success_data.get('procedure_id')}")
                    return {
                        "success": True,
                        "procedure_id": success_data.get("procedure_id"),
                        "response": success_data
                    }
                else:
                    print_result(False, "Success response missing expected fields", str(success_data))
                    return {"success": False, "error": "Missing expected fields in success response"}
                    
            except json.JSONDecodeError:
                print_result(False, "Success response is not valid JSON", response.text)
                return {"success": False, "error": "Invalid JSON in success response"}
                
        elif response.status_code == 409:
            # Conflict - procedure already exists
            try:
                conflict_data = response.json()
                print_result(False, "Procedure creation failed - already exists", str(conflict_data))
                return {"success": False, "error": "Procedure already exists", "response": conflict_data}
            except json.JSONDecodeError:
                print_result(False, "Conflict response is not valid JSON", response.text)
                return {"success": False, "error": "Invalid JSON in conflict response"}
                
        else:
            print_result(False, f"Unexpected status code {response.status_code}", response.text)
            return {"success": False, "error": f"Unexpected status code: {response.status_code}"}
            
    except Exception as e:
        print_result(False, "Request failed", str(e))
        return {"success": False, "error": str(e)}

def main():
    """Main test execution"""
    print("🚀 Starting Admin Panel Procedure Creation API Validation Test")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"📧 Admin Email: {ADMIN_EMAIL}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Login to get authentication token
    token = test_admin_login()
    if not token:
        print("\n❌ CRITICAL FAILURE: Could not obtain authentication token")
        print("🛑 Stopping test execution")
        sys.exit(1)
    
    # Step 2: Test validation errors (422 responses)
    validation_results = test_procedure_creation_validation_errors(token)
    
    # Step 3: Test successful creation
    success_result = test_procedure_creation_success(token)
    
    # Summary
    print_test_header("TEST SUMMARY")
    
    print(f"🔐 Admin Login: {'✅ SUCCESS' if token else '❌ FAILED'}")
    
    # Validation errors summary
    total_validation_tests = len(validation_results)
    successful_validations = len([r for r in validation_results if r['status_code'] == 422 and r['properly_structured']])
    
    print(f"🚫 Validation Error Tests: {successful_validations}/{total_validation_tests} passed")
    
    for result in validation_results:
        status = "✅" if result['status_code'] == 422 and result['properly_structured'] else "❌"
        print(f"   {status} {result['scenario']}: Status {result['status_code']}")
    
    # Success test summary
    print(f"✅ Success Creation Test: {'✅ PASSED' if success_result.get('success') else '❌ FAILED'}")
    if not success_result.get('success'):
        print(f"   Error: {success_result.get('error', 'Unknown error')}")
    
    # Final verdict
    all_tests_passed = (
        token is not None and
        successful_validations == total_validation_tests and
        success_result.get('success', False)
    )
    
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    if all_tests_passed:
        print("🎉 The admin panel procedure creation API validation is working correctly!")
        print("✅ 422 validation errors are properly returned for missing/empty required fields")
        print("✅ Valid procedure creation works as expected")
        print("✅ Error responses are properly structured with readable messages")
    else:
        print("⚠️  Issues found with the admin panel procedure creation API:")
        if not token:
            print("   - Admin login failed")
        if successful_validations < total_validation_tests:
            print(f"   - {total_validation_tests - successful_validations} validation error tests failed")
        if not success_result.get('success'):
            print("   - Valid procedure creation failed")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)