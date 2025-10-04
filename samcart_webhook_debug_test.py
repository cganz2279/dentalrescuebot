#!/usr/bin/env python3
"""
SamCart Webhook Debug Test
==========================

This test debugs the SamCart webhook integration issue where user clicked 
"Start my free trial" but nothing happened. We'll check:

1. Webhook logs for recent activity
2. Webhook stats to see if any webhooks were received
3. Recent practice accounts in MongoDB
4. Backend logs for webhook-related errors

Time window: Last 30 minutes since user just attempted this
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

print(f"🔍 SAMCART WEBHOOK DEBUG TEST")
print(f"Backend URL: {BACKEND_URL}")
print(f"MongoDB URL: {MONGO_URL}")
print(f"Database: {DB_NAME}")
print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
print("=" * 80)

class SamCartWebhookDebugger:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.mongo_client = None
        self.db = None
        self.session = None
        
    async def setup(self):
        """Initialize connections"""
        try:
            # Setup MongoDB connection
            self.mongo_client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            
            # Setup HTTP session
            self.session = aiohttp.ClientSession()
            
            print("✅ Connections initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize connections: {e}")
            return False
    
    async def cleanup(self):
        """Clean up connections"""
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()
    
    async def check_webhook_logs(self):
        """Check recent webhook logs via API"""
        print("\n🔍 CHECKING WEBHOOK LOGS...")
        print("-" * 50)
        
        try:
            url = f"{self.backend_url}/api/webhook/samcart/logs"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logs = data.get('logs', [])
                    
                    print(f"📊 Total webhook logs found: {len(logs)}")
                    
                    if not logs:
                        print("⚠️  NO WEBHOOK LOGS FOUND - This suggests no webhooks have been received")
                        return False
                    
                    # Check for recent logs (last 30 minutes)
                    now = datetime.now(timezone.utc)
                    recent_cutoff = now - timedelta(minutes=30)
                    
                    recent_logs = []
                    for log in logs:
                        try:
                            # Parse the created_at timestamp
                            if isinstance(log.get('created_at'), str):
                                log_time = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                            else:
                                log_time = log.get('created_at')
                            
                            if log_time and log_time >= recent_cutoff:
                                recent_logs.append(log)
                        except Exception as e:
                            print(f"⚠️  Error parsing log timestamp: {e}")
                    
                    print(f"🕐 Recent logs (last 30 minutes): {len(recent_logs)}")
                    
                    if recent_logs:
                        print("\n📋 RECENT WEBHOOK ACTIVITY:")
                        for i, log in enumerate(recent_logs[:5], 1):  # Show last 5
                            print(f"  {i}. Webhook ID: {log.get('webhook_id', 'N/A')}")
                            print(f"     Event Type: {log.get('event_type', 'N/A')}")
                            print(f"     Status: {log.get('processing_status', 'N/A')}")
                            print(f"     Time: {log.get('created_at', 'N/A')}")
                            if log.get('error_message'):
                                print(f"     Error: {log.get('error_message')}")
                            print()
                        return True
                    else:
                        print("⚠️  NO RECENT WEBHOOK ACTIVITY in the last 30 minutes")
                        print("   This suggests SamCart did not send a webhook for the payment attempt")
                        return False
                        
                else:
                    print(f"❌ Failed to fetch webhook logs: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error checking webhook logs: {e}")
            return False
    
    async def check_webhook_stats(self):
        """Check webhook statistics via API"""
        print("\n📊 CHECKING WEBHOOK STATISTICS...")
        print("-" * 50)
        
        try:
            url = f"{self.backend_url}/api/webhook/samcart/stats"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    stats = await response.json()
                    
                    print(f"📈 Total webhooks received: {stats.get('total_webhooks', 0)}")
                    print(f"✅ Successful webhooks: {stats.get('successful_webhooks', 0)}")
                    print(f"❌ Failed webhooks: {stats.get('failed_webhooks', 0)}")
                    print(f"📊 Success rate: {stats.get('success_rate', 0):.1f}%")
                    print(f"🆕 Recent practice signups (30 days): {stats.get('recent_practice_signups', 0)}")
                    
                    if stats.get('total_webhooks', 0) == 0:
                        print("\n⚠️  CRITICAL: NO WEBHOOKS HAVE EVER BEEN RECEIVED")
                        print("   This indicates either:")
                        print("   1. SamCart webhook URL is not configured correctly")
                        print("   2. SamCart is not sending webhooks")
                        print("   3. Webhooks are being blocked by firewall/proxy")
                        return False
                    
                    return True
                    
                else:
                    print(f"❌ Failed to fetch webhook stats: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error checking webhook stats: {e}")
            return False
    
    async def check_recent_practices(self):
        """Check for recent practice accounts in MongoDB"""
        print("\n🏥 CHECKING RECENT PRACTICE ACCOUNTS...")
        print("-" * 50)
        
        try:
            # Check for practices created in the last hour
            now = datetime.now(timezone.utc)
            recent_cutoff = now - timedelta(hours=1)
            
            # Get all recent practices
            recent_practices = await self.db.practices.find({
                "createdAt": {"$gte": recent_cutoff}
            }).sort("createdAt", -1).to_list(length=10)
            
            print(f"🕐 Practices created in last hour: {len(recent_practices)}")
            
            if recent_practices:
                print("\n📋 RECENT PRACTICE ACCOUNTS:")
                for i, practice in enumerate(recent_practices, 1):
                    print(f"  {i}. Practice: {practice.get('name', 'N/A')}")
                    print(f"     Email: {practice.get('email', 'N/A')}")
                    print(f"     Source: {practice.get('source', 'N/A')}")
                    print(f"     Created: {practice.get('createdAt', 'N/A')}")
                    print(f"     Status: {practice.get('subscription', {}).get('status', 'N/A')}")
                    print()
                return True
            else:
                print("⚠️  NO RECENT PRACTICE ACCOUNTS CREATED")
                print("   This confirms no account was created from the payment attempt")
                
                # Check for any SamCart practices ever
                samcart_practices = await self.db.practices.count_documents({"source": "samcart"})
                print(f"\n📊 Total SamCart practices ever created: {samcart_practices}")
                
                return False
                
        except Exception as e:
            print(f"❌ Error checking recent practices: {e}")
            return False
    
    async def check_backend_logs(self):
        """Check backend logs for webhook-related errors"""
        print("\n📝 CHECKING BACKEND LOGS...")
        print("-" * 50)
        
        try:
            # Check supervisor backend logs
            import subprocess
            
            # Get recent backend logs
            result = subprocess.run(
                ['tail', '-n', '100', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for webhook-related entries
                webhook_lines = []
                for line in logs.split('\n'):
                    if any(keyword in line.lower() for keyword in ['webhook', 'samcart', 'error', 'exception']):
                        webhook_lines.append(line)
                
                if webhook_lines:
                    print(f"🔍 Found {len(webhook_lines)} relevant log entries:")
                    for line in webhook_lines[-10:]:  # Show last 10
                        print(f"   {line}")
                else:
                    print("ℹ️  No webhook-related errors found in recent backend logs")
                
                return True
            else:
                print(f"⚠️  Could not read backend logs: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking backend logs: {e}")
            return False
    
    async def test_webhook_endpoint(self):
        """Test if the webhook endpoint is accessible"""
        print("\n🔗 TESTING WEBHOOK ENDPOINT ACCESSIBILITY...")
        print("-" * 50)
        
        try:
            # Test the webhook endpoint with a simple GET request
            url = f"{self.backend_url}/api/webhook/samcart"
            
            async with self.session.get(url) as response:
                print(f"📡 Webhook endpoint status: HTTP {response.status}")
                
                if response.status == 405:  # Method Not Allowed is expected for GET on POST endpoint
                    print("✅ Webhook endpoint is accessible (405 Method Not Allowed is expected)")
                    return True
                elif response.status == 404:
                    print("❌ Webhook endpoint not found - routing issue")
                    return False
                else:
                    print(f"⚠️  Unexpected response: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing webhook endpoint: {e}")
            return False
    
    async def run_comprehensive_debug(self):
        """Run all debug checks"""
        print("🚀 STARTING COMPREHENSIVE SAMCART WEBHOOK DEBUG")
        print("=" * 80)
        
        if not await self.setup():
            return False
        
        try:
            results = {
                'webhook_logs': await self.check_webhook_logs(),
                'webhook_stats': await self.check_webhook_stats(),
                'recent_practices': await self.check_recent_practices(),
                'backend_logs': await self.check_backend_logs(),
                'endpoint_test': await self.test_webhook_endpoint()
            }
            
            print("\n" + "=" * 80)
            print("🎯 DIAGNOSTIC SUMMARY")
            print("=" * 80)
            
            # Analyze results
            if not results['webhook_logs'] and not results['webhook_stats']:
                print("🚨 CRITICAL ISSUE IDENTIFIED:")
                print("   NO WEBHOOKS HAVE BEEN RECEIVED FROM SAMCART")
                print("\n💡 LIKELY CAUSES:")
                print("   1. SamCart webhook URL is incorrect or not configured")
                print("   2. SamCart webhook is disabled or not triggered")
                print("   3. Network/firewall blocking webhook delivery")
                print("   4. SamCart payment process didn't complete successfully")
                
                print(f"\n🔧 EXPECTED WEBHOOK URL: {self.backend_url}/api/webhook/samcart")
                print("   ↳ Verify this URL is configured in SamCart dashboard")
                
            elif not results['recent_practices']:
                print("🚨 WEBHOOK RECEIVED BUT NO ACCOUNT CREATED:")
                print("   Webhooks are being received but account creation failed")
                print("\n💡 CHECK:")
                print("   1. Webhook payload format compatibility")
                print("   2. Database connection issues")
                print("   3. Email service configuration")
                
            else:
                print("✅ WEBHOOK SYSTEM APPEARS TO BE WORKING")
                print("   Recent activity detected - investigate specific payment")
            
            print(f"\n📊 TEST RESULTS:")
            for test, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {test.replace('_', ' ').title()}: {status}")
            
            return any(results.values())
            
        finally:
            await self.cleanup()

async def main():
    """Main debug function"""
    debugger = SamCartWebhookDebugger()
    success = await debugger.run_comprehensive_debug()
    
    if not success:
        print("\n🚨 URGENT ACTION REQUIRED:")
        print("   The SamCart webhook integration is not functioning")
        print("   Customer payments are not creating practice accounts")
        print("   Immediate investigation and fix needed")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())