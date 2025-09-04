#!/usr/bin/env python3
"""
Sync local database with production backend expectations
"""

import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import bcrypt
from datetime import datetime
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

def sync_production_data():
    """Sync local database with production expectations"""
    
    print("🔄 SYNCING LOCAL DATABASE WITH PRODUCTION")
    print("=" * 50)
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Production practice ID from ganzseth login
    production_practice_id = "0b08d321-ae1a-43d5-b69a-4850cfa3a9fc"
    
    # 1. Create the production practice if it doesn't exist
    print("1️⃣ Creating production practice...")
    existing_practice = db.practices.find_one({"id": production_practice_id})
    
    if not existing_practice:
        practice_doc = {
            "id": production_practice_id,
            "name": "Cary Ganz DDS PC",
            "email": "cganz2279@gmail.com",
            "phone": "5162361083",
            "website": "www.theoncallbot.com",
            "address": {
                "street": "47 Hamlet Woods Drive",
                "city": "St. James",
                "state": "NY",
                "zipCode": "11780"
            },
            "branding": {
                "primaryColor": "#2563eb",
                "secondaryColor": "#1e40af",
                "welcomeMessage": "Welcome to Cary Ganz DDS PC's Library"
            },
            "subscription": {
                "plan": "basic",
                "status": "active",
                "paymentSource": "samcart",
                "monthlyAmount": 49.0,
                "activatedAt": datetime.utcnow(),
                "nextBillingDate": datetime.utcnow()
            },
            "settings": {
                "allowPatientRegistration": False,
                "requirePatientApproval": True,
                "customProcedures": []
            },
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        db.practices.insert_one(practice_doc)
        print("   ✅ Created production practice")
    else:
        print("   ✅ Production practice already exists")
    
    # 2. Create cganz2279@gmail.com user in production practice
    print("2️⃣ Creating cganz2279@gmail.com user...")
    
    # Remove existing cganz user if any
    db.users.delete_many({"email": "cganz2279@gmail.com"})
    
    # Create new cganz user with correct practice ID
    cganz_user_doc = {
        "id": str(uuid.uuid4()),
        "email": "cganz2279@gmail.com",
        "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "firstName": "Cary",
        "lastName": "Ganz",
        "role": "practice_admin",
        "practiceId": production_practice_id,
        "isActive": True,
        "isEmailVerified": True,
        "loginCount": 0,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    db.users.insert_one(cganz_user_doc)
    print("   ✅ Created cganz2279@gmail.com user in production practice")
    
    # 3. Test the login
    print("3️⃣ Testing cganz2279@gmail.com login...")
    session = requests.Session()
    login_data = {"email": "cganz2279@gmail.com", "password": "password123"}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ LOGIN SUCCESS!")
        data = response.json()
        user = data.get('user', {})
        practice = data.get('practice', {})
        print(f"   User: {user.get('firstName')} {user.get('lastName')} ({user.get('role')})")
        print(f"   Practice: {practice.get('name')}")
    else:
        print(f"   ❌ Still failing: {response.text}")
        
        # Let's check what we have in the database now
        print("\n🔍 Checking current database state:")
        cganz_user = db.users.find_one({"email": "cganz2279@gmail.com"})
        if cganz_user:
            print(f"   cganz user exists: {cganz_user.get('email')}")
            print(f"   Practice ID: {cganz_user.get('practiceId')}")
            print(f"   Active: {cganz_user.get('isActive')}")
            print(f"   Role: {cganz_user.get('role')}")
            
            # Test password hash
            stored_hash = cganz_user.get('password', '')
            is_valid = bcrypt.checkpw("password123".encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"   Password valid: {is_valid}")
        
        practice = db.practices.find_one({"id": production_practice_id})
        if practice:
            print(f"   Practice exists: {practice.get('name')}")
            print(f"   Practice active: {practice.get('isActive')}")
    
    client.close()

if __name__ == "__main__":
    sync_production_data()