#!/usr/bin/env python3
"""
CRITICAL SAMCART PAYMENT INVESTIGATION
=====================================
Real SamCart payment processed but NO welcome email sent.
User paid with live credit card, got SamCart confirmation, but no app welcome email or account creation.

This test investigates:
1. SamCart webhook logs for recent activity (last 30 minutes)
2. SamCart webhook endpoint accessibility 
3. Webhook processing errors
4. Account creation process
5. Email system functionality
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"

class SamCartWebhookInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, status: str, details: str, data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        self.results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        
        if data and status in ["FAIL", "WARN"]:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
    
    async def test_webhook_endpoint_accessibility(self):
        """Test if SamCart webhook endpoint is accessible"""
        try:
            # Test GET request (should return 405 Method Not Allowed)
            async with self.session.get(f"{self.backend_url}/api/webhook/samcart") as response:
                if response.status == 405:
                    self.log_result(
                        "Webhook Endpoint Accessibility",
                        "PASS",
                        f"Webhook endpoint accessible (returns {response.status} as expected for GET)"
                    )
                else:
                    self.log_result(
                        "Webhook Endpoint Accessibility", 
                        "WARN",
                        f"Unexpected status code: {response.status}",
                        {"status": response.status, "text": await response.text()}
                    )
        except Exception as e:
            self.log_result(
                "Webhook Endpoint Accessibility",
                "FAIL", 
                f"Cannot access webhook endpoint: {str(e)}"
            )
    
    async def check_recent_webhook_logs(self):
        """Check SamCart webhook logs for recent activity (last 30 minutes)"""
        try:
            async with self.session.get(f"{self.backend_url}/api/webhook/samcart/logs") as response:
                if response.status == 200:
                    data = await response.json()
                    logs = data.get("logs", [])
                    
                    # Filter logs from last 30 minutes
                    now = datetime.now(timezone.utc)
                    thirty_minutes_ago = now - timedelta(minutes=30)
                    
                    recent_logs = []
                    for log in logs:
                        try:
                            log_time = datetime.fromisoformat(log["created_at"].replace("Z", "+00:00"))
                            if log_time >= thirty_minutes_ago:
                                recent_logs.append(log)
                        except:
                            continue
                    
                    if recent_logs:
                        self.log_result(
                            "Recent Webhook Activity (30 min)",
                            "WARN",
                            f"Found {len(recent_logs)} webhook(s) in last 30 minutes",
                            {
                                "recent_webhooks": len(recent_logs),
                                "logs": [
                                    {
                                        "webhook_id": log.get("webhook_id"),
                                        "event_type": log.get("event_type"),
                                        "status": log.get("processing_status"),
                                        "created_at": log.get("created_at"),
                                        "customer_email": log.get("payload", {}).get("customer", {}).get("email")
                                    } for log in recent_logs
                                ]
                            }
                        )
                    else:
                        self.log_result(
                            "Recent Webhook Activity (30 min)",
                            "FAIL",
                            "NO webhooks received in last 30 minutes - this explains missing welcome email",
                            {"total_logs": len(logs), "recent_logs": 0}
                        )
                        
                    # Also check all logs for patterns
                    all_emails = []
                    for log in logs:
                        customer_email = log.get("payload", {}).get("customer", {}).get("email")
                        if customer_email:
                            all_emails.append(customer_email)
                    
                    self.log_result(
                        "All Webhook Logs Analysis",
                        "INFO",
                        f"Total webhooks: {len(logs)}, Unique emails: {len(set(all_emails))}",
                        {
                            "total_webhooks": len(logs),
                            "unique_emails": list(set(all_emails)),
                            "most_recent": logs[0] if logs else None
                        }
                    )
                        
                else:
                    self.log_result(
                        "Recent Webhook Activity",
                        "FAIL",
                        f"Cannot access webhook logs: HTTP {response.status}"
                    )
        except Exception as e:
            self.log_result(
                "Recent Webhook Activity",
                "FAIL",
                f"Error checking webhook logs: {str(e)}"
            )
    
    async def check_webhook_statistics(self):
        """Check webhook processing statistics"""
        try:
            async with self.session.get(f"{self.backend_url}/api/webhook/samcart/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    
                    self.log_result(
                        "Webhook Statistics",
                        "PASS",
                        f"Total: {stats.get('total_webhooks', 0)}, Success: {stats.get('successful_webhooks', 0)}, Failed: {stats.get('failed_webhooks', 0)}, Success Rate: {stats.get('success_rate', 0):.1f}%",
                        stats
                    )
                else:
                    self.log_result(
                        "Webhook Statistics",
                        "FAIL",
                        f"Cannot access webhook stats: HTTP {response.status}"
                    )
        except Exception as e:
            self.log_result(
                "Webhook Statistics",
                "FAIL",
                f"Error checking webhook stats: {str(e)}"
            )
    
    async def test_webhook_processing(self):
        """Test webhook processing with a test payload"""
        try:
            test_email = f"urgent.test.{datetime.now().strftime('%H%M%S')}@example.com"
            
            async with self.session.post(f"{self.backend_url}/api/webhook/samcart/test?test_email={test_email}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        self.log_result(
                            "Webhook Processing Test",
                            "PASS",
                            f"Test webhook processed successfully for {test_email}",
                            {
                                "practice_id": data.get("practice_info", {}).get("practice_id"),
                                "emails_sent": data.get("emails_sent", {}),
                                "test_email": test_email
                            }
                        )
                    else:
                        self.log_result(
                            "Webhook Processing Test",
                            "WARN",
                            f"Test webhook returned: {data.get('message', 'Unknown status')}",
                            data
                        )
                else:
                    self.log_result(
                        "Webhook Processing Test",
                        "FAIL",
                        f"Test webhook failed: HTTP {response.status}",
                        {"response": await response.text()}
                    )
        except Exception as e:
            self.log_result(
                "Webhook Processing Test",
                "FAIL",
                f"Error testing webhook processing: {str(e)}"
            )
    
    async def check_email_system(self):
        """Test email system functionality"""
        try:
            # Test password reset email (uses same email service)
            test_payload = {
                "email": "test.email.check@example.com",
                "recovery_method": "email"
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/auth/forgot-password",
                json=test_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "email" in data.get("sent_methods", []):
                        self.log_result(
                            "Email System Test",
                            "PASS",
                            "Email service is operational (password reset email sent)",
                            {"sent_methods": data.get("sent_methods")}
                        )
                    else:
                        self.log_result(
                            "Email System Test",
                            "WARN",
                            "Email service may have issues",
                            data
                        )
                else:
                    self.log_result(
                        "Email System Test",
                        "FAIL",
                        f"Email test failed: HTTP {response.status}",
                        {"response": await response.text()}
                    )
        except Exception as e:
            self.log_result(
                "Email System Test",
                "FAIL",
                f"Error testing email system: {str(e)}"
            )
    
    async def check_backend_health(self):
        """Check backend health"""
        try:
            async with self.session.get(f"{self.backend_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Backend Health Check",
                        "PASS",
                        f"Backend is healthy: {data.get('message', 'OK')}",
                        data
                    )
                else:
                    self.log_result(
                        "Backend Health Check",
                        "FAIL",
                        f"Backend health check failed: HTTP {response.status}"
                    )
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                "FAIL",
                f"Cannot reach backend: {str(e)}"
            )
    
    async def investigate_specific_customer_issue(self):
        """Look for specific patterns that might indicate the customer's payment issue"""
        try:
            # Check if there are any failed webhooks or processing errors
            async with self.session.get(f"{self.backend_url}/api/webhook/samcart/logs?limit=100") as response:
                if response.status == 200:
                    data = await response.json()
                    logs = data.get("logs", [])
                    
                    # Analyze for patterns
                    failed_logs = [log for log in logs if log.get("processing_status") == "failed"]
                    recent_orders = []
                    
                    # Look for recent order activity
                    now = datetime.now(timezone.utc)
                    one_hour_ago = now - timedelta(hours=1)
                    
                    for log in logs:
                        try:
                            log_time = datetime.fromisoformat(log["created_at"].replace("Z", "+00:00"))
                            if log_time >= one_hour_ago:
                                order_id = log.get("payload", {}).get("order", {}).get("id")
                                customer_email = log.get("payload", {}).get("customer", {}).get("email")
                                recent_orders.append({
                                    "webhook_id": log.get("webhook_id"),
                                    "order_id": order_id,
                                    "customer_email": customer_email,
                                    "event_type": log.get("event_type"),
                                    "status": log.get("processing_status"),
                                    "created_at": log.get("created_at")
                                })
                        except:
                            continue
                    
                    if failed_logs:
                        self.log_result(
                            "Failed Webhook Analysis",
                            "WARN",
                            f"Found {len(failed_logs)} failed webhook(s)",
                            {"failed_webhooks": failed_logs[:5]}  # Show first 5
                        )
                    
                    if recent_orders:
                        self.log_result(
                            "Recent Order Activity (1 hour)",
                            "INFO",
                            f"Found {len(recent_orders)} recent order(s)",
                            {"recent_orders": recent_orders}
                        )
                    else:
                        self.log_result(
                            "Recent Order Activity (1 hour)",
                            "FAIL",
                            "NO recent order activity found - customer's payment likely didn't trigger webhook",
                            {"analysis": "This confirms the customer's payment did not reach our webhook system"}
                        )
                        
        except Exception as e:
            self.log_result(
                "Customer Issue Investigation",
                "FAIL",
                f"Error investigating customer issue: {str(e)}"
            )
    
    async def run_investigation(self):
        """Run complete investigation"""
        print("🚨 CRITICAL SAMCART PAYMENT INVESTIGATION")
        print("=" * 50)
        print("Real payment processed but NO welcome email sent!")
        print("Investigating webhook system...")
        print()
        
        # Run all tests
        await self.check_backend_health()
        await self.test_webhook_endpoint_accessibility()
        await self.check_recent_webhook_logs()
        await self.check_webhook_statistics()
        await self.investigate_specific_customer_issue()
        await self.test_webhook_processing()
        await self.check_email_system()
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 50)
        
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARN"])
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print()
        
        # Critical findings
        critical_issues = [r for r in self.results if r["status"] == "FAIL"]
        if critical_issues:
            print("🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   • {issue['test']}: {issue['details']}")
        
        # Root cause analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        
        recent_webhook_test = next((r for r in self.results if "Recent Webhook Activity" in r["test"]), None)
        if recent_webhook_test and recent_webhook_test["status"] == "FAIL":
            print("   🎯 PRIMARY ISSUE: No webhook received for customer's payment")
            print("   📋 LIKELY CAUSES:")
            print("      1. SamCart webhook URL misconfigured")
            print("      2. SamCart webhook disabled for this product")
            print("      3. Payment failed before webhook trigger")
            print("      4. Network/firewall blocking webhook delivery")
            print()
            print("   🔧 IMMEDIATE ACTIONS REQUIRED:")
            print("      1. Verify SamCart webhook URL: https://samcart-auth-fix.preview.emergentagent.com/api/webhook/samcart")
            print("      2. Check SamCart dashboard webhook configuration")
            print("      3. Test webhook delivery from SamCart admin panel")
            print("      4. Manually create account for paying customer")
        
        webhook_test = next((r for r in self.results if "Webhook Processing Test" in r["test"]), None)
        email_test = next((r for r in self.results if "Email System Test" in r["test"]), None)
        
        if webhook_test and webhook_test["status"] == "PASS" and email_test and email_test["status"] == "PASS":
            print("   ✅ BACKEND SYSTEMS: All backend systems are working correctly")
            print("   🎯 CONCLUSION: Issue is at SamCart webhook delivery level, not backend processing")

async def main():
    """Main investigation function"""
    async with SamCartWebhookInvestigator() as investigator:
        await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())