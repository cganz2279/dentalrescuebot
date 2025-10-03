#!/usr/bin/env python3
"""
SamCart Webhook Integration Verification Test
Testing webhook activity since 5:55 PM on 10/3/2025 as requested in review
"""

import requests
import json
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env
frontend_env_path = '/app/frontend/.env'
backend_url = None
try:
    with open(frontend_env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.split('=', 1)[1].strip()
                break
except:
    pass

if not backend_url:
    backend_url = "https://aftercareportal.preview.emergentagent.com"

print(f"🔗 Using backend URL: {backend_url}")

def test_samcart_webhook_verification():
    """Test SamCart webhook integration verification as requested"""
    
    print("\n" + "="*80)
    print("🎯 SAMCART WEBHOOK INTEGRATION VERIFICATION")
    print("   Testing webhook activity since 5:55 PM on 10/3/2025")
    print("="*80)
    
    # Define the time window (5:55 PM today)
    target_time = datetime.now(timezone.utc).replace(hour=17, minute=55, second=0, microsecond=0)
    if datetime.now(timezone.utc) < target_time:
        # If it's before 5:55 PM today, check yesterday's 5:55 PM
        target_time = target_time - timedelta(days=1)
    
    print(f"📅 Checking for webhook activity since: {target_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    results = {
        "webhook_logs_check": False,
        "webhook_stats_check": False,
        "recent_activity_found": False,
        "connection_verified": False
    }
    
    try:
        # 1. Check Recent Webhook Activity - GET /api/webhook/samcart/logs
        print("\n1️⃣ CHECKING RECENT WEBHOOK LOGS...")
        logs_url = f"{backend_url}/api/webhook/samcart/logs"
        
        try:
            logs_response = requests.get(logs_url, timeout=10)
            print(f"   📡 GET {logs_url}")
            print(f"   📊 Status: {logs_response.status_code}")
            
            if logs_response.status_code == 200:
                results["webhook_logs_check"] = True
                logs_data = logs_response.json()
                
                print(f"   📋 Total logs found: {logs_data.get('count', 0)}")
                
                # Check for recent activity since 5:55 PM
                recent_logs = []
                if logs_data.get('logs'):
                    for log in logs_data['logs']:
                        try:
                            # Handle different datetime formats
                            created_at = log['created_at']
                            if isinstance(created_at, str):
                                if created_at.endswith('Z'):
                                    log_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                elif '+' in created_at or created_at.endswith('UTC'):
                                    log_time = datetime.fromisoformat(created_at.replace('UTC', '').strip())
                                    if log_time.tzinfo is None:
                                        log_time = log_time.replace(tzinfo=timezone.utc)
                                else:
                                    log_time = datetime.fromisoformat(created_at)
                                    if log_time.tzinfo is None:
                                        log_time = log_time.replace(tzinfo=timezone.utc)
                            else:
                                log_time = created_at
                                if log_time.tzinfo is None:
                                    log_time = log_time.replace(tzinfo=timezone.utc)
                            
                            if log_time >= target_time:
                                recent_logs.append(log)
                        except Exception as e:
                            print(f"      ⚠️ Error parsing log timestamp: {e}")
                            continue
                
                if recent_logs:
                    results["recent_activity_found"] = True
                    print(f"   ✅ Found {len(recent_logs)} webhook events since 5:55 PM today!")
                    
                    for i, log in enumerate(recent_logs[:3], 1):  # Show first 3
                        log_time = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                        print(f"      {i}. Event: {log.get('event_type', 'unknown')} at {log_time.strftime('%H:%M:%S')} UTC")
                        print(f"         Status: {log.get('processing_status', 'unknown')}")
                        if log.get('error_message'):
                            print(f"         Error: {log['error_message']}")
                else:
                    print(f"   ⚠️ No webhook activity found since {target_time.strftime('%H:%M:%S')} UTC")
                    
                    # Show most recent activity for context
                    if logs_data.get('logs'):
                        latest_log = logs_data['logs'][0]
                        latest_time = datetime.fromisoformat(latest_log['created_at'].replace('Z', '+00:00'))
                        print(f"   📝 Most recent webhook: {latest_log.get('event_type', 'unknown')} at {latest_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                
            else:
                print(f"   ❌ Failed to fetch webhook logs: {logs_response.status_code}")
                if logs_response.text:
                    print(f"   📄 Response: {logs_response.text[:200]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        
        # 2. Check Updated Stats - GET /api/webhook/samcart/stats
        print("\n2️⃣ CHECKING WEBHOOK STATISTICS...")
        stats_url = f"{backend_url}/api/webhook/samcart/stats"
        
        try:
            stats_response = requests.get(stats_url, timeout=10)
            print(f"   📡 GET {stats_url}")
            print(f"   📊 Status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                results["webhook_stats_check"] = True
                stats_data = stats_response.json()
                
                print(f"   📈 Webhook Statistics:")
                print(f"      • Total webhooks: {stats_data.get('total_webhooks', 0)}")
                print(f"      • Successful: {stats_data.get('successful_webhooks', 0)}")
                print(f"      • Failed: {stats_data.get('failed_webhooks', 0)}")
                print(f"      • Success rate: {stats_data.get('success_rate', 0):.1f}%")
                print(f"      • Recent practice signups (30 days): {stats_data.get('recent_practice_signups', 0)}")
                
                # Check if webhook count has increased (indicating recent activity)
                total_webhooks = stats_data.get('total_webhooks', 0)
                if total_webhooks > 0:
                    print(f"   ✅ Webhook system is active with {total_webhooks} total processed webhooks")
                    results["connection_verified"] = True
                else:
                    print(f"   ⚠️ No webhooks have been processed yet")
                
            else:
                print(f"   ❌ Failed to fetch webhook stats: {stats_response.status_code}")
                if stats_response.text:
                    print(f"   📄 Response: {stats_response.text[:200]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        
        # 3. Verify Connection Status
        print("\n3️⃣ VERIFYING WEBHOOK CONNECTION...")
        
        # Test webhook endpoint accessibility
        webhook_url = f"{backend_url}/api/webhook/samcart"
        try:
            # Try a HEAD request to check if endpoint is accessible
            head_response = requests.head(webhook_url, timeout=5)
            print(f"   📡 HEAD {webhook_url}")
            print(f"   📊 Status: {head_response.status_code}")
            
            if head_response.status_code in [200, 405]:  # 405 is expected for HEAD on POST endpoint
                print(f"   ✅ Webhook endpoint is accessible")
                results["connection_verified"] = True
            else:
                print(f"   ⚠️ Webhook endpoint returned: {head_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Webhook endpoint test failed: {e}")
        
        # 4. Summary and Recommendations
        print("\n" + "="*80)
        print("📋 VERIFICATION SUMMARY")
        print("="*80)
        
        if results["recent_activity_found"]:
            print("✅ RECENT WEBHOOK ACTIVITY DETECTED")
            print("   SamCart sent webhook(s) since 5:55 PM today - integration is working!")
        elif results["webhook_logs_check"] and results["webhook_stats_check"]:
            print("⚠️ NO RECENT ACTIVITY BUT SYSTEM OPERATIONAL")
            print("   Webhook endpoints are working but no activity since 5:55 PM today")
            print("   This could mean:")
            print("   • No payments were processed since connection")
            print("   • SamCart hasn't sent test webhooks yet")
            print("   • User needs to make a test purchase")
        else:
            print("❌ WEBHOOK SYSTEM ISSUES DETECTED")
            print("   Unable to verify webhook functionality")
        
        if results["connection_verified"]:
            print("\n✅ CONNECTION STATUS: VERIFIED")
            print("   Webhook URL is properly configured and accessible")
        else:
            print("\n⚠️ CONNECTION STATUS: NEEDS VERIFICATION")
            print("   Webhook endpoint may not be properly configured")
        
        print("\n🔧 NEXT STEPS:")
        if results["recent_activity_found"]:
            print("   • Integration is working - ready for real payment testing")
            print("   • Monitor webhook logs for any payment attempts")
        else:
            print("   • Verify SamCart webhook URL: https://aftercareportal.preview.emergentagent.com/api/webhook/samcart")
            print("   • Check SamCart dashboard webhook configuration")
            print("   • Test with a real payment attempt")
            print("   • Verify webhook is enabled for ProductPurchased events")
        
        return results
        
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return results

if __name__ == "__main__":
    test_results = test_samcart_webhook_verification()
    
    # Exit with appropriate code
    if test_results["recent_activity_found"] or (test_results["webhook_logs_check"] and test_results["webhook_stats_check"]):
        exit(0)  # Success
    else:
        exit(1)  # Issues detected