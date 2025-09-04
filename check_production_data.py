#!/usr/bin/env python3
"""
Check what data exists in production vs local database
"""

import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path
import requests

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

def compare_production_vs_local():
    """Compare production backend data vs local database"""
    
    print("🔍 PRODUCTION VS LOCAL DATA COMPARISON")
    print("=" * 50)
    
    # Connect to local database
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("📊 LOCAL DATABASE:")
    print(f"   Database: {db.name}")
    print(f"   Total users: {db.users.count_documents({})}")
    print(f"   Total practices: {db.practices.count_documents({})}")
    
    # List all users in local database
    print("\n👥 LOCAL USERS:")
    local_users = list(db.users.find({}, {"email": 1, "firstName": 1, "lastName": 1, "role": 1, "practiceId": 1, "_id": 0}))
    for user in local_users:
        print(f"   {user.get('email')} - {user.get('firstName')} {user.get('lastName')} ({user.get('role')}) - Practice: {user.get('practiceId')}")
    
    # List all practices in local database
    print("\n🏢 LOCAL PRACTICES:")
    local_practices = list(db.practices.find({}, {"id": 1, "name": 1, "email": 1, "isActive": 1, "_id": 0}))
    for practice in local_practices:
        print(f"   {practice.get('id')} - {practice.get('name')} ({practice.get('email')}) - Active: {practice.get('isActive')}")
    
    # Now test what the production backend knows
    print("\n🌐 PRODUCTION BACKEND DATA:")
    
    # Test ganzseth login to see what practice data comes back
    session = requests.Session()
    login_data = {"email": "ganzseth@gmail.com", "password": "password123"}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        user = data.get('user', {})
        practice = data.get('practice', {})
        
        print(f"   ganzseth@gmail.com works:")
        print(f"     User ID: {user.get('id')}")
        print(f"     Practice ID: {user.get('practiceId')}")
        print(f"     Practice Name: {practice.get('name')}")
        print(f"     Practice Email: {practice.get('email')}")
        print(f"     Practice Active: {practice.get('isActive')}")
        
        # Check if this practice exists in local database
        local_practice = db.practices.find_one({"id": user.get('practiceId')})
        if local_practice:
            print(f"     ✅ This practice EXISTS in local database")
        else:
            print(f"     ❌ This practice does NOT exist in local database")
        
        # Check if cganz2279 exists in the same practice
        cganz_in_same_practice = db.users.find_one({"email": "cganz2279@gmail.com", "practiceId": user.get('practiceId')})
        if cganz_in_same_practice:
            print(f"     ✅ cganz2279@gmail.com EXISTS in same practice in local database")
        else:
            print(f"     ❌ cganz2279@gmail.com does NOT exist in same practice in local database")
    
    # Check if there's a cganz2279 user in the production practice
    production_practice_id = "0b08d321-ae1a-43d5-b69a-4850cfa3a9fc"  # From ganzseth login
    cganz_in_prod_practice = db.users.find_one({"email": "cganz2279@gmail.com", "practiceId": production_practice_id})
    
    print(f"\n🔍 Checking for cganz2279@gmail.com in production practice {production_practice_id}:")
    if cganz_in_prod_practice:
        print(f"   ✅ Found cganz2279@gmail.com in production practice")
        print(f"   Active: {cganz_in_prod_practice.get('isActive')}")
        print(f"   Role: {cganz_in_prod_practice.get('role')}")
    else:
        print(f"   ❌ cganz2279@gmail.com NOT found in production practice")
        
        # Let's create the user in the correct practice
        print(f"\n🔧 FIXING: Moving cganz2279@gmail.com to production practice")
        
        # Get the existing cganz user
        existing_cganz = db.users.find_one({"email": "cganz2279@gmail.com"})
        if existing_cganz:
            # Update the practice ID
            result = db.users.update_one(
                {"email": "cganz2279@gmail.com"},
                {"$set": {"practiceId": production_practice_id}}
            )
            print(f"   ✅ Updated cganz2279@gmail.com practiceId: {result.modified_count} records")
            
            # Test login again
            print(f"\n🧪 Testing cganz2279@gmail.com login after fix:")
            login_data = {"email": "cganz2279@gmail.com", "password": "password123"}
            response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ LOGIN SUCCESS!")
                data = response.json()
                user = data.get('user', {})
                print(f"   User: {user.get('firstName')} {user.get('lastName')} ({user.get('role')})")
            else:
                print(f"   ❌ Still failing: {response.text}")
    
    client.close()

if __name__ == "__main__":
    compare_production_vs_local()