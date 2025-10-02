#!/usr/bin/env python3

import requests
import json

# Configuration
BASE_URL = "https://aftercareportal.preview.emergentagent.com/api"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

def test_email_functionality():
    """Test just the email functionality"""
    session = requests.Session()
    
    # Login first
    print("🔐 Logging in as admin...")
    auth_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BASE_URL}/admin/login", json=auth_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get("success"):
        print(f"❌ Login failed: {data.get('error')}")
        return False
    
    admin_token = data["token"]
    session.headers.update({"Authorization": f"Bearer {admin_token}"})
    print("✅ Admin login successful")
    
    # Test email endpoint
    print("\n📧 Testing welcome email endpoint...")
    email_data = {
        "practiceData": {
            "practiceName": "Test Practice for Email"
        },
        "adminCredentials": {
            "adminEmail": "test@example.com",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "tempPassword": "TestPass123!"
        },
        "appUrl": "https://aftercareportal.preview.emergentagent.com"
    }
    
    response = session.post(f"{BASE_URL}/admin/send-welcome-email", json=email_data)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ Email functionality working")
            return True
        else:
            print(f"❌ Email failed: {data.get('error')}")
            return False
    else:
        print(f"❌ Email failed with status {response.status_code}")
        return False

if __name__ == "__main__":
    test_email_functionality()