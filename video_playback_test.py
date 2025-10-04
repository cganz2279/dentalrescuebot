#!/usr/bin/env python3
"""
Video Playback Diagnostic Test
Focus: Diagnose why videos load (show controls) but don't actually play content
"""

import requests
import os
import sys
from pathlib import Path

# Get backend URL from environment
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

def test_video_api_endpoint():
    """Test the video API endpoint /api/video/tutorial/{filename} directly"""
    print("🎬 TESTING VIDEO API ENDPOINT")
    print("=" * 50)
    
    # Get list of available video files
    try:
        files_response = requests.get(f"{BACKEND_URL}/api/video/list", 
                                    headers={"Authorization": "Bearer test_token"})
        print(f"Video list endpoint status: {files_response.status_code}")
        
        if files_response.status_code == 401:
            print("❌ Video list requires authentication - this might be the issue!")
        elif files_response.status_code == 200:
            print("✅ Video list endpoint accessible")
            try:
                videos = files_response.json().get("videos", [])
                print(f"Found {len(videos)} videos: {[v['filename'] for v in videos]}")
            except:
                print("Could not parse video list response")
    except Exception as e:
        print(f"❌ Error accessing video list: {e}")
    
    # Test actual video files from directory listing
    video_files = ["test.mp4", "test_large.mp4", "5ca71a02-f593-40f8-ab29-b82c58345717.mp4"]
    
    for filename in video_files:
        print(f"\n🎥 Testing video file: {filename}")
        
        # Test without authentication first
        try:
            response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{filename}")
            print(f"  Status Code: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'Not set')}")
            print(f"  Content-Length: {response.headers.get('Content-Length', 'Not set')}")
            print(f"  Accept-Ranges: {response.headers.get('Accept-Ranges', 'Not set')}")
            print(f"  Cache-Control: {response.headers.get('Cache-Control', 'Not set')}")
            
            if response.status_code == 200:
                print("  ✅ Video endpoint accessible without authentication")
                content_length = len(response.content)
                print(f"  📊 Actual content size: {content_length} bytes")
                
                # Check if it's actually video content
                if content_length < 100:
                    print(f"  ⚠️ WARNING: Very small file size ({content_length} bytes) - might be corrupted")
                    print(f"  📄 Content preview: {response.content[:50]}")
                
            elif response.status_code == 401:
                print("  ❌ CRITICAL: Video endpoint requires authentication!")
                print("  🔍 This could be why videos don't play - authentication blocking")
            elif response.status_code == 404:
                print("  ❌ Video file not found")
            else:
                print(f"  ❌ Unexpected status code: {response.status_code}")
                print(f"  📄 Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Error accessing video: {e}")
        
        # Test with Range request (video seeking)
        try:
            headers = {"Range": "bytes=0-1023"}
            range_response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{filename}", headers=headers)
            print(f"  📡 Range request status: {range_response.status_code}")
            
            if range_response.status_code == 206:
                print("  ✅ Range requests supported (good for video seeking)")
                print(f"  📊 Content-Range: {range_response.headers.get('Content-Range', 'Not set')}")
            elif range_response.status_code == 200:
                print("  ⚠️ Range request returned full file (suboptimal for video)")
            else:
                print(f"  ❌ Range request failed: {range_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error with range request: {e}")

