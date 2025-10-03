#!/usr/bin/env python3
"""
URGENT: SamCart Payment Investigation - Real Payment Missing Email
Testing webhook logs, stats, and recent account creation for user's payment issue
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com"

def test_webhook_logs():
    """Check recent webhook logs for the last 10 minutes"""
    print("🔍 CHECKING RECENT WEBHOOK LOGS...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/logs")
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Webhook logs retrieved: {len(logs)} total logs")
            
            # Check for recent logs (last 10 minutes)
            now = datetime.utcnow()
            recent_logs = []
            
            for log in logs:
                if 'timestamp' in log:
                    # Parse timestamp
                    log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                    if isinstance(log_time, datetime):
                        log_time = log_time.replace(tzinfo=None)
                    
                    time_diff = now - log_time
                    if time_diff.total_seconds() <= 600:  # 10 minutes
                        recent_logs.append(log)
                        print(f"🕐 RECENT LOG: {log_time} - {log.get('event_type', 'Unknown')} - {log.get('status', 'Unknown')}")
                        if 'customer_email' in log:
                            print(f"   📧 Customer Email: {log['customer_email']}")
            
            if not recent_logs:
                print("❌ NO RECENT WEBHOOK LOGS FOUND in last 10 minutes")
                print("🔍 Most recent webhook logs:")
                # Show last 3 logs safely
                recent_logs_to_show = logs[-3:] if len(logs) >= 3 else logs
                for log in recent_logs_to_show:
                    timestamp = log.get('timestamp', 'Unknown time')
                    event_type = log.get('event_type', 'Unknown event')
                    status = log.get('status', 'Unknown status')
                    email = log.get('customer_email', 'No email')
                    print(f"   📝 {timestamp} - {event_type} - {status} - {email}")
                    
                # Show all logs with timestamps for debugging
                print(f"🔍 All webhook logs ({len(logs)} total):")
                for i, log in enumerate(logs):
                    timestamp = log.get('timestamp', 'Unknown time')
                    event_type = log.get('event_type', 'Unknown event')
                    status = log.get('status', 'Unknown status')
                    email = log.get('customer_email', 'No email')
                    print(f"   {i+1}. {timestamp} - {event_type} - {status} - {email}")
            
            return recent_logs
        else:
            print(f"❌ Failed to get webhook logs: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error checking webhook logs: {str(e)}")
        return []

def test_webhook_stats():
    """Check webhook statistics"""
    print("\n📊 CHECKING WEBHOOK STATISTICS...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Webhook stats retrieved:")
            print(f"   📈 Total webhooks: {stats.get('total_webhooks', 0)}")
            print(f"   ✅ Successful: {stats.get('successful_webhooks', 0)}")
            print(f"   ❌ Failed: {stats.get('failed_webhooks', 0)}")
            print(f"   📊 Success rate: {stats.get('success_rate', 0)}%")
            print(f"   🆕 Recent signups (30 days): {stats.get('recent_practice_signups', 0)}")
            return stats
        else:
            print(f"❌ Failed to get webhook stats: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Error checking webhook stats: {str(e)}")
        return {}

def test_recent_practice_accounts():
    """Check for recent practice accounts created (requires admin access)"""
    print("\n👥 CHECKING RECENT PRACTICE ACCOUNTS...")
    
    # First try to login as admin
    admin_credentials = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        # Admin login
        login_response = requests.post(f"{BACKEND_URL}/api/admin/login", json=admin_credentials)
        if login_response.status_code == 200:
            admin_token = login_response.json().get('token')
            print("✅ Admin login successful")
            
            # Get recent practices (this would require an admin endpoint to list practices)
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Try to get practice list (if endpoint exists)
            try:
                practices_response = requests.get(f"{BACKEND_URL}/api/admin/practices", headers=headers)
                if practices_response.status_code == 200:
                    practices = practices_response.json()
                    print(f"✅ Found {len(practices)} total practices")
                    
                    # Check for recent practices (last 10 minutes)
                    now = datetime.utcnow()
                    recent_practices = []
                    
                    for practice in practices:
                        if 'created_at' in practice or 'createdAt' in practice:
                            created_field = practice.get('created_at') or practice.get('createdAt')
                            try:
                                created_time = datetime.fromisoformat(created_field.replace('Z', '+00:00'))
                                if isinstance(created_time, datetime):
                                    created_time = created_time.replace(tzinfo=None)
                                
                                time_diff = now - created_time
                                if time_diff.total_seconds() <= 600:  # 10 minutes
                                    recent_practices.append(practice)
                                    print(f"🆕 RECENT PRACTICE: {practice.get('practice_name', 'Unknown')} - {practice.get('admin_email', 'No email')} - {created_time}")
                            except:
                                pass
                    
                    if not recent_practices:
                        print("❌ NO RECENT PRACTICE ACCOUNTS FOUND in last 10 minutes")
                    
                    return recent_practices
                else:
                    print(f"❌ Could not retrieve practices list: {practices_response.status_code}")
                    return []
            except Exception as e:
                print(f"❌ Error retrieving practices: {str(e)}")
                return []
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error with admin access: {str(e)}")
        return []

def test_email_service_status():
    """Test email service functionality"""
    print("\n📧 TESTING EMAIL SERVICE STATUS...")
    
    # Test with existing practice account
    practice_credentials = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        # Practice login
        login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=practice_credentials)
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print("✅ Practice login successful")
            
            # Test email functionality by trying to send a test PDF email
            headers = {"Authorization": f"Bearer {token}"}
            
            email_test_payload = {
                "procedureId": "root-canal-therapy",
                "patientName": "Test Patient",
                "patientEmail": "test@example.com",
                "customInstructions": "Email service test"
            }
            
            try:
                email_response = requests.post(f"{BACKEND_URL}/api/practice/email-pdf", 
                                             json=email_test_payload, headers=headers)
                if email_response.status_code == 200:
                    print("✅ Email service is operational - test email sent successfully")
                    return True
                else:
                    print(f"⚠️ Email service test failed: {email_response.status_code}")
                    print(f"Response: {email_response.text}")
                    return False
            except Exception as e:
                print(f"❌ Error testing email service: {str(e)}")
                return False
        else:
            print(f"❌ Practice login failed: {login_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing email service: {str(e)}")
        return False

def test_webhook_endpoint_accessibility():
    """Test if webhook endpoint is accessible"""
    print("\n🔗 TESTING WEBHOOK ENDPOINT ACCESSIBILITY...")
    try:
        # Test GET request (should return 405 Method Not Allowed)
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart")
        if response.status_code == 405:
            print("✅ Webhook endpoint is accessible (returns 405 for GET as expected)")
            return True
        else:
            print(f"⚠️ Unexpected response from webhook endpoint: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing webhook endpoint: {str(e)}")
        return False

def main():
    print("🚨 URGENT: SAMCART PAYMENT INVESTIGATION")
    print("=" * 60)
    print("Investigating missing welcome email for real payment")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Investigation time: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # Run all tests
    recent_logs = test_webhook_logs()
    stats = test_webhook_stats()
    recent_practices = test_recent_practice_accounts()
    email_status = test_email_service_status()
    webhook_accessible = test_webhook_endpoint_accessibility()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if not recent_logs:
        print("❌ CRITICAL: NO webhook received for recent payment")
        print("   This indicates SamCart did NOT send webhook for the real payment")
    else:
        print(f"✅ Found {len(recent_logs)} recent webhook(s)")
    
    if stats:
        print(f"📊 Total webhooks processed: {stats.get('total_webhooks', 0)}")
        print(f"📊 Success rate: {stats.get('success_rate', 0)}%")
    
    if not recent_practices:
        print("❌ NO recent practice accounts created")
    else:
        print(f"✅ Found {len(recent_practices)} recent practice account(s)")
    
    if email_status:
        print("✅ Email service is operational")
    else:
        print("❌ Email service has issues")
    
    if webhook_accessible:
        print("✅ Webhook endpoint is accessible")
    else:
        print("❌ Webhook endpoint accessibility issues")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    if not recent_logs:
        print("1. ⚠️ Check SamCart webhook configuration")
        print("2. ⚠️ Verify webhook URL in SamCart dashboard")
        print("3. ⚠️ Test webhook delivery from SamCart admin panel")
        print("4. ⚠️ Manually create account for paying customer")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()