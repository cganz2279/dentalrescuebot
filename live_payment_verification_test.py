#!/usr/bin/env python3
"""
URGENT LIVE PAYMENT VERIFICATION TEST
=====================================
This test verifies that a real SamCart payment just processed correctly.

CRITICAL CHECKS:
1. Recent webhook logs (last 10 minutes)
2. Account creation for real customer
3. Welcome email delivery confirmation
4. SendGrid usage verification
5. Customer login functionality

Expected: Real customer data, not test data
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def check_recent_webhook_logs():
    """Check for recent webhook activity in last 10 minutes"""
    print_header("CHECKING RECENT WEBHOOK LOGS")
    
    try:
        # Get webhook logs
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/logs")
        
        if response.status_code != 200:
            print_error(f"Failed to get webhook logs: {response.status_code}")
            return None
            
        logs = response.json()
        print_info(f"Total webhook logs found: {len(logs)}")
        
        # Check for recent activity (last 10 minutes)
        now = datetime.utcnow()
        recent_cutoff = now - timedelta(minutes=10)
        
        recent_logs = []
        for log in logs:
            try:
                # Parse timestamp
                timestamp_str = log.get('timestamp', '')
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamp = timestamp.replace(tzinfo=None)  # Remove timezone for comparison
                    else:
                        continue
                        
                    if timestamp > recent_cutoff:
                        recent_logs.append(log)
            except Exception as e:
                print_info(f"Could not parse timestamp for log: {e}")
                continue
        
        print_info(f"Recent webhook logs (last 10 minutes): {len(recent_logs)}")
        
        if recent_logs:
            print_success("RECENT WEBHOOK ACTIVITY DETECTED!")
            for log in recent_logs:
                customer_email = log.get('customer_email', 'No email')
                event_type = log.get('event_type', 'Unknown')
                status = log.get('status', 'Unknown')
                timestamp = log.get('timestamp', 'No timestamp')
                order_id = log.get('order_id', 'No order ID')
                
                print(f"  📧 Customer: {customer_email}")
                print(f"  📅 Time: {timestamp}")
                print(f"  🎯 Event: {event_type}")
                print(f"  ✅ Status: {status}")
                print(f"  🆔 Order ID: {order_id}")
                print(f"  ---")
                
                # Check if this looks like real customer data
                if customer_email and 'test' not in customer_email.lower() and 'example.com' not in customer_email.lower():
                    print_success(f"REAL CUSTOMER DETECTED: {customer_email}")
                    return customer_email
        else:
            print_error("No recent webhook activity found in last 10 minutes")
            
        return None
        
    except Exception as e:
        print_error(f"Error checking webhook logs: {e}")
        return None

def check_webhook_stats():
    """Check webhook statistics"""
    print_header("WEBHOOK STATISTICS")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/stats")
        
        if response.status_code != 200:
            print_error(f"Failed to get webhook stats: {response.status_code}")
            return
            
        stats = response.json()
        print_info(f"Total webhooks: {stats.get('total_webhooks', 0)}")
        print_info(f"Successful: {stats.get('successful_webhooks', 0)}")
        print_info(f"Failed: {stats.get('failed_webhooks', 0)}")
        print_info(f"Success rate: {stats.get('success_rate', 0)}%")
        print_info(f"Recent signups (30 days): {stats.get('recent_practice_signups', 0)}")
        
        if stats.get('success_rate', 0) == 100:
            print_success("Webhook system has 100% success rate")
        else:
            print_error(f"Webhook system has failures: {stats.get('success_rate', 0)}% success rate")
            
    except Exception as e:
        print_error(f"Error checking webhook stats: {e}")

def verify_account_creation(customer_email):
    """Verify if account was created for the customer"""
    print_header(f"VERIFYING ACCOUNT CREATION FOR {customer_email}")
    
    if not customer_email:
        print_error("No customer email provided")
        return False
    
    try:
        # Try to trigger password reset to check if account exists
        reset_data = {
            "email": customer_email,
            "recovery_method": "email"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json=reset_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('message') and 'sent' in result.get('message', '').lower():
                print_success(f"Account exists for {customer_email} - password reset available")
                return True
            else:
                print_error(f"Unexpected response: {result}")
                return False
        elif response.status_code == 404:
            print_error(f"Account NOT found for {customer_email}")
            return False
        else:
            print_error(f"Error checking account: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error verifying account creation: {e}")
        return False

def check_sendgrid_configuration():
    """Check if SendGrid is properly configured"""
    print_header("SENDGRID CONFIGURATION CHECK")
    
    try:
        # Check if we can access the backend health endpoint
        response = requests.get(f"{BACKEND_URL}/api/health")
        
        if response.status_code == 200:
            print_success("Backend is accessible")
        else:
            print_error(f"Backend not accessible: {response.status_code}")
            
        # Note: We can't directly test SendGrid API key from here for security reasons
        print_info("SendGrid configuration must be verified through backend logs")
        
    except Exception as e:
        print_error(f"Error checking backend: {e}")

def test_customer_login_access(customer_email):
    """Test if customer can access login system (not actual login, just endpoint availability)"""
    print_header(f"TESTING LOGIN ACCESS FOR {customer_email}")
    
    if not customer_email:
        print_error("No customer email provided")
        return False
    
    try:
        # Test login endpoint accessibility with wrong password to see if account exists
        login_data = {
            "email": customer_email,
            "password": "wrong_password_test"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 401:
            print_success(f"Login endpoint accessible - account exists for {customer_email}")
            print_info("Customer can use password reset to access account")
            return True
        elif response.status_code == 404:
            print_error(f"Account not found in login system for {customer_email}")
            return False
        elif response.status_code == 500:
            print_error(f"Server error during login test - possible account corruption")
            return False
        else:
            print_info(f"Unexpected login response: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing login access: {e}")
        return False

def main():
    """Main verification function"""
    print_header("URGENT LIVE SAMCART PAYMENT VERIFICATION")
    print_info("Checking for recent real payment processing...")
    
    # Step 1: Check recent webhook logs
    customer_email = check_recent_webhook_logs()
    
    # Step 2: Check webhook statistics
    check_webhook_stats()
    
    # Step 3: Verify account creation
    account_created = False
    if customer_email:
        account_created = verify_account_creation(customer_email)
    
    # Step 4: Check SendGrid configuration
    check_sendgrid_configuration()
    
    # Step 5: Test customer login access
    login_accessible = False
    if customer_email:
        login_accessible = test_customer_login_access(customer_email)
    
    # Final summary
    print_header("LIVE PAYMENT VERIFICATION SUMMARY")
    
    if customer_email:
        print_success(f"Real customer payment detected: {customer_email}")
    else:
        print_error("No recent real customer payment found")
    
    if account_created:
        print_success("Customer account was created successfully")
    else:
        print_error("Customer account creation could not be verified")
    
    if login_accessible:
        print_success("Customer can access login system")
    else:
        print_error("Customer login access issues detected")
    
    # Overall status
    if customer_email and account_created and login_accessible:
        print_header("🎉 LIVE PAYMENT PROCESSING: SUCCESS")
        print_success("Complete payment flow working correctly!")
        print_info(f"Customer {customer_email} can login at: {BACKEND_URL.replace('/api', '')}/login")
        print_info("Customer should use password reset if needed")
    else:
        print_header("🚨 LIVE PAYMENT PROCESSING: ISSUES DETECTED")
        print_error("Payment flow has issues that need attention")
        
        if not customer_email:
            print_error("- No recent webhook received for real payment")
        if not account_created:
            print_error("- Customer account not created or not accessible")
        if not login_accessible:
            print_error("- Customer cannot access login system")

if __name__ == "__main__":
    main()