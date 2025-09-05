#!/usr/bin/env python3
"""
Production Backend Endpoint Testing
Test the production backend at https://dentist-portal-3.emergent.host/api
to identify which endpoints are available and which are missing.
"""

import requests
import json
import sys
from datetime import datetime

# Production backend URL from review request
PRODUCTION_URL = "https://dentist-portal-3.emergent.host/api"

# Test credentials from review request
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def test_endpoint(method, endpoint, headers=None, data=None, expected_status=None):
    """Test a single endpoint and return results"""
    url = f"{PRODUCTION_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        result = {
            "endpoint": endpoint,
            "method": method.upper(),
            "status_code": response.status_code,
            "available": True,
            "response_size": len(response.text),
            "content_type": response.headers.get("content-type", ""),
        }
        
        # Try to parse JSON response
        try:
            result["response_data"] = response.json()
        except:
            result["response_text"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            "endpoint": endpoint,
            "method": method.upper(),
            "available": False,
            "error": str(e),
            "status_code": None
        }

def authenticate_and_get_token():
    """Authenticate with production backend and get JWT token"""
    print(f"\n🔐 AUTHENTICATION TEST")
    print(f"Testing login with {TEST_EMAIL}")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    result = test_endpoint("POST", "/auth/login", data=login_data)
    
    if result["available"] and result["status_code"] == 200:
        if "response_data" in result and "token" in result["response_data"]:
            token = result["response_data"]["token"]
            print(f"✅ Authentication successful - Token received")
            print(f"   User: {result['response_data'].get('user', {}).get('email', 'N/A')}")
            print(f"   Role: {result['response_data'].get('user', {}).get('role', 'N/A')}")
            print(f"   Practice: {result['response_data'].get('user', {}).get('practiceName', 'N/A')}")
            return token
        else:
            print(f"❌ Authentication failed - No token in response")
            print(f"   Response: {result.get('response_data', result.get('response_text', 'No response'))}")
    else:
        print(f"❌ Authentication failed - Status: {result['status_code']}")
        print(f"   Error: {result.get('error', result.get('response_data', result.get('response_text', 'Unknown error')))}")
    
    return None

def test_core_endpoints():
    """Test core procedure and specialty endpoints"""
    print(f"\n📋 CORE PROCEDURE ENDPOINTS TEST")
    
    endpoints_to_test = [
        ("GET", "/"),
        ("GET", "/procedures"),
        ("GET", "/specialties"),
        ("GET", "/procedures/search?q=root"),
        ("GET", "/procedures/root-canal-therapy"),
        ("GET", "/procedures/dental-implant-placement"),
        ("GET", "/specialties/oral-surgery"),
    ]
    
    results = []
    for method, endpoint in endpoints_to_test:
        result = test_endpoint(method, endpoint)
        results.append(result)
        
        status_icon = "✅" if result["available"] and result["status_code"] < 400 else "❌"
        status_code = result["status_code"] if result["available"] else "UNAVAILABLE"
        
        print(f"   {status_icon} {method} {endpoint} - Status: {status_code}")
        
        if result["available"] and "response_data" in result:
            if endpoint == "/procedures" and "data" in result["response_data"]:
                count = len(result["response_data"]["data"])
                print(f"      → Found {count} procedures")
            elif endpoint == "/specialties" and "data" in result["response_data"]:
                count = len(result["response_data"]["data"])
                print(f"      → Found {count} specialties")
    
    return results

def test_practice_endpoints(token):
    """Test practice management endpoints with authentication"""
    print(f"\n🏥 PRACTICE ENDPOINTS TEST")
    
    if not token:
        print("❌ No authentication token - skipping practice endpoint tests")
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints_to_test = [
        ("GET", "/practice/patients"),
        ("GET", "/practice/procedures"),
        ("GET", "/practice/dentists"),
        ("GET", "/practice/doctors"),  # Legacy endpoint
        ("GET", "/practice/dashboard"),
        ("GET", "/practice/export-data"),
    ]
    
    results = []
    for method, endpoint in endpoints_to_test:
        result = test_endpoint(method, endpoint, headers=headers)
        results.append(result)
        
        status_icon = "✅" if result["available"] and result["status_code"] < 400 else "❌"
        status_code = result["status_code"] if result["available"] else "UNAVAILABLE"
        
        print(f"   {status_icon} {method} {endpoint} - Status: {status_code}")
        
        if result["available"] and "response_data" in result:
            if "data" in result["response_data"] and isinstance(result["response_data"]["data"], list):
                count = len(result["response_data"]["data"])
                print(f"      → Found {count} items")
            elif endpoint == "/practice/dashboard":
                print(f"      → Dashboard data available")
    
    return results

def test_admin_endpoints():
    """Test admin endpoints"""
    print(f"\n👑 ADMIN ENDPOINTS TEST")
    
    # Test admin login
    admin_data = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    result = test_endpoint("POST", "/admin/login", data=admin_data)
    
    status_icon = "✅" if result["available"] and result["status_code"] < 400 else "❌"
    status_code = result["status_code"] if result["available"] else "UNAVAILABLE"
    
    print(f"   {status_icon} POST /admin/login - Status: {status_code}")
    
    admin_token = None
    if result["available"] and result["status_code"] == 200 and "response_data" in result:
        if "token" in result["response_data"]:
            admin_token = result["response_data"]["token"]
            print(f"      → Admin authentication successful")
    
    # Test admin dashboard if we have token
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        dashboard_result = test_endpoint("GET", "/admin/dashboard", headers=headers)
        
        status_icon = "✅" if dashboard_result["available"] and dashboard_result["status_code"] < 400 else "❌"
        status_code = dashboard_result["status_code"] if dashboard_result["available"] else "UNAVAILABLE"
        
        print(f"   {status_icon} GET /admin/dashboard - Status: {status_code}")
    
    return [result]

