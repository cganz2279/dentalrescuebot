#!/usr/bin/env python3
"""
Deep authentication debugging - simulate the exact backend logic
"""

import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import requests

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

def simulate_backend_auth():
    """Simulate the exact backend authentication logic"""
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 SIMULATING BACKEND AUTH LOGIC")
    print("=" * 50)
    
    # Simulate the exact login process from auth.py
    request_email = "cganz2279@gmail.com"
    request_password = "password123"
    
    print(f"📧 Request Email: {request_email}")
    print(f"🔑 Request Password: {request_password}")
    
    # Step 1: Find user by email (lowercase)
    print(f"\n1️⃣ Finding user by email: {request_email.lower()}")
    user = db.users.find_one({"email": request_email.lower()})
    
    if not user:
        print("❌ User not found")
        return
    
    print("✅ User found:")
    print(f"   Email: {user.get('email')}")
    print(f"   Name: {user.get('firstName')} {user.get('lastName')}")
    print(f"   Role: {user.get('role')}")
    print(f"   Active: {user.get('isActive')}")
    print(f"   Practice ID: {user.get('practiceId')}")
    
    # Step 2: Check if user is active
    print(f"\n2️⃣ Checking user active status")
    is_active = user.get('isActive', True)
    print(f"   isActive: {is_active}")
    
    if not is_active:
        print("❌ User is not active")
        return
    
    # Step 3: Verify password
    print(f"\n3️⃣ Verifying password")
    stored_password = user.get('password', '')
    print(f"   Stored hash: {stored_password}")
    print(f"   Test password: {request_password}")
    
    try:
        password_valid = bcrypt.checkpw(request_password.encode('utf-8'), stored_password.encode('utf-8'))
        print(f"   Password valid: {password_valid}")
        
        if not password_valid:
            print("❌ Password verification failed")
            return
    except Exception as e:
        print(f"❌ Password verification error: {str(e)}")
        return
    
    # Step 4: Get practice info
    print(f"\n4️⃣ Getting practice info")
    practice_id = user.get('practiceId')
    if practice_id:
        practice = db.practices.find_one({"id": practice_id})
        if practice:
            print("✅ Practice found:")
            print(f"   Name: {practice.get('name')}")
            print(f"   Active: {practice.get('isActive')}")
            print(f"   Subscription: {practice.get('subscription', {}).get('status')}")
        else:
            print("❌ Practice not found")
    else:
        print("⚠️ No practice ID")
    
    print(f"\n✅ All authentication checks passed!")
    print("🤔 Backend should allow login, but API returns 401...")
    
    # Let's check if there are any other issues
    print(f"\n🔍 Additional checks:")
    
    # Check if there are multiple users with same email
    all_users = list(db.users.find({"email": request_email.lower()}))
    print(f"   Users with this email: {len(all_users)}")
    
    # Check if there are any special characters or encoding issues
    email_bytes = request_email.encode('utf-8')
    print(f"   Email bytes: {email_bytes}")
    
    # Check the exact database connection being used
    print(f"   Database name: {db.name}")
    print(f"   Collection count: {db.users.count_documents({})}")
    
    client.close()

def test_other_working_credentials():
    """Test with credentials we know work"""
    
    print(f"\n🧪 TESTING OTHER WORKING CREDENTIALS")
    print("=" * 30)
    
    session = requests.Session()
    
    # Test ganzseth@gmail.com (we know this works)
    login_data = {"email": "ganzseth@gmail.com", "password": "password123"}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"ganzseth@gmail.com: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('user', {}).get('firstName')} {data.get('user', {}).get('lastName')}")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    simulate_backend_auth()
    test_other_working_credentials()