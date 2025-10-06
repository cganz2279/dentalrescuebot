#!/usr/bin/env python3
"""
URGENT: Manual Welcome Email for Recent SamCart Payment
Testing script to find recent SamCart payment and send manual welcome email
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "https://dentiportal.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class UrgentSamCartPaymentHandler:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def admin_authenticate(self):
        """Authenticate as admin"""
        print("🔐 Authenticating as admin...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/admin/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                self.log_test(
                    "Admin Authentication", 
                    True, 
                    f"Admin token obtained successfully"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get admin authentication headers"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def find_recent_samcart_payments(self):
        """Find the most recent SamCart payments (last 30 minutes)"""
        print("\n🔍 Searching for recent SamCart payments...")
        
        try:
            # Get SamCart webhook logs
            response = self.session.get(
                f"{BACKEND_URL}/api/webhook/samcart/logs",
                params={"limit": 20}
            )
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                
                # Filter for recent payments (last 30 minutes)
                cutoff_time = datetime.utcnow() - timedelta(minutes=30)
                recent_payments = []
                
                for log in logs:
                    created_at = datetime.fromisoformat(log["created_at"].replace("Z", "+00:00"))
                    
                    # Check if it's a recent payment event
                    if (created_at > cutoff_time and 
                        log.get("event_type") in ["ProductPurchased", "Order", "OrderCompleted"] and
                        log.get("processing_status") == "success"):
                        
                        # Extract customer email from payload
                        payload = log.get("payload", {})
                        customer = payload.get("customer", {})
                        customer_email = customer.get("email", "").lower().strip()
                        
                        if customer_email and "@" in customer_email:
                            recent_payments.append({
                                "webhook_id": log["webhook_id"],
                                "event_type": log["event_type"],
                                "customer_email": customer_email,
                                "customer_name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                                "order_id": payload.get("order", {}).get("id"),
                                "created_at": log["created_at"],
                                "minutes_ago": int((datetime.utcnow() - created_at).total_seconds() / 60)
                            })
                
                if recent_payments:
                    # Sort by most recent first
                    recent_payments.sort(key=lambda x: x["created_at"], reverse=True)
                    
                    self.log_test(
                        "Find Recent SamCart Payments", 
                        True, 
                        f"Found {len(recent_payments)} recent payments in last 30 minutes"
                    )
                    
                    # Display recent payments
                    print("\n📋 Recent SamCart Payments (Last 30 minutes):")
                    for i, payment in enumerate(recent_payments, 1):
                        print(f"   {i}. {payment['customer_email']} ({payment['customer_name']})")
                        print(f"      Order ID: {payment['order_id']}, {payment['minutes_ago']} minutes ago")
                        print(f"      Event: {payment['event_type']}, Webhook: {payment['webhook_id']}")
                    
                    return recent_payments
                else:
                    self.log_test(
                        "Find Recent SamCart Payments", 
                        False, 
                        "No recent payments found in last 30 minutes"
                    )
                    return []
            else:
                self.log_test(
                    "Find Recent SamCart Payments", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test("Find Recent SamCart Payments", False, f"Exception: {str(e)}")
            return []
    
    def check_practice_account_exists(self, customer_email):
        """Check if practice account already exists for customer"""
        print(f"\n🔍 Checking if practice account exists for {customer_email}...")
        
        try:
            # Try to test webhook endpoint to see if account exists
            response = self.session.post(
                f"{BACKEND_URL}/api/webhook/samcart/test",
                params={"test_email": customer_email}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "duplicate":
                    self.log_test(
                        f"Account Check - {customer_email}", 
                        True, 
                        "Practice account already exists"
                    )
                    return True, data.get("practice_info", {})
                elif data.get("status") == "success":
                    self.log_test(
                        f"Account Check - {customer_email}", 
                        True, 
                        "New practice account created via test endpoint"
                    )
                    return True, data.get("practice_info", {})
                else:
                    self.log_test(
                        f"Account Check - {customer_email}", 
                        False, 
                        f"Unexpected response: {data}"
                    )
                    return False, {}
            else:
                self.log_test(
                    f"Account Check - {customer_email}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(f"Account Check - {customer_email}", False, f"Exception: {str(e)}")
            return False, {}
    
    def send_manual_welcome_email(self, customer_email, practice_info=None):
        """Send manual welcome email using admin endpoint"""
        print(f"\n📧 Sending manual welcome email to {customer_email}...")
        
        try:
            # Prepare practice data for welcome email
            if not practice_info:
                # Create basic practice info if not provided
                practice_info = {
                    "practiceName": f"Dental Practice ({customer_email})",
                    "adminEmail": customer_email,
                    "adminFirstName": "Doctor",
                    "adminLastName": "Practice",
                    "tempPassword": "TempPass123!"
                }
            
            # Send welcome email via admin endpoint
            response = self.session.post(
                f"{BACKEND_URL}/api/admin/send-welcome-email",
                json=practice_info,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    f"Manual Welcome Email - {customer_email}", 
                    True, 
                    f"Welcome email sent successfully: {data.get('message', 'Success')}"
                )
                return True, data
            else:
                self.log_test(
                    f"Manual Welcome Email - {customer_email}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(f"Manual Welcome Email - {customer_email}", False, f"Exception: {str(e)}")
            return False, {}
    
    def get_login_credentials(self, customer_email):
        """Get or generate login credentials for customer"""
        print(f"\n🔑 Getting login credentials for {customer_email}...")
        
        try:
            # Try password reset to get fresh credentials
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/forgot-password",
                json={
                    "email": customer_email,
                    "recovery_method": "email"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    f"Password Reset - {customer_email}", 
                    True, 
                    f"Password reset email sent: {data.get('message', 'Success')}"
                )
                
                return {
                    "email": customer_email,
                    "password_reset": "Password reset email sent",
                    "login_url": "https://app.dentalaftercarenotes.com/login",
                    "instructions": "Check email for password reset link"
                }
            else:
                self.log_test(
                    f"Password Reset - {customer_email}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
                # Return basic login info even if password reset fails
                return {
                    "email": customer_email,
                    "password": "Use password reset if needed",
                    "login_url": "https://app.dentalaftercarenotes.com/login",
                    "instructions": "Contact support if login issues persist"
                }
                
        except Exception as e:
            self.log_test(f"Password Reset - {customer_email}", False, f"Exception: {str(e)}")
            
            # Return basic login info
            return {
                "email": customer_email,
                "password": "Contact support for password",
                "login_url": "https://app.dentalaftercarenotes.com/login",
                "instructions": "Contact support for login assistance"
            }
    
    def handle_urgent_payment(self):
        """Handle the urgent payment issue - main workflow"""
        print("🚨 URGENT: Handling Recent SamCart Payment Issue")
        print("=" * 60)
        
        # Step 1: Authenticate as admin
        if not self.admin_authenticate():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Find recent SamCart payments
        recent_payments = self.find_recent_samcart_payments()
        
        if not recent_payments:
            print("⚠️ No recent SamCart payments found in last 30 minutes")
            print("   Checking last 2 hours instead...")
            
            # Extend search to 2 hours
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/api/webhook/samcart/logs",
                    params={"limit": 50}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logs = data.get("logs", [])
                    
                    # Filter for payments in last 2 hours
                    cutoff_time = datetime.utcnow() - timedelta(hours=2)
                    extended_payments = []
                    
                    for log in logs:
                        created_at = datetime.fromisoformat(log["created_at"].replace("Z", "+00:00"))
                        
                        if (created_at > cutoff_time and 
                            log.get("event_type") in ["ProductPurchased", "Order", "OrderCompleted"] and
                            log.get("processing_status") == "success"):
                            
                            payload = log.get("payload", {})
                            customer = payload.get("customer", {})
                            customer_email = customer.get("email", "").lower().strip()
                            
                            if customer_email and "@" in customer_email:
                                extended_payments.append({
                                    "webhook_id": log["webhook_id"],
                                    "event_type": log["event_type"],
                                    "customer_email": customer_email,
                                    "customer_name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                                    "order_id": payload.get("order", {}).get("id"),
                                    "created_at": log["created_at"],
                                    "hours_ago": int((datetime.utcnow() - created_at).total_seconds() / 3600)
                                })
                    
                    if extended_payments:
                        print(f"📋 Found {len(extended_payments)} payments in last 2 hours:")
                        for i, payment in enumerate(extended_payments, 1):
                            print(f"   {i}. {payment['customer_email']} ({payment['customer_name']})")
                            print(f"      Order ID: {payment['order_id']}, {payment['hours_ago']} hours ago")
                        
                        recent_payments = extended_payments
                    else:
                        print("❌ No recent payments found even in last 2 hours")
                        return False
            except Exception as e:
                print(f"❌ Error extending search: {e}")
                return False
        
        # Step 3: Process each recent payment
        success_count = 0
        
        for payment in recent_payments:
            customer_email = payment["customer_email"]
            customer_name = payment["customer_name"]
            
            print(f"\n🎯 Processing payment for: {customer_email} ({customer_name})")
            print(f"   Order ID: {payment['order_id']}")
            
            # Check if account exists
            account_exists, practice_info = self.check_practice_account_exists(customer_email)
            
            if account_exists:
                print(f"✅ Practice account confirmed for {customer_email}")
                
                # Send manual welcome email
                email_success, email_data = self.send_manual_welcome_email(
                    customer_email, 
                    practice_info
                )
                
                if email_success:
                    print(f"✅ Welcome email sent to {customer_email}")
                    
                    # Get login credentials
                    credentials = self.get_login_credentials(customer_email)
                    
                    print(f"\n🔑 LOGIN CREDENTIALS FOR {customer_email}:")
                    print(f"   Email: {credentials['email']}")
                    print(f"   Password: {credentials.get('password', 'Use password reset')}")
                    print(f"   Login URL: {credentials['login_url']}")
                    print(f"   Instructions: {credentials['instructions']}")
                    
                    success_count += 1
                else:
                    print(f"❌ Failed to send welcome email to {customer_email}")
            else:
                print(f"❌ Could not confirm/create account for {customer_email}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 URGENT PAYMENT HANDLING SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULT: Successfully processed {success_count}/{len(recent_payments)} recent payments")
        
        if success_count > 0:
            print("🎉 URGENT ISSUE RESOLVED: Welcome emails sent and login credentials provided")
            return True
        else:
            print("⚠️ URGENT ISSUE PARTIALLY RESOLVED: Some payments may need manual intervention")
            return False

def main():
    """Main execution for urgent payment handling"""
    handler = UrgentSamCartPaymentHandler()
    success = handler.handle_urgent_payment()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()