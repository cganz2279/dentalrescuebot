#!/usr/bin/env python3

"""
ADMIN CUSTOMER INVESTIGATION - Check SamCart customers and accounts
"""

import requests
import json
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_admin_token():
    """Get admin token"""
    login_url = f"{BACKEND_URL}/api/admin/login"
    admin_credentials = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        response = requests.post(login_url, json=admin_credentials, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
    except Exception as e:
        log_test(f"❌ Admin login error: {e}")
    return None

def investigate_samcart_customers():
    """Investigate SamCart customers and webhook data"""
    log_test("🔍 INVESTIGATING SAMCART CUSTOMERS")
    
    admin_token = get_admin_token()
    if not admin_token:
        log_test("❌ Could not get admin token")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Check SamCart webhook logs
    webhook_logs_url = f"{BACKEND_URL}/api/webhook/samcart/logs"
    try:
        response = requests.get(webhook_logs_url, timeout=30)
        if response.status_code == 200:
            logs = response.json()
            log_test(f"📊 SamCart Webhook Logs: {len(logs)} entries found")
            
            # Show recent webhook activity
            for i, log_entry in enumerate(logs[:5]):
                log_test(f"  {i+1}. {log_entry.get('event_type', 'Unknown')} - {log_entry.get('customer_email', 'No email')} - {log_entry.get('status', 'Unknown status')}")
        else:
            log_test(f"❌ Could not get webhook logs: {response.status_code}")
    except Exception as e:
        log_test(f"❌ Webhook logs error: {e}")
    
    # Check SamCart webhook stats
    webhook_stats_url = f"{BACKEND_URL}/api/webhook/samcart/stats"
    try:
        response = requests.get(webhook_stats_url, timeout=30)
        if response.status_code == 200:
            stats = response.json()
            log_test(f"📈 SamCart Stats:")
            log_test(f"  - Total Webhooks: {stats.get('total_webhooks', 'N/A')}")
            log_test(f"  - Successful: {stats.get('successful_webhooks', 'N/A')}")
            log_test(f"  - Failed: {stats.get('failed_webhooks', 'N/A')}")
            log_test(f"  - Success Rate: {stats.get('success_rate', 'N/A')}%")
            log_test(f"  - Recent Signups: {stats.get('recent_practice_signups', 'N/A')}")
        else:
            log_test(f"❌ Could not get webhook stats: {response.status_code}")
    except Exception as e:
        log_test(f"❌ Webhook stats error: {e}")
    
    # Check all practices with detailed info
    practices_url = f"{BACKEND_URL}/api/admin/practices"
    try:
        response = requests.get(practices_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            practices = data.get('practices', [])
            
            log_test(f"🏥 DETAILED PRACTICE ANALYSIS: {len(practices)} practices")
            
            # Categorize practices
            samcart_practices = []
            regular_practices = []
            real_customer_practices = []
            
            for practice in practices:
                email = practice.get('email', '')
                name = practice.get('name', '')
                source = practice.get('source', 'unknown')
                
                if 'example.com' in email or 'test' in email.lower():
                    # Test practice
                    if source == 'samcart':
                        samcart_practices.append(practice)
                    else:
                        regular_practices.append(practice)
                else:
                    # Potential real customer
                    real_customer_practices.append(practice)
            
            log_test(f"📊 Practice Categories:")
            log_test(f"  - SamCart Test Practices: {len(samcart_practices)}")
            log_test(f"  - Regular Test Practices: {len(regular_practices)}")
            log_test(f"  - Real Customer Practices: {len(real_customer_practices)}")
            
            # Show real customer practices
            if real_customer_practices:
                log_test(f"\n🎯 REAL CUSTOMER PRACTICES:")
                for i, practice in enumerate(real_customer_practices):
                    log_test(f"  {i+1}. {practice.get('name', 'Unknown')} - {practice.get('email', 'No email')}")
                    log_test(f"     Status: {practice.get('subscription', {}).get('status', 'Unknown')}")
                    log_test(f"     Source: {practice.get('source', 'Unknown')}")
                    log_test(f"     Created: {practice.get('createdAt', 'Unknown')}")
            else:
                log_test(f"\n⚠️ NO REAL CUSTOMER PRACTICES FOUND")
                log_test(f"   All practices appear to be test accounts")
            
            # Show some SamCart practices
            if samcart_practices:
                log_test(f"\n🛒 SAMCART PRACTICES (showing first 3):")
                for i, practice in enumerate(samcart_practices[:3]):
                    log_test(f"  {i+1}. {practice.get('name', 'Unknown')} - {practice.get('email', 'No email')}")
                    log_test(f"     Status: {practice.get('subscription', {}).get('status', 'Unknown')}")
        else:
            log_test(f"❌ Could not get practices: {response.status_code}")
    except Exception as e:
        log_test(f"❌ Practices error: {e}")

def check_specific_customer_accounts():
    """Check for specific customer accounts mentioned in the context"""
    log_test("🔍 CHECKING SPECIFIC CUSTOMER ACCOUNTS")
    
    admin_token = get_admin_token()
    if not admin_token:
        log_test("❌ Could not get admin token")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Known customer emails from the context
    customer_emails = [
        "cganz2279@gmail.com",
        "caryganz@gmail.com", 
        "caryganzconsulting@gmail.com"
    ]
    
    practices_url = f"{BACKEND_URL}/api/admin/practices"
    try:
        response = requests.get(practices_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            practices = data.get('practices', [])
            
            log_test(f"🎯 SEARCHING FOR SPECIFIC CUSTOMERS:")
            
            found_customers = []
            for email in customer_emails:
                for practice in practices:
                    if practice.get('email', '').lower() == email.lower():
                        found_customers.append((email, practice))
                        break
            
            if found_customers:
                log_test(f"✅ FOUND {len(found_customers)} CUSTOMER ACCOUNTS:")
                for email, practice in found_customers:
                    log_test(f"  📧 {email}")
                    log_test(f"     Practice: {practice.get('name', 'Unknown')}")
                    log_test(f"     Status: {practice.get('subscription', {}).get('status', 'Unknown')}")
                    log_test(f"     ID: {practice.get('id', 'No ID')}")
                    log_test(f"     Source: {practice.get('source', 'Unknown')}")
            else:
                log_test(f"❌ NO SPECIFIC CUSTOMER ACCOUNTS FOUND")
                log_test(f"   Searched for: {', '.join(customer_emails)}")
        else:
            log_test(f"❌ Could not get practices: {response.status_code}")
    except Exception as e:
        log_test(f"❌ Customer search error: {e}")

if __name__ == "__main__":
    log_test("🚀 STARTING ADMIN CUSTOMER INVESTIGATION")
    log_test("=" * 80)
    
    investigate_samcart_customers()
    log_test("\n" + "=" * 80)
    check_specific_customer_accounts()
    
    log_test("\n" + "=" * 80)
    log_test("🎯 INVESTIGATION COMPLETE")