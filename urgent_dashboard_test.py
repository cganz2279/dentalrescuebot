#!/usr/bin/env python3
"""
URGENT DATA LOSS INVESTIGATION - Dashboard Empty Data Testing
Focus: Investigating why user dashboard shows all zeros and empty data
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from review request
BACKEND_URL = "https://dentalpractice-hub-1.preview.emergentagent.com"

class UrgentDashboardTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.practice_data = None
        self.test_results = {}
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the backend API"""
        print(f"🔐 URGENT: Authenticating with {email}...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.practice_data = data.get("practice", {})
                
                print(f"✅ Authentication successful!")
                print(f"   Practice: {self.practice_data.get('name', 'Unknown')}")
                print(f"   Practice ID: {self.practice_data.get('id', 'Unknown')}")
                print(f"   Role: {data.get('role', 'Unknown')}")
                print(f"   User ID: {data.get('userId', 'Unknown')}")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                self.test_results["authentication"] = {
                    "status": "success",
                    "practice_name": self.practice_data.get('name'),
                    "practice_id": self.practice_data.get('id'),
                    "user_role": data.get('role')
                }
                
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results["authentication"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            self.test_results["authentication"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_dashboard_api(self) -> Dict[str, Any]:
        """Test the dashboard API that should return practice statistics"""
        print(f"\n🏥 TESTING DASHBOARD API: GET /api/practice/dashboard")
        print("-" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/practice/dashboard")
            
            print(f"Dashboard API status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dashboard API responded successfully")
                print(f"Raw response: {json.dumps(data, indent=2)}")
                
                # Extract key metrics
                dashboard_data = data.get("data", {}) if isinstance(data, dict) else data
                
                total_patients = dashboard_data.get("totalPatients", "NOT_FOUND")
                active_procedures = dashboard_data.get("activeProcedures", "NOT_FOUND")
                recent_patients = dashboard_data.get("recentPatients", "NOT_FOUND")
                recent_procedures = dashboard_data.get("recentProcedures", "NOT_FOUND")
                
                print(f"\n📊 DASHBOARD METRICS:")
                print(f"   Total Patients: {total_patients}")
                print(f"   Active Procedures: {active_procedures}")
                print(f"   Recent Patients: {len(recent_patients) if isinstance(recent_patients, list) else recent_patients}")
                print(f"   Recent Procedures: {len(recent_procedures) if isinstance(recent_procedures, list) else recent_procedures}")
                
                self.test_results["dashboard"] = {
                    "status": "success",
                    "total_patients": total_patients,
                    "active_procedures": active_procedures,
                    "recent_patients_count": len(recent_patients) if isinstance(recent_patients, list) else str(recent_patients),
                    "recent_procedures_count": len(recent_procedures) if isinstance(recent_procedures, list) else str(recent_procedures),
                    "raw_response": data
                }
                
                return dashboard_data
                
            else:
                print(f"❌ Dashboard API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results["dashboard"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return {}
                
        except Exception as e:
            print(f"❌ Dashboard API error: {str(e)}")
            self.test_results["dashboard"] = {
                "status": "error",
                "error": str(e)
            }
            return {}
    
    def test_patients_api(self) -> Dict[str, Any]:
        """Test the patients API to see if there are any patients"""
        print(f"\n👥 TESTING PATIENTS API: GET /api/practice/patients")
        print("-" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/practice/patients")
            
            print(f"Patients API status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Patients API responded successfully")
                
                patients = data.get("data", []) if isinstance(data, dict) else data
                patient_count = len(patients) if isinstance(patients, list) else 0
                
                print(f"📊 PATIENTS DATA:")
                print(f"   Total patients found: {patient_count}")
                
                if patient_count > 0:
                    print(f"   First few patients:")
                    for i, patient in enumerate(patients[:3]):
                        if isinstance(patient, dict):
                            print(f"     {i+1}. {patient.get('firstName', 'Unknown')} {patient.get('lastName', 'Unknown')} (ID: {patient.get('id', 'Unknown')})")
                        else:
                            print(f"     {i+1}. {patient}")
                else:
                    print(f"   ❌ NO PATIENTS FOUND")
                
                self.test_results["patients"] = {
                    "status": "success",
                    "count": patient_count,
                    "raw_response": data
                }
                
                return {"patients": patients, "count": patient_count}
                
            else:
                print(f"❌ Patients API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results["patients"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return {}
                
        except Exception as e:
            print(f"❌ Patients API error: {str(e)}")
            self.test_results["patients"] = {
                "status": "error",
                "error": str(e)
            }
            return {}
    
    def test_procedures_api(self) -> Dict[str, Any]:
        """Test the procedures API to verify the 81 procedures are still there"""
        print(f"\n📋 TESTING PROCEDURES API: GET /api/procedures")
        print("-" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/procedures")
            
            print(f"Procedures API status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Procedures API responded successfully")
                
                procedures = data.get("data", []) if isinstance(data, dict) else data
                procedure_count = len(procedures) if isinstance(procedures, list) else 0
                
                print(f"📊 PROCEDURES DATA:")
                print(f"   Total procedures found: {procedure_count}")
                print(f"   Expected: 81 procedures")
                
                if procedure_count > 0:
                    # Count by specialty
                    specialty_counts = {}
                    for proc in procedures:
                        if isinstance(proc, dict):
                            specialty = proc.get('specialtyName', 'Unknown')
                            specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
                    
                    print(f"   Procedures by specialty:")
                    for specialty, count in specialty_counts.items():
                        print(f"     - {specialty}: {count}")
                    
                    # Show first few procedures
                    print(f"   First few procedures:")
                    for i, proc in enumerate(procedures[:5]):
                        if isinstance(proc, dict):
                            print(f"     {i+1}. {proc.get('name', 'Unknown')} ({proc.get('specialtyName', 'Unknown')})")
                        else:
                            print(f"     {i+1}. {proc}")
                else:
                    print(f"   ❌ NO PROCEDURES FOUND")
                
                self.test_results["procedures"] = {
                    "status": "success",
                    "count": procedure_count,
                    "expected_count": 81,
                    "specialty_breakdown": specialty_counts if procedure_count > 0 else {},
                    "raw_response": data
                }
                
                return {"procedures": procedures, "count": procedure_count}
                
            else:
                print(f"❌ Procedures API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results["procedures"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return {}
                
        except Exception as e:
            print(f"❌ Procedures API error: {str(e)}")
            self.test_results["procedures"] = {
                "status": "error",
                "error": str(e)
            }
            return {}
    
    def test_database_connection(self) -> bool:
        """Test if we're connected to the correct database by checking basic endpoints"""
        print(f"\n🗄️ TESTING DATABASE CONNECTION")
        print("-" * 60)
        
        # Test a simple endpoint that doesn't require auth
        try:
            response = self.session.get(f"{self.base_url}/api/specialties")
            
            print(f"Specialties API status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                specialties = data.get("data", []) if isinstance(data, dict) else data
                specialty_count = len(specialties) if isinstance(specialties, list) else 0
                
                print(f"✅ Database connection working")
                print(f"   Specialties found: {specialty_count}")
                
                if specialty_count > 0:
                    print(f"   Available specialties:")
                    for spec in specialties:
                        if isinstance(spec, dict):
                            print(f"     - {spec.get('name', 'Unknown')} ({spec.get('procedureCount', 0)} procedures)")
                
                self.test_results["database_connection"] = {
                    "status": "success",
                    "specialties_count": specialty_count
                }
                
                return True
            else:
                print(f"❌ Database connection issue: {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results["database_connection"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                return False
                
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            self.test_results["database_connection"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def generate_summary_report(self) -> None:
        """Generate a comprehensive summary of all test results"""
        print(f"\n🚨 URGENT DATA LOSS INVESTIGATION SUMMARY")
        print("=" * 80)
        
        # Authentication Summary
        auth_result = self.test_results.get("authentication", {})
        if auth_result.get("status") == "success":
            print(f"✅ AUTHENTICATION: Working")
            print(f"   Practice: {auth_result.get('practice_name')}")
            print(f"   Practice ID: {auth_result.get('practice_id')}")
        else:
            print(f"❌ AUTHENTICATION: Failed - {auth_result.get('error', 'Unknown error')}")
        
        # Database Connection Summary
        db_result = self.test_results.get("database_connection", {})
        if db_result.get("status") == "success":
            print(f"✅ DATABASE CONNECTION: Working ({db_result.get('specialties_count', 0)} specialties)")
        else:
            print(f"❌ DATABASE CONNECTION: Failed - {db_result.get('error', 'Unknown error')}")
        
        # Dashboard API Summary
        dashboard_result = self.test_results.get("dashboard", {})
        if dashboard_result.get("status") == "success":
            print(f"✅ DASHBOARD API: Responding")
            print(f"   Total Patients: {dashboard_result.get('total_patients')}")
            print(f"   Active Procedures: {dashboard_result.get('active_procedures')}")
            print(f"   Recent Patients: {dashboard_result.get('recent_patients_count')}")
            print(f"   Recent Procedures: {dashboard_result.get('recent_procedures_count')}")
        else:
            print(f"❌ DASHBOARD API: Failed - {dashboard_result.get('error', 'Unknown error')}")
        
        # Patients API Summary
        patients_result = self.test_results.get("patients", {})
        if patients_result.get("status") == "success":
            patient_count = patients_result.get("count", 0)
            if patient_count > 0:
                print(f"✅ PATIENTS API: {patient_count} patients found")
            else:
                print(f"⚠️ PATIENTS API: Responding but 0 patients found")
        else:
            print(f"❌ PATIENTS API: Failed - {patients_result.get('error', 'Unknown error')}")
        
        # Procedures API Summary
        procedures_result = self.test_results.get("procedures", {})
        if procedures_result.get("status") == "success":
            procedure_count = procedures_result.get("count", 0)
            expected_count = procedures_result.get("expected_count", 81)
            if procedure_count == expected_count:
                print(f"✅ PROCEDURES API: {procedure_count} procedures found (matches expected {expected_count})")
            elif procedure_count > 0:
                print(f"⚠️ PROCEDURES API: {procedure_count} procedures found (expected {expected_count})")
            else:
                print(f"🚨 PROCEDURES API: 0 procedures found (expected {expected_count})")
        else:
            print(f"❌ PROCEDURES API: Failed - {procedures_result.get('error', 'Unknown error')}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        # Determine the most likely root cause
        if auth_result.get("status") != "success":
            print("🔴 PRIMARY ISSUE: Authentication failure - cannot access user data")
        elif db_result.get("status") != "success":
            print("🔴 PRIMARY ISSUE: Database connection failure")
        elif dashboard_result.get("status") != "success":
            print("🔴 PRIMARY ISSUE: Dashboard API not working - frontend cannot get statistics")
        elif patients_result.get("status") == "success" and patients_result.get("count", 0) == 0:
            print("🔴 PRIMARY ISSUE: No patients in database - data loss or wrong database")
        elif procedures_result.get("status") == "success" and procedures_result.get("count", 0) == 0:
            print("🔴 PRIMARY ISSUE: No procedures in database - data loss or wrong database")
        elif procedures_result.get("status") == "success" and procedures_result.get("count", 0) != 81:
            print(f"🟡 SECONDARY ISSUE: Procedure count mismatch ({procedures_result.get('count', 0)} vs 81 expected)")
        else:
            print("🟢 BACKEND DATA APPEARS INTACT: Issue may be in frontend display logic")
        
        print(f"\n📋 NEXT STEPS:")
        print("-" * 20)
        if auth_result.get("status") != "success":
            print("1. Fix authentication credentials or backend auth system")
        elif db_result.get("status") != "success":
            print("1. Check database connection and configuration")
        elif patients_result.get("count", 0) == 0 and procedures_result.get("count", 0) == 0:
            print("1. Verify correct database environment is being used")
            print("2. Check if data migration or restore is needed")
        elif dashboard_result.get("status") != "success":
            print("1. Fix dashboard API endpoint implementation")
        else:
            print("1. Check frontend dashboard component logic")
            print("2. Verify frontend is calling correct API endpoints")
            print("3. Check frontend state management and data display")

def main():
    """Main testing function for urgent data loss investigation"""
    print("🚨 URGENT DATA LOSS INVESTIGATION - DASHBOARD EMPTY DATA")
    print("=" * 80)
    print("User reports: Total Patients: 0, Active Procedures: 0, No patients/procedures found")
    print(f"Backend URL: {BACKEND_URL}")
    print("Testing with credentials: cganz2279@gmail.com/password123")
    
    tester = UrgentDashboardTester()
    
    # Step 1: Authenticate
    if not tester.authenticate("cganz2279@gmail.com", "password123"):
        print("❌ CRITICAL: Authentication failed. Cannot proceed with investigation.")
        tester.generate_summary_report()
        sys.exit(1)
    
    # Step 2: Test database connection
    tester.test_database_connection()
    
    # Step 3: Test dashboard API
    tester.test_dashboard_api()
    
    # Step 4: Test patients API
    tester.test_patients_api()
    
    # Step 5: Test procedures API
    tester.test_procedures_api()
    
    # Step 6: Generate comprehensive summary
    tester.generate_summary_report()
    
    print(f"\n🎯 INVESTIGATION COMPLETE")
    print("=" * 80)
    print("Review the summary above to understand the root cause of the empty dashboard data.")

if __name__ == "__main__":
    main()