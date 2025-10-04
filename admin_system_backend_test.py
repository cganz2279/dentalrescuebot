#!/usr/bin/env python3

"""
ADMIN SYSTEM INVESTIGATION - Backend Testing
Critical: Admin system not working - no practices listed, admin program broken.
Need immediate investigation and fixes.
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_admin_authentication():
    """Test Admin Authentication - login with admin credentials"""
    log_test("🔐 TESTING ADMIN AUTHENTICATION")
    
    # Test admin login endpoint
    login_url = f"{BACKEND_URL}/api/admin/login"
    
    # Admin credentials from the code
    admin_credentials = {
        "email": "cganz@admin.com",
        "password": "Dentist1#"
    }
    
    try:
        log_test(f"POST {login_url}")
        log_test(f"Credentials: {admin_credentials['email']} / {admin_credentials['password']}")
        
        response = requests.post(login_url, json=admin_credentials, timeout=30)
        log_test(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ Admin login successful")
            log_test(f"Response: {json.dumps(data, indent=2)}")
            
            if 'token' in data:
                admin_token = data['token']
                log_test(f"🎯 Admin token obtained: {admin_token[:50]}...")
                return admin_token
            else:
                log_test("❌ No token in response")
                return None
        else:
            log_test(f"❌ Admin login failed: {response.status_code}")
            log_test(f"Response: {response.text}")
            return None
            
    except Exception as e:
        log_test(f"❌ Admin login error: {e}")
        return None

def test_admin_dashboard(admin_token):
    """Test Admin Dashboard - check if admin can see dashboard data"""
    log_test("📊 TESTING ADMIN DASHBOARD")
    
    if not admin_token:
        log_test("❌ No admin token available for dashboard test")
        return False
    
    dashboard_url = f"{BACKEND_URL}/api/admin/dashboard"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        log_test(f"GET {dashboard_url}")
        response = requests.get(dashboard_url, headers=headers, timeout=30)
        log_test(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ Admin dashboard accessible")
            
            if 'stats' in data:
                stats = data['stats']
                log_test(f"📈 Dashboard Stats:")
                log_test(f"  - Total Practices: {stats.get('total_practices', 'N/A')}")
                log_test(f"  - Active Practices: {stats.get('active_practices', 'N/A')}")
                log_test(f"  - Trial Practices: {stats.get('trial_practices', 'N/A')}")
                log_test(f"  - Total Revenue: ${stats.get('total_revenue', 'N/A')}")
                
                if stats.get('total_practices', 0) > 0:
                    log_test("✅ Practices found in dashboard")
                else:
                    log_test("⚠️ No practices found in dashboard")
            
            if 'recent_practices' in data:
                recent = data['recent_practices']
                log_test(f"📋 Recent Practices: {len(recent)} found")
                for i, practice in enumerate(recent[:3]):  # Show first 3
                    log_test(f"  {i+1}. {practice.get('name', 'Unknown')} - {practice.get('email', 'No email')}")
            
            return True
        else:
            log_test(f"❌ Dashboard access failed: {response.status_code}")
            log_test(f"Response: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Dashboard error: {e}")
        return False

def test_admin_practices_list(admin_token):
    """Test Admin Practices List - GET /api/admin/practices"""
    log_test("📋 TESTING ADMIN PRACTICES LIST")
    
    if not admin_token:
        log_test("❌ No admin token available for practices list test")
        return False
    
    practices_url = f"{BACKEND_URL}/api/admin/practices"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        log_test(f"GET {practices_url}")
        response = requests.get(practices_url, headers=headers, timeout=30)
        log_test(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ Admin practices list accessible")
            
            if 'practices' in data:
                practices = data['practices']
                log_test(f"📊 Found {len(practices)} practices")
                
                if len(practices) > 0:
                    log_test("✅ PRACTICES FOUND - Admin can see practice listings")
                    
                    # Show details of first few practices
                    for i, practice in enumerate(practices[:5]):
                        log_test(f"  Practice {i+1}:")
                        log_test(f"    - Name: {practice.get('name', 'Unknown')}")
                        log_test(f"    - Email: {practice.get('email', 'No email')}")
                        log_test(f"    - Status: {practice.get('subscription', {}).get('status', 'Unknown')}")
                        log_test(f"    - ID: {practice.get('id', 'No ID')}")
                        
                        # Check if admin user info is included
                        if 'admin_user' in practice and practice['admin_user']:
                            admin_user = practice['admin_user']
                            log_test(f"    - Admin: {admin_user.get('firstName', '')} {admin_user.get('lastName', '')} ({admin_user.get('email', '')})")
                else:
                    log_test("❌ CRITICAL: NO PRACTICES LISTED - This is the reported issue!")
                    
            if 'pagination' in data:
                pagination = data['pagination']
                log_test(f"📄 Pagination: {pagination.get('total', 0)} total practices")
            
            return len(practices) > 0
        else:
            log_test(f"❌ Practices list access failed: {response.status_code}")
            log_test(f"Response: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Practices list error: {e}")
        return False

def test_admin_endpoints(admin_token):
    """Test all /api/admin/* endpoints"""
    log_test("🔍 TESTING ALL ADMIN ENDPOINTS")
    
    if not admin_token:
        log_test("❌ No admin token available for endpoint tests")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # List of admin endpoints to test
    endpoints = [
        "/api/admin/dashboard",
        "/api/admin/practices",
        "/api/admin/monitoring",
        "/api/admin/payments",
        "/api/admin/registration-attempts",
        "/api/admin/procedure-requests",
        "/api/admin/procedures"
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints)
    
    for endpoint in endpoints:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            log_test(f"Testing: GET {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                log_test(f"  ✅ {endpoint} - Working")
                working_endpoints += 1
            elif response.status_code == 401:
                log_test(f"  🔐 {endpoint} - Auth required (expected)")
                working_endpoints += 1  # This is expected behavior
            elif response.status_code == 403:
                log_test(f"  🚫 {endpoint} - Forbidden (token issue)")
            else:
                log_test(f"  ❌ {endpoint} - Failed ({response.status_code})")
                
        except Exception as e:
            log_test(f"  ❌ {endpoint} - Error: {e}")
    
    log_test(f"📊 Admin Endpoints Summary: {working_endpoints}/{total_endpoints} working")
    return working_endpoints > 0

def test_admin_database_access(admin_token):
    """Test Admin Database Access - verify admin can access practices collection"""
    log_test("🗄️ TESTING ADMIN DATABASE ACCESS")
    
    if not admin_token:
        log_test("❌ No admin token available for database access test")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test monitoring endpoint which shows database statistics
    monitoring_url = f"{BACKEND_URL}/api/admin/monitoring"
    
    try:
        log_test(f"GET {monitoring_url}")
        response = requests.get(monitoring_url, headers=headers, timeout=30)
        log_test(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ Admin database access working")
            
            if 'system_stats' in data:
                stats = data['system_stats']
                log_test(f"📊 Database Statistics:")
                log_test(f"  - Total Practices: {stats.get('total_practices', 'N/A')}")
                log_test(f"  - Active Practices: {stats.get('active_practices', 'N/A')}")
                log_test(f"  - Total Users: {stats.get('total_users', 'N/A')}")
                log_test(f"  - Total Patients: {stats.get('total_patients', 'N/A')}")
                log_test(f"  - Active Procedures: {stats.get('active_procedures', 'N/A')}")
                
                if stats.get('total_practices', 0) > 0:
                    log_test("✅ Admin can access practices collection")
                    return True
                else:
                    log_test("❌ No practices found in database")
                    return False
            else:
                log_test("❌ No system stats in monitoring response")
                return False
        else:
            log_test(f"❌ Monitoring access failed: {response.status_code}")
            log_test(f"Response: {response.text}")
            return False
            
    except Exception as e:
        log_test(f"❌ Database access error: {e}")
        return False

def test_admin_practice_management(admin_token):
    """Test Admin Practice Management functionality"""
    log_test("⚙️ TESTING ADMIN PRACTICE MANAGEMENT")
    
    if not admin_token:
        log_test("❌ No admin token available for practice management test")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # First, get a practice to test management on
    practices_url = f"{BACKEND_URL}/api/admin/practices"
    
    try:
        response = requests.get(practices_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            practices = data.get('practices', [])
            
            if len(practices) > 0:
                test_practice = practices[0]
                practice_id = test_practice.get('id')
                practice_name = test_practice.get('name', 'Unknown')
                
                log_test(f"🎯 Testing management on practice: {practice_name} ({practice_id})")
                
                # Test getting practice users
                users_url = f"{BACKEND_URL}/api/admin/users/{practice_id}"
                users_response = requests.get(users_url, headers=headers, timeout=30)
                
                if users_response.status_code == 200:
                    users_data = users_response.json()
                    users = users_data.get('users', [])
                    log_test(f"✅ Practice users accessible: {len(users)} users found")
                    
                    for user in users[:3]:  # Show first 3 users
                        log_test(f"  - {user.get('firstName', '')} {user.get('lastName', '')} ({user.get('email', '')}) - {user.get('role', 'Unknown role')}")
                else:
                    log_test(f"❌ Practice users access failed: {users_response.status_code}")
                
                return True
            else:
                log_test("❌ No practices available for management testing")
                return False
        else:
            log_test(f"❌ Could not get practices for management test: {response.status_code}")
            return False
            
    except Exception as e:
        log_test(f"❌ Practice management test error: {e}")
        return False

def run_comprehensive_admin_test():
    """Run comprehensive admin system investigation"""
    log_test("🚀 STARTING COMPREHENSIVE ADMIN SYSTEM INVESTIGATION")
    log_test("=" * 80)
    
    # Test results tracking
    test_results = {
        'admin_authentication': False,
        'admin_dashboard': False,
        'admin_practices_list': False,
        'admin_endpoints': False,
        'admin_database_access': False,
        'admin_practice_management': False
    }
    
    # 1. Test Admin Authentication
    admin_token = test_admin_authentication()
    test_results['admin_authentication'] = admin_token is not None
    
    if admin_token:
        # 2. Test Admin Dashboard
        test_results['admin_dashboard'] = test_admin_dashboard(admin_token)
        
        # 3. Test Admin Practices List (CRITICAL)
        test_results['admin_practices_list'] = test_admin_practices_list(admin_token)
        
        # 4. Test Admin Endpoints
        test_results['admin_endpoints'] = test_admin_endpoints(admin_token)
        
        # 5. Test Admin Database Access
        test_results['admin_database_access'] = test_admin_database_access(admin_token)
        
        # 6. Test Admin Practice Management
        test_results['admin_practice_management'] = test_admin_practice_management(admin_token)
    
    # Summary
    log_test("=" * 80)
    log_test("🎯 ADMIN SYSTEM INVESTIGATION SUMMARY")
    log_test("=" * 80)
    
    for test_name, result in test_results.items():
        status = "✅ WORKING" if result else "❌ FAILED"
        log_test(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Critical findings
    log_test("\n🚨 CRITICAL FINDINGS:")
    
    if not test_results['admin_authentication']:
        log_test("❌ CRITICAL: Admin authentication is broken - cannot login")
    
    if not test_results['admin_practices_list']:
        log_test("❌ CRITICAL: Admin cannot see practice listings - THIS IS THE REPORTED ISSUE!")
    
    if not test_results['admin_database_access']:
        log_test("❌ CRITICAL: Admin cannot access database - data access broken")
    
    # Success criteria check
    working_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    log_test(f"\n📊 OVERALL RESULT: {working_tests}/{total_tests} tests passed")
    
    if working_tests == total_tests:
        log_test("🎉 ALL ADMIN FUNCTIONALITY WORKING")
    elif test_results['admin_authentication'] and test_results['admin_practices_list']:
        log_test("✅ CORE ADMIN FUNCTIONALITY WORKING")
    else:
        log_test("🚨 ADMIN SYSTEM HAS CRITICAL ISSUES")
    
    return test_results

if __name__ == "__main__":
    run_comprehensive_admin_test()