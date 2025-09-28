#!/usr/bin/env python3
"""
SMS Cellphone Debug Test for Michael Brown Patient
Testing the SMS cellphone issue where patient cellphone number is not available
"""

import requests
import json
from typing import List, Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://oncallbot.preview.emergentagent.com/api"

# Test credentials
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

def authenticate():
    """Authenticate and get JWT token"""
    print("🔐 Authenticating with test credentials...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user', {})
            practice = data.get('practice', {})
            
            print(f"   ✅ Authentication successful")
            print(f"   User: {user.get('firstName')} {user.get('lastName')} ({user.get('email')})")
            print(f"   Practice: {practice.get('name', 'N/A')}")
            print(f"   Practice ID: {user.get('practiceId', 'N/A')}")
            
            return token, user.get('practiceId')
        else:
            print(f"   ❌ Authentication failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Authentication error: {str(e)}")
        return None, None

def test_patient_data_lookup(token, practice_id):
    """Test 1: Look up Michael Brown in patients database"""
    print("\n🔍 TEST 1: Looking up Michael Brown in patients database...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all patients for the practice
        response = requests.get(
            f"{BACKEND_URL}/practice/patients",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            patients = data.get('data', [])
            
            print(f"   Total patients found: {len(patients)}")
            
            # Look for Michael Brown
            michael_brown = None
            for patient in patients:
                first_name = patient.get('firstName', '').lower()
                last_name = patient.get('lastName', '').lower()
                
                if 'michael' in first_name and 'brown' in last_name:
                    michael_brown = patient
                    break
            
            if michael_brown:
                print(f"   ✅ Michael Brown found!")
                print(f"   Patient ID: {michael_brown.get('id')}")
                print(f"   Full Name: {michael_brown.get('firstName')} {michael_brown.get('lastName')}")
                print(f"   Email: {michael_brown.get('email')}")
                print(f"   Cellphone: {michael_brown.get('cellphone', 'NOT SET')}")
                print(f"   Phone (old field): {michael_brown.get('phone', 'NOT SET')}")
                print(f"   Is Active: {michael_brown.get('isActive')}")
                print(f"   Created At: {michael_brown.get('createdAt')}")
                print(f"   Updated At: {michael_brown.get('updatedAt')}")
                
                # Check if cellphone field exists and has value
                if michael_brown.get('cellphone'):
                    print(f"   ✅ CELLPHONE FIELD POPULATED: {michael_brown.get('cellphone')}")
                else:
                    print(f"   ❌ CELLPHONE FIELD MISSING OR EMPTY")
                
                return michael_brown
            else:
                print(f"   ❌ Michael Brown not found in patients list")
                print(f"   Available patients:")
                for patient in patients[:5]:  # Show first 5 patients
                    print(f"      - {patient.get('firstName')} {patient.get('lastName')} ({patient.get('email')})")
                return None
        else:
            print(f"   ❌ Failed to get patients: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error looking up patient data: {str(e)}")
        return None

def test_dashboard_api_response(token, practice_id):
    """Test 2: Check dashboard API response for patient data"""
    print("\n🔍 TEST 2: Testing dashboard API response...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BACKEND_URL}/practice/dashboard",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            dashboard_data = data.get('data', {})
            recent_patients = dashboard_data.get('recentPatients', [])
            
            print(f"   Recent patients count: {len(recent_patients)}")
            
            # Look for Michael Brown in recent patients
            michael_in_dashboard = None
            for patient in recent_patients:
                first_name = patient.get('firstName', '').lower()
                last_name = patient.get('lastName', '').lower()
                
                if 'michael' in first_name and 'brown' in last_name:
                    michael_in_dashboard = patient
                    break
            
            if michael_in_dashboard:
                print(f"   ✅ Michael Brown found in dashboard!")
                print(f"   Dashboard Patient ID: {michael_in_dashboard.get('id')}")
                print(f"   Dashboard Full Name: {michael_in_dashboard.get('firstName')} {michael_in_dashboard.get('lastName')}")
                print(f"   Dashboard Email: {michael_in_dashboard.get('email')}")
                print(f"   Dashboard Cellphone: {michael_in_dashboard.get('cellphone', 'NOT SET')}")
                print(f"   Dashboard Phone (old): {michael_in_dashboard.get('phone', 'NOT SET')}")
                print(f"   Dashboard Status: {michael_in_dashboard.get('status')}")
                
                # Check if cellphone is included in dashboard response
                if michael_in_dashboard.get('cellphone'):
                    print(f"   ✅ CELLPHONE INCLUDED IN DASHBOARD: {michael_in_dashboard.get('cellphone')}")
                else:
                    print(f"   ❌ CELLPHONE NOT INCLUDED IN DASHBOARD RESPONSE")
                
                return michael_in_dashboard
            else:
                print(f"   ❌ Michael Brown not found in dashboard recent patients")
                print(f"   Available recent patients:")
                for patient in recent_patients:
                    print(f"      - {patient.get('firstName')} {patient.get('lastName')} ({patient.get('email')})")
                return None
        else:
            print(f"   ❌ Failed to get dashboard: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error getting dashboard data: {str(e)}")
        return None

def test_patient_update(token, practice_id, patient_data):
    """Test 3: Try updating Michael Brown's cellphone through API"""
    print("\n🔍 TEST 3: Testing patient cellphone update...")
    
    if not patient_data:
        print("   ❌ No patient data available for update test")
        return False
    
    patient_id = patient_data.get('id')
    if not patient_id:
        print("   ❌ No patient ID available for update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test cellphone number (realistic looking)
        test_cellphone = "+1-555-123-4567"
        
        print(f"   Attempting to update cellphone for patient ID: {patient_id}")
        print(f"   New cellphone number: {test_cellphone}")
        
        # Update patient cellphone
        response = requests.put(
            f"{BACKEND_URL}/practice/patients/{patient_id}",
            headers=headers,
            json={
                "cellphone": test_cellphone
            },
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Update successful!")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Verify the update by fetching patient data again
            print(f"   Verifying update by fetching patient data...")
            
            verify_response = requests.get(
                f"{BACKEND_URL}/practice/patients",
                headers=headers,
                timeout=30
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                patients = verify_data.get('data', [])
                
                # Find Michael Brown again
                updated_michael = None
                for patient in patients:
                    if patient.get('id') == patient_id:
                        updated_michael = patient
                        break
                
                if updated_michael:
                    updated_cellphone = updated_michael.get('cellphone')
                    print(f"   Verified cellphone after update: {updated_cellphone}")
                    
                    if updated_cellphone == test_cellphone:
                        print(f"   ✅ CELLPHONE UPDATE SUCCESSFUL AND PERSISTED")
                        return True
                    else:
                        print(f"   ❌ CELLPHONE UPDATE NOT PERSISTED (expected: {test_cellphone}, got: {updated_cellphone})")
                        return False
                else:
                    print(f"   ❌ Could not find patient after update")
                    return False
            else:
                print(f"   ❌ Failed to verify update: {verify_response.text}")
                return False
        else:
            print(f"   ❌ Update failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating patient cellphone: {str(e)}")
        return False

def test_patient_procedure_relationship(token, practice_id, patient_data):
    """Test 4: Check patient-procedure relationship and SMS functionality"""
    print("\n🔍 TEST 4: Testing patient-procedure relationship for SMS...")
    
    if not patient_data:
        print("   ❌ No patient data available for procedure relationship test")
        return False
    
    patient_id = patient_data.get('id')
    if not patient_id:
        print("   ❌ No patient ID available for procedure relationship test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get recent procedures from dashboard
        dashboard_response = requests.get(
            f"{BACKEND_URL}/practice/dashboard",
            headers=headers,
            timeout=30
        )
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json().get('data', {})
            recent_procedures = dashboard_data.get('recentProcedures', [])
            
            print(f"   Total recent procedures: {len(recent_procedures)}")
            
            # Look for procedures assigned to Michael Brown
            michael_procedures = []
            for procedure in recent_procedures:
                if procedure.get('patientId') == patient_id:
                    michael_procedures.append(procedure)
            
            print(f"   Procedures assigned to Michael Brown: {len(michael_procedures)}")
            
            if michael_procedures:
                for i, procedure in enumerate(michael_procedures):
                    print(f"   Procedure {i+1}:")
                    print(f"      - ID: {procedure.get('id')}")
                    print(f"      - Name: {procedure.get('procedureName')}")
                    print(f"      - Patient ID: {procedure.get('patientId')}")
                    print(f"      - Patient Name: {procedure.get('patientName')}")
                    print(f"      - Performed Date: {procedure.get('performedDate')}")
                    print(f"      - Status: {procedure.get('status')}")
                
                # Test SMS functionality with first procedure
                test_procedure = michael_procedures[0]
                print(f"\n   Testing SMS functionality with procedure: {test_procedure.get('procedureName')}")
                
                # Check if we can get patient cellphone for SMS
                patient_cellphone = patient_data.get('cellphone')
                if patient_cellphone:
                    print(f"   ✅ PATIENT CELLPHONE AVAILABLE FOR SMS: {patient_cellphone}")
                    
                    # Test SMS endpoint (if available)
                    sms_test_data = {
                        "patientCellphone": patient_cellphone,
                        "procedureId": test_procedure.get('procedureId'),
                        "procedureName": test_procedure.get('procedureName'),
                        "assignmentId": test_procedure.get('id')
                    }
                    
                    print(f"   SMS test data prepared:")
                    print(f"      - Patient Cellphone: {sms_test_data['patientCellphone']}")
                    print(f"      - Procedure ID: {sms_test_data['procedureId']}")
                    print(f"      - Procedure Name: {sms_test_data['procedureName']}")
                    print(f"      - Assignment ID: {sms_test_data['assignmentId']}")
                    
                    return True
                else:
                    print(f"   ❌ PATIENT CELLPHONE NOT AVAILABLE FOR SMS")
                    return False
            else:
                print(f"   ❌ No procedures found for Michael Brown")
                return False
        else:
            print(f"   ❌ Failed to get dashboard for procedure check: {dashboard_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking patient-procedure relationship: {str(e)}")
        return False

def test_direct_database_query(token, practice_id):
    """Test 5: Direct database query simulation to check data consistency"""
    print("\n🔍 TEST 5: Testing data consistency between patient updates and dashboard loading...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get patients data
        patients_response = requests.get(
            f"{BACKEND_URL}/practice/patients",
            headers=headers,
            timeout=30
        )
        
        # Get dashboard data
        dashboard_response = requests.get(
            f"{BACKEND_URL}/practice/dashboard",
            headers=headers,
            timeout=30
        )
        
        if patients_response.status_code == 200 and dashboard_response.status_code == 200:
            patients_data = patients_response.json().get('data', [])
            dashboard_data = dashboard_response.json().get('data', {})
            recent_patients = dashboard_data.get('recentPatients', [])
            
            print(f"   Patients endpoint returned: {len(patients_data)} patients")
            print(f"   Dashboard endpoint returned: {len(recent_patients)} recent patients")
            
            # Compare Michael Brown data between endpoints
            patients_michael = None
            dashboard_michael = None
            
            for patient in patients_data:
                if 'michael' in patient.get('firstName', '').lower() and 'brown' in patient.get('lastName', '').lower():
                    patients_michael = patient
                    break
            
            for patient in recent_patients:
                if 'michael' in patient.get('firstName', '').lower() and 'brown' in patient.get('lastName', '').lower():
                    dashboard_michael = patient
                    break
            
            if patients_michael and dashboard_michael:
                print(f"   ✅ Michael Brown found in both endpoints")
                
                # Compare cellphone data
                patients_cellphone = patients_michael.get('cellphone')
                dashboard_cellphone = dashboard_michael.get('cellphone')
                
                print(f"   Patients endpoint cellphone: {patients_cellphone}")
                print(f"   Dashboard endpoint cellphone: {dashboard_cellphone}")
                
                if patients_cellphone == dashboard_cellphone:
                    print(f"   ✅ CELLPHONE DATA CONSISTENT BETWEEN ENDPOINTS")
                    if patients_cellphone:
                        print(f"   ✅ CELLPHONE DATA AVAILABLE: {patients_cellphone}")
                        return True
                    else:
                        print(f"   ❌ CELLPHONE DATA MISSING IN BOTH ENDPOINTS")
                        return False
                else:
                    print(f"   ❌ CELLPHONE DATA INCONSISTENT BETWEEN ENDPOINTS")
                    return False
            elif patients_michael:
                print(f"   ⚠️  Michael Brown found in patients endpoint but not in dashboard")
                print(f"   Patients endpoint cellphone: {patients_michael.get('cellphone')}")
                return False
            elif dashboard_michael:
                print(f"   ⚠️  Michael Brown found in dashboard but not in patients endpoint")
                print(f"   Dashboard endpoint cellphone: {dashboard_michael.get('cellphone')}")
                return False
            else:
                print(f"   ❌ Michael Brown not found in either endpoint")
                return False
        else:
            print(f"   ❌ Failed to get data from endpoints")
            print(f"   Patients response: {patients_response.status_code}")
            print(f"   Dashboard response: {dashboard_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking data consistency: {str(e)}")
        return False

def run_sms_cellphone_debug_test():
    """Run all SMS cellphone debug tests"""
    print("🚀 SMS CELLPHONE DEBUG TEST FOR MICHAEL BROWN PATIENT")
    print("=" * 80)
    
    # Authenticate
    token, practice_id = authenticate()
    if not token:
        print("\n❌ CRITICAL FAILURE: Authentication failed. Cannot proceed with tests.")
        return False
    
    # Test 1: Patient data lookup
    patient_data = test_patient_data_lookup(token, practice_id)
    
    # Test 2: Dashboard API response
    dashboard_patient_data = test_dashboard_api_response(token, practice_id)
    
    # Test 3: Patient update
    update_success = test_patient_update(token, practice_id, patient_data)
    
    # Test 4: Patient-procedure relationship
    procedure_relationship_success = test_patient_procedure_relationship(token, practice_id, patient_data)
    
    # Test 5: Data consistency
    consistency_success = test_direct_database_query(token, practice_id)
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 SMS CELLPHONE DEBUG TEST RESULTS:")
    print("=" * 80)
    
    all_tests = [
        ("Patient Data Lookup", patient_data is not None),
        ("Dashboard API Response", dashboard_patient_data is not None),
        ("Patient Cellphone Update", update_success),
        ("Patient-Procedure Relationship", procedure_relationship_success),
        ("Data Consistency Check", consistency_success)
    ]
    
    passed_tests = 0
    for test_name, passed in all_tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if passed:
            passed_tests += 1
    
    print(f"\n📈 OVERALL RESULT: {passed_tests}/{len(all_tests)} tests passed")
    
    # Specific SMS issue analysis
    print(f"\n🔍 SMS ISSUE ANALYSIS:")
    if patient_data:
        cellphone = patient_data.get('cellphone')
        if cellphone:
            print(f"   ✅ Michael Brown has cellphone number: {cellphone}")
            print(f"   ✅ SMS should be available for this patient")
        else:
            print(f"   ❌ Michael Brown does NOT have cellphone number set")
            print(f"   ❌ This explains why SMS shows 'patient cellphone number not available'")
    else:
        print(f"   ❌ Could not retrieve Michael Brown patient data")
    
    if passed_tests == len(all_tests):
        print("🎉 ALL TESTS PASSED: SMS cellphone functionality should be working!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED: SMS cellphone issue identified")
        return False

if __name__ == "__main__":
    success = run_sms_cellphone_debug_test()
    exit(0 if success else 1)