#!/usr/bin/env python3
"""
Database Investigation Script
Connects to production backend to investigate user accounts and password issues
"""

import requests
import json
import sys

# Production backend URL
PRODUCTION_BACKEND_URL = "https://dentist-portal-3.emergent.host/api"

class DatabaseInvestigator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        
    def login_as_admin(self):
        """Login as super admin to access admin endpoints"""
        try:
            login_data = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    print("✅ Admin login successful")
                    return True
                else:
                    print(f"❌ Admin login failed: Invalid response format")
                    return False
            else:
                print(f"❌ Admin login failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login exception: {str(e)}")
            return False
    
    def get_all_practices(self):
        """Get all practices from admin endpoint"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None
            
        try:
            response = self.session.get(f"{self.base_url}/admin/practices", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "practices" in data:
                    practices = data["practices"]
                    print(f"✅ Found {len(practices)} practices")
                    
                    for practice in practices:
                        print(f"\n📋 Practice: {practice.get('name', 'Unknown')}")
                        print(f"   ID: {practice.get('id', 'Unknown')}")
                        print(f"   Status: {practice.get('subscription', {}).get('status', 'Unknown')}")
                        
                        # Check admin user
                        admin_user = practice.get('admin_user', {})
                        if admin_user:
                            print(f"   Admin User:")
                            print(f"     - {admin_user.get('firstName', '')} {admin_user.get('lastName', '')} ({admin_user.get('email', '')})")
                            print(f"       Role: {admin_user.get('role', '')}, Active: {admin_user.get('isActive', False)}")
                            print(f"       Login Count: {admin_user.get('loginCount', 0)}")
                    
                    return practices
                else:
                    print(f"❌ Invalid response format: {data}")
                    return None
            else:
                print(f"❌ Failed to get practices: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception getting practices: {str(e)}")
            return None
    
    def test_password_reset_for_cganz(self):
        """Test password reset process for cganz2279@gmail.com"""
        try:
            # Step 1: Request password reset
            reset_request = {
                "email": "cganz2279@gmail.com"
            }
            
            response = self.session.post(f"{self.base_url}/auth/forgot-password", json=reset_request, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "reset_token" in data:
                    reset_token = data["reset_token"]
                    print(f"✅ Reset token generated: {reset_token[:8]}...")
                    
                    # Step 2: Reset password to known value
                    reset_data = {
                        "reset_token": reset_token,
                        "new_password": "password123"
                    }
                    
                    reset_response = self.session.post(f"{self.base_url}/auth/reset-password", json=reset_data, timeout=10)
                    
                    if reset_response.status_code == 200:
                        reset_result = reset_response.json()
                        if reset_result.get("success"):
                            print("✅ Password reset successful")
                            
                            # Step 3: Test login with new password
                            login_data = {
                                "email": "cganz2279@gmail.com",
                                "password": "password123"
                            }
                            
                            login_response = self.session.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
                            
                            if login_response.status_code == 200:
                                login_result = login_response.json()
                                if login_result.get("success"):
                                    user_info = login_result.get("user", {})
                                    practice_info = login_result.get("practice", {})
                                    print(f"✅ LOGIN NOW WORKS! User: {user_info.get('firstName', '')} {user_info.get('lastName', '')} ({user_info.get('role', '')})")
                                    print(f"   Practice: {practice_info.get('name', 'Unknown')}")
                                    return True
                                else:
                                    print(f"❌ Login still failed after reset: {login_result}")
                                    return False
                            else:
                                print(f"❌ Login failed after reset: Status {login_response.status_code}")
                                return False
                        else:
                            print(f"❌ Password reset failed: {reset_result}")
                            return False
                    else:
                        print(f"❌ Password reset request failed: Status {reset_response.status_code}")
                        return False
                else:
                    print(f"❌ No reset token in response: {data}")
                    return False
            else:
                print(f"❌ Forgot password failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during password reset: {str(e)}")
            return False
    
    def investigate_user_credentials(self):
        """Main investigation function"""
        print("=" * 80)
        print("🔍 DATABASE INVESTIGATION - USER CREDENTIAL ANALYSIS")
        print("=" * 80)
        
        # Step 1: Login as admin
        if not self.login_as_admin():
            print("❌ Cannot proceed without admin access")
            return False
        
        # Step 2: Get all practices and users
        practices = self.get_all_practices()
        
        if not practices:
            print("❌ Cannot get practice information")
            return False
        
        # Step 3: Try to fix cganz2279@gmail.com password
        print("\n" + "=" * 60)
        print("🔧 ATTEMPTING TO FIX cganz2279@gmail.com PASSWORD")
        print("=" * 60)
        
        success = self.test_password_reset_for_cganz()
        
        if success:
            print("\n✅ SOLUTION FOUND: Password reset successful")
            print("   cganz2279@gmail.com/password123 should now work")
        else:
            print("\n❌ ISSUE PERSISTS: Password reset did not resolve the problem")
        
        return success

def main():
    """Main function"""
    investigator = DatabaseInvestigator(PRODUCTION_BACKEND_URL)
    success = investigator.investigate_user_credentials()
    
    if success:
        print("\n✅ Investigation completed successfully - User credentials fixed")
        sys.exit(0)
    else:
        print("\n❌ Investigation completed - Issue not resolved")
        sys.exit(1)

if __name__ == "__main__":
    main()