#!/usr/bin/env python3
"""
Login System Persistence Test
Testing both regular login and admin login endpoints for persistence and consistency
"""

import requests
import json
import time
import subprocess
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BACKEND_URL = "https://postopcare-1.preview.emergentagent.com/api"

# Test credentials
REGULAR_LOGIN_CREDENTIALS = {
    "email": "cganz2279@gmail.com",
    "password": "password123"
}

ADMIN_LOGIN_CREDENTIALS = {
    "email": "cganz@admin.com", 
    "password": "Dentist1#"
}

def test_regular_login(attempt_number: int = 1) -> Dict[str, Any]:
    """Test regular login endpoint"""
    print(f"🔐 TEST {attempt_number}: Testing Regular Login (/api/auth/login)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=REGULAR_LOGIN_CREDENTIALS,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if data.get('success') and data.get('token') and data.get('user'):
                user = data['user']
                practice = data.get('practice')
                
                print(f"   ✅ Login successful")
                print(f"   📧 User: {user.get('firstName')} {user.get('lastName')} ({user.get('email')})")
                print(f"   🏥 Practice: {practice.get('name') if practice else 'No practice'}")
                print(f"   🎫 Token: {data['token'][:20]}...")
                print(f"   👤 Role: {user.get('role')}")
                print(f"   ✅ Active: {user.get('isActive')}")
                
                return {
                    "success": True,
                    "token": data['token'],
                    "user": user,
                    "practice": practice,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                print(f"   ❌ FAIL: Invalid response structure")
                print(f"   Response: {data}")
                return {"success": False, "error": "Invalid response structure"}
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
                return {"success": False, "error": error_data}
            except:
                print(f"   Error: {response.text}")
                return {"success": False, "error": response.text}
                
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return {"success": False, "error": str(e)}

def test_admin_login(attempt_number: int = 1) -> Dict[str, Any]:
    """Test admin login endpoint"""
    print(f"🔐 TEST {attempt_number}: Testing Admin Login (/api/admin/login)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/login",
            json=ADMIN_LOGIN_CREDENTIALS,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if data.get('success') and data.get('token'):
                print(f"   ✅ Admin login successful")
                print(f"   📧 Admin: {data.get('admin', {}).get('email', 'N/A')}")
                print(f"   🎫 Token: {data['token'][:20]}...")
                print(f"   👑 Role: {data.get('admin', {}).get('role', 'N/A')}")
                
                return {
                    "success": True,
                    "token": data['token'],
                    "admin": data.get('admin'),
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                print(f"   ❌ FAIL: Invalid response structure")
                print(f"   Response: {data}")
                return {"success": False, "error": "Invalid response structure"}
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
                return {"success": False, "error": error_data}
            except:
                print(f"   Error: {response.text}")
                return {"success": False, "error": response.text}
                
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return {"success": False, "error": str(e)}

def test_token_validation(token: str, endpoint_type: str) -> bool:
    """Test if JWT token is valid by making an authenticated request"""
    print(f"🎫 Testing {endpoint_type} token validation...")
    
    try:
        if endpoint_type == "regular":
            # Test with /api/auth/me endpoint
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
        else:  # admin
            # Test with /api/admin/dashboard endpoint
            response = requests.get(
                f"{BACKEND_URL}/admin/dashboard",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
        
        print(f"   Token validation status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Token is valid and working")
            return True
        else:
            print(f"   ❌ Token validation failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Token validation error: {str(e)}")
        return False

def check_service_status() -> Dict[str, Any]:
    """Check if all services are running properly"""
    print("🔧 Checking service status...")
    
    try:
        # Check supervisorctl status
        result = subprocess.run(
            ["sudo", "supervisorctl", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"   Supervisor status output:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
        
        # Check if backend and frontend are running
        backend_running = "backend" in result.stdout and "RUNNING" in result.stdout
        frontend_running = "frontend" in result.stdout and "RUNNING" in result.stdout
        
        # Check backend logs for any errors
        backend_logs = subprocess.run(
            ["sudo", "tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print(f"   Recent backend error logs:")
        if backend_logs.stdout.strip():
            for line in backend_logs.stdout.split('\n')[-5:]:  # Last 5 lines
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"   No recent backend errors")
        
        return {
            "backend_running": backend_running,
            "frontend_running": frontend_running,
            "supervisor_output": result.stdout,
            "backend_errors": backend_logs.stdout
        }
        
    except Exception as e:
        print(f"   ❌ Service check error: {str(e)}")
        return {"error": str(e)}

def check_cron_job() -> bool:
    """Check if cron job for service monitoring is active"""
    print("⏰ Checking cron job status...")
    
    try:
        # Check if there are any cron jobs related to service monitoring
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            cron_jobs = result.stdout
            print(f"   Current cron jobs:")
            for line in cron_jobs.split('\n'):
                if line.strip():
                    print(f"   {line}")
            
            # Look for service monitoring related cron jobs
            service_monitoring = any("supervisor" in line.lower() or "service" in line.lower() 
                                   for line in cron_jobs.split('\n'))
            
            if service_monitoring:
                print(f"   ✅ Service monitoring cron job found")
                return True
            else:
                print(f"   ⚠️  No service monitoring cron job found")
                return False
        else:
            print(f"   ⚠️  No cron jobs found or crontab not accessible")
            return False
            
    except Exception as e:
        print(f"   ❌ Cron check error: {str(e)}")
        return False

def run_multiple_login_tests(num_tests: int = 5) -> Dict[str, Any]:
    """Run multiple login tests to ensure consistency"""
    print(f"🔄 Running {num_tests} consecutive login tests for consistency...")
    
    regular_results = []
    admin_results = []
    
    for i in range(1, num_tests + 1):
        print(f"\n--- Test Round {i}/{num_tests} ---")
        
        # Test regular login
        regular_result = test_regular_login(i)
        regular_results.append(regular_result)
        
        # Small delay between tests
        time.sleep(1)
        
        # Test admin login
        admin_result = test_admin_login(i)
        admin_results.append(admin_result)
        
        # Test token validation if login was successful
        if regular_result.get('success') and regular_result.get('token'):
            test_token_validation(regular_result['token'], "regular")
        
        if admin_result.get('success') and admin_result.get('token'):
            test_token_validation(admin_result['token'], "admin")
        
        # Small delay between rounds
        time.sleep(2)
    
    # Analyze results
    regular_success_count = sum(1 for r in regular_results if r.get('success'))
    admin_success_count = sum(1 for r in admin_results if r.get('success'))
    
    regular_avg_time = sum(r.get('response_time', 0) for r in regular_results if r.get('success')) / max(regular_success_count, 1)
    admin_avg_time = sum(r.get('response_time', 0) for r in admin_results if r.get('success')) / max(admin_success_count, 1)
    
    return {
        "total_tests": num_tests,
        "regular_login": {
            "success_count": regular_success_count,
            "success_rate": (regular_success_count / num_tests) * 100,
            "avg_response_time": regular_avg_time,
            "results": regular_results
        },
        "admin_login": {
            "success_count": admin_success_count,
            "success_rate": (admin_success_count / num_tests) * 100,
            "avg_response_time": admin_avg_time,
            "results": admin_results
        }
    }

def run_login_persistence_test():
    """Run comprehensive login persistence test"""
    print("🚀 LOGIN SYSTEM PERSISTENCE TEST")
    print("=" * 80)
    
    # Step 1: Check service status
    service_status = check_service_status()
    
    # Step 2: Check cron job
    cron_active = check_cron_job()
    
    # Step 3: Run multiple login tests
    test_results = run_multiple_login_tests(5)
    
    # Step 4: Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 80)
    
    # Service status
    print(f"🔧 SERVICE STATUS:")
    if service_status.get('backend_running'):
        print(f"   ✅ Backend service: RUNNING")
    else:
        print(f"   ❌ Backend service: NOT RUNNING")
    
    if service_status.get('frontend_running'):
        print(f"   ✅ Frontend service: RUNNING")
    else:
        print(f"   ❌ Frontend service: NOT RUNNING")
    
    # Cron job status
    print(f"⏰ CRON JOB STATUS:")
    if cron_active:
        print(f"   ✅ Service monitoring cron job: ACTIVE")
    else:
        print(f"   ⚠️  Service monitoring cron job: NOT FOUND")
    
    # Login test results
    print(f"🔐 LOGIN TEST RESULTS:")
    regular_stats = test_results['regular_login']
    admin_stats = test_results['admin_login']
    
    print(f"   Regular Login (/api/auth/login):")
    print(f"   - Success Rate: {regular_stats['success_rate']:.1f}% ({regular_stats['success_count']}/{test_results['total_tests']})")
    print(f"   - Avg Response Time: {regular_stats['avg_response_time']:.3f}s")
    
    print(f"   Admin Login (/api/admin/login):")
    print(f"   - Success Rate: {admin_stats['success_rate']:.1f}% ({admin_stats['success_count']}/{test_results['total_tests']})")
    print(f"   - Avg Response Time: {admin_stats['avg_response_time']:.3f}s")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    
    services_ok = service_status.get('backend_running', False) and service_status.get('frontend_running', False)
    regular_login_ok = regular_stats['success_rate'] >= 80
    admin_login_ok = admin_stats['success_rate'] >= 80
    
    if services_ok and regular_login_ok and admin_login_ok:
        print(f"   ✅ LOGIN SYSTEM PERSISTENCE: WORKING")
        print(f"   ✅ Both login endpoints are functioning consistently")
        print(f"   ✅ Services are running and stable")
        if cron_active:
            print(f"   ✅ Service monitoring is active")
        return True
    else:
        print(f"   ❌ LOGIN SYSTEM PERSISTENCE: ISSUES FOUND")
        if not services_ok:
            print(f"   ❌ Service issues detected")
        if not regular_login_ok:
            print(f"   ❌ Regular login inconsistent ({regular_stats['success_rate']:.1f}% success rate)")
        if not admin_login_ok:
            print(f"   ❌ Admin login inconsistent ({admin_stats['success_rate']:.1f}% success rate)")
        if not cron_active:
            print(f"   ⚠️  Service monitoring cron job not found")
        return False

if __name__ == "__main__":
    success = run_login_persistence_test()
    exit(0 if success else 1)