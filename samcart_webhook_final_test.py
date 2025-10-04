#!/usr/bin/env python3
"""
SamCart Webhook Final Debug Test
================================

Final comprehensive test of SamCart webhook integration after fixing import issues.
This will test all webhook endpoints and provide final diagnosis.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

print(f"🔍 SAMCART WEBHOOK FINAL DEBUG TEST")
print(f"Backend URL: {BACKEND_URL}")
print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
print("=" * 80)

async def test_webhook_endpoints():
    """Test all SamCart webhook endpoints"""
    print("\n🔗 TESTING WEBHOOK ENDPOINTS...")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Test 1: Webhook logs endpoint
            print("1. Testing webhook logs endpoint...")
            url = f"{BACKEND_URL}/api/webhook/samcart/logs"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Logs endpoint working - {len(data.get('logs', []))} logs found")
                else:
                    print(f"   ❌ Logs endpoint failed: HTTP {response.status}")
            
            # Test 2: Webhook stats endpoint
            print("2. Testing webhook stats endpoint...")
            url = f"{BACKEND_URL}/api/webhook/samcart/stats"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Stats endpoint working - {data.get('total_webhooks', 0)} total webhooks")
                else:
                    print(f"   ❌ Stats endpoint failed: HTTP {response.status}")
            
            # Test 3: Main webhook endpoint (should return 405 for GET)
            print("3. Testing main webhook endpoint...")
            url = f"{BACKEND_URL}/api/webhook/samcart"
            async with session.get(url) as response:
                if response.status == 405:
                    print(f"   ✅ Main webhook endpoint accessible (405 expected for GET)")
                else:
                    print(f"   ⚠️  Unexpected response: HTTP {response.status}")
            
            # Test 4: Test webhook endpoint
            print("4. Testing webhook test endpoint...")
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            test_email = f"debug.test.{int(datetime.now().timestamp())}@example.com"
            
            async with session.post(url, params={"test_email": test_email}) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Test endpoint working - created practice: {data.get('practice_info', {}).get('practice_name', 'N/A')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   ❌ Test endpoint failed: HTTP {response.status}")
                    print(f"      Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing webhook endpoints: {e}")
        return False

async def check_recent_webhook_activity():
    """Check for any webhook activity in the last hour"""
    print("\n🕐 CHECKING RECENT WEBHOOK ACTIVITY...")
    print("-" * 50)
    
    try:
        # Connect to MongoDB directly
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Check for webhook logs in the last hour
        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(hours=1)
        
        # Get recent webhook logs
        recent_logs = await db.samcart_webhook_logs.find({
            "created_at": {"$gte": recent_cutoff}
        }).sort("created_at", -1).to_list(length=10)
        
        print(f"📊 Webhook logs in last hour: {len(recent_logs)}")
        
        if recent_logs:
            print("\n📋 RECENT WEBHOOK ACTIVITY:")
            for i, log in enumerate(recent_logs, 1):
                print(f"  {i}. Event: {log.get('event_type', 'N/A')}")
                print(f"     Status: {log.get('processing_status', 'N/A')}")
                print(f"     Time: {log.get('created_at', 'N/A')}")
                if log.get('error_message'):
                    print(f"     Error: {log.get('error_message')}")
                print()
        else:
            print("⚠️  NO RECENT WEBHOOK ACTIVITY in the last hour")
            print("   This confirms no webhook was received for the user's payment attempt")
        
        # Check for recent practice accounts
        recent_practices = await db.practices.find({
            "source": "samcart",
            "createdAt": {"$gte": recent_cutoff}
        }).sort("createdAt", -1).to_list(length=5)
        
        print(f"\n🏥 SamCart practices created in last hour: {len(recent_practices)}")
        
        if recent_practices:
            for i, practice in enumerate(recent_practices, 1):
                email = practice.get('email', 'N/A')
                is_test = 'test' in email.lower() or 'example.com' in email.lower()
                account_type = "🧪 TEST" if is_test else "👤 REAL"
                
                print(f"  {i}. {practice.get('name', 'N/A')} ({account_type})")
                print(f"     Email: {email}")
                print(f"     Created: {practice.get('createdAt', 'N/A')}")
        
        client.close()
        return len(recent_logs) > 0
        
    except Exception as e:
        print(f"❌ Error checking recent activity: {e}")
        return False

async def provide_final_diagnosis():
    """Provide final diagnosis and recommendations"""
    print("\n" + "=" * 80)
    print("🎯 FINAL DIAGNOSIS AND RECOMMENDATIONS")
    print("=" * 80)
    
    # Test webhook functionality
    webhook_test_passed = await test_webhook_endpoints()
    recent_activity = await check_recent_webhook_activity()
    
    print(f"\n📊 FINAL TEST RESULTS:")
    print(f"   Webhook Endpoints: {'✅ WORKING' if webhook_test_passed else '❌ FAILED'}")
    print(f"   Recent Activity: {'✅ DETECTED' if recent_activity else '❌ NONE'}")
    
    if webhook_test_passed and not recent_activity:
        print(f"\n🎯 CONCLUSION:")
        print(f"   ✅ SamCart webhook integration is WORKING correctly")
        print(f"   ❌ NO webhook was received for the user's payment attempt")
        
        print(f"\n🚨 ROOT CAUSE:")
        print(f"   The user's payment attempt did NOT trigger a webhook from SamCart")
        
        print(f"\n💡 MOST LIKELY REASONS:")
        print(f"   1. 🔗 SamCart webhook URL is incorrect in SamCart dashboard")
        print(f"   2. 🚫 SamCart webhook is disabled or not configured for this product")
        print(f"   3. 💳 Payment failed before completion (no webhook sent)")
        print(f"   4. 🌐 SamCart webhook delivery failed (network/firewall issue)")
        print(f"   5. ⏰ Webhook delivery delayed (check again in a few minutes)")
        
        print(f"\n🔧 IMMEDIATE ACTIONS:")
        print(f"   1. Check SamCart dashboard webhook configuration")
        print(f"   2. Verify webhook URL: {BACKEND_URL}/api/webhook/samcart")
        print(f"   3. Test webhook delivery from SamCart admin panel")
        print(f"   4. Check SamCart transaction logs for the payment")
        print(f"   5. Verify webhook is enabled for ProductPurchased events")
        
    elif not webhook_test_passed:
        print(f"\n🚨 CRITICAL ISSUE:")
        print(f"   SamCart webhook integration has technical problems")
        print(f"   Backend endpoints are not functioning correctly")
        
        print(f"\n🔧 TECHNICAL FIXES NEEDED:")
        print(f"   1. Fix backend import/configuration issues")
        print(f"   2. Restart backend services")
        print(f"   3. Verify database connectivity")
        print(f"   4. Check email service configuration")
        
    else:
        print(f"\n✅ SYSTEM STATUS:")
        print(f"   SamCart webhook integration is working correctly")
        print(f"   Recent webhook activity detected")
        print(f"   User's payment may have been processed successfully")
    
    return webhook_test_passed

async def main():
    """Main debug function"""
    success = await provide_final_diagnosis()
    
    print(f"\n" + "=" * 80)
    print(f"🏁 FINAL SUMMARY")
    print(f"=" * 80)
    
    if success:
        print(f"✅ SamCart webhook system is operational")
        print(f"❌ User's specific payment did not trigger a webhook")
        print(f"🔍 Investigation needed at SamCart configuration level")
    else:
        print(f"❌ SamCart webhook system has technical issues")
        print(f"🔧 Backend fixes required before investigating payment issue")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())