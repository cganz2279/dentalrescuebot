#!/usr/bin/env python3
"""
IV Sedation Creation Verification Test
Specifically testing the review request requirements:
1. GET /api/procedures/iv-sedation - Does it exist now?
2. GET /api/specialties - What's the Oral Surgery procedure count now?
3. GET /api/procedures?specialty=oral-surgery - List all procedures in Oral Surgery
"""

import requests
import json
import sys
from typing import Dict, Any

# Backend URL from review request
BACKEND_URL = "https://dentist-portal-3.emergent.host/api"
TEST_EMAIL = "cganz2279@gmail.com"
TEST_PASSWORD = "password123"

class IVSedationVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}: {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def authenticate(self) -> bool:
        """Authenticate with the backend"""
        try:
            print(f"\n🔐 AUTHENTICATING with {TEST_EMAIL}")
            
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "token" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    practice_name = data.get("practice", {}).get("name", "Unknown")
                    self.log_result("Authentication", True, f"Successfully authenticated as {practice_name}")
                    return True
                else:
                    self.log_result("Authentication", False, f"Login response missing token: {data}")
                    return False
            else:
                self.log_result("Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_iv_sedation_exists(self) -> bool:
        """Test 1: GET /api/procedures/iv-sedation - Does it exist now?"""
        try:
            print(f"\n🔍 TESTING: GET /api/procedures/iv-sedation")
            
            response = self.session.get(f"{BACKEND_URL}/procedures/iv-sedation")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedure = data["data"]
                    procedure_name = procedure.get("name", "Unknown")
                    specialty = procedure.get("specialtyName", "Unknown")
                    duration = procedure.get("duration", "Unknown")
                    
                    details = f"IV Sedation procedure EXISTS - Name: '{procedure_name}', Specialty: '{specialty}', Duration: '{duration}'"
                    self.log_result("IV Sedation Exists", True, details)
                    
                    # Log additional details
                    print(f"   📋 Full procedure details:")
                    print(f"   - ID: {procedure.get('id', 'N/A')}")
                    print(f"   - Name: {procedure.get('name', 'N/A')}")
                    print(f"   - Specialty: {procedure.get('specialty', 'N/A')} ({procedure.get('specialtyName', 'N/A')})")
                    print(f"   - Duration: {procedure.get('duration', 'N/A')}")
                    print(f"   - Overview length: {len(procedure.get('overview', ''))} characters")
                    
                    return True
                else:
                    self.log_result("IV Sedation Exists", False, f"Invalid response format: {data}")
                    return False
            elif response.status_code == 404:
                self.log_result("IV Sedation Exists", False, "IV Sedation procedure NOT FOUND (404)")
                return False
            else:
                self.log_result("IV Sedation Exists", False, f"Request failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("IV Sedation Exists", False, f"Error checking IV Sedation: {str(e)}")
            return False
    
    def test_oral_surgery_specialty_count(self) -> int:
        """Test 2: GET /api/specialties - What's the Oral Surgery procedure count now?"""
        try:
            print(f"\n🔍 TESTING: GET /api/specialties (Oral Surgery count)")
            
            response = self.session.get(f"{BACKEND_URL}/specialties")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    specialties = data["data"]
                    
                    # Find Oral Surgery specialty
                    oral_surgery = None
                    for specialty in specialties:
                        if "oral" in specialty.get("name", "").lower() and "surgery" in specialty.get("name", "").lower():
                            oral_surgery = specialty
                            break
                    
                    if oral_surgery:
                        count = oral_surgery.get("procedureCount", 0)
                        specialty_name = oral_surgery.get("name", "Unknown")
                        specialty_id = oral_surgery.get("id", "Unknown")
                        
                        details = f"Oral Surgery specialty found - Name: '{specialty_name}', ID: '{specialty_id}', Procedure Count: {count}"
                        self.log_result("Oral Surgery Count", True, details)
                        
                        print(f"   📊 Oral Surgery Details:")
                        print(f"   - Name: {specialty_name}")
                        print(f"   - ID: {specialty_id}")
                        print(f"   - Procedure Count: {count}")
                        
                        return count
                    else:
                        self.log_result("Oral Surgery Count", False, "Oral Surgery specialty not found in specialties list")
                        print(f"   📋 Available specialties:")
                        for spec in specialties:
                            print(f"   - {spec.get('name', 'Unknown')} (Count: {spec.get('procedureCount', 0)})")
                        return 0
                else:
                    self.log_result("Oral Surgery Count", False, f"Invalid response format: {data}")
                    return 0
            else:
                self.log_result("Oral Surgery Count", False, f"Request failed with status {response.status_code}: {response.text}")
                return 0
                
        except Exception as e:
            self.log_result("Oral Surgery Count", False, f"Error checking specialties: {str(e)}")
            return 0
    
    def test_oral_surgery_procedures_list(self) -> list:
        """Test 3: GET /api/procedures?specialty=oral-surgery - List all procedures in Oral Surgery"""
        try:
            print(f"\n🔍 TESTING: GET /api/procedures?specialty=oral-surgery")
            
            response = self.session.get(f"{BACKEND_URL}/procedures?specialty=oral-surgery")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    procedures = data["data"]
                    procedure_count = len(procedures)
                    
                    details = f"Found {procedure_count} procedures in Oral Surgery specialty"
                    self.log_result("Oral Surgery Procedures List", True, details)
                    
                    print(f"   📋 Oral Surgery Procedures ({procedure_count} total):")
                    iv_sedation_found = False
                    
                    for i, proc in enumerate(procedures, 1):
                        proc_name = proc.get("name", "Unknown")
                        proc_id = proc.get("id", "Unknown")
                        proc_duration = proc.get("duration", "Unknown")
                        
                        print(f"   {i:2d}. {proc_name} (ID: {proc_id}, Duration: {proc_duration})")
                        
                        # Check if IV Sedation is in the list
                        if "iv" in proc_name.lower() and "sedation" in proc_name.lower():
                            iv_sedation_found = True
                            print(f"       🎯 IV SEDATION FOUND IN ORAL SURGERY LIST!")
                    
                    if iv_sedation_found:
                        print(f"   ✅ IV Sedation is properly assigned to Oral Surgery specialty")
                    else:
                        print(f"   ❌ IV Sedation NOT found in Oral Surgery procedures list")
                    
                    return procedures
                else:
                    self.log_result("Oral Surgery Procedures List", False, f"Invalid response format: {data}")
                    return []
            else:
                self.log_result("Oral Surgery Procedures List", False, f"Request failed with status {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Oral Surgery Procedures List", False, f"Error checking oral surgery procedures: {str(e)}")
            return []
    
    def run_verification_tests(self):
        """Run all IV Sedation verification tests"""
        print("🚨 IV SEDATION CREATION VERIFICATION - SECOND ATTEMPT")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: {TEST_EMAIL}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("\n❌ AUTHENTICATION FAILED - Cannot proceed with tests")
            return False
        
        # Step 2: Test IV Sedation exists
        iv_sedation_exists = self.test_iv_sedation_exists()
        
        # Step 3: Check Oral Surgery specialty count
        oral_surgery_count = self.test_oral_surgery_specialty_count()
        
        # Step 4: List all Oral Surgery procedures
        oral_surgery_procedures = self.test_oral_surgery_procedures_list()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print()
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Critical Analysis
        print("\n🔍 CRITICAL ANALYSIS:")
        
        if iv_sedation_exists:
            print("✅ IV Sedation procedure EXISTS and is accessible via API")
        else:
            print("❌ IV Sedation procedure does NOT exist or is not accessible")
        
        print(f"📊 Oral Surgery specialty has {oral_surgery_count} procedures")
        
        if len(oral_surgery_procedures) > 0:
            iv_in_list = any("iv" in proc.get("name", "").lower() and "sedation" in proc.get("name", "").lower() 
                           for proc in oral_surgery_procedures)
            if iv_in_list:
                print("✅ IV Sedation is properly assigned to Oral Surgery specialty")
            else:
                print("❌ IV Sedation is NOT found in Oral Surgery procedures list")
        
        # Final verdict
        if iv_sedation_exists and oral_surgery_count > 1:
            print("\n🎉 VERIFICATION SUCCESSFUL: IV Sedation appears to be properly created and assigned")
        else:
            print("\n🚨 VERIFICATION FAILED: Issues found with IV Sedation creation/assignment")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = IVSedationVerificationTest()
    success = tester.run_verification_tests()
    sys.exit(0 if success else 1)