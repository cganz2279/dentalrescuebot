#!/usr/bin/env python3
"""
Create the specific account for Dr. Cary H. Ganz
"""

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_dr_ganz_account():
    """Create Dr. Ganz's specific account"""
    print("🔄 Creating Dr. Cary H. Ganz's account...")
    print("=" * 50)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Dr. Ganz's practice data
    practice_id = str(uuid.uuid4())
    practice_data = {
        'id': practice_id,
        'name': 'Cary H. Ganz DDS',
        'email': 'cganz2279@gmail.com',
        'phone': '(555) 000-0000',  # Default - can be updated
        'address': '',  # Can be updated later
        'officeHours': 'Monday-Friday: 8:00 AM - 5:00 PM',
        'emergencyContact': '(555) 000-0000',
        'createdAt': datetime.utcnow().isoformat() + 'Z',
        'updatedAt': datetime.utcnow().isoformat() + 'Z',
        'isActive': True
    }
    
    # Dr. Ganz's user data
    user_data = {
        'id': str(uuid.uuid4()),
        'name': 'Dr. Cary H. Ganz',
        'email': 'cganz2279@gmail.com',
        'password': 'password123',  # Will be hashed
        'role': 'dentist',
        'practiceId': practice_id,
        'createdAt': datetime.utcnow().isoformat() + 'Z',
        'updatedAt': datetime.utcnow().isoformat() + 'Z',
        'isActive': True
    }
    
    # Clear existing data and create fresh
    print("🧹 Clearing sample accounts...")
    await db.practices.delete_many({})
    await db.users.delete_many({})
    
    # Create practice
    print("🏥 Creating practice: Cary H. Ganz DDS")
    await db.practices.insert_one(practice_data)
    print(f"  ✅ Practice created with ID: {practice_id}")
    
    # Hash password and create user
    print("👤 Creating user account...")
    hashed = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
    user_data['password'] = hashed.decode('utf-8')
    
    await db.users.insert_one(user_data)
    print(f"  ✅ User account created: {user_data['email']}")
    
    print("\n" + "=" * 50)
    print("🎉 Dr. Ganz's account created successfully!")
    print("\n📝 Your Login Credentials:")
    print("Email: cganz2279@gmail.com")
    print("Password: password123")
    print("\n🌐 Login at: https://dentalpractice-hub-1.preview.emergentagent.com")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_dr_ganz_account())