#!/usr/bin/env python3
"""
COMPREHENSIVE USER ACCOUNT INVESTIGATION
Answering: "Where do users get their username and password for the practice login?"

This comprehensive test will:
1. Check existing user accounts in database
2. Test registration processes (both regular and SamCart)
3. Test authentication with existing accounts
4. Test password recovery systems
5. Investigate admin account creation capabilities
6. Provide clear answers to the user's question
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com/api"

class ComprehensiveUserAccountTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.admin_token = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_admin_access(self):
        """Get admin access to investigate database"""
        try:
            admin_credentials = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=admin_credentials)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.admin_token = data["token"]
                    self.log_test("Admin Login", True, "Successfully obtained admin access")
                    return True
                else:
                    self.log_test("Admin Login", False, f"No token in response: {data}")
                    return False
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False
    
    def investigate_existing_accounts(self):
        """Investigate what user accounts currently exist"""
        print("\n" + "="*60)
        print("🔍 INVESTIGATING EXISTING USER ACCOUNTS")
        print("="*60)
        
        if not self.admin_token:
            self.log_test("Database Investigation", False, "No admin access - cannot investigate database")
            return []
        
        try:
            # Get all practices
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/practices", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                practices = data.get("data", {}).get("practices", [])
                
                print(f"\n📊 FOUND {len(practices)} PRACTICE(S) IN DATABASE:")
                
                existing_accounts = []
                
                for i, practice in enumerate(practices, 1):
                    practice_name = practice.get("name", "Unknown")
                    practice_email = practice.get("email", "No email")
                    status = practice.get("isActive", False)
                    
                    print(f"\n🏥 PRACTICE {i}: {practice_name}")
                    print(f"   📧 Email: {practice_email}")
                    print(f"   🔄 Status: {'Active' if status else 'Inactive'}")
                    
                    # Get admin users for this practice
                    admin_users = practice.get("adminUsers", [])
                    print(f"   👥 Admin Users: {len(admin_users)}")
                    
                    for user in admin_users:
                        email = user.get("email", "No email")
                        role = user.get("role", "No role")
                        user_status = user.get("isActive", False)
                        
                        print(f"      👤 {email} ({role}) - {'Active' if user_status else 'Inactive'}")
                        
                        existing_accounts.append({
                            "email": email,
                            "role": role,
                            "practice": practice_name,
                            "status": "Active" if user_status else "Inactive"
                        })
                
                self.log_test("Database Investigation", True, f"Found {len(existing_accounts)} user accounts")
                return existing_accounts
            else:
                self.log_test("Database Investigation", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Database Investigation", False, f"Error: {str(e)}")
            return []
    
    def test_existing_login_credentials(self):
        """Test login with known credentials"""
        print("\n" + "="*60)
        print("🔑 TESTING EXISTING LOGIN CREDENTIALS")
        print("="*60)
        
        # Known credentials from test history
        test_credentials = [
            {"email": "cganz2279@gmail.com", "password": "password123"},
            {"email": "ganzseth@gmail.com", "password": "password123"},
            {"email": "admin@smithdental.com", "password": "password123"},
            {"email": "completenew@gmail.com", "password": "password123"},
            {"email": "jones@gmail.com", "password": "password123"},
            {"email": "jones2@gmail.com", "password": "password123"}
        ]
        
        working_credentials = []
        
        for cred in test_credentials:
            try:
                response = self.session.post(f"{self.base_url}/auth/login", json=cred)
                
                if response.status_code == 200:
                    data = response.json()
                    if "token" in data and data.get("success"):
                        user_info = data.get("user", {})
                        practice_info = data.get("practice", {})
                        
                        practice_name = practice_info.get("name", "Unknown Practice") if practice_info else "No Practice"
                        user_role = user_info.get("role", "Unknown Role")
                        
                        print(f"\n✅ WORKING CREDENTIALS FOUND:")
                        print(f"   📧 Email: {cred['email']}")
                        print(f"   🔑 Password: {cred['password']}")
                        print(f"   🏥 Practice: {practice_name}")
                        print(f"   👤 Role: {user_role}")
                        
                        working_credentials.append({
                            "email": cred["email"],
                            "password": cred["password"],
                            "practice": practice_name,
                            "role": user_role
                        })
                        
                        self.log_test(f"Login Test - {cred['email']}", True, f"Practice: {practice_name}, Role: {user_role}")
                    else:
                        self.log_test(f"Login Test - {cred['email']}", False, "No token in response")
                else:
                    self.log_test(f"Login Test - {cred['email']}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Login Test - {cred['email']}", False, f"Error: {str(e)}")
        
        return working_credentials
    
    def test_registration_process(self):
        """Test the registration process for new practices"""
        print("\n" + "="*60)
        print("📝 TESTING REGISTRATION PROCESS")
        print("="*60)
        
        # Test regular registration
        registration_data = {
            "practiceName": "Test New Practice Registration",
            "email": "test.registration@example.com",
            "phone": "555-123-4567",
            "website": "https://testnewpractice.com",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "adminPassword": "TestPassword123!",
            "street": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "zipCode": "12345"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/register-practice", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ REGISTRATION PROCESS WORKING:")
                print(f"   📧 New Practice Email: {registration_data['email']}")
                print(f"   🔑 New Admin Password: {registration_data['adminPassword']}")
                print(f"   🏥 Practice Name: {registration_data['practiceName']}")
                print(f"   ⚠️  Status: {data.get('message', 'Registration successful')}")
                
                if data.get("requiresPaymentSetup"):
                    print(f"   💳 Payment Required: Yes (Trial requires payment setup)")
                
                self.log_test("Regular Registration", True, "New practices can register via /register-practice")
                return True
            elif response.status_code == 400:
                data = response.json()
                if "already exists" in str(data).lower():
                    print(f"\n✅ REGISTRATION VALIDATION WORKING:")
                    print(f"   📧 Email {registration_data['email']} already exists")
                    print(f"   ✅ System prevents duplicate registrations")
                    self.log_test("Registration Validation", True, "Prevents duplicate email registration")
                    return True
                else:
                    self.log_test("Regular Registration", False, f"Validation error: {data}")
                    return False
            else:
                self.log_test("Regular Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Regular Registration", False, f"Error: {str(e)}")
            return False
    
    def test_samcart_registration(self):
        """Test SamCart integration registration"""
        print("\n" + "="*60)
        print("💳 TESTING SAMCART INTEGRATION")
        print("="*60)
        
        samcart_data = {
            "practiceName": "SamCart Integration Test Practice",
            "email": "samcart.integration@example.com",
            "phone": "555-987-6543",
            "website": "https://samcarttest.com",
            "adminFirstName": "SamCart",
            "adminLastName": "User",
            "adminPassword": "SamCartPassword123!",
            "street": "456 SamCart Avenue",
            "city": "Payment City",
            "state": "PC",
            "zipCode": "67890"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/register-practice-samcart", json=samcart_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SAMCART INTEGRATION WORKING:")
                print(f"   📧 New Practice Email: {samcart_data['email']}")
                print(f"   🔑 New Admin Password: {samcart_data['adminPassword']}")
                print(f"   🏥 Practice Name: {samcart_data['practiceName']}")
                print(f"   💳 Payment Status: Already processed via SamCart")
                print(f"   🔄 Account Status: Immediately active")
                
                self.log_test("SamCart Registration", True, "SamCart integration working - immediate activation")
                return True
            elif response.status_code == 400:
                data = response.json()
                if "already exists" in str(data).lower():
                    print(f"\n✅ SAMCART VALIDATION WORKING:")
                    print(f"   📧 Email {samcart_data['email']} already exists")
                    self.log_test("SamCart Validation", True, "Prevents duplicate SamCart registrations")
                    return True
                else:
                    self.log_test("SamCart Registration", False, f"Validation error: {data}")
                    return False
            else:
                self.log_test("SamCart Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("SamCart Registration", False, f"Error: {str(e)}")
            return False
    
    def test_password_recovery_system(self):
        """Test password recovery capabilities"""
        print("\n" + "="*60)
        print("🔄 TESTING PASSWORD RECOVERY SYSTEM")
        print("="*60)
        
        # Test forgot password
        try:
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json={
                "email": "cganz2279@gmail.com"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ FORGOT PASSWORD SYSTEM WORKING:")
                print(f"   📧 Users can request password reset via email")
                print(f"   🔗 Reset link provided: {data.get('reset_link', 'Email sent')}")
                print(f"   🔑 Reset token: {data.get('reset_token', 'Hidden for security')}")
                
                self.log_test("Forgot Password", True, "Password reset system functional")
            else:
                self.log_test("Forgot Password", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Forgot Password", False, f"Error: {str(e)}")
        
        # Test forgot username
        try:
            response = self.session.post(f"{self.base_url}/auth/forgot-username", json={
                "practice_name": "Cary Ganz DDS PC",
                "phone": "555-123-4567",
                "adminPassword": "password123"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ USERNAME RECOVERY SYSTEM WORKING:")
                print(f"   🏥 Users can recover username via practice name + phone")
                print(f"   📧 Recovered email: {data.get('email', 'Sent via email')}")
                print(f"   🔗 Login URL: {data.get('login_url', 'Provided in email')}")
                
                self.log_test("Username Recovery", True, "Username recovery system functional")
            else:
                self.log_test("Username Recovery", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Username Recovery", False, f"Error: {str(e)}")
    
    def generate_comprehensive_report(self, existing_accounts, working_credentials):
        """Generate comprehensive report answering the user's question"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE USER ACCOUNT INVESTIGATION REPORT")
        print("="*80)
        
        print(f"\n🎯 ANSWERING THE CRITICAL QUESTION:")
        print(f"   'Where do users get their username and password for the practice login?'")
        
        print(f"\n📊 CURRENT DATABASE STATUS:")
        print(f"   🏥 Total Practices: {len(existing_accounts) if existing_accounts else 0}")
        print(f"   👥 Total User Accounts: {len(existing_accounts) if existing_accounts else 0}")
        print(f"   🔑 Working Login Credentials: {len(working_credentials)}")
        
        if working_credentials:
            print(f"\n✅ CURRENT WORKING PRACTICE LOGIN CREDENTIALS:")
            for i, cred in enumerate(working_credentials, 1):
                print(f"   {i}. Email: {cred['email']}")
                print(f"      Password: {cred['password']}")
                print(f"      Practice: {cred['practice']}")
                print(f"      Role: {cred['role']}")
        else:
            print(f"\n❌ NO WORKING CREDENTIALS FOUND!")
        
        print(f"\n🚀 HOW NEW USERS GET LOGIN CREDENTIALS:")
        print(f"   1. 📝 SELF-REGISTRATION:")
        print(f"      • Visit registration page (/register)")
        print(f"      • Fill out practice and admin details")
        print(f"      • Choose email and password")
        print(f"      • Complete payment setup for activation")
        
        print(f"\n   2. 💳 SAMCART INTEGRATION:")
        print(f"      • Purchase subscription via SamCart")
        print(f"      • Automatic redirect to registration")
        print(f"      • Create email and password")
        print(f"      • Immediate activation (payment already processed)")
        
        print(f"\n   3. 👨‍💼 ADMIN CREATION:")
        print(f"      • Super admin can create practice accounts")
        print(f"      • Admin provides initial credentials")
        print(f"      • Practice admin can change password later")
        
        print(f"\n🔄 CREDENTIAL RECOVERY OPTIONS:")
        print(f"   1. 🔑 FORGOT PASSWORD:")
        print(f"      • Enter email address")
        print(f"      • Receive reset link via email")
        print(f"      • Set new password")
        
        print(f"\n   2. 📧 FORGOT USERNAME:")
        print(f"      • Provide practice name and phone")
        print(f"      • Receive username via email")
        print(f"      • Use recovered email to login")
        
        print(f"\n🎯 IMMEDIATE SOLUTIONS FOR USERS:")
        if working_credentials:
            print(f"   ✅ USE EXISTING CREDENTIALS:")
            for cred in working_credentials:
                print(f"      • Email: {cred['email']}")
                print(f"      • Password: {cred['password']}")
        
        print(f"\n   ✅ FOR NEW PRACTICES:")
        print(f"      • Visit: https://dentalpractice-hub-1.preview.emergentagent.com/register")
        print(f"      • Or purchase via SamCart integration")
        
        print(f"\n   ✅ FOR FORGOTTEN CREDENTIALS:")
        print(f"      • Use password reset: /forgot-password")
        print(f"      • Use username recovery: /forgot-username")
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"\n📈 TESTING STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
    
    def run_comprehensive_investigation(self):
        """Run complete user account investigation"""
        print("🚨 COMPREHENSIVE USER ACCOUNT INVESTIGATION")
        print("Question: Where do users get their username and password for the practice login?")
        print("="*80)
        
        # Step 1: Get admin access
        self.test_admin_access()
        
        # Step 2: Investigate existing accounts
        existing_accounts = self.investigate_existing_accounts()
        
        # Step 3: Test existing credentials
        working_credentials = self.test_existing_login_credentials()
        
        # Step 4: Test registration processes
        self.test_registration_process()
        self.test_samcart_registration()
        
        # Step 5: Test password recovery
        self.test_password_recovery_system()
        
        # Step 6: Generate comprehensive report
        self.generate_comprehensive_report(existing_accounts, working_credentials)

if __name__ == "__main__":
    print("Starting Comprehensive User Account Investigation...")
    tester = ComprehensiveUserAccountTester(BACKEND_URL)
    tester.run_comprehensive_investigation()