#!/usr/bin/env python3
"""
CRITICAL CORS DEBUGGING TEST
Testing CORS functionality for login from https://app.dentalaftercarenotes.com to https://dentist-portal-3.emergent.host
"""

import requests
import json
import sys
from datetime import datetime

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_cors_preflight():
    """Test CORS preflight (OPTIONS) requests"""
    log_test("🔍 TESTING CORS PREFLIGHT REQUESTS")
    
    # Test URLs from review request
    frontend_url = "https://app.dentalaftercarenotes.com"
    backend_url = "https://dentist-portal-3.emergent.host"
    
    # Test OPTIONS request to login endpoint
    login_endpoint = f"{backend_url}/api/auth/login"
    
    headers = {
        'Origin': frontend_url,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    
    try:
        log_test(f"📡 Sending OPTIONS request to: {login_endpoint}")
        log_test(f"📡 Origin header: {frontend_url}")
        
        response = requests.options(login_endpoint, headers=headers, timeout=10)
        
        log_test(f"✅ OPTIONS Response Status: {response.status_code}")
        log_test(f"✅ Response Headers:")
        for header, value in response.headers.items():
            if 'cors' in header.lower() or 'access-control' in header.lower():
                log_test(f"   {header}: {value}")
        
        # Check for required CORS headers
        required_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            log_test(f"❌ Missing CORS headers: {missing_headers}")
            return False
        else:
            log_test("✅ All required CORS headers present")
            return True
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ OPTIONS request failed: {str(e)}")
        return False

def test_actual_login_request():
    """Test actual login POST request with CORS headers"""
    log_test("🔍 TESTING ACTUAL LOGIN REQUEST WITH CORS")
    
    frontend_url = "https://app.dentalaftercarenotes.com"
    backend_url = "https://dentist-portal-3.emergent.host"
    login_endpoint = f"{backend_url}/api/auth/login"
    
    headers = {
        'Origin': frontend_url,
        'Content-Type': 'application/json',
        'Referer': frontend_url
    }
    
    # Test credentials from review
    login_data = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        log_test(f"📡 Sending POST request to: {login_endpoint}")
        log_test(f"📡 Origin header: {frontend_url}")
        log_test(f"📡 Login data: {login_data['email']}")
        
        response = requests.post(
            login_endpoint, 
            json=login_data, 
            headers=headers, 
            timeout=10
        )
        
        log_test(f"✅ POST Response Status: {response.status_code}")
        log_test(f"✅ Response Headers:")
        for header, value in response.headers.items():
            if 'cors' in header.lower() or 'access-control' in header.lower():
                log_test(f"   {header}: {value}")
        
        if response.status_code == 200:
            log_test("✅ Login request successful")
            return True
        else:
            log_test(f"❌ Login request failed: {response.status_code}")
            try:
                error_data = response.json()
                log_test(f"❌ Error response: {error_data}")
            except:
                log_test(f"❌ Error response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ POST request failed: {str(e)}")
        return False

def test_backend_health():
    """Test if backend is accessible"""
    log_test("🔍 TESTING BACKEND HEALTH")
    
    backend_url = "https://dentist-portal-3.emergent.host"
    health_endpoint = f"{backend_url}/api/health"
    
    try:
        log_test(f"📡 Checking health endpoint: {health_endpoint}")
        response = requests.get(health_endpoint, timeout=10)
        
        log_test(f"✅ Health check status: {response.status_code}")
        if response.status_code == 200:
            try:
                health_data = response.json()
                log_test(f"✅ Health response: {health_data}")
                return True
            except:
                log_test(f"✅ Health response: {response.text}")
                return True
        else:
            log_test(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ Health check failed: {str(e)}")
        return False

def test_different_origins():
    """Test CORS with different origins"""
    log_test("🔍 TESTING CORS WITH DIFFERENT ORIGINS")
    
    backend_url = "https://dentist-portal-3.emergent.host"
    login_endpoint = f"{backend_url}/api/auth/login"
    
    # Test different origins
    origins_to_test = [
        "https://app.dentalaftercarenotes.com",
        "https://dentist-portal-3.emergent.host",
        "http://localhost:3000",
        "https://example.com"
    ]
    
    results = {}
    
    for origin in origins_to_test:
        log_test(f"📡 Testing origin: {origin}")
        
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        try:
            response = requests.options(login_endpoint, headers=headers, timeout=10)
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin', 'Not Set')
            log_test(f"   Status: {response.status_code}, CORS Origin: {cors_origin}")
            
            results[origin] = {
                'status': response.status_code,
                'cors_origin': cors_origin,
                'allowed': cors_origin == origin or cors_origin == '*'
            }
            
        except requests.exceptions.RequestException as e:
            log_test(f"   Failed: {str(e)}")
            results[origin] = {'status': 'error', 'error': str(e)}
    
    return results

def main():
    """Main test function"""
    log_test("🚨 CRITICAL CORS DEBUGGING - USER CANNOT LOGIN")
    log_test("=" * 60)
    
    # Test 1: Backend Health
    log_test("TEST 1: Backend Health Check")
    health_ok = test_backend_health()
    log_test(f"Result: {'✅ PASS' if health_ok else '❌ FAIL'}")
    log_test("-" * 40)
    
    # Test 2: CORS Preflight
    log_test("TEST 2: CORS Preflight (OPTIONS)")
    preflight_ok = test_cors_preflight()
    log_test(f"Result: {'✅ PASS' if preflight_ok else '❌ FAIL'}")
    log_test("-" * 40)
    
    # Test 3: Different Origins
    log_test("TEST 3: Different Origins")
    origin_results = test_different_origins()
    log_test("Origin test results:")
    for origin, result in origin_results.items():
        if 'error' in result:
            log_test(f"   {origin}: ❌ ERROR - {result['error']}")
        else:
            status = "✅ ALLOWED" if result['allowed'] else "❌ BLOCKED"
            log_test(f"   {origin}: {status} (Status: {result['status']}, CORS: {result['cors_origin']})")
    log_test("-" * 40)
    
    # Test 4: Actual Login
    log_test("TEST 4: Actual Login Request")
    login_ok = test_actual_login_request()
    log_test(f"Result: {'✅ PASS' if login_ok else '❌ FAIL'}")
    log_test("-" * 40)
    
    # Summary
    log_test("🎯 CORS DEBUGGING SUMMARY")
    log_test(f"Backend Health: {'✅' if health_ok else '❌'}")
    log_test(f"CORS Preflight: {'✅' if preflight_ok else '❌'}")
    log_test(f"Login Request: {'✅' if login_ok else '❌'}")
    
    if not (health_ok and preflight_ok and login_ok):
        log_test("❌ CRITICAL ISSUES FOUND - LOGIN WILL FAIL")
        return False
    else:
        log_test("✅ ALL TESTS PASSED - LOGIN SHOULD WORK")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)