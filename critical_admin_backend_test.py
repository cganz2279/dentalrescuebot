#!/usr/bin/env python3
"""
CRITICAL ADMIN SYSTEM FAILURE INVESTIGATION - Backend Testing
Testing admin functionality that must work perfectly with no room for error.

CRITICAL ADMIN FUNCTIONALITY REQUIRED:
1. View All Practices - Admin must see all customer accounts including SamCart customers
2. Practice Statistics - Total, active, trial, cancelled counts must be accurate
3. Trial Management - Track expiring trials, extend trials, manage renewals
4. Customer Support - Search customers, view account details, manage subscriptions
5. Revenue Tracking - Monitor subscription revenue and business metrics

IMMEDIATE INVESTIGATION NEEDED:
1. Test Admin Authentication - Verify admin login still works
2. Test Admin Database Queries - Check if admin can access practices collection
3. Test Admin Dashboard Endpoint - Verify statistics and data retrieval
4. Test Admin Practice Management - Verify CRUD operations on practices
5. Check Database Connection - Ensure admin system connects to correct database
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dentiportal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "cganz@admin.com"
ADMIN_PASSWORD = "Dentist1#"

class AdminSystemTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_admin_authentication(self):
        """Test admin login functionality"""
        try:
            print("🔐 Testing Admin Authentication...")
            
            # Test admin login
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = requests.post(f"{API_BASE}/admin/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.admin_token = data["token"]
                    self.log_test(
                        "Admin Login",
                        True,
                        f"Successfully authenticated as {ADMIN_EMAIL}, token received"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Login",
                        False,
                        "",
                        f"Login response missing success/token: {data}"
                    )
            else:
                self.log_test(
                    "Admin Login",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Admin Login", False, "", str(e))
            
        return False

    def test_admin_dashboard_statistics(self):
        """Test admin dashboard statistics - CRITICAL ISSUE"""
        try:
            print("📊 Testing Admin Dashboard Statistics...")
            
            if not self.admin_token:
                self.log_test(
                    "Admin Dashboard Statistics",
                    False,
                    "",
                    "No admin token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{API_BASE}/admin/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("stats", {})
                    
                    # Check for null values - CRITICAL ISSUE
                    critical_stats = [
                        "total_practices",
                        "active_practices", 
                        "trial_practices",
                        "cancelled_practices"
                    ]
                    
                    null_stats = []
                    for stat in critical_stats:
                        if stats.get(stat) is None:
                            null_stats.append(stat)
                    
                    if null_stats:
                        self.log_test(
                            "Admin Dashboard Statistics",
                            False,
                            f"Stats: {stats}",
                            f"CRITICAL: These stats are returning null: {null_stats}"
                        )
                        return False
                    else:
                        self.log_test(
                            "Admin Dashboard Statistics",
                            True,
                            f"All stats working: total_practices={stats.get('total_practices')}, "
                            f"active_practices={stats.get('active_practices')}, "
                            f"trial_practices={stats.get('trial_practices')}, "
                            f"cancelled_practices={stats.get('cancelled_practices')}, "
                            f"total_revenue={stats.get('total_revenue')}, "
                            f"monthly_revenue={stats.get('monthly_revenue')}"
                        )
                        return True
                else:
                    self.log_test(
                        "Admin Dashboard Statistics",
                        False,
                        "",
                        f"Dashboard response not successful: {data}"
                    )
            else:
                self.log_test(
                    "Admin Dashboard Statistics",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Admin Dashboard Statistics", False, "", str(e))
            
        return False

    def test_admin_practices_list(self):
        """Test admin practices list - CRITICAL ISSUE"""
        try:
            print("📋 Testing Admin Practices List...")
            
            if not self.admin_token:
                self.log_test(
                    "Admin Practices List",
                    False,
                    "",
                    "No admin token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test with higher limit to see all practices
            response = requests.get(f"{API_BASE}/admin/practices?limit=100", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practices = data.get("practices", [])
                    pagination = data.get("pagination", {})
                    total = pagination.get("total", 0)
                    
                    if total == 0:
                        self.log_test(
                            "Admin Practices List",
                            False,
                            f"Pagination: {pagination}",
                            "CRITICAL: Returning 0 practices when there should be multiple including caryganz@gmail.com"
                        )
                        return False
                    else:
                        # Look for specific customer
                        caryganz_found = False
                        samcart_practices = 0
                        
                        for practice in practices:
                            if practice.get("email") == "caryganz@gmail.com":
                                caryganz_found = True
                            if practice.get("source") == "samcart":
                                samcart_practices += 1
                        
                        details = f"Total practices: {total}, SamCart practices: {samcart_practices}"
                        if caryganz_found:
                            details += ", caryganz@gmail.com found ✅"
                        else:
                            details += ", caryganz@gmail.com NOT found ❌"
                            
                        self.log_test(
                            "Admin Practices List",
                            True,
                            details
                        )
                        return True
                else:
                    self.log_test(
                        "Admin Practices List",
                        False,
                        "",
                        f"Practices response not successful: {data}"
                    )
            else:
                self.log_test(
                    "Admin Practices List",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Admin Practices List", False, "", str(e))
            
        return False

    def test_admin_search_functionality(self):
        """Test admin search for specific customers"""
        try:
            print("🔍 Testing Admin Search Functionality...")
            
            if not self.admin_token:
                self.log_test(
                    "Admin Search Functionality",
                    False,
                    "",
                    "No admin token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Search for caryganz@gmail.com
            response = requests.get(
                f"{API_BASE}/admin/practices?search=caryganz@gmail.com&limit=100", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    practices = data.get("practices", [])
                    total = data.get("pagination", {}).get("total", 0)
                    
                    if total > 0:
                        practice = practices[0]
                        self.log_test(
                            "Admin Search Functionality",
                            True,
                            f"Found caryganz@gmail.com: {practice.get('name', 'Unknown')}, "
                            f"Status: {practice.get('subscription', {}).get('status', 'Unknown')}, "
                            f"Source: {practice.get('source', 'Unknown')}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Admin Search Functionality",
                            False,
                            "",
                            "Search for caryganz@gmail.com returned 0 results"
                        )
                else:
                    self.log_test(
                        "Admin Search Functionality",
                        False,
                        "",
                        f"Search response not successful: {data}"
                    )
            else:
                self.log_test(
                    "Admin Search Functionality",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Admin Search Functionality", False, "", str(e))
            
        return False

    def test_database_connectivity(self):
        """Test database connectivity through admin endpoints"""
        try:
            print("🗄️ Testing Database Connectivity...")
            
            if not self.admin_token:
                self.log_test(
                    "Database Connectivity",
                    False,
                    "",
                    "No admin token available"
                )
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test multiple endpoints to verify database connectivity
            endpoints_to_test = [
                ("/admin/dashboard", "Dashboard"),
                ("/admin/practices?limit=1", "Practices"),
                ("/admin/monitoring", "Monitoring")
            ]
            
            successful_connections = 0
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            successful_connections += 1
                except:
                    pass
            
            if successful_connections == len(endpoints_to_test):
                self.log_test(
                    "Database Connectivity",
                    True,
                    f"All {successful_connections}/{len(endpoints_to_test)} admin endpoints successfully connected to database"
                )
                return True
            else:
                self.log_test(
                    "Database Connectivity",
                    False,
                    "",
                    f"Only {successful_connections}/{len(endpoints_to_test)} admin endpoints successfully connected to database"
                )
                
        except Exception as e:
            self.log_test("Database Connectivity", False, "", str(e))
            
        return False

    def run_all_tests(self):
        """Run all admin system tests"""
        print("🚨 CRITICAL ADMIN SYSTEM FAILURE INVESTIGATION")
        print("=" * 60)
        print(f"Testing admin functionality at: {API_BASE}")
        print("=" * 60)
        print()
        
        # Test admin authentication first
        if not self.test_admin_authentication():
            print("❌ CRITICAL: Admin authentication failed - cannot proceed with other tests")
            return False
            
        # Run all admin functionality tests
        tests = [
            self.test_admin_dashboard_statistics,
            self.test_admin_practices_list,
            self.test_admin_search_functionality,
            self.test_database_connectivity
        ]
        
        passed_tests = 0
        total_tests = len(tests) + 1  # +1 for authentication test
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Add authentication test to passed count
        passed_tests += 1
        
        print("=" * 60)
        print("🔍 ADMIN SYSTEM TEST RESULTS")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Analyze critical issues
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and "CRITICAL" in result["error"]:
                critical_issues.append(result)
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['error']}")
            print()
        
        # Summary
        if success_rate >= 90:
            print("✅ ADMIN SYSTEM STATUS: OPERATIONAL")
        elif success_rate >= 70:
            print("⚠️ ADMIN SYSTEM STATUS: DEGRADED - Some issues detected")
        else:
            print("❌ ADMIN SYSTEM STATUS: CRITICAL FAILURE - Multiple issues detected")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = AdminSystemTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n🚨 ADMIN SYSTEM REQUIRES IMMEDIATE ATTENTION")
        print("Business operations may be impacted.")
        sys.exit(1)
    else:
        print("\n✅ ADMIN SYSTEM VERIFICATION COMPLETE")
        sys.exit(0)