def test_video_file_storage():
    """Check video file storage and accessibility"""
    print("\n📁 TESTING VIDEO FILE STORAGE")
    print("=" * 50)
    
    uploads_dir = "/app/uploads/tutorials/"
    
    if not os.path.exists(uploads_dir):
        print("❌ CRITICAL: Uploads directory does not exist!")
        return
    
    print(f"✅ Uploads directory exists: {uploads_dir}")
    
    # List all files
    try:
        files = os.listdir(uploads_dir)
        print(f"📂 Found {len(files)} files:")
        
        for file in files:
            file_path = os.path.join(uploads_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                permissions = oct(os.stat(file_path).st_mode)[-3:]
                print(f"  📄 {file}: {size} bytes, permissions: {permissions}")
                
                # Check if file is readable
                try:
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(20)
                        print(f"    🔍 First 20 bytes: {first_bytes}")
                        
                        # Check for video file signatures
                        if first_bytes.startswith(b'\x00\x00\x00'):
                            if b'ftyp' in first_bytes:
                                print("    ✅ Valid MP4 file signature detected")
                            else:
                                print("    ⚠️ Possible MP4 but unclear signature")
                        else:
                            print("    ❌ Does not appear to be a valid video file")
                            
                except Exception as e:
                    print(f"    ❌ Cannot read file: {e}")
            else:
                print(f"  📁 {file}: Directory")
                
    except Exception as e:
        print(f"❌ Error listing files: {e}")

def test_cors_headers():
    """Test CORS headers for cross-origin requests"""
    print("\n🌐 TESTING CORS HEADERS")
    print("=" * 50)
    
    video_files = ["test.mp4", "test_large.mp4"]
    
    for filename in video_files:
        print(f"\n🎥 Testing CORS for: {filename}")
        
        try:
            # Test preflight request
            preflight_headers = {
                "Origin": "https://app.dentalaftercarenotes.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Range"
            }
            
            preflight_response = requests.options(f"{BACKEND_URL}/api/video/tutorial/{filename}", 
                                                headers=preflight_headers)
            print(f"  Preflight status: {preflight_response.status_code}")
            print(f"  Access-Control-Allow-Origin: {preflight_response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
            print(f"  Access-Control-Allow-Methods: {preflight_response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
            print(f"  Access-Control-Allow-Headers: {preflight_response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
            
            # Test actual request with Origin header
            actual_headers = {"Origin": "https://app.dentalaftercarenotes.com"}
            actual_response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{filename}", 
                                         headers=actual_headers)
            print(f"  Actual request status: {actual_response.status_code}")
            print(f"  CORS Allow-Origin: {actual_response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
            
            if actual_response.headers.get('Access-Control-Allow-Origin') in ['*', 'https://app.dentalaftercarenotes.com']:
                print("  ✅ CORS headers allow frontend access")
            else:
                print("  ❌ CORS headers may block frontend access")
                
        except Exception as e:
            print(f"  ❌ Error testing CORS: {e}")

def test_authentication_requirements():
    """Test if video endpoint still requires admin auth"""
    print("\n🔐 TESTING AUTHENTICATION REQUIREMENTS")
    print("=" * 50)
    
    video_files = ["test.mp4", "test_large.mp4"]
    
    for filename in video_files:
        print(f"\n🎥 Testing auth for: {filename}")
        
        # Test without any authentication
        try:
            response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{filename}")
            print(f"  No auth status: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ Video accessible without authentication (correct)")
            elif response.status_code == 401:
                print("  ❌ CRITICAL: Video requires authentication (this blocks playback!)")
            elif response.status_code == 403:
                print("  ❌ CRITICAL: Video access forbidden (this blocks playback!)")
            else:
                print(f"  ⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error testing no auth: {e}")
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{filename}", headers=headers)
            print(f"  Invalid token status: {response.status_code}")
            
        except Exception as e:
            print(f"  ❌ Error testing invalid token: {e}")

def test_video_streaming_functionality():
    """Test video streaming functionality in detail"""
    print("\n📺 TESTING VIDEO STREAMING FUNCTIONALITY")
    print("=" * 50)
    
    filename = "test_large.mp4"  # Use the larger file for better testing
    
    print(f"🎥 Testing streaming for: {filename}")
    
    try:
        # Get full file info first
        response = requests.head(f"{BACKEND_URL}/api/video/tutorial/{filename}")
        print(f"HEAD request status: {response.status_code}")
        
        if response.status_code == 200:
            content_length = response.headers.get('Content-Length')
            content_type = response.headers.get('Content-Type')
            accept_ranges = response.headers.get('Accept-Ranges')
            
            print(f"  Content-Length: {content_length}")
            print(f"  Content-Type: {content_type}")
            print(f"  Accept-Ranges: {accept_ranges}")
            
            # Validate MIME type
            if content_type and content_type.startswith('video/'):
                print("  ✅ Correct video MIME type")
            else:
                print(f"  ❌ CRITICAL: Wrong MIME type: {content_type}")
                print("  🔍 This could prevent video playback!")
            
            # Test range requests
            if accept_ranges == 'bytes':
                print("  ✅ Range requests supported")
                
                # Test specific range request
                range_headers = {"Range": "bytes=0-1023"}
                range_response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{filename}", 
                                            headers=range_headers)
                
                print(f"  Range request status: {range_response.status_code}")
                
                if range_response.status_code == 206:
                    print("  ✅ Partial content served correctly")
                    content_range = range_response.headers.get('Content-Range')
                    print(f"  Content-Range: {content_range}")
                else:
                    print(f"  ❌ Range request failed: {range_response.status_code}")
            else:
                print("  ❌ Range requests not supported - may affect video seeking")
                
        else:
            print(f"❌ HEAD request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing streaming: {e}")

def test_video_urls():
    """Test if video URLs are correctly formed"""
    print("\n🔗 TESTING VIDEO URL FORMATION")
    print("=" * 50)
    
    # Test different URL patterns that might be used
    url_patterns = [
        "/api/video/tutorial/test.mp4",
        "/uploads/tutorials/test.mp4",
        f"{BACKEND_URL}/api/video/tutorial/test.mp4",
        f"{BACKEND_URL}/uploads/tutorials/test.mp4"
    ]
    
    for url_pattern in url_patterns:
        print(f"\n🔗 Testing URL pattern: {url_pattern}")
        
        try:
            if url_pattern.startswith('http'):
                response = requests.get(url_pattern)
            else:
                response = requests.get(f"{BACKEND_URL}{url_pattern}")
                
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ URL pattern works")
                content_type = response.headers.get('Content-Type', 'Not set')
                print(f"  Content-Type: {content_type}")
            elif response.status_code == 404:
                print("  ❌ URL pattern not found")
            else:
                print(f"  ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    """Run all video playback diagnostic tests"""
    print("🎬 VIDEO PLAYBACK DIAGNOSTIC TEST")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    # Run all tests
    test_video_api_endpoint()
    test_video_file_storage()
    test_cors_headers()
    test_authentication_requirements()
    test_video_streaming_functionality()
    test_video_urls()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("Check the output above for:")
    print("❌ Authentication blocking video access")
    print("❌ Incorrect MIME types")
    print("❌ CORS issues")
    print("❌ Missing or corrupted video files")
    print("❌ Malformed video URLs")
    print("❌ Range request problems")

if __name__ == "__main__":
    main()