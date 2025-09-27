#!/usr/bin/env python3
"""
Create sample practice accounts for testing login functionality
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

async def create_sample_practices():
    """Create sample practices and users for testing"""
    print("🔄 Creating sample practice accounts...")
    print("=" * 50)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.dental_portal
    
    # Sample practices to create
    practices_data = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Smile Dental Clinic',
            'email': 'admin@smiledentalclinic.com',
            'phone': '(555) 123-4567',
            'address': '123 Main Street, Anytown, ST 12345',
            'officeHours': 'Monday-Friday: 8:00 AM - 5:00 PM',
            'emergencyContact': '(555) 123-4567',
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'isActive': True
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Family Dental Care',
            'email': 'contact@familydentalcare.com', 
            'phone': '(555) 987-6543',
            'address': '456 Oak Avenue, Somewhere, ST 67890',
            'officeHours': 'Monday-Thursday: 9:00 AM - 6:00 PM, Friday: 9:00 AM - 3:00 PM',
            'emergencyContact': '(555) 987-6543',
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'isActive': True
        }
    ]
    
    # Sample users for each practice
    users_data = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Dr. Sarah Johnson',
            'email': 'dr.johnson@smiledentalclinic.com',
            'password': 'dental123',  # Will be hashed
            'role': 'dentist',
            'practiceId': practices_data[0]['id'],
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'isActive': True
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Dr. Mike Chen',
            'email': 'dr.chen@familydentalcare.com',
            'password': 'dental456',  # Will be hashed
            'role': 'dentist',
            'practiceId': practices_data[1]['id'],
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'isActive': True
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Test User',
            'email': 'test@test.com',
            'password': 'test123',  # Will be hashed
            'role': 'dentist',
            'practiceId': practices_data[0]['id'],
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
            'isActive': True
        }
    ]
    
    # Clear existing data
    await db.practices.delete_many({})
    await db.users.delete_many({})
    
    # Insert practices
    print("📋 Creating practices...")
    await db.practices.insert_many(practices_data)
    
    for practice in practices_data:
        print(f"  ✅ {practice['name']} ({practice['email']})")
    
    # Hash passwords and insert users
    print("\n👤 Creating users...")
    for user in users_data:
        # Hash the password
        hashed = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
        user['password'] = hashed.decode('utf-8')
        
        await db.users.insert_one(user)
        print(f"  ✅ {user['name']} ({user['email']}) - Password: {user['password'][:20]}...")
    
    print("\n" + "=" * 50)
    print("🎉 Sample accounts created successfully!")
    print("\n📝 Login Credentials:")
    print("1. dr.johnson@smiledentalclinic.com / dental123")
    print("2. dr.chen@familydentalcare.com / dental456") 
    print("3. test@test.com / test123")
    print("\n🌐 Try logging in at: https://dental-instructions.preview.emergentagent.com")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_practices())