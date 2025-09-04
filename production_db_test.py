#!/usr/bin/env python3
"""
Test what database the production backend is actually using
"""

import requests
import json

BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

def test_production_backend():
    """Test production backend to understand what's happening"""
    
    print("🌐 PRODUCTION BACKEND INVESTIGATION")
    print("=" * 50)
    
    session = requests.Session()
    
    # 1. Test health check
    print("1️⃣ Testing health check:")
    try:
        response = session.get(f"{BACKEND_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # 2. Test with known working credentials (ganzseth)
    print("\n2️⃣ Testing known working credentials (ganzseth@gmail.com):")
    login_data = {"email": "ganzseth@gmail.com", "password": "password123"}
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            practice = data.get('practice', {})
            print(f"   User: {user.get('firstName')} {user.get('lastName')} ({user.get('role')})")
            print(f"   Practice: {practice.get('name')} (ID: {practice.get('id')})")
            print(f"   Practice Active: {practice.get('isActive')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # 3. Test with problematic credentials (cganz2279)
    print("\n3️⃣ Testing problematic credentials (cganz2279@gmail.com):")
    login_data = {"email": "cganz2279@gmail.com", "password": "password123"}
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # 4. Test with wrong password for cganz2279 to see if error is different
    print("\n4️⃣ Testing cganz2279@gmail.com with wrong password:")
    login_data = {"email": "cganz2279@gmail.com", "password": "wrongpassword"}
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # 5. Test with non-existent user
    print("\n5️⃣ Testing non-existent user:")
    login_data = {"email": "nonexistent@example.com", "password": "password123"}
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")

if __name__ == "__main__":
    test_production_backend()