#!/usr/bin/env python3
"""
Database Investigation Script
Investigating database connectivity and practice record existence
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Get backend URL from frontend environment (where user is accessing)
FRONTEND_BACKEND_URL = "https://dentist-portal-3.emergent.host"
API_BASE = f"{FRONTEND_BACKEND_URL}/api"

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'dentist_management')]

class DatabaseInvestigator:
    def __init__(self):
        self.session = requests.Session()
        
    async def check_practice_record(self):
        """Check if the practice record exists for caryganz@gmail.com"""
        print("🔍 CHECKING PRACTICE RECORD...")
        print("=" * 60)
        
        try:
            # Find practice record for caryganz@gmail.com
            practice = await db.practices.find_one(
                {"email": "caryganz@gmail.com"},
                {"_id": 0, "password": 0}  # Exclude sensitive data
            )
            
            if practice:
                print("✅ PRACTICE RECORD FOUND:")
                print(f"   ID: {practice.get('id')}")
                print(f"   Email: {practice.get('email')}")
                print(f"   Name: {practice.get('practiceName', practice.get('name', 'N/A'))}")
                print(f"   Active: {practice.get('isActive', 'N/A')}")
                print(f"   Created: {practice.get('createdAt', 'N/A')}")
                return practice.get('id')
            else:
                print("❌ NO PRACTICE RECORD FOUND for caryganz@gmail.com")
                return None
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None

    async def check_user_record(self):
        """Check if there's a user record for caryganz@gmail.com"""
        print("🔍 CHECKING USER RECORD...")
        print("=" * 60)
        
        try:
            # Find user record for caryganz@gmail.com
            user = await db.users.find_one(
                {"email": "caryganz@gmail.com"},
                {"_id": 0, "password": 0}  # Exclude sensitive data
            )
            
            if user:
                print("✅ USER RECORD FOUND:")
                print(f"   ID: {user.get('id')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Name: {user.get('firstName')} {user.get('lastName')}")
                print(f"   Role: {user.get('role')}")
                print(f"   Active: {user.get('isActive', 'N/A')}")
                print(f"   Practice ID: {user.get('practiceId', 'N/A')}")
                return user.get('id')
            else:
                print("❌ NO USER RECORD FOUND for caryganz@gmail.com")
                return None
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None

    async def test_database_connectivity(self):
        """Test database connectivity"""
        print("🔍 TESTING DATABASE CONNECTIVITY...")
        print("=" * 60)
        
        try:
            # Test basic database connection
            collections = await db.list_collection_names()
            print(f"✅ DATABASE CONNECTION SUCCESSFUL")
            print(f"   Database: {os.getenv('DB_NAME', 'dentist_management')}")
            print(f"   Collections: {len(collections)}")
            print(f"   Available collections: {', '.join(collections[:10])}")
            
            # Test password_resets collection
            reset_count = await db.password_resets.count_documents({})
            print(f"   Password resets count: {reset_count}")
            
            # Test practices collection
            practices_count = await db.practices.count_documents({})
            print(f"   Practices count: {practices_count}")
            
            # Test users collection
            users_count = await db.users.count_documents({})
            print(f"   Users count: {users_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connectivity error: {e}")
            return False

    def test_api_login(self):
        """Test API login with caryganz@gmail.com"""
        print("🔍 TESTING API LOGIN...")
        print("=" * 60)
        
        try:
            # Test login
            payload = {
                "email": "caryganz@gmail.com",
                "password": "password123"  # Common test password
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔐 Login Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ LOGIN SUCCESSFUL")
                print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
                print(f"   Email: {data.get('user', {}).get('email', 'N/A')}")
                print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
                print(f"   Practice ID: {data.get('user', {}).get('practiceId', 'N/A')}")
                return data.get('user', {}).get('id')
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                print(f"❌ LOGIN FAILED: {data.get('detail', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Login test error: {e}")
            return None

    async def check_token_validation_logic(self, practice_id):
        """Check if the token validation logic is working correctly"""
        print("🔍 CHECKING TOKEN VALIDATION LOGIC...")
        print("=" * 60)
        
        try:
            # Get the latest token
            latest_token = await db.password_resets.find_one(
                {"email": "caryganz@gmail.com"},
                sort=[("created_at", -1)]
            )
            
            if not latest_token:
                print("❌ No tokens found")
                return False
                
            print(f"🎫 Latest Token: {latest_token['reset_token']}")
            print(f"   User ID in token: {latest_token['user_id']}")
            print(f"   Practice ID from login: {practice_id}")
            print(f"   IDs match: {latest_token['user_id'] == practice_id}")
            
            # Check if practice exists with this ID
            practice_check = await db.practices.find_one({"id": latest_token['user_id']})
            print(f"   Practice exists with token user_id: {practice_check is not None}")
            
            if practice_check:
                print(f"   Practice email: {practice_check.get('email')}")
                print(f"   Practice active: {practice_check.get('isActive')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Token validation logic error: {e}")
            return False

    async def run_investigation(self):
        """Run complete database investigation"""
        print("🚀 STARTING DATABASE INVESTIGATION...")
        print(f"🔗 Backend URL: {FRONTEND_BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print(f"🔗 Database: {os.getenv('DB_NAME', 'dentist_management')}")
        print(f"🔗 Mongo URL: {mongo_url}")
        print("=" * 80)
        
        # Step 1: Test database connectivity
        db_connected = await self.test_database_connectivity()
        print()
        
        # Step 2: Check practice record
        practice_id = await self.check_practice_record()
        print()
        
        # Step 3: Check user record
        user_id = await self.check_user_record()
        print()
        
        # Step 4: Test API login
        login_user_id = self.test_api_login()
        print()
        
        # Step 5: Check token validation logic
        if practice_id or login_user_id:
            await self.check_token_validation_logic(practice_id or login_user_id)
        
        print("=" * 80)
        print("🎯 DATABASE INVESTIGATION COMPLETE")
        print("=" * 80)
        
        # Summary
        print("📊 SUMMARY:")
        print(f"   Database Connected: {'✅' if db_connected else '❌'}")
        print(f"   Practice Record: {'✅' if practice_id else '❌'}")
        print(f"   User Record: {'✅' if user_id else '❌'}")
        print(f"   API Login: {'✅' if login_user_id else '❌'}")
        print()

async def main():
    investigator = DatabaseInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())