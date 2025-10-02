#!/usr/bin/env python3
"""
FINAL CORS SOLUTION TEST
Verifying the complete login flow works with the correct backend URL
"""

import requests
import json
import sys
from datetime import datetime

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_complete_login_flow():
    """Test the complete login flow as a browser would do it"""
    log_test("🔍 TESTING COMPLETE LOGIN FLOW")
    
    # Use the CORRECT backend URL from frontend .env
    frontend_origin = "https://app.dentalaftercarenotes.com"
    backend_url = "https://app.dentalaftercarenotes.com"  # Same as frontend!
    
    log_test(f"Frontend Origin: {frontend_origin}")
    log_test(f"Backend URL: {backend_url}")
    log_test("=" * 50)
    
    # Step 1: Browser sends OPTIONS preflight request
    log_test("STEP 1: Browser CORS Preflight Request")
    
    preflight_headers = {
        'Origin': frontend_origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type,authorization',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',  # Same origin since URLs match!
        'Sec-Fetch-Dest': 'empty'
    }
    
    try:
        preflight_response = requests.options(
            f"{backend_url}/api/auth/login", 
            headers=preflight_headers, 
            timeout=10
        )
        
        log_test(f"✅ Preflight Status: {preflight_response.status_code}")
        
        # Check CORS headers
        cors_headers = {}
        for header, value in preflight_response.headers.items():
            if 'access-control' in header.lower():
                cors_headers[header] = value
                log_test(f"✅ {header}: {value}")
        
        allow_origin = cors_headers.get('Access-Control-Allow-Origin') or cors_headers.get('access-control-allow-origin')
        
        if preflight_response.status_code in [200, 204] and allow_origin:
            log_test("✅ CORS Preflight: SUCCESS - Browser will proceed")
            preflight_success = True
        else:
            log_test("❌ CORS Preflight: FAILED - Browser will block request")
            preflight_success = False
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ Preflight Request Error: {str(e)}")
        preflight_success = False
    
    if not preflight_success:
        return False
    
    log_test("-" * 30)
    
    # Step 2: Browser sends actual POST request
    log_test("STEP 2: Actual Login POST Request")
    
    login_headers = {
        'Origin': frontend_origin,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f"{frontend_origin}/login",
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Dest': 'empty'
    }
    
    login_data = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(
            f"{backend_url}/api/auth/login",
            json=login_data,
            headers=login_headers,
            timeout=10
        )
        
        log_test(f"✅ Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            try:
                login_result = login_response.json()
                
                # Check response structure
                if 'token' in login_result:
                    log_test("✅ JWT Token: Received")
                if 'practice' in login_result:
                    practice_name = login_result['practice'].get('name', 'Unknown')
                    practice_id = login_result['practice'].get('id', 'Unknown')
                    log_test(f"✅ Practice: {practice_name} (ID: {practice_id})")
                
                # Check CORS headers in response
                response_cors = login_response.headers.get('Access-Control-Allow-Origin')
                if response_cors:
                    log_test(f"✅ Response CORS: {response_cors}")
                
                log_test("✅ LOGIN FLOW: COMPLETE SUCCESS")
                return True
                
            except json.JSONDecodeError:
                log_test("❌ Invalid JSON response")
                return False
        else:
            log_test(f"❌ Login Failed: {login_response.status_code}")
            try:
                error_data = login_response.json()
                log_test(f"❌ Error: {error_data}")
            except:
                log_test(f"❌ Error: {login_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ Login Request Error: {str(e)}")
        return False

def test_problematic_url():
    """Test the problematic URL mentioned in review request"""
    log_test("🔍 TESTING PROBLEMATIC URL FROM REVIEW")
    
    frontend_origin = "https://app.dentalaftercarenotes.com"
    problematic_backend = "https://dentist-portal-3.emergent.host"
    
    log_test(f"Frontend Origin: {frontend_origin}")
    log_test(f"Backend URL: {problematic_backend}")
    log_test("=" * 50)
    
    preflight_headers = {
        'Origin': frontend_origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type,authorization'
    }
    
    try:
        preflight_response = requests.options(
            f"{problematic_backend}/api/auth/login", 
            headers=preflight_headers, 
            timeout=10
        )
        
        log_test(f"❌ Preflight Status: {preflight_response.status_code}")
        
        allow_origin = preflight_response.headers.get('Access-Control-Allow-Origin')
        log_test(f"❌ Allow-Origin: {allow_origin or 'Missing'}")
        
        if preflight_response.status_code != 200 or not allow_origin:
            log_test("❌ CONFIRMED: This URL has CORS issues")
            log_test("❌ This is exactly what the user is experiencing!")
            return False
        else:
            log_test("✅ Unexpectedly working")
            return True
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ Request Error: {str(e)}")
        return False

def main():
    """Main solution verification test"""
    log_test("🚨 FINAL CORS SOLUTION VERIFICATION")
    log_test("Testing both the working and problematic URLs")
    log_test("=" * 60)
    
    # Test 1: Verify the problematic URL fails
    log_test("TEST 1: Confirming the problematic URL fails")
    problematic_fails = not test_problematic_url()
    log_test(f"Result: {'✅ CONFIRMED BROKEN' if problematic_fails else '❌ UNEXPECTEDLY WORKING'}")
    log_test("-" * 40)
    
    # Test 2: Verify the correct URL works
    log_test("TEST 2: Verifying the correct URL works")
    correct_works = test_complete_login_flow()
    log_test(f"Result: {'✅ WORKING PERFECTLY' if correct_works else '❌ UNEXPECTED FAILURE'}")
    log_test("-" * 40)
    
    # Final conclusion
    log_test("🎯 FINAL CONCLUSION")
    log_test("=" * 30)
    
    if problematic_fails and correct_works:
        log_test("✅ SOLUTION CONFIRMED:")
        log_test("   - Problematic URL (dentist-portal-3.emergent.host) has CORS issues")
        log_test("   - Correct URL (app.dentalaftercarenotes.com) works perfectly")
        log_test("   - Frontend is already configured correctly")
        log_test("")
        log_test("🔧 USER ACTION REQUIRED:")
        log_test("   - Ensure you're accessing: https://app.dentalaftercarenotes.com")
        log_test("   - Do NOT use: https://dentist-portal-3.emergent.host")
        log_test("   - Clear browser cache if needed")
        log_test("   - The login functionality is working correctly!")
        return True
    else:
        log_test("❌ UNEXPECTED RESULTS - Further investigation needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)