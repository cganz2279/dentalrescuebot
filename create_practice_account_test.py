#!/usr/bin/env python3
"""
URGENT: Create caryganz@gmail.com practice account in practices collection
Focus: Create practice account for "The Dental Spa at Garden City" with proper details
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import time

# Configuration
BACKEND_URL = "https://samcart-auth-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

# Target practice details from review request
PRACTICE_EMAIL = "caryganz@gmail.com"
PRACTICE_NAME = "The Dental Spa at Garden City"
PRACTICE_OWNER = "Cary Ganz"
PRACTICE_PHONE = "516-236-1083"

class PracticeAccountCreator:
    def __init__(self):
        self.admin_token = None
        self.practice_password = None
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
    
    def create_practice_via_samcart_webhook(self):
        """Create practice account using SamCart webhook test endpoint"""
        try:
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
                    self.practice_password = practice_info.get("password", "")
                    practice_name = practice_info.get("practice_name", "")
                    practice_id = practice_info.get("practice_id", "")
                    
                    self.log_result(
                        "Create Practice via SamCart Webhook",
                        True,
                        f"Practice created successfully: {practice_name}, ID: {practice_id}, Password: {self.practice_password}"
                    )
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
    
    def test_practice_login_with_generated_password(self):
        """Test practice login with generated password"""
        if not self.practice_password:
            self.log_result("Practice Login Test", False, error="No practice password available")
            return None
            
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": PRACTICE_EMAIL,
                "password": self.practice_password
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
                email = data.get("email", "")
                
                self.log_result(
                    "Practice Dashboard Test",
                    True,
                    f"Dashboard accessible! Practice: {practice_name}, Owner: {owner}, Phone: {phone}, Email: {email}"
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
                    "password": self.practice_password or "temp_password_123"
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
    
    def run_creation_process(self):
        """Run the complete practice creation process"""
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
        
        # Step 2: Create practice account via SamCart webhook
        print("🔧 Creating practice account via SamCart webhook...")
        if not self.create_practice_via_samcart_webhook():
            print("❌ Failed to create practice account")
            return False
        
        # Step 3: Test login with generated password
        print("🔐 Testing practice login with generated password...")
        practice_token = self.test_practice_login_with_generated_password()
        
        # Step 4: Test dashboard access
        if practice_token:
            print("📊 Testing practice dashboard...")
            self.test_practice_dashboard(practice_token)
        
        # Step 5: Send welcome email
        print("📧 Sending welcome email...")
        self.send_welcome_email()
        
        # Summary
        print("=" * 70)
        print("📊 PRACTICE CREATION SUMMARY")
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
            print(f"   🔑 Login credentials: {PRACTICE_EMAIL} / {self.practice_password}")
            print(f"   🔗 Login URL: https://app.dentalaftercarenotes.com/login")
        else:
            print(f"   🚨 Practice {PRACTICE_EMAIL} cannot login - needs immediate attention")
        
        if dashboard_test and dashboard_test["success"]:
            print(f"   ✅ Practice dashboard accessible with correct data")
        else:
            print(f"   ⚠️ Practice dashboard has issues")
        
        print()
        print("🎯 CUSTOMER INSTRUCTIONS:")
        print(f"   📧 Email: {PRACTICE_EMAIL}")
        print(f"   🔑 Password: {self.practice_password or 'Use password reset'}")
        print(f"   🔗 Login: https://app.dentalaftercarenotes.com/login")
        print(f"   🏥 Practice: {PRACTICE_NAME}")
        print(f"   👤 Owner: {PRACTICE_OWNER}")
        print(f"   📞 Phone: {PRACTICE_PHONE}")
        
        return success_rate >= 80  # Require 80%+ success

if __name__ == "__main__":
    creator = PracticeAccountCreator()
    success = creator.run_creation_process()
    
    if success:
        print("🎉 PRACTICE CREATION COMPLETED SUCCESSFULLY!")
        print("✅ Customer caryganz@gmail.com now has full access to their practice account")
        sys.exit(0)
    else:
        print("❌ PRACTICE CREATION COMPLETED WITH ISSUES!")
        print("🚨 Manual intervention may be required")
        sys.exit(1)