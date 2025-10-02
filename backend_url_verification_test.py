#!/usr/bin/env python3
"""
BACKEND URL VERIFICATION TEST
Testing which backend URL should be used and if CORS works correctly
"""

import requests
import json
import sys
from datetime import datetime

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_backend_url_functionality(backend_url, url_name):
    """Test full functionality of a backend URL"""
    log_test(f"🔍 TESTING {url_name}: {backend_url}")
    
    frontend_origin = "https://app.dentalaftercarenotes.com"
    results = {
        'health': False,
        'cors_preflight': False,
        'login_api': False,
        'cors_headers': {}
    }
    
    # Test 1: Health check
    try:
        health_response = requests.get(f"{backend_url}/api/health", timeout=10)
        if health_response.status_code == 200:
            results['health'] = True
            log_test(f"   ✅ Health check: {health_response.status_code}")
            try:
                health_data = health_response.json()
                log_test(f"   ✅ Health data: {health_data}")
            except:
                pass
        else:
            log_test(f"   ❌ Health check failed: {health_response.status_code}")
    except requests.exceptions.RequestException as e:
        log_test(f"   ❌ Health check error: {str(e)}")
    
    # Test 2: CORS Preflight
    try:
        preflight_headers = {
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        preflight_response = requests.options(
            f"{backend_url}/api/auth/login", 
            headers=preflight_headers, 
            timeout=10
        )
        
        log_test(f"   📡 CORS Preflight: {preflight_response.status_code}")
        
        # Extract CORS headers
        for header, value in preflight_response.headers.items():
            if 'access-control' in header.lower():
                results['cors_headers'][header] = value
        
        # Check if CORS is properly configured
        allow_origin = results['cors_headers'].get('Access-Control-Allow-Origin') or results['cors_headers'].get('access-control-allow-origin')
        
        if preflight_response.status_code in [200, 204] and allow_origin:
            results['cors_preflight'] = True
            log_test(f"   ✅ CORS Preflight successful")
            log_test(f"   ✅ Allow-Origin: {allow_origin}")
        else:
            log_test(f"   ❌ CORS Preflight failed")
            log_test(f"   ❌ Allow-Origin: {allow_origin or 'Missing'}")
        
    except requests.exceptions.RequestException as e:
        log_test(f"   ❌ CORS Preflight error: {str(e)}")
    
    # Test 3: Actual Login API
    if results['cors_preflight']:
        try:
            login_headers = {
                'Origin': frontend_origin,
                'Content-Type': 'application/json'
            }
            
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            login_response = requests.post(
                f"{backend_url}/api/auth/login",
                json=login_data,
                headers=login_headers,
                timeout=10
            )
            
            log_test(f"   📡 Login API: {login_response.status_code}")
            
            if login_response.status_code == 200:
                results['login_api'] = True
                log_test(f"   ✅ Login successful")
                try:
                    login_result = login_response.json()
                    if 'token' in login_result:
                        log_test(f"   ✅ JWT token received")
                    if 'practice' in login_result:
                        practice_name = login_result['practice'].get('name', 'Unknown')
                        log_test(f"   ✅ Practice: {practice_name}")
                except:
                    pass
            else:
                log_test(f"   ❌ Login failed: {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    log_test(f"   ❌ Error: {error_data}")
                except:
                    log_test(f"   ❌ Error: {login_response.text}")
                    
        except requests.exceptions.RequestException as e:
            log_test(f"   ❌ Login API error: {str(e)}")
    else:
        log_test(f"   ⏭️  Skipping login test (CORS preflight failed)")
    
    # Summary for this backend
    log_test(f"   📊 SUMMARY for {url_name}:")
    log_test(f"      Health: {'✅' if results['health'] else '❌'}")
    log_test(f"      CORS: {'✅' if results['cors_preflight'] else '❌'}")
    log_test(f"      Login: {'✅' if results['login_api'] else '❌'}")
    
    return results

def main():
    """Main backend URL verification test"""
    log_test("🚨 BACKEND URL VERIFICATION TEST")
    log_test("Determining which backend URL should be used")
    log_test("=" * 60)
    
    # URLs to test based on review request and .env files
    backend_urls_to_test = [
        {
            'url': 'https://dentist-portal-3.emergent.host',
            'name': 'REVIEW REQUEST URL',
            'description': 'URL mentioned in the review request as problematic'
        },
        {
            'url': 'https://app.dentalaftercarenotes.com', 
            'name': 'ENV FILE URL',
            'description': 'URL from frontend/.env REACT_APP_BACKEND_URL'
        }
    ]
    
    results = {}
    
    for backend_info in backend_urls_to_test:
        log_test(f"\n{backend_info['description']}")
        results[backend_info['name']] = test_backend_url_functionality(
            backend_info['url'], 
            backend_info['name']
        )
        log_test("-" * 50)
    
    # Final analysis
    log_test("\n🎯 FINAL ANALYSIS")
    log_test("=" * 30)
    
    working_backends = []
    for name, result in results.items():
        if result['health'] and result['cors_preflight'] and result['login_api']:
            working_backends.append(name)
            log_test(f"✅ {name}: FULLY FUNCTIONAL")
        else:
            issues = []
            if not result['health']:
                issues.append("Health")
            if not result['cors_preflight']:
                issues.append("CORS")
            if not result['login_api']:
                issues.append("Login")
            log_test(f"❌ {name}: ISSUES - {', '.join(issues)}")
    
    log_test("\n🔧 RECOMMENDATIONS:")
    
    if len(working_backends) == 1:
        log_test(f"✅ USE: {working_backends[0]} - This backend is fully functional")
        log_test("✅ SOLUTION: Update frontend to use the working backend URL")
    elif len(working_backends) > 1:
        log_test(f"✅ MULTIPLE OPTIONS: {', '.join(working_backends)} are working")
        log_test("✅ SOLUTION: Use the ENV FILE URL as it matches your configuration")
    else:
        log_test("❌ NO WORKING BACKENDS FOUND")
        log_test("❌ SOLUTION: Fix CORS configuration at ingress level")
    
    # Check current frontend configuration
    log_test("\n📋 CURRENT FRONTEND CONFIGURATION:")
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            log_test(f"Frontend .env content:")
            for line in env_content.strip().split('\n'):
                if 'REACT_APP_BACKEND_URL' in line:
                    log_test(f"   {line}")
    except:
        log_test("   Could not read frontend .env file")
    
    return len(working_backends) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)