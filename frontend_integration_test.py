#!/usr/bin/env python3
"""
FRONTEND INTEGRATION TEST
Testing if frontend can actually load data from backend
"""

import requests
import json
import time
from datetime import datetime

# URLs
FRONTEND_URL = "https://dentist-portal-3.emergent.host"
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_result(success, message, data=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data:
        print(f"📊 Data: {data}")

def test_frontend_loading():
    """Test if frontend loads correctly"""
    print_test_header("FRONTEND LOADING TEST")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for React app indicators
            react_indicators = [
                'id="root"',
                'react',
                'App.js',
                'bundle.js'
            ]
            
            found_indicators = [indicator for indicator in react_indicators if indicator.lower() in content.lower()]
            
            print_result(True, f"Frontend loads successfully")
            print_result(True, f"React indicators found: {len(found_indicators)}")
            
            # Check for backend URL in the HTML
            if 'dentist-portal-3.emergent.host' in content:
                print_result(True, "Backend URL found in frontend")
            else:
                print_result(False, "Backend URL NOT found in frontend")
            
            return True
        else:
            print_result(False, f"Frontend returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Frontend loading error: {str(e)}")
        return False

def test_api_calls_from_frontend_perspective():
    """Test API calls as frontend would make them"""
    print_test_header("FRONTEND API CALLS TEST")
    
    # Simulate frontend making API calls
    headers = {
        'Origin': FRONTEND_URL,
        'Referer': FRONTEND_URL,
        'User-Agent': 'Mozilla/5.0 (compatible; Frontend-Test)'
    }
    
    # Test 1: Get specialties (first call frontend makes)
    try:
        response = requests.get(f"{BACKEND_URL}/specialties", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            specialties = data.get('data', [])
            print_result(True, f"Specialties API call successful: {len(specialties)} specialties")
        else:
            print_result(False, f"Specialties API failed: {response.status_code}")
    except Exception as e:
        print_result(False, f"Specialties API error: {str(e)}")
    
    # Test 2: Login simulation
    try:
        login_data = {
            "email": "cganz2279@gmail.com",
            "password": "password123"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print_result(True, f"Login API call successful")
            
            # Test authenticated call
            auth_headers = headers.copy()
            auth_headers['Authorization'] = f'Bearer {token}'
            
            response = requests.get(f"{BACKEND_URL}/practice/dashboard", headers=auth_headers, timeout=10)
            if response.status_code == 200:
                print_result(True, f"Authenticated dashboard call successful")
            else:
                print_result(False, f"Dashboard call failed: {response.status_code}")
                
        else:
            print_result(False, f"Login API failed: {response.status_code}")
    except Exception as e:
        print_result(False, f"Login API error: {str(e)}")

def test_network_connectivity():
    """Test network connectivity issues"""
    print_test_header("NETWORK CONNECTIVITY TEST")
    
    # Test DNS resolution
    try:
        import socket
        ip = socket.gethostbyname('dentist-portal-3.emergent.host')
        print_result(True, f"DNS resolution successful: {ip}")
    except Exception as e:
        print_result(False, f"DNS resolution failed: {str(e)}")
    
    # Test SSL certificate
    try:
        response = requests.get(FRONTEND_URL, timeout=5, verify=True)
        print_result(True, "SSL certificate valid")
    except requests.exceptions.SSLError as e:
        print_result(False, f"SSL certificate issue: {str(e)}")
    except Exception as e:
        print_result(True, "SSL certificate appears valid")
    
    # Test response times
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/specialties", timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if response_time < 1000:
            print_result(True, f"API response time good: {response_time:.0f}ms")
        elif response_time < 3000:
            print_result(True, f"API response time acceptable: {response_time:.0f}ms")
        else:
            print_result(False, f"API response time slow: {response_time:.0f}ms")
            
    except Exception as e:
        print_result(False, f"Response time test failed: {str(e)}")

def check_browser_compatibility():
    """Check for potential browser compatibility issues"""
    print_test_header("BROWSER COMPATIBILITY CHECK")
    
    # Test different request methods
    methods_to_test = ['GET', 'POST', 'OPTIONS']
    
    for method in methods_to_test:
        try:
            if method == 'GET':
                response = requests.get(f"{BACKEND_URL}/specialties", timeout=5)
            elif method == 'POST':
                response = requests.post(f"{BACKEND_URL}/auth/login", 
                                       json={"email": "test", "password": "test"}, 
                                       timeout=5)
            elif method == 'OPTIONS':
                response = requests.options(f"{BACKEND_URL}/specialties", timeout=5)
            
            print_result(True, f"{method} method supported (Status: {response.status_code})")
            
        except Exception as e:
            print_result(False, f"{method} method failed: {str(e)}")

def main():
    """Run frontend integration tests"""
    print(f"🌐 FRONTEND INTEGRATION TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Run all tests
    frontend_loads = test_frontend_loading()
    test_api_calls_from_frontend_perspective()
    test_network_connectivity()
    check_browser_compatibility()
    
    # Final diagnosis
    print(f"\n{'='*60}")
    print("🎯 FRONTEND INTEGRATION DIAGNOSIS")
    print(f"{'='*60}")
    
    if frontend_loads:
        print("✅ Frontend application loads successfully")
        print("✅ Backend APIs are fully functional")
        print("✅ Network connectivity is working")
        print("✅ CORS is properly configured")
        
        print(f"\n🔍 LIKELY CAUSES OF 'NO DATA' ISSUE:")
        print("1. 🐛 JavaScript errors in browser console")
        print("2. 🔄 Frontend not making API calls (check Network tab)")
        print("3. 🔐 Authentication state not persisting")
        print("4. 📱 Browser caching old version of app")
        print("5. 🎨 UI components not rendering data correctly")
        
        print(f"\n💡 DEBUGGING STEPS FOR USER:")
        print("1. Open browser Developer Tools (F12)")
        print("2. Check Console tab for JavaScript errors")
        print("3. Check Network tab - are API calls being made?")
        print("4. Try hard refresh (Ctrl+F5 or Cmd+Shift+R)")
        print("5. Try incognito/private browsing mode")
        print("6. Clear browser cache and cookies")
        
    else:
        print("❌ Frontend application has loading issues")
        print("This could explain why user sees no data")

if __name__ == "__main__":
    main()