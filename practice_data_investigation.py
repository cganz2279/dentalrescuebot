#!/usr/bin/env python3
"""
Practice Data Investigation Script
Detailed investigation of practice data flow for PDF generation
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://admin-panel-debug-5.preview.emergentagent.com/api"

class PracticeDataInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.practice_data = {}
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        print("🔐 Authenticating with cganz2279@gmail.com/password123...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": "cganz2279@gmail.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.jwt_token = data["token"]
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.jwt_token}"
                    })
                    
                    print("✅ Authentication successful")
                    print(f"   User: {data.get('user', {}).get('email')}")
                    print(f"   Role: {data.get('user', {}).get('role')}")
                    print(f"   Practice: {data.get('user', {}).get('practiceName', 'N/A')}")
                    print()
                    return True
                else:
                    print(f"❌ Login successful but no token in response: {data}")
                    return False
            else:
                print(f"❌ Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication request failed: {str(e)}")
            return False
    
    def investigate_login_response(self):
        """Investigate what practice data is available in login response"""
        print("🔍 Investigating Login Response...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": "cganz2279@gmail.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Login Response Analysis:")
                print(f"   Full Response Keys: {list(data.keys())}")
                
                user_data = data.get('user', {})
                print(f"   User Data Keys: {list(user_data.keys())}")
                
                # Check for practice-related fields in user data
                practice_fields = ['practiceName', 'practiceId', 'officeHours', 'emergencyContact', 'practicePhone', 'practiceAddress']
                found_practice_fields = {}
                
                for field in practice_fields:
                    if field in user_data:
                        found_practice_fields[field] = user_data[field]
                
                if found_practice_fields:
                    print("   Practice Fields in Login Response:")
                    for field, value in found_practice_fields.items():
                        print(f"     {field}: {value}")
                else:
                    print("   ❌ No practice fields found in login response")
                
                print()
                return found_practice_fields
            else:
                print(f"❌ Login failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Login investigation failed: {str(e)}")
            return {}
    
    def investigate_practice_dashboard(self):
        """Investigate practice dashboard API for complete practice data"""
        print("🏥 Investigating Practice Dashboard API...")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return {}
            
        try:
            response = self.session.get(f"{BACKEND_URL}/practice/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Practice Dashboard Response Analysis:")
                print(f"   Response Structure: {list(data.keys())}")
                
                if data.get("success"):
                    dashboard_data = data.get("data", {})
                    print(f"   Dashboard Data Keys: {list(dashboard_data.keys())}")
                    
                    practice_data = dashboard_data.get("practice", {})
                    if practice_data:
                        print(f"   Practice Object Keys: {list(practice_data.keys())}")
                        
                        # Extract key practice information
                        practice_info = {
                            'name': practice_data.get('name'),
                            'phone': practice_data.get('phone'),
                            'website': practice_data.get('website'),
                            'officeHours': practice_data.get('officeHours'),
                            'emergencyContact': practice_data.get('emergencyContact'),
                            'address': practice_data.get('address')
                        }
                        
                        print("   Practice Information Available:")
                        for field, value in practice_info.items():
                            status = "✅" if value else "❌"
                            print(f"     {status} {field}: {value}")
                        
                        self.practice_data = practice_info
                        print()
                        return practice_info
                    else:
                        print("   ❌ No practice object in dashboard data")
                        return {}
                else:
                    print(f"   ❌ Dashboard API returned success=false: {data}")
                    return {}
            else:
                print(f"❌ Dashboard API failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Dashboard investigation failed: {str(e)}")
            return {}
    
    def investigate_procedure_api(self):
        """Investigate procedure API to see if practice data is included"""
        print("🦷 Investigating Procedure API...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/procedures/root-canal-therapy")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Procedure API Response Analysis:")
                
                procedure_data = data.get("data", {}) if data.get("success") else data
                print(f"   Procedure Data Keys: {list(procedure_data.keys())}")
                
                # Check for practice-related fields
                practice_fields = ['practiceName', 'practicePhone', 'practiceOfficeHours', 'practiceEmergencyContact', 'practiceAddress']
                found_practice_fields = {}
                
                for field in practice_fields:
                    if field in procedure_data:
                        found_practice_fields[field] = procedure_data[field]
                
                if found_practice_fields:
                    print("   Practice Fields in Procedure Response:")
                    for field, value in found_practice_fields.items():
                        print(f"     ✅ {field}: {value}")
                else:
                    print("   ❌ No practice fields found in procedure response")
                    print("   📝 This is EXPECTED - frontend should add practice data during PDF generation")
                
                print()
                return found_practice_fields
            else:
                print(f"❌ Procedure API failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Procedure investigation failed: {str(e)}")
            return {}
    
    def investigate_practice_settings_api(self):
        """Check if there's a separate practice settings endpoint"""
        print("⚙️ Investigating Practice Settings API...")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return {}
            
        # Try different potential endpoints
        endpoints_to_try = [
            "/practice/settings",
            "/practice/info", 
            "/practice/details",
            "/practice/profile"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Found working endpoint: {endpoint}")
                    print(f"   Response: {json.dumps(data, indent=2)}")
                    return data
                elif response.status_code != 404:
                    print(f"   {endpoint}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"   {endpoint}: Error - {str(e)}")
        
        print("   ❌ No separate practice settings endpoint found")
        print("   📝 Practice data should be retrieved via /practice/dashboard")
        print()
        return {}
    
    def analyze_data_flow_issue(self):
        """Analyze the root cause of the data flow issue"""
        print("🔍 ANALYZING DATA FLOW ISSUE...")
        print("=" * 60)
        
        # Check if we have practice data from dashboard
        if not self.practice_data:
            print("❌ CRITICAL: No practice data retrieved from dashboard API")
            return
        
        office_hours = self.practice_data.get('officeHours')
        emergency_contact = self.practice_data.get('emergencyContact')
        
        print("📊 DATA AVAILABILITY ANALYSIS:")
        print(f"   Office Hours Available: {'✅ YES' if office_hours else '❌ NO'}")
        if office_hours:
            print(f"     Value: '{office_hours}'")
        
        print(f"   Emergency Contact Available: {'✅ YES' if emergency_contact else '❌ NO'}")
        if emergency_contact:
            print(f"     Value: '{emergency_contact}'")
        
        print()
        print("🎯 ROOT CAUSE ANALYSIS:")
        
        if office_hours and emergency_contact:
            print("✅ BACKEND DATA: Practice information is available in backend")
            print("✅ API ENDPOINT: /api/practice/dashboard provides complete practice data")
            print("❌ FRONTEND ISSUE: The problem is likely in the frontend data flow:")
            print("   1. Frontend may not be calling /api/practice/dashboard to get practice data")
            print("   2. Frontend may not be storing practice data in context/state")
            print("   3. PDF generator may not be accessing the practice data from context")
            print("   4. Practice data may not be passed to PDF generation function")
            
            print()
            print("🔧 RECOMMENDED SOLUTION:")
            print("   1. Ensure frontend calls /api/practice/dashboard on login/app load")
            print("   2. Store practice data in React context or state management")
            print("   3. Pass practice data to PDF generator component")
            print("   4. Include practice.officeHours and practice.emergencyContact in PDF")
            
        else:
            print("❌ BACKEND DATA MISSING: Practice information is not properly configured")
            print("🔧 SOLUTION: Update practice settings to include Office Hours and Emergency Contact")
        
        print()
    
    def run_investigation(self):
        """Run complete investigation"""
        print("🚀 STARTING PRACTICE DATA INVESTIGATION")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Investigation failed - cannot authenticate")
            return False
        
        # Step 2: Check login response for practice data
        login_practice_data = self.investigate_login_response()
        
        # Step 3: Check practice dashboard API
        dashboard_practice_data = self.investigate_practice_dashboard()
        
        # Step 4: Check procedure API
        procedure_practice_data = self.investigate_procedure_api()
        
        # Step 5: Check for separate practice settings API
        settings_data = self.investigate_practice_settings_api()
        
        # Step 6: Analyze the data flow issue
        self.analyze_data_flow_issue()
        
        print("=" * 60)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        print(f"✅ Authentication: SUCCESS")
        print(f"📊 Login Response Practice Fields: {len(login_practice_data)} found")
        print(f"📊 Dashboard Practice Fields: {len(dashboard_practice_data)} found")
        print(f"📊 Procedure Practice Fields: {len(procedure_practice_data)} found")
        print(f"📊 Settings API: {'Found' if settings_data else 'Not found'}")
        
        office_hours_available = bool(dashboard_practice_data.get('officeHours'))
        emergency_contact_available = bool(dashboard_practice_data.get('emergencyContact'))
        
        print()
        print("🎯 KEY FINDINGS:")
        print(f"   Office Hours in Backend: {'✅ YES' if office_hours_available else '❌ NO'}")
        print(f"   Emergency Contact in Backend: {'✅ YES' if emergency_contact_available else '❌ NO'}")
        
        if office_hours_available and emergency_contact_available:
            print("   🎉 BACKEND IS READY - Issue is in frontend data flow")
        else:
            print("   ⚠️  BACKEND CONFIGURATION NEEDED")
        
        return True

if __name__ == "__main__":
    investigator = PracticeDataInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)