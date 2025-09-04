#!/usr/bin/env python3
"""
Debug email case sensitivity and multiple user issues
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

def debug_email_issues():
    """Debug email case and multiple user issues"""
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 EMAIL CASE SENSITIVITY DEBUG")
    print("=" * 50)
    
    # 1. Check all users with cganz in email
    print("📧 All users with 'cganz' in email:")
    cganz_users = list(db.users.find({"email": {"$regex": "cganz", "$options": "i"}}))
    for user in cganz_users:
        print(f"   Email: '{user.get('email')}'")
        print(f"   Name: {user.get('firstName')} {user.get('lastName')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Active: {user.get('isActive')}")
        print(f"   Practice ID: {user.get('practiceId')}")
        print("   ---")
    
    # 2. Test exact email matches
    test_emails = [
        "cganz2279@gmail.com",
        "CGANZ2279@GMAIL.COM", 
        "Cganz2279@Gmail.com"
    ]
    
    print("🔍 Testing exact email matches:")
    for email in test_emails:
        user = db.users.find_one({"email": email})
        lower_user = db.users.find_one({"email": email.lower()})
        print(f"   '{email}': {user is not None}")
        print(f"   '{email.lower()}': {lower_user is not None}")
    
    # 3. Check if there are multiple practices for the same user
    print("\n🏢 Checking practices:")
    practices = list(db.practices.find({}))
    for practice in practices:
        print(f"   Practice: {practice.get('name')}")
        print(f"   ID: {practice.get('id')}")
        print(f"   Active: {practice.get('isActive')}")
        print(f"   Email: {practice.get('email')}")
        print("   ---")
    
    # 4. Test login with different case variations
    print("\n🌐 Testing login with different cases:")
    session = requests.Session()
    
    for email in test_emails:
        login_data = {"email": email, "password": "password123"}
        try:
            response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"   {email}: Status {response.status_code}")
            if response.status_code != 200:
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   {email}: Exception {str(e)}")
    
    client.close()

if __name__ == "__main__":
    debug_email_issues()