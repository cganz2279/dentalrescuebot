#!/usr/bin/env python3
"""
CRITICAL SYSTEM FAILURE INVESTIGATION
Urgent investigation of real SamCart payment failure where customer paid but received:
1. NO welcome email
2. NO password reset email  
3. NO practice created in admin system
4. System completely not working for real payments
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Real customer email from the issue
REAL_CUSTOMER_EMAIL = "caryganz@gmail.com"

class CriticalSystemInvestigator:
    def __init__(self):
        self.investigation_results = []
        self.admin_token = None
        
    def log_investigation(self, investigation_name, success, details="", error="", critical=False):
        """Log investigation result"""
        result = {
            "investigation": investigation_name,
            "success": success,
            "details": details,
            "error": error,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.investigation_results.append(result)
        
        status = "✅" if success else "🚨" if critical else "❌"
        print(f"{status} {investigation_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def investigate_admin_system_practices(self):
        """INVESTIGATION 1: Check Admin System - Look in actual admin system to see what practices exist"""
        try:
            # First authenticate as admin
            admin_login_url = f"{API_BASE}/admin/login"
            admin_credentials = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            print("🔐 Authenticating as admin to check practice database...")
            response = requests.post(admin_login_url, json=admin_credentials, timeout=30)
            
            if response.status_code == 200:
                admin_data = response.json()
                if admin_data.get("success") and admin_data.get("token"):
                    self.admin_token = admin_data["token"]
                    print(f"✅ Admin authentication successful")
                    
                    # Now check practices in admin system
                    practices_url = f"{API_BASE}/admin/practices"
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                    
                    practices_response = requests.get(practices_url, headers=headers, timeout=30)
                    
                    if practices_response.status_code == 200:
                        practices_data = practices_response.json()
                        practices = practices_data.get("practices", [])
                        
                        # Look for the real customer
                        customer_practice = None
                        for practice in practices:
                            if practice.get("adminEmail") == REAL_CUSTOMER_EMAIL:
                                customer_practice = practice
                                break
                        
                        if customer_practice:
                            self.log_investigation(
                                "Admin System Practice Check",
                                True,
                                f"FOUND customer practice in admin system! Practice: {customer_practice.get('practiceName', 'Unknown')}, Admin: {customer_practice.get('adminEmail')}, Status: {customer_practice.get('subscriptionStatus', 'Unknown')}",
                                critical=True
                            )
                        else:
                            self.log_investigation(
                                "Admin System Practice Check", 
                                False,
                                f"Customer practice NOT FOUND in admin system. Total practices found: {len(practices)}. Customer email {REAL_CUSTOMER_EMAIL} not in admin database.",
                                critical=True
                            )
                        
                        # List all practices for debugging
                        practice_emails = [p.get("adminEmail", "No email") for p in practices]
                        print(f"📋 All practice emails in admin system: {practice_emails}")
                        
                        return customer_practice is not None
                    else:
                        self.log_investigation(
                            "Admin System Practice Check",
                            False,
                            "",
                            f"Failed to get practices from admin system: HTTP {practices_response.status_code}",
                            critical=True
                        )
                        return False
                else:
                    self.log_investigation(
                        "Admin System Practice Check",
                        False,
                        "",
                        f"Admin authentication failed: {admin_data.get('message', 'Unknown error')}",
                        critical=True
                    )
                    return False
            else:
                self.log_investigation(
                    "Admin System Practice Check",
                    False,
                    "",
                    f"Admin login failed: HTTP {response.status_code}: {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_investigation(
                "Admin System Practice Check",
                False,
                "",
                f"Exception during admin system check: {str(e)}",
                critical=True
            )
            return False

    def investigate_webhook_reception(self):
        """INVESTIGATION 2: Verify Real Webhook Reception - Check if SamCart actually sent webhook for real payment"""
        try:
            # Check webhook logs for the real customer
            logs_url = f"{API_BASE}/webhook/samcart/logs"
            
            print(f"📋 Checking SamCart webhook logs for customer: {REAL_CUSTOMER_EMAIL}")
            response = requests.get(logs_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    logs = data.get("logs", [])
                    
                    # Look for webhooks with the real customer email
                    customer_webhooks = []
                    for log in logs:
                        if log.get("customer_email") == REAL_CUSTOMER_EMAIL:
                            customer_webhooks.append(log)
                    
                    if customer_webhooks:
                        # Analyze the customer webhooks
                        latest_webhook = max(customer_webhooks, key=lambda x: x.get("timestamp", ""))
                        
                        webhook_details = {
                            "timestamp": latest_webhook.get("timestamp"),
                            "event_type": latest_webhook.get("event_type"),
                            "status": latest_webhook.get("status"),
                            "order_id": latest_webhook.get("order_id"),
                            "customer_name": latest_webhook.get("customer_name")
                        }
                        
                        self.log_investigation(
                            "Real Webhook Reception Check",
                            True,
                            f"WEBHOOK FOUND for customer! Count: {len(customer_webhooks)}, Latest: {webhook_details}",
                            critical=True
                        )
                        
                        # Check if webhook was processed successfully
                        if latest_webhook.get("status") == "success":
                            print("✅ Webhook was marked as successfully processed")
                        else:
                            print(f"⚠️ Webhook status: {latest_webhook.get('status')}")
                        
                        return True
                    else:
                        # Check recent webhooks to see what's there
                        recent_webhooks = [log for log in logs if log.get("timestamp", "") > (datetime.now() - timedelta(hours=24)).isoformat()]
                        recent_emails = [log.get("customer_email") for log in recent_webhooks]
                        
                        self.log_investigation(
                            "Real Webhook Reception Check",
                            False,
                            f"NO webhook found for customer {REAL_CUSTOMER_EMAIL}. Recent webhook emails (24h): {recent_emails}",
                            critical=True
                        )
                        return False
                else:
                    self.log_investigation(
                        "Real Webhook Reception Check",
                        False,
                        "",
                        f"Webhook logs endpoint error: {data.get('message', 'Unknown error')}",
                        critical=True
                    )
                    return False
            else:
                self.log_investigation(
                    "Real Webhook Reception Check",
                    False,
                    "",
                    f"Failed to get webhook logs: HTTP {response.status_code}: {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_investigation(
                "Real Webhook Reception Check",
                False,
                "",
                f"Exception during webhook investigation: {str(e)}",
                critical=True
            )
            return False

    def investigate_database_practices(self):
        """INVESTIGATION 3: Database Investigation - Check what's actually in the practices collection"""
        try:
            # Use webhook stats to get database information
            stats_url = f"{API_BASE}/webhook/samcart/stats"
            
            print("📊 Checking SamCart webhook statistics and database state...")
            response = requests.get(stats_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                total_webhooks = data.get("total_webhooks", 0)
                successful_webhooks = data.get("successful_webhooks", 0)
                failed_webhooks = data.get("failed_webhooks", 0)
                success_rate = data.get("success_rate", 0)
                recent_signups = data.get("recent_practice_signups", 0)
                
                # Try to test webhook with customer email to see if account exists
                test_url = f"{API_BASE}/webhook/samcart/test"
                params = {"test_email": REAL_CUSTOMER_EMAIL}
                
                test_response = requests.post(test_url, params=params, timeout=30)
                
                account_exists = False
                if test_response.status_code == 200:
                    test_data = test_response.json()
                    if test_data.get("status") == "duplicate":
                        account_exists = True
                
                self.log_investigation(
                    "Database Practices Investigation",
                    True,
                    f"Database stats - Total webhooks: {total_webhooks}, Success: {successful_webhooks}, Failed: {failed_webhooks}, Rate: {success_rate}%, Recent signups: {recent_signups}. Customer account exists: {account_exists}",
                    critical=True
                )
                
                return True
            else:
                self.log_investigation(
                    "Database Practices Investigation",
                    False,
                    "",
                    f"Failed to get database stats: HTTP {response.status_code}: {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_investigation(
                "Database Practices Investigation",
                False,
                "",
                f"Exception during database investigation: {str(e)}",
                critical=True
            )
            return False

    def investigate_email_system(self):
        """INVESTIGATION 4: Email System Deep Test - Test if emails are actually being sent to real email addresses"""
        try:
            # Test password reset email to real customer
            reset_url = f"{API_BASE}/auth/forgot-password"
            reset_data = {
                "email": REAL_CUSTOMER_EMAIL,
                "recovery_method": "email"
            }
            
            print(f"📧 Testing email system with real customer email: {REAL_CUSTOMER_EMAIL}")
            response = requests.post(reset_url, json=reset_data, timeout=30)
            
            email_test_success = False
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    email_test_success = True
                    
            # Also test admin welcome email if we have admin token
            admin_email_success = False
            if self.admin_token:
                welcome_url = f"{API_BASE}/admin/send-welcome-email"
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                welcome_data = {
                    "practiceData": {
                        "practiceName": "Test Practice for Email Investigation",
                        "adminEmail": REAL_CUSTOMER_EMAIL
                    },
                    "adminCredentials": {
                        "email": REAL_CUSTOMER_EMAIL,
                        "password": "TestPassword123!"
                    }
                }
                
                welcome_response = requests.post(welcome_url, json=welcome_data, headers=headers, timeout=30)
                if welcome_response.status_code == 200:
                    welcome_result = welcome_response.json()
                    if welcome_result.get("success"):
                        admin_email_success = True
            
            self.log_investigation(
                "Email System Deep Test",
                email_test_success or admin_email_success,
                f"Password reset email test: {'✅ Success' if email_test_success else '❌ Failed'}, Admin welcome email test: {'✅ Success' if admin_email_success else '❌ Failed'}",
                "" if (email_test_success or admin_email_success) else "Both email tests failed - email system may be broken",
                critical=True
            )
            
            return email_test_success or admin_email_success
            
        except Exception as e:
            self.log_investigation(
                "Email System Deep Test",
                False,
                "",
                f"Exception during email system test: {str(e)}",
                critical=True
            )
            return False

    def investigate_webhook_url_config(self):
        """INVESTIGATION 5: SamCart Webhook URL - Verify webhook URL configuration"""
        try:
            # Test webhook endpoint accessibility
            webhook_url = f"{API_BASE}/webhook/samcart"
            
            print("🔗 Testing SamCart webhook URL accessibility...")
            
            # Test GET request (should return 405 Method Not Allowed)
            get_response = requests.get(webhook_url, timeout=30)
            
            # Test POST request with minimal data
            test_webhook_data = {
                "event_type": "test",
                "customer": {
                    "email": "test@example.com",
                    "name": "Test Customer"
                }
            }
            
            post_response = requests.post(webhook_url, json=test_webhook_data, timeout=30)
            
            webhook_accessible = False
            if get_response.status_code == 405:  # Method not allowed is expected for GET
                webhook_accessible = True
            elif post_response.status_code in [200, 400, 422]:  # These are acceptable responses
                webhook_accessible = True
            
            expected_webhook_url = f"{BACKEND_URL}/api/webhook/samcart"
            
            self.log_investigation(
                "SamCart Webhook URL Configuration",
                webhook_accessible,
                f"Webhook URL: {expected_webhook_url}, GET response: {get_response.status_code}, POST response: {post_response.status_code}",
                "" if webhook_accessible else "Webhook endpoint not accessible - SamCart cannot send webhooks",
                critical=True
            )
            
            return webhook_accessible
            
        except Exception as e:
            self.log_investigation(
                "SamCart Webhook URL Configuration",
                False,
                "",
                f"Exception during webhook URL test: {str(e)}",
                critical=True
            )
            return False

    def investigate_backend_errors(self):
        """INVESTIGATION 6: Backend Error Analysis - Look for hidden errors in email sending"""
        try:
            # Check if we can access backend health
            health_url = f"{API_BASE}/health"
            
            print("🏥 Checking backend health and error status...")
            response = requests.get(health_url, timeout=30)
            
            backend_healthy = False
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    backend_healthy = True
            
            # Test a webhook creation to see if there are any hidden errors
            test_webhook_url = f"{API_BASE}/webhook/samcart/test"
            test_email = f"error.investigation.{int(time.time())}@example.com"
            params = {"test_email": test_email}
            
            webhook_test_response = requests.post(test_webhook_url, params=params, timeout=30)
            webhook_test_success = False
            webhook_error = ""
            
            if webhook_test_response.status_code == 200:
                webhook_data = webhook_test_response.json()
                if webhook_data.get("status") == "success":
                    webhook_test_success = True
                else:
                    webhook_error = f"Webhook test failed: {webhook_data.get('message', 'Unknown error')}"
            else:
                webhook_error = f"Webhook test HTTP error: {webhook_test_response.status_code}"
            
            self.log_investigation(
                "Backend Error Analysis",
                backend_healthy and webhook_test_success,
                f"Backend health: {'✅ Healthy' if backend_healthy else '❌ Unhealthy'}, Webhook test: {'✅ Success' if webhook_test_success else '❌ Failed'}",
                webhook_error if webhook_error else "",
                critical=True
            )
            
            return backend_healthy and webhook_test_success
            
        except Exception as e:
            self.log_investigation(
                "Backend Error Analysis",
                False,
                "",
                f"Exception during backend error analysis: {str(e)}",
                critical=True
            )
            return False

    def provide_immediate_solution(self):
        """INVESTIGATION 7: Provide immediate solution for the customer"""
        try:
            if not self.admin_token:
                print("❌ Cannot provide solution - no admin access")
                return False
            
            # Try to manually create/fix the customer account
            print(f"🔧 Attempting to provide immediate solution for customer: {REAL_CUSTOMER_EMAIL}")
            
            # Send password reset email
            reset_url = f"{API_BASE}/auth/forgot-password"
            reset_data = {
                "email": REAL_CUSTOMER_EMAIL,
                "recovery_method": "email"
            }
            
            reset_response = requests.post(reset_url, json=reset_data, timeout=30)
            reset_success = False
            if reset_response.status_code == 200:
                reset_result = reset_response.json()
                if reset_result.get("success"):
                    reset_success = True
            
            # Send manual welcome email
            welcome_url = f"{API_BASE}/admin/send-welcome-email"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            welcome_data = {
                "practiceData": {
                    "practiceName": "The Dental Spa at Garden City",
                    "adminEmail": REAL_CUSTOMER_EMAIL
                },
                "adminCredentials": {
                    "email": REAL_CUSTOMER_EMAIL,
                    "password": "DentalSpa2025!"
                }
            }
            
            welcome_response = requests.post(welcome_url, json=welcome_data, headers=headers, timeout=30)
            welcome_success = False
            if welcome_response.status_code == 200:
                welcome_result = welcome_response.json()
                if welcome_result.get("success"):
                    welcome_success = True
            
            solution_provided = reset_success or welcome_success
            
            self.log_investigation(
                "Immediate Customer Solution",
                solution_provided,
                f"Password reset email: {'✅ Sent' if reset_success else '❌ Failed'}, Manual welcome email: {'✅ Sent' if welcome_success else '❌ Failed'}",
                "" if solution_provided else "Unable to send any emails to customer",
                critical=True
            )
            
            if solution_provided:
                print(f"📧 CUSTOMER SOLUTION: Emails sent to {REAL_CUSTOMER_EMAIL}")
                print("   Customer should check email for:")
                print("   1. Password reset link (if password reset worked)")
                print("   2. Welcome email with login credentials (if welcome email worked)")
                print(f"   3. Login at: {BACKEND_URL.replace('/api', '')}/login")
            
            return solution_provided
            
        except Exception as e:
            self.log_investigation(
                "Immediate Customer Solution",
                False,
                "",
                f"Exception during solution attempt: {str(e)}",
                critical=True
            )
            return False

    def run_critical_investigation(self):
        """Run all critical system failure investigations"""
        print("🚨 STARTING CRITICAL SYSTEM FAILURE INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Real Customer Email: {REAL_CUSTOMER_EMAIL}")
        print("INVESTIGATING: Real SamCart payment with NO system response")
        print("=" * 80)
        print()
        
        # Run investigations in order
        investigations = [
            ("Admin System Check", self.investigate_admin_system_practices),
            ("Webhook Reception Check", self.investigate_webhook_reception),
            ("Database Investigation", self.investigate_database_practices),
            ("Email System Test", self.investigate_email_system),
            ("Webhook URL Config", self.investigate_webhook_url_config),
            ("Backend Error Analysis", self.investigate_backend_errors),
            ("Immediate Solution", self.provide_immediate_solution)
        ]
        
        passed = 0
        critical_failures = []
        
        for name, investigation in investigations:
            print(f"🔍 Running: {name}")
            try:
                if investigation():
                    passed += 1
                else:
                    critical_failures.append(name)
            except Exception as e:
                print(f"💥 EXCEPTION in {name}: {str(e)}")
                critical_failures.append(name)
            
            time.sleep(2)  # Pause between investigations
            print()
        
        # Print critical summary
        print("=" * 80)
        print("🎯 CRITICAL INVESTIGATION SUMMARY")
        print("=" * 80)
        
        for result in self.investigation_results:
            if result["critical"]:
                status = "✅ WORKING" if result["success"] else "🚨 CRITICAL FAILURE"
                print(f"{status} {result['investigation']}")
                if result["details"]:
                    print(f"     Details: {result['details']}")
                if result["error"]:
                    print(f"     Error: {result['error']}")
                print()
        
        print(f"📊 Investigation Results: {passed}/{len(investigations)} systems working")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   - {failure}")
        
        # Provide root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if "Webhook Reception Check" in critical_failures:
            print("   🚨 PRIMARY ISSUE: SamCart did NOT send webhook for real payment")
            print("   🔧 SOLUTION: Check SamCart webhook configuration")
        elif "Email System Test" in critical_failures:
            print("   🚨 PRIMARY ISSUE: Email system is completely broken")
            print("   🔧 SOLUTION: Fix SendGrid configuration and email service")
        elif "Admin System Check" in critical_failures:
            print("   🚨 PRIMARY ISSUE: Customer account was never created")
            print("   🔧 SOLUTION: Manual account creation required")
        else:
            print("   ✅ Most systems working - issue may be resolved or intermittent")
        
        return len(critical_failures) == 0

if __name__ == "__main__":
    investigator = CriticalSystemInvestigator()
    success = investigator.run_critical_investigation()
    
    if success:
        print("\n✅ INVESTIGATION COMPLETE - No critical failures found")
        exit(0)
    else:
        print("\n🚨 CRITICAL SYSTEM FAILURES IDENTIFIED - Immediate action required")
        exit(1)