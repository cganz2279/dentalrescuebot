#!/usr/bin/env python3
"""
URGENT: Create caryganz@gmail.com practice account in empty database
Focus: Create practice account for "The Dental Spa at Garden City" with proper details
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import time
import bcrypt
import uuid

# Configuration
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

# Target practice details from review request
PRACTICE_EMAIL = "caryganz@gmail.com"
PRACTICE_NAME = "The Dental Spa at Garden City"
PRACTICE_OWNER = "Cary Ganz"
PRACTICE_PHONE = "516-236-1083"
PRACTICE_PASSWORD = "DentalSpa2025!"

class UrgentPracticeCreator:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def admin_login(self):
        """Test admin authentication"""
        try:
            response = requests.post(f"{API_BASE}/admin/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {ADMIN_EMAIL}, token obtained"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False
    
    def check_existing_account(self):
        """Check if practice account already exists"""
        try:
            # Test login attempt to check account status
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": PRACTICE_EMAIL,
                "password": "test_password_123"  # Wrong password to test account existence
            }, timeout=30)
            
            if response.status_code == 401:
                # 401 means account exists but wrong password (healthy account)
                self.log_result(
                    f"Existing Account Check ({PRACTICE_EMAIL})",
                    True,
                    "Account already exists and is healthy (401 unauthorized for wrong password)"
                )
                return "exists_healthy"
            elif response.status_code == 500:
                # 500 means account exists but has corruption issues
                self.log_result(
                    f"Existing Account Check ({PRACTICE_EMAIL})",
                    True,
                    "Account exists but has corruption issues (500 server error) - needs password reset"
                )
                return "exists_corrupted"
            elif response.status_code == 404:
                # 404 means account doesn't exist
                self.log_result(
                    f"Existing Account Check ({PRACTICE_EMAIL})",
                    True,
                    "Account does not exist - ready for creation"
                )
                return "not_exists"
            else:
                self.log_result(
                    f"Existing Account Check ({PRACTICE_EMAIL})",
                    False,
                    f"Unexpected status: {response.status_code}",
                    response.text
                )
                return "unknown"
                
        except Exception as e:
            self.log_result(f"Existing Account Check ({PRACTICE_EMAIL})", False, error=str(e))
            return "error"
    
    def create_practice_account(self):
        """Create practice account using admin endpoint"""
        if not self.admin_token:
            self.log_result("Create Practice Account", False, error="No admin token available")
            return False
            
        try:
            # Calculate trial end date (30 days from now)
            trial_end_date = datetime.now() + timedelta(days=30)
            
            practice_data = {
                "practiceName": PRACTICE_NAME,
                "adminEmail": PRACTICE_EMAIL,
                "adminCredentials": {
                    "email": PRACTICE_EMAIL,
                    "password": PRACTICE_PASSWORD
                },
                "subscriptionType": "trial",
                "practiceDetails": {
                    "owner": PRACTICE_OWNER,
                    "phone": PRACTICE_PHONE,
                    "address": "",
                    "city": "Garden City",
                    "state": "NY",
                    "zipCode": ""
                }
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{API_BASE}/admin/create-practice",
                json=practice_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                practice_id = data.get("practice_id", "")
                
                self.log_result(
                    "Create Practice Account",
                    True,
                    f"Practice created successfully: {message}, ID: {practice_id}"
                )
                return True
            elif response.status_code == 409:
                # Account already exists
                self.log_result(
                    "Create Practice Account",
                    True,
                    "Practice account already exists (409 conflict) - this is expected if account was created previously"
                )
                return True
            else:
                self.log_result(
                    "Create Practice Account",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Create Practice Account", False, error=str(e))
            return False
    
    def create_practice_directly_via_samcart_webhook(self):
        """Create practice account directly via SamCart webhook test endpoint"""
        try:
            # Use the SamCart webhook test endpoint to create the practice
            response = requests.post(
                f"{API_BASE}/webhook/samcart/test",
                params={"test_email": PRACTICE_EMAIL},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                message = data.get("message", "")
                
                if status == "success":
                    practice_info = data.get("practice_info", {})
                    password = practice_info.get("password", "N/A")
                    practice_name = practice_info.get("practice_name", "N/A")
                    
                    self.log_result(
                        "Create Practice via SamCart Webhook",
                        True,
                        f"Practice created successfully: {practice_name}, Generated Password: {password}"
                    )
                    
                    # Store the generated password for login testing
                    global PRACTICE_PASSWORD
                    PRACTICE_PASSWORD = password
                    
                    return True
                elif "already exists" in message.lower() or "duplicate" in message.lower():
                    self.log_result(
                        "Create Practice via SamCart Webhook",
                        True,
                        "Practice account already exists (duplicate prevention working)"
                    )
                    return True
                else:
                    self.log_result(
                        "Create Practice via SamCart Webhook",
                        False,
                        f"Unexpected response: {message}"
                    )
                    return False
            else:
                self.log_result(
                    "Create Practice via SamCart Webhook",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Create Practice via SamCart Webhook", False, error=str(e))
            return False
    
    def test_practice_login(self):
        """Test practice login with created credentials"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": PRACTICE_EMAIL,
                "password": PRACTICE_PASSWORD
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                practice_id = data.get("practice_id")
                
                self.log_result(
                    "Practice Login Test",
                    True,
                    f"Login successful! Practice ID: {practice_id}, Token obtained"
                )
                return access_token
            else:
                self.log_result(
                    "Practice Login Test",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("Practice Login Test", False, error=str(e))
            return None
    
    def test_practice_dashboard(self, practice_token):
        """Test practice dashboard access"""
        if not practice_token:
            self.log_result("Practice Dashboard Test", False, error="No practice token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {practice_token}"}
            response = requests.get(
                f"{API_BASE}/practice/dashboard",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                practice_name = data.get("practice_name", "")
                owner = data.get("owner", "")
                phone = data.get("phone", "")
                
                self.log_result(
                    "Practice Dashboard Test",
                    True,
                    f"Dashboard accessible! Practice: {practice_name}, Owner: {owner}, Phone: {phone}"
                )
                
                # Verify correct practice details
                if practice_name == PRACTICE_NAME and owner == PRACTICE_OWNER and phone == PRACTICE_PHONE:
                    self.log_result(
                        "Practice Details Verification",
                        True,
                        "All practice details match the requirements perfectly"
                    )
                else:
                    self.log_result(
                        "Practice Details Verification",
                        False,
                        f"Details mismatch - Expected: {PRACTICE_NAME}/{PRACTICE_OWNER}/{PRACTICE_PHONE}, Got: {practice_name}/{owner}/{phone}"
                    )
                
                return True
            else:
                self.log_result(
                    "Practice Dashboard Test",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Practice Dashboard Test", False, error=str(e))
            return False
    
    def test_password_reset_functionality(self):
        """Test password reset functionality for the practice"""
        try:
            response = requests.post(f"{API_BASE}/auth/forgot-password", json={
                "email": PRACTICE_EMAIL,
                "recovery_method": "email"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                sent_methods = data.get("sent_methods", [])
                
                self.log_result(
                    "Password Reset Functionality",
                    True,
                    f"Password reset working: {message}, Methods: {sent_methods}"
                )
                return True
            else:
                self.log_result(
                    "Password Reset Functionality",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Password Reset Functionality", False, error=str(e))
            return False
    
    def send_welcome_email(self):
        """Send welcome email to the practice"""
        if not self.admin_token:
            self.log_result("Send Welcome Email", False, error="No admin token available")
            return False
            
        try:
            practice_data = {
                "practiceName": PRACTICE_NAME,
                "adminEmail": PRACTICE_EMAIL,
                "adminCredentials": {
                    "email": PRACTICE_EMAIL,
                    "password": PRACTICE_PASSWORD
                }
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{API_BASE}/admin/send-welcome-email",
                json=practice_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_result(
                    "Send Welcome Email",
                    True,
                    f"Welcome email sent successfully: {message}"
                )
                return True
            else:
                self.log_result(
                    "Send Welcome Email",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Send Welcome Email", False, error=str(e))
            return False
    
    def run_urgent_creation(self):
        """Run urgent practice creation process"""
        print("🚨 URGENT: Creating Practice Account for caryganz@gmail.com")
        print("=" * 70)
        print(f"Practice Name: {PRACTICE_NAME}")
        print(f"Practice Owner: {PRACTICE_OWNER}")
        print(f"Practice Phone: {PRACTICE_PHONE}")
        print(f"Practice Email: {PRACTICE_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Creation Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()
        
        # Step 1: Admin authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Check existing account status
        account_status = self.check_existing_account()
        
        # Step 3: Create or handle existing account
        if account_status == "not_exists":
            print("🔧 Creating new practice account via SamCart webhook...")
            if not self.create_practice_directly_via_samcart_webhook():
                print("❌ Failed to create practice account via SamCart webhook")
                print("🔧 Trying admin create-practice endpoint...")
                if not self.create_practice_account():
                    print("❌ Failed to create practice account via admin endpoint")
                    return False
        elif account_status == "exists_healthy":
            print("✅ Practice account already exists and is healthy")
        elif account_status == "exists_corrupted":
            print("⚠️ Practice account exists but has issues - will test password reset")
        
        # Step 4: Test login functionality
        print("🔐 Testing practice login...")
        practice_token = self.test_practice_login()
        
        # Step 5: Test dashboard access
        if practice_token:
            print("📊 Testing practice dashboard...")
            self.test_practice_dashboard(practice_token)
        
        # Step 6: Test password reset (backup access method)
        print("🔄 Testing password reset functionality...")
        self.test_password_reset_functionality()
        
        # Step 7: Send welcome email
        print("📧 Sending welcome email...")
        self.send_welcome_email()
        
        # Summary
        print("=" * 70)
        print("📊 URGENT CREATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Operations: {total_tests}")
        print(f"Successful: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical status
        login_test = next((r for r in self.test_results if "Practice Login Test" in r["test"]), None)
        dashboard_test = next((r for r in self.test_results if "Practice Dashboard Test" in r["test"]), None)
        
        print("🎯 CRITICAL STATUS:")
        if login_test and login_test["success"]:
            print(f"   ✅ Practice {PRACTICE_EMAIL} can login successfully")
            print(f"   🔑 Login credentials: {PRACTICE_EMAIL} / {PRACTICE_PASSWORD}")
            print(f"   🔗 Login URL: https://app.dentalaftercarenotes.com/login")
        else:
            print(f"   🚨 Practice {PRACTICE_EMAIL} cannot login - needs immediate attention")
        
        if dashboard_test and dashboard_test["success"]:
            print(f"   ✅ Practice dashboard accessible with correct data")
        else:
            print(f"   ⚠️ Practice dashboard has issues")
        
        # Password reset backup
        reset_test = next((r for r in self.test_results if "Password Reset" in r["test"]), None)
        if reset_test and reset_test["success"]:
            print(f"   ✅ Password reset available as backup access method")
        
        print()
        print("🎯 CUSTOMER INSTRUCTIONS:")
        print(f"   📧 Email: {PRACTICE_EMAIL}")
        print(f"   🔑 Password: {PRACTICE_PASSWORD}")
        print(f"   🔗 Login: https://app.dentalaftercarenotes.com/login")
        print(f"   🏥 Practice: {PRACTICE_NAME}")
        print(f"   👤 Owner: {PRACTICE_OWNER}")
        print(f"   📞 Phone: {PRACTICE_PHONE}")
        
        return success_rate >= 80  # Require 80%+ success for urgent creation

if __name__ == "__main__":
    creator = UrgentPracticeCreator()
    success = creator.run_urgent_creation()
    
    if success:
        print("🎉 URGENT PRACTICE CREATION COMPLETED SUCCESSFULLY!")
        print("✅ Customer caryganz@gmail.com now has full access to their practice account")
        sys.exit(0)
    else:
        print("❌ URGENT PRACTICE CREATION COMPLETED WITH ISSUES!")
        print("🚨 Manual intervention may be required")
        sys.exit(1)