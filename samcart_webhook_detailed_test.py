#!/usr/bin/env python3
"""
SamCart Webhook Detailed Debug Test
===================================

This test provides detailed debugging of the SamCart webhook issue.
Focus on checking recent webhook activity and database state.
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentalpractice-hub-1.preview.emergentagent.com')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'dentist_management')

print(f"🔍 SAMCART WEBHOOK DETAILED DEBUG")
print(f"Backend URL: {BACKEND_URL}")
print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
print("=" * 80)

async def check_webhook_logs_detailed():
    """Check webhook logs with detailed analysis"""
    print("\n🔍 DETAILED WEBHOOK LOGS ANALYSIS...")
    print("-" * 50)
    
    try:
        # Connect to MongoDB directly
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Get all webhook logs
        logs = await db.samcart_webhook_logs.find().sort("created_at", -1).to_list(length=50)
        
        print(f"📊 Total webhook logs in database: {len(logs)}")
        
        if not logs:
            print("⚠️  NO WEBHOOK LOGS FOUND IN DATABASE")
            print("   This means no webhooks have ever been received from SamCart")
            client.close()
            return False
        
        # Analyze logs
        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(minutes=30)
        
        print(f"\n📋 ALL WEBHOOK LOGS (most recent first):")
        recent_count = 0
        
        for i, log in enumerate(logs, 1):
            webhook_id = log.get('webhook_id', 'N/A')
            event_type = log.get('event_type', 'N/A')
            status = log.get('processing_status', 'N/A')
            created_at = log.get('created_at')
            error_msg = log.get('error_message', '')
            
            # Handle different timestamp formats
            log_time_str = "N/A"
            is_recent = False
            
            if created_at:
                try:
                    if isinstance(created_at, datetime):
                        log_time = created_at
                    else:
                        # Try parsing string timestamp
                        log_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                    
                    log_time_str = log_time.strftime('%Y-%m-%d %H:%M:%S UTC')
                    is_recent = log_time >= recent_cutoff
                    if is_recent:
                        recent_count += 1
                        
                except Exception as e:
                    log_time_str = f"Parse error: {created_at}"
            
            recent_marker = "🔥 RECENT" if is_recent else ""
            
            print(f"  {i}. {recent_marker}")
            print(f"     Webhook ID: {webhook_id}")
            print(f"     Event Type: {event_type}")
            print(f"     Status: {status}")
            print(f"     Time: {log_time_str}")
            if error_msg:
                print(f"     Error: {error_msg}")
            print()
        
        print(f"🕐 Recent logs (last 30 minutes): {recent_count}")
        
        if recent_count == 0:
            print("⚠️  NO RECENT WEBHOOK ACTIVITY")
            print("   SamCart did not send a webhook for the recent payment attempt")
        
        client.close()
        return recent_count > 0
        
    except Exception as e:
        print(f"❌ Error checking webhook logs: {e}")
        return False

async def check_recent_practices_detailed():
    """Check recent practice accounts with detailed info"""
    print("\n🏥 DETAILED RECENT PRACTICE ANALYSIS...")
    print("-" * 50)
    
    try:
        # Connect to MongoDB directly
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Check for practices created in the last hour
        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(hours=1)
        
        # Get recent practices
        recent_practices = await db.practices.find({
            "createdAt": {"$gte": recent_cutoff}
        }).sort("createdAt", -1).to_list(length=20)
        
        print(f"🕐 Practices created in last hour: {len(recent_practices)}")
        
        if recent_practices:
            print("\n📋 RECENT PRACTICE ACCOUNTS:")
            for i, practice in enumerate(recent_practices, 1):
                print(f"  {i}. Practice: {practice.get('name', 'N/A')}")
                print(f"     Email: {practice.get('email', 'N/A')}")
                print(f"     Source: {practice.get('source', 'N/A')}")
                print(f"     Created: {practice.get('createdAt', 'N/A')}")
                print(f"     Status: {practice.get('subscription', {}).get('status', 'N/A')}")
                
                # Check if this is a real customer vs test
                email = practice.get('email', '')
                if 'test' in email.lower() or 'example.com' in email.lower():
                    print(f"     🧪 TEST ACCOUNT")
                else:
                    print(f"     👤 REAL CUSTOMER")
                print()
        else:
            print("⚠️  NO RECENT PRACTICE ACCOUNTS CREATED")
            
            # Check total SamCart practices
            total_samcart = await db.practices.count_documents({"source": "samcart"})
            print(f"\n📊 Total SamCart practices ever: {total_samcart}")
        
        client.close()
        return len(recent_practices) > 0
        
    except Exception as e:
        print(f"❌ Error checking recent practices: {e}")
        return False

async def test_webhook_endpoint_detailed():
    """Test webhook endpoint with detailed response"""
    print("\n🔗 DETAILED WEBHOOK ENDPOINT TEST...")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test webhook endpoint accessibility
            url = f"{BACKEND_URL}/api/webhook/samcart"
            
            print(f"📡 Testing webhook URL: {url}")
            
            async with session.get(url) as response:
                status = response.status
                headers = dict(response.headers)
                
                print(f"   Status: HTTP {status}")
                print(f"   Server: {headers.get('server', 'N/A')}")
                print(f"   Content-Type: {headers.get('content-type', 'N/A')}")
                
                if status == 405:
                    print("✅ Webhook endpoint is accessible (405 Method Not Allowed expected for GET)")
                    return True
                elif status == 404:
                    print("❌ Webhook endpoint not found - routing issue")
                    return False
                else:
                    print(f"⚠️  Unexpected response: {status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing webhook endpoint: {e}")
        return False

async def check_samcart_configuration():
    """Check SamCart configuration and provide guidance"""
    print("\n⚙️  SAMCART CONFIGURATION CHECK...")
    print("-" * 50)
    
    expected_webhook_url = f"{BACKEND_URL}/api/webhook/samcart"
    
    print(f"🔗 Expected webhook URL: {expected_webhook_url}")
    print(f"🔑 Webhook secret configured: {'Yes' if os.environ.get('SAMCART_WEBHOOK_SECRET') else 'No'}")
    print(f"📧 Admin email: {os.environ.get('ADMIN_EMAIL', 'Not configured')}")
    print(f"📤 Sender email: {os.environ.get('SENDER_EMAIL', 'Not configured')}")
    
    print(f"\n📋 SAMCART WEBHOOK CONFIGURATION CHECKLIST:")
    print(f"   1. ✅ Webhook URL: {expected_webhook_url}")
    print(f"   2. ⚠️  Event Types: ProductPurchased, OrderCompleted, Order.Completed")
    print(f"   3. ⚠️  HTTP Method: POST")
    print(f"   4. ⚠️  Content-Type: application/json")
    print(f"   5. ⚠️  Webhook Status: Active/Enabled")
    
    return True

async def main():
    """Main debug function"""
    print("🚀 STARTING DETAILED SAMCART WEBHOOK DEBUG")
    print("=" * 80)
    
    results = {
        'webhook_logs': await check_webhook_logs_detailed(),
        'recent_practices': await check_recent_practices_detailed(),
        'endpoint_test': await test_webhook_endpoint_detailed(),
        'config_check': await check_samcart_configuration()
    }
    
    print("\n" + "=" * 80)
    print("🎯 DETAILED DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    # Detailed analysis
    if not results['webhook_logs']:
        print("🚨 ROOT CAUSE IDENTIFIED: NO RECENT WEBHOOK ACTIVITY")
        print("\n💡 MOST LIKELY SCENARIOS:")
        print("   1. 🔗 SamCart webhook URL is incorrect or not configured")
        print("   2. 🚫 SamCart webhook is disabled or not triggered by payment")
        print("   3. 💳 Payment process failed before webhook trigger")
        print("   4. 🌐 Network/firewall blocking webhook delivery")
        
        if not results['recent_practices']:
            print("\n✅ CONFIRMATION: No practice accounts created recently")
            print("   This confirms the payment did not result in account creation")
        
        print(f"\n🔧 IMMEDIATE ACTIONS REQUIRED:")
        print(f"   1. Verify SamCart webhook URL: {BACKEND_URL}/api/webhook/samcart")
        print(f"   2. Check SamCart dashboard for webhook configuration")
        print(f"   3. Verify webhook is enabled for ProductPurchased events")
        print(f"   4. Test webhook delivery from SamCart admin panel")
        
    elif results['recent_practices']:
        print("✅ WEBHOOK SYSTEM WORKING: Recent activity detected")
        print("   But no activity in last 30 minutes for user's payment attempt")
        
    else:
        print("⚠️  MIXED RESULTS: Webhooks received but no recent accounts")
        print("   Investigate webhook processing errors")
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test.replace('_', ' ').title()}: {status}")
    
    return any(results.values())

if __name__ == "__main__":
    asyncio.run(main())