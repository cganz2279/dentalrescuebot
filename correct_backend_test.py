#!/usr/bin/env python3
"""
URGENT DATA RECOVERY INVESTIGATION - CORRECTED BACKEND URL
Testing the CORRECT backend URL: https://dentist-portal-3.emergent.host/api
As requested in review to investigate data discrepancy between environments
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# CORRECT Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host"

class CorrectBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.practice_data = None
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the CORRECT backend API"""
        print(f"🔐 Authenticating with {email} on CORRECT backend...")
        print(f"   Backend URL: {self.base_url}/api/auth/login")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.practice_data = data.get("practice", {})
                
                print(f"✅ Authentication successful on CORRECT backend!")
                print(f"   Practice: {self.practice_data.get('name', 'Unknown')}")
                print(f"   Role: {data.get('role', 'Unknown')}")
                print(f"   User ID: {data.get('userId', 'Unknown')}")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_practice_patients(self) -> Dict[str, Any]:
        """Test GET /api/practice/patients - are there patients here?"""
        print(f"\n🏥 TESTING PRACTICE PATIENTS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/practice/patients", timeout=30)
            
            print(f"GET /api/practice/patients - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patients = data.get("data", [])
                    print(f"✅ SUCCESS: Found {len(patients)} patients")
                    
                    if patients:
                        print(f"📋 PATIENT SAMPLE:")
                        for i, patient in enumerate(patients[:3], 1):  # Show first 3
                            print(f"   {i}. {patient.get('firstName', 'N/A')} {patient.get('lastName', 'N/A')}")
                            print(f"      Email: {patient.get('email', 'N/A')}")
                            print(f"      Phone: {patient.get('phone', 'N/A')}")
                    
                    return {"success": True, "count": len(patients), "data": patients}
                else:
                    print(f"❌ API returned success=false: {data}")
                    return {"success": False, "error": "API returned success=false"}
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_procedures(self) -> Dict[str, Any]:
        """Test GET /api/procedures - are the 81 procedures available?"""
        print(f"\n🦷 TESTING PROCEDURES")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/procedures", timeout=30)
            
            print(f"GET /api/procedures - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedures = data.get("data", [])
                    print(f"✅ SUCCESS: Found {len(procedures)} procedures")
                    
                    # Count by specialty
                    specialty_counts = {}
                    for proc in procedures:
                        specialty = proc.get('specialtyName', 'Unknown')
                        specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
                    
                    print(f"📊 PROCEDURES BY SPECIALTY:")
                    for specialty, count in sorted(specialty_counts.items()):
                        print(f"   {specialty}: {count} procedures")
                    
                    # Show sample procedures
                    print(f"📋 SAMPLE PROCEDURES:")
                    for i, proc in enumerate(procedures[:5], 1):  # Show first 5
                        print(f"   {i}. {proc.get('name', 'N/A')} ({proc.get('specialtyName', 'N/A')})")
                    
                    return {"success": True, "count": len(procedures), "specialties": specialty_counts}
                else:
                    print(f"❌ API returned success=false: {data}")
                    return {"success": False, "error": "API returned success=false"}
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_practice_dashboard(self) -> Dict[str, Any]:
        """Test GET /api/practice/dashboard - what shows up?"""
        print(f"\n📊 TESTING PRACTICE DASHBOARD")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/practice/dashboard", timeout=30)
            
            print(f"GET /api/practice/dashboard - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    dashboard = data.get("data", {})
                    print(f"✅ SUCCESS: Dashboard data retrieved")
                    
                    # Show key dashboard metrics
                    print(f"📈 DASHBOARD METRICS:")
                    
                    # Practice info
                    practice = dashboard.get('practice', {})
                    if practice:
                        print(f"   Practice Name: {practice.get('name', 'N/A')}")
                        print(f"   Practice Phone: {practice.get('phone', 'N/A')}")
                        print(f"   Office Hours: {practice.get('officeHours', 'N/A')}")
                        print(f"   Emergency Contact: {practice.get('emergencyContact', 'N/A')}")
                    
                    # Stats
                    stats = dashboard.get('stats', {})
                    if stats:
                        print(f"   Total Patients: {stats.get('totalPatients', 'N/A')}")
                        print(f"   Total Dentists: {stats.get('totalDentists', 'N/A')}")
                        print(f"   Total Procedures: {stats.get('totalProcedures', 'N/A')}")
                        print(f"   Recent Assignments: {stats.get('recentAssignments', 'N/A')}")
                    
                    return {"success": True, "data": dashboard}
                else:
                    print(f"❌ API returned success=false: {data}")
                    return {"success": False, "error": "API returned success=false"}
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_create_patient(self) -> Dict[str, Any]:
        """Test if we can create patients on the correct backend"""
        print(f"\n👤 TESTING PATIENT CREATION")
        print("=" * 50)
        
        # Test patient data
        test_patient = {
            "firstName": "Test",
            "lastName": "Patient",
            "email": f"test.patient.{int(__import__('time').time())}@example.com",
            "phone": "555-123-4567",
            "dateOfBirth": "1990-01-01",
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zipCode": "12345"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/practice/patients",
                json=test_patient,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"POST /api/practice/patients - Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                if data.get("success"):
                    patient = data.get("data", {})
                    print(f"✅ SUCCESS: Patient created")
                    print(f"   Patient ID: {patient.get('id', 'N/A')}")
                    print(f"   Name: {patient.get('firstName', 'N/A')} {patient.get('lastName', 'N/A')}")
                    print(f"   Email: {patient.get('email', 'N/A')}")
                    
                    return {"success": True, "patient_id": patient.get('id')}
                else:
                    print(f"❌ API returned success=false: {data}")
                    return {"success": False, "error": "API returned success=false"}
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_specific_procedure(self, procedure_id: str) -> Dict[str, Any]:
        """Test a specific procedure to verify content"""
        print(f"\n🔍 TESTING SPECIFIC PROCEDURE: {procedure_id}")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/procedures/{procedure_id}", timeout=30)
            
            print(f"GET /api/procedures/{procedure_id} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    procedure = data.get("data", {})
                    print(f"✅ SUCCESS: Procedure found")
                    print(f"   Name: {procedure.get('name', 'N/A')}")
                    print(f"   Specialty: {procedure.get('specialtyName', 'N/A')}")
                    print(f"   Duration: {procedure.get('duration', 'N/A')}")
                    
                    # Check content
                    overview = procedure.get('overview', '')
                    print(f"   Overview Length: {len(overview)} characters")
                    
                    # Check structured fields
                    structured_fields = ['immediateAftercare', 'dietRestrictions', 'warningSignsToCallDoctor', 'recoveryTimeline', 'medications']
                    print(f"   Structured Content:")
                    for field in structured_fields:
                        field_data = procedure.get(field, [])
                        print(f"     {field}: {len(field_data) if isinstance(field_data, list) else 'N/A'} items")
                    
                    return {"success": True, "procedure": procedure}
                else:
                    print(f"❌ API returned success=false: {data}")
                    return {"success": False, "error": "API returned success=false"}
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}

def main():
    """Main testing function for CORRECT backend URL investigation"""
    print("🚨 URGENT DATA RECOVERY INVESTIGATION - CORRECTED BACKEND URL")
    print("=" * 80)
    print("Testing the CORRECT backend URL: https://dentist-portal-3.emergent.host/api")
    print("Investigating data discrepancy between environments as requested in review")
    print("=" * 80)
    
    tester = CorrectBackendTester()
    
    # Authenticate with specified credentials
    print(f"\n🔐 STEP 1: AUTHENTICATION TEST")
    if not tester.authenticate("cganz2279@gmail.com", "password123"):
        print("❌ Authentication failed on CORRECT backend. Cannot proceed with testing.")
        print("🔍 This confirms the hypothesis - user credentials may not exist on this environment")
        sys.exit(1)
    
    # Test all critical endpoints as requested
    results = {}
    
    print(f"\n🔍 STEP 2: CRITICAL ENDPOINT TESTING")
    
    # Test patients
    results['patients'] = tester.test_practice_patients()
    
    # Test procedures
    results['procedures'] = tester.test_procedures()
    
    # Test dashboard
    results['dashboard'] = tester.test_practice_dashboard()
    
    # Test patient creation
    results['patient_creation'] = tester.test_create_patient()
    
    # Test specific procedures
    print(f"\n🦷 STEP 3: SPECIFIC PROCEDURE TESTING")
    test_procedures = ['root-canal-therapy', 'dental-implant-placement']
    results['specific_procedures'] = {}
    
    for proc_id in test_procedures:
        results['specific_procedures'][proc_id] = tester.test_specific_procedure(proc_id)
    
    # Final summary
    print(f"\n📊 FINAL INVESTIGATION SUMMARY")
    print("=" * 80)
    
    print(f"🔐 AUTHENTICATION: {'✅ SUCCESS' if tester.auth_token else '❌ FAILED'}")
    print(f"🏥 PATIENTS: {'✅ ' + str(results['patients'].get('count', 0)) + ' found' if results['patients'].get('success') else '❌ FAILED'}")
    print(f"🦷 PROCEDURES: {'✅ ' + str(results['procedures'].get('count', 0)) + ' found' if results['procedures'].get('success') else '❌ FAILED'}")
    print(f"📊 DASHBOARD: {'✅ SUCCESS' if results['dashboard'].get('success') else '❌ FAILED'}")
    print(f"👤 PATIENT CREATION: {'✅ SUCCESS' if results['patient_creation'].get('success') else '❌ FAILED'}")
    
    print(f"\n🎯 CRITICAL QUESTIONS ANSWERED:")
    print(f"   • Was previous testing hitting wrong environment? {'✅ YES - this is the correct environment' if tester.auth_token else '❌ NO - same issue exists here'}")
    print(f"   • Is patient data available on correct backend? {'✅ YES - ' + str(results['patients'].get('count', 0)) + ' patients found' if results['patients'].get('success') else '❌ NO - no patient data'}")
    print(f"   • Are 81 procedures accessible? {'✅ YES - ' + str(results['procedures'].get('count', 0)) + ' procedures found' if results['procedures'].get('success') else '❌ NO - procedures not accessible'}")
    print(f"   • Can we create patients? {'✅ YES - patient creation works' if results['patient_creation'].get('success') else '❌ NO - patient creation failed'}")
    
    if results['procedures'].get('success') and results['procedures'].get('count', 0) == 81:
        print(f"\n✅ HYPOTHESIS CONFIRMED: This is the correct environment with all 81 procedures!")
    elif results['procedures'].get('success') and results['procedures'].get('count', 0) > 0:
        print(f"\n⚠️ PARTIAL CONFIRMATION: Found {results['procedures'].get('count', 0)} procedures (not 81)")
    else:
        print(f"\n❌ HYPOTHESIS REJECTED: No procedures found on this environment either")
    
    print(f"\n🔍 RECOMMENDATION:")
    if tester.auth_token and results['patients'].get('success') and results['procedures'].get('success'):
        print("   ✅ This appears to be the correct backend environment")
        print("   ✅ User should be able to see data on this environment")
        print("   🔧 Check frontend configuration to ensure it's pointing to this backend")
    else:
        print("   ❌ This environment also has issues")
        print("   🔍 Need to investigate other possible environments or database issues")

if __name__ == "__main__":
    main()