def generate_summary_report(auth_result, core_results, practice_results, admin_results):
    """Generate a comprehensive summary report"""
    print(f"\n" + "="*80)
    print(f"🎯 PRODUCTION BACKEND ENDPOINT ANALYSIS SUMMARY")
    print(f"Backend URL: {PRODUCTION_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"="*80)
    
    # Authentication Summary
    print(f"\n🔐 AUTHENTICATION STATUS:")
    if auth_result:
        print(f"   ✅ Login endpoint available (/auth/login)")
        print(f"   ✅ Credentials cganz2279@gmail.com/password123 working")
    else:
        print(f"   ❌ Authentication failed or unavailable")
    
    # Core Endpoints Summary
    print(f"\n📋 CORE PROCEDURE ENDPOINTS:")
    available_core = [r for r in core_results if r["available"] and r["status_code"] < 400]
    missing_core = [r for r in core_results if not r["available"] or r["status_code"] >= 400]
    
    print(f"   Available ({len(available_core)}/{len(core_results)}):")
    for result in available_core:
        print(f"      ✅ {result['method']} {result['endpoint']}")
    
    if missing_core:
        print(f"   Missing/Failed ({len(missing_core)}):")
        for result in missing_core:
            print(f"      ❌ {result['method']} {result['endpoint']} - {result.get('status_code', 'UNAVAILABLE')}")
    
    # Practice Endpoints Summary
    print(f"\n🏥 PRACTICE MANAGEMENT ENDPOINTS:")
    if practice_results:
        available_practice = [r for r in practice_results if r["available"] and r["status_code"] < 400]
        missing_practice = [r for r in practice_results if not r["available"] or r["status_code"] >= 400]
        
        print(f"   Available ({len(available_practice)}/{len(practice_results)}):")
        for result in available_practice:
            print(f"      ✅ {result['method']} {result['endpoint']}")
        
        if missing_practice:
            print(f"   Missing/Failed ({len(missing_practice)}):")
            for result in missing_practice:
                print(f"      ❌ {result['method']} {result['endpoint']} - {result.get('status_code', 'UNAVAILABLE')}")
    else:
        print(f"   ❌ Could not test - Authentication required but failed")
    
    # Critical Issues
    print(f"\n🚨 CRITICAL FINDINGS:")
    
    # Check for missing dentist management
    dentist_endpoint_found = any(r["endpoint"] == "/practice/dentists" and r["available"] and r["status_code"] < 400 for r in practice_results)
    if not dentist_endpoint_found:
        print(f"   ❌ MISSING: /practice/dentists endpoint (required for Add Patient page)")
    
    # Check for missing patient management
    patient_endpoint_found = any(r["endpoint"] == "/practice/patients" and r["available"] and r["status_code"] < 400 for r in practice_results)
    if not patient_endpoint_found:
        print(f"   ❌ MISSING: /practice/patients endpoint (required for patient management)")
    
    # Check for missing procedure endpoints
    procedures_endpoint_found = any(r["endpoint"] == "/procedures" and r["available"] and r["status_code"] < 400 for r in core_results)
    if not procedures_endpoint_found:
        print(f"   ❌ MISSING: /procedures endpoint (required for procedure assignment)")
    
    print(f"\n" + "="*80)

def main():
    """Main test execution"""
    print(f"🔍 PRODUCTION BACKEND ENDPOINT TESTING")
    print(f"Target: {PRODUCTION_URL}")
    print(f"Credentials: {TEST_EMAIL}")
    
    # Step 1: Test authentication
    token = authenticate_and_get_token()
    
    # Step 2: Test core endpoints (no auth required)
    core_results = test_core_endpoints()
    
    # Step 3: Test practice endpoints (auth required)
    practice_results = test_practice_endpoints(token)
    
    # Step 4: Test admin endpoints
    admin_results = test_admin_endpoints()
    
    # Step 5: Generate summary report
    generate_summary_report(token is not None, core_results, practice_results, admin_results)
    
    return {
        "authentication_working": token is not None,
        "core_endpoints": core_results,
        "practice_endpoints": practice_results,
        "admin_endpoints": admin_results
    }

if __name__ == "__main__":
    try:
        results = main()
        
        # Exit with appropriate code
        auth_ok = results["authentication_working"]
        core_ok = any(r["available"] and r["status_code"] < 400 for r in results["core_endpoints"])
        practice_ok = any(r["available"] and r["status_code"] < 400 for r in results["practice_endpoints"]) if results["practice_endpoints"] else False
        
        if auth_ok and core_ok and practice_ok:
            print(f"\n✅ All critical endpoints working")
            sys.exit(0)
        else:
            print(f"\n❌ Some critical endpoints missing or failing")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        sys.exit(2)