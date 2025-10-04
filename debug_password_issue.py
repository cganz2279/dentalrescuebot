#!/usr/bin/env python3
"""
Debug Password Corruption Issue in SamCart Webhook Accounts
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

async def debug_password_issue():
    """Debug the password corruption issue"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 DEBUGGING PASSWORD CORRUPTION ISSUE")
        print("=" * 50)
        
        # Test 1: Create a new account via webhook test endpoint
        print("\n1. Creating new test account via webhook...")
        test_email = f"debug.password.{datetime.now().strftime('%H%M%S')}@test.com"
        
        url = f"{BACKEND_URL}/api/webhook/samcart/test"
        params = {"test_email": test_email}
        
        async with session.post(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "success":
                    print(f"✅ Account created successfully for {test_email}")
                    practice_info = data.get("practice_info", {})
                    print(f"   Practice: {practice_info.get('practice_name')}")
                    print(f"   Email: {practice_info.get('email')}")
                else:
                    print(f"❌ Account creation failed: {data}")
                    return
            else:
                print(f"❌ HTTP {response.status}: {await response.text()}")
                return
        
        # Test 2: Try to login with the created account
        print(f"\n2. Testing login with created account {test_email}...")
        
        # Since we don't have the actual password, test with wrong password to see error type
        login_url = f"{BACKEND_URL}/api/auth/login"
        login_data = {
            "email": test_email,
            "password": "wrong_password_123"
        }
        
        async with session.post(login_url, json=login_data) as response:
            response_text = await response.text()
            print(f"   Login attempt result: HTTP {response.status}")
            print(f"   Response: {response_text}")
            
            if response.status == 500:
                print("🚨 CRITICAL: 500 error indicates password field corruption!")
            elif response.status == 401:
                print("✅ 401 error is expected for wrong password - account structure OK")
            else:
                print(f"⚠️ Unexpected response: {response.status}")
        
        # Test 3: Test password reset for the account
        print(f"\n3. Testing password reset for {test_email}...")
        
        reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
        reset_data = {
            "email": test_email,
            "recovery_method": "email"
        }
        
        async with session.post(reset_url, json=reset_data) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    print("✅ Password reset email sent successfully")
                    print(f"   Methods: {data.get('sent_methods', [])}")
                else:
                    print(f"❌ Password reset failed: {data}")
            else:
                print(f"❌ Password reset HTTP {response.status}: {await response.text()}")
        
        # Test 4: Check webhook logs for any errors
        print("\n4. Checking recent webhook logs...")
        
        logs_url = f"{BACKEND_URL}/api/webhook/samcart/logs"
        async with session.get(logs_url) as response:
            if response.status == 200:
                data = await response.json()
                logs = data.get("logs", [])
                print(f"✅ Retrieved {len(logs)} webhook logs")
                
                # Show recent logs
                for i, log in enumerate(logs[:3]):
                    timestamp = log.get('created_at', 'Unknown')
                    event_type = log.get('event_type', 'Unknown')
                    status = log.get('processing_status', 'Unknown')
                    error = log.get('error_message', 'None')
                    
                    print(f"   Log {i+1}: {timestamp} - {event_type} - {status}")
                    if error != 'None':
                        print(f"      Error: {error}")
            else:
                print(f"❌ Failed to get logs: HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_password_issue())