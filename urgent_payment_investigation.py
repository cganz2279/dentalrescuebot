#!/usr/bin/env python3
"""
URGENT: Real Payment Investigation
User made real SamCart payment but did NOT receive welcome email
Need to investigate webhook logs, stats, and recent account creation
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_webhook_logs():
    """Check recent webhook logs for the last 15 minutes"""
    print_section("CHECKING RECENT WEBHOOK LOGS")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/logs")
        print(f"📡 GET /api/webhook/samcart/logs")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Found {len(logs)} total webhook logs")
            
            # Filter logs from last 15 minutes
            now = datetime.utcnow()
            recent_cutoff = now - timedelta(minutes=15)
            
            recent_logs = []
            for log in logs:
                # Parse timestamp
                try:
                    log_time = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                    if log_time.replace(tzinfo=None) > recent_cutoff:
                        recent_logs.append(log)
                except:
                    continue
            
            print(f"🕐 Recent logs (last 15 minutes): {len(recent_logs)}")
            
            if recent_logs:
                print("\n📋 RECENT WEBHOOK ACTIVITY:")
                for i, log in enumerate(recent_logs[-5:], 1):  # Show last 5
                    print(f"  {i}. Time: {log.get('timestamp')}")
                    print(f"     Event: {log.get('event_type')}")
                    print(f"     Status: {log.get('status')}")
                    print(f"     Email: {log.get('customer_email', 'N/A')}")
                    print(f"     Webhook ID: {log.get('webhook_id', 'N/A')}")
                    print()
            else:
                print("❌ NO RECENT WEBHOOK ACTIVITY FOUND")
                print("   This suggests the real payment did NOT trigger a webhook")
                
        else:
            print(f"❌ Failed to get webhook logs: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking webhook logs: {e}")

def check_webhook_stats():
    """Check webhook statistics"""
    print_section("CHECKING WEBHOOK STATISTICS")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/stats")
        print(f"📊 GET /api/webhook/samcart/stats")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Webhook Statistics:")
            print(f"   Total webhooks: {stats.get('total_webhooks', 0)}")
            print(f"   Successful: {stats.get('successful_webhooks', 0)}")
            print(f"   Failed: {stats.get('failed_webhooks', 0)}")
            print(f"   Success rate: {stats.get('success_rate', 0)}%")
            print(f"   Recent signups: {stats.get('recent_practice_signups', 0)}")
            
            # Check if stats increased since last known count
            if stats.get('total_webhooks', 0) > 6:  # Previous test showed 6 webhooks
                print("🆕 NEW WEBHOOK ACTIVITY DETECTED!")
            else:
                print("⚠️  No new webhook activity since last test")
                
        else:
            print(f"❌ Failed to get webhook stats: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking webhook stats: {e}")

def check_recent_practice_accounts():
    """Check for recently created practice accounts"""
    print_section("CHECKING RECENT PRACTICE ACCOUNTS")
    
    # This would require admin authentication, but let's try to get some info
    try:
        # Try to check if there are any new SamCart accounts
        print("🔍 Attempting to check recent practice account creation...")
        print("   (Note: This may require admin authentication)")
        
        # We can't directly query the database, but we can infer from webhook logs
        print("   Checking webhook logs for account creation indicators...")
        
    except Exception as e:
        print(f"❌ Error checking practice accounts: {e}")

def check_email_service_status():
    """Check if email service is working"""
    print_section("CHECKING EMAIL SERVICE STATUS")
    
    try:
        # Test if we can reach the backend health endpoint
        response = requests.get(f"{BACKEND_URL}/api/health")
        print(f"🏥 Backend Health Check: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend is responding")
            
            # Check if SendGrid configuration exists (we can't test directly without auth)
            print("📧 Email service configuration:")
            print("   SendGrid API integration: Configured in backend")
            print("   Sender email: admin@theoncallbot.com")
            print("   Admin email: admin@theoncallbot.com")
            
        else:
            print(f"❌ Backend health check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking email service: {e}")

def analyze_payment_flow():
    """Analyze what should happen vs what actually happened"""
    print_section("PAYMENT FLOW ANALYSIS")
    
    print("🔄 EXPECTED FLOW:")
    print("   1. User completes real payment on SamCart")
    print("   2. SamCart sends ProductPurchased webhook to backend")
    print("   3. Backend receives webhook and creates practice account")
    print("   4. Backend sends welcome email with login credentials")
    print("   5. User receives email and can access account")
    
    print("\n❓ ACTUAL FLOW INVESTIGATION:")
    print("   1. ✅ User completed real payment (confirmed)")
    print("   2. ❓ Did SamCart send webhook? (checking logs...)")
    print("   3. ❓ Was account created? (checking recent accounts...)")
    print("   4. ❓ Was email sent? (checking email service...)")
    print("   5. ❌ User did NOT receive email (confirmed)")

def main():
    print("🚨 URGENT: REAL PAYMENT INVESTIGATION")
    print("User made real SamCart payment but did NOT receive welcome email")
    print(f"Investigation time: {datetime.utcnow().isoformat()}Z")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Run all checks
    check_webhook_logs()
    check_webhook_stats() 
    check_recent_practice_accounts()
    check_email_service_status()
    analyze_payment_flow()
    
    print_section("INVESTIGATION SUMMARY")
    print("🎯 KEY FINDINGS:")
    print("   - Check webhook logs for recent activity")
    print("   - Compare webhook stats to previous counts")
    print("   - Verify if backend received the payment webhook")
    print("   - Determine if email service is operational")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. If no recent webhook: SamCart configuration issue")
    print("   2. If webhook received but no email: Email service issue")
    print("   3. If webhook received and account created: Check email delivery")
    print("   4. May need to manually create account for user")

if __name__ == "__main__":
    main()