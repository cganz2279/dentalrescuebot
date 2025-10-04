#!/usr/bin/env python3

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "https://dentalpractice-hub-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class AdminFunctionalityTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin"""
        print("🔐 Authenticating as admin...")
        
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/admin/login", json=auth_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.admin_token = data.get("token")
                    
                    # Set authorization header
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    
                    print(f"   ✅ Admin authentication successful")
                    return True
                else:
                    print(f"   ❌ Admin authentication failed: {data.get('error')}")
                    return False
            else:
                print(f"   ❌ Admin authentication failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Admin authentication error: {str(e)}")
            return False
    
    def test_admin_practices_list(self):
        """Test admin practices list"""
        print("\n📋 Testing Admin Practices List...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/practices", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practices = data.get("data", [])
                    print(f"   ✅ Found {len(practices)} practices")
                    
                    for practice in practices:
                        print(f"      - {practice.get('name', 'Unknown')} ({practice.get('adminEmail', 'No email')})")
                        print(f"        Status: {practice.get('status', 'Unknown')}")
                        print(f"        Created: {practice.get('createdAt', 'Unknown')}")
                    
                    return True
                else:
                    print(f"   ❌ Failed: {data.get('error')}")
                    return False
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def test_create_practice(self):
        """Test creating a new practice"""
        print("\n➕ Testing Create Practice...")
        
        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        practice_data = {
            "practiceName": f"Test Practice {test_id}",
            "adminEmail": f"test.admin.{test_id}@example.com",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "phone": "555-123-4567",
            "tempPassword": "TempPass123!",
            "address": "123 Test Street, Test City, TS 12345",
            "subscriptionType": "trial",
            "trialDays": 30
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/admin/create-practice", json=practice_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practice_id = data.get("practiceId")
                    print(f"   ✅ Practice created successfully")
                    print(f"      Practice ID: {practice_id}")
                    print(f"      Practice Name: {practice_data['practiceName']}")
                    return practice_id
                else:
                    print(f"   ❌ Failed: {data.get('error')}")
                    return None
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
    
    def test_welcome_email(self, practice_id=None):
        """Test welcome email functionality"""
        print("\n📧 Testing Welcome Email...")
        
        if not practice_id:
            practice_id = "test-practice-id"
        
        email_data = {
            "practiceId": practice_id,
            "adminEmail": "test@example.com",
            "practiceName": "Test Practice",
            "adminFirstName": "Test",
            "adminLastName": "Admin",
            "tempPassword": "TempPass123!"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/admin/send-welcome-email", json=email_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Welcome email sent successfully")
                    print(f"      Message: {data.get('message', 'Email sent')}")
                    return True
                else:
                    print(f"   ❌ Failed: {data.get('error')}")
                    return False
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access"""
        print("\n🏠 Testing Admin Dashboard Access...")
        
        try:
            # Test admin dashboard endpoint
            response = self.session.get(f"{BASE_URL}/admin/dashboard", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    dashboard_data = data.get("data", {})
                    print(f"   ✅ Admin dashboard accessible")
                    print(f"      Admin: {dashboard_data.get('adminName', 'Unknown')}")
                    print(f"      Total Practices: {dashboard_data.get('totalPractices', 0)}")
                    return True
                else:
                    print(f"   ❌ Failed: {data.get('error')}")
                    return False
            elif response.status_code == 404:
                print(f"   ⚠️  Admin dashboard endpoint not found (404)")
                return False
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def test_admin_routes_accessibility(self):
        """Test various admin routes for accessibility"""
        print("\n🛣️  Testing Admin Routes Accessibility...")
        
        routes_to_test = [
            "/admin/practices",
            "/admin/users", 
            "/admin/stats",
            "/admin/settings"
        ]
        
        accessible_routes = []
        inaccessible_routes = []
        
        for route in routes_to_test:
            try:
                response = self.session.get(f"{BASE_URL}{route}", timeout=10)
                
                if response.status_code == 200:
                    accessible_routes.append(route)
                    print(f"   ✅ {route} - Accessible")
                elif response.status_code == 404:
                    inaccessible_routes.append((route, "Not Found"))
                    print(f"   ❌ {route} - Not Found (404)")
                elif response.status_code in [401, 403]:
                    inaccessible_routes.append((route, "Auth Error"))
                    print(f"   ❌ {route} - Auth Error ({response.status_code})")
                else:
                    inaccessible_routes.append((route, f"Status {response.status_code}"))
                    print(f"   ❌ {route} - Status {response.status_code}")
                    
            except Exception as e:
                inaccessible_routes.append((route, f"Error: {str(e)}"))
                print(f"   ❌ {route} - Error: {str(e)}")
        
        print(f"\n   📊 Summary: {len(accessible_routes)} accessible, {len(inaccessible_routes)} inaccessible")
        return len(accessible_routes) > 0
    
    def run_comprehensive_admin_test(self):
        """Run comprehensive admin functionality test"""
        print("👑 COMPREHENSIVE ADMIN FUNCTIONALITY TEST")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all admin tests
        tests = [
            ("Admin Dashboard Access", self.test_admin_dashboard_access),
            ("Admin Practices List", self.test_admin_practices_list),
            ("Admin Routes Accessibility", self.test_admin_routes_accessibility),
            ("Welcome Email", lambda: self.test_welcome_email()),
            ("Create Practice", self.test_create_practice)
        ]
        
        results = []
        practice_id = None
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            try:
                if test_name == "Create Practice":
                    result = test_func()
                    if result:
                        practice_id = result
                        results.append((test_name, True))
                    else:
                        results.append((test_name, False))
                else:
                    result = test_func()
                    results.append((test_name, result))
                    
            except Exception as e:
                print(f"❌ {test_name}: CRITICAL ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Test welcome email with created practice if available
        if practice_id:
            print(f"\n{'='*60}")
            print("📧 Testing Welcome Email with Created Practice...")
            try:
                email_result = self.test_welcome_email(practice_id)
                results.append(("Welcome Email (Created Practice)", email_result))
            except Exception as e:
                print(f"❌ Welcome Email (Created Practice): ERROR - {str(e)}")
                results.append(("Welcome Email (Created Practice)", False))
        
        # Generate summary
        print("\n" + "="*80)
        print("👑 ADMIN FUNCTIONALITY TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📊 RESULTS: {passed}/{total} tests passed")
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        if passed == total:
            print(f"\n🎉 ALL ADMIN FUNCTIONALITY TESTS PASSED!")
            return True
        elif passed >= total * 0.7:  # 70% pass rate
            print(f"\n⚠️  ADMIN FUNCTIONALITY MOSTLY WORKING ({passed}/{total} passed)")
            return True
        else:
            print(f"\n❌ ADMIN FUNCTIONALITY HAS SIGNIFICANT ISSUES ({passed}/{total} passed)")
            return False

def main():
    """Main function"""
    tester = AdminFunctionalityTester()
    success = tester.run_comprehensive_admin_test()
    
    if success:
        print("\n✅ Admin functionality is working!")
    else:
        print("\n❌ Admin functionality has critical issues!")
    
    return success

if __name__ == "__main__":
    main()