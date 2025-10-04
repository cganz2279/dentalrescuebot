#!/usr/bin/env python3
"""
SamCart Webhook Status Testing
Testing current webhook activity and endpoint accessibility as requested by user
"""

import requests
import json
import os
from datetime import datetime, timezone
import sys

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentalpractice-hub-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def print_header(title):
    """Print formatted test section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def test_webhook_endpoint_accessibility():
    """Test if the SamCart webhook endpoint is accessible"""
    print_header("WEBHOOK ENDPOINT ACCESSIBILITY TEST")
    
    try:
        # Test GET request to webhook endpoint (should return 405 Method Not Allowed)
        response = requests.get(f"{API_BASE}/webhook/samcart", timeout=10)
        
        if response.status_code == 405:
            print_result("Webhook endpoint accessible", True, 
                        f"Returns 405 Method Not Allowed as expected for GET request")
            return True
        else:
            print_result("Webhook endpoint accessibility", False, 
                        f"Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result("Webhook endpoint accessibility", False, f"Connection error: {e}")
        return False

def test_webhook_logs():
    """Check current webhook logs"""
    print_header("CURRENT WEBHOOK LOGS")
    
    try:
        response = requests.get(f"{API_BASE}/webhook/samcart/logs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            count = data.get('count', 0)
            
            print_result("Webhook logs endpoint", True, f"Retrieved {count} log entries")
            
            if count > 0:
                print(f"\n📋 Recent Webhook Activity:")
                for i, log in enumerate(logs[:5]):  # Show first 5 logs
                    created_at = log.get('created_at', 'Unknown')
                    event_type = log.get('event_type', 'Unknown')
                    status = log.get('processing_status', 'Unknown')
                    webhook_id = log.get('webhook_id', 'Unknown')[:8]
                    
                    print(f"   {i+1}. {created_at} | {event_type} | {status} | ID: {webhook_id}...")
                    
                    # Show customer email if available
                    payload = log.get('payload', {})
                    customer = payload.get('customer', {})
                    if customer.get('email'):
                        print(f"      Customer: {customer.get('email')}")
                
                if count > 5:
                    print(f"   ... and {count - 5} more entries")
            else:
                print(f"\n📋 No webhook activity found")
                
            return True, logs
            
        else:
            print_result("Webhook logs endpoint", False, 
                        f"HTTP {response.status_code}: {response.text}")
            return False, []
            
    except requests.exceptions.RequestException as e:
        print_result("Webhook logs endpoint", False, f"Connection error: {e}")
        return False, []

def test_webhook_stats():
    """Check webhook statistics"""
    print_header("WEBHOOK STATISTICS")
    
    try:
        response = requests.get(f"{API_BASE}/webhook/samcart/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            
            print_result("Webhook stats endpoint", True, "Statistics retrieved successfully")
            
            print(f"\n📊 Webhook Statistics:")
            print(f"   Total Webhooks: {stats.get('total_webhooks', 0)}")
            print(f"   Successful: {stats.get('successful_webhooks', 0)}")
            print(f"   Failed: {stats.get('failed_webhooks', 0)}")
            print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
            print(f"   Recent Practice Signups (30 days): {stats.get('recent_practice_signups', 0)}")
            
            return True, stats
            
        else:
            print_result("Webhook stats endpoint", False, 
                        f"HTTP {response.status_code}: {response.text}")
            return False, {}
            
    except requests.exceptions.RequestException as e:
        print_result("Webhook stats endpoint", False, f"Connection error: {e}")
        return False, {}

def analyze_webhook_activity(logs, stats):
    """Analyze current webhook activity and provide insights"""
    print_header("WEBHOOK ACTIVITY ANALYSIS")
    
    total_webhooks = stats.get('total_webhooks', 0)
    recent_signups = stats.get('recent_practice_signups', 0)
    
    if total_webhooks == 0:
        print("🔍 BASELINE STATUS: No webhook activity detected")
        print("   This is the perfect baseline for testing new webhook activity")
        print("   Any new webhooks received will be clearly visible")
        return
    
    # Analyze recent activity
    now = datetime.now(timezone.utc)
    recent_logs = []
    
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log.get('created_at', '').replace('Z', '+00:00'))
            time_diff = (now - log_time).total_seconds() / 60  # minutes ago
            
            if time_diff <= 60:  # Within last hour
                recent_logs.append((log, time_diff))
        except:
            continue
    
    if recent_logs:
        print(f"🔥 RECENT ACTIVITY: {len(recent_logs)} webhooks in the last hour")
        for log, minutes_ago in recent_logs[:3]:
            event_type = log.get('event_type', 'Unknown')
            status = log.get('processing_status', 'Unknown')
            print(f"   {minutes_ago:.1f} min ago: {event_type} ({status})")
    else:
        print(f"📊 CURRENT STATUS: {total_webhooks} total webhooks, but none in the last hour")
        print("   Good baseline for monitoring new test purchase activity")
    
    # Check for test vs real data
    test_emails = 0
    real_emails = 0
    
    for log in logs[:10]:  # Check recent logs
        payload = log.get('payload', {})
        customer = payload.get('customer', {})
        email = customer.get('email', '').lower()
        
        if 'test' in email or 'example.com' in email:
            test_emails += 1
        elif email and '@' in email:
            real_emails += 1
    
    if test_emails > 0:
        print(f"🧪 TEST DATA: {test_emails} test webhooks found in recent activity")
    if real_emails > 0:
        print(f"💰 REAL DATA: {real_emails} real customer webhooks found in recent activity")

def main():
    """Main testing function"""
    print("🚀 SamCart Webhook Status Check")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Test webhook endpoint accessibility
    endpoint_accessible = test_webhook_endpoint_accessibility()
    
    # Get current webhook logs
    logs_success, logs = test_webhook_logs()
    
    # Get webhook statistics
    stats_success, stats = test_webhook_stats()
    
    # Analyze activity if we have data
    if logs_success and stats_success:
        analyze_webhook_activity(logs, stats)
    
    # Summary
    print_header("SUMMARY")
    
    if endpoint_accessible and logs_success and stats_success:
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("   Webhook endpoint is accessible")
        print("   Logs and statistics are available")
        print("   Ready to monitor for new webhook activity")
        
        total_webhooks = stats.get('total_webhooks', 0)
        if total_webhooks == 0:
            print("\n🎯 PERFECT TESTING BASELINE:")
            print("   No existing webhook activity detected")
            print("   Any new webhooks from test purchase will be clearly visible")
        else:
            print(f"\n📊 CURRENT BASELINE: {total_webhooks} existing webhooks")
            print("   Monitor for new activity after test purchase")
            
        print(f"\n🔗 Webhook URL: {BACKEND_URL}/api/webhook/samcart")
        print("   This is the URL that should be configured in SamCart")
        
    else:
        print("❌ ISSUES DETECTED")
        if not endpoint_accessible:
            print("   Webhook endpoint is not accessible")
        if not logs_success:
            print("   Cannot retrieve webhook logs")
        if not stats_success:
            print("   Cannot retrieve webhook statistics")
        print("   These issues need to be resolved before testing")
    
    return endpoint_accessible and logs_success and stats_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)