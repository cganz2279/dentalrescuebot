#!/usr/bin/env python3
"""
Active Procedures Investigation Backend Test
Testing current real-time data from practice dashboard for cganz2279@gmail.com
User reports seeing 6 active procedures, need to verify current count
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://aftercareportal.preview.emergentagent.com/api"

def test_practice_login_and_dashboard():
    """Test practice login and get current dashboard data"""
    print("🔐 Testing Practice Login and Dashboard Data...")
    
    # Login credentials as specified in review request
    login_data = {
        "email": "cganz2279@gmail.com",
        "password": "password123"
    }
    
    try:
        # Test login
        print(f"📡 POST {BACKEND_URL}/auth/login")
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
        login_result = login_response.json()
        print(f"📄 Login Response: {json.dumps(login_result, indent=2)}")
        
        token = login_result.get("access_token") or login_result.get("token")
        practice_id = login_result.get("practice_id") or login_result.get("practiceId")
        
        # Extract practice ID from user object if not directly available
        if not practice_id and "user" in login_result:
            practice_id = login_result["user"].get("practiceId")
        
        print(f"✅ Login successful")
        print(f"🔑 Token: {token[:20]}..." if token else "❌ No token found")
        print(f"🏥 Practice ID: {practice_id}")
        
        # Get dashboard data
        headers = {"Authorization": f"Bearer {token}"}
        print(f"\n📊 GET {BACKEND_URL}/practice/dashboard")
        dashboard_response = requests.get(f"{BACKEND_URL}/practice/dashboard", headers=headers)
        print(f"Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code != 200:
            print(f"❌ Dashboard request failed: {dashboard_response.text}")
            return False
            
        dashboard_data = dashboard_response.json()
        
        # Extract key metrics from the correct nested structure
        data = dashboard_data.get("data", {})
        practice_info = data.get("practice", {})
        stats = data.get("stats", {})
        
        practice_name = practice_info.get("name", "Unknown")
        active_procedures = stats.get("activeProcedures", 0)
        total_patients = stats.get("patientCount", 0)  # Note: it's patientCount, not totalPatients
        
        print(f"📄 Dashboard Response: {json.dumps(dashboard_data, indent=2)}")
        
        print(f"✅ Dashboard data retrieved successfully")
        print(f"🏥 Practice Name: {practice_name}")
        print(f"📈 Current Active Procedures: {active_procedures}")
        print(f"👥 Current Total Patients: {total_patients}")
        
        # Get detailed active procedures list
        print(f"\n📋 Getting detailed active procedures...")
        procedures_response = requests.get(f"{BACKEND_URL}/practice/patient-procedures", headers=headers)
        
        if procedures_response.status_code == 200:
            procedures_data = procedures_response.json()
            active_procs = [p for p in procedures_data.get("data", []) if p.get("status") == "active"]
            
            print(f"📊 Active Procedures Details:")
            print(f"   Total Active: {len(active_procs)}")
            
            # Group by patient
            patients = {}
            for proc in active_procs:
                patient_name = proc.get("patientName", "Unknown")
                if patient_name not in patients:
                    patients[patient_name] = []
                patients[patient_name].append(proc.get("procedureName", "Unknown"))
            
            print(f"   Patients with Active Procedures: {len(patients)}")
            for patient, procs in patients.items():
                print(f"   • {patient}: {len(procs)} procedures ({', '.join(procs[:3])}{'...' if len(procs) > 3 else ''})")
        
        # Compare with user's reported count
        print(f"\n🔍 COMPARISON ANALYSIS:")
        print(f"   User Reports: 6 active procedures")
        print(f"   System Shows: {active_procedures} active procedures")
        print(f"   Discrepancy: {abs(active_procedures - 6)} procedures")
        
        if active_procedures == 6:
            print(f"✅ MATCH: System data matches user's view")
        else:
            print(f"⚠️  MISMATCH: System shows {active_procedures}, user sees 6")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def test_recent_procedure_activity():
    """Check for recent procedure assignments/updates"""
    print("\n🕒 Testing Recent Procedure Activity...")
    
    login_data = {
        "email": "cganz2279@gmail.com", 
        "password": "password123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed for activity check")
            return False
            
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get patient procedures with timestamps
        procedures_response = requests.get(f"{BACKEND_URL}/practice/patient-procedures", headers=headers)
        
        if procedures_response.status_code == 200:
            procedures_data = procedures_response.json()
            all_procedures = procedures_data.get("data", [])
            
            # Sort by creation date (most recent first)
            sorted_procedures = sorted(all_procedures, 
                                     key=lambda x: x.get("createdAt", ""), 
                                     reverse=True)
            
            print(f"📊 Recent Procedure Activity (Last 10):")
            for i, proc in enumerate(sorted_procedures[:10]):
                status = proc.get("status", "unknown")
                patient = proc.get("patientName", "Unknown")
                procedure = proc.get("procedureName", "Unknown")
                created = proc.get("createdAt", "Unknown")
                
                status_icon = "🟢" if status == "active" else "🔴" if status == "completed" else "⚪"
                print(f"   {i+1}. {status_icon} {patient} - {procedure} ({status}) [{created}]")
                
            # Count by status
            status_counts = {}
            for proc in all_procedures:
                status = proc.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
                
            print(f"\n📈 Status Summary:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error checking recent activity: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("=" * 80)
    print("🎯 ACTIVE PROCEDURES INVESTIGATION - REAL-TIME DATA CHECK")
    print("=" * 80)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"👤 Practice Login: cganz2279@gmail.com")
    print(f"🎯 User Reports: 6 active procedures (need to verify)")
    print("=" * 80)
    
    # Run tests
    test1_passed = test_practice_login_and_dashboard()
    test2_passed = test_recent_procedure_activity()
    
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Practice Login & Dashboard: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Recent Activity Check: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 ALL TESTS PASSED - Real-time data retrieved successfully")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED - Check error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())