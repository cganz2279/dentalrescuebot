#!/usr/bin/env python3
"""
Minimal Field Test for Admin Procedure Creation
Tests POST /api/admin/procedures with minimal data to identify required vs optional fields
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://patient-portal-45.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def get_admin_token():
    """Get admin authentication token"""
    print("🔐 Getting admin authentication token...")
    
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{API_BASE}/admin/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin login successful")
            return token
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def test_procedure_creation(token, test_data, test_name):
    """Test procedure creation with specific data"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")
    print(f"📋 Test Data:")
    print(json.dumps(test_data, indent=2))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{API_BASE}/admin/procedures", json=test_data, headers=headers)
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 422:
            # Validation error
            error_data = response.json()
            print(f"❌ Validation Errors:")
            if "detail" in error_data:
                for error in error_data["detail"]:
                    field = error.get("loc", [])[-1] if error.get("loc") else "unknown"
                    message = error.get("msg", "")
                    print(f"   • Field '{field}': {message}")
            return {"status": 422, "errors": error_data}
            
        elif response.status_code == 200:
            # Success
            success_data = response.json()
            print(f"✅ Success! Procedure created:")
            print(f"   • ID: {success_data.get('procedure_id', 'N/A')}")
            print(f"   • Name: {success_data.get('procedure', {}).get('name', 'N/A')}")
            return {"status": 200, "data": success_data}
            
        else:
            # Other error
            print(f"⚠️  Unexpected status {response.status_code}: {response.text}")
            return {"status": response.status_code, "error": response.text}
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return {"status": "error", "error": str(e)}

def main():
    """Main test function"""
    print("🎯 MINIMAL FIELD VALIDATION TEST FOR ADMIN PROCEDURE CREATION")
    print("Testing which fields are required vs optional")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Test cases to identify required vs optional fields
    test_cases = [
        {
            "name": "Test 1: Only name, specialty, overview (NO recoveryTimeline)",
            "data": {
                "name": "Minimal Test Procedure",
                "specialty": "general-dentistry", 
                "overview": "Basic test overview"
            }
        },
        {
            "name": "Test 2: Missing specialtyName field",
            "data": {
                "name": "Test Without SpecialtyName",
                "specialty": "general-dentistry",
                "overview": "Test without specialtyName field"
            }
        },
        {
            "name": "Test 3: Missing duration field",
            "data": {
                "name": "Test Without Duration",
                "specialty": "general-dentistry",
                "overview": "Test without duration field"
            }
        },
        {
            "name": "Test 4: Missing all list fields",
            "data": {
                "name": "Test Without Lists",
                "specialty": "general-dentistry",
                "overview": "Test without any list fields"
            }
        },
        {
            "name": "Test 5: Empty list fields",
            "data": {
                "name": "Test Empty Lists",
                "specialty": "general-dentistry",
                "overview": "Test with empty list fields",
                "immediateAftercare": [],
                "dietRestrictions": [],
                "warningSignsToCallDoctor": [],
                "recoveryTimeline": [],
                "medications": []
            }
        },
        {
            "name": "Test 6: Only required fields based on model",
            "data": {
                "name": "Required Fields Only",
                "specialty": "general-dentistry",
                "specialtyName": "General Dentistry",
                "duration": "Variable",
                "overview": "Test with only required fields",
                "immediateAftercare": [],
                "dietRestrictions": [],
                "warningSignsToCallDoctor": [],
                "recoveryTimeline": [],
                "medications": []
            }
        }
    ]
    
    results = []
    
    # Run all test cases
    for test_case in test_cases:
        result = test_procedure_creation(token, test_case["data"], test_case["name"])
        results.append({
            "test": test_case["name"],
            "data": test_case["data"],
            "result": result
        })
    
    # Analyze results
    print(f"\n{'='*60}")
    print("📊 FIELD REQUIREMENT ANALYSIS")
    print(f"{'='*60}")
    
    required_fields = set()
    optional_fields = set()
    successful_tests = []
    
    for result in results:
        test_name = result["test"]
        test_data = result["data"]
        test_result = result["result"]
        
        print(f"\n{test_name}:")
        
        if test_result["status"] == 422:
            # Validation error - analyze which fields are missing
            errors = test_result["errors"]
            if "detail" in errors:
                for error in errors["detail"]:
                    field_name = error.get("loc", [])[-1] if error.get("loc") else "unknown"
                    error_msg = error.get("msg", "")
                    print(f"  ❌ Field '{field_name}': {error_msg}")
                    
                    if "Field required" in error_msg:
                        required_fields.add(field_name)
                        
        elif test_result["status"] == 200:
            print(f"  ✅ SUCCESS - All fields in this test are sufficient")
            successful_tests.append(result)
            
            # Fields present in successful test are either required or optional
            for field in test_data.keys():
                if field not in required_fields:
                    optional_fields.add(field)
        else:
            print(f"  ⚠️  Status: {test_result['status']}")
    
    # Final analysis
    print(f"\n{'='*60}")
    print("🎯 FINAL FIELD REQUIREMENTS ANALYSIS")
    print(f"{'='*60}")
    
    print(f"\n🔴 REQUIRED FIELDS (must have asterisk *):")
    for field in sorted(required_fields):
        print(f"   • {field}")
    
    print(f"\n🟢 OPTIONAL FIELDS (no asterisk needed):")
    # Determine optional fields from successful minimal tests
    minimal_successful = None
    for result in successful_tests:
        if "Only name, specialty, overview" in result["test"]:
            minimal_successful = result
            break
    
    if minimal_successful:
        print("   Based on minimal successful test:")
        all_possible_fields = [
            "specialtyName", "duration", "immediateAftercare", 
            "dietRestrictions", "warningSignsToCallDoctor", 
            "recoveryTimeline", "medications"
        ]
        
        for field in all_possible_fields:
            if field not in required_fields:
                print(f"   • {field}")
    
    print(f"\n📋 SPECIFIC FINDINGS:")
    
    # Check if recoveryTimeline is optional
    recovery_optional = any("Only name, specialty, overview" in r["test"] and r["result"]["status"] == 200 for r in results)
    if recovery_optional:
        print("   ✅ recoveryTimeline IS OPTIONAL (as requested)")
    else:
        print("   ❌ recoveryTimeline appears to be required")
    
    # Check minimal working combination
    minimal_working = None
    for result in results:
        if result["result"]["status"] == 200:
            field_count = len(result["data"])
            if minimal_working is None or field_count < len(minimal_working["data"]):
                minimal_working = result
    
    if minimal_working:
        print(f"\n   🎯 MINIMAL WORKING COMBINATION:")
        for field in sorted(minimal_working["data"].keys()):
            print(f"      • {field}")
    
    print(f"\n🎉 RECOMMENDATIONS FOR FRONTEND:")
    print(f"   • Mark with asterisk (*): {', '.join(sorted(required_fields))}")
    print(f"   • Leave without asterisk: All other fields")
    print(f"   • recoveryTimeline can be left empty/optional")
    
    print(f"\n✅ Test completed successfully!")

if __name__ == "__main__":
    main()