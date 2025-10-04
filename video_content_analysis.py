#!/usr/bin/env python3
"""
Video Content Analysis - Deep dive into video file issues
"""

import requests
import os
import sys
from pathlib import Path

BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

def analyze_video_files():
    """Analyze the actual video files to understand why they don't play"""
    print("🔍 ANALYZING VIDEO FILE CONTENT")
    print("=" * 50)
    
    uploads_dir = "/app/uploads/tutorials/"
    
    for file in os.listdir(uploads_dir):
        if file.endswith('.mp4'):
            file_path = os.path.join(uploads_dir, file)
            size = os.path.getsize(file_path)
            
            print(f"\n📄 Analyzing: {file} ({size} bytes)")
            
            # Read first 100 bytes to analyze content
            with open(file_path, 'rb') as f:
                content = f.read(100)
                
            print(f"  📊 First 50 bytes (hex): {content[:50].hex()}")
            print(f"  📊 First 50 bytes (text): {content[:50]}")
            
            # Check for valid MP4 signatures
            if content.startswith(b'\x00\x00\x00'):
                # Look for ftyp box
                if b'ftyp' in content[:20]:
                    print("  ✅ Valid MP4 file header detected")
                    
                    # Check MP4 brand
                    if b'mp41' in content[:30]:
                        print("  ✅ MP4 version 1 format")
                    elif b'mp42' in content[:30]:
                        print("  ✅ MP4 version 2 format")
                    else:
                        print("  ⚠️ Unknown MP4 brand")
                else:
                    print("  ❌ Missing ftyp box - not a valid MP4")
            else:
                print("  ❌ Invalid MP4 header")
                
                # Check if it's text content
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    if text_content.isprintable():
                        print(f"  📝 File contains text: {text_content[:50]}")
                        print("  🚨 CRITICAL: This is NOT a video file!")
                except:
                    print("  ❓ Unknown binary content")
            
            # Test if the file can be served via API
            try:
                response = requests.get(f"{BACKEND_URL}/api/video/tutorial/{file}")
                print(f"  🌐 API serves file: {response.status_code}")
                
                if response.status_code == 200:
                    api_content = response.content
                    print(f"  📊 API content size: {len(api_content)} bytes")
                    
                    if len(api_content) != size:
                        print("  ⚠️ Size mismatch between file and API response")
                    
                    # Check if API content matches file content
                    if api_content[:50] == content[:50]:
                        print("  ✅ API content matches file content")
                    else:
                        print("  ❌ API content differs from file content")
                        print(f"  📊 API first 50 bytes: {api_content[:50]}")
                        
            except Exception as e:
                print(f"  ❌ Error testing API: {e}")

def test_real_video_playback():
    """Test with a real video file to compare"""
    print("\n🎬 TESTING WITH REAL VIDEO CONTENT")
    print("=" * 50)
    
    # Create a minimal valid MP4 file for testing
    minimal_mp4 = bytes.fromhex(
        "0000001c667479706d703431000000006d703431"  # ftyp box
        "0000001c6d646174"  # mdat box header
        "000000000000000000000000"  # minimal data
    )
    
    test_file_path = "/app/uploads/tutorials/minimal_test.mp4"
    
    try:
        with open(test_file_path, 'wb') as f:
            f.write(minimal_mp4)
        
        print(f"✅ Created minimal MP4 test file: {len(minimal_mp4)} bytes")
        
        # Test via API
        response = requests.get(f"{BACKEND_URL}/api/video/tutorial/minimal_test.mp4")
        print(f"API response: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print("✅ Minimal MP4 served successfully")
            
            # Test with HTML5 video element simulation
            print("\n🎥 Simulating HTML5 video element behavior:")
            
            # Test HEAD request (what browsers do first)
            head_response = requests.head(f"{BACKEND_URL}/api/video/tutorial/minimal_test.mp4")
            print(f"HEAD request: {head_response.status_code}")
            print(f"Accept-Ranges: {head_response.headers.get('Accept-Ranges')}")
            print(f"Content-Length: {head_response.headers.get('Content-Length')}")
            
            # Test range request (what browsers do for video)
            range_headers = {"Range": "bytes=0-"}
            range_response = requests.get(f"{BACKEND_URL}/api/video/tutorial/minimal_test.mp4", 
                                        headers=range_headers)
            print(f"Range request: {range_response.status_code}")
            
            if range_response.status_code in [200, 206]:
                print("✅ Video streaming requests work correctly")
            else:
                print("❌ Video streaming requests fail")
        
        # Clean up
        os.remove(test_file_path)
        
    except Exception as e:
        print(f"❌ Error creating test file: {e}")

def check_frontend_video_urls():
    """Check what video URLs the frontend is actually trying to use"""
    print("\n🔗 CHECKING FRONTEND VIDEO URL PATTERNS")
    print("=" * 50)
    
    # Test the URLs that the frontend might be generating
    test_urls = [
        "/api/video/tutorial/5ca71a02-f593-40f8-ab29-b82c58345717.mp4",
        "/uploads/tutorials/5ca71a02-f593-40f8-ab29-b82c58345717.mp4",
        f"{BACKEND_URL}/api/video/tutorial/5ca71a02-f593-40f8-ab29-b82c58345717.mp4",
        f"{BACKEND_URL}/uploads/tutorials/5ca71a02-f593-40f8-ab29-b82c58345717.mp4"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Testing URL: {url}")
        
        try:
            if url.startswith('http'):
                response = requests.get(url)
            else:
                response = requests.get(f"{BACKEND_URL}{url}")
            
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'Not set')}")
            print(f"  Content-Length: {response.headers.get('Content-Length', 'Not set')}")
            
            if response.status_code == 200:
                content = response.content
                print(f"  Content size: {len(content)} bytes")
                
                # Check if it's actually video content
                if len(content) > 20:
                    if content.startswith(b'\x00\x00\x00') and b'ftyp' in content[:20]:
                        print("  ✅ Valid video content")
                    else:
                        print("  ❌ Not valid video content")
                        print(f"  First 20 bytes: {content[:20]}")
                else:
                    print("  ⚠️ Very small content - likely not a real video")
                    print(f"  Content: {content}")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    """Run video content analysis"""
    print("🔍 VIDEO CONTENT ANALYSIS")
    print("=" * 60)
    
    analyze_video_files()
    test_real_video_playback()
    check_frontend_video_urls()
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS SUMMARY")
    print("=" * 60)
    print("Key findings:")
    print("1. Check if video files are actually valid MP4 files")
    print("2. Look for text content masquerading as video files")
    print("3. Verify API serves the same content as stored files")
    print("4. Confirm video streaming headers are correct")

if __name__ == "__main__":
    main()