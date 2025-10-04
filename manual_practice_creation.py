#!/usr/bin/env python3
"""
URGENT: Manually create caryganz@gmail.com practice account
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

# Target practice details
PRACTICE_EMAIL = "caryganz@gmail.com"
PRACTICE_NAME = "The Dental Spa at Garden City"
PRACTICE_OWNER = "Cary Ganz"
PRACTICE_PHONE = "516-236-1083"
PRACTICE_PASSWORD = "DentalSpa2025!"

def main():
    print("🚨 URGENT: Manually creating practice account for caryganz@gmail.com")
    print("=" * 70)
    
    # Step 1: Admin login
    print("🔐 Logging in as admin...")
    admin_response = requests.post(f"{API_BASE}/admin/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if admin_response.status_code != 200:
        print(f"❌ Admin login failed: {admin_response.text}")
        return False
    
    admin_token = admin_response.json().get("token")
    print(f"✅ Admin login successful")
    
    # Step 2: Create practice account
    print("🏥 Creating practice account...")
    practice_data = {
        "practiceName": PRACTICE_NAME,
        "adminEmail": PRACTICE_EMAIL,
        "adminCredentials": {
            "email": PRACTICE_EMAIL,
            "password": PRACTICE_PASSWORD
        },
        "subscriptionType": "trial",
        "practiceDetails": {
            "owner": PRACTICE_OWNER,
            "phone": PRACTICE_PHONE,
            "address": "",
            "city": "Garden City",
            "state": "NY",
            "zipCode": "11530"
        }
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    create_response = requests.post(
        f"{API_BASE}/admin/create-practice",
        json=practice_data,
        headers=headers
    )
    
    print(f"Create practice response status: {create_response.status_code}")
    print(f"Create practice response: {create_response.text}")
    
    if create_response.status_code == 200:
        data = create_response.json()
        practice_id = data.get("practice_id", "")
        print(f"✅ Practice created successfully! ID: {practice_id}")
    elif create_response.status_code == 409:
        print("✅ Practice already exists (409 conflict)")
    else:
        print(f"❌ Practice creation failed: {create_response.text}")
        return False
    
    # Step 3: Test login
    print("🔐 Testing practice login...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": PRACTICE_EMAIL,
        "password": PRACTICE_PASSWORD
    })
    
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response: {login_response.text}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        practice_token = login_data.get("access_token")
        practice_id = login_data.get("practice_id")
        print(f"✅ Login successful! Practice ID: {practice_id}")
        
        # Step 4: Test dashboard
        print("📊 Testing dashboard access...")
        headers = {"Authorization": f"Bearer {practice_token}"}
        dashboard_response = requests.get(
            f"{API_BASE}/practice/dashboard",
            headers=headers
        )
        
        print(f"Dashboard response status: {dashboard_response.status_code}")
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"✅ Dashboard accessible!")
            print(f"   Practice Name: {dashboard_data.get('practice_name', 'N/A')}")
            print(f"   Owner: {dashboard_data.get('owner', 'N/A')}")
            print(f"   Phone: {dashboard_data.get('phone', 'N/A')}")
            print(f"   Email: {dashboard_data.get('email', 'N/A')}")
        else:
            print(f"❌ Dashboard access failed: {dashboard_response.text}")
    else:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    # Step 5: Send welcome email
    print("📧 Sending welcome email...")
    welcome_data = {
        "practiceName": PRACTICE_NAME,
        "adminEmail": PRACTICE_EMAIL,
        "adminCredentials": {
            "email": PRACTICE_EMAIL,
            "password": PRACTICE_PASSWORD
        }
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    welcome_response = requests.post(
        f"{API_BASE}/admin/send-welcome-email",
        json=welcome_data,
        headers=headers
    )
    
    print(f"Welcome email response status: {welcome_response.status_code}")
    if welcome_response.status_code == 200:
        print("✅ Welcome email sent successfully!")
    else:
        print(f"⚠️ Welcome email failed: {welcome_response.text}")
    
    print("\n" + "=" * 70)
    print("🎯 FINAL CUSTOMER INSTRUCTIONS:")
    print(f"   📧 Email: {PRACTICE_EMAIL}")
    print(f"   🔑 Password: {PRACTICE_PASSWORD}")
    print(f"   🔗 Login: https://app.dentalaftercarenotes.com/login")
    print(f"   🏥 Practice: {PRACTICE_NAME}")
    print(f"   👤 Owner: {PRACTICE_OWNER}")
    print(f"   📞 Phone: {PRACTICE_PHONE}")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 PRACTICE ACCOUNT CREATION COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ PRACTICE ACCOUNT CREATION FAILED!")
        sys.exit(1)