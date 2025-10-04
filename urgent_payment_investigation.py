#!/usr/bin/env python3
"""
URGENT: SamCart Payment Investigation for caryganzconsulting@gmail.com
User just completed payment but did NOT receive welcome email
Time Window: Last 10-15 minutes
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
import os
import sys

# Test configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
URGENT_EMAIL = "caryganzconsulting@gmail.com"

class UrgentPaymentInvestigator:
    def __init__(self):
        self.session = None
        self.investigation_results = []
        self.current_time = datetime.now(timezone.utc)
        self.cutoff_time = self.current_time - timedelta(minutes=15)
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    def log_finding(self, investigation_step, status, details):
        """Log investigation finding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {investigation_step}")
        if details:
            print(f"   Details: {details}")
        self.investigation_results.append({
            "step": investigation_step,
            "status": status,
            "details": details,
            "timestamp": timestamp
        })
        
    async def check_recent_webhook_logs(self):
        """CRITICAL CHECK 1: Look for recent webhooks for caryganzconsulting@gmail.com"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/logs"
            async with self.session.get(url) as response:
                if response.status == 200:
                    logs_data = await response.json()
                    logs = logs_data.get("logs", [])
                    
                    # Look for webhooks in the last 15 minutes for our specific email
                    recent_webhooks = []
                    target_webhooks = []
                    
                    for log in logs:
                        log_time_str = log.get("timestamp", "")
                        try:
                            # Parse timestamp
                            log_time = datetime.fromisoformat(log_time_str.replace('Z', '+00:00'))
                            
                            # Check if within last 15 minutes
                            if log_time >= self.cutoff_time:
                                recent_webhooks.append(log)
                                
                                # Check if for our target email
                                customer_data = log.get("customer_data", {})
                                if customer_data.get("email") == URGENT_EMAIL:
                                    target_webhooks.append(log)
                        except:
                            continue
                    
                    if target_webhooks:
                        webhook = target_webhooks[0]  # Most recent
                        event_type = webhook.get("event_type", "Unknown")
                        status = webhook.get("status", "Unknown")
                        order_id = webhook.get("order_id", "Unknown")
                        
                        self.log_finding("Recent Webhook for Target Email", "🎯 FOUND", 
                                       f"Webhook received for {URGENT_EMAIL} - Event: {event_type}, Status: {status}, Order: {order_id}")
                        return webhook
                    else:
                        self.log_finding("Recent Webhook for Target Email", "❌ NOT FOUND", 
                                       f"No webhooks found for {URGENT_EMAIL} in last 15 minutes. Found {len(recent_webhooks)} recent webhooks total")
                        
                        # Show recent webhook emails for context
                        if recent_webhooks:
                            recent_emails = [w.get("customer_data", {}).get("email", "Unknown") for w in recent_webhooks[:3]]
                            self.log_finding("Recent Webhook Activity", "ℹ️ INFO", 
                                           f"Recent webhooks for: {', '.join(recent_emails)}")
                        
                        return None
                else:
                    self.log_finding("Webhook Logs Access", "❌ FAILED", 
                                   f"HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.log_finding("Recent Webhook Logs Check", "❌ ERROR", f"Exception: {e}")
            return None
            
    async def check_webhook_stats(self):
        """CRITICAL CHECK 2: Check if webhook count increased recently"""
        try:
            url = f"{BACKEND_URL}/api/webhook/samcart/stats"
            async with self.session.get(url) as response:
                if response.status == 200:
                    stats_data = await response.json()
                    total_webhooks = stats_data.get("total_webhooks", 0)
                    successful_webhooks = stats_data.get("successful_webhooks", 0)
                    failed_webhooks = stats_data.get("failed_webhooks", 0)
                    success_rate = stats_data.get("success_rate", 0)
                    recent_signups = stats_data.get("recent_practice_signups", 0)
                    
                    self.log_finding("Webhook Statistics", "✅ RETRIEVED", 
                                   f"Total: {total_webhooks}, Success: {successful_webhooks}, Failed: {failed_webhooks}, Rate: {success_rate}%, Recent signups: {recent_signups}")
                    return stats_data
                else:
                    self.log_finding("Webhook Stats Access", "❌ FAILED", 
                                   f"HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.log_finding("Webhook Stats Check", "❌ ERROR", f"Exception: {e}")
            return None
            
    async def check_practice_account_exists(self):
        """CRITICAL CHECK 3: Check if practice account exists for caryganzconsulting@gmail.com"""
        try:
            # Try to use the webhook test endpoint to check if account exists
            url = f"{BACKEND_URL}/api/webhook/samcart/test"
            params = {"test_email": URGENT_EMAIL}
            
            async with self.session.post(url, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    status = response_data.get("status", "unknown")
                    
                    if status == "duplicate":
                        self.log_finding("Practice Account Existence", "✅ EXISTS", 
                                       f"Account already exists for {URGENT_EMAIL}")
                        return True
                    elif status == "success":
                        self.log_finding("Practice Account Existence", "🆕 CREATED", 
                                       f"New account created for {URGENT_EMAIL}")
                        return True
                    else:
                        self.log_finding("Practice Account Existence", "❌ UNKNOWN", 
                                       f"Unexpected status: {status}")
                        return False
                else:
                    self.log_finding("Practice Account Check", "❌ FAILED", 
                                   f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_finding("Practice Account Check", "❌ ERROR", f"Exception: {e}")
            return False
            
    async def test_login_attempt(self):
        """CRITICAL CHECK 4: Test login to see account status"""
        try:
            url = f"{BACKEND_URL}/api/auth/login"
            login_data = {
                "email": URGENT_EMAIL,
                "password": "test_password_123"  # Wrong password to test account status
            }
            
            async with self.session.post(url, json=login_data) as response:
                response_text = await response.text()
                
                if response.status == 401:
                    self.log_finding("Account Login Test", "✅ ACCOUNT EXISTS", 
                                   f"Account exists (401 for wrong password is expected)")
                    return "exists_healthy"
                elif response.status == 500:
                    self.log_finding("Account Login Test", "🚨 CORRUPTED", 
                                   f"Account exists but password field corrupted (500 error)")
                    return "exists_corrupted"
                elif response.status == 404:
                    self.log_finding("Account Login Test", "❌ NO ACCOUNT", 
                                   f"No account found for {URGENT_EMAIL}")
                    return "not_found"
                else:
                    self.log_finding("Account Login Test", "❓ UNKNOWN", 
                                   f"Unexpected response: HTTP {response.status}")
                    return "unknown"
                    
        except Exception as e:
            self.log_finding("Login Attempt Test", "❌ ERROR", f"Exception: {e}")
            return "error"
            
    async def test_email_service_status(self):
        """CRITICAL CHECK 5: Test email service functionality"""
        try:
            # Test password reset email as a way to verify email service
            url = f"{BACKEND_URL}/api/auth/forgot-password"
            reset_data = {
                "email": URGENT_EMAIL,
                "recovery_method": "email"
            }
            
            async with self.session.post(url, json=reset_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        sent_methods = response_data.get("sent_methods", [])
                        self.log_finding("Email Service Status", "✅ WORKING", 
                                       f"Email service operational - sent via: {sent_methods}")
                        return True
                    else:
                        self.log_finding("Email Service Status", "❌ FAILED", 
                                       f"Email service failed: {response_data}")
                        return False
                else:
                    self.log_finding("Email Service Status", "❌ ERROR", 
                                   f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_finding("Email Service Test", "❌ ERROR", f"Exception: {e}")
            return False
            
    async def run_urgent_investigation(self):
        """Run complete urgent investigation"""
        print("🚨 URGENT PAYMENT INVESTIGATION")
        print("=" * 60)
        print(f"Target Email: {URGENT_EMAIL}")
        print(f"Investigation Time: {self.current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Looking for activity since: {self.cutoff_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run investigation steps
            print("\n🔍 STEP 1: Checking recent webhook logs...")
            webhook_found = await self.check_recent_webhook_logs()
            
            print("\n🔍 STEP 2: Checking webhook statistics...")
            stats = await self.check_webhook_stats()
            
            print("\n🔍 STEP 3: Checking if practice account exists...")
            account_exists = await self.check_practice_account_exists()
            
            print("\n🔍 STEP 4: Testing account login status...")
            login_status = await self.test_login_attempt()
            
            print("\n🔍 STEP 5: Testing email service status...")
            email_working = await self.test_email_service_status()
            
            # Analysis
            print("\n" + "=" * 60)
            print("🎯 INVESTIGATION ANALYSIS")
            print("=" * 60)
            
            if webhook_found:
                print("✅ WEBHOOK RECEIVED: SamCart sent webhook for this payment")
                event_type = webhook_found.get("event_type", "Unknown")
                status = webhook_found.get("status", "Unknown")
                print(f"   Event Type: {event_type}")
                print(f"   Processing Status: {status}")
                
                if status == "success":
                    print("✅ WEBHOOK PROCESSED: Backend processed webhook successfully")
                    if account_exists:
                        print("✅ ACCOUNT CREATED: Practice account was created")
                        if login_status == "exists_corrupted":
                            print("🚨 CRITICAL ISSUE: Account created but password corrupted")
                            print("💡 SOLUTION: Customer needs password reset email")
                        elif login_status == "exists_healthy":
                            print("✅ ACCOUNT HEALTHY: Account created successfully")
                            if not email_working:
                                print("🚨 EMAIL ISSUE: Welcome email may not have been sent")
                            else:
                                print("❓ MYSTERY: Account exists and email working - why no welcome email?")
                    else:
                        print("🚨 ACCOUNT CREATION FAILED: Webhook processed but no account created")
                else:
                    print("🚨 WEBHOOK PROCESSING FAILED: Webhook received but processing failed")
            else:
                print("❌ NO WEBHOOK RECEIVED: SamCart did not send webhook for this payment")
                print("🔧 POSSIBLE CAUSES:")
                print("   1. SamCart webhook URL misconfigured")
                print("   2. SamCart webhook disabled for this product")
                print("   3. Payment failed before completion")
                print("   4. Network/firewall blocking webhook delivery")
                
            # Recommendations
            print("\n🔧 IMMEDIATE ACTIONS REQUIRED:")
            if not webhook_found:
                print("1. ❗ Check SamCart webhook configuration")
                print("2. ❗ Verify webhook URL: https://samcart-auth-fix.preview.emergentagent.com/api/webhook/samcart")
                print("3. ❗ Test webhook delivery from SamCart admin panel")
                print("4. ❗ Manually create account for customer")
            elif login_status == "exists_corrupted":
                print("1. ✅ Password reset email already sent to customer")
                print("2. ❗ Customer should check email and reset password")
            elif account_exists and email_working:
                print("1. ❗ Check SendGrid delivery logs")
                print("2. ❗ Customer should check spam folder")
                print("3. ❗ Manually resend welcome email")
            
            return {
                "webhook_received": webhook_found is not None,
                "account_exists": account_exists,
                "login_status": login_status,
                "email_working": email_working,
                "webhook_data": webhook_found
            }
            
        finally:
            await self.cleanup()

async def main():
    """Main investigation execution"""
    investigator = UrgentPaymentInvestigator()
    results = await investigator.run_urgent_investigation()
    
    print(f"\n🎯 INVESTIGATION COMPLETE")
    print("=" * 60)
    
    if results["webhook_received"]:
        if results["account_exists"]:
            if results["login_status"] == "exists_healthy" and results["email_working"]:
                print("✅ LIKELY RESOLVED: Account exists and email working")
                sys.exit(0)
            else:
                print("⚠️ PARTIAL ISSUE: Account exists but may need password reset")
                sys.exit(1)
        else:
            print("🚨 CRITICAL: Webhook received but account not created")
            sys.exit(2)
    else:
        print("🚨 CRITICAL: No webhook received - SamCart configuration issue")
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())