#!/usr/bin/env python3
"""
URGENT: Fix caryganz@gmail.com account - delete user and create practice
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
    print("🚨 URGENT: Fixing caryganz@gmail.com account")
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
    
    # Step 2: Try to find and delete existing user account
    print("🗑️ Checking for existing user account...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all practices to find if there's a practice with this email
    practices_response = requests.get(f"{API_BASE}/admin/practices", headers=headers)
    if practices_response.status_code == 200:
        practices = practices_response.json().get("practices", [])
        existing_practice = None
        for practice in practices:
            if practice.get("email") == PRACTICE_EMAIL:
                existing_practice = practice
                break
        
        if existing_practice:
            print(f"✅ Found existing practice: {existing_practice.get('name')} (ID: {existing_practice.get('id')})")
            
            # Test login with the existing practice
            print("🔐 Testing login with existing practice...")
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": PRACTICE_EMAIL,
                "password": PRACTICE_PASSWORD
            })
            
            if login_response.status_code == 200:
                print("✅ Login successful with existing practice!")
                login_data = login_response.json()
                practice_token = login_data.get("access_token")
                practice_id = login_data.get("practice_id")
                
                # Test dashboard
                print("📊 Testing dashboard access...")
                dashboard_headers = {"Authorization": f"Bearer {practice_token}"}
                dashboard_response = requests.get(
                    f"{API_BASE}/practice/dashboard",
                    headers=dashboard_headers
                )
                
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    print(f"✅ Dashboard accessible!")
                    print(f"   Practice Name: {dashboard_data.get('practice_name', 'N/A')}")
                    print(f"   Owner: {dashboard_data.get('owner', 'N/A')}")
                    print(f"   Phone: {dashboard_data.get('phone', 'N/A')}")
                    print(f"   Email: {dashboard_data.get('email', 'N/A')}")
                    
                    print("\n" + "=" * 70)
                    print("🎯 ACCOUNT IS ALREADY WORKING!")
                    print(f"   📧 Email: {PRACTICE_EMAIL}")
                    print(f"   🔑 Password: {PRACTICE_PASSWORD}")
                    print(f"   🔗 Login: https://app.dentalaftercarenotes.com/login")
                    print(f"   🏥 Practice: {dashboard_data.get('practice_name', PRACTICE_NAME)}")
                    print(f"   👤 Owner: {dashboard_data.get('owner', PRACTICE_OWNER)}")
                    print(f"   📞 Phone: {dashboard_data.get('phone', PRACTICE_PHONE)}")
                    print("=" * 70)
                    return True
                else:
                    print(f"❌ Dashboard access failed: {dashboard_response.text}")
            else:
                print(f"❌ Login failed: {login_response.text}")
                print("🔧 Need to fix the password...")
    
    # Step 3: Create practice account using SamCart webhook
    print("🔧 Creating practice account via SamCart webhook...")
    webhook_response = requests.post(
        f"{API_BASE}/webhook/samcart/test",
        params={"test_email": PRACTICE_EMAIL},
        timeout=30
    )
    
    print(f"Webhook response status: {webhook_response.status_code}")
    print(f"Webhook response: {webhook_response.text}")
    
    if webhook_response.status_code == 200:
        data = webhook_response.json()
        status = data.get("status")
        
        if status == "success":
            practice_info = data.get("practice_info", {})
            generated_password = practice_info.get("password", "")
            practice_name = practice_info.get("practice_name", "")
            practice_id = practice_info.get("practice_id", "")
            
            print(f"✅ Practice created via webhook!")
            print(f"   Practice: {practice_name}")
            print(f"   ID: {practice_id}")
            print(f"   Generated Password: {generated_password}")
            
            # Test login with generated password
            print("🔐 Testing login with generated password...")
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": PRACTICE_EMAIL,
                "password": generated_password
            })
            
            if login_response.status_code == 200:
                print("✅ Login successful with generated password!")
                login_data = login_response.json()
                practice_token = login_data.get("access_token")
                
                # Test dashboard
                print("📊 Testing dashboard access...")
                dashboard_headers = {"Authorization": f"Bearer {practice_token}"}
                dashboard_response = requests.get(
                    f"{API_BASE}/practice/dashboard",
                    headers=dashboard_headers
                )
                
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    print(f"✅ Dashboard accessible!")
                    print(f"   Practice Name: {dashboard_data.get('practice_name', 'N/A')}")
                    print(f"   Owner: {dashboard_data.get('owner', 'N/A')}")
                    print(f"   Phone: {dashboard_data.get('phone', 'N/A')}")
                    print(f"   Email: {dashboard_data.get('email', 'N/A')}")
                    
                    print("\n" + "=" * 70)
                    print("🎯 FINAL CUSTOMER INSTRUCTIONS:")
                    print(f"   📧 Email: {PRACTICE_EMAIL}")
                    print(f"   🔑 Password: {generated_password}")
                    print(f"   🔗 Login: https://app.dentalaftercarenotes.com/login")
                    print(f"   🏥 Practice: {dashboard_data.get('practice_name', PRACTICE_NAME)}")
                    print(f"   👤 Owner: {dashboard_data.get('owner', PRACTICE_OWNER)}")
                    print(f"   📞 Phone: {dashboard_data.get('phone', PRACTICE_PHONE)}")
                    print("=" * 70)
                    return True
                else:
                    print(f"❌ Dashboard access failed: {dashboard_response.text}")
            else:
                print(f"❌ Login failed with generated password: {login_response.text}")
        else:
            print(f"⚠️ Webhook response: {data.get('message', 'Unknown status')}")
    else:
        print(f"❌ Webhook failed: {webhook_response.text}")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 ACCOUNT FIXED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ ACCOUNT FIX FAILED!")
        sys.exit(1)