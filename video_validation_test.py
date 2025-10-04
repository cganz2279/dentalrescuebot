#!/usr/bin/env python3
"""
Quick test for video file validation fix
"""

import requests
import tempfile
import os

BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def test_video_validation():
    session = requests.Session()
    
    # Authenticate
    auth_response = session.post(
        f"{BACKEND_URL}/api/admin/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = auth_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a non-video file
    temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    temp_file.write(b'This is not a video file')
    temp_file.close()
    
    try:
        with open(temp_file.name, 'rb') as fake_video:
            files = {'video': ('fake_video.txt', fake_video, 'text/plain')}
            data = {
                'title': 'Invalid File Test',
                'description': 'Testing with non-video file',
                'category': 'test',
                'order': '1'
            }
            
            response = session.post(
                f"{BACKEND_URL}/api/admin/tutorials",
                files=files,
                data=data,
                headers=headers
            )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 400:
            print("✅ Video validation working correctly - returns 400 for non-video files")
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
            
    finally:
        try:
            os.unlink(temp_file.name)
        except:
            pass

if __name__ == "__main__":
    test_video_validation()