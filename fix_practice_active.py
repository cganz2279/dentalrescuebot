#!/usr/bin/env python3
"""
Fix the practice isActive field for cganz2279@gmail.com
"""

import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

def fix_practice_active():
    """Fix the isActive field for the practice"""
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Find the user
    user = db.users.find_one({"email": "cganz2279@gmail.com"})
    if not user:
        print("❌ User not found")
        return
    
    practice_id = user.get('practiceId')
    print(f"🔍 Checking practice ID: {practice_id}")
    
    # Find the practice
    practice = db.practices.find_one({"id": practice_id})
    if not practice:
        print("❌ Practice not found")
        return
    
    print(f"📋 Current practice status:")
    print(f"   Name: {practice.get('name')}")
    print(f"   isActive: {practice.get('isActive')}")
    print(f"   Subscription Status: {practice.get('subscription', {}).get('status')}")
    
    # Fix the isActive field
    if practice.get('isActive') is None:
        print("🔧 Fixing isActive field...")
        result = db.practices.update_one(
            {"id": practice_id},
            {"$set": {"isActive": True}}
        )
        print(f"✅ Updated {result.modified_count} practice record")
    else:
        print("✅ Practice isActive field is already set correctly")
    
    # Verify the fix
    updated_practice = db.practices.find_one({"id": practice_id})
    print(f"📋 Updated practice status:")
    print(f"   isActive: {updated_practice.get('isActive')}")
    
    client.close()

if __name__ == "__main__":
    fix_practice_active()