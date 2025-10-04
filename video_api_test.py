#!/usr/bin/env python3
"""
URGENT VIDEO API AUTHENTICATION FIX TESTING
Testing the video API authentication fix for tutorial video playback issues.
"""

import requests
import json
import os
from pathlib import Path

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 URGENT VIDEO API AUTHENTICATION FIX TESTING")
print(f"🔗 Backend URL: {BACKEND_URL}")
print(f"🔗 API Base: {API_BASE}")
print("=" * 80)

def test_admin_login():
    """Test admin login to get authentication token"""
    print("\n1️⃣ TESTING ADMIN LOGIN")
    
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
                print(f"   ✅ Admin login successful")
                print(f"   🔑 Token received: {token[:50]}...")
                return token
            else:
                print(f"   ❌ No token in response: {data}")
                return None
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def test_backend_health():
    """Test if backend is running without import errors"""
    print("\n2️⃣ TESTING BACKEND HEALTH")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Backend is healthy")
            print(f"   📊 Response: {response.json()}")
            return True
        else:
            print(f"   ❌ Backend health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Backend health error: {e}")
        return False

def test_video_list_endpoint(token):
    """Test video list endpoint with authentication"""
    print("\n3️⃣ TESTING VIDEO LIST ENDPOINT")
    
    if not token:
        print("   ❌ No token available for testing")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/video/list", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Video list endpoint accessible")
            print(f"   📹 Videos found: {len(data.get('videos', []))}")
            
            videos = data.get('videos', [])
            for video in videos:
                print(f"      - {video.get('filename')} ({video.get('size')} bytes)")
            
            return videos
        elif response.status_code == 403:
            print(f"   ❌ AUTHENTICATION FAILED - 403 Forbidden")
            print(f"   🔍 Response: {response.text}")
            return False
        else:
            print(f"   ❌ Video list failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Video list error: {e}")
        return False

def test_video_serving_endpoint(token, filename="test.mp4"):
    """Test video serving endpoint with authentication"""
    print(f"\n4️⃣ TESTING VIDEO SERVING ENDPOINT: {filename}")
    
    if not token:
        print("   ❌ No token available for testing")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test HEAD request first (common for video players)
        response = requests.head(f"{API_BASE}/video/tutorial/{filename}", headers=headers, timeout=10)
        print(f"   HEAD Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ HEAD request successful")
            print(f"   📊 Content-Type: {response.headers.get('content-type')}")
            print(f"   📊 Content-Length: {response.headers.get('content-length')}")
            print(f"   📊 Accept-Ranges: {response.headers.get('accept-ranges')}")
        elif response.status_code == 403:
            print(f"   ❌ AUTHENTICATION FAILED - 403 Forbidden (HEAD)")
            print(f"   🔍 Headers sent: {headers}")
            return False
        else:
            print(f"   ❌ HEAD request failed: {response.status_code}")
        
        # Test GET request
        response = requests.get(f"{API_BASE}/video/tutorial/{filename}", headers=headers, timeout=10)
        print(f"   GET Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ GET request successful")
            print(f"   📊 Content-Type: {response.headers.get('content-type')}")
            print(f"   📊 Content-Length: {response.headers.get('content-length')}")
            print(f"   📊 Response size: {len(response.content)} bytes")
            return True
        elif response.status_code == 403:
            print(f"   ❌ AUTHENTICATION FAILED - 403 Forbidden (GET)")
            print(f"   🔍 Response: {response.text}")
            return False
        elif response.status_code == 404:
            print(f"   ❌ Video file not found: {filename}")
            return False
        else:
            print(f"   ❌ GET request failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Video serving error: {e}")
        return False

def test_video_streaming(token, filename="test.mp4"):
    """Test video streaming with Range requests"""
    print(f"\n5️⃣ TESTING VIDEO STREAMING: {filename}")
    
    if not token:
        print("   ❌ No token available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Range": "bytes=0-1023"  # Request first 1KB
    }
    
    try:
        response = requests.get(f"{API_BASE}/video/tutorial/{filename}", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 206:  # Partial Content
            print(f"   ✅ Video streaming working (206 Partial Content)")
            print(f"   📊 Content-Range: {response.headers.get('content-range')}")
            print(f"   📊 Content-Length: {response.headers.get('content-length')}")
            print(f"   📊 Response size: {len(response.content)} bytes")
            return True
        elif response.status_code == 200:
            print(f"   ⚠️ Full content returned instead of partial (streaming may not work optimally)")
            return True
        elif response.status_code == 403:
            print(f"   ❌ AUTHENTICATION FAILED - 403 Forbidden (Range)")
            return False
        else:
            print(f"   ❌ Streaming failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Video streaming error: {e}")
        return False

def test_unauthenticated_access():
    """Test that unauthenticated requests are properly rejected"""
    print(f"\n6️⃣ TESTING UNAUTHENTICATED ACCESS (Should be rejected)")
    
    try:
        # Test without token
        response = requests.get(f"{API_BASE}/video/tutorial/test.mp4", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401 or response.status_code == 403:
            print(f"   ✅ Unauthenticated access properly rejected")
            return True
        else:
            print(f"   ❌ Unauthenticated access allowed (security issue!)")
            print(f"   🔍 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Unauthenticated test error: {e}")
        return False

def main():
    """Run all video API tests"""
    print("🚀 Starting Video API Authentication Fix Testing...")
    
    results = {
        "admin_login": False,
        "backend_health": False,
        "video_list": False,
        "video_serving": False,
        "video_streaming": False,
        "unauthenticated_rejection": False
    }
    
    # Test backend health first
    results["backend_health"] = test_backend_health()
    
    # Test admin login
    token = test_admin_login()
    results["admin_login"] = token is not None
    
    if token:
        # Test video endpoints with authentication
        videos = test_video_list_endpoint(token)
        results["video_list"] = videos is not False
        
        results["video_serving"] = test_video_serving_endpoint(token)
        results["video_streaming"] = test_video_streaming(token)
    
    # Test unauthenticated access
    results["unauthenticated_rejection"] = test_unauthenticated_access()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 VIDEO API AUTHENTICATION FIX TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Video API authentication fix is working!")
    else:
        print("🚨 SOME TESTS FAILED - Video API authentication needs attention!")
        
        # Specific failure analysis
        if not results["admin_login"]:
            print("   🔍 Admin login failed - check credentials")
        if not results["backend_health"]:
            print("   🔍 Backend health failed - check server startup")
        if not results["video_list"] or not results["video_serving"]:
            print("   🔍 Video API authentication failed - check token verification")
        if not results["unauthenticated_rejection"]:
            print("   🔍 Security issue - unauthenticated access allowed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)