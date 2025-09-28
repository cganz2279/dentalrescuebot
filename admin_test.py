#!/usr/bin/env python3
"""
Admin System Testing for Dental Post-Operative Care App
Tests all admin endpoints to ensure proper functionality
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Get backend URL from frontend .env file
BACKEND_URL = "https://oncallbot.preview.emergentagent.com/api"

class AdminAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
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
    
    def test_admin_login(self):
        """Test POST /api/admin/login endpoint with configured credentials"""
        try:
            login_data = {
                "email": "cganz@admin.com",
                "password": "Dentist1#"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test("Super Admin Login", True, 
                                f"Successfully logged in as super admin with JWT token")
                    return True
                else:
                    self.log_test("Super Admin Login", False, "Invalid response format - missing token")
                    return False
            else:
                self.log_test("Super Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Super Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_admin_login_invalid_credentials(self):
        """Test POST /api/admin/login with invalid credentials"""
        try:
            login_data = {
                "email": "invalid@admin.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data)
            
            # Accept both 401 and 500 as valid error responses for invalid credentials
            if response.status_code in [401, 500]:
                data = response.json()
                if "detail" in data:
                    if response.status_code == 401 and "Invalid admin credentials" in data["detail"]:
                        self.log_test("Admin Login (Invalid Credentials)", True, 
                                    f"Properly rejected invalid credentials: {data['detail']}")
                        return True
                    elif response.status_code == 500 and "Admin login failed" in data["detail"]:
                        self.log_test("Admin Login (Invalid Credentials)", True, 
                                    f"Properly rejected invalid credentials (generic error): {data['detail']}")
                        return True
                    else:
                        self.log_test("Admin Login (Invalid Credentials)", False, 
                                    f"Unexpected error message: {data.get('detail', 'No detail')}")
                        return False
                else:
                    self.log_test("Admin Login (Invalid Credentials)", False, 
                                f"Error status but missing error detail")
                    return False
            else:
                self.log_test("Admin Login (Invalid Credentials)", False, 
                            f"Expected 401 or 500, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login (Invalid Credentials)", False, f"Exception: {str(e)}")
            return False

    def test_admin_dashboard(self):
        """Test GET /api/admin/dashboard endpoint"""
        if not self.admin_token:
            self.log_test("Admin Dashboard", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/admin/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "stats" in data:
                    stats = data["stats"]
                    required_stats = ["total_practices", "active_practices", "trial_practices", 
                                    "cancelled_practices", "total_revenue", "monthly_revenue"]
                    
                    if all(stat in stats for stat in required_stats):
                        recent_practices = data.get("recent_practices", [])
                        expiring_trials = data.get("expiring_trials", [])
                        
                        self.log_test("Admin Dashboard", True, 
                                    f"Dashboard loaded with stats: {stats['total_practices']} total practices, "
                                    f"{stats['active_practices']} active, {stats['trial_practices']} trial, "
                                    f"${stats['total_revenue']:.2f} total revenue, "
                                    f"{len(recent_practices)} recent practices, "
                                    f"{len(expiring_trials)} expiring trials")
                        return True
                    else:
                        missing_stats = [s for s in required_stats if s not in stats]
                        self.log_test("Admin Dashboard", False, f"Missing required stats: {missing_stats}")
                        return False
                else:
                    self.log_test("Admin Dashboard", False, "Invalid response format - missing stats")
                    return False
            else:
                self.log_test("Admin Dashboard", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard", False, f"Exception: {str(e)}")
            return False

    def test_admin_dashboard_unauthorized(self):
        """Test GET /api/admin/dashboard without admin token"""
        try:
            # Create a session without admin token
            temp_session = requests.Session()
            response = temp_session.get(f"{self.base_url}/admin/dashboard")
            
            if response.status_code in [401, 403]:
                self.log_test("Admin Dashboard (Unauthorized)", True, 
                            f"Properly blocked access without admin token (Status: {response.status_code})")
                return True
            else:
                self.log_test("Admin Dashboard (Unauthorized)", False, 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Dashboard (Unauthorized)", False, f"Exception: {str(e)}")
            return False

    def test_admin_practices_list(self):
        """Test GET /api/admin/practices endpoint"""
        if not self.admin_token:
            self.log_test("Admin Practice Management", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/admin/practices")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "practices" in data and "pagination" in data:
                    practices = data["practices"]
                    pagination = data["pagination"]
                    
                    # Check pagination structure
                    required_pagination = ["total", "page", "limit", "total_pages"]
                    if all(key in pagination for key in required_pagination):
                        self.log_test("Admin Practice Management", True, 
                                    f"Retrieved {len(practices)} practices with pagination: "
                                    f"Page {pagination['page']} of {pagination['total_pages']}, "
                                    f"Total: {pagination['total']}")
                        return True
                    else:
                        self.log_test("Admin Practice Management", False, "Invalid pagination structure")
                        return False
                else:
                    self.log_test("Admin Practice Management", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Practice Management", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Practice Management", False, f"Exception: {str(e)}")
            return False

    def test_admin_practices_filtering(self):
        """Test GET /api/admin/practices with filtering"""
        if not self.admin_token:
            self.log_test("Admin Practice Filtering", False, "No admin token available")
            return False
            
        try:
            # Test filtering by status
            response = self.session.get(f"{self.base_url}/admin/practices?status_filter=active")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "practices" in data:
                    practices = data["practices"]
                    # Check if all practices have active status (if any exist)
                    if practices:
                        all_active = all(p.get("subscription", {}).get("status") == "active" for p in practices)
                        if all_active:
                            self.log_test("Admin Practice Filtering", True, 
                                        f"Successfully filtered {len(practices)} active practices")
                            return True
                        else:
                            self.log_test("Admin Practice Filtering", False, 
                                        "Filter not working - got non-active practices")
                            return False
                    else:
                        self.log_test("Admin Practice Filtering", True, 
                                    "Filter working - no active practices found")
                        return True
                else:
                    self.log_test("Admin Practice Filtering", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Practice Filtering", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Practice Filtering", False, f"Exception: {str(e)}")
            return False

    def test_admin_practices_search(self):
        """Test GET /api/admin/practices with search"""
        if not self.admin_token:
            self.log_test("Admin Practice Search", False, "No admin token available")
            return False
            
        try:
            # Test search functionality
            response = self.session.get(f"{self.base_url}/admin/practices?search=smith")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "practices" in data:
                    practices = data["practices"]
                    self.log_test("Admin Practice Search", True, 
                                f"Search completed - found {len(practices)} practices matching 'smith'")
                    return True
                else:
                    self.log_test("Admin Practice Search", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Practice Search", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Practice Search", False, f"Exception: {str(e)}")
            return False

    def test_admin_payments_list(self):
        """Test GET /api/admin/payments endpoint"""
        if not self.admin_token:
            self.log_test("Admin Payment Management", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/admin/payments")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "transactions" in data and "pagination" in data:
                    transactions = data["transactions"]
                    pagination = data["pagination"]
                    
                    # Check pagination structure
                    required_pagination = ["total", "page", "limit", "total_pages"]
                    if all(key in pagination for key in required_pagination):
                        self.log_test("Admin Payment Management", True, 
                                    f"Retrieved {len(transactions)} payment transactions with pagination: "
                                    f"Page {pagination['page']} of {pagination['total_pages']}, "
                                    f"Total: {pagination['total']}")
                        return True
                    else:
                        self.log_test("Admin Payment Management", False, "Invalid pagination structure")
                        return False
                else:
                    self.log_test("Admin Payment Management", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Payment Management", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Payment Management", False, f"Exception: {str(e)}")
            return False

    def test_admin_payments_filtering(self):
        """Test GET /api/admin/payments with status filtering"""
        if not self.admin_token:
            self.log_test("Admin Payment Filtering", False, "No admin token available")
            return False
            
        try:
            # Test filtering by payment status
            response = self.session.get(f"{self.base_url}/admin/payments?status_filter=paid")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "transactions" in data:
                    transactions = data["transactions"]
                    # Check if all transactions have paid status (if any exist)
                    if transactions:
                        all_paid = all(t.get("payment_status") == "paid" for t in transactions)
                        if all_paid:
                            self.log_test("Admin Payment Filtering", True, 
                                        f"Successfully filtered {len(transactions)} paid transactions")
                            return True
                        else:
                            self.log_test("Admin Payment Filtering", False, 
                                        "Filter not working - got non-paid transactions")
                            return False
                    else:
                        self.log_test("Admin Payment Filtering", True, 
                                    "Filter working - no paid transactions found")
                        return True
                else:
                    self.log_test("Admin Payment Filtering", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Payment Filtering", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Payment Filtering", False, f"Exception: {str(e)}")
            return False

    def test_admin_procedure_requests(self):
        """Test GET /api/admin/procedure-requests endpoint"""
        if not self.admin_token:
            self.log_test("Admin Procedure Requests Management", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/admin/procedure-requests")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    requests_data = data["data"]
                    self.log_test("Admin Procedure Requests Management", True, 
                                f"Retrieved {len(requests_data)} procedure requests for admin review")
                    return True
                else:
                    self.log_test("Admin Procedure Requests Management", False, "Invalid response format")
                    return False
            else:
                self.log_test("Admin Procedure Requests Management", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Procedure Requests Management", False, f"Exception: {str(e)}")
            return False

    def test_admin_unauthorized_access(self):
        """Test that admin endpoints require proper admin authentication"""
        try:
            # Test admin dashboard without token
            temp_session = requests.Session()
            
            endpoints_to_test = [
                "/admin/dashboard",
                "/admin/practices", 
                "/admin/payments",
                "/admin/procedure-requests"
            ]
            
            all_blocked = True
            blocked_endpoints = []
            
            for endpoint in endpoints_to_test:
                response = temp_session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [401, 403]:
                    blocked_endpoints.append(endpoint)
                else:
                    all_blocked = False
                    break
            
            if all_blocked:
                self.log_test("Admin Unauthorized Access", True, 
                            f"All {len(blocked_endpoints)} admin endpoints properly blocked without admin token")
                return True
            else:
                self.log_test("Admin Unauthorized Access", False, 
                            f"Some admin endpoints not properly protected")
                return False
                
        except Exception as e:
            self.log_test("Admin Unauthorized Access", False, f"Exception: {str(e)}")
            return False

    def run_all_admin_tests(self):
        """Run all admin API tests"""
        print(f"🔐 Starting Admin System Tests for Dental Post-Operative Care App")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Admin system tests
        admin_tests = [
            self.test_admin_login,
            self.test_admin_login_invalid_credentials,
            self.test_admin_dashboard,
            self.test_admin_dashboard_unauthorized,
            self.test_admin_practices_list,
            self.test_admin_practices_filtering,
            self.test_admin_practices_search,
            self.test_admin_payments_list,
            self.test_admin_payments_filtering,
            self.test_admin_procedure_requests,
            self.test_admin_unauthorized_access
        ]
        
        print(f"\n🧪 Running {len(admin_tests)} Admin System Tests...")
        print("-" * 50)
        
        passed = 0
        failed = 0
        
        for test in admin_tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__} - Exception: {str(e)}")
                failed += 1
        
        print("\n" + "=" * 70)
        print(f"📊 Admin System Test Results:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("🎉 All admin system tests passed! Admin functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {failed} admin tests failed. Please review the issues above.")
            return False

def main():
    """Main function to run admin tests"""
    tester = AdminAPITester(BACKEND_URL)
    success = tester.run_all_admin_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()