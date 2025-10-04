#!/usr/bin/env python3
"""
Detailed webhook analysis to understand the timing and content of webhook logs
"""

import requests
import json
from datetime import datetime, timedelta
import sys

BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

def analyze_webhook_logs():
    """Get detailed webhook log analysis"""
    print("🔍 DETAILED WEBHOOK LOG ANALYSIS")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/logs")
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Retrieved {len(logs)} webhook logs")
            
            if logs:
                print("\n📋 ALL WEBHOOK LOGS (most recent first):")
                
                # Sort by timestamp (most recent first)
                try:
                    logs_sorted = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
                except:
                    logs_sorted = logs
                
                for i, log in enumerate(logs_sorted, 1):
                    print(f"\n--- WEBHOOK LOG #{i} ---")
                    print(f"Timestamp: {log.get('timestamp', 'N/A')}")
                    print(f"Event Type: {log.get('event_type', 'N/A')}")
                    print(f"Status: {log.get('status', 'N/A')}")
                    print(f"Customer Email: {log.get('customer_email', 'N/A')}")
                    print(f"Webhook ID: {log.get('webhook_id', 'N/A')}")
                    
                    # Parse timestamp to check how recent it is
                    try:
                        timestamp_str = log.get('timestamp', '')
                        if timestamp_str:
                            # Handle different timestamp formats
                            if timestamp_str.endswith('Z'):
                                log_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            else:
                                log_time = datetime.fromisoformat(timestamp_str)
                            
                            now = datetime.utcnow()
                            time_diff = now - log_time.replace(tzinfo=None)
                            
                            if time_diff.total_seconds() < 900:  # 15 minutes
                                print(f"⏰ Time ago: {int(time_diff.total_seconds()/60)} minutes ago (RECENT!)")
                            elif time_diff.total_seconds() < 3600:  # 1 hour
                                print(f"⏰ Time ago: {int(time_diff.total_seconds()/60)} minutes ago")
                            else:
                                print(f"⏰ Time ago: {int(time_diff.total_seconds()/3600)} hours ago")
                    except Exception as e:
                        print(f"⏰ Time parsing error: {e}")
                
                # Check for any webhooks in the last 30 minutes
                print(f"\n🕐 RECENT ACTIVITY CHECK (last 30 minutes):")
                now = datetime.utcnow()
                recent_cutoff = now - timedelta(minutes=30)
                recent_count = 0
                
                for log in logs:
                    try:
                        timestamp_str = log.get('timestamp', '')
                        if timestamp_str:
                            if timestamp_str.endswith('Z'):
                                log_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            else:
                                log_time = datetime.fromisoformat(timestamp_str)
                            
                            if log_time.replace(tzinfo=None) > recent_cutoff:
                                recent_count += 1
                    except:
                        continue
                
                if recent_count > 0:
                    print(f"✅ Found {recent_count} webhooks in last 30 minutes")
                else:
                    print("❌ NO webhooks found in last 30 minutes")
                    print("   This confirms the real payment did NOT trigger a webhook")
                
            else:
                print("❌ No webhook logs found")
                
        else:
            print(f"❌ Failed to get webhook logs: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error analyzing webhook logs: {e}")

def check_webhook_endpoint_accessibility():
    """Check if the webhook endpoint is accessible"""
    print(f"\n🌐 WEBHOOK ENDPOINT ACCESSIBILITY CHECK")
    print("="*60)
    
    webhook_url = f"{BACKEND_URL}/api/webhook/samcart"
    
    try:
        # Try to access the webhook endpoint (this should return method not allowed for GET)
        response = requests.get(webhook_url)
        print(f"📡 GET {webhook_url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 405:  # Method Not Allowed is expected for GET on POST endpoint
            print("✅ Webhook endpoint is accessible (405 Method Not Allowed is expected for GET)")
        elif response.status_code == 200:
            print("✅ Webhook endpoint is accessible")
        else:
            print(f"⚠️  Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking webhook endpoint: {e}")

def main():
    print("🚨 DETAILED WEBHOOK INVESTIGATION")
    print(f"Current time: {datetime.utcnow().isoformat()}Z")
    print(f"Backend URL: {BACKEND_URL}")
    
    analyze_webhook_logs()
    check_webhook_endpoint_accessibility()
    
    print(f"\n🎯 CRITICAL CONCLUSION:")
    print("If no recent webhook activity is found, this confirms:")
    print("1. ❌ SamCart did NOT send a webhook for the real payment")
    print("2. 🔧 Issue is at SamCart configuration level, not backend")
    print("3. 📋 Possible causes:")
    print("   - Webhook URL incorrect in SamCart dashboard")
    print("   - Webhook disabled for this product")
    print("   - Payment failed before completion")
    print("   - Network/firewall blocking webhook delivery")

if __name__ == "__main__":
    main()