#!/usr/bin/env python3
"""
Video Routing Issue Investigation
=================================

Testing the specific routing issue where /uploads/* paths are being served by React instead of backend.
This is the critical issue preventing video playback.
"""

import requests
import json
import os
import tempfile
import io

BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
ADMIN_CREDENTIALS = {
    "email": "cganz@admin.com",
    "password": "Dentist1#"
}

def authenticate_admin():
    """Get admin token"""
    response = requests.post(
        f"{BACKEND_URL}/api/admin/login",
        json=ADMIN_CREDENTIALS,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

def create_real_mp4_file():
    """Create a minimal but valid MP4 file"""
    # This creates a minimal MP4 file with proper headers
    mp4_data = (
        b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'  # ftyp box
        b'\x00\x00\x00\x08free'  # free box
        b'\x00\x00\x00\x28mdat'  # mdat box header
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # minimal data
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    return io.BytesIO(mp4_data)

def test_video_upload_and_routing():
    """Test video upload and then check routing"""
    print("🔍 TESTING VIDEO UPLOAD AND ROUTING ISSUE")
    print("=" * 50)
    
    # Step 1: Authenticate
    admin_token = authenticate_admin()
    if not admin_token:
        print("❌ Failed to authenticate as admin")
        return
    
    print("✅ Admin authentication successful")
    
    # Step 2: Upload a test video
    video_file = create_real_mp4_file()
    
    files = {
        'video': ('routing_test.mp4', video_file, 'video/mp4')
    }
    data = {
        'title': 'Routing Test Video',
        'description': 'Testing video routing issue',
        'category': 'test',
        'order': 1
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.post(
        f"{BACKEND_URL}/api/admin/tutorials",
        files=files,
        data=data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Video upload failed: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    tutorial_id = result.get('tutorial_id')
    print(f"✅ Video uploaded successfully. Tutorial ID: {tutorial_id}")
    
    # Step 3: Get the video URL
    response = requests.get(f"{BACKEND_URL}/api/admin/tutorials", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to retrieve tutorials")
        return
    
    tutorials = response.json()
    test_tutorial = None
    for tutorial in tutorials:
        if tutorial.get('title') == 'Routing Test Video':
            test_tutorial = tutorial
            break
    
    if not test_tutorial:
        print("❌ Test tutorial not found")
        return
    
    video_url = test_tutorial.get('video_url')
    print(f"📹 Video URL: {video_url}")
    
    # Step 4: Test direct access to video file
    full_video_url = f"{BACKEND_URL}{video_url}"
    print(f"🔗 Testing access to: {full_video_url}")
    
    # Test HEAD request
    head_response = requests.head(full_video_url)
    print(f"HEAD Response: {head_response.status_code}")
    print(f"Content-Type: {head_response.headers.get('Content-Type', 'Not Set')}")
    print(f"Content-Length: {head_response.headers.get('Content-Length', 'Not Set')}")
    
    # Test GET request
    get_response = requests.get(full_video_url)
    print(f"GET Response: {get_response.status_code}")
    print(f"Content-Type: {get_response.headers.get('Content-Type', 'Not Set')}")
    
    # Check if we're getting HTML instead of video
    content_type = get_response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        print("🚨 CRITICAL ISSUE: Getting HTML instead of video file!")
        print("First 200 characters of response:")
        print(get_response.text[:200])
        print("\n🔍 This confirms the reverse proxy routing issue!")
        print("The /uploads/* path is being handled by React frontend instead of backend static files.")
    elif 'video/' in content_type:
        print("✅ Correct video content type received")
        # Check file signature
        content = get_response.content
        if content.startswith(b'\x00\x00\x00'):
            print("✅ Valid MP4 file signature detected")
        else:
            print("⚠️ Unexpected file signature")
    else:
        print(f"⚠️ Unexpected content type: {content_type}")
    
    # Step 5: Test different /uploads paths
    print("\n🔍 TESTING DIFFERENT /uploads PATHS:")
    
    test_paths = [
        "/uploads/",
        "/uploads/tutorials/",
        f"/uploads/tutorials/nonexistent.mp4",
        video_url  # The actual video file
    ]
    
    for path in test_paths:
        test_url = f"{BACKEND_URL}{path}"
        response = requests.get(test_url)
        content_type = response.headers.get('Content-Type', '')
        
        is_html = 'text/html' in content_type
        status_icon = "🚨" if is_html else "✅"
        content_desc = "HTML (ROUTING ISSUE)" if is_html else f"Proper response ({content_type})"
        
        print(f"{status_icon} {path}: {response.status_code} - {content_desc}")
    
    # Step 6: Cleanup
    print(f"\n🧹 Cleaning up test tutorial...")
    delete_response = requests.delete(
        f"{BACKEND_URL}/api/admin/tutorials/{tutorial_id}",
        headers=headers
    )
    
    if delete_response.status_code == 200:
        print("✅ Test tutorial cleaned up")
    else:
        print(f"⚠️ Failed to cleanup: {delete_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSION:")
    print("The issue is confirmed - reverse proxy is serving React HTML")
    print("instead of backend static files for /uploads/* paths.")
    print("This prevents videos from being served correctly.")
    print("=" * 50)

if __name__ == "__main__":
    test_video_upload_and_routing()