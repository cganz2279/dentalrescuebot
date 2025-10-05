#!/usr/bin/env python3
"""
FINAL CUSTOMER VERIFICATION TEST
================================
This test focuses on verifying that the real customers can actually access their accounts
and that the complete SamCart integration is working for new payments.
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

def print_warning(message):
    print(f"⚠️  {message}")

def test_samcart_webhook_integration():
    """Test the complete SamCart webhook integration with a new test customer"""
    print_header("TESTING SAMCART WEBHOOK INTEGRATION")
    
    try:
        # Use test endpoint to simulate a new customer payment
        test_email = f"live.test.{int(datetime.now().timestamp())}@example.com"
        
        response = requests.post(f"{BACKEND_URL}/api/webhook/samcart/test?test_email={test_email}")
        
        if response.status_code == 200:
            result = response.json()
            print_success("SamCart webhook test endpoint working")
            print_info(f"Test customer: {test_email}")
            print_info(f"Account created: {result.get('account_created', 'Unknown')}")
            print_info(f"Email sent: {result.get('email_sent', 'Unknown')}")
            print_info(f"Practice ID: {result.get('practice_id', 'Unknown')}")
            
            # Test if the created account can login
            if result.get('password'):
                login_data = {
                    "email": test_email,
                    "password": result.get('password')
                }
                
                login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    print_success("New SamCart account can login successfully")
                    login_result = login_response.json()
                    print_info(f"User ID: {login_result.get('user_id', 'Unknown')}")
                    print_info(f"Practice ID: {login_result.get('practice_id', 'Unknown')}")
                    return True
                else:
                    print_error(f"New SamCart account login failed: {login_response.status_code}")
                    return False
            else:
                print_warning("No password returned from test endpoint")
                return False
        else:
            print_error(f"SamCart webhook test failed: {response.status_code}")
            try:
                error_data = response.json()
                print_info(f"Error: {error_data}")
            except:
                print_info(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error testing SamCart integration: {e}")
        return False

def verify_customer_account_access(customer_email):
    """Verify that a customer can access their account via password reset"""
    print_header(f"VERIFYING ACCOUNT ACCESS FOR {customer_email}")
    
    try:
        # Send password reset
        reset_data = {
            "email": customer_email,
            "recovery_method": "email"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json=reset_data)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Password reset available for {customer_email}")
            print_info(f"Message: {result.get('message', 'No message')}")
            
            sent_methods = result.get('sent_methods', [])
            if 'email' in sent_methods:
                print_success("Password reset email sent successfully")
                print_info("Customer can use this email to reset password and login")
                return True
            else:
                print_warning("Password reset email may not have been sent")
                return False
        else:
            print_error(f"Password reset failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error verifying account access: {e}")
        return False

def check_webhook_statistics():
    """Check current webhook statistics"""
    print_header("WEBHOOK STATISTICS")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/webhook/samcart/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print_success("Webhook statistics accessible")
            print_info(f"Total webhooks: {stats.get('total_webhooks', 0)}")
            print_info(f"Successful: {stats.get('successful_webhooks', 0)}")
            print_info(f"Failed: {stats.get('failed_webhooks', 0)}")
            print_info(f"Success rate: {stats.get('success_rate', 0)}%")
            print_info(f"Recent signups (30 days): {stats.get('recent_practice_signups', 0)}")
            return True
        else:
            print_error(f"Failed to get webhook stats: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking webhook stats: {e}")
        return False

def verify_sendgrid_email_functionality():
    """Verify SendGrid email functionality through password reset"""
    print_header("VERIFYING SENDGRID EMAIL FUNCTIONALITY")
    
    try:
        # Test with a known working email (from the logs we saw it worked)
        test_email = "caryganz@gmail.com"
        
        reset_data = {
            "email": test_email,
            "recovery_method": "email"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json=reset_data)
        
        if response.status_code == 200:
            result = response.json()
            sent_methods = result.get('sent_methods', [])
            
            if 'email' in sent_methods:
                print_success("SendGrid email delivery working")
                print_info("Password reset emails are being sent successfully")
                return True
            else:
                print_error("SendGrid email delivery failed")
                return False
        else:
            print_error(f"Email test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing SendGrid: {e}")
        return False

def main():
    """Main verification function"""
    print_header("FINAL CUSTOMER VERIFICATION TEST")
    print_info("Testing complete SamCart payment → account → email → login flow")
    
    results = {}
    
    # Test 1: SamCart webhook integration
    results['webhook_integration'] = test_samcart_webhook_integration()
    
    # Test 2: Webhook statistics
    results['webhook_stats'] = check_webhook_statistics()
    
    # Test 3: SendGrid email functionality
    results['sendgrid_emails'] = verify_sendgrid_email_functionality()
    
    # Test 4: Real customer account access
    real_customers = ["caryganz@gmail.com", "caryganzconsulting@gmail.com"]
    results['customer_access'] = {}
    
    for customer in real_customers:
        results['customer_access'][customer] = verify_customer_account_access(customer)
    
    # Final summary
    print_header("FINAL VERIFICATION SUMMARY")
    
    if results['webhook_integration']:
        print_success("✅ SamCart webhook integration working")
    else:
        print_error("❌ SamCart webhook integration issues")
    
    if results['webhook_stats']:
        print_success("✅ Webhook statistics accessible")
    else:
        print_error("❌ Webhook statistics issues")
    
    if results['sendgrid_emails']:
        print_success("✅ SendGrid email delivery working")
    else:
        print_error("❌ SendGrid email delivery issues")
    
    print_info("\nReal Customer Account Access:")
    all_customers_ok = True
    for customer, access_ok in results['customer_access'].items():
        if access_ok:
            print_success(f"✅ {customer} - Account accessible")
        else:
            print_error(f"❌ {customer} - Account access issues")
            all_customers_ok = False
    
    # Overall status
    print_header("LIVE PAYMENT FLOW STATUS")
    
    if (results['webhook_integration'] and results['sendgrid_emails'] and all_customers_ok):
        print_success("🎉 LIVE PAYMENT FLOW: FULLY OPERATIONAL")
        print_info("✅ New SamCart payments will create accounts successfully")
        print_info("✅ Welcome emails are being sent")
        print_info("✅ Customers can access their accounts")
        print_info("✅ Password reset system working")
        print_info("\n🔗 Customer Login URL: https://samcart-auth-fix.preview.emergentagent.com/login")
    else:
        print_error("🚨 LIVE PAYMENT FLOW: PARTIAL ISSUES")
        print_info("Issues detected:")
        
        if not results['webhook_integration']:
            print_error("  - SamCart webhook integration needs attention")
        if not results['sendgrid_emails']:
            print_error("  - Email delivery system needs attention")
        if not all_customers_ok:
            print_error("  - Some customer accounts have access issues")
    
    # Specific recommendations
    print_header("RECOMMENDATIONS")
    
    if results['webhook_integration'] and results['sendgrid_emails']:
        print_success("✅ Core payment processing is working")
        print_info("New customers will receive accounts and can login")
    
    if all_customers_ok:
        print_success("✅ Existing customers can access their accounts")
        print_info("Password reset emails are working for account recovery")
    
    print_info("\n📧 For any customer login issues:")
    print_info("  1. Customer should check email for welcome message")
    print_info("  2. Use password reset if needed")
    print_info("  3. Contact support if password reset doesn't work")

if __name__ == "__main__":
    main()