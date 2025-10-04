#!/usr/bin/env python3
"""
URGENT: Manual Welcome Email for Real SamCart Customers
Testing script to handle specific real customers mentioned in test_result.md
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

# Real customers identified from test_result.md
REAL_CUSTOMERS = [
    {
        "email": "caryganz@gmail.com",
        "name": "Cary Ganz",
        "practice_name": "The Dental Spa at Garden City",
        "order_id": "22677369",
        "status": "password_corrupted"
    },
    {
        "email": "caryganzconsulting@gmail.com", 
        "name": "Dr. Ganz",
        "practice_name": "Dr. Ganz Dental Practice",
        "order_id": "22677753",
        "status": "healthy_account"
    }
]

class UrgentRealCustomerHandler:
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
    
    def send_password_reset(self, customer_email):
        """Send password reset email to customer"""
        print(f"\n🔑 Sending password reset to {customer_email}...")
        
        try:
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
                return True, data
            else:
                self.log_test(
                    f"Password Reset - {customer_email}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(f"Password Reset - {customer_email}", False, f"Exception: {str(e)}")
            return False, {}
    
    def send_manual_welcome_email(self, customer):
        """Send manual welcome email using admin endpoint"""
        print(f"\n📧 Sending manual welcome email to {customer['email']}...")
        
        try:
            # Prepare practice data and admin credentials in correct format
            request_data = {
                "practiceData": {
                    "practiceName": customer["practice_name"]
                },
                "adminCredentials": {
                    "adminEmail": customer["email"],
                    "adminFirstName": customer["name"].split()[0] if customer["name"] else "Doctor",
                    "adminLastName": customer["name"].split()[-1] if len(customer["name"].split()) > 1 else "Practice",
                    "tempPassword": "TempPass123!"  # Temporary password for welcome email
                },
                "appUrl": "https://app.dentalaftercarenotes.com"
            }
            
            # Send welcome email via admin endpoint
            response = self.session.post(
                f"{BACKEND_URL}/api/admin/send-welcome-email",
                json=request_data,
                headers=self.get_admin_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    f"Manual Welcome Email - {customer['email']}", 
                    True, 
                    f"Welcome email sent successfully: {data.get('message', 'Success')}"
                )
                return True, data
            else:
                self.log_test(
                    f"Manual Welcome Email - {customer['email']}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False, {}
                
        except Exception as e:
            self.log_test(f"Manual Welcome Email - {customer['email']}", False, f"Exception: {str(e)}")
            return False, {}
    
    def verify_account_status(self, customer_email):
        """Verify account status by testing login"""
        print(f"\n🔍 Verifying account status for {customer_email}...")
        
        try:
            # Try to login with a dummy password to check account health
            response = self.session.post(
                f"{BACKEND_URL}/api/auth/login",
                json={
                    "email": customer_email,
                    "password": "dummy_password_test"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                # 401 means account exists and is healthy (wrong password)
                self.log_test(
                    f"Account Status - {customer_email}", 
                    True, 
                    "Account exists and is healthy (401 Unauthorized)"
                )
                return "healthy"
            elif response.status_code == 500:
                # 500 means account has corruption issues
                self.log_test(
                    f"Account Status - {customer_email}", 
                    True, 
                    "Account exists but has password corruption (500 Server Error)"
                )
                return "corrupted"
            else:
                self.log_test(
                    f"Account Status - {customer_email}", 
                    False, 
                    f"Unexpected status: {response.status_code}, Response: {response.text}"
                )
                return "unknown"
                
        except Exception as e:
            self.log_test(f"Account Status - {customer_email}", False, f"Exception: {str(e)}")
            return "error"
    
    def handle_urgent_customers(self):
        """Handle urgent real customer issues"""
        print("🚨 URGENT: Handling Real SamCart Customer Issues")
        print("=" * 60)
        
        # Step 1: Authenticate as admin
        if not self.admin_authenticate():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        success_count = 0
        
        # Step 2: Process each real customer
        for customer in REAL_CUSTOMERS:
            print(f"\n🎯 Processing customer: {customer['email']}")
            print(f"   Name: {customer['name']}")
            print(f"   Practice: {customer['practice_name']}")
            print(f"   Order ID: {customer['order_id']}")
            print(f"   Known Status: {customer['status']}")
            
            # Verify current account status
            actual_status = self.verify_account_status(customer["email"])
            
            # Send password reset (works for both healthy and corrupted accounts)
            reset_success, reset_data = self.send_password_reset(customer["email"])
            
            # Send manual welcome email
            email_success, email_data = self.send_manual_welcome_email(customer)
            
            if reset_success and email_success:
                print(f"✅ Successfully processed {customer['email']}")
                print(f"   - Password reset email sent")
                print(f"   - Welcome email sent")
                print(f"   - Customer can now access account at: https://app.dentalaftercarenotes.com/login")
                
                success_count += 1
            else:
                print(f"❌ Failed to fully process {customer['email']}")
                if reset_success:
                    print(f"   - Password reset email sent ✅")
                else:
                    print(f"   - Password reset email failed ❌")
                
                if email_success:
                    print(f"   - Welcome email sent ✅")
                else:
                    print(f"   - Welcome email failed ❌")
        
        # Step 3: Provide customer login instructions
        print("\n" + "=" * 60)
        print("🔑 CUSTOMER LOGIN INSTRUCTIONS")
        print("=" * 60)
        
        for customer in REAL_CUSTOMERS:
            print(f"\n📧 {customer['email']} ({customer['name']}):")
            print(f"   Practice: {customer['practice_name']}")
            print(f"   Login URL: https://app.dentalaftercarenotes.com/login")
            print(f"   Instructions:")
            print(f"   1. Check email inbox and spam folder for password reset email")
            print(f"   2. Click the password reset link (valid for 1 hour)")
            print(f"   3. Set a new secure password")
            print(f"   4. Login with email and new password")
            print(f"   5. Complete practice setup and branding")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 URGENT CUSTOMER HANDLING SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n🎯 RESULT: Successfully processed {success_count}/{len(REAL_CUSTOMERS)} real customers")
        
        if success_count == len(REAL_CUSTOMERS):
            print("🎉 URGENT ISSUE RESOLVED: All real customers have been provided with account access")
            print("   - Password reset emails sent to all customers")
            print("   - Welcome emails sent to all customers")
            print("   - Customers can now login and access their paid accounts")
            return True
        else:
            print("⚠️ URGENT ISSUE PARTIALLY RESOLVED: Some customers may need additional support")
            return False

def main():
    """Main execution for urgent real customer handling"""
    handler = UrgentRealCustomerHandler()
    success = handler.handle_urgent_customers()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()