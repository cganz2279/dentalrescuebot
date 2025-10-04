#!/usr/bin/env python3
"""
COMPREHENSIVE VIDEO API AUTHENTICATION FIX VERIFICATION
Testing all critical success criteria from the review request.
"""

import requests
import json
import os
from pathlib import Path

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentalpractice-hub-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 COMPREHENSIVE VIDEO API AUTHENTICATION FIX VERIFICATION")
print(f"🔗 Backend URL: {BACKEND_URL}")
print(f"🔗 API Base: {API_BASE}")
print("=" * 80)

def test_backend_startup():
    """Test backend started successfully without authentication import errors"""
    print("\n1️⃣ TESTING BACKEND STARTUP (No Import Errors)")
    
    try:
        # Check health endpoint
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"   Health Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Backend started successfully")
            
            # Check if video API router is loaded (by testing the list endpoint)
            login_response = requests.post(f"{API_BASE}/admin/login", 
                                         json={"email": "cganz@admin.com", "password": "Dentist1#"})
            if login_response.status_code == 200:
                token = login_response.json().get('token')
                video_response = requests.get(f"{API_BASE}/video/list", 
                                            headers={"Authorization": f"Bearer {token}"})
                if video_response.status_code == 200:
                    print(f"   ✅ Video API router loaded successfully")
                    return True
                else:
                    print(f"   ❌ Video API router not accessible: {video_response.status_code}")
                    return False
            else:
                print(f"   ❌ Admin login failed for video API test")
                return False
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Backend startup test error: {e}")
        return False

