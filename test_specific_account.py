#!/usr/bin/env python3
"""
Test specific account that's showing password corruption
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"

async def test_specific_accounts():
    """Test specific accounts showing issues"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 TESTING SPECIFIC ACCOUNTS WITH PASSWORD ISSUES")
        print("=" * 60)
        
        # Test accounts that might have issues based on logs
        test_accounts = [
            "caryganz@gmail.com",  # This was mentioned in the review request
            "test.samcart.payment@gmail.com",  # Our test email
            "cganz2279@gmail.com"  # Working practice account
        ]
        
        for email in test_accounts:
            print(f"\n🔍 Testing account: {email}")
            print("-" * 40)
            
            # Test 1: Login attempt with wrong password
            login_url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": email,
                "password": "wrong_password_test"
            }
            
            async with session.post(login_url, json=login_data) as response:
                response_text = await response.text()
                print(f"   Login test: HTTP {response.status}")
                
                if response.status == 500:
                    print("   🚨 CRITICAL: 500 error - PASSWORD FIELD CORRUPTION DETECTED!")
                    print(f"   Response: {response_text}")
                elif response.status == 401:
                    print("   ✅ 401 error - Account structure OK")
                else:
                    print(f"   ⚠️ Unexpected: {response.status} - {response_text}")
            
            # Test 2: Password reset
            reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": email,
                "recovery_method": "email"
            }
            
            async with session.post(reset_url, json=reset_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        methods = data.get("sent_methods", [])
                        print(f"   ✅ Password reset: Success (methods: {methods})")
                    else:
                        print(f"   ❌ Password reset: Failed - {data}")
                else:
                    print(f"   ❌ Password reset: HTTP {response.status}")
        
        # Test 3: Check if we can create account for caryganz@gmail.com via webhook
        print(f"\n🔍 Testing webhook account creation for caryganz@gmail.com")
        print("-" * 50)
        
        webhook_url = f"{BACKEND_URL}/api/webhook/samcart/test"
        params = {"test_email": "caryganz@gmail.com"}
        
        async with session.post(webhook_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                status = data.get("status")
                message = data.get("message", "No message")
                print(f"   Webhook test result: {status}")
                print(f"   Message: {message}")
                
                if status == "duplicate":
                    print("   ✅ Account exists - duplicate detection working")
                elif status == "success":
                    print("   ✅ New account created successfully")
                else:
                    print(f"   ❌ Unexpected status: {data}")
            else:
                print(f"   ❌ Webhook test failed: HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(test_specific_accounts())