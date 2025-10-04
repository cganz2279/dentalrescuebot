#!/usr/bin/env python3
"""
URGENT SamCart Webhook Investigation
Investigating real customer payment that didn't create account or send emails
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://samcart-auth-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class UrgentWebhookInvestigator:
    def __init__(self):
        self.investigation_results = []
        
    def log_finding(self, investigation, success, details="", error=""):
        """Log investigation result"""
        result = {
            "investigation": investigation,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.investigation_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {investigation}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def check_recent_webhook_logs(self):
        """Investigation 1: Check Recent Webhook Logs (last 30 minutes)"""
        try:
            url = f"{API_BASE}/webhook/samcart/logs"
            
            print("🔍 Checking recent webhook logs for activity in last 30 minutes...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    logs = data.get("logs", [])
                    count = data.get("count", 0)
                    
                    # Filter logs from last 30 minutes
                    now = datetime.now()
                    thirty_minutes_ago = now - timedelta(minutes=30)
                    
                    recent_logs = []
                    for log in logs:
                        try:
                            # Parse timestamp from log
                            timestamp_str = log.get("timestamp", "")
                            if timestamp_str:
                                # Handle different timestamp formats
                                if "T" in timestamp_str:
                                    log_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                    log_time = log_time.replace(tzinfo=None)  # Remove timezone for comparison
                                    
                                    if log_time >= thirty_minutes_ago:
                                        recent_logs.append(log)
                        except Exception as parse_error:
                            print(f"   Warning: Could not parse timestamp {timestamp_str}: {parse_error}")
                    
                    if recent_logs:
                        self.log_finding(
                            "Recent Webhook Activity (Last 30 Minutes)",
                            True,
                            f"Found {len(recent_logs)} recent webhook(s). Total logs: {count}"
                        )
                        
                        # Show details of recent webhooks
                        for i, log in enumerate(recent_logs[:3]):  # Show up to 3 most recent
                            customer_email = log.get("customer_email", "Unknown")
                            event_type = log.get("event_type", "Unknown")
                            status = log.get("status", "Unknown")
                            order_id = log.get("order_id", "Unknown")
                            timestamp = log.get("timestamp", "Unknown")
                            
                            print(f"   Recent Webhook #{i+1}:")
                            print(f"     Customer: {customer_email}")
                            print(f"     Event Type: {event_type}")
                            print(f"     Status: {status}")
                            print(f"     Order ID: {order_id}")
                            print(f"     Timestamp: {timestamp}")
                            print()
                        
                        return True
                    else:
                        self.log_finding(
                            "Recent Webhook Activity (Last 30 Minutes)",
                            False,
                            f"No webhooks found in last 30 minutes. Total logs: {count}",
                            "No recent webhook activity detected - this suggests SamCart didn't send webhook for the payment"
                        )
                        
                        # Show most recent webhook for context
                        if logs:
                            latest_log = logs[0]  # Assuming logs are sorted by timestamp
                            timestamp = latest_log.get("timestamp", "Unknown")
                            customer_email = latest_log.get("customer_email", "Unknown")
                            print(f"   Most recent webhook was:")
                            print(f"     Customer: {customer_email}")
                            print(f"     Timestamp: {timestamp}")
                            print()
                        
                        return False
                else:
                    self.log_finding(
                        "Recent Webhook Activity",
                        False,
                        "",
                        f"Logs endpoint error: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_finding(
                    "Recent Webhook Activity",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_finding(
                "Recent Webhook Activity",
                False,
                "",
                str(e)
            )
            return False

    def check_webhook_stats(self):
        """Investigation 2: Check Webhook Statistics"""
        try:
            url = f"{API_BASE}/webhook/samcart/stats"
            
            print("📊 Checking webhook statistics...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                total = data.get("total_webhooks", 0)
                successful = data.get("successful_webhooks", 0)
                failed = data.get("failed_webhooks", 0)
                success_rate = data.get("success_rate", 0)
                signups = data.get("recent_practice_signups", 0)
                
                self.log_finding(
                    "Webhook Statistics",
                    True,
                    f"Total: {total}, Successful: {successful}, Failed: {failed}, Success Rate: {success_rate}%, Recent Signups: {signups}"
                )
                
                # Check if there are any failed webhooks
                if failed > 0:
                    print(f"   ⚠️  WARNING: {failed} failed webhooks detected")
                
                return True
            else:
                self.log_finding(
                    "Webhook Statistics",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_finding(
                "Webhook Statistics",
                False,
                "",
                str(e)
            )
            return False

    def check_backend_error_logs(self):
        """Investigation 3: Check Backend Error Logs"""
        try:
            print("🔍 Checking backend error logs...")
            
            # Check supervisor backend logs for errors
            import subprocess
            
            # Get recent backend logs
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                error_logs = result.stdout
                
                if error_logs.strip():
                    # Look for webhook-related errors
                    webhook_errors = []
                    lines = error_logs.split('\n')
                    
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['webhook', 'samcart', 'error', 'failed', 'exception']):
                            webhook_errors.append(line.strip())
                    
                    if webhook_errors:
                        self.log_finding(
                            "Backend Error Logs",
                            False,
                            f"Found {len(webhook_errors)} potential webhook-related errors",
                            "Check backend logs for webhook processing errors"
                        )
                        
                        # Show recent errors
                        print("   Recent webhook-related errors:")
                        for error in webhook_errors[-5:]:  # Show last 5 errors
                            print(f"     {error}")
                        print()
                        
                        return False
                    else:
                        self.log_finding(
                            "Backend Error Logs",
                            True,
                            "No webhook-related errors found in recent backend logs"
                        )
                        return True
                else:
                    self.log_finding(
                        "Backend Error Logs",
                        True,
                        "No errors in backend error log"
                    )
                    return True
            else:
                self.log_finding(
                    "Backend Error Logs",
                    False,
                    "",
                    f"Could not read backend error logs: {result.stderr}"
                )
                return False
                
        except Exception as e:
            self.log_finding(
                "Backend Error Logs",
                False,
                "",
                str(e)
            )
            return False

    def verify_webhook_endpoint_accessibility(self):
        """Investigation 4: Verify Webhook URL Status"""
        try:
            url = f"{API_BASE}/webhook/samcart"
            
            print("🌐 Verifying webhook endpoint accessibility...")
            response = requests.get(url, timeout=30)
            
            # Webhook endpoint should return 405 Method Not Allowed for GET requests
            if response.status_code == 405:
                self.log_finding(
                    "Webhook Endpoint Accessibility",
                    True,
                    "Webhook endpoint is accessible (returns 405 for GET as expected)"
                )
                return True
            elif response.status_code == 200:
                self.log_finding(
                    "Webhook Endpoint Accessibility",
                    True,
                    "Webhook endpoint is accessible (returns 200)"
                )
                return True
            else:
                self.log_finding(
                    "Webhook Endpoint Accessibility",
                    False,
                    "",
                    f"Webhook endpoint returned unexpected status: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_finding(
                "Webhook Endpoint Accessibility",
                False,
                "",
                str(e)
            )
            return False

    def test_webhook_endpoint_response(self):
        """Investigation 5: Test Webhook Endpoint Response"""
        try:
            # Test with a sample webhook payload
            url = f"{API_BASE}/webhook/samcart"
            
            # Sample SamCart webhook payload
            test_payload = {
                "event_type": "ProductPurchased",
                "customer": {
                    "email": "test.investigation@example.com",
                    "first_name": "Test",
                    "last_name": "Customer"
                },
                "order": {
                    "id": "TEST_ORDER_123",
                    "total": "49.95"
                }
            }
            
            print("🧪 Testing webhook endpoint with sample payload...")
            response = requests.post(url, json=test_payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.log_finding(
                    "Webhook Endpoint Response Test",
                    True,
                    f"Webhook endpoint processed test payload successfully: {data.get('message', 'Success')}"
                )
                return True
            else:
                self.log_finding(
                    "Webhook Endpoint Response Test",
                    False,
                    "",
                    f"Webhook endpoint test failed: HTTP {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_finding(
                "Webhook Endpoint Response Test",
                False,
                "",
                str(e)
            )
            return False

    def check_backend_service_status(self):
        """Investigation 6: Check Backend Service Status"""
        try:
            print("🔧 Checking backend service status...")
            
            # Check if backend service is running
            import subprocess
            
            result = subprocess.run(
                ["sudo", "supervisorctl", "status", "backend"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status_output = result.stdout.strip()
                
                if "RUNNING" in status_output:
                    self.log_finding(
                        "Backend Service Status",
                        True,
                        f"Backend service is running: {status_output}"
                    )
                    return True
                else:
                    self.log_finding(
                        "Backend Service Status",
                        False,
                        "",
                        f"Backend service not running properly: {status_output}"
                    )
                    return False
            else:
                self.log_finding(
                    "Backend Service Status",
                    False,
                    "",
                    f"Could not check service status: {result.stderr}"
                )
                return False
                
        except Exception as e:
            self.log_finding(
                "Backend Service Status",
                False,
                "",
                str(e)
            )
            return False

    def run_urgent_investigation(self):
        """Run urgent investigation of webhook failure"""
        print("🚨 URGENT SAMCART WEBHOOK INVESTIGATION")
        print("=" * 60)
        print("Investigating real customer payment that failed to create account")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Run investigations in order of priority
        investigations = [
            self.check_recent_webhook_logs,
            self.check_webhook_stats,
            self.verify_webhook_endpoint_accessibility,
            self.test_webhook_endpoint_response,
            self.check_backend_error_logs,
            self.check_backend_service_status
        ]
        
        critical_issues = 0
        total_investigations = len(investigations)
        
        for investigation in investigations:
            if not investigation():
                critical_issues += 1
            time.sleep(1)  # Brief pause between investigations
        
        # Print summary
        print("=" * 60)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        for result in self.investigation_results:
            status = "✅ OK" if result["success"] else "❌ ISSUE"
            print(f"{status} {result['investigation']}")
            if result["error"]:
                print(f"     Issue: {result['error']}")
        
        print()
        print(f"📊 Results: {critical_issues} critical issues found out of {total_investigations} investigations")
        
        # Provide diagnosis
        print("\n🔍 DIAGNOSIS:")
        if critical_issues == 0:
            print("✅ All webhook infrastructure appears to be working correctly.")
            print("   The issue may be:")
            print("   - SamCart webhook URL configuration")
            print("   - SamCart webhook not enabled for this product")
            print("   - Payment failed before completion")
            print("   - Network/firewall blocking webhook delivery")
        else:
            print(f"❌ Found {critical_issues} critical issues that need immediate attention.")
            print("   Check the issues above and resolve them first.")
        
        print("\n🔧 IMMEDIATE ACTIONS REQUIRED:")
        print("1. Verify SamCart webhook URL: https://samcart-auth-fix.preview.emergentagent.com/api/webhook/samcart")
        print("2. Check SamCart dashboard webhook configuration")
        print("3. Test webhook delivery from SamCart admin panel")
        print("4. Manually create account for customer if needed")
        print("5. Send welcome email manually to customer")
        
        return critical_issues == 0

if __name__ == "__main__":
    investigator = UrgentWebhookInvestigator()
    success = investigator.run_urgent_investigation()
    
    if success:
        print("\n✅ WEBHOOK INFRASTRUCTURE IS HEALTHY")
        print("   Issue is likely at SamCart configuration level")
    else:
        print("\n⚠️  CRITICAL ISSUES FOUND")
        print("   Resolve backend issues before investigating SamCart configuration")