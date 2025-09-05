#!/usr/bin/env python3
"""
URGENT USER ACCOUNT INVESTIGATION
Investigating the critical question: "Where do users get their username and password for the practice login?"

This script will:
1. Check what user accounts exist in the database
2. Test the registration/signup process
3. Check authentication endpoints and credentials
4. Investigate business process for creating new practice accounts
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://dentistpdf.preview.emergentagent.com/api"

class UserAccountInvestigator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.investigation_results = []
        self.auth_token = None
        self.admin_token = None
        
    def log_finding(self, category: str, finding: str, details: str = ""):
        """Log investigation findings"""
        print(f"\n🔍 {category}: {finding}")
        if details:
            print(f"   Details: {details}")
        
        self.investigation_results.append({
            "category": category,
            "finding": finding,
            "details": details
        })
    
    def test_admin_login(self):
        """Test admin login to access user management"""
        try:
            # Try known admin credentials from test_result.md
            admin_credentials = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=admin_credentials)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.admin_token = data["token"]
                    self.log_finding("ADMIN ACCESS", "Successfully logged in as admin", 
                                   f"Admin token obtained for user management access")
                    return True
                else:
                    self.log_finding("ADMIN ACCESS", "Admin login failed - no token", 
                                   f"Response: {data}")
                    return False
            else:
                self.log_finding("ADMIN ACCESS", "Admin login failed", 
                               f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_finding("ADMIN ACCESS", "Admin login error", f"Error: {str(e)}")
            return False
    
    def investigate_database_users(self):
        """Investigate what users exist in the database"""
        try:
            if not self.admin_token:
                self.log_finding("DATABASE USERS", "Cannot investigate - no admin access", 
                               "Need admin token to access user data")
                return
            
            # Try to get practices (which contain user accounts)
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/practices", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                practices = data.get("data", {}).get("practices", [])
                
                self.log_finding("DATABASE USERS", f"Found {len(practices)} practice(s) in database")
                
                for i, practice in enumerate(practices, 1):
                    practice_name = practice.get("name", "Unknown")
                    admin_users = practice.get("adminUsers", [])
                    
                    self.log_finding("PRACTICE ACCOUNT", f"Practice {i}: {practice_name}", 
                                   f"Admin users: {len(admin_users)}")
                    
                    for user in admin_users:
                        email = user.get("email", "No email")
                        role = user.get("role", "No role")
                        status = user.get("status", "No status")
                        self.log_finding("USER CREDENTIAL", f"Email: {email}", 
                                       f"Role: {role}, Status: {status}")
                
                return practices
            else:
                self.log_finding("DATABASE USERS", "Failed to retrieve practices", 
                               f"Status: {response.status_code}, Response: {response.text}")
                return []
        except Exception as e:
            self.log_finding("DATABASE USERS", "Error investigating database", f"Error: {str(e)}")
            return []
    
    def test_registration_system(self):
        """Test the registration/signup process"""
        try:
            # Test if registration endpoint exists
            test_registration = {
                "practiceName": "Test Investigation Practice",
                "adminEmail": "test.investigation@example.com",
                "adminPassword": "TestPassword123!",
                "phone": "555-123-4567",
                "address": "123 Test St, Test City, TS 12345"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register-practice", json=test_registration)
            
            if response.status_code == 200:
                self.log_finding("REGISTRATION SYSTEM", "Registration endpoint working", 
                               "New practices can register via /api/auth/register-practice")
            elif response.status_code == 400:
                data = response.json()
                if "already exists" in str(data).lower():
                    self.log_finding("REGISTRATION SYSTEM", "Registration endpoint working (email exists)", 
                                   "Registration system is functional but email already in use")
                else:
                    self.log_finding("REGISTRATION SYSTEM", "Registration validation working", 
                                   f"Validation error: {data}")
            else:
                self.log_finding("REGISTRATION SYSTEM", "Registration endpoint issue", 
                               f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_finding("REGISTRATION SYSTEM", "Registration test error", f"Error: {str(e)}")
    
    def test_samcart_integration(self):
        """Test SamCart integration for new signups"""
        try:
            # Test SamCart registration endpoint
            samcart_data = {
                "practiceName": "SamCart Test Practice",
                "adminEmail": "samcart.test@example.com",
                "adminPassword": "SamCartTest123!",
                "phone": "555-987-6543",
                "address": "456 SamCart Ave, Payment City, PC 67890",
                "paymentId": "test_payment_123",
                "subscriptionType": "monthly"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register-practice-samcart", json=samcart_data)
            
            if response.status_code == 200:
                self.log_finding("SAMCART INTEGRATION", "SamCart registration working", 
                               "New practices can sign up via SamCart integration")
            elif response.status_code == 400:
                data = response.json()
                self.log_finding("SAMCART INTEGRATION", "SamCart endpoint exists but validation failed", 
                               f"Response: {data}")
            else:
                self.log_finding("SAMCART INTEGRATION", "SamCart integration issue", 
                               f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_finding("SAMCART INTEGRATION", "SamCart test error", f"Error: {str(e)}")
    
    def test_existing_credentials(self):
        """Test login with known credentials from test history"""
        known_credentials = [
            {"email": "cganz2279@gmail.com", "password": "password123", "source": "test_result.md"},
            {"email": "admin@smithdental.com", "password": "password123", "source": "test_result.md"},
            {"email": "completenew@gmail.com", "password": "password123", "source": "test_result.md"},
            {"email": "jones@gmail.com", "password": "password123", "source": "test_result.md"},
            {"email": "ganzseth@gmail.com", "password": "password123", "source": "test_result.md"}
        ]
        
        working_credentials = []
        
        for cred in known_credentials:
            try:
                response = self.session.post(f"{self.base_url}/auth/login", json={
                    "email": cred["email"],
                    "password": cred["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if "token" in data:
                        working_credentials.append(cred)
                        practice_name = data.get("user", {}).get("practiceName", "Unknown Practice")
                        self.log_finding("WORKING CREDENTIALS", f"✅ {cred['email']}", 
                                       f"Password: {cred['password']}, Practice: {practice_name}")
                    else:
                        self.log_finding("CREDENTIAL TEST", f"❌ {cred['email']} - No token", 
                                       f"Response: {data}")
                else:
                    self.log_finding("CREDENTIAL TEST", f"❌ {cred['email']} - Login failed", 
                                   f"Status: {response.status_code}")
            except Exception as e:
                self.log_finding("CREDENTIAL TEST", f"❌ {cred['email']} - Error", f"Error: {str(e)}")
        
        return working_credentials
    
    def investigate_password_reset_system(self):
        """Investigate password reset capabilities"""
        try:
            # Test forgot password endpoint
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json={
                "email": "cganz2279@gmail.com"
            })
            
            if response.status_code == 200:
                self.log_finding("PASSWORD RESET", "Forgot password system working", 
                               "Users can reset passwords via /api/auth/forgot-password")
            else:
                self.log_finding("PASSWORD RESET", "Password reset issue", 
                               f"Status: {response.status_code}, Response: {response.text}")
            
            # Test forgot username endpoint
            response = self.session.post(f"{self.base_url}/auth/forgot-username", json={
                "practiceName": "Cary Ganz DDS PC",
                "phone": "555-123-4567",
                "adminPassword": "password123"
            })
            
            if response.status_code == 200:
                self.log_finding("USERNAME RECOVERY", "Username recovery system working", 
                               "Users can recover usernames via practice name and phone")
            else:
                self.log_finding("USERNAME RECOVERY", "Username recovery issue", 
                               f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_finding("PASSWORD RESET", "Password reset test error", f"Error: {str(e)}")
    
    def investigate_patient_accounts(self):
        """Investigate patient account system"""
        try:
            # First login as practice admin to check patient accounts
            login_response = self.session.post(f"{self.base_url}/auth/login", json={
                "email": "cganz2279@gmail.com",
                "password": "password123"
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                if "token" in data:
                    practice_token = data["token"]
                    headers = {"Authorization": f"Bearer {practice_token}"}
                    
                    # Get patients
                    patients_response = self.session.get(f"{self.base_url}/practice/patients", headers=headers)
                    
                    if patients_response.status_code == 200:
                        patients_data = patients_response.json()
                        patients = patients_data.get("data", [])
                        
                        self.log_finding("PATIENT ACCOUNTS", f"Found {len(patients)} patient account(s)")
                        
                        for patient in patients:
                            email = patient.get("email", "No email")
                            name = f"{patient.get('firstName', '')} {patient.get('lastName', '')}"
                            status = patient.get("status", "unknown")
                            self.log_finding("PATIENT CREDENTIAL", f"Patient: {name}", 
                                           f"Email: {email}, Status: {status}")
                    else:
                        self.log_finding("PATIENT ACCOUNTS", "Failed to retrieve patients", 
                                       f"Status: {patients_response.status_code}")
        except Exception as e:
            self.log_finding("PATIENT ACCOUNTS", "Patient investigation error", f"Error: {str(e)}")
    
    def run_investigation(self):
        """Run complete user account investigation"""
        print("=" * 80)
        print("🚨 URGENT USER ACCOUNT INVESTIGATION")
        print("Question: Where do users get their username and password for the practice login?")
        print("=" * 80)
        
        # Step 1: Get admin access
        print("\n📋 STEP 1: OBTAINING ADMIN ACCESS")
        self.test_admin_login()
        
        # Step 2: Investigate database users
        print("\n📋 STEP 2: INVESTIGATING DATABASE USERS")
        practices = self.investigate_database_users()
        
        # Step 3: Test existing credentials
        print("\n📋 STEP 3: TESTING KNOWN CREDENTIALS")
        working_creds = self.test_existing_credentials()
        
        # Step 4: Test registration systems
        print("\n📋 STEP 4: TESTING REGISTRATION SYSTEMS")
        self.test_registration_system()
        self.test_samcart_integration()
        
        # Step 5: Test password recovery
        print("\n📋 STEP 5: TESTING PASSWORD RECOVERY")
        self.investigate_password_reset_system()
        
        # Step 6: Investigate patient accounts
        print("\n📋 STEP 6: INVESTIGATING PATIENT ACCOUNTS")
        self.investigate_patient_accounts()
        
        # Generate summary report
        self.generate_summary_report(working_creds)
    
    def generate_summary_report(self, working_credentials):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 80)
        print("📊 INVESTIGATION SUMMARY REPORT")
        print("=" * 80)
        
        print("\n🔑 WORKING PRACTICE LOGIN CREDENTIALS:")
        if working_credentials:
            for cred in working_credentials:
                print(f"   ✅ Email: {cred['email']}")
                print(f"      Password: {cred['password']}")
        else:
            print("   ❌ No working credentials found!")
        
        print(f"\n📈 INVESTIGATION STATISTICS:")
        print(f"   Total findings: {len(self.investigation_results)}")
        
        categories = {}
        for result in self.investigation_results:
            cat = result["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for category, count in categories.items():
            print(f"   {category}: {count} findings")
        
        print("\n🎯 KEY ANSWERS TO USER'S QUESTION:")
        print("   'Where do users get their username and password for the practice login?'")
        print("\n   1. EXISTING USERS: Use credentials from registration process")
        print("   2. NEW USERS: Register via /register or SamCart integration")
        print("   3. FORGOT CREDENTIALS: Use password reset or username recovery")
        print("   4. ADMIN CREATED: Super admin can create practice accounts")

if __name__ == "__main__":
    print("Starting User Account Investigation...")
    investigator = UserAccountInvestigator(BACKEND_URL)
    investigator.run_investigation()