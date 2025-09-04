#!/usr/bin/env python3
"""
FOCUSED LOGIN TEST - Investigate cganz2279@gmail.com login issue
"""

import requests
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path
import bcrypt

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

def test_cganz_login_detailed():
    """Detailed investigation of cganz2279@gmail.com login issue"""
    
    print("🔍 DETAILED CGANZ LOGIN INVESTIGATION")
    print("=" * 50)
    
    # 1. Check database for cganz2279@gmail.com
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    user = db.users.find_one({"email": "cganz2279@gmail.com"})
    if not user:
        print("❌ User cganz2279@gmail.com NOT FOUND in database")
        return
    
    print("✅ User found in database:")
    print(f"   Email: {user.get('email')}")
    print(f"   Name: {user.get('firstName')} {user.get('lastName')}")
    print(f"   Role: {user.get('role')}")
    print(f"   Active: {user.get('isActive')}")
    print(f"   Practice ID: {user.get('practiceId')}")
    
    # 2. Test password hash directly
    stored_hash = user.get('password', '')
    test_password = "password123"
    
    print(f"\n🔐 PASSWORD VERIFICATION:")
    print(f"   Stored Hash: {stored_hash}")
    print(f"   Test Password: {test_password}")
    
    try:
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"   ✅ Direct bcrypt check: {is_valid}")
    except Exception as e:
        print(f"   ❌ Bcrypt error: {str(e)}")
        return
    
    # 3. Check practice exists and is active
    practice = db.practices.find_one({"id": user.get('practiceId')})
    if practice:
        print(f"\n🏢 PRACTICE INFO:")
        print(f"   Practice Name: {practice.get('name')}")
        print(f"   Practice Active: {practice.get('isActive')}")
        print(f"   Subscription Status: {practice.get('subscription', {}).get('status')}")
    else:
        print(f"\n❌ Practice NOT FOUND for ID: {user.get('practiceId')}")
    
    # 4. Test login API call step by step
    print(f"\n🌐 API LOGIN TEST:")
    
    session = requests.Session()
    login_data = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    print(f"   Request URL: {BACKEND_URL}/auth/login")
    print(f"   Request Data: {login_data}")
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login SUCCESS")
            print(f"   User: {data.get('user', {})}")
        else:
            print(f"   ❌ Login FAILED")
            
    except Exception as e:
        print(f"   ❌ Request Exception: {str(e)}")
    
    # 5. Compare with working ganzseth login
    print(f"\n🔄 COMPARISON WITH WORKING LOGIN:")
    
    ganzseth_user = db.users.find_one({"email": "ganzseth@gmail.com"})
    if ganzseth_user:
        print(f"   ganzseth@gmail.com found:")
        print(f"   - Active: {ganzseth_user.get('isActive')}")
        print(f"   - Role: {ganzseth_user.get('role')}")
        print(f"   - Practice ID: {ganzseth_user.get('practiceId')}")
        
        # Test ganzseth login
        ganzseth_data = {
            "email": "ganzseth@gmail.com", 
            "password": "password123"
        }
        
        ganzseth_response = session.post(f"{BACKEND_URL}/auth/login", json=ganzseth_data)
        print(f"   ganzseth login status: {ganzseth_response.status_code}")
        
        if ganzseth_response.status_code == 200:
            print(f"   ✅ ganzseth login works")
        else:
            print(f"   ❌ ganzseth login failed: {ganzseth_response.text}")
    
    client.close()

if __name__ == "__main__":
    test_cganz_login_detailed()