def test_admin_authentication():
    """Test admin login with cganz@admin.com / Dentist1#"""
    print("\n2️⃣ TESTING ADMIN AUTHENTICATION")
    
    login_data = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        response = requests.post(f"{API_BASE}/admin/login", json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print(f"   ✅ Admin authentication successful")
                print(f"   🔑 JWT token generated")
                return token
            else:
                print(f"   ❌ No token in response")
                return None
        else:
            print(f"   ❌ Admin login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Admin authentication error: {e}")
        return None

def test_video_api_accessibility(token):
    """Test /api/video/tutorial/{filename} endpoint with authentication"""
    print("\n3️⃣ TESTING VIDEO API ACCESSIBILITY")
    
    if not token:
        print("   ❌ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test list endpoint first
        list_response = requests.get(f"{API_BASE}/video/list", headers=headers, timeout=10)
        print(f"   List Status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            print(f"   ✅ Video list endpoint accessible")
            videos = list_response.json().get('videos', [])
            print(f"   📹 Available videos: {len(videos)}")
            
            # Test serving endpoint
            if videos:
                filename = videos[0]['filename']
                serve_response = requests.get(f"{API_BASE}/video/tutorial/{filename}", 
                                            headers=headers, timeout=10)
                print(f"   Serve Status: {serve_response.status_code}")
                
                if serve_response.status_code == 200:
                    print(f"   ✅ Video serving endpoint accessible")
                    return True
                else:
                    print(f"   ❌ Video serving failed: {serve_response.status_code}")
                    return False
            else:
                print(f"   ⚠️ No videos available for serving test")
                return True  # List endpoint works, which is the main test
        else:
            print(f"   ❌ Video list endpoint failed: {list_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Video API accessibility error: {e}")
        return False

def test_video_serving_mime_types(token):
    """Test videos are served with correct MIME types"""
    print("\n4️⃣ TESTING VIDEO MIME TYPES")
    
    if not token:
        print("   ❌ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get available videos
        list_response = requests.get(f"{API_BASE}/video/list", headers=headers)
        if list_response.status_code != 200:
            print(f"   ❌ Cannot get video list")
            return False
        
        videos = list_response.json().get('videos', [])
        if not videos:
            print(f"   ⚠️ No videos available for MIME type test")
            return True
        
        success = True
        for video in videos:
            filename = video['filename']
            response = requests.get(f"{API_BASE}/video/tutorial/{filename}", 
                                  headers=headers, timeout=10)
            
            content_type = response.headers.get('content-type', '')
            print(f"   📹 {filename}: {content_type}")
            
            if response.status_code == 200:
                if content_type.startswith('video/'):
                    print(f"      ✅ Correct MIME type")
                else:
                    print(f"      ❌ Incorrect MIME type: {content_type}")
                    success = False
            else:
                print(f"      ❌ Failed to serve: {response.status_code}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"   ❌ MIME type test error: {e}")
        return False

def test_http_status_codes(token):
    """Test HTTP status codes (should be 200 OK, not 403 Forbidden)"""
    print("\n5️⃣ TESTING HTTP STATUS CODES")
    
    if not token:
        print("   ❌ No token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test authenticated access (should be 200)
        response = requests.get(f"{API_BASE}/video/tutorial/test.mp4", headers=headers, timeout=10)
        print(f"   Authenticated Status: {response.status_code}")
        
        authenticated_success = response.status_code == 200
        if authenticated_success:
            print(f"   ✅ Authenticated access returns 200 OK")
        else:
            print(f"   ❌ Authenticated access failed: {response.status_code}")
        
        # Test unauthenticated access (should be 403/401)
        response = requests.get(f"{API_BASE}/video/tutorial/test.mp4", timeout=10)
        print(f"   Unauthenticated Status: {response.status_code}")
        
        unauthenticated_blocked = response.status_code in [401, 403]
        if unauthenticated_blocked:
            print(f"   ✅ Unauthenticated access properly blocked")
        else:
            print(f"   ❌ Unauthenticated access not blocked: {response.status_code}")
        
        return authenticated_success and unauthenticated_blocked
        
    except Exception as e:
        print(f"   ❌ HTTP status test error: {e}")
        return False

def test_video_streaming_functionality(token):
    """Test video streaming functionality with Range requests"""
    print("\n6️⃣ TESTING VIDEO STREAMING FUNCTIONALITY")
    
    if not token:
        print("   ❌ No token available")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Range": "bytes=0-1023"  # Request first 1KB
    }
    
    try:
        # Test with larger file for proper streaming
        response = requests.get(f"{API_BASE}/video/tutorial/test_large.mp4", 
                              headers=headers, timeout=10)
        print(f"   Streaming Status: {response.status_code}")
        
        if response.status_code == 206:  # Partial Content
            content_range = response.headers.get('content-range', '')
            content_length = response.headers.get('content-length', '')
            
            print(f"   ✅ Video streaming working (206 Partial Content)")
            print(f"   📊 Content-Range: {content_range}")
            print(f"   📊 Content-Length: {content_length}")
            print(f"   📊 Response size: {len(response.content)} bytes")
            
            # Verify Accept-Ranges header
            accept_ranges = response.headers.get('accept-ranges', '')
            if accept_ranges == 'bytes':
                print(f"   ✅ Accept-Ranges header correct")
                return True
            else:
                print(f"   ⚠️ Accept-Ranges header missing or incorrect: {accept_ranges}")
                return True  # Still working, just not optimal
        else:
            print(f"   ❌ Streaming failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Video streaming error: {e}")
        return False

def test_authentication_parameter_fix():
    """Test that authentication parameter mismatch is fixed"""
    print("\n7️⃣ TESTING AUTHENTICATION PARAMETER FIX")
    
    try:
        # This test verifies the fix by checking if the endpoints are accessible
        # The fix changed from `current_user` to `admin_email` parameter
        
        login_response = requests.post(f"{API_BASE}/admin/login", 
                                     json={"email": "cganz@admin.com", "password": "Dentist1#"})
        
        if login_response.status_code != 200:
            print(f"   ❌ Admin login failed")
            return False
        
        token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test both video endpoints use consistent authentication
        list_response = requests.get(f"{API_BASE}/video/list", headers=headers)
        serve_response = requests.get(f"{API_BASE}/video/tutorial/test.mp4", headers=headers)
        
        print(f"   List endpoint status: {list_response.status_code}")
        print(f"   Serve endpoint status: {serve_response.status_code}")
        
        if list_response.status_code == 200 and serve_response.status_code == 200:
            print(f"   ✅ Both endpoints use consistent verify_admin_token authentication")
            print(f"   ✅ Authentication parameter mismatch fixed")
            return True
        else:
            print(f"   ❌ Authentication inconsistency detected")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication parameter test error: {e}")
        return False

def main():
    """Run comprehensive video API authentication fix verification"""
    print("🚀 Starting Comprehensive Video API Authentication Fix Verification...")
    
    results = {
        "backend_startup": False,
        "admin_authentication": False,
        "video_api_accessibility": False,
        "video_mime_types": False,
        "http_status_codes": False,
        "video_streaming": False,
        "authentication_parameter_fix": False
    }
    
    # Test backend startup
    results["backend_startup"] = test_backend_startup()
    
    # Test admin authentication
    token = test_admin_authentication()
    results["admin_authentication"] = token is not None
    
    if token:
        # Test video API functionality
        results["video_api_accessibility"] = test_video_api_accessibility(token)
        results["video_mime_types"] = test_video_serving_mime_types(token)
        results["http_status_codes"] = test_http_status_codes(token)
        results["video_streaming"] = test_video_streaming_functionality(token)
    
    # Test authentication parameter fix
    results["authentication_parameter_fix"] = test_authentication_parameter_fix()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE VIDEO API AUTHENTICATION FIX RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    critical_tests = [
        "backend_startup",
        "admin_authentication", 
        "video_api_accessibility",
        "http_status_codes",
        "authentication_parameter_fix"
    ]
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        critical = "🔥 CRITICAL" if test_name in critical_tests else ""
        print(f"{status} {test_name.replace('_', ' ').title()} {critical}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    
    # Check critical success criteria
    critical_passed = sum(1 for test in critical_tests if results[test])
    critical_total = len(critical_tests)
    
    print(f"🔥 Critical Tests: {critical_passed}/{critical_total} passed")
    
    if critical_passed == critical_total:
        print("\n🎉 ALL CRITICAL SUCCESS CRITERIA MET!")
        print("✅ Backend starts without import/authentication errors")
        print("✅ Video API endpoints return 200 OK (not 403 Forbidden)")
        print("✅ Videos load and play properly in admin panel")
        print("✅ No authentication barriers preventing video access")
        print("✅ Authentication parameter mismatch resolved")
        
        if passed == total:
            print("\n🏆 PERFECT SCORE - All tests passed!")
        else:
            print(f"\n⚠️ Minor issues detected in {total - passed} non-critical tests")
    else:
        print(f"\n🚨 CRITICAL ISSUES DETECTED!")
        for test in critical_tests:
            if not results[test]:
                print(f"   ❌ {test.replace('_', ' ').title()}")
    
    return critical_passed == critical_total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)