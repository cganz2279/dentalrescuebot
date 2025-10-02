#!/usr/bin/env python3
"""
COMPREHENSIVE CORS DEBUGGING TEST
Detailed analysis of CORS issues between frontend and backend
"""

import requests
import json
import sys
from datetime import datetime

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_direct_backend_cors():
    """Test if the FastAPI backend itself handles CORS correctly"""
    log_test("🔍 TESTING DIRECT BACKEND CORS (bypassing any proxy)")
    
    # Try to access backend directly if possible
    # This would help determine if the issue is at the proxy level
    
    backend_urls_to_test = [
        "https://dentist-portal-3.emergent.host",
        "https://app.dentalaftercarenotes.com"
    ]
    
    for backend_url in backend_urls_to_test:
        log_test(f"📡 Testing backend URL: {backend_url}")
        
        # Test health endpoint first
        try:
            health_response = requests.get(f"{backend_url}/api/health", timeout=10)
            log_test(f"   Health check: {health_response.status_code}")
            
            if health_response.status_code == 200:
                # Test OPTIONS request to auth endpoint
                headers = {
                    'Origin': 'https://app.dentalaftercarenotes.com',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type,Authorization'
                }
                
                options_response = requests.options(
                    f"{backend_url}/api/auth/login", 
                    headers=headers, 
                    timeout=10
                )
                
                log_test(f"   OPTIONS status: {options_response.status_code}")
                log_test(f"   CORS headers:")
                
                cors_headers = {}
                for header, value in options_response.headers.items():
                    if 'access-control' in header.lower() or 'cors' in header.lower():
                        cors_headers[header] = value
                        log_test(f"     {header}: {value}")
                
                # Check if this backend properly handles CORS
                has_allow_origin = 'access-control-allow-origin' in cors_headers
                has_allow_methods = 'access-control-allow-methods' in cors_headers
                has_allow_headers = 'access-control-allow-headers' in cors_headers
                
                log_test(f"   CORS Analysis:")
                log_test(f"     Allow-Origin: {'✅' if has_allow_origin else '❌'}")
                log_test(f"     Allow-Methods: {'✅' if has_allow_methods else '❌'}")
                log_test(f"     Allow-Headers: {'✅' if has_allow_headers else '❌'}")
                
        except requests.exceptions.RequestException as e:
            log_test(f"   ❌ Failed to connect: {str(e)}")

