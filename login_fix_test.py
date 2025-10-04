#!/usr/bin/env python3
"""
Quick test to verify the login fix for SamCart accounts
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

async def test_login_fix():
    """Test the login fix"""
    
    # First create a test account
    import uuid
    test_email = f"loginfix.test.{uuid.uuid4().hex[:8]}@example.com"
    
    async with aiohttp.ClientSession() as session:
        # Create test account
        print("Creating test account...")
        async with session.post(
            f"{API_BASE}/webhook/samcart/test",
            params={"test_email": test_email}
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('status') == 'success':
                    practice_info = data.get('practice_info', {})
                    password = practice_info.get('password')
                    print(f"✅ Test account created: {test_email}")
                    print(f"   Password: {password}")
                    
                    # Now test login
                    print("\nTesting login...")
                    login_payload = {
                        "email": test_email,
                        "password": password
                    }
                    
                    async with session.post(
                        f"{API_BASE}/auth/login",
                        json=login_payload,
                        headers={"Content-Type": "application/json"}
                    ) as login_response:
                        if login_response.status == 200:
                            login_data = await login_response.json()
                            if login_data.get('success') and login_data.get('token'):
                                print("✅ Login successful!")
                                print(f"   User: {login_data.get('user', {}).get('email')}")
                                print(f"   Practice: {login_data.get('practice', {}).get('name')}")
                                print(f"   Token: {login_data.get('token')[:20]}...")
                                return True
                            else:
                                print(f"❌ Login failed: {login_data}")
                                return False
                        else:
                            response_text = await login_response.text()
                            print(f"❌ Login HTTP error {login_response.status}: {response_text}")
                            return False
                else:
                    print(f"❌ Account creation failed: {data}")
                    return False
            else:
                response_text = await response.text()
                print(f"❌ Account creation HTTP error {response.status}: {response_text}")
                return False

if __name__ == "__main__":
    success = asyncio.run(test_login_fix())
    print(f"\nLogin fix test: {'PASSED' if success else 'FAILED'}")