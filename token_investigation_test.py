#!/usr/bin/env python3
"""
Token Investigation Script
Investigating why the newly generated token is not validating
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

class TokenInvestigator:
    def __init__(self):
        self.session = requests.Session()
        
    async def investigate_database_tokens(self):
        """Investigate all tokens in the database for caryganz@gmail.com"""
        print("🔍 INVESTIGATING DATABASE TOKENS...")
        print("=" * 60)
        
        try:
            # Find all reset tokens for caryganz@gmail.com
            tokens = await db.password_resets.find(
                {"email": "caryganz@gmail.com"}
            ).sort("created_at", -1).to_list(length=10)
            
            print(f"📊 Found {len(tokens)} reset tokens for caryganz@gmail.com:")
            print()
            
            for i, token in enumerate(tokens, 1):
                print(f"🔹 Token #{i}:")
                print(f"   Token: {token['reset_token']}")
                print(f"   Created: {token['created_at']}")
                print(f"   Expires: {token['expires_at']}")
                print(f"   Used: {token.get('used', False)}")
                print(f"   Collection: {token.get('account_collection', 'users')}")
                print(f"   User ID: {token['user_id']}")
                
                # Check if token is still valid (not expired)
                now = datetime.utcnow()
                is_expired = token['expires_at'] < now
                print(f"   Status: {'EXPIRED' if is_expired else 'ACTIVE'}")
                
                # Test this token via API
                await self.test_token_via_api(token['reset_token'], i)
                print()
                
        except Exception as e:
            print(f"❌ Database investigation error: {e}")

    async def test_token_via_api(self, token, token_number):
        """Test a specific token via the API"""
        try:
            response = self.session.get(
                f"{API_BASE}/auth/validate-reset-token/{token}"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   API Test: ✅ VALID (200) - User: {data.get('user', {}).get('email', 'N/A')}")
            elif response.status_code == 400:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                print(f"   API Test: ❌ INVALID (400) - {data.get('detail', 'Unknown error')}")
            else:
                print(f"   API Test: ⚠️ UNEXPECTED ({response.status_code})")
                
        except Exception as e:
            print(f"   API Test: ❌ ERROR - {e}")

    def send_fresh_email_and_get_token(self):
        """Send a fresh email and immediately get the new token"""
        print("🚨 SENDING FRESH EMAIL AND TRACKING TOKEN...")
        print("=" * 60)
        
        try:
            # Send password reset email
            payload = {
                "email": "caryganz@gmail.com",
                "recovery_method": "email"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/forgot-password",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📧 Email Request Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📧 Response: {data.get('message', 'No message')}")
                print(f"📧 Sent Methods: {data.get('sent_methods', [])}")
                return True
            else:
                print(f"❌ Email sending failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Email sending error: {e}")
            return False

    async def check_backend_logs_for_token(self):
        """Check backend logs for token generation"""
        print("🔍 CHECKING BACKEND LOGS FOR TOKEN GENERATION...")
        print("=" * 60)
        
        try:
            # This would require access to backend logs
            # For now, we'll just indicate what we're looking for
            print("📋 Looking for recent log entries containing:")
            print("   - 'Password reset token generated'")
            print("   - 'caryganz@gmail.com'")
            print("   - Token UUID patterns")
            print()
            
        except Exception as e:
            print(f"❌ Log checking error: {e}")

    async def run_investigation(self):
        """Run complete investigation"""
        print("🚀 STARTING TOKEN INVESTIGATION...")
        print(f"🔗 Backend URL: {FRONTEND_BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print(f"🔗 Database: {os.getenv('DB_NAME', 'dentist_management')}")
        print("=" * 80)
        
        # Step 1: Check existing tokens in database
        await self.investigate_database_tokens()
        
        # Step 2: Send fresh email
        print("🚨 STEP 2: Sending fresh email...")
        email_sent = self.send_fresh_email_and_get_token()
        
        if email_sent:
            # Wait a moment for database to update
            print("⏳ Waiting 3 seconds for database update...")
            time.sleep(3)
            
            # Step 3: Check database again for new token
            print("🚨 STEP 3: Checking for new token in database...")
            await self.investigate_database_tokens()
        
        print("=" * 80)
        print("🎯 INVESTIGATION COMPLETE")
        print("=" * 80)

async def main():
    investigator = TokenInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())