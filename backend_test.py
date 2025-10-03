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
            data = response.json()
            logs = data.get('logs', [])
            print(f"✅ Webhook logs retrieved: {len(logs)} total logs")
            
            # Check for recent logs (last 10 minutes)
            now = datetime.utcnow()
            recent_logs = []
            
            # Show all logs with timestamps for debugging
            print(f"🔍 All webhook logs ({len(logs)} total):")
            for i, log in enumerate(logs):
                timestamp = log.get('created_at', 'Unknown time')
                event_type = log.get('event_type', 'Unknown event')
                status = log.get('processing_status', 'Unknown status')
                
                # Extract customer email from payload
                email = 'No email'
                if 'payload' in log and 'customer' in log['payload']:
                    email = log['payload']['customer'].get('email', 'No email')
                
                print(f"   {i+1}. {timestamp} - {event_type} - {status} - {email}")
                
                # Check if this is a recent log
                if 'created_at' in log:
                    try:
                        log_time = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                        if hasattr(log_time, 'tzinfo') and log_time.tzinfo is not None:
                            log_time = log_time.replace(tzinfo=None)
                        
                        time_diff = now - log_time
                        if time_diff.total_seconds() <= 600:  # 10 minutes
                            recent_logs.append(log)
                            print(f"      🕐 RECENT LOG (within 10 minutes): {log_time}")
                            print(f"      📧 Customer: {email}")
                            print(f"      🎯 Event: {event_type}")
                            print(f"      ✅ Status: {status}")
                            
                            # Show more details about the payload
                            if 'payload' in log:
                                payload = log['payload']
                                if 'customer' in payload:
                                    customer = payload['customer']
                                    print(f"      👤 Customer Name: {customer.get('first_name', '')} {customer.get('last_name', '')}")
                                if 'order' in payload:
                                    order = payload['order']
                                    print(f"      💰 Order Total: ${order.get('total', '0.00')}")
                                    print(f"      🆔 Order ID: {order.get('id', 'Unknown')}")
                    except Exception as parse_error:
                        print(f"      ⚠️ Could not parse timestamp: {parse_error}")
            
            if not recent_logs:
                print("❌ NO RECENT WEBHOOK LOGS FOUND in last 10 minutes")
            else:
                print(f"✅ Found {len(recent_logs)} recent webhook(s)")
            
            return recent_logs
        else:
            print(f"❌ Failed to get webhook logs: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error checking webhook logs: {str(e)}")
        import traceback
        traceback.print_exc()
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

def test_recent_practice_accounts(recent_webhook_emails=None):
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
                    
                    # Also check for practices matching recent webhook emails
                    webhook_email_matches = []
                    
                    for practice in practices:
                        admin_email = practice.get('admin_email', '')
                        practice_name = practice.get('practice_name', 'Unknown')
                        
                        # Check if this practice matches a recent webhook email
                        if recent_webhook_emails and admin_email in recent_webhook_emails:
                            webhook_email_matches.append(practice)
                            print(f"🎯 WEBHOOK EMAIL MATCH: {practice_name} - {admin_email}")
                            if 'created_at' in practice or 'createdAt' in practice:
                                created_field = practice.get('created_at') or practice.get('createdAt')
                                print(f"   📅 Created: {created_field}")
                        
                        # Check for recent practices (last 10 minutes)
                        if 'created_at' in practice or 'createdAt' in practice:
                            created_field = practice.get('created_at') or practice.get('createdAt')
                            try:
                                created_time = datetime.fromisoformat(created_field.replace('Z', '+00:00'))
                                if isinstance(created_time, datetime):
                                    created_time = created_time.replace(tzinfo=None)
                                
                                time_diff = now - created_time
                                if time_diff.total_seconds() <= 600:  # 10 minutes
                                    recent_practices.append(practice)
                                    print(f"🆕 RECENT PRACTICE: {practice_name} - {admin_email} - {created_time}")
                            except:
                                pass
                    
                    if not recent_practices:
                        print("❌ NO RECENT PRACTICE ACCOUNTS FOUND in last 10 minutes")
                    
                    if not webhook_email_matches and recent_webhook_emails:
                        print(f"❌ NO PRACTICE ACCOUNTS FOUND for webhook emails: {recent_webhook_emails}")
                    
                    return recent_practices, webhook_email_matches
                else:
                    print(f"❌ Could not retrieve practices list: {practices_response.status_code}")
                    return [], []
            except Exception as e:
                print(f"❌ Error retrieving practices: {str(e)}")
                return [], []
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            return [], []
    except Exception as e:
        print(f"❌ Error with admin access: {str(e)}")
        return [], []

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
                "procedureName": "Root Canal Therapy",
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
    
    # Extract emails from recent webhooks
    recent_webhook_emails = []
    for log in recent_logs:
        if 'payload' in log and 'customer' in log['payload']:
            email = log['payload']['customer'].get('email')
            if email:
                recent_webhook_emails.append(email)
    
    recent_practices, webhook_email_matches = test_recent_practice_accounts(recent_webhook_emails)
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
    
    if webhook_email_matches:
        print(f"✅ Found {len(webhook_email_matches)} practice account(s) matching recent webhook emails")
    elif recent_webhook_emails:
        print(f"❌ NO practice accounts found for recent webhook emails: {recent_webhook_emails}")
    
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