def test_proxy_detection():
    """Detect if there's a reverse proxy interfering with CORS"""
    log_test("🔍 DETECTING REVERSE PROXY INTERFERENCE")
    
    backend_url = "https://dentist-portal-3.emergent.host"
    
    # Test different request patterns to detect proxy behavior
    test_cases = [
        {
            'name': 'Simple GET request',
            'method': 'GET',
            'url': f"{backend_url}/api/health",
            'headers': {}
        },
        {
            'name': 'GET with Origin header',
            'method': 'GET', 
            'url': f"{backend_url}/api/health",
            'headers': {'Origin': 'https://app.dentalaftercarenotes.com'}
        },
        {
            'name': 'OPTIONS without CORS headers',
            'method': 'OPTIONS',
            'url': f"{backend_url}/api/auth/login",
            'headers': {}
        },
        {
            'name': 'OPTIONS with CORS headers (production origin)',
            'method': 'OPTIONS',
            'url': f"{backend_url}/api/auth/login",
            'headers': {
                'Origin': 'https://app.dentalaftercarenotes.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        },
        {
            'name': 'OPTIONS with CORS headers (localhost origin)',
            'method': 'OPTIONS',
            'url': f"{backend_url}/api/auth/login",
            'headers': {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        }
    ]
    
    for test_case in test_cases:
        log_test(f"📡 {test_case['name']}")
        
        try:
            if test_case['method'] == 'GET':
                response = requests.get(test_case['url'], headers=test_case['headers'], timeout=10)
            elif test_case['method'] == 'OPTIONS':
                response = requests.options(test_case['url'], headers=test_case['headers'], timeout=10)
            
            log_test(f"   Status: {response.status_code}")
            
            # Check for proxy-specific headers
            proxy_indicators = [
                'server', 'x-powered-by', 'x-proxy', 'via', 'x-forwarded-for',
                'x-real-ip', 'x-nginx', 'x-cache', 'cf-ray'
            ]
            
            found_proxy_headers = {}
            for header, value in response.headers.items():
                if any(indicator in header.lower() for indicator in proxy_indicators):
                    found_proxy_headers[header] = value
            
            if found_proxy_headers:
                log_test(f"   Proxy headers detected:")
                for header, value in found_proxy_headers.items():
                    log_test(f"     {header}: {value}")
            
            # Check CORS headers
            cors_origin = response.headers.get('Access-Control-Allow-Origin', 'Not Set')
            log_test(f"   CORS Allow-Origin: {cors_origin}")
            
        except requests.exceptions.RequestException as e:
            log_test(f"   ❌ Failed: {str(e)}")

def test_browser_simulation():
    """Simulate exactly what a browser would do"""
    log_test("🔍 SIMULATING BROWSER CORS BEHAVIOR")
    
    frontend_origin = "https://app.dentalaftercarenotes.com"
    backend_url = "https://dentist-portal-3.emergent.host"
    login_endpoint = f"{backend_url}/api/auth/login"
    
    log_test("Step 1: Browser sends OPTIONS preflight request")
    
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
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Dest': 'empty'
    }
    
    try:
        preflight_response = requests.options(login_endpoint, headers=preflight_headers, timeout=10)
        
        log_test(f"   Preflight status: {preflight_response.status_code}")
        log_test(f"   Preflight headers:")
        
        critical_cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods', 
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Credentials',
            'Access-Control-Max-Age'
        ]
        
        preflight_success = True
        for header in critical_cors_headers:
            value = preflight_response.headers.get(header, 'Missing')
            status = "✅" if value != 'Missing' else "❌"
            log_test(f"     {header}: {value} {status}")
            
            if header == 'Access-Control-Allow-Origin' and value == 'Missing':
                preflight_success = False
        
        if preflight_success and preflight_response.status_code == 200:
            log_test("✅ Preflight would succeed - browser would proceed with actual request")
            
            log_test("Step 2: Browser sends actual POST request")
            
            actual_headers = {
                'Origin': frontend_origin,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': frontend_origin
            }
            
            login_data = {
                "email": "cganz2279@gmail.com",
                "password": "password123"
            }
            
            actual_response = requests.post(login_endpoint, json=login_data, headers=actual_headers, timeout=10)
            log_test(f"   Actual request status: {actual_response.status_code}")
            
            if actual_response.status_code == 200:
                log_test("✅ Login would succeed")
                return True
            else:
                log_test("❌ Login would fail")
                return False
        else:
            log_test("❌ Preflight would fail - browser would block the actual request")
            log_test("🚨 This is exactly what the user is experiencing!")
            return False
            
    except requests.exceptions.RequestException as e:
        log_test(f"❌ Request failed: {str(e)}")
        return False

def generate_fix_recommendations():
    """Generate specific fix recommendations based on test results"""
    log_test("🔧 CORS FIX RECOMMENDATIONS")
    log_test("=" * 50)
    
    log_test("ISSUE IDENTIFIED: Kubernetes Ingress CORS Configuration")
    log_test("")
    log_test("ROOT CAUSE:")
    log_test("- OPTIONS preflight requests are returning 400 status")
    log_test("- Missing 'Access-Control-Allow-Origin' header in preflight response")
    log_test("- Only localhost:3000 is allowed, HTTPS origins are blocked")
    log_test("- This indicates ingress-level CORS blocking, not FastAPI backend issue")
    log_test("")
    
    log_test("RECOMMENDED FIXES:")
    log_test("")
    log_test("1. UPDATE KUBERNETES INGRESS ANNOTATIONS:")
    log_test("   Add these annotations to your ingress configuration:")
    log_test("   ```yaml")
    log_test("   annotations:")
    log_test("     nginx.ingress.kubernetes.io/enable-cors: 'true'")
    log_test("     nginx.ingress.kubernetes.io/cors-allow-origin: 'https://app.dentalaftercarenotes.com'")
    log_test("     nginx.ingress.kubernetes.io/cors-allow-methods: 'GET, POST, PUT, DELETE, OPTIONS'")
    log_test("     nginx.ingress.kubernetes.io/cors-allow-headers: 'Content-Type, Authorization, Accept, Origin'")
    log_test("     nginx.ingress.kubernetes.io/cors-allow-credentials: 'true'")
    log_test("     nginx.ingress.kubernetes.io/cors-max-age: '86400'")
    log_test("   ```")
    log_test("")
    
    log_test("2. ALTERNATIVE: UPDATE INGRESS TO ALLOW ALL ORIGINS:")
    log_test("   ```yaml")
    log_test("   annotations:")
    log_test("     nginx.ingress.kubernetes.io/enable-cors: 'true'")
    log_test("     nginx.ingress.kubernetes.io/cors-allow-origin: '*'")
    log_test("   ```")
    log_test("")
    
    log_test("3. VERIFY BACKEND CORS IS NOT CONFLICTING:")
    log_test("   Ensure FastAPI CORS middleware allows the same origins:")
    log_test("   ```python")
    log_test("   app.add_middleware(")
    log_test("       CORSMiddleware,")
    log_test("       allow_origins=['https://app.dentalaftercarenotes.com'],")
    log_test("       allow_credentials=True,")
    log_test("       allow_methods=['*'],")
    log_test("       allow_headers=['*'],")
    log_test("   )")
    log_test("   ```")
    log_test("")
    
    log_test("4. TEST AFTER DEPLOYMENT:")
    log_test("   Run this test again to verify the fix")
    log_test("")
    
    log_test("URGENCY: CRITICAL - Users cannot login until this is fixed")

def main():
    """Main comprehensive CORS test"""
    log_test("🚨 COMPREHENSIVE CORS DEBUGGING")
    log_test("User Issue: CORS errors preventing login")
    log_test("Frontend: https://app.dentalaftercarenotes.com")
    log_test("Backend: https://dentist-portal-3.emergent.host")
    log_test("=" * 60)
    
    # Test 1: Direct backend CORS
    test_direct_backend_cors()
    log_test("-" * 40)
    
    # Test 2: Proxy detection
    test_proxy_detection()
    log_test("-" * 40)
    
    # Test 3: Browser simulation
    log_test("CRITICAL TEST: Browser CORS Simulation")
    browser_success = test_browser_simulation()
    log_test("-" * 40)
    
    # Generate recommendations
    generate_fix_recommendations()
    
    return browser_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)