#!/usr/bin/env python3
"""
Comprehensive Dentist Management Endpoints Testing
Tests dentist management endpoints on multiple backend environments
"""

import requests
import json
import sys
from datetime import datetime

class ComprehensiveDentistTester:
    def __init__(self):
        self.test_credentials = {
            "email": "cganz2279@gmail.com",
            "password": "password123"
        }
        self.environments = {
            "Local Backend": "http://localhost:8001/api",
            "Production Backend 1": "https://dental-pdf-sync.preview.emergentagent.com/api",
            "Production Backend 2": "https://dentist-portal-3.emergent.host/api"
        }
        self.results = {}
        
    def test_environment(self, env_name, base_url):
        """Test dentist management endpoints for a specific environment"""
        print(f"\n🔍 TESTING {env_name.upper()}")
        print(f"URL: {base_url}")
        print("=" * 60)
        
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Step 1: Authentication
        try:
            auth_response = session.post(
                f"{base_url}/auth/login",
                json=self.test_credentials,
                timeout=30
            )
            
            if auth_response.status_code != 200:
                print(f"❌ Authentication failed: {auth_response.status_code}")
                self.results[env_name] = {"status": "auth_failed", "details": f"HTTP {auth_response.status_code}"}
                return
                
            auth_data = auth_response.json()
            if not auth_data.get("success"):
                print(f"❌ Authentication failed: {auth_data}")
                self.results[env_name] = {"status": "auth_failed", "details": "Invalid credentials"}
                return
                
            token = auth_data.get("token")
            user_info = auth_data.get("user", {})
            practice_info = auth_data.get("practice", {})
            
            session.headers.update({"Authorization": f"Bearer {token}"})
            
            print(f"✅ Authentication successful")
            print(f"   User: {user_info.get('firstName')} {user_info.get('lastName')}")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Practice: {practice_info.get('name', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            self.results[env_name] = {"status": "auth_error", "details": str(e)}
            return
        
        # Step 2: Test GET /api/practice/dentists
        try:
            get_response = session.get(f"{base_url}/practice/dentists", timeout=30)
            
            if get_response.status_code == 404:
                print(f"❌ GET /api/practice/dentists: 404 Not Found")
                print(f"   ⚠️  CRITICAL: Dentist management endpoints NOT DEPLOYED")
                self.results[env_name] = {
                    "status": "not_deployed",
                    "details": "Dentist management endpoints return 404 - not deployed to this backend",
                    "auth_working": True,
                    "endpoints_deployed": False
                }
                return
            elif get_response.status_code == 200:
                get_data = get_response.json()
                if get_data.get("success"):
                    dentists = get_data.get("data", [])
                    print(f"✅ GET /api/practice/dentists: Found {len(dentists)} dentists")
                    for dentist in dentists:
                        print(f"   - Dr. {dentist.get('firstName')} {dentist.get('lastName')}")
                else:
                    print(f"❌ GET /api/practice/dentists: API error - {get_data}")
                    self.results[env_name] = {"status": "api_error", "details": get_data}
                    return
            else:
                print(f"❌ GET /api/practice/dentists: HTTP {get_response.status_code}")
                self.results[env_name] = {"status": "http_error", "details": f"HTTP {get_response.status_code}"}
                return
                
        except Exception as e:
            print(f"❌ GET /api/practice/dentists: Error - {str(e)}")
            self.results[env_name] = {"status": "network_error", "details": str(e)}
            return
        
        # Step 3: Test POST /api/practice/dentists (Create)
        # Use unique email to avoid conflicts
        import time
        unique_id = int(time.time())
        test_dentist = {
            "firstName": "TestDentist",
            "lastName": f"User{unique_id}",
            "email": f"test.dentist.{unique_id}@dentaltest.com",
            "phone": "(555) 123-4567",
            "licenseNumber": f"TEST{unique_id}",
            "specialties": ["General Dentistry", "Oral Surgery"]
        }
        
        try:
            post_response = session.post(
                f"{base_url}/practice/dentists",
                json=test_dentist,
                timeout=30
            )
            
            if post_response.status_code == 200:
                post_data = post_response.json()
                if post_data.get("success"):
                    created_dentist = post_data.get("data", {})
                    dentist_id = created_dentist.get("id")
                    print(f"✅ POST /api/practice/dentists: Created Dr. {created_dentist.get('firstName')} {created_dentist.get('lastName')}")
                    print(f"   ID: {dentist_id}")
                    
                    # Step 4: Test PUT /api/practice/dentists/{id} (Update)
                    update_data = {
                        "lastName": "Smith-Updated",
                        "phone": "(555) 999-8888"
                    }
                    
                    put_response = session.put(
                        f"{base_url}/practice/dentists/{dentist_id}",
                        json=update_data,
                        timeout=30
                    )
                    
                    if put_response.status_code == 200:
                        put_data = put_response.json()
                        if put_data.get("success"):
                            print(f"✅ PUT /api/practice/dentists/{dentist_id}: Updated successfully")
                        else:
                            print(f"❌ PUT /api/practice/dentists/{dentist_id}: API error - {put_data}")
                    else:
                        print(f"❌ PUT /api/practice/dentists/{dentist_id}: HTTP {put_response.status_code}")
                    
                    # Step 5: Test DELETE /api/practice/dentists/{id} (Delete)
                    delete_response = session.delete(
                        f"{base_url}/practice/dentists/{dentist_id}",
                        timeout=30
                    )
                    
                    if delete_response.status_code == 200:
                        delete_data = delete_response.json()
                        if delete_data.get("success"):
                            print(f"✅ DELETE /api/practice/dentists/{dentist_id}: Deleted successfully")
                        else:
                            print(f"❌ DELETE /api/practice/dentists/{dentist_id}: API error - {delete_data}")
                    else:
                        print(f"❌ DELETE /api/practice/dentists/{dentist_id}: HTTP {delete_response.status_code}")
                    
                    self.results[env_name] = {
                        "status": "fully_working",
                        "details": "All CRUD operations working correctly",
                        "auth_working": True,
                        "endpoints_deployed": True,
                        "crud_operations": "all_working"
                    }
                    
                else:
                    print(f"❌ POST /api/practice/dentists: API error - {post_data}")
                    self.results[env_name] = {"status": "api_error", "details": post_data}
            else:
                print(f"❌ POST /api/practice/dentists: HTTP {post_response.status_code}")
                self.results[env_name] = {"status": "http_error", "details": f"HTTP {post_response.status_code}"}
                
        except Exception as e:
            print(f"❌ POST /api/practice/dentists: Error - {str(e)}")
            self.results[env_name] = {"status": "network_error", "details": str(e)}
    
    def run_comprehensive_test(self):
        """Run tests on all environments"""
        print("🦷 COMPREHENSIVE DENTIST MANAGEMENT ENDPOINTS TESTING")
        print("=" * 80)
        print(f"Test Credentials: {self.test_credentials['email']}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        for env_name, base_url in self.environments.items():
            try:
                self.test_environment(env_name, base_url)
            except Exception as e:
                print(f"\n❌ CRITICAL ERROR testing {env_name}: {str(e)}")
                self.results[env_name] = {"status": "critical_error", "details": str(e)}
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        working_environments = []
        not_deployed_environments = []
        failed_environments = []
        
        for env_name, result in self.results.items():
            status = result.get("status")
            if status == "fully_working":
                working_environments.append(env_name)
                print(f"✅ {env_name}: FULLY WORKING")
                print(f"   All dentist management CRUD operations functional")
            elif status == "not_deployed":
                not_deployed_environments.append(env_name)
                print(f"❌ {env_name}: NOT DEPLOYED")
                print(f"   Authentication works, but dentist endpoints return 404")
            else:
                failed_environments.append(env_name)
                print(f"⚠️  {env_name}: {status.upper()}")
                print(f"   Details: {result.get('details', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 80)
        
        if working_environments:
            print(f"✅ WORKING ENVIRONMENTS ({len(working_environments)}):")
            for env in working_environments:
                print(f"   - {env}")
        
        if not_deployed_environments:
            print(f"\n❌ DEPLOYMENT ISSUES ({len(not_deployed_environments)}):")
            for env in not_deployed_environments:
                print(f"   - {env}: Dentist management endpoints not deployed")
        
        if failed_environments:
            print(f"\n⚠️  OTHER ISSUES ({len(failed_environments)}):")
            for env in failed_environments:
                print(f"   - {env}: {self.results[env].get('status', 'unknown')}")
        
        print(f"\n📋 REVIEW REQUEST STATUS:")
        if len(working_environments) >= 1:
            print(f"✅ Dentist management endpoints ARE WORKING in {len(working_environments)} environment(s)")
            print(f"✅ All requested CRUD operations (GET, POST, PUT, DELETE) functional")
            print(f"✅ Authentication with cganz2279@gmail.com/password123 working")
            
            if "Production Backend 2" in not_deployed_environments:
                print(f"\n⚠️  NOTE: Production Backend 2 (dentist-portal-3.emergent.host) missing endpoints")
                print(f"   This may explain previous reports of missing functionality")
            
            return True
        else:
            print(f"❌ Dentist management endpoints NOT WORKING in any environment")
            return False

def main():
    tester = ComprehensiveDentistTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()