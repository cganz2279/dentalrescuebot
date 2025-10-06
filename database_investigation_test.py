#!/usr/bin/env python3
"""
DATABASE INVESTIGATION - Deep dive into database collections
to understand the disconnect between SamCart webhook system and admin system
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Real customer email from the issue
REAL_CUSTOMER_EMAIL = "caryganz@gmail.com"

class DatabaseInvestigator:
    def __init__(self):
        self.admin_token = None
        
    def log_finding(self, finding_name, details=""):
        """Log investigation finding"""
        print(f"🔍 {finding_name}")
        if details:
            print(f"   {details}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin"""
        try:
            admin_login_url = f"{API_BASE}/admin/login"
            admin_credentials = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = requests.post(admin_login_url, json=admin_credentials, timeout=30)
            
            if response.status_code == 200:
                admin_data = response.json()
                if admin_data.get("success") and admin_data.get("token"):
                    self.admin_token = admin_data["token"]
                    self.log_finding("Admin Authentication", "✅ Success")
                    return True
            
            self.log_finding("Admin Authentication", "❌ Failed")
            return False
                
        except Exception as e:
            self.log_finding("Admin Authentication", f"❌ Exception: {str(e)}")
            return False

    def investigate_admin_practices_collection(self):
        """Check what's in the admin practices collection"""
        try:
            if not self.admin_token:
                self.log_finding("Admin Practices Collection", "❌ No admin token")
                return
            
            practices_url = f"{API_BASE}/admin/practices"
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(practices_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                practices = data.get("practices", [])
                
                self.log_finding("Admin Practices Collection", f"Found {len(practices)} practices")
                
                # Look for customer email
                customer_found = False
                for practice in practices:
                    admin_email = practice.get("adminEmail") or practice.get("email")
                    if admin_email == REAL_CUSTOMER_EMAIL:
                        customer_found = True
                        self.log_finding("Customer in Admin System", f"✅ FOUND: {practice}")
                        break
                
                if not customer_found:
                    self.log_finding("Customer in Admin System", f"❌ NOT FOUND in {len(practices)} practices")
                
                # Show sample practice structure
                if practices:
                    sample = practices[0]
                    sample_keys = list(sample.keys())
                    self.log_finding("Admin Practice Structure", f"Sample keys: {sample_keys}")
                    
                    # Show all admin emails
                    admin_emails = []
                    for practice in practices:
                        email = practice.get("adminEmail") or practice.get("email") or "No email"
                        admin_emails.append(email)
                    
                    self.log_finding("All Admin Emails", f"{admin_emails}")
            else:
                self.log_finding("Admin Practices Collection", f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_finding("Admin Practices Collection", f"❌ Exception: {str(e)}")

    def investigate_samcart_webhook_logs(self):
        """Check SamCart webhook logs for customer"""
        try:
            logs_url = f"{API_BASE}/webhook/samcart/logs"
            
            response = requests.get(logs_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                
                self.log_finding("SamCart Webhook Logs", f"Found {len(logs)} webhook logs")
                
                # Look for customer webhooks
                customer_webhooks = []
                for log in logs:
                    if log.get("customer_email") == REAL_CUSTOMER_EMAIL:
                        customer_webhooks.append(log)
                
                if customer_webhooks:
                    self.log_finding("Customer Webhook Logs", f"✅ FOUND {len(customer_webhooks)} webhooks for customer")
                    for webhook in customer_webhooks:
                        self.log_finding("Webhook Details", f"{webhook}")
                else:
                    self.log_finding("Customer Webhook Logs", f"❌ NO webhooks found for {REAL_CUSTOMER_EMAIL}")
                
                # Show recent webhook activity
                recent_emails = [log.get("customer_email", "No email") for log in logs[:10]]
                self.log_finding("Recent Webhook Emails", f"{recent_emails}")
                
            else:
                self.log_finding("SamCart Webhook Logs", f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_finding("SamCart Webhook Logs", f"❌ Exception: {str(e)}")

    def investigate_samcart_webhook_stats(self):
        """Check SamCart webhook statistics"""
        try:
            stats_url = f"{API_BASE}/webhook/samcart/stats"
            
            response = requests.get(stats_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                total_webhooks = data.get("total_webhooks", 0)
                successful_webhooks = data.get("successful_webhooks", 0)
                failed_webhooks = data.get("failed_webhooks", 0)
                success_rate = data.get("success_rate", 0)
                recent_signups = data.get("recent_practice_signups", 0)
                
                self.log_finding("SamCart Webhook Stats", 
                    f"Total: {total_webhooks}, Success: {successful_webhooks}, Failed: {failed_webhooks}, Rate: {success_rate}%, Recent signups: {recent_signups}")
                
            else:
                self.log_finding("SamCart Webhook Stats", f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_finding("SamCart Webhook Stats", f"❌ Exception: {str(e)}")

    def test_customer_account_existence(self):
        """Test if customer account exists in SamCart system"""
        try:
            test_url = f"{API_BASE}/webhook/samcart/test"
            params = {"test_email": REAL_CUSTOMER_EMAIL}
            
            response = requests.post(test_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "duplicate":
                    self.log_finding("Customer Account in SamCart System", "✅ EXISTS (duplicate status)")
                elif status == "success":
                    self.log_finding("Customer Account in SamCart System", "❌ CREATED NEW (should have been duplicate)")
                else:
                    self.log_finding("Customer Account in SamCart System", f"❓ Unknown status: {status}")
                    
                self.log_finding("SamCart Test Response", f"{data}")
            else:
                self.log_finding("Customer Account in SamCart System", f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_finding("Customer Account in SamCart System", f"❌ Exception: {str(e)}")

    def test_customer_login_attempt(self):
        """Test if customer can login"""
        try:
            login_url = f"{API_BASE}/auth/login"
            
            # Try with common passwords
            test_passwords = ["password123", "DentalSpa2025!", "Dentist123!", "caryganz123"]
            
            for password in test_passwords:
                login_data = {
                    "email": REAL_CUSTOMER_EMAIL,
                    "password": password
                }
                
                response = requests.post(login_url, json=login_data, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_finding("Customer Login Test", f"✅ SUCCESS with password: {password}")
                        return
                elif response.status_code == 401:
                    self.log_finding("Customer Login Test", f"❌ Wrong password: {password}")
                else:
                    self.log_finding("Customer Login Test", f"❌ HTTP {response.status_code} with password: {password}")
            
            self.log_finding("Customer Login Test", "❌ All password attempts failed")
                
        except Exception as e:
            self.log_finding("Customer Login Test", f"❌ Exception: {str(e)}")

    def test_password_reset_for_customer(self):
        """Test password reset for customer"""
        try:
            reset_url = f"{API_BASE}/auth/forgot-password"
            reset_data = {
                "email": REAL_CUSTOMER_EMAIL,
                "recovery_method": "email"
            }
            
            response = requests.post(reset_url, json=reset_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_finding("Customer Password Reset", f"✅ SUCCESS: {data.get('message')}")
                else:
                    self.log_finding("Customer Password Reset", f"❌ FAILED: {data.get('message')}")
            else:
                self.log_finding("Customer Password Reset", f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_finding("Customer Password Reset", f"❌ Exception: {str(e)}")

    def investigate_recent_webhook_activity(self):
        """Check recent webhook activity to understand what's happening"""
        try:
            # Check if there are any recent webhooks being ignored
            logs_url = f"{API_BASE}/webhook/samcart/logs"
            
            response = requests.get(logs_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                
                # Look at recent logs (last 10)
                recent_logs = logs[:10]
                
                self.log_finding("Recent Webhook Activity", f"Last {len(recent_logs)} webhooks:")
                
                for i, log in enumerate(recent_logs):
                    timestamp = log.get("created_at", "No timestamp")
                    event_type = log.get("event_type", "No event type")
                    customer_email = log.get("customer_email", "No email")
                    status = log.get("status", "No status")
                    
                    self.log_finding(f"Webhook {i+1}", f"Time: {timestamp}, Event: {event_type}, Email: {customer_email}, Status: {status}")
                
            else:
                self.log_finding("Recent Webhook Activity", f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_finding("Recent Webhook Activity", f"❌ Exception: {str(e)}")

    def run_database_investigation(self):
        """Run complete database investigation"""
        print("🔍 STARTING DATABASE INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Customer Email: {REAL_CUSTOMER_EMAIL}")
        print("INVESTIGATING: Database disconnect between admin and SamCart systems")
        print("=" * 80)
        print()
        
        # Run investigations
        self.authenticate_admin()
        self.investigate_admin_practices_collection()
        self.investigate_samcart_webhook_logs()
        self.investigate_samcart_webhook_stats()
        self.test_customer_account_existence()
        self.test_customer_login_attempt()
        self.test_password_reset_for_customer()
        self.investigate_recent_webhook_activity()
        
        print("=" * 80)
        print("🎯 DATABASE INVESTIGATION COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    investigator = DatabaseInvestigator()
    investigator.run_database_investigation()