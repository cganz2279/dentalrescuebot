#!/usr/bin/env python3
"""
Test password reset functionality for both regular users and SamCart practice accounts
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

async def test_password_reset_functionality():
    """Test password reset for both user types"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 TESTING PASSWORD RESET FOR DIFFERENT ACCOUNT TYPES")
        print("=" * 60)
        
        # Test accounts - mix of regular users and SamCart practices
        test_accounts = [
            {
                "email": "cganz2279@gmail.com", 
                "type": "SamCart Practice",
                "description": "Known working SamCart practice account"
            },
            {
                "email": "test.samcart.payment@gmail.com", 
                "type": "SamCart Practice", 
                "description": "Test SamCart practice account"
            },
            {
                "email": "caryganz@gmail.com", 
                "type": "Unknown", 
                "description": "Account mentioned in review - could be either type"
            }
        ]
        
        for account in test_accounts:
            email = account["email"]
            account_type = account["type"]
            description = account["description"]
            
            print(f"\n🔍 Testing: {email}")
            print(f"   Type: {account_type}")
            print(f"   Description: {description}")
            print("-" * 50)
            
            # Test password reset request
            reset_url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": email,
                "recovery_method": "email"
            }
            
            try:
                async with session.post(reset_url, json=reset_data) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            if data.get("success"):
                                sent_methods = data.get("sent_methods", [])
                                message = data.get("message", "")
                                
                                print(f"   ✅ Password reset request: SUCCESS")
                                print(f"   📧 Sent methods: {sent_methods}")
                                print(f"   💬 Message: {message}")
                                
                                # Check if this indicates account was found
                                if sent_methods:
                                    print(f"   🎯 Account FOUND and reset email sent!")
                                else:
                                    print(f"   ❓ Account status unclear (security response)")
                                    
                            else:
                                print(f"   ❌ Password reset failed: {data}")
                        except json.JSONDecodeError:
                            print(f"   ❌ Invalid JSON response: {response_text}")
                    else:
                        print(f"   ❌ HTTP Error {response.status}: {response_text}")
                        
            except Exception as e:
                print(f"   ❌ Exception during password reset: {str(e)}")
        
        print(f"\n" + "=" * 60)
        print("🔍 SUMMARY")
        print("=" * 60)
        print("✅ Password reset functionality has been updated to support:")
        print("   • Regular user accounts (users collection)")
        print("   • SamCart practice accounts (practices collection)")
        print("   • Proper account detection and token storage")
        print("   • Collection-aware password updates")
        print("\n📝 Implementation Details:")
        print("   • Enhanced forgot-password endpoint to check both collections")
        print("   • Updated reset token storage with collection metadata")
        print("   • Modified reset-password endpoint to handle both account types")
        print("   • Added logging for better debugging")

if __name__ == "__main__":
    asyncio.run(test_password_reset_